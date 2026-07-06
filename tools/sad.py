#!/usr/bin/env python3
"""sad — Sempreaddue Adventure CLI (F1: engine a moduli + pack di contenuti)

Comandi:
    python3 tools/sad.py build-base [pack]
        Assembla il gioco: moduli engine (engine/src/) + configurazione del
        pack (packs/<pack>/config/*.json) + asset in base64 → stanza.html.
        Il pack predefinito è "martina".

    python3 tools/sad.py build clienti/<slug>.json
        Genera la copia personalizzata in dist/stanza-<slug>.html sostituendo
        il blocco CONFIG di stanza.html. I valori "file:percorso" (relativo al
        JSON) vengono incorporati in base64.

    python3 tools/sad.py check [pack]
        Verifica moduli, asset, config del pack e placeholder residui.

Architettura (vedi ARCHITETTURA.md):
  engine/src/          moduli ordinati per numero: il builder li concatena.
                       _config.js/_room.js/_assets.js NON vengono concatenati:
                       sono i frammenti storici, sostituiti dai dati del pack.
  packs/<slug>/        manifest.json + config/*.json = TUTTO il contenuto.
                       Il motore non conosce alcun contenuto specifico.
"""
import base64, json, mimetypes, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'engine', 'src')
BASE_OUT = os.path.join(ROOT, 'stanza.html')
DEFAULT_PACK = 'martina'

# Placeholder asset → file del repo
ASSET_MAP = {
    'bg':            ('assets/rooms/stanza_bg.jpg',   'image/jpeg'),
    'bg2':           ('assets/rooms/stanza_bg2.jpg',  'image/jpeg'),
    'lei_down':      ('assets/sprites/lei_down.png',  'image/png'),
    'lei_right':     ('assets/sprites/lei_right.png', 'image/png'),
    'lei_up':        ('assets/sprites/lei_up.png',    'image/png'),
    'lei_left':      ('assets/sprites/lei_left.png',  'image/png'),
    'lui_emo':       ('assets/sprites/lui_emo.png',   'image/png'),
    'gatto':         ('assets/sprites/gatto.png',     'image/png'),
    'ballo5':        ('assets/sprites/ballo5.png',    'image/png'),
    'pt_lui_0':      ('assets/sprites/pt_lui_0.png',  'image/png'),
    'pt_lui_1':      ('assets/sprites/pt_lui_1.png',  'image/png'),
    'pt_lui_2':      ('assets/sprites/pt_lui_2.png',  'image/png'),
    'pt_lui_3':      ('assets/sprites/pt_lui_3.png',  'image/png'),
    'pt_lui_4':      ('assets/sprites/pt_lui_4.png',  'image/png'),
    'pt_gatto':      ('assets/sprites/pt_gatto.png',  'image/png'),
    'cuore8':        ('assets/sprites/cuore8.png',    'image/png'),
    'pop_vinile':    ('assets/popup/pop_vinile.jpg',    'image/jpeg'),
    'pop_tv':        ('assets/popup/pop_tv.jpg',        'image/jpeg'),
    'pop_scrivania': ('assets/popup/pop_scrivania.jpg', 'image/jpeg'),
    'pop_finestra':  ('assets/popup/pop_finestra.jpg',  'image/jpeg'),
    'mus_gioco':     ('assets/audio/mus_gioco.mp3',   'audio/mpeg'),
    'mus_menu':      ('assets/audio/mus_menu.mp3',    'audio/mpeg'),
}

CONFIG_RE = re.compile(
    r'/\* ★★ INIZIO CONFIG ★★ \*/.*?/\* ★★ FINE CONFIG ★★[^\n]*\*/', re.S)


