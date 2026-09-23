"""모델을 평가하기 전에 합성 자료와 분할을 고정한다.

같은 단어가 들어간 문구는 한 그룹으로 묶어 자료 누출을 줄인다.
그룹을 쪼개서 수량을 맞추지 않고 실제 분할 수량을 기록한다.
"""
import json
import random
import unicodedata
from pathlib import Path
from jamo.core import annotate,render,validate_input,write_jsonl,digest

def main():
    out=Path('data/draft'); out.mkdir(parents=True,exist_ok=True)
    if (out/'manifest.json').exists():
        raise RuntimeError('Data already frozen; do not regenerate after seeing results.')
    texts=Path('data/candidate_texts.txt').read_text().splitlines()
    eligible=[]; rejected=[]
    from training.render_images import PILOT_TEXTS
    for text in texts:
        try:
            text=validate_input(text)
            if text in PILOT_TEXTS:
                raise ValueError('Used in pilot')
            eligible.append(text)
        except ValueError as exc:
            rejected.append({'text':text,'reason':str(exc)})
    if len(set(eligible))!=len(eligible):
        raise ValueError('Duplicate originals')
    # 단어 하나인 입력과 그 단어가 그대로 들어 있는 문구를 같은 그룹으로 묶는다.
    parents=list(range(len(eligible)))
    def root(i):
        while parents[i]!=i:
            parents[i]=parents[parents[i]]; i=parents[i]
        return i
    def union(a,b):
        parents[root(a)]=root(b)
    single={t:i for i,t in enumerate(eligible) if ' ' not in t}
    for i,text in enumerate(eligible):
        for token in text.split():
            if token in single:
                union(i,single[token])
    groups={}
    for i,text in enumerate(eligible):
        groups.setdefault(root(i),[]).append((i,text))
    rng=random.Random(20260923)
    groups=list(groups.values()); rng.shuffle(groups)
    # 약 10%를 검증(validation), 다음 10%를 테스트(test), 나머지를 학습(train)에 둔다.
    # 그룹을 보존하므로 처음 계획한 수량과 실제 수량은 다를 수 있다.
    bins={'validation':[],'test':[],'train':[]}
    target=round(len(eligible)*0.1)
    for group_id,group in enumerate(groups):
        split='validation' if len(bins['validation'])<target else 'test' if len(bins['test'])<target else 'train'
        for i,text in group:
            points=annotate(text)
            bins[split].append(dict(id=f'mq03_{i:03d}',text=text,target=render(points),points=points,
                split=split,group_id=f'g{group_id:03d}',annotation_source='synthetic_coordinates',
                review_approved=False))
    for split,rows in bins.items():
        write_jsonl(out/f'{split}.jsonl',rows)
    write_jsonl(out/'excluded.jsonl',rejected)
    manifest={'status':'draft_labels_not_approved_for_training','seed':20260923,
      'style':'aligned-v0.1','source':'newly authored generic Korean candidates; no scraped corpus',
      'counts':{s:len(rows) for s,rows in bins.items()},'excluded':len(rejected),
      'split_rule':'group exact word-containing phrases; no same group across splits',
      'limitations':'Partial morpheme overlap remains; this is new-phrase composition, not unseen-jamo generalization.',
      'candidate_sha256':digest('data/candidate_texts.txt'),
      'files':{s:digest(out/f'{s}.jsonl') for s in bins}}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
