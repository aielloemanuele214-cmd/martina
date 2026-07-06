#!/usr/bin/env python3
"""SempreAddue — generatore kit social.
SVG sorgente (font+immagini incorporati) → poi PNG via Chromium e WebP via Pillow.
Identità: tema notturno del sito, palette brand, Baloo 2 / Nunito / Press Start 2P.
"""
import base64, os, math

ROOT = '/home/user/martina'
OUT = os.path.join(ROOT, 'social')
IMG = os.path.join(ROOT, 'site', 'img')
SCRATCH = os.path.dirname(os.path.abspath(__file__)) + '/..'

# ---------- palette ----------
CREMA   = '#FBF3E9'
PESCA   = '#F6C9A8'
CORALLO = '#E8896B'
CORALLO_D = '#c96a4e'
ROSA    = '#C65B7C'
ROSALUCE= '#E890A8'
PRUGNA  = '#5E2A47'
NOTTE   = '#120a10'
NOTTE2  = '#1b0f17'
NOTTE3  = '#241420'
TESTO   = '#f3e7dc'
SOFT    = 'rgba(243,231,220,0.74)'
BORDO   = 'rgba(246,201,168,0.35)'

BALOO = "'Baloo 2'"
PIXEL = "'Press Start 2P'"

W, H = 1080, 1350
MX = 84  # margine laterale

def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()

def datauri(path):
    ext = path.rsplit('.', 1)[1].lower()
    mime = {'webp':'image/webp','png':'image/png','jpg':'image/jpeg','woff2':'font/woff2'}[ext]
    return f'data:{mime};base64,{b64(path)}'

FONTS = {
    'baloo':  datauri(f'{ROOT}/site/fonts/baloo2-800.woff2'),
    'baloo7': datauri(f'{ROOT}/site/fonts/baloo2-700.woff2'),
    'nunito': datauri(f'{ROOT}/site/fonts/nunito-400.woff2'),
    'nunito7':datauri(f'{ROOT}/site/fonts/nunito-700.woff2'),
    'pixel':  datauri(f'{ROOT}/site/fonts/pressstart2p-400.woff2'),
}

def font_css():
    return f"""
    @font-face{{font-family:'Baloo 2';font-weight:800;src:url({FONTS['baloo']}) format('woff2')}}
    @font-face{{font-family:'Baloo 2';font-weight:700;src:url({FONTS['baloo7']}) format('woff2')}}
    @font-face{{font-family:'Nunito';font-weight:400;src:url({FONTS['nunito']}) format('woff2')}}
    @font-face{{font-family:'Nunito';font-weight:700;src:url({FONTS['nunito7']}) format('woff2')}}
    @font-face{{font-family:'Press Start 2P';font-weight:400;src:url({FONTS['pixel']}) format('woff2')}}
    text{{-webkit-font-smoothing:antialiased}}
    """

# ---------- primitive ----------
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def stars(seed=7, n=42, y0=0, y1=H):
    """quadratini pixel sparsi, deterministici (angolo aureo)"""
    out = []
    for i in range(n):
        t = (i + seed) * 137.508
        x = (t % 100) / 100 * W
        y = y0 + ((t * 0.61803) % 100) / 100 * (y1 - y0)
        s = 4 + (i % 3) * 2
        o = 0.05 + (i % 5) * 0.03
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{s}" height="{s}" fill="{PESCA}" opacity="{o:.2f}"/>')
    return '\n'.join(out)

def bg(glow_x=760, glow_y=180, glow_c=ROSA, seed=7):
    return f"""
  <rect width="{W}" height="{H}" fill="url(#bggrad)"/>
  <ellipse cx="{glow_x}" cy="{glow_y}" rx="620" ry="430" fill="{glow_c}" opacity="0.13"/>
  <ellipse cx="{W-glow_x}" cy="{H-260}" rx="540" ry="380" fill="{CORALLO}" opacity="0.07"/>
  {stars(seed)}
"""

HEART_PATH = "M2 3h3v1h1v1h1v1h2V5h1V4h1V3h3v1h1v4h-1v1h-1v1h-1v1h-1v1h-1v1h-1v1H8v-1H7v-1H6v-1H5v-1H4V9H3V8H2V7H1V4h1z"

def heart(x, y, scale, fill=CORALLO, highlight=True):
    hl = f'<rect x="4" y="5" width="2" height="1" fill="{PESCA}"/>' if highlight else ''
    return (f'<g transform="translate({x},{y}) scale({scale})">'
            f'<path d="{HEART_PATH}" fill="{fill}"/>{hl}</g>')

def logo(x=MX, y=64):
    """lockup: sempre (pixel) sopra, cuore + Addue"""
    return f"""
  <g>
    {heart(x, y+6, 2.6)}
    <text x="{x+56}" y="{y+16}" font-family="'Press Start 2P'" font-size="17" fill="{CORALLO}">sempre</text>
    <text x="{x+56}" y="{y+52}" font-family="'Baloo 2'" font-weight="800" font-size="40" fill="{CREMA}">Addue</text>
  </g>"""

def slide_index(i, n=7):
    return (f'<text x="{W-MX}" y="{64+30}" text-anchor="end" font-family="{PIXEL}" '
            f'font-size="19" fill="{PESCA}" opacity="0.85">{i:02d}/{n:02d}</text>')

