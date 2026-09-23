"""기존 원시 출력의 문자·좌표 오류를 재분석한다. 추가 모델 호출은 없다."""
import argparse
import collections
import json
from pathlib import Path
from jamo.core import canonical, decompose, HORIZONTAL, read_jsonl


def edit_distance(a, b):
    # 편집 거리: 삽입·삭제·치환에 각각 비용 1을 부여한다.
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j-1] + (x != y)))
        previous = current
    return previous[-1]


def points(text):
    # 빈칸은 분모에서 제외한다. 설명 문자도 오답 위치로 센다.
    return {(x, y, c) for y, row in enumerate(canonical(text).split('\n'))
            for x, c in enumerate(row) if not c.isspace()}


def detail(row):
    p, t = canonical(row['prediction']), canonical(row['target'])
    pc = collections.Counter(c for c in p if not c.isspace())
    tc = collections.Counter(c for c in t if not c.isspace())
    syllables = [decompose(c) for c in row['text'] if '가' <= c <= '힣']
    a = ''.join(c for c in p if not c.isspace())
    b = ''.join(c for c in t if not c.isspace())
    return dict(id=row['id'], text=row['text'], prediction=p, target=t,
                exact_grid=int(p == t), inventory_exact=int(pc == tc),
                predicted_chars=sum(pc.values()), target_chars=sum(tc.values()),
                inventory_matches=sum((pc & tc).values()), coordinate_matches=len(points(p) & points(t)),
                missing=sum((tc-pc).values()), extra=sum((pc-tc).values()),
                nonspace_edit_distance=edit_distance(a,b),
                composed_hangul_present=any('가' <= c <= '힣' for c in p),
                code_fence_present='```' in p, hit_token_limit=row['hit_token_limit'],
                empty=not p, syllable_count=len(syllables), has_word_space=' ' in row['text'],
                has_final=any(t for _,_,t in syllables),
                has_horizontal_vowel=any(v in HORIZONTAL for _,v,_ in syllables))


def summarize(rows):
    total = lambda key: sum(r[key] for r in rows)
    np, nt = total('predicted_chars'), total('target_chars')
    im, cm = total('inventory_matches'), total('coordinate_matches')
    return dict(n=len(rows), exact_grid=total('exact_grid'), inventory_exact=total('inventory_exact'),
                inventory_precision=im/np if np else 0, inventory_recall=im/nt if nt else 0,
                inventory_f1=2*im/(np+nt) if np+nt else 0,
                coordinate_f1=2*cm/(np+nt) if np+nt else 0,
                nonspace_cer=total('nonspace_edit_distance')/nt if nt else 0,
                missing=total('missing'), extra=total('extra'),
                composed_hangul_present=total('composed_hangul_present'),
                code_fence_present=total('code_fence_present'),
                hit_token_limit=total('hit_token_limit'), empty=total('empty'))


def group_summary(rows):
    # 소집단 비교는 표본 수를 함께 기록한다. 관찰 차이를 인과 효과로 해석하지 않는다.
    groups={}
    for key in ['has_word_space','has_final','has_horizontal_vowel']:
        groups[key]={str(value):summarize([r for r in rows if r[key]==value]) for value in [False,True]}
    groups['syllable_count']={label:summarize([r for r in rows if low<=r['syllable_count']<=high])
                              for label,low,high in [('1-2',1,2),('3-4',3,4),('5+',5,24)]}
    return groups


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw-dir', required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result={'purpose':'기존 결과에 대한 사후 기술 분석 · 새 성능 평가 아님','conditions':{}}
    for condition in 'ABC':
        rows=[detail(r) for r in read_jsonl(Path(args.raw_dir)/f'{condition}_test.jsonl')]
        groups=group_summary(rows)
        result['conditions'][condition]={'overall':summarize(rows),'groups':groups,'items':rows}
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for c, obj in result['conditions'].items():
        print(c,json.dumps(obj['overall'],ensure_ascii=False))


if __name__=='__main__': main()
