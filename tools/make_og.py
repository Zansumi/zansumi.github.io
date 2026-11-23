#!/usr/bin/env python3
"""Genera las imagenes de vista previa (Discord, X, WhatsApp...) de cada seccion.
Toma assets/banners/baner2.png, lo recorta a 1200x630 sin deformar y le pone el
nombre de la seccion en grande, la direccion debajo y un detalle en rojo.
Salida: assets/banners/og/<seccion>.png  (inicio.png, proyectos.png, ...)
Los nombres salen del campo "n" del objeto DD en index.html.
Uso (desde la carpeta del sitio): python3 tools/make_og.py   y luego   python3 build_pages.py
Necesita Pillow:  pip install pillow"""
import json, re, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root = pathlib.Path(__file__).resolve().parent.parent
W, H = 1200, 630
SITE = 'zansumi.github.io'
RED = (179, 38, 45)
src = (root / 'index.html').read_text(encoding='utf-8')
DD = json.loads(re.search(r'/\*DD-START\*/var DD=(.*?);/\*DD-END\*/', src, re.S).group(1))

def font(size, weight=800):
    here = pathlib.Path(__file__).parent
    for p, var in ((here / 'BricolageGrotesque.ttf', True), (pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'), False)):
        try:
            f = ImageFont.truetype(str(p), size)
            if var:
                axes = f.get_variation_axes()  # opsz, wdth, wght
                vals = []
                for a in axes:
                    n = a['name'].decode() if isinstance(a['name'], bytes) else a['name']
                    vals.append(weight if 'eight' in n else (a['default'] if 'ptical' not in n else min(max(size/ 4, a['minimum']), a['maximum'])))
                f.set_variation_by_axes(vals)
            return f
        except Exception:
            continue
    return ImageFont.load_default()

def spaced(d, xy_center, text, f, fill, tracking=0):
    widths = [d.textlength(c, font=f) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy_center[0] - total / 2
    for c, w in zip(text, widths):
        d.text((x, xy_center[1]), c, font=f, fill=fill, anchor='lm')
        x += w + tracking
    return total

def base():
    b = Image.open(root / 'assets' / 'banners' / 'baner2.png').convert('RGB')
    ch = round(b.width * H / W)                  # recorte 1200:630 a todo el ancho
    top = (b.height - ch) // 2
    b = b.crop((0, top, b.width, top + ch)).resize((W, H), Image.LANCZOS)
    # un poco mas oscuro al centro para que el texto se lea limpio
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).ellipse((150, 120, W - 150, H - 120), fill=(0, 0, 0, 150))
    shade = shade.filter(ImageFilter.GaussianBlur(70))
    return Image.alpha_composite(b.convert('RGBA'), shade)

out = root / 'assets' / 'banners' / 'og'
out.mkdir(parents=True, exist_ok=True)
bg = base()
for slug, d in DD.items():
    name = d.get('n') or slug.replace('-', ' ').upper()
    im = bg.copy(); dr = ImageDraw.Draw(im)
    size = 150
    while True:                                   # el nombre siempre cabe en el centro vacio
        f = font(size)
        w = sum(dr.textlength(c, font=f) for c in name) + 6 * (len(name) - 1)
        if w <= 600 or size <= 60: break
        size -= 4
    cy = H // 2 - 14
    spaced(dr, (W // 2, cy), name, f, (244, 245, 247), 6)
    dr.rectangle((W // 2 - 28, cy - size // 2 - 34, W // 2 + 28, cy - size // 2 - 31), fill=RED)   # detalle rojo
    addr = SITE if slug == 'inicio' else f'{SITE}/{slug}/'
    spaced(dr, (W // 2, cy + size // 2 + 46), addr, font(30, 500), (139, 144, 150), 1)
    im.convert('RGB').save(out / f'{slug}.png', optimize=True)
    print('og:', slug, '->', name)
