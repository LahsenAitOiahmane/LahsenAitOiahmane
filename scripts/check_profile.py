"""Validate profile images, layout, frame timing, and links."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from render_webp import parse_placement

ROOT = Path(__file__).resolve().parents[1]


def check():
    assert parse_placement('translate(110 78) scale(.76)') == [110,78,.76]
    assert parse_placement('translate(110 78) scale(0.76)') == [110,78,.76]
    try:
        parse_placement('translate(110 78) scale(76)')
    except ValueError:
        pass
    else:
        raise AssertionError('Oversized portrait scale must be rejected')
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
        portrait = next(n for n in tree.iter() if n.attrib.get('id')=='binary-portrait')
        frame_color = '#548000' if name.startswith('light') else '#b4ff57'
        assert sum(n.attrib.get('fill')==frame_color for n in portrait) > 50
        if 'mobile' in name:
            heading = next(n for n in tree if n.tag.rsplit('}',1)[-1]=='text')
            assert float(heading.attrib['y'])-float(heading.attrib['font-size']) >= 24
        animation = ROOT / 'assets' / f'profile-{name}.webp'
        assert animation.stat().st_size < 8*1024*1024, 'Profile image exceeded its download budget'
        with Image.open(animation) as im:
            assert im.is_animated and im.n_frames >= 200
            assert im.size == ((480, 1540) if 'mobile' in name else (1120,650))
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
    assert 'docs/PROFILE.md' not in readme
    assert not (ROOT/'docs/PROFILE.md').exists()
    assert not (ROOT/'docs/PERFORMANCE.md').exists()
    face = json.loads((ROOT / 'assets/source/face-luminance.json').read_text(encoding='utf-8'))
    assert len(face['glasses']) == face['width']*face['height']
    assert sum(face['glasses']) > 50, 'Glasses need their own color mask'
    assert sum(v==1 for v in face['glasses']) > 100, 'Lenses must be green, not just frames'
    assert sum(v==2 for v in face['glasses']) > 50
    from binary_flow import face_points,COUNT
    assert COUNT >= 3000 and len(face_points())==COUNT, 'Preserve full portrait detail'
    assert set(face)=={'width','height','luminance','glasses'}
    relief = json.loads((ROOT / 'assets/source/number-relief.json').read_text(encoding='utf-8'))
    assert {point['surface'] for point in relief['points']} == {'front', 'side'}
    assert max(point['shade'] for point in relief['points']) - min(point['shade'] for point in relief['points']) > .5
    cache = json.loads((ROOT / 'data/public-github.json').read_text(encoding='utf-8'))
    assert set(cache) == {'public_repos', 'stars', 'checked_utc'}
    assert all(isinstance(cache[key], int) and cache[key] >= 0 for key in ('public_repos', 'stars'))
    print('Verified: 30 fps WebP loops, no live SVG animations, static reduced-motion fallbacks, both themes, and profile links.')


if __name__ == '__main__':
    check()