def footer(handle='@sempreaddue'):
    return (f'<g opacity="0.9">{heart(W/2-118, H-74, 1.5)}'
            f'<text x="{W/2-80}" y="{H-53}" font-family="{PIXEL}" font-size="18" '
            f'fill="{PESCA}">{handle}</text></g>')

def kicker(y, text, x=MX, anchor='start'):
    tx = x + 46 if anchor == 'start' else x
    dash = (f'<rect x="{x}" y="{y-9}" width="30" height="4" fill="{CORALLO}"/>'
            if anchor == 'start' else '')
    a = f' text-anchor="middle"' if anchor == 'middle' else ''
    return (f'{dash}<text x="{tx}" y="{y}"{a} font-family="{PIXEL}" '
            f'font-size="23" fill="{PESCA}">{esc(text)}</text>')

def title(y, lines, size=96, x=MX, anchor='start', lh=None):
    """lines: lista di liste di (testo, colore)"""
    lh = lh or int(size * 1.12)
    a = ' text-anchor="middle"' if anchor == 'middle' else ''
    out = []
    for i, segs in enumerate(lines):
        spans = ''.join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in segs)
        out.append(f'<text x="{x}" y="{y+i*lh}"{a} font-family="{BALOO}" '
                   f'font-weight="800" font-size="{size}">{spans}</text>')
    return '\n'.join(out), y + len(lines) * lh

def body(y, lines, size=40, x=MX, anchor='start', fill=SOFT, lh=None, weight=400):
    lh = lh or int(size * 1.5)
    a = ' text-anchor="middle"' if anchor == 'middle' else ''
    out = []
    for i, line in enumerate(lines):
        if isinstance(line, str):
            spans = esc(line)
        else:
            spans = ''.join(f'<tspan fill="{c}" font-weight="{w}">{esc(t)}</tspan>' for t, c, w in line)
        out.append(f'<text x="{x}" y="{y+i*lh}"{a} font-family="Nunito" '
                   f'font-weight="{weight}" font-size="{size}" fill="{fill}">{spans}</text>')
    return '\n'.join(out), y + len(lines) * lh

def image_frame(path, x, y, w, h, rotate=0, radius=44, border=True):
    uri = datauri(path)
    cx, cy = x + w/2, y + h/2
    rot = f' transform="rotate({rotate} {cx} {cy})"' if rotate else ''
    b = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="none" '
         f'stroke="{BORDO}" stroke-width="3"/>') if border else ''
    return f"""
  <g{rot}>
    <rect x="{x+10}" y="{y+18}" width="{w}" height="{h}" rx="{radius}" fill="#000" opacity="0.45"/>
    <clipPath id="clip{abs(hash((path,x,y)))%99999}">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}"/>
    </clipPath>
    <image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"
      clip-path="url(#clip{abs(hash((path,x,y)))%99999})"/>
    {b}
  </g>"""

def sprite(path, x, y, w):
    """sprite pixel con rendering nitido"""
    uri = datauri(path)
    return (f'<image href="{uri}" x="{x}" y="{y}" width="{w}" '
            f'style="image-rendering:pixelated" preserveAspectRatio="xMidYMid meet"/>')

def pill(cx, y, text, w=None, size=40, fill_grad=True):
    w = w or int(len(text) * size * 0.56 + 120)
    h = int(size * 2.1)
    f = 'url(#ctagrad)' if fill_grad else NOTTE3
    return f"""
  <rect x="{cx-w/2}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{f}"/>
  <text x="{cx}" y="{y+h/2+size*0.36}" text-anchor="middle" font-family="'Baloo 2'"
    font-weight="800" font-size="{size}" fill="#fff">{esc(text)}</text>"""

def check_row(y, txt, sub=None, x=MX):
    """riga con quadratino pixel di spunta"""
    r = f"""
  <rect x="{x}" y="{y-30}" width="34" height="34" fill="none" stroke="{CORALLO}" stroke-width="3"/>
  <rect x="{x+9}" y="{y-21}" width="16" height="16" fill="{CORALLO}"/>
  <text x="{x+60}" y="{y}" font-family="'Baloo 2'" font-weight="700" font-size="42" fill="{CREMA}">{esc(txt)}</text>"""
    if sub:
        r += (f'<text x="{x+60}" y="{y+46}" font-family="Nunito" font-size="33" '
              f'fill="{SOFT}">{esc(sub)}</text>')
    return r

def num_badge(x, y, n):
    return f"""
  <rect x="{x}" y="{y}" width="72" height="72" rx="20" fill="{NOTTE3}" stroke="{BORDO}" stroke-width="2.5"/>
  <text x="{x+36}" y="{y+48}" text-anchor="middle" font-family="'Press Start 2P'" font-size="30"
    fill="{CORALLO}">{n}</text>"""

def svg_doc(content, glow_x=760, glow_y=180, glow_c=ROSA, seed=7):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="bggrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#181019"/><stop offset="0.55" stop-color="{NOTTE}"/>
    <stop offset="1" stop-color="{NOTTE2}"/>
  </linearGradient>
  <linearGradient id="ctagrad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f0996f"/><stop offset="0.55" stop-color="{CORALLO}"/>
    <stop offset="1" stop-color="{CORALLO_D}"/>
  </linearGradient>
  <style>{font_css()}</style>
</defs>
{bg(glow_x, glow_y, glow_c, seed)}
{content}
</svg>"""

def write(path, svg):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(svg)
    print(f'{os.path.relpath(path, OUT)}  ({os.path.getsize(path)//1024} KB)')
