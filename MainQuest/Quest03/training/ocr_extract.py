"""OCR 원시 결과를 저장한다. 알고 있는 정답 좌표로 대체하지 않는다."""
import argparse
import json
from pathlib import Path

def main():
    import easyocr
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', default='data/images/train')
    parser.add_argument('--output', default='data/ocr_raw.jsonl')
    args = parser.parse_args()
    reader = easyocr.Reader(['ko','en'], gpu=False)
    images = sorted(Path(args.images).glob('*.png'))
    if not images:
        raise RuntimeError('No training images found.')
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        for path in images:
            detections = reader.readtext(str(path), detail=1, paragraph=False)
            row = {'id':path.stem, 'image':str(path), 'engine':'easyocr',
                   'detections':[{'box':[[float(x),float(y)] for x,y in box],
                                  'text':text, 'confidence':float(conf)} for box,text,conf in detections]}
            f.write(json.dumps(row, ensure_ascii=False)+'\n')
            f.flush()
    print(f'Saved {len(images)} raw OCR records. These are not approved character-coordinate labels.')

if __name__ == '__main__':
    main()