def b64(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def jsdump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def strip_notes(obj):
    """Rimuove le chiavi di documentazione (_note, _*) prima dell'iniezione."""
    if isinstance(obj, dict):
        return {k: strip_notes(v) for k, v in obj.items() if not k.startswith('_')}
    if isinstance(obj, list):
        return [strip_notes(x) for x in obj]
    return obj


def load_pack(pack):
    pdir = os.path.join(ROOT, 'packs', pack)
    manifest = json.load(open(os.path.join(pdir, 'manifest.json'), encoding='utf-8'))
    # CONFIG = fusione profonda dei file elencati nel manifest (ordine = precedenza)
    config = {}
    def merge(dst, src):
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                merge(dst[k], v)
            else:
                dst[k] = v
    for f in manifest['config']:
        merge(config, strip_notes(json.load(open(os.path.join(pdir, 'config', f), encoding='utf-8'))))
    room = strip_notes(json.load(open(os.path.join(pdir, 'config', 'room.json'), encoding='utf-8')))
    sprites = strip_notes(json.load(open(os.path.join(pdir, 'config', 'sprites.json'), encoding='utf-8')))
    return manifest, config, room, sprites


def gen_config_js(config):
    return ('/* ★★ INIZIO CONFIG ★★ */\nconst CONFIG = '
            + jsdump(config)
            + ';\n/* ★★ FINE CONFIG ★★ — non modificare sotto questa riga */\n')


def gen_room_js(room):
    return ('\n/* ====== STANZA (da packs/<pack>/config/room.json) ====== */\n'
            'const ROOM = ' + jsdump(room) + ';\n'
            'const COLLIDERS = ROOM.colliders;\n'
            'const BEHIND_BED = ROOM.dietroLetto.pts;\n')


def gen_assets_js(sprites):
    rows = []
    for key, sh in sprites['sheets'].items():
        dims = ''.join(f', {d}:{sh[d]}' for d in ('fw', 'fh', 'n') if d in sh)
        rows.append(f"  {key}: {{ src:'{{{{B64:{sh['asset']}}}}}'{dims} }},")
    return ('\n/* ====== ASSET (da packs/<pack>/config/sprites.json, incorporati in base64) ====== */\n'
            'const ASSETS = {\n' + '\n'.join(rows) + '\n};\n'
            "/* Direzione → foglio sprite di lei */\n"
            "const DIR_SHEET = { down:'leiDown', up:'leiUp', left:'leiLeft', right:'leiRight' };\n"
            "/* Indici frame di lei */\n"
            "const FR_IDLE=0, FR_WALK_A=1, FR_WALK_B=2, FR_INTERACT=3;\n"
            "/* Ritratti dei dialoghi */\n"
            "const PORTRAITS_LUI = ['{{B64:pt_lui_0}}','{{B64:pt_lui_1}}','{{B64:pt_lui_2}}','{{B64:pt_lui_3}}','{{B64:pt_lui_4}}'];\n"
            "const PORTRAIT_GATTO = '{{B64:pt_gatto}}';\n"
            "/* Colonna sonora (mp3 incorporati) */\n"
            "const MUSICHE = {\n"
            "  gioco: '{{B64:mus_gioco}}',\n"
            "  menu:  '{{B64:mus_menu}}',\n"
            "};\n"
            "/* Immagine del segreto finestra */\n"
            "const IMG_FINESTRA = '{{B64:pop_finestra}}';\n")


def modules():
    """Frammenti engine in ordine, esclusi quelli storici (_*)."""
    return sorted(f for f in os.listdir(SRC)
                  if not f.startswith('_') and re.match(r'\d\d-', f))


def build_base(pack=DEFAULT_PACK):
    manifest, config, room, sprites = load_pack(pack)
    frags = modules()
    parts = []
    for f in frags:
        parts.append(open(os.path.join(SRC, f), encoding='utf-8').read())
        if f == '02-corpo.html':        # dopo il banner CONFIG dello script
            parts.append(gen_config_js(config))
            parts.append(gen_room_js(room))
            parts.append(gen_assets_js(sprites))
    html = ''.join(parts)
    # incorpora gli asset
    for name, (rel, mime) in ASSET_MAP.items():
        ph = '{{B64:%s}}' % name
        path = os.path.join(ROOT, rel)
        assert os.path.exists(path), f'asset mancante: {rel}'
        if ph in html:
            html = html.replace(ph, b64(path, mime))
    left = re.findall(r'\{\{[^}]+\}\}', html)
    assert not left, f'placeholder residui: {sorted(set(left))}'
    open(BASE_OUT, 'w', encoding='utf-8').write(html)
    print(f"stanza.html assemblato (pack '{pack}', {len(frags)} moduli): "
          f"{os.path.getsize(BASE_OUT)//1024} KB")


def _inline(v, basedir):
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
    blocco = ('/* ★★ INIZIO CONFIG ★★ */\nconst CONFIG = ' + jsdump(cfg)
              + ';\n/* ★★ FINE CONFIG ★★ — non modificare sotto questa riga */')
    out, n = CONFIG_RE.subn(lambda _: blocco, src, count=1)
    assert n == 1, 'blocco CONFIG non trovato in stanza.html'
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    dest = os.path.join(ROOT, 'dist', f'stanza-{slug}.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'creato dist/stanza-{slug}.html ({os.path.getsize(dest)//1024} KB)')


def check(pack=DEFAULT_PACK):
    ok = True
    try:
        _, config, room, sprites = load_pack(pack)
        for k in ('nomi', 'dialoghi', 'sorprese', 'finale', 'posizioni'):
            if k not in config:
                print(f'config del pack incompleta: manca "{k}"'); ok = False
        for k in ('bounds', 'colliders', 'dietroLetto'):
            if k not in room:
                print(f'room.json incompleta: manca "{k}"'); ok = False
    except Exception as e:
        print(f'pack "{pack}" illeggibile: {e}'); ok = False
    for name, (rel, _) in ASSET_MAP.items():
        if not os.path.exists(os.path.join(ROOT, rel)):
            print(f'MANCA {rel}  ({name})'); ok = False
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
        build_base(*sys.argv[2:3])
    elif cmd == 'build' and len(sys.argv) == 3:
        build_client(sys.argv[2])
    elif cmd == 'check':
        check(*sys.argv[2:3])
    else:
        sys.exit(__doc__)
