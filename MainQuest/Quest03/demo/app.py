"""학습 모델과 논문을 검증한 릴리즈 기록이 있을 때만 변환을 제공한다."""
import html
import argparse
import hashlib
import json
import threading
from pathlib import Path
from urllib.parse import urlparse
from jamo.prompts import messages

MODEL_ID='Qwen/Qwen2.5-0.5B-Instruct'
_loaded=None
_lock=threading.Lock()

def load_release():
    path=Path('release_manifest.json')
    if not path.exists():
        raise RuntimeError('학습 모델을 준비하고 있습니다. 아직 공개 변환을 제공하지 않습니다.')
    config=json.loads(path.read_text())
    if config.get('status')!='validated' or config.get('condition') not in ('B','C'):
        raise RuntimeError('검증된 학습 모델 정보가 필요합니다.')
    required=['revision','adapter','version','github_url','adapter_sha256']
    if any(not config.get(k) for k in required):
        raise RuntimeError('모델 또는 논문 연결 정보가 완성되지 않았습니다.')
    for key in ['github_url'] + (['paper_url'] if config.get('paper_url') else []):
        if urlparse(config[key]).scheme!='https':
            raise RuntimeError('공개 자료에는 HTTPS 링크를 사용해야 합니다.')
    weights=Path(config['adapter'])/'adapter_model.safetensors'
    if not weights.is_file() or hashlib.sha256(weights.read_bytes()).hexdigest()!=config['adapter_sha256']:
        raise RuntimeError('선택한 어댑터 파일의 지문이 일치하지 않습니다.')
    if not config.get('paper_url') and not Path(config.get('paper_file','')).is_file():
        raise RuntimeError('열람할 논문 PDF가 필요합니다.')
    return config

def check_input(text):
    # 입력 범위만 검사한다. 정답 생성기를 가져와 모델 출력을 대신하지 않는다.
    import unicodedata
    text=unicodedata.normalize('NFC',text)
    if not text or len(text)>24 or text!=text.strip():
        raise ValueError('앞뒤 공백 없이 한글 1~24자를 입력해 주세요.')
    if not any('가'<=c<='힣' for c in text):
        raise ValueError('한글이 필요합니다.')
    for c in text:
        if c not in ' .,!?' and not '가'<=c<='힣':
            raise ValueError('한글과 공백, . , ! ? 만 사용할 수 있습니다.')
        if '가'<=c<='힣' and (ord(c)-0xAC00)//28%21 in (9,10,11,14,15,16,19):
            raise ValueError('이번 연구 모델은 ㅘ·ㅙ·ㅚ·ㅝ·ㅞ·ㅟ·ㅢ가 포함된 글자를 지원하지 않습니다.')
    return text

def display_grid(raw):
    # 셀 폭만 같게 표시한다. 생성된 문자·공백·줄바꿈은 교정하지 않는다.
    lines=[]
    for row in raw.split('\n'):
        cells=''.join('<span style="display:inline-block;width:1.15em;text-align:center">'+
                      ('&nbsp;' if c==' ' else html.escape(c))+'</span>' for c in row)
        lines.append('<div style="min-height:1.7em;white-space:nowrap">'+cells+'</div>')
    return '<div style="font-size:24px;padding:20px;overflow:auto;line-height:1.7">'+''.join(lines)+'</div>'

