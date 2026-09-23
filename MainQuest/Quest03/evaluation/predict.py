"""탐욕적 생성(greedy decoding)의 원시 출력을 기록한다.

테스트 전에 검증 자료로 선택한 설정 파일이 고정되어 있어야 한다.
"""
import argparse
import json
import time
from pathlib import Path
from jamo.core import read_jsonl, write_jsonl, digest, score
from jamo.prompts import messages

def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    p=argparse.ArgumentParser()
    p.add_argument('--data',required=True)
    p.add_argument('--split',choices=['validation','test'],required=True)
    p.add_argument('--condition',choices=['A','B','C'],required=True)
    p.add_argument('--adapter')
    p.add_argument('--revision',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--selection',default='evaluation/frozen_selection.json')
    a=p.parse_args()
    if Path(a.output).exists():
        raise ValueError('Refusing to overwrite raw predictions.')
    if a.condition!='A' and not a.adapter:
        raise ValueError('Trained conditions require a real adapter.')
    if a.condition=='A' and a.adapter:
        raise ValueError('Base condition must not load an adapter.')
    # 테스트 결과를 보고 모델을 다시 고르는 자료 누출을 막는다.
    if a.split=='test':
        choice=json.loads(Path(a.selection).read_text())
        if choice['revision']!=a.revision or choice['test_sha256']!=digest(a.data):
            raise ValueError('Frozen model or test data mismatch')
        if a.condition!='A' and choice['adapters'][a.condition]!=a.adapter:
            raise ValueError('Checkpoint differs from frozen validation selection')
    rows=read_jsonl(a.data)
    if any(r['split']!=a.split for r in rows):
        raise ValueError('Split mismatch')
    model_id='Qwen/Qwen2.5-0.5B-Instruct'
    tok=AutoTokenizer.from_pretrained(model_id,revision=a.revision)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=a.revision,torch_dtype=torch.float32).to(device)
    if a.adapter:
        model=PeftModel.from_pretrained(model,a.adapter)
    model.eval(); records=[]
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    for row in rows:
        encoded=tok.apply_chat_template(messages(row['text']),tokenize=True,add_generation_prompt=True,return_tensors='pt').to(device)
        t=time.monotonic()
        # 평가 중에는 기울기를 계산하지 않는다. 매 단계 가장 높은 확률의 토큰을 고른다.
        with torch.inference_mode():
            generated=model.generate(input_ids=encoded,attention_mask=torch.ones_like(encoded),max_new_tokens=256,
                                     do_sample=False,pad_token_id=tok.eos_token_id)
        new=generated[0,encoded.shape[-1]:]
        # 입력 부분을 제외한 생성 토큰만 읽는다. 공백 자동 정리를 꺼 배치 오류를 보존한다.
        prediction=tok.decode(new,skip_special_tokens=True,clean_up_tokenization_spaces=False)
        records.append(dict(id=row['id'],text=row['text'],condition=a.condition,prediction=prediction,
            target=row['target'],scores=score(prediction,row['target']),seconds=time.monotonic()-t,
            generated_tokens=len(new),hit_token_limit=bool(len(new)==256 and new[-1].item()!=tok.eos_token_id),
            adapter=a.adapter,revision=a.revision,data_sha256=digest(a.data)))
        write_jsonl(a.output,records)
    print(json.dumps({'n':len(records),'exact_grid':sum(r['scores']['exact_grid'] for r in records)/len(records)},indent=2))

if __name__=='__main__':
    main()
