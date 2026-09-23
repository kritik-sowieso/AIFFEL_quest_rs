"""내려받은 실제 결과를 검수하고 논문용 수치·그림을 만든다.

학습이나 모델 선택을 다시 수행하지 않는다. 실패한 출력도 그대로 집계한다.
"""
import argparse
import json
from pathlib import Path
from jamo.core import read_jsonl, score, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--received', default='runs/main_received')
    args = parser.parse_args()
    root = Path(args.received)
    state = json.loads((root/'runs/main/status.json').read_text())
    if state['status'] != 'completed':
        raise ValueError('완료되지 않은 실험을 최종 성적으로 요약하지 않습니다.')
    choice = json.loads((root/'evaluation/frozen_selection.json').read_text())
    raw = root/'evaluation/raw'
    report = {'status': state, 'selection': choice, 'conditions': {}, 'validation': {}}
    test_hash = digest(root/'data/test.jsonl')
    assert test_hash == choice['test_sha256'] == digest('data/test.jsonl')
    tests = {}
    for condition in 'ABC':
        rows = read_jsonl(raw/f'{condition}_test.jsonl')
        assert len(rows) == 25 and len({r['id'] for r in rows}) == 25
        for r in rows:
            assert r['scores'] == score(r['prediction'], r['target'])
            assert r['revision'] == choice['revision'] and r['data_sha256'] == test_hash
            assert r['adapter'] == (None if condition == 'A' else choice['adapters'][condition])
        tests[condition] = {r['id']: r for r in rows}
        n = len(rows)
        report['conditions'][condition] = {
            'n': n,
            'grid_correct': sum(r['scores']['exact_grid'] for r in rows),
            'inventory_correct': sum(r['scores']['character_inventory'] for r in rows),
            'mean_seconds': sum(r['seconds'] for r in rows)/n,
            'truncated': sum(r['hit_token_limit'] for r in rows),
            'empty': sum(not r['prediction'] for r in rows),
            'inventory_right_layout_wrong': sum(r['scores']['character_inventory'] and not r['scores']['exact_grid'] for r in rows),
            'total_missing': sum(r['scores']['missing'] for r in rows),
            'total_extra': sum(r['scores']['extra'] for r in rows),
        }
    assert tests['A'].keys() == tests['B'].keys() == tests['C'].keys()
    for k in tests['A']:
        assert len({(tests[c][k]['text'], tests[c][k]['target']) for c in 'ABC'}) == 1
    for condition in 'BC':
        values = []
        for epoch in range(1, 6):
            rows = read_jsonl(raw/f'{condition}_validation_epoch_{epoch}.jsonl')
            assert len(rows) == 25
            values.append({'epoch': epoch, 'grid_correct': sum(r['scores']['exact_grid'] for r in rows),
                           'inventory_correct': sum(r['scores']['character_inventory'] for r in rows)})
        best = max(values, key=lambda x: (x['grid_correct'], x['inventory_correct'], -x['epoch']))
        assert choice['adapters'][condition] == f"checkpoints/{condition}/epoch_{best['epoch']}"
        config_path = root/f'checkpoints/{condition}/config.json'
        if not config_path.exists():
            config_path = root/f'runs/training_{condition}_config.json'
        config = json.loads(config_path.read_text())
        assert config['data_sha256'] == digest('data/train_reviewed.jsonl')
        log_path = root/f'checkpoints/{condition}/training.jsonl'
        if not log_path.exists():
            log_path = root/f'runs/training_{condition}_training.jsonl'
        log = read_jsonl(log_path)
        assert len(log) == 5 and log[-1]['updates'] == 125
        report['validation'][condition] = values
        report['conditions'][condition]['training'] = {'config': config, 'log': log}
    bm = choice['validation_metrics']['B'][:2]
    cm = choice['validation_metrics']['C'][:2]
    assert choice['deploy_condition'] == ('C' if cm > bm else 'B')
    b, c = tests['B'], tests['C']
    report['paired'] = {
        'C_only_correct': [k for k in b if c[k]['scores']['exact_grid'] and not b[k]['scores']['exact_grid']],
        'B_only_correct': [k for k in b if b[k]['scores']['exact_grid'] and not c[k]['scores']['exact_grid']],
        'both_correct': [k for k in b if b[k]['scores']['exact_grid'] and c[k]['scores']['exact_grid']],
        'neither_correct': [k for k in b if not b[k]['scores']['exact_grid'] and not c[k]['scores']['exact_grid']],
    }
    report['audit'] = '원본 조건별 25개, 채점 재계산, 짝지음, 데이터 지문, 검증 선택 및 어댑터 일치 확인'
    out = Path('evaluation/report'); out.mkdir(parents=True, exist_ok=True)
    (out/'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.0), layout='constrained')
    colors = {'A': '#8795a1', 'B': '#387b9c', 'C': '#b65a42'}
    for condition in 'BC':
        log = report['conditions'][condition]['training']['log']
        axes[0].plot([x['epoch'] for x in log], [x['main_loss'] for x in log],
                     marker='o', label=condition, color=colors[condition])
    axes[0].set(xlabel='Training epoch', ylabel='Conversion token loss', xticks=range(1, 6))
    axes[0].legend(title='Condition', frameon=False)
    for i, condition in enumerate('ABC'):
        info = report['conditions'][condition]
        value = info['truncated']
        axes[1].bar(i, value, 0.6, color=colors[condition])
        axes[1].text(i, value+0.3, str(value), ha='center', fontsize=9)
    axes[1].set(xticks=range(3), xticklabels=list('ABC'), ylabel='Truncated test outputs (out of 25)', ylim=(0, 11))
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=0.15); ax.set_axisbelow(True)
    Path('paper/figures').mkdir(exist_ok=True)
    fig.savefig('paper/figures/main_results.png', dpi=240)
    plt.close(fig)
    print(json.dumps({k: {n: v for n, v in x.items() if n != 'training'}
                      for k, x in report['conditions'].items()}, ensure_ascii=False, indent=2))
    print('검증 선택:', choice['deploy_condition'], choice['adapters'])
    print('짝지은 결과:', {k: len(v) for k, v in report['paired'].items()})


if __name__ == '__main__':
    main()
