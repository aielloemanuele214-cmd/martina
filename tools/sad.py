#!/usr/bin/env python3
"""sad — Sempreaddue Adventure CLI (F0: builder unificato)

Comandi:
    python3 tools/sad.py build-base
        Ricostruisce stanza.html (il modello base) da engine/stanza_template.html
        incorporando in base64 tutti gli asset del repo. È il passaggio che prima
        viveva fuori dal repo: da qui il progetto è ricostruibile da zero.

    python3 tools/sad.py build clienti/<slug>.json
        Genera la copia personalizzata del cliente in dist/stanza-<slug>.html
        sostituendo il blocco CONFIG di stanza.html con i dati del JSON.
        I valori stringa "file:percorso" (relativo al JSON) vengono incorporati
        in base64 (foto, lettere, audio del cliente).

    python3 tools/sad.py check
        Verifica che tutti gli asset richiesti dal template esistano e che
        stanza.html non contenga placeholder residui.

Tutti i percorsi sono relativi alla radice del repo (lo script la trova da solo).
"""
import base64, json, mimetypes, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'engine', 'stanza_template.html')
BASE_OUT = os.path.join(ROOT, 'stanza.html')

# Mappa placeholder → asset del repo (unica fonte di verità del build base)
ASSET_MAP = {
    '{{B64:bg}}':            ('assets/rooms/stanza_bg.jpg',   'image/jpeg'),
    '{{B64:bg2}}':           ('assets/rooms/stanza_bg2.jpg',  'image/jpeg'),
    '{{B64:lei_down}}':      ('assets/sprites/lei_down.png',  'image/png'),
    '{{B64:lei_right}}':     ('assets/sprites/lei_right.png', 'image/png'),
    '{{B64:lei_up}}':        ('assets/sprites/lei_up.png',    'image/png'),
    '{{B64:lei_left}}':      ('assets/sprites/lei_left.png',  'image/png'),
    '{{B64:lui_emo}}':       ('assets/sprites/lui_emo.png',   'image/png'),
    '{{B64:gatto}}':         ('assets/sprites/gatto.png',     'image/png'),
    '{{B64:ballo5}}':        ('assets/sprites/ballo5.png',    'image/png'),
    '{{B64:pt_lui_0}}':      ('assets/sprites/pt_lui_0.png',  'image/png'),
    '{{B64:pt_lui_1}}':      ('assets/sprites/pt_lui_1.png',  'image/png'),
    '{{B64:pt_lui_2}}':      ('assets/sprites/pt_lui_2.png',  'image/png'),
    '{{B64:pt_lui_3}}':      ('assets/sprites/pt_lui_3.png',  'image/png'),
    '{{B64:pt_lui_4}}':      ('assets/sprites/pt_lui_4.png',  'image/png'),
    '{{B64:pt_gatto}}':      ('assets/sprites/pt_gatto.png',  'image/png'),
    '{{B64:cuore8}}':        ('assets/sprites/cuore8.png',    'image/png'),
    '{{B64:pop_vinile}}':    ('assets/popup/pop_vinile.jpg',    'image/jpeg'),
    '{{B64:pop_tv}}':        ('assets/popup/pop_tv.jpg',        'image/jpeg'),
    '{{B64:pop_scrivania}}': ('assets/popup/pop_scrivania.jpg', 'image/jpeg'),
    '{{B64:pop_finestra}}':  ('assets/popup/pop_finestra.jpg',  'image/jpeg'),
    '{{B64:mus_gioco}}':     ('assets/audio/mus_gioco.mp3',   'audio/mpeg'),
    '{{B64:mus_menu}}':      ('assets/audio/mus_menu.mp3',    'audio/mpeg'),
}

CONFIG_RE = re.compile(
    r'/\* ★★ INIZIO CONFIG ★★ \*/.*?/\* ★★ FINE CONFIG ★★[^\n]*\*/', re.S)


def b64(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def build_base():
    tpl = open(TEMPLATE, encoding='utf-8').read()
    for ph, (rel, mime) in ASSET_MAP.items():
        path = os.path.join(ROOT, rel)
        assert os.path.exists(path), f'asset mancante: {rel}'
        assert ph in tpl, f'placeholder assente nel template: {ph}'
        tpl = tpl.replace(ph, b64(path, mime))
    left = re.findall(r'\{\{[^}]+\}\}', tpl)
    assert not left, f'placeholder residui: {sorted(set(left))}'
    open(BASE_OUT, 'w', encoding='utf-8').write(tpl)
    print(f'stanza.html ricostruito: {os.path.getsize(BASE_OUT)//1024} KB')


def _inline(v, basedir):
    """Sostituisce 'file:percorso' con il data-URI base64 del file."""
    if isinstance(v, dict):
        return {k: _inline(x, basedir) for k, x in v.items()}
    if isinstance(v, list):
        return [_inline(x, basedir) for x in v]
    if isinstance(v, str) and v.startswith('file:'):
        path = os.path.normpath(os.path.join(basedir, v[5:]))
        mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        return b64(path, mime)
    return v


def build_client(json_path):
    src = open(BASE_OUT, encoding='utf-8').read()
    cfg = json.load(open(json_path, encoding='utf-8'))
    slug = cfg.pop('_slug', None)
    assert slug, "il JSON del cliente deve avere '_slug'"
    cfg = _inline(cfg, os.path.dirname(os.path.abspath(json_path)))
    blocco = ('/* ★★ INIZIO CONFIG ★★ */\nconst CONFIG = '
              + json.dumps(cfg, ensure_ascii=False, indent=2)
              + ';\n/* ★★ FINE CONFIG ★★ — non modificare sotto questa riga */')
    out, n = CONFIG_RE.subn(lambda _: blocco, src, count=1)
    assert n == 1, 'blocco CONFIG non trovato in stanza.html'
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    dest = os.path.join(ROOT, 'dist', f'stanza-{slug}.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'creato dist/stanza-{slug}.html ({os.path.getsize(dest)//1024} KB)')


def check():
    ok = True
    for ph, (rel, _) in ASSET_MAP.items():
        if not os.path.exists(os.path.join(ROOT, rel)):
            print(f'MANCA {rel}  ({ph})'); ok = False
    if os.path.exists(BASE_OUT):
        left = re.findall(r'\{\{[^}]+\}\}', open(BASE_OUT, encoding='utf-8').read())
        if left:
            print(f'placeholder residui in stanza.html: {sorted(set(left))}'); ok = False
    else:
        print('stanza.html assente: esegui build-base'); ok = False
    print('check OK' if ok else 'check FALLITO')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'build-base':
        build_base()
    elif cmd == 'build' and len(sys.argv) == 3:
        build_client(sys.argv[2])
    elif cmd == 'check':
        check()
    else:
        sys.exit(__doc__)
