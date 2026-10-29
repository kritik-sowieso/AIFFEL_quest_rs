"""Dependency-free validation of slide IDs and all local HTML references."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.slides=[]; self.images=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='section' and 'slide' in attrs.get('class','').split():self.slides.append(attrs.get('id'))
        if tag=='img':self.images.append(attrs)
        for key in ['src','href','poster','data-zoom']:
            if attrs.get(key):self.refs.append(attrs[key])

doc=Document();doc.feed((ROOT/'index.html').read_text())
assert len(doc.ids)==len(set(doc.ids)), 'Duplicate IDs'
assert doc.slides==[f'{i:02}' for i in range(1,16)], doc.slides
for ref in doc.refs:
    url=urlsplit(ref)
    if url.scheme or url.netloc:continue
    if url.path:assert (ROOT/unquote(url.path)).is_file(), f'Missing asset: {ref}'
    elif url.fragment:assert url.fragment in doc.ids, f'Missing anchor: {ref}'
assert all('alt' in im for im in doc.images), 'Image without alt'
for video in (ROOT/'assets'/'videos').glob('*.mp4'):
    assert video.stat().st_size>10000, f'Empty video: {video}'
assert len(list((ROOT/'assets'/'videos').glob('*.mp4')))==2
print(f'PASS: {len(doc.slides)} slides, unique IDs, {len(doc.refs)} references, image alternatives, 2 rendered videos')
