"""Render and copy browser-ready Manim media, using this Python environment."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
for scene,name in [('AllMaskPrediction','all-mask'),('StructuredIDs','structured-ids')]:
    subprocess.run([sys.executable,'-m','manim','-qm','--fps','30',
                    '--media_dir',str(ROOT/'media'),str(ROOT/'manim_scenes'/'stamplus.py'),scene],check=True,cwd=ROOT)
    candidates=list((ROOT/'media'/'videos'/'stamplus').glob('*/'+scene+'.mp4'))
    source=max(candidates,key=lambda p:p.stat().st_mtime)
    dest=ROOT/'assets'/'videos'/(name+'.mp4')
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-sseof','-1','-i',str(dest),'-frames:v','1',str(dest.with_suffix('.jpg'))],check=True)
    print(dest)
