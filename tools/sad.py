#!/usr/bin/env python3
"""sad — Sempreaddue Adventure CLI (F3: produzione automatizzata)

Comandi:
    build-base [pack]         moduli engine + pack + asset → stanza.html (valida prima)
    build clienti/<x>.json    stanza.html + JSON cliente → dist/ (valida prima)
    validate [pack]           JSON Schema + lint semantici sul pack
    validate clienti/<x>.json JSON Schema + lint sul file di un cliente
    check [pack]              verifica asset e placeholder
    ordine <slug>             scaffolding di un nuovo ordine (clienti/<slug>.json)
    new <slug> [--da pack]    scaffolding di un nuovo pack (copia di un pack esistente)
    qa [file.html]            suite QA Playwright parametrica (default: stanza.html)
    preview                   server locale per provare stanza.html e dist/
    art                       rigenera gli sprite da assets/_src/ (tools/sprites.py)
    music <in.mp3> <out.mp3>  loop strumentale senza stacco (tools/music.py)

Architettura (vedi ARCHITETTURA.md):
  engine/src/   moduli ordinati per numero: il builder li concatena.
  packs/<slug>/ manifest.json + config/*.json = TUTTO il contenuto.
                Il motore non conosce alcun contenuto specifico.
  tools/schemas/*.schema.json  contratti di ogni file di configurazione.
"""
import base64, json, mimetypes, os, re, subprocess, sys

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

# Vocabolario '@nome' di default (pack storici: martina/romantica/compleanno/proposta,
# tutti con lo stesso npc "lui" a 5 ritratti). Un pack nuovo può dichiarare il proprio
# in sprites.json con "assetUri"/"ritrattiNpc" senza toccare questo file.
LEGACY_ASSET_URI = ['pt_gatto', 'pop_finestra'] + [f'pt_lui_{i}' for i in range(5)]
LEGACY_RITRATTI_NPC = [f'pt_lui_{i}' for i in range(5)]


def find_pack_asset(pack, name):
    """Cerca <name>.{png,jpg,jpeg,mp3} dentro packs/<pack>/assets/ (ricorsivo).
    Permette a un pack di portarsi i propri asset senza registrarli in ASSET_MAP."""
    pdir = os.path.join(ROOT, 'packs', pack, 'assets')
    for dirpath, _dirs, files in os.walk(pdir):
        for f in files:
            base, ext = os.path.splitext(f)
            if base == name and ext.lower() in ('.png', '.jpg', '.jpeg', '.mp3'):
                mime = mimetypes.guess_type(f)[0] or 'application/octet-stream'
                return os.path.join(dirpath, f), mime
    return None


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
    story = strip_notes(json.load(open(os.path.join(pdir, 'config', manifest.get('story', 'story.json')), encoding='utf-8')))
    return manifest, config, room, sprites, story


def gen_config_js(config):
    return ('/* ★★ INIZIO CONFIG ★★ */\nconst CONFIG = '
            + jsdump(config)
            + ';\n/* ★★ FINE CONFIG ★★ — non modificare sotto questa riga */\n')


def gen_room_js(room):
    return ('\n/* ====== STANZA (da packs/<pack>/config/room.json) ====== */\n'
            'const ROOM = ' + jsdump(room) + ';\n'
            'const COLLIDERS = ROOM.colliders;\n'
            'const BEHIND_BED = ROOM.dietroLetto.pts;\n')


