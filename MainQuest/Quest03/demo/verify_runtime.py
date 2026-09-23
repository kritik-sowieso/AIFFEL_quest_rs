"""선택된 실제 어댑터의 추론을 저장된 출력 3개와 대조한다.

새로운 성능 평가나 모델 선택이 아니라 배포 경로의 출력 보존 검사다.
"""
import json
import time
from pathlib import Path
from demo.app import infer, load_release


def main():
    config = load_release()
    cases = json.loads(Path('demo/verification_cases.json').read_text())
    assert len(cases) == 3
    records = []
    for case in cases:
        started = time.monotonic()
        _, raw, notice = infer(case['text'], config)
        records.append({'id': case['id'], 'text': case['text'], 'raw_output': raw,
                        'matches_recorded_prediction': raw == case['prediction'],
                        'seconds': time.monotonic()-started, 'notice': notice})
    result = {'purpose': '배포 경로의 원시 출력 보존 확인', 'condition': config['condition'],
              'epoch': config['epoch'], 'cases': records,
              'all_match': all(r['matches_recorded_prediction'] for r in records)}
    Path('runtime_verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['all_match']:
        raise RuntimeError('저장된 출력과 다릅니다. 차이를 확인한 뒤 공개해야 합니다.')
    config['runtime_status'] = 'raw_output_verified'
    Path('release_manifest.json').write_text(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
