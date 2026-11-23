#!/usr/bin/env python3
"""Genera una pagina real por seccion (/proyectos/index.html, etc.) y 404.html
a partir de index.html. Cada pagina lleva su propio titulo y descripcion
(Discord, X, WhatsApp... leen esas etiquetas sin ejecutar JavaScript).
Uso: python3 build_pages.py   (ejecutalo despues de editar index.html)
Titulos y descripciones se editan en index.html, en el objeto DD."""
import json, re, pathlib, html

root = pathlib.Path(__file__).parent
src = (root / 'index.html').read_text(encoding='utf-8')
DD = json.loads(re.search(r'/\*DD-START\*/var DD=(.*?);/\*DD-END\*/', src, re.S).group(1))
SITE = 'https://zansumi.github.io'
e = lambda v: html.escape(v, quote=True)

def page(n, title=None):
    d = DD[n]; t = title or d['t']; url = SITE + ('/' if n == 'inicio' else '/%s/' % n)
    h = src
    og = SITE + '/assets/banners/og/%s.png?v=3' % n
    subs = [
      (r'(<meta property="og:image" content=").*?(">)', og),
      (r'(<meta property="og:image:secure_url" content=").*?(">)', og),
      (r'(<meta name="twitter:image" content=").*?(">)', og),
      (r'(<meta property="og:image:alt" content=").*?(">)', 'Zansumi · ' + e(d['n'].title() if n != 'inicio' else 'Creador de contenido')),
      (r'(<meta name="twitter:image:alt" content=").*?(">)', 'Zansumi · ' + e(d['n'].title() if n != 'inicio' else 'Creador de contenido')),
      (r'<title>.*?</title>', '<title>%s</title>' % e(t)),
      (r'(<meta name="description" content=").*?(">)', e(d['d'])),
      (r'(<link rel="canonical" href=").*?(">)', url),
      (r'(<meta property="og:url" content=").*?(">)', url),
      (r'(<meta property="og:title" content=").*?(">)', e(d['t'])),
      (r'(<meta property="og:description" content=").*?(">)', e(d['d'])),
      (r'(<meta name="twitter:title" content=").*?(">)', e(d['t'])),
      (r'(<meta name="twitter:description" content=").*?(">)', e(d['d'])),
    ]
    for pat, val in subs:
        h, k = re.subn(pat, lambda m, val=val: (m.group(1) + val + m.group(2)) if m.lastindex == 2 else val, h, count=1, flags=re.S)
        assert k == 1, pat
    return h

for n in DD:
    if n == 'inicio': continue
    out = root / n / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page(n), encoding='utf-8')

# 404.html: GitHub Pages lo sirve para cualquier ruta inexistente; la web muestra su panel 404
h404 = page('inicio', '404 | Zansumi').replace('<base href="/">', '<base href="/">\n<meta name="robots" content="noindex">')
(root / '404.html').write_text(h404, encoding='utf-8')
print('listo:', ', '.join(n for n in DD if n != 'inicio'), '+ 404.html')
