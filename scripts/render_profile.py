"""Build self-contained binary animation SVGs, using the standard library only.

The user's supplied portrait is sampled into a luminance grid after a close-up edit.
No raster portrait, JavaScript, remote fonts, or trackers are embedded in the SVGs.
"""

import json
import random
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
FACE = json.loads((ROOT / "assets/source/face-luminance.json").read_text(encoding="utf-8"))
STATS_PATH = ROOT / "data/public-github.json"
STATS = json.loads(STATS_PATH.read_text(encoding="utf-8")) if STATS_PATH.exists() else None
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", key="#76b900", value="#eeeeee",
                 muted="#969696", rule="#25370d", portrait="#e7f3d5", accent="#76b900", brand="#76b900"),
    "light": dict(bg="#ffffff", fg="#1e1e1e", key="#426800", value="#1e1e1e",
                  muted="#666666", rule="#cddbb7", portrait="#1e1e1e", accent="#426800", brand="#76b900"),
}

CSS = """
text {font-family:Consolas,'Liberation Mono','Courier New',monospace;white-space:pre}
.face-mask{animation:face-cycle 12s linear infinite}
.number-mask{opacity:0;animation:number-cycle 12s linear infinite}
.bits-a{animation:bits-a 1.6s steps(1,end) infinite}
.bits-b{opacity:0;animation:bits-b 1.6s steps(1,end) infinite}
.scan{animation:scan 6s linear infinite}
.rain{animation:rain 4s linear infinite;opacity:.45}
.cursor{animation:blink 1.4s steps(1,end) infinite}
@keyframes face-cycle{0%,60%{opacity:1}66%,88%{opacity:0}96%,100%{opacity:1}}
@keyframes number-cycle{0%,64%{opacity:0}70%,84%{opacity:1}94%,100%{opacity:0}}
@keyframes bits-a{0%,49%{opacity:1}50%,99%{opacity:0}100%{opacity:1}}
@keyframes bits-b{0%,49%{opacity:0}50%,99%{opacity:1}100%{opacity:0}}
@keyframes scan{0%{transform:translateY(-50px)}100%{transform:translateY(570px)}}
@keyframes rain{0%{transform:translateY(-200px)}100%{transform:translateY(560px)}}
@keyframes blink{0%,68%{opacity:1}69%,100%{opacity:0}}
@media(prefers-reduced-motion:reduce){
 .face-mask,.bits-a{animation:none;opacity:1}
 .number-mask,.bits-b,.scan,.rain{animation:none;display:none}
 .cursor{animation:none;opacity:1}
}
"""


def blend(a, b, t):
    av, bv = [int(a[i:i+2], 16) for i in (1, 3, 5)], [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y-x)*t):02x}" for x, y in zip(av, bv))


