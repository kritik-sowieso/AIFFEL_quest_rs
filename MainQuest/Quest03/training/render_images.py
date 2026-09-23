"""각 셀의 폭을 같게 하여 합성 정답 이미지를 만든다."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from jamo.core import annotate, render, write_jsonl

PILOT_TEXTS = ['가나다', '강지수', '챗지피티', '오늘', '한글', '구름', '기차', '했는데', '우리 집', '아 오늘 이거 하려고 했는데']

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--font', required=True)
    p.add_argument('--output', default='data/pilot')
    args = p.parse_args()
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(args.font, 36)
    rows = []
    for i, text in enumerate(PILOT_TEXTS):
        points = annotate(text)
        w = (max(a['x'] for a in points)+1)*48+48
        h = (max(a['y'] for a in points)+1)*56+48
        image = Image.new('RGB', (w,h), 'white')
        draw = ImageDraw.Draw(image)
        for a in points:
            draw.text((24+a['x']*48+24,24+a['y']*56+28), a['char'], font=font, fill='black', anchor='mm')
        item_id = f'pilot_{i:02d}'
        image.save(out/f'{item_id}.png')
        rows.append({'id':item_id, 'text':text, 'target':render(points), 'points':points,
                     'annotation_source':'synthetic_rule', 'split':'pilot_excluded_from_main_evaluation'})
    write_jsonl(out/'gold.jsonl', rows)
    print(f'{len(rows)} synthetic images saved; gold coordinates are NOT OCR output.')

if __name__ == '__main__':
    main()
