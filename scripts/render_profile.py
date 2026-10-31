"""Build static SVG fallbacks and pre-rendered binary animation WebPs.

The user's supplied portrait is sampled into a luminance grid after a close-up edit.
No raster portrait, JavaScript, remote fonts, or trackers are embedded in the SVGs.
"""

import json
import argparse
from html import escape
from binary_flow import binary_art, FLOW_CSS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
STATS_PATH = ROOT / "data/public-github.json"
STATS = json.loads(STATS_PATH.read_text(encoding="utf-8")) if STATS_PATH.exists() else None
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", key="#b4ff57", value="#eeeeee",
                 muted="#969696", rule="#25370d", portrait="#e7f3d5", accent="#b4ff57", brand="#b4ff57"),
    "light": dict(bg="#ffffff", fg="#1e1e1e", key="#548000", value="#1e1e1e",
                  muted="#666666", rule="#cddbb7", portrait="#1e1e1e", accent="#548000", brand="#b4ff57"),
}

CSS = FLOW_CSS


def render(theme, mobile=False):
    c = THEMES[theme]
    w, h = (480, 1225) if mobile else (1120, 620)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
         '<title id="title">l27sen / binary alter ego</title>',
         '<desc id="desc">Lahsen wearing glasses, abstracted into binary particles that flow into a shaded 27. Cybersecurity engineering student focused on reverse engineering and binary analysis. Hobbies include XOR and PRNG checks, heap use-after-free and GOT overwrites, JWT algorithm confusion, and local LLMs. Advanced CTF practice on Hack The Box and Root-Me.</desc>',
         '<style>' + CSS + '</style>',
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{c["bg"]}" stroke="{c["rule"]}"/>']

    def text(x, y, value, color="fg", size=15, weight=400, klass="", **attrs):
        extra = ' '.join(f'{k.replace("_", "-")}="{escape(str(v))}"' for k, v in attrs.items())
        s.append(f'<text x="{x}" y="{y}" fill="{c[color]}" font-size="{size}" font-weight="{weight}" class="{klass}" {extra}>{escape(str(value))}</text>')

    def rule(x, y, width):
        s.append(f'<path d="M{x} {y}h{width}" stroke="{c["rule"]}" stroke-dasharray="2 5"/>')

    def row(y, key, value):
        text(393, y, key + ':', "key")
        end = 393 + (len(key) + 1) * 9.05 + 12
        leader_end = max(end, 1097 - len(value) * 9.05 - 12)
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
        text(393 + len('l27sen@localhost:~$ ./whoami') * 10.25 + 5, 42, '_', 'accent', 17, 700, klass='cursor')
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--static-only', action='store_true')
    parser.add_argument('--theme', choices=list(THEMES))
    args = parser.parse_args()
    selected = {args.theme: THEMES[args.theme]} if args.theme else THEMES
    for theme in selected:
        for mobile in (False, True):
            name = f'profile-{theme}{"-mobile" if mobile else ""}.svg'
            (ROOT / 'assets' / name).write_text(render(theme, mobile), encoding='utf-8')
            print('Rendered assets/' + name)

    if not args.static_only:
        from render_webp import build_animations
        build_animations(selected)
