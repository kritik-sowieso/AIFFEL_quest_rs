"""두 과제를 함께 학습하는 LoRA 코드. 각 과제의 손실 가중치는 같다.

B와 C는 별도 프로세스에서 동일한 초기 모델로 시작한다.
이번 본 실험은 검수된 합성 좌표(synthetic coordinates)를 사용한다.
"""
import argparse
import json
import random
import time
from pathlib import Path
from jamo.core import read_jsonl, digest
from jamo.prompts import messages

def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
    from peft import LoraConfig, get_peft_model
    p = argparse.ArgumentParser()
    p.add_argument('--condition', choices=['B','C'], required=True)
    p.add_argument('--data', default='data/train_reviewed.jsonl')
    p.add_argument('--model', default='Qwen/Qwen2.5-0.5B-Instruct')
    p.add_argument('--revision', required=True, help='Exact revision recorded by the pilot')
    p.add_argument('--epochs', type=int, default=5)
    p.add_argument('--seed', type=int, default=20260923)
    p.add_argument('--accumulation', type=int, default=8)
    p.add_argument('--lr', type=float, default=2e-4)
    p.add_argument('--max-length', type=int, default=1536)
    p.add_argument('--annotation-mode', choices=['reviewed_ocr','synthetic_coordinates'], default='reviewed_ocr')
    args = p.parse_args()
    rows = read_jsonl(args.data)
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicate training set')
    for r in rows:
        if r['split'] != 'train' or r.get('annotation_source') != args.annotation_mode or not r.get('review_approved'):
            raise ValueError(f"Unapproved training annotation: {r['id']}")
        if args.annotation_mode == 'reviewed_ocr' and not r.get('ocr_record_id'):
            raise ValueError('OCR provenance required')
        if not r.get('aux_points'):
            raise ValueError('Missing reviewed auxiliary points')
    # 난수 시드(seed)를 고정해 B/C의 초기 어댑터와 자료 순서를 맞춘다.
    set_seed(args.seed)
    if not torch.cuda.is_available():
        raise RuntimeError('This training configuration requires a GPU.')
    out = Path('checkpoints')/args.condition
    if out.exists():
        raise RuntimeError(f'Refusing to overwrite {out}; use a fresh experiment directory.')
    out.mkdir(parents=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(args.model, revision=args.revision, torch_dtype=torch.float32).to('cuda')
    # LoRA: 기반 가중치는 고정하고 작은 저랭크 행렬만 추가 학습한다.
    # q_proj, v_proj는 어텐션(attention)의 질의·값 투영층이다.
    model = get_peft_model(model, LoraConfig(r=8,lora_alpha=16,lora_dropout=0,
                              target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    model.config.use_cache = False
    optimizer = torch.optim.AdamW(model.parameters(),lr=args.lr)
    def encode(text, task, target):
        prompt = tokenizer.apply_chat_template(messages(text,task,args.condition),tokenize=False,add_generation_prompt=True)
        prefix = tokenizer.encode(prompt,add_special_tokens=False)
        suffix = tokenizer.encode(target,add_special_tokens=False)+[tokenizer.eos_token_id]
        if len(prefix)+len(suffix)>args.max_length:
            raise ValueError('Overlength sample: refuse silent training truncation.')
        ids = torch.tensor([prefix+suffix],device='cuda')
        # 입력 지시는 정답 손실에서 제외한다. -100은 손실 계산에서 무시하는 표식이다.
        labels = ids.clone(); labels[:,:len(prefix)] = -100
        return ids, labels, len(suffix)
    encoded = []
    for row in rows:
        # 검수된 정답의 자모 순서를 사용한다. 모델 예측에서 정답을 추측하지 않는다.
        points = row['aux_points']
        auxiliary = ';'.join(a['char'] if args.condition=='B' else f"{a['char']}@{a['x']},{a['y']}" for a in points)
        tasks=[]
        for task,target in [('CONVERT',row['target']),('ANNOTATE',auxiliary)]:
            ids, labels, n = encode(row['text'],task,target)
            tasks.append((ids.cpu(),labels.cpu(),n))
        encoded.append(tasks)
    metadata = vars(args) | {'data_sha256':digest(args.data),'gpu':torch.cuda.get_device_name(0),
        'lora':{'r':8,'alpha':16,'dropout':0,'modules':['q_proj','v_proj']},
        'loss_weights':{'CONVERT':0.5,'ANNOTATE':0.5}, 'examples':len(rows),
        'target_tokens_per_epoch':{'main':sum(e[0][2] for e in encoded),'auxiliary':sum(e[1][2] for e in encoded)}}
    (out/'config.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
    rng = random.Random(args.seed)
    start=time.monotonic(); updates=0
    with open(out/'training.jsonl','w') as log:
        # epoch는 학습 자료 전체를 한 번 보는 회차다.
        for epoch in range(1,args.epochs+1):
            order=list(range(len(encoded))); rng.shuffle(order); model.train()
            totals=[0.,0.]
            for start_i in range(0,len(order),args.accumulation):
                group=order[start_i:start_i+args.accumulation]
                # 원문 8개에 대한 기울기를 누적한 뒤 한 번 가중치를 갱신한다.
                optimizer.zero_grad(set_to_none=True)
                for index in group:
                    for task_i,(ids,labels,_) in enumerate(encoded[index]):
                        ids,labels=ids.to('cuda'),labels.to('cuda')
                        loss=model(input_ids=ids,attention_mask=torch.ones_like(ids),labels=labels).loss
                        if not torch.isfinite(loss):
                            raise RuntimeError('Non-finite loss; stop experiment.')
                        totals[task_i]+=float(loss.detach())
                        # 각 과제 손실은 출력 토큰 평균이다. 주 과제와 보조 과제를 0.5씩 반영한다.
                        (loss*0.5/len(group)).backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
                optimizer.step(); updates+=1
            record={'epoch':epoch,'updates':updates,'main_loss':totals[0]/len(rows),
                'aux_loss':totals[1]/len(rows),'elapsed_seconds':time.monotonic()-start,
                'max_gpu_bytes':torch.cuda.max_memory_allocated()}
            log.write(json.dumps(record)+'\n'); log.flush(); print(record,flush=True)
            # 검증 자료로 회차를 선택할 수 있도록 각 회차의 어댑터를 저장한다.
            checkpoint=out/f'epoch_{epoch}'
            model.save_pretrained(checkpoint); tokenizer.save_pretrained(checkpoint)
    print('Training complete. Select checkpoint on validation only before opening test results.')

if __name__=='__main__':
    main()
