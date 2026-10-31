"""Build profile images and static fallbacks."""

import json
import argparse
import textwrap
from html import escape
from binary_flow import binary_art, FLOW_CSS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
STATS_PATH = ROOT / "data/public-github.json"
STATS = json.loads(STATS_PATH.read_text(encoding="utf-8")) if STATS_PATH.exists() else None
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", key="#b4ff57", value="#eeeeee",
                 muted="#969696", rule="#25370d", portrait="#ffffff", accent="#b4ff57", brand="#b4ff57"),
    "light": dict(bg="#ffffff", fg="#1e1e1e", key="#548000", value="#1e1e1e",
                  muted="#666666", rule="#cddbb7", portrait="#111111", accent="#548000", brand="#b4ff57"),
}

CSS = FLOW_CSS


def render(theme, mobile=False):
    c = THEMES[theme]
    w, h = (480, 1540) if mobile else (1120, 650)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
         '<title id="title">l27sen / binary alter ego</title>',
         '<desc id="desc">Lahsen in binary with green glasses, flowing into 27. Cybersecurity engineering student focused on reverse engineering, binary analysis, and pentesting. Preparing for HTB CPTS and getting started in bug bounty. Interests include XOR and PRNG checks, heap exploitation, JWT confusion, insecure deserialization, and AI-assisted binary analysis.</desc>',
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
        rows = textwrap.wrap(value,width=43)
        for i,row in enumerate(rows):
            text(24,y+24+i*24,row,"value",16.5)
        return y+34+len(rows)*24

    github = f'{STATS["public_repos"]} public repos / {STATS["stars"]} stars' if STATS else 'Public work on GitHub'
    checked = STATS['checked_utc'] + ' UTC' if STATS else 'Refresh via GitHub Actions'
    prompt = P['handle']+'@localhost:~$ ./whoami'
    if mobile:
        text(24, 44, P['handle']+'@localhost:~$', "accent", 16, 700)
        s.append('<g transform="translate(110 78) scale(0.76)">')
        s.append(binary_art(c))
        s.append('</g>')
        text(240, 507, '27 / 0x1b / 00011011', 'muted', 14, text_anchor="middle")
        rule(24, 526, 432)
        y=558
        for key,value in [('Role',P['role']),('Focus',P['focus']),('Training',P['training']),('Next',P['next'])]:
            y=mobile_row(y,key,value)
        y+=14
        for key,value in [('Languages.Code',P['languages']),('Tools.Reverse',P['reverse_tools']),('Tools.Security',P['security_tools'])]:
            y=mobile_row(y,key,value)
        rule(24,y+4,432)
        y+=32
        for hobby in P['hobbies']:
            y=mobile_row(y,hobby['key'],hobby['value'])
        rule(24,y+4,432)
        y=mobile_row(y+32,'HTB / Root-Me',P['platforms']['level'])
        y=mobile_row(y,'GitHub.Public',github)
        text(24,y+20,P['signature'],'accent',18,700)
        text(24,y+55,'GitHub checked '+checked,'muted',11)
    else:
        s.append('<g transform="translate(23 34)">')
        s.append(binary_art(c))
        s.append('</g>')
        text(393, 42, prompt, 'accent', 17, 700)
        text(393 + len(prompt) * 10.25 + 5, 42, '_', 'accent', 17, 700, klass='cursor')
        rule(393, 61, 704)
        row(91, 'Role', P['role'])
        row(113, 'Focus', P['focus'])
        row(135, 'Training', P['training'])
        row(157, 'Next', P['next'])
        row(199, 'Languages.Code', P['languages'])
        row(221, 'Languages.LowLevel', P['lowlevel'])
        row(243, 'Tools.Reverse', P['reverse_tools'])
        row(265, 'Tools.Security', P['security_tools'])
        for i, hobby in enumerate(P['hobbies']):
            row(307 + i*22, hobby['key'], hobby['value'])
        row(415, 'Platforms', 'Hack The Box / Root-Me')
        row(437, 'Practice', P['platforms']['level'])
        row(459, 'Notes', '0xWriteups / solvers & rabbit holes')
        rule(393, 483, 704)
        row(510, 'GitHub.Public', github)
        row(532, 'GitHub.Checked', checked)
        text(393, 583, P['signature'], 'accent', 19, 700)
        text(24, 620, P['handle']+' :: binary alter ego', 'muted', 12)
        text(1097, 620, '27 / 0x1b / 00011011', 'muted', 12, text_anchor='end')
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
