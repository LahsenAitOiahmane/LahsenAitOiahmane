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
        assert '@keyframes face-cycle' in svg and '@keyframes number-cycle' in svg
        assert 'prefers-reduced-motion' in svg
        assert not re.search(r'onload=|onclick=|https?://(?!www\.w3\.org/)', svg)
        assert '5,690' not in svg and '216 challenges' not in svg
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', svg)
    assert profile['platforms']['hackthebox'] in readme
    assert profile['platforms']['rootme'] in readme
    assert 'hardware' not in readme.lower()
    cache = json.loads((ROOT / 'data/public-github.json').read_text(encoding='utf-8'))
    assert set(cache) == {'public_repos', 'stars', 'checked_utc'}
    assert all(isinstance(cache[key], int) and cache[key] >= 0 for key in ('public_repos', 'stars'))
    print('Verified: all themes, animation, reduced motion, local assets, public-only counts, and profile links.')


if __name__ == '__main__':
    check()
