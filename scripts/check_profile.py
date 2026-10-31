"""Validate published artwork and its references, including privacy constraints."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def check():
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    profile = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))
    for relative in re.findall(r'(?:src|srcset)="(\./[^"]+)"', readme):
        assert (ROOT / relative).is_file(), f'Missing image: {relative}'
    for name in ('dark', 'light', 'dark-mobile', 'light-mobile'):
        path = ROOT / 'assets' / f'profile-{name}.svg'
        svg = path.read_text(encoding='utf-8')
        tree = ET.fromstring(svg)
        assert not {node.tag.rsplit('}', 1)[-1] for node in tree.iter()} & {'script', 'foreignObject', 'image'}
        tags = {node.tag.rsplit('}', 1)[-1] for node in tree.iter()}
        assert not tags & {'animateMotion', 'animate', 'animateTransform'}, 'Do not restore expensive live particle animations'
        assert '@keyframes' not in svg, 'Reduced-motion SVG must be fully static'
        animation = ROOT / 'assets' / f'profile-{name}.webp'
        assert animation.stat().st_size < 8*1024*1024, 'Profile image exceeded its download budget'
        with Image.open(animation) as im:
            assert im.is_animated and im.n_frames >= 200
            assert im.size == ((480, 1225) if 'mobile' in name else (1120,620))
            duration = 0
            small_frames = 0
            for index in range(im.n_frames):
                im.seek(index)
                im.load()
                delay = im.info['duration']
                duration += delay
                small_frames += delay <= 34
            assert duration == 16000, f'Loop duration changed: {duration}'
            assert small_frames >= 200, 'Motion must play at 30 fps, not a low-frame-rate preview'
        assert not re.search(r'onload=|onclick=|https?://(?!www\.w3\.org/)', svg)
        assert '5,690' not in svg and '216 challenges' not in svg
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', svg)
    assert profile['platforms']['hackthebox'] in readme
    assert profile['platforms']['rootme'] in readme
    assert 'prefers-reduced-motion: reduce' in readme
    assert 'hardware' not in readme.lower()
    face = json.loads((ROOT / 'assets/source/face-luminance.json').read_text(encoding='utf-8'))
    assert face['width'] <= 36 and face['height'] <= 46, 'Do not publish a detailed portrait grid'
    relief = json.loads((ROOT / 'assets/source/number-relief.json').read_text(encoding='utf-8'))
    assert {point['surface'] for point in relief['points']} == {'front', 'side'}
    assert max(point['shade'] for point in relief['points']) - min(point['shade'] for point in relief['points']) > .5
    cache = json.loads((ROOT / 'data/public-github.json').read_text(encoding='utf-8'))
    assert set(cache) == {'public_repos', 'stars', 'checked_utc'}
    assert all(isinstance(cache[key], int) and cache[key] >= 0 for key in ('public_repos', 'stars'))
    print('Verified: 30 fps WebP loops, no live SVG animations, static reduced-motion fallbacks, both themes, and profile links.')


if __name__ == '__main__':
    check()
