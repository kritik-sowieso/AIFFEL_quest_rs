"""Colab에서 학습 1단계가 가능한지 확인한다. 본 실험 성적은 아니다."""
import json
import subprocess
import time
from pathlib import Path

def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model
    report = {'status': 'started', 'started_at_unix': time.time()}
    out = Path('runs/pilot'); out.mkdir(parents=True, exist_ok=True)
    try:
        report['gpu'] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        if not report['gpu']:
            raise RuntimeError('GPU unavailable. Stop; do not start the full training run.')
        model_id = 'Qwen/Qwen2.5-0.5B-Instruct'
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32).to('cuda')
        report['model'] = model_id
        report['revision'] = getattr(model.config, '_commit_hash', None)
        model = get_peft_model(model, LoraConfig(r=8, lora_alpha=16, lora_dropout=0,
                                  target_modules=['q_proj','v_proj'], task_type='CAUSAL_LM'))
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
        from jamo.core import annotate, render
        prompt = tokenizer.apply_chat_template([{'role':'user','content':'[TASK=CONVERT] 강지수'}], tokenize=False, add_generation_prompt=True)
        prefix = tokenizer.encode(prompt, add_special_tokens=False)
        target = tokenizer.encode(render(annotate('강지수')), add_special_tokens=False)+[tokenizer.eos_token_id]
        ids = torch.tensor([prefix+target], device='cuda')
        labels = ids.clone(); labels[:, :len(prefix)] = -100
        start = time.monotonic()
        model.train()
        loss = model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels).loss
        loss.backward(); optimizer.step(); torch.cuda.synchronize()
        report.update(training_step_seconds=time.monotonic()-start, loss=float(loss.detach()),
                      max_gpu_bytes=torch.cuda.max_memory_allocated(), status='training_step_passed')
    except Exception as exc:
        report.update(status='failed', error=repr(exc))
        raise
    finally:
        report['packages'] = subprocess.check_output(['python','-m','pip','freeze'], text=True)
        (out/'pilot.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='packages'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
