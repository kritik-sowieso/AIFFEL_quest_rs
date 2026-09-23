"""공개 재현용 실행기: 동일 데이터·10회 학습·고정 5/10회 평가. 개인 승인 기록은 포함하지 않는다."""
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from jamo.core import digest, read_jsonl
from evaluation.analyze_baseline import detail, summarize, group_summary


def main():
    import argparse
    parser=argparse.ArgumentParser(description='공개 재현용 10회 학습. 새 작업 폴더와 GPU가 필요합니다.')
    parser.add_argument('--run-training',action='store_true',help='GPU 학습 시작을 명시적으로 선택합니다.')
    if not parser.parse_args().run_training:
        raise SystemExit('읽기 전용 기본 상태: 실제 재학습에는 --run-training이 필요합니다.')
    plan=json.loads(Path('extension_v2/frozen_plan.json').read_text())
    for split,path in plan['data_paths'].items():
        if digest(path)!=plan['data_sha256'][split]:
            raise RuntimeError('사전 고정 자료 지문 불일치: '+split)
    if Path('checkpoints').exists():
        raise RuntimeError('기존 결과를 덮어쓰지 않습니다. 별도 새 폴더가 필요합니다.')
    logs=Path('runs/extension');logs.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    status={'status':'running','plan_sha256':digest('extension_v2/frozen_plan.json'),
            'started_at_unix':time.time(),'purpose':'사전 고정 10회차 비교 · 5회차 대비 · 탐색적 구성요소 제거 실험'}
    def save_status():
        status['elapsed_seconds']=time.monotonic()-started
        (logs/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2))
    def run(name,args):
        remaining=int(5400-(time.monotonic()-started))
        if remaining<=0:raise TimeoutError('추가 실험 실행 상한 90분 도달')
        status['current_step']=name;save_status();print('시작:',name,flush=True)
        with open(logs/f'{name}.log','w') as f:
            subprocess.run([sys.executable,'-u',*args],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=remaining)
        print('완료:',name,flush=True)
    try:
        run('코드검사',['-m','unittest','discover','-s','tests','-v'])
        for condition in ['D','B','C']:
            run(f'학습_{condition}',['-m','training.train_v2','--condition',condition,'--epochs','10',
                 '--revision',plan['revision'],'--annotation-mode','synthetic_coordinates'])
        results={}
        # 주 비교는 10회차, 부 비교는 5회차다. 점수를 보고 다른 회차로 바꾸지 않는다.
        for condition in ['D','B','C']:
            results[condition]={}
            for epoch in [5,10]:
                results[condition][str(epoch)]={}
                for split in ['train_probe','validation','test']:
                    output=f'evaluation/raw/{condition}_{split}_epoch_{epoch}.jsonl'
                    run(f'평가_{condition}_{epoch}_{split}',['-m','evaluation.predict_v2',
                        '--data',plan['data_paths'][split],'--split',split,'--condition',condition,
                        '--adapter',f'checkpoints/{condition}/epoch_{epoch}','--revision',plan['revision'],
                        '--selection','extension_v2/frozen_plan.json','--output',output])
                    items=[detail(r) for r in read_jsonl(output)]
                    results[condition][str(epoch)][split]={'overall':summarize(items),'groups':group_summary(items),'items':items}
                    Path('evaluation/extension_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
        status['status']='completed'
    except Exception as exc:
        status.update(status='failed',error=repr(exc));raise
    finally:
        save_status()
        # 실패 시에도 생성된 결과를 보존한다. 원본 실험 폴더에는 접근하지 않는다.
        with zipfile.ZipFile('extension_results.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for folder in ['runs','evaluation','checkpoints','data','extension_v2','training','jamo','tests']:
                for path in Path(folder).rglob('*'):
                    if path.is_file() and '__pycache__' not in path.parts:
                        archive.write(path,str(path))
        print(json.dumps(status,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
