"""Binary particles follow shared curved currents from a coarse face to a shaded 27.

Geometry and fill are computed at build time and encoded into WebP frames.
The reduced-motion alternative is a separate static, deliberately abstract portrait.
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACE = json.loads((ROOT / 'assets/source/face-luminance.json').read_text(encoding='utf-8'))
NUMBER = json.loads((ROOT / 'assets/source/number-relief.json').read_text(encoding='utf-8'))
DURATION = 16
COUNT = len(NUMBER['points'])
TIMES = '0;.24;.48;.72;.96;1'
SPLINES = '0 0 1 1;.42 0 .18 1;0 0 1 1;.42 0 .18 1;0 0 1 1'

FLOW_CSS = """
text{font-family:'Roboto Mono','Liberation Mono','Courier New',monospace;white-space:pre}
"""


def blend(a, b, t):
    av, bv = [int(a[i:i+2], 16) for i in (1, 3, 5)], [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x+(y-x)*t):02x}' for x, y in zip(av, bv))


def face_points():
    """Keep coarse topology but discard photographic eye, skin, and mouth detail."""
    w, h = FACE['width'], FACE['height']
    rng = random.Random(27031)
    candidates = []
    # Structured subcells give readable density without restoring photographic detail.
    for y in range(h):
        for x in range(w):
            lum = FACE['luminance'][y*w+x]
            if lum < 32:
                continue
            for jx in (-.24, .24):
                for jy in (-.24, .24):
                    px = 22 + (x+.5+jx+rng.uniform(-.035,.035)) * 298/w
                    py = 12 + (y+.5+jy+rng.uniform(-.035,.035)) * 492/h
                    shade = max(0, min(1, (lum-35)/190))
                    candidates.append((px, py, shade))
    candidates.sort(key=lambda p: p[1]+p[0]*.12)
    return [candidates[min(len(candidates)-1,int((i+.5)*len(candidates)/COUNT))] for i in range(COUNT)]


def number_points():
    candidates = sorted(NUMBER['points'], key=lambda p: p['y']+p['x']*.12)
    # Preserve both front faces and shallow side faces in a fixed-size particle set.
    indices = [int((i+.5)*len(candidates)/COUNT) for i in range(COUNT)]
    return [(candidates[i]['x'], candidates[i]['y'], candidates[i]['shade']) for i in indices]


def face_color(c, shade):
    # Spatial abstraction controls recognizability; contrast still defines the face.
    strength = .35 + .45*shade if c['bg'] == '#000000' else .50 + .40*shade
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
    for fx, fy, fs in face_points():
        size = 9.0 + rng.random()*.3
        bit = rng.randrange(2)
        color = face_color(c, fs)
        out.append(f'<text x="{fx:.1f}" y="{fy:.1f}" fill="{color}" font-size="{size:.1f}">{bit}</text>')
    out.append('</g>')
    return '\n'.join(out)