def gen_assets_js(sprites, story):
    rows = []
    for key, sh in sprites['sheets'].items():
        dims = ''.join(f', {d}:{sh[d]}' for d in ('fw', 'fh', 'n', 'alt') if d in sh)
        rows.append(f"  {key}: {{ src:'{{{{B64:{sh['asset']}}}}}'{dims} }},")
    # asset referenziabili dalla STORY con '@nome' (ritratti, immagini dei popup)
    # — un pack può dichiarare il proprio vocabolario in sprites.json ("assetUri",
    # "ritrattiNpc"); se assente si usa quello storico (pack martina e derivati)
    uri_names = sprites.get('assetUri', LEGACY_ASSET_URI)
    ritratti_npc = sprites.get('ritrattiNpc', LEGACY_RITRATTI_NPC)
    uris = '\n'.join(f"  {n}: '{{{{B64:{n}}}}}'," for n in uri_names)
    portraits = ', '.join(f'ASSET_URI.{n}' for n in ritratti_npc)
    return ('\n/* ====== ASSET (da packs/<pack>/config/sprites.json, incorporati in base64) ====== */\n'
            'const ASSETS = {\n' + '\n'.join(rows) + '\n};\n'
            '/* Personaggi: fogli, stati di animazione, altezze (data-driven) */\n'
            'const SPR = ' + jsdump(sprites['personaggi']) + ';\n'
            '/* Asset referenziabili con "@nome" da STORY */\n'
            'const ASSET_URI = {\n' + uris + '\n};\n'
            f"const PORTRAITS_LUI = [{portraits}];\n"
            "/* Colonna sonora (mp3 incorporati) */\n"
            "const MUSICHE = {\n"
            "  gioco: '{{B64:mus_gioco}}',\n"
            "  menu:  '{{B64:mus_menu}}',\n"
            "};\n")


def gen_story_js(story):
    return ('\n/* ====== STORY (da packs/<pack>/config/story.json): eventi, scene, dialoghi,\n'
            '   segreti e finali — il comportamento della partita, 100% dati ====== */\n'
            'const STORY = ' + jsdump(story) + ';\n')


def modules():
    """Frammenti engine in ordine, esclusi quelli storici (_*)."""
    return sorted(f for f in os.listdir(SRC)
                  if not f.startswith('_') and re.match(r'\d\d-', f))


# ============================================================
# VALIDAZIONE — JSON Schema + lint semantici
# ============================================================
def _schema(nome):
    return json.load(open(os.path.join(ROOT, 'tools', 'schemas', nome), encoding='utf-8'))


def _valida_schema(dati, nome_schema, etichetta, errs):
    import jsonschema
    v = jsonschema.Draft7Validator(_schema(nome_schema))
    for e in sorted(v.iter_errors(dati), key=lambda e: list(e.path)):
        dove = '/'.join(map(str, e.path)) or '(radice)'
        errs.append(f'{etichetta} → {dove}: {e.message}')


def _atomi_condizione(c, out):
    """Raccoglie i flag citati da una condizione ('!x', 'a.*', all/any)."""
    if c is None: return
    if isinstance(c, str):
        c = c.lstrip('!')
        if c and c != 'prima_interazione': out.add(c)
    elif isinstance(c, dict):
        for r in list(c.get('all', [])) + list(c.get('any', [])):
            _atomi_condizione(r, out)


