"""Extract cited figure regions from the user-supplied 18-page arXiv v1 PDF.

Usage: python scripts/extract_figures.py /path/to/STAMPlus.pdf
Requires Poppler's pdftoppm and Pillow. No source PDF is distributed.
Coordinates are proportions of each complete page, excluding its caption.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
from PIL import Image

REGIONS = {
    "fig3-comparison": (4, (.16,.068,.84,.508)),
    "fig3-result": (4, (.515,.346,.806,.473)),
    "fig5-pipeline": (7, (.077,.069,.903,.340)),
    "fig7-capabilities": (12, (.077,.423,.913,.773)),
    "fig9-latency": (15, (.518,.322,.912,.500)),
}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf',type=Path)
    args=parser.parse_args()
    out=Path(__file__).resolve().parents[1]/'assets'/'figures'
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        pages={}
        for name,(page,box) in REGIONS.items():
            if page not in pages:
                dest=Path(tmp)/str(page)
                subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','3000','-png','-singlefile',str(args.pdf),str(dest)],check=True)
                pages[page]=Image.open(str(dest)+'.png').convert('RGB')
            im=pages[page]
            region=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box)))
            region.save(out/(name+'.webp'),quality=94,method=6)
            print(name,region.size)

if __name__=='__main__':
    main()