def binary_art(c):
    """Two bit planes preserve luminance while characters change in place."""
    out = ['<g id="binary-portrait" aria-hidden="true">', '<g class="face-mask">']
    width, height = FACE["width"], FACE["height"]
    cw, rh = 341.6 / width, 518.4 / height
    font = cw / .58
    for plane in range(2):
        rng = random.Random(2700 + plane)
        bits = [str(rng.randrange(2)) for _ in FACE["luminance"]]
        buckets = [min(7, round((value / 255) ** .8 * 7)) for value in FACE["luminance"]]
        out.append(f'<g class="bits-{"a" if plane == 0 else "b"}">')
        for bucket in range(1, 8):
            fill = blend(c["bg"], c["portrait"], bucket / 7)
            out.append(f'<g fill="{fill}" font-size="{font:.2f}">')
            for y in range(height):
                row = ''.join(bits[y*width+x] if buckets[y*width+x] == bucket else ' ' for x in range(width))
                if row.strip():
                    out.append(f'<text x="0" y="{font+y*rh:.1f}" textLength="341.6" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{row}</text>')
            out.append('</g>')
        out.append('</g>')
    out.append('<clipPath id="face-shape">')
    for y in range(height):
        start = None
        for x in range(width + 1):
            inside = x < width and FACE['luminance'][y * width + x] > 38
            if inside and start is None:
                start = x
            elif not inside and start is not None:
                out.append(f'<rect x="{start*cw:.1f}" y="{2+y*rh:.1f}" width="{(x-start)*cw:.1f}" height="{rh:.2f}"/>')
                start = None
    out.append('</clipPath><g clip-path="url(#face-shape)">')
    rain_rng = random.Random(271)
    for column in range(4, width-3, 5):
        duration = 3.1 + rain_rng.random() * 2.2
        delay = -rain_rng.random() * duration
        out.append(f'<g class="rain" style="animation-duration:{duration:.2f}s;animation-delay:{delay:.2f}s" fill="{c["accent"]}" font-size="{font:.2f}">')
        for y in range(18):
            out.append(f'<text x="{column*cw:.1f}" y="{y*rh:.1f}">{rain_rng.randrange(2)}</text>')
        out.append('</g>')
    out.append('</g></g><g class="number-mask">')
    two = ["11111", "00001", "00001", "11111", "10000", "10000", "11111"]
    seven = ["11111", "00001", "00010", "00100", "01000", "01000", "01000"]
    sx, sy = max(2, width//14), max(3, height//12)
    left, top = (width-11*sx)//2, (height-7*sy)//2
    for plane in range(2):
        rng = random.Random(27 + plane)
        out.append(f'<g class="bits-{"a" if plane == 0 else "b"}">')
        for y in range(height):
            row = []
            for x in range(width):
                gy, gx = (y - top) // sy, (x - left) // sx
                on = False
                if 0 <= gy < 7:
                    if 0 <= gx < 5:
                        on = two[gy][gx] == '1'
                    elif 6 <= gx < 11:
                        on = seven[gy][gx - 6] == '1'
                row.append(str(rng.randrange(2)) if on else ' ')
            if ''.join(row).strip():
                out.append(f'<text x="0" y="{font+y*rh:.1f}" font-size="{font:.2f}" fill="{c["accent"]}" textLength="341.6" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{"".join(row)}</text>')
        out.append('</g>')
    out.append('</g>')
    out.append('<clipPath id="portrait-clip"><rect width="342" height="530"/></clipPath>')
    out.append(f'<g clip-path="url(#portrait-clip)"><rect class="scan" width="342" height="24" fill="{c["brand"]}" opacity=".055"/></g>')
    out.append('</g>')
    return '\n'.join(out)


def render(theme, mobile=False):
    c = THEMES[theme]
    w, h = (480, 1225) if mobile else (1120, 620)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
         '<title id="title">l27sen / binary alter ego</title>',
         '<desc id="desc">Lahsen wearing glasses, rendered entirely in animated zeros and ones that dissolve into 27. Cybersecurity engineering student focused on reverse engineering and binary analysis. Hobbies include XOR and PRNG checks, heap use-after-free and GOT overwrites, JWT algorithm confusion, and local LLMs. Advanced CTF practice on Hack The Box and Root-Me.</desc>',
         '<style>' + CSS + '</style>',
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{c["bg"]}" stroke="{c["rule"]}"/>']

    def text(x, y, value, color="fg", size=15, weight=400, klass="", **attrs):
        extra = ' '.join(f'{k.replace("_", "-")}="{escape(str(v))}"' for k, v in attrs.items())
        s.append(f'<text x="{x}" y="{y}" fill="{c[color]}" font-size="{size}" font-weight="{weight}" class="{klass}" {extra}>{escape(str(value))}</text>')

    def rule(x, y, width):
        s.append(f'<path d="M{x} {y}h{width}" stroke="{c["rule"]}" stroke-dasharray="2 5"/>')

    def row(y, key, value):
        text(393, y, key + ':', "key")
        end = 393 + (len(key) + 1) * 8.3 + 12
        leader_end = max(end, 1097 - len(value) * 8.25 - 12)
        s.append(f'<path d="M{end:.1f} {y-4}H{leader_end:.1f}" stroke="{c["rule"]}" stroke-dasharray="2 5"/>')
        text(1097, y, value, "value", text_anchor="end")

    def mobile_row(y, key, value):
        text(24, y, key + ':', "key", 16)
        text(24, y+24, value, "value", 16.5)

    github = f'{STATS["public_repos"]} public repos / {STATS["stars"]} stars' if STATS else 'Public work on GitHub'
    checked = STATS['checked_utc'] + ' UTC' if STATS else 'Refresh via GitHub Actions'
    if mobile:
        text(24, 28, 'l27sen@localhost:~$', "accent", 15, 700)
        s.append('<g transform="translate(110 46) scale(.76)">')
        s.append(binary_art(c))
        s.append('</g>')
        text(240, 466, '27 / 0x1b / 00011011', 'muted', 14, text_anchor="middle")
        rule(24, 485, 432)
        mobile_row(518, 'Role', P['role'])
        mobile_row(573, 'Focus', P['focus'])
        mobile_row(635, 'Languages.Code', P['languages'])
        mobile_row(690, 'Tools.Reverse', P['reverse_tools'])
        mobile_row(745, 'Tools.Security', P['security_tools'])
        rule(24, 793, 432)
        for i, hobby in enumerate(P['hobbies']):
            mobile_row(823 + i * 55, hobby['key'], hobby['value'])
        rule(24, 1023, 432)
        mobile_row(1054, 'HTB / Root-Me', P['platforms']['level'])
        mobile_row(1112, 'GitHub.Public', github)
        text(24, 1165, P['signature'], 'accent', 18, 700)
        text(24, 1200, 'GitHub checked ' + checked, 'muted', 11)
    else:
        s.append('<g transform="translate(23 34)">')
        s.append(binary_art(c))
        s.append('</g>')
        text(393, 42, 'l27sen@localhost:~$ ./whoami', 'accent', 17, 700)
        text(393 + len('l27sen@localhost:~$ ./whoami') * 9.35 + 5, 42, '_', 'accent', 17, 700, klass='cursor')
        rule(393, 61, 704)
        row(91, 'Role', P['role'])
        row(113, 'Focus', P['focus'])
        row(135, 'Method', P['approach'])
        row(177, 'Languages.Code', P['languages'])
        row(199, 'Languages.LowLevel', P['lowlevel'])
        row(221, 'Tools.Reverse', P['reverse_tools'])
        row(243, 'Tools.Security', P['security_tools'])
        for i, hobby in enumerate(P['hobbies']):
            row(285 + i*22, hobby['key'], hobby['value'])
        row(393, 'Platforms', 'Hack The Box / Root-Me')
        row(415, 'Practice', P['platforms']['level'])
        row(437, 'Notes', '0xWriteups / solvers & rabbit holes')
        rule(393, 461, 704)
        row(488, 'GitHub.Public', github)
        row(510, 'GitHub.Checked', checked)
        text(393, 561, P['signature'], 'accent', 19, 700)
        text(24, 598, 'l27sen :: binary alter ego', 'muted', 12)
        text(1097, 598, '27 / 0x1b / 00011011', 'muted', 12, text_anchor='end')
    s.append('</svg>')
    return '\n'.join(s) + '\n'


if __name__ == '__main__':
    for theme in THEMES:
        for mobile in (False, True):
            name = f'profile-{theme}{"-mobile" if mobile else ""}.svg'
            (ROOT / 'assets' / name).write_text(render(theme, mobile), encoding='utf-8')
            print('Rendered assets/' + name)