def infer(text, config):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    global _loaded
    text=check_input(text)
    with _lock:
        if _loaded is None:
            tok=AutoTokenizer.from_pretrained(MODEL_ID,revision=config['revision'])
            model=AutoModelForCausalLM.from_pretrained(MODEL_ID,revision=config['revision'],torch_dtype=torch.float32)
            model=PeftModel.from_pretrained(model,config['adapter'])
            model.to('cuda' if torch.cuda.is_available() else 'cpu').eval()
            _loaded=(tok,model)
        tok,model=_loaded
        prompt=tok.apply_chat_template(messages(text),tokenize=True,add_generation_prompt=True,return_tensors='pt').to(model.device)
        with torch.inference_mode():
            generated=model.generate(input_ids=prompt,attention_mask=torch.ones_like(prompt),
                                    do_sample=False,max_new_tokens=256,pad_token_id=tok.eos_token_id)
        suffix=generated[0,prompt.shape[-1]:]
        raw=tok.decode(suffix,skip_special_tokens=True,clean_up_tokenization_spaces=False)
        truncated=len(suffix)==256 and suffix[-1].item()!=tok.eos_token_id
        notice='- 출력 잘림: 새 토큰 256개 상한 도달' if truncated else '- 빈 출력: 생성 문자 없음' if not raw else '- 모델 원시 출력\n- 자모·위치 오류 가능\n- 정답 교정 미적용'
        return display_grid(raw),raw,notice

def build_app():
    import gradio as gr
    try:
        config=load_release(); ready=True
    except RuntimeError as exc:
        config=None; ready=False; reason=str(exc)
    with gr.Blocks(title='자모로 쓰기') as app:
        gr.Markdown('# 자모로 쓰기\n- 정상 한글 입력 → 학습 모델의 자모 배치 생성\n- 공백·줄바꿈을 유지한 원시 출력 확인')
        gr.Markdown('**연구용 임시 데모**\n- Colab 세션 종료 시 접속 중단\n- 미세 조정 모델의 실제 생성 관찰\n- 정답 교정·대체 미적용')
        if not ready:
            gr.Markdown(reason)
        else:
            gr.Markdown('**평가 결과**\n- 테스트 배치 정답: **0/25**\n- 실패를 포함한 실제 모델 출력 제공')
        text=gr.Textbox(label='변환할 한글',placeholder='짧은 단어나 문구를 입력하세요',max_lines=1)
        gr.Markdown('- 입력 한도: 24자\n- 실제 테스트 길이: 2~8자\n- 지원 제외: 복합 방향 모음 ㅘ·ㅙ·ㅚ·ㅝ·ㅞ·ㅟ·ㅢ')
        button=gr.Button('자모로 변환',interactive=ready,variant='primary')
        visual=gr.HTML()
        raw=gr.Textbox(label='복사할 원문 출력',lines=4,interactive=False,show_copy_button=True)
        notice=gr.Markdown()
        if ready:
            def convert(text):
                try: return infer(text,config)
                except ValueError as exc: raise gr.Error(str(exc))
                except Exception: raise gr.Error('변환을 완료하지 못했습니다. 잠시 후 다시 시도해 주세요.')
            button.click(convert,inputs=text,outputs=[visual,raw,notice],concurrency_limit=1)
            gr.Examples(examples=['강지수','바다','노란 나비'],inputs=text)
            if config.get('paper_url'):
                gr.Markdown(f"[논문 읽기·다운로드]({config['paper_url']})")
            else:
                gr.File(value=config['paper_file'],label='영문 논문 PDF',interactive=False)
            gr.Markdown(f"- [연구 코드]({config['github_url']})\n- 모델 버전: {config['version']}\n- 학습 조건: {config['condition']} · 1회차\n- 선택 근거: 검증 동점 규칙 · 우수성 입증 아님")
    return app,config

def main():
    parser=argparse.ArgumentParser(description='선택한 학습 모델로 임시 데모를 실행합니다.')
    parser.add_argument('--share',action='store_true',help='공개 임시 링크 생성: 공개 범위 승인 후에만 사용')
    args=parser.parse_args()
    app,config=build_app()
    # 논문 파일 한 개만 배포 대상으로 지정한다. 작업 폴더 전체를 공유하지 않는다.
    allowed=[str(Path(config['paper_file']).resolve())] if config and config.get('paper_file') else []
    app.queue(max_size=8).launch(share=args.share,allowed_paths=allowed)

if __name__=='__main__':
    main()
