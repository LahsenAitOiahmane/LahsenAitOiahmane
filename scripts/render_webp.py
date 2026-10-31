"""Bake the flow into 30 fps WebP images: no per-particle work in the browser.

Static layout remains SVG. Only the build process computes particle trajectories.
Glyph masks and curve lengths are cached; held poses are stored as long frames.
"""

import bisect
import gc
import math
import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from binary_flow import DURATION, face_points, number_points, face_color, relief_color

ROOT = Path(__file__).resolve().parents[1]
FPS = 30
SCALE = 2
FONT = ROOT / 'assets/fonts/RobotoMono.ttf'


@lru_cache(maxsize=96)
def font(size, weight=400):
    result = ImageFont.truetype(str(FONT), size)
    result.set_variation_by_axes([weight])
    return result


def rgb(value):
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def parse_placement(transform):
    values = [float(n) for n in re.findall(r'-?(?:\d+(?:\.\d*)?|\.\d+)',transform)]
    if len(values) not in (2,3) or (len(values)==3 and not 0 < values[2] <= 2):
        raise ValueError(f'Invalid portrait placement: {transform}')
    return values


def background(svg_path):
    """Rasterize our small layout vocabulary, excluding the portrait placeholder."""
    root = ET.parse(svg_path).getroot()
    w, h = int(root.attrib['width']), int(root.attrib['height'])
    background_color = next(n.attrib['fill'] for n in root if n.tag.rsplit('}',1)[-1]=='rect')
    image = Image.new('RGB', (w*SCALE, h*SCALE), background_color)
    draw = ImageDraw.Draw(image)
    placement = None
    for node in root:
        tag = node.tag.rsplit('}', 1)[-1]
        a = node.attrib
        if tag == 'g':
            placement = parse_placement(a['transform'])
        elif tag == 'rect':
            x, y = float(a.get('x', 0))*SCALE, float(a.get('y', 0))*SCALE
            box = (x, y, x+float(a['width'])*SCALE, y+float(a['height'])*SCALE)
            draw.rounded_rectangle(box, radius=float(a.get('rx', 0))*SCALE,
                                   fill=a.get('fill'), outline=a.get('stroke'), width=SCALE)
        elif tag == 'path':
            values = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', a['d'])]
            x, y, end = values
            if 'h' in a['d']:
                end += x
            if 'stroke-dasharray' in a:
                while x < end:
                    draw.line((x*SCALE, y*SCALE, min(x+2, end)*SCALE, y*SCALE),
                              fill=a['stroke'], width=SCALE)
                    x += 7
            else:
                draw.line((x*SCALE, y*SCALE, end*SCALE, y*SCALE), fill=a['stroke'], width=SCALE)
        elif tag == 'text':
            size = round(float(a.get('font-size', 15))*SCALE)
            weight = 700 if int(a.get('font-weight', 400)) >= 600 else 400
            anchor = {'end': 'rs', 'middle': 'ms'}.get(a.get('text-anchor'), 'ls')
            draw.text((float(a['x'])*SCALE, float(a['y'])*SCALE), node.text or '',
                      font=font(size, weight), fill=a['fill'], anchor=anchor)
    assert placement is not None
    return image.resize((w, h), Image.Resampling.LANCZOS), placement


def cubic(points, t):
    a, b, c, d = points
    k = 1-t
    return (k*k*k*a[0]+3*k*k*t*b[0]+3*k*t*t*c[0]+t*t*t*d[0],
            k*k*k*a[1]+3*k*k*t*b[1]+3*k*t*t*c[1]+t*t*t*d[1])


def easing(t):
    lo, hi = 0., 1.
    for _ in range(17):
        q = (lo+hi)/2
        x, _ = cubic(((0,0),(.42,0),(.18,1),(1,1)), q)
        if x < t:
            lo = q
        else:
            hi = q
    return cubic(((0,0),(.42,0),(.18,1),(1,1)), (lo+hi)/2)[1]


EASE = [easing(i/1024) for i in range(1025)]


def progress(t):
    u = (t % DURATION)/DURATION
    if u < .24 or u >= .96:
        return 0.
    if u < .48:
        return EASE[min(1024, round((u-.24)/.24*1024))]
    if u < .72:
        return 1.
    return 1-EASE[min(1024, round((u-.72)/.24*1024))]


@lru_cache(maxsize=16)
def glyph(bit, size):
    f = font(size,600)
    mask = Image.new('L', (30, 36))
    ImageDraw.Draw(mask).text((3, 26), str(bit), font=f, fill=255, anchor='ls')
    box = mask.getbbox()
    return mask.crop(box), (box[0]-3, box[1]-26)


