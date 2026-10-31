"""Validate published artwork and its references, including privacy constraints."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

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
        motions = [node for node in tree.iter() if node.tag.rsplit('}', 1)[-1] == 'animateMotion']
        assert len(motions) >= 1800, 'Expected a continuous particle morph'
        assert all('C' in node.attrib['path'] and node.attrib['keyPoints'] == '0;0;.5;.5;1;1' for node in motions)
        assert 'face-cycle' not in svg and 'number-cycle' not in svg, 'The old crossfade must not return'
        assert 'static-portrait' in svg and 'fluid-particles' in svg
        assert 'prefers-reduced-motion' in svg
        assert not re.search(r'onload=|onclick=|https?://(?!www\.w3\.org/)', svg)
        assert '5,690' not in svg and '216 challenges' not in svg
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', svg)
    assert profile['platforms']['hackthebox'] in readme
    assert profile['platforms']['rootme'] in readme
    assert 'hardware' not in readme.lower()
    face = json.loads((ROOT / 'assets/source/face-luminance.json').read_text(encoding='utf-8'))
    assert face['width'] <= 36 and face['height'] <= 46, 'Do not publish a detailed portrait grid'
    relief = json.loads((ROOT / 'assets/source/number-relief.json').read_text(encoding='utf-8'))
    assert {point['surface'] for point in relief['points']} == {'front', 'side'}
    assert max(point['shade'] for point in relief['points']) - min(point['shade'] for point in relief['points']) > .5
    cache = json.loads((ROOT / 'data/public-github.json').read_text(encoding='utf-8'))
    assert set(cache) == {'public_repos', 'stars', 'checked_utc'}
    assert all(isinstance(cache[key], int) and cache[key] >= 0 for key in ('public_repos', 'stars'))
    print('Verified: fluid particle morph, shaded numeral, medium-detail source, both themes, reduced motion, and profile links.')


if __name__ == '__main__':
    check()
