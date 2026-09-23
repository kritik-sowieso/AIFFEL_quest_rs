"""실제 예측 기록을 요약한다. 미실행 결과를 0점으로 채우지 않는다."""
import argparse
import json
from pathlib import Path
from jamo.core import read_jsonl

def main():
    p=argparse.ArgumentParser()
    p.add_argument('files',nargs='+')
    p.add_argument('--output',default='evaluation/summary.json')
    a=p.parse_args(); groups={}; summary={}
    for name in a.files:
        rows=read_jsonl(name)
        if not rows: raise ValueError(f'No observations: {name}')
        condition=rows[0]['condition']
        if condition in groups: raise ValueError('Multiple files for one condition')
        if any(r['condition']!=condition for r in rows): raise ValueError('Mixed conditions')
        groups[condition]={r['id']:r for r in rows}
        if len(groups[condition])!=len(rows): raise ValueError('Duplicate predictions')
        n=len(rows)
        summary[condition]={'n':n,'correct':sum(r['scores']['exact_grid'] for r in rows),
            'character_inventory_correct':sum(r['scores']['character_inventory'] for r in rows),
            'mean_seconds':sum(r['seconds'] for r in rows)/n,
            'truncated':sum(r['hit_token_limit'] for r in rows)}
        summary[condition]['accuracy']=summary[condition]['correct']/n
    if 'B' in groups and 'C' in groups:
        b,c=groups['B'],groups['C']
        if b.keys()!=c.keys(): raise ValueError('Unpaired test items')
        for key in b:
            if (b[key]['text'],b[key]['target'],b[key]['data_sha256'])!=(c[key]['text'],c[key]['target'],c[key]['data_sha256']):
                raise ValueError('Different comparison data')
        pairs=[(b[k]['scores']['exact_grid'],c[k]['scores']['exact_grid']) for k in b]
        summary['C_minus_B']={'accuracy_difference':sum(y-x for x,y in pairs)/len(pairs),
            'C_only_correct':sum(x==0 and y==1 for x,y in pairs),
            'B_only_correct':sum(x==1 and y==0 for x,y in pairs),
            'interpretation':'Descriptive single-seed pilot; no general superiority claim.'}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
