"""정답 주석을 만드는 규칙 도구. 서비스의 모델 추론에는 사용하지 않는다."""
import collections
import hashlib
import json
import unicodedata

INITIAL = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
MEDIAL = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
FINAL = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'
HORIZONTAL = set('ㅗㅛㅜㅠㅡ')
MIXED = set('ㅘㅙㅚㅝㅞㅟㅢ')

def decompose(char):
    n = ord(char) - 0xAC00
    if not 0 <= n < 11172:
        raise ValueError('완성형 한글만 분해할 수 있습니다.')
    return INITIAL[n // 588], MEDIAL[n // 28 % 21], FINAL[n % 28].strip()

def validate_input(text):
    text = unicodedata.normalize('NFC', text)
    if not text or len(text) > 24 or text != text.strip():
        raise ValueError('앞뒤 공백 없이 1~24자를 입력하세요.')
    if not any('가' <= c <= '힣' for c in text):
        raise ValueError('한글이 필요합니다.')
    for c in text:
        if c not in ' .,!?' and not '가' <= c <= '힣':
            raise ValueError('한글, 공백, 마침표, 쉼표, 느낌표, 물음표만 지원합니다.')
        if '가' <= c <= '힣' and decompose(c)[1] in MIXED:
            raise ValueError('이번 파일럿에서는 복합 방향 모음을 제외합니다: ㅘㅙㅚㅝㅞㅟㅢ')
    return text

def annotate(text, style='aligned'):
    """자모 한 개를 한 셀에 놓고 음절 사이 한 셀을 비우는 정답 생성기.

    된소리와 겹받침은 유니코드 자모 한 글자로 유지한다.
    본 실험은 aligned(윗줄 정렬)만 사용한다.
    """
    text = validate_input(text)
    if style not in ('aligned', 'staircase'):
        raise ValueError(style)
    points, x, y = [], 0, 0
    for i, c in enumerate(text):
        if c == ' ':
            x += 2
            continue
        if not '가' <= c <= '힣':
            points.append(dict(char=c, x=x, y=y, syllable=i))
            x += 1
            continue
        l, v, t = decompose(c)
        local = [(l, 0, 0)]
        if v in HORIZONTAL:
            local += [(v, 0, 1)]
            if t:
                local += [(t, 0, 2)]
            width = 1
        else:
            local += [(v, 1, 0)]
            if t:
                local += [(t, 0, 1)]
            width = 2
        points.extend(dict(char=j, x=x+dx, y=y+dy, syllable=i) for j, dx, dy in local)
        x += width + 1
        if style == 'staircase':
            y += max(p[2] for p in local)
    return points

def render(points):
    rows = [[' '] * (max(p['x'] for p in points)+1) for _ in range(max(p['y'] for p in points)+1)]
    for p in points:
        if rows[p['y']][p['x']] != ' ':
            raise ValueError('좌표 충돌')
        rows[p['y']][p['x']] = p['char']
    return '\n'.join(''.join(r).rstrip() for r in rows)

def canonical(text):
    """줄바꿈 표현, 줄 끝 공백, 바깥 빈 줄만 통일한다.

    앞쪽 공백·설명·코드 블록을 제거하거나 자모를 교정하지 않는다.
    """
    return '\n'.join(r.rstrip(' ') for r in text.replace('\r\n', '\n').split('\n')).strip('\n')

def score(prediction, target):
    p, t = canonical(prediction), canonical(target)
    pc = collections.Counter(c for c in p if not c.isspace())
    tc = collections.Counter(c for c in t if not c.isspace())
    return dict(exact_grid=int(p == t), character_inventory=int(pc == tc),
                missing=sum((tc-pc).values()), extra=sum((pc-tc).values()))

def digest(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False)+'\n')
