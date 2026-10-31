"""Portrait geometry and colors for the binary flow animation."""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACE = json.loads((ROOT / 'assets/source/face-luminance.json').read_text(encoding='utf-8'))
NUMBER = json.loads((ROOT / 'assets/source/number-relief.json').read_text(encoding='utf-8'))
DURATION = 16
COUNT = sum(lum >= 10 or bool(glass) for lum,glass in zip(FACE['luminance'],FACE['glasses']))

FLOW_CSS = """
text{font-family:'Roboto Mono','Liberation Mono','Courier New',monospace;white-space:pre}
"""


def blend(a, b, t):
    av, bv = [int(a[i:i+2], 16) for i in (1, 3, 5)], [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x+(y-x)*t):02x}' for x, y in zip(av, bv))


def face_points():
    """Preserve every visible cell in the detailed portrait grid."""
    w, h = FACE['width'], FACE['height']
    points = []
    for y in range(h):
        for x in range(w):
            lum = FACE['luminance'][y*w+x]
            glass = FACE['glasses'][y*w+x]
            if lum < 10 and not glass:
                continue
            px = x*341.6/w
            py = 9.2+y*518.4/h
            shade = max(0, min(1, lum/235))
            points.append((px,py,shade,glass))
    return sorted(points,key=lambda p:p[1]+p[0]*.12)


def number_points():
    candidates = sorted(NUMBER['points'], key=lambda p: p['y']+p['x']*.12)
    # Preserve both front faces and shallow side faces in a fixed-size particle set.
    indices = [int((i+.5)*len(candidates)/COUNT) for i in range(COUNT)]
    return [(candidates[i]['x'], candidates[i]['y'], candidates[i]['shade']) for i in indices]


def face_color(c, shade, glasses=False):
    if glasses == 2:
        return c['brand'] if c['bg']=='#000000' else c['accent']
    if glasses == 1:
        green = c['brand'] if c['bg']=='#000000' else c['accent']
        return blend(c['bg'],green,.12+.88*shade**.75)
    strength = .12 + .88*shade
    return blend(c['bg'], c['portrait'], strength)


def relief_color(c, shade):
    if c['bg'] == '#000000':
        if shade < .4:
            return blend('#233a08', '#6daf23', shade/.4)
        if shade < .72:
            return blend('#78b52c', c['brand'], (shade-.4)/.32)
        return blend(c['brand'], '#f1ffdb', (shade-.72)/.28)
    if shade < .4:
        return blend('#25350f', '#54801a', shade/.4)
    if shade < .72:
        return blend('#669e24', '#98de46', (shade-.4)/.32)
    return blend('#98de46', '#d5ff9f', (shade-.72)/.28)


def binary_art(c):
    """Static SVG fallback; the expensive motion is baked into WebP at build time."""
    out = ['<g id="binary-portrait" aria-hidden="true">']
    rng = random.Random(270)
    for fx, fy, fs, glasses in face_points():
        size = 9.0 + rng.random()*.3
        bit = rng.randrange(2)
        color = face_color(c, fs, glasses)
        out.append(f'<text x="{fx:.1f}" y="{fy:.1f}" fill="{color}" font-size="{size:.1f}" font-weight="600">{bit}</text>')
    out.append('</g>')
    return '\n'.join(out)
