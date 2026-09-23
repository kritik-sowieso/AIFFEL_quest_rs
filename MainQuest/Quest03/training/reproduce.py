"""공개 재현용 실행기: 같은 198/25/25 분할과 고정된 선택·평가 절차를 실행한다.

원실험의 개인 실행 승인 확인 부분만 제외했다. 학습·선택·평가 알고리즘은 같다.
이 파일을 실행하면 GPU 학습을 수행하므로 재현할 때만 실행한다.
"""
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from jamo.core import read_jsonl, digest

REVISION='7ae557604adf67be50417f59c2c2f167def9a775'

def main():
    logdir=Path('runs/main');logdir.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    metadata={'status':'running','started_at_unix':time.time(),'revision':REVISION,'annotation_source':'synthetic_coordinates'}
    (logdir/'status.json').write_text(json.dumps(metadata,indent=2))
    def run(name, args):
        remaining=int(5400-(time.monotonic()-started))
        if remaining<=0: raise TimeoutError('Main run exceeded 90-minute budget')
        print('시작:',name,flush=True)
        with open(logdir/f'{name}.log','w') as f:
            subprocess.run([sys.executable,'-u',*args],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=remaining)
        print('완료:',name,flush=True)
    def metric(path, epoch):
        rows=read_jsonl(path)
        if len(rows)!=25: raise ValueError('Incomplete validation output')
        return (sum(r['scores']['exact_grid'] for r in rows),
                sum(r['scores']['character_inventory'] for r in rows),-epoch)
    try:
        run('tests',['-m','unittest','discover','-s','tests','-v'])
        adapters={}; selected_metrics={}
        for condition in ['B','C']:
            run(f'train_{condition}',['-m','training.train','--condition',condition,'--revision',REVISION,'--annotation-mode','synthetic_coordinates'])
            candidates=[]
            for epoch in range(1,6):
                adapter=f'checkpoints/{condition}/epoch_{epoch}'
                output=f'evaluation/raw/{condition}_validation_epoch_{epoch}.jsonl'
                run(f'validation_{condition}_{epoch}',['-m','evaluation.predict','--data','data/validation.jsonl',
                    '--split','validation','--condition',condition,'--adapter',adapter,'--revision',REVISION,'--output',output])
                candidates.append((metric(output,epoch),adapter,output))
            best=max(candidates,key=lambda x:x[0])
            selected_metrics[condition]=best[0];adapters[condition]=best[1]
        run('validation_A',['-m','evaluation.predict','--data','data/validation.jsonl','--split','validation',
            '--condition','A','--revision',REVISION,'--output','evaluation/raw/A_validation.jsonl'])
        # 체크포인트(checkpoint) 동점이면 더 이른 학습 회차(epoch)를 선택한다.
        # 배포 후보는 검증 정답 수·자모 보존 수로 비교하고, B/C 완전 동점이면 B를 선택한다.
        deploy='C' if selected_metrics['C'][:2]>selected_metrics['B'][:2] else 'B'
        selection={'revision':REVISION,'test_sha256':digest('data/test.jsonl'),'adapters':adapters,
            'deploy_condition':deploy,'validation_metrics':selected_metrics,'frozen_at_unix':time.time(),
            'selection_rule':'validation exact grid, then inventory, then earlier epoch; B on deployment ties',
            'max_new_tokens':256,'do_sample':False}
        path=Path('evaluation/frozen_selection.json')
        if path.exists(): raise ValueError('Refusing to overwrite selection')
        path.write_text(json.dumps(selection,indent=2))
        for condition in ['A','B','C']:
            args=['-m','evaluation.predict','--data','data/test.jsonl','--split','test','--condition',condition,
                  '--revision',REVISION,'--output',f'evaluation/raw/{condition}_test.jsonl']
            if condition!='A':args+=['--adapter',adapters[condition]]
            run(f'test_{condition}',args)
        run('summary',['-m','evaluation.summarize',*[f'evaluation/raw/{c}_test.jsonl' for c in 'ABC']])
        metadata['status']='completed'
    except Exception as exc:
        metadata.update(status='failed',error=repr(exc));raise
    finally:
        metadata['elapsed_seconds']=time.monotonic()-started
        (logdir/'status.json').write_text(json.dumps(metadata,indent=2))
        with zipfile.ZipFile('main_experiment_results.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for folder in ['runs/main','evaluation','checkpoints']:
                for path in Path(folder).rglob('*'):
                    if path.is_file() and '__pycache__' not in path.parts:
                        archive.write(path,str(path))
            for filename in ['data/train_reviewed.jsonl','data/validation.jsonl','data/test.jsonl']:
                archive.write(filename,filename)
        print(json.dumps(metadata),flush=True)

if __name__=='__main__':
    main()
