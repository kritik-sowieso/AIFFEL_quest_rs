"""공개 원시 출력 372개를 GPU 없이 다시 채점하고 저장 결과와 대조한다."""
import json
from pathlib import Path
from jamo.core import read_jsonl, digest, score
from evaluation.analyze_baseline import detail, summarize, group_summary

def main():
    plan=json.loads(Path('extension_v2/frozen_plan.json').read_text())
    report=json.loads(Path('extension_v2/report/results.json').read_text())
    total=0
    for split,path in plan['data_paths'].items():
        assert digest(path)==plan['data_sha256'][split], '자료 지문 불일치'
    for condition in ['D','B','C']:
        for epoch in [5,10]:
            for split in ['train_probe','validation','test']:
                filename=f'{condition}_{split}_epoch_{epoch}.jsonl'
                rows=read_jsonl('extension_v2/raw/'+filename)
                data={r['id']:r for r in read_jsonl(plan['data_paths'][split])}
                assert len(rows)==len(data) and {r['id'] for r in rows}==data.keys()
                assert digest('extension_v2/raw/'+filename)==report['audit']['raw_file_sha256']['evaluation/raw/'+filename]
                for row in rows:
                    assert row['text']==data[row['id']]['text'] and row['target']==data[row['id']]['target']
                    assert row['revision']==plan['revision'] and row['condition']==condition
                    assert row['adapter']==f'checkpoints/{condition}/epoch_{epoch}'
                    assert row['data_sha256']==plan['data_sha256'][split]
                    assert row['scores']==score(row['prediction'],row['target'])
                items=[detail(row) for row in rows]
                expected=report['conditions'][condition][str(epoch)][split]
                assert summarize(items)==expected['overall']
                assert group_summary(items)==expected['groups']
                total+=len(rows)
    for split in ['validation','test']:
        items=[detail(r) for r in read_jsonl(f'evaluation/raw/A_{split}.jsonl')]
        assert summarize(items)==report['baseline_A_reused'][split]['overall']
    assert total==372
    print('검수 통과: 추가 실험 18개 파일 · 372개 출력 · 기반 모델 A · 저장 집계와 일치')
    print('기존 테스트 재사용 · 탐색 결과 · 추가 학습 없음')

if __name__=='__main__':main()