def _scava(obj, chiave, out):
    """Trova ricorsivamente tutti i valori di una chiave ('scena', 'dialogo', 'set'…)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == chiave and isinstance(v, str): out.append(v)
            _scava(v, chiave, out)
    elif isinstance(obj, list):
        for x in obj: _scava(x, chiave, out)


def _riferimenti(obj, out_cfg, out_asset):
    """Raccoglie i riferimenti '$percorso' e '@asset' della STORY."""
    if isinstance(obj, str):
        if obj.startswith('$'): out_cfg.append(obj[1:])
        elif obj.startswith('@'): out_asset.append(obj[1:])
    elif isinstance(obj, dict):
        for v in obj.values(): _riferimenti(v, out_cfg, out_asset)
    elif isinstance(obj, list):
        for x in obj: _riferimenti(x, out_cfg, out_asset)


def validate_pack(pack=DEFAULT_PACK, silenzioso=False):
    errs = []
    manifest, config, room, sprites, story = load_pack(pack)
    _valida_schema(manifest, 'manifest.schema.json', 'manifest.json', errs)
    _valida_schema(config,   'config.schema.json',   'config (fusa)',  errs)
    _valida_schema(room,     'room.schema.json',     'room.json',      errs)
    _valida_schema(sprites,  'sprites.schema.json',  'sprites.json',   errs)
    _valida_schema(story,    'story.schema.json',    'story.json',     errs)

    # --- lint semantici ---
    # 1. ogni sorpresa ha un evento che la gestisce
    quando = {e['quando'] for e in story.get('eventi', [])}
    for s in config.get('sorprese', []):
        if f"interagisci:{s['id']}" not in quando:
            errs.append(f"story.json: nessun evento gestisce 'interagisci:{s['id']}'")
    # 2. scene e dialoghi citati esistono
    scene_citate, dialoghi_citati = [], []
    _scava(story.get('eventi', []), 'scena', scene_citate)
    _scava(story.get('scene', {}), 'scena', scene_citate)
    _scava(story.get('eventi', []), 'dialogo', dialoghi_citati)
    for sc in scene_citate:
        if sc not in story.get('scene', {}): errs.append(f"story.json: scena '{sc}' citata ma non definita")
    for d in dialoghi_citati:
        if d not in story.get('dialoghi', {}): errs.append(f"story.json: dialogo '{d}' citato ma non definito")
    # 3. i riferimenti '$' risolvono nella config, gli '@' negli asset noti
    ref_cfg, ref_asset = [], []
    _riferimenti(story, ref_cfg, ref_asset)
    for r in set(ref_cfg):
        o = config
        for k in r.split('.'):
            o = o.get(k) if isinstance(o, dict) else None
        if o is None: errs.append(f"story.json: '${r}' non risolve nella config del pack")
    noti = set(sprites.get('assetUri', LEGACY_ASSET_URI))
    for r in set(ref_asset):
        if r not in noti: errs.append(f"story.json: '@{r}' non è un asset incorporato noto")
    # 4. i flag usati nelle condizioni sono impostabili da qualche azione
    settabili = set()
    _scava(story, 'set', [])  # (firma uniforme)
    tmp = []; _scava(story, 'set', tmp); settabili |= set(tmp)
    tmp = []; _scava(story, 'sorpresa', tmp)
    settabili |= {f'trovato.{s}' for s in tmp}
    settabili |= {'interagito'}
    usati = set()
    for e in story.get('eventi', []): _atomi_condizione(e.get('se'), usati)
    for f in story.get('finali', []): _atomi_condizione(f.get('se'), usati)
    tmp = []; _scava(story, 'se', tmp)  # condizioni annidate stringa
    for c in tmp: _atomi_condizione(c, usati)
    for u in usati:
        if u.endswith('.*'):
            pre = u[:-1]
            for s in config.get('sorprese', []):
                if pre + s['id'] not in settabili:
                    errs.append(f"story.json: '{u}' richiede '{pre}{s['id']}' ma nessuna azione lo imposta")
        elif u not in settabili:
            errs.append(f"story.json: la condizione usa '{u}' ma nessuna azione lo imposta")
    # 5. fogli dei personaggi esistono; punti d'arrivo dentro i limiti stanza
    sheets = sprites.get('sheets', {})
    for nome, p in sprites.get('personaggi', {}).items():
        for f in list((p.get('fogli') or {}).values()) + ([p['foglio']] if 'foglio' in p else []):
            if f not in sheets: errs.append(f"sprites.json: personaggio '{nome}' usa foglio '{f}' inesistente")
    B = room.get('bounds', {})
    for s in config.get('sorprese', []):
        ax, ay = s.get('ax', s['x']), s.get('ay', s['y'])
        if not (B.get('xMin', 0) <= ax <= B.get('xMax', 100) and B.get('yMin', 0) <= ay <= B.get('yMax', 100)):
            errs.append(f"sorpresa '{s['id']}': punto d'arrivo ({ax},{ay}) fuori dai limiti stanza")

    if errs:
        print(f'✗ validate pack "{pack}": {len(errs)} problemi')
        for e in errs: print('  -', e)
        sys.exit(1)
    if not silenzioso:
        print(f'✓ pack "{pack}" valido (schemi + lint: eventi, scene, dialoghi, riferimenti, flag, fogli, limiti)')


def validate_cliente(json_path, pack=DEFAULT_PACK):
    errs = []
    cfg = json.load(open(json_path, encoding='utf-8'))
    _valida_schema(cfg, 'cliente.schema.json', os.path.basename(json_path), errs)
    # gli id delle sorprese devono restare quelli del pack: la STORY li cita
    _, config, _, _, _ = load_pack(pack)
    ids_pack = sorted(s['id'] for s in config['sorprese'])
    ids_cli = sorted(s.get('id', '?') for s in cfg.get('sorprese', []))
    if ids_cli != ids_pack:
        errs.append(f"sorprese: id {ids_cli} ≠ id del pack {ids_pack} (gli eventi della storia li citano)")
    # i file citati con 'file:' devono esistere
    basedir = os.path.dirname(os.path.abspath(json_path))
    def cerca_file(v):
        if isinstance(v, dict):  [cerca_file(x) for x in v.values()]
        elif isinstance(v, list): [cerca_file(x) for x in v]
        elif isinstance(v, str) and v.startswith('file:'):
            if not os.path.exists(os.path.join(basedir, v[5:])):
                errs.append(f"file mancante: {v[5:]} (relativo a {os.path.relpath(basedir, ROOT)})")
    cerca_file(cfg)
    if errs:
        print(f'✗ validate {json_path}: {len(errs)} problemi')
        for e in errs: print('  -', e)
        sys.exit(1)
    print(f'✓ {json_path} valido')


def build_base(pack=DEFAULT_PACK):
    validate_pack(pack, silenzioso=True)
    manifest, config, room, sprites, story = load_pack(pack)
    frags = modules()
    parts = []
    for f in frags:
        parts.append(open(os.path.join(SRC, f), encoding='utf-8').read())
        if f == '02-corpo.html':        # dopo il banner CONFIG dello script
            parts.append(gen_config_js(config))
            parts.append(gen_room_js(room))
            parts.append(gen_assets_js(sprites, story))
            parts.append(gen_story_js(story))
    html = ''.join(parts)
    # incorpora gli asset: prima la mappa storica condivisa (assets/ di repo),
    # poi — per ogni placeholder non riconosciuto — gli asset propri del pack
    # (packs/<pack>/assets/**), così un pack nuovo porta i suoi file senza
    # toccare ASSET_MAP.
    for name in sorted(set(re.findall(r'\{\{B64:([^}]+)\}\}', html))):
        ph = '{{B64:%s}}' % name
        if name in ASSET_MAP:
            rel, mime = ASSET_MAP[name]
            path = os.path.join(ROOT, rel)
            assert os.path.exists(path), f'asset mancante: {rel}'
        else:
            found = find_pack_asset(pack, name)
            assert found, f"asset mancante: '{name}' (né in ASSET_MAP né in packs/{pack}/assets/)"
            path, mime = found
        html = html.replace(ph, b64(path, mime))
    left = re.findall(r'\{\{[^}]+\}\}', html)
    assert not left, f'placeholder residui: {sorted(set(left))}'
    if pack == DEFAULT_PACK:
        out = BASE_OUT
    else:
        os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
        out = os.path.join(ROOT, 'dist', f'base-{pack}.html')
    open(out, 'w', encoding='utf-8').write(html)
    print(f"{os.path.relpath(out, ROOT)} assemblato (pack '{pack}', {len(frags)} moduli): "
          f"{os.path.getsize(out)//1024} KB")


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
    validate_cliente(json_path)
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
        _, config, room, sprites, story = load_pack(pack)
        for k in ('nomi', 'dialoghi', 'sorprese', 'finale', 'posizioni'):
            if k not in config:
                print(f'config del pack incompleta: manca "{k}"'); ok = False
        for k in ('bounds', 'colliders', 'dietroLetto'):
            if k not in room:
                print(f'room.json incompleta: manca "{k}"'); ok = False
        for k in ('eventi', 'scene', 'dialoghi', 'segreti', 'finali', 'ui'):
            if k not in story:
                print(f'story.json incompleta: manca "{k}"'); ok = False
        if 'personaggi' not in sprites:
            print('sprites.json incompleta: manca "personaggi"'); ok = False
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


# ============================================================
# SCAFFOLDING, QA, PREVIEW, WRAPPER
# ============================================================
def nuovo_ordine(slug):
    """Un ordine = UNA cartella autonoma: clienti/<slug>/ con dentro ordine.json,
    le foto e tutto il materiale del cliente. Niente file sparsi."""
    assert re.fullmatch(r'[a-z0-9-]+', slug), 'slug: solo minuscole, cifre e trattini'
    cart = os.path.join(ROOT, 'clienti', slug)
    assert not os.path.exists(cart), f'esiste già: clienti/{slug}/'
    os.makedirs(os.path.join(cart, 'foto'))
    cfg = json.load(open(os.path.join(ROOT, 'clienti', 'esempio.json'), encoding='utf-8'))
    cfg['_slug'] = slug
    # le immagini del cliente vivranno nella cartella dell'ordine
    for s in cfg.get('sorprese', []):
        if isinstance(s.get('img'), str) and s['img'].startswith('file:../assets/'):
            s['img'] = 'file:' + s['img'][len('file:../'):].replace('assets/', '../../assets/')
    open(os.path.join(cart, 'ordine.json'), 'w', encoding='utf-8')\
        .write(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')
    open(os.path.join(cart, 'NOTE.md'), 'w', encoding='utf-8').write(
        f'# Ordine {slug}\n\n- data ordine: \n- contatto: \n- tier: \n- consegna (link): \n\n'
        'Foto del cliente in `foto/` e nei testi usare `"img": "file:foto/nome.jpg"`.\n')
    print(f'creata la cartella clienti/{slug}/ con ordine.json, foto/, NOTE.md')
    print(f'poi:  python3 tools/sad.py build clienti/{slug}/ordine.json')


def nuovo_pack(slug, da=DEFAULT_PACK):
    import shutil
    assert re.fullmatch(r'[a-z0-9-]+', slug), 'slug: solo minuscole, cifre e trattini'
    src = os.path.join(ROOT, 'packs', da)
    dest = os.path.join(ROOT, 'packs', slug)
    assert os.path.isdir(src), f'pack di partenza inesistente: {da}'
    assert not os.path.exists(dest), f'esiste già: packs/{slug}'
    shutil.copytree(src, dest)
    mpath = os.path.join(dest, 'manifest.json')
    m = json.load(open(mpath, encoding='utf-8'))
    m['slug'] = slug
    m['descrizione'] = f'Pack derivato da "{da}".'
    open(mpath, 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
    print(f'creato packs/{slug} (copia di {da}) — modifica config/ e assets, poi build-base {slug}')


def qa(file=None):
    file = file or BASE_OUT
    env = dict(os.environ)
    env['GAME_FILE'] = os.path.abspath(file)
    r = subprocess.call(['node', os.path.join(ROOT, 'tools', 'qa.js')], env=env)
    sys.exit(r)


def preview():
    import http.server, functools
    os.chdir(ROOT)
    porta = int(os.environ.get('PORT', 8000))
    print(f'anteprima:  http://localhost:{porta}/stanza.html')
    print(f'clienti:    http://localhost:{porta}/dist/  (Ctrl+C per uscire)')
    http.server.HTTPServer(('', porta),
        functools.partial(http.server.SimpleHTTPRequestHandler)).serve_forever()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'build-base':
        build_base(*sys.argv[2:3])
    elif cmd == 'build' and len(sys.argv) == 3:
        build_client(sys.argv[2])
    elif cmd == 'validate':
        arg = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PACK
        if arg.endswith('.json'): validate_cliente(arg)
        else: validate_pack(arg)
    elif cmd == 'check':
        check(*sys.argv[2:3])
    elif cmd == 'ordine' and len(sys.argv) == 3:
        nuovo_ordine(sys.argv[2])
    elif cmd == 'new' and len(sys.argv) >= 3:
        da = sys.argv[sys.argv.index('--da') + 1] if '--da' in sys.argv else DEFAULT_PACK
        nuovo_pack(sys.argv[2], da)
    elif cmd == 'qa':
        qa(*sys.argv[2:3])
    elif cmd == 'preview':
        preview()
    elif cmd == 'art':
        sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'sprites.py')]))
    elif cmd == 'music' and len(sys.argv) == 4:
        sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'music.py'),
                                  sys.argv[2], sys.argv[3]]))
    else:
        sys.exit(__doc__)