def trajectories(c):
    import random
    rng = random.Random(270)
    result = []
    for (fx, fy, fs, glasses), (nx, ny, ns) in zip(face_points(), number_points()):
        guide = 172+math.sin(fy/86)*67
        a = (fx*.48+guide*.52, min(512, fy+128))
        b = (nx*.43+(172+math.sin(ny/92+1.7)*79)*.57, max(15, ny-134))
        curve = ((fx,fy), a, b, (nx,ny))
        lengths, previous = [0.], (fx, fy)
        for i in range(1, 49):
            xy = cubic(curve, i/48)
            lengths.append(lengths[-1]+math.hypot(xy[0]-previous[0],xy[1]-previous[1]))
            previous = xy
        size = round((9+rng.random()*.3)*SCALE)
        bit = rng.randrange(2)
        result.append((curve, lengths, fy/518*.68, rgb(face_color(c,fs,glasses)),
                       rgb(relief_color(c,ns)), (bit,size)))
    return result


def portrait_frame(c, particles, t):
    image = Image.new('RGB', (342*SCALE,530*SCALE), c['bg'])
    for curve, lengths, phase, fc, nc, (bit,size) in particles:
        p = progress(t+phase)
        if p <= 0:
            x, y = curve[0]
            color = fc
        elif p >= 1:
            x, y = curve[-1]
            color = nc
        else:
            distance = p*lengths[-1]
            i = min(48, max(1,bisect.bisect_left(lengths,distance)))
            ratio = (distance-lengths[i-1])/max(1e-9,lengths[i]-lengths[i-1])
            x, y = cubic(curve, (i-1+ratio)/48)
            color = tuple(round(a+(b-a)*p) for a,b in zip(fc,nc))
        mask,offset = glyph(bit,round(size*(1-.15*p)))
        image.paste(color, (round(x*SCALE+offset[0]),round(y*SCALE+offset[1])), mask)
    resized = image.resize((342,530), Image.Resampling.LANCZOS)
    image.close()
    return resized


def portrait_frames(c):
    frames, durations = [], []
    particles = trajectories(c)
    last_hold = None
    for i in range(DURATION*FPS):
        t = i/FPS
        # Only merge spans where every staggered particle is stationary.
        hold = 'face' if t < 3.15 or t >= 15.36 else 'number' if 7.68 <= t < 10.84 else None
        duration = round((i+1)*1000/FPS)-round(i*1000/FPS)
        if hold is not None and hold == last_hold:
            durations[-1] += duration
        else:
            frames.append(portrait_frame(c, particles, t))
            durations.append(duration)
        last_hold = hold
    return frames, durations


class FrameSequence(Image.Image):
    """Expose composed frames lazily instead of retaining hundreds of full cards."""

    def __init__(self, base, portraits, placement):
        super().__init__()
        self.base, self.portraits, self.placement = base, portraits, placement
        self.n_frames = len(portraits)-1
        self._current = None
        self.seek(0)

    def seek(self, index):
        if not 0 <= index < self.n_frames:
            raise EOFError(index)
        if self._current is not None:
            self._current.close()
        self._current = compose(self.base,self.portraits[index+1],self.placement)
        self._im = self._current.im
        self._mode, self._size = self._current.mode,self._current.size
        self._index = index

    def tell(self):
        return self._index


def compose(base,portrait,placement):
    x,y = placement[:2]
    scale = placement[2] if len(placement)>2 else 1
    assert 0 < scale <= 2, f'Invalid portrait scale: {scale}'
    frame = base.copy()
    if scale != 1:
        scaled = portrait.resize((round(342*scale),round(530*scale)),Image.Resampling.LANCZOS)
        frame.paste(scaled,(round(x),round(y)))
        scaled.close()
    else:
        frame.paste(portrait,(round(x),round(y)))
    return frame


def build_animations(themes):
    for theme, c in themes.items():
        print(f'Baking {theme} flow at {FPS} fps...', flush=True)
        portraits, durations = portrait_frames(c)
        for mobile in (False,True):
            name = f'profile-{theme}{"-mobile" if mobile else ""}'
            base, placement = background(ROOT/'assets'/f'{name}.svg')
            first = compose(base,portraits[0],placement)
            sequence = FrameSequence(base,portraits,placement)
            path = ROOT/'assets'/f'{name}.webp'
            temporary = path.with_name(path.stem+'.tmp.webp')
            for quality in (80,79,78):
                first.save(temporary,save_all=True,append_images=[sequence],duration=durations,
                           loop=0,lossless=False,quality=quality,method=4,minimize_size=False,
                           allow_mixed=False,kmin=30,kmax=60)
                if temporary.stat().st_size < 8*1024*1024:
                    break
            assert temporary.stat().st_size < 8*1024*1024, 'Profile image exceeded its download budget'
            temporary.replace(path)
            print(f'Rendered assets/{name}.webp ({path.stat().st_size:,} bytes, {len(portraits)} frames)',flush=True)
            first.close()
            sequence.close()
            base.close()
            del first,sequence,base
            gc.collect()
        for frame in portraits:
            frame.close()
        del portraits
        gc.collect()
