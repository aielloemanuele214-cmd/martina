#!/usr/bin/env python3
"""sad genera — generazione asset di un ordine con Gemini (Nano Banana) + pipeline.

Legge il brief artistico da packs/<slug>/genera.json, genera gli asset su
sfondo VERDE (personaggi/oggetti) o a piena scena (stanza/popup), li fa passare
nella pipeline di scontorno/packing (tools/sprites.py) e scrive gli sprite
pronti in packs/<slug>/assets/. Metodo reference-first: il primo foglio del
protagonista fa da riferimento per tutti gli altri (coerenza del personaggio).

Ogni immagine generata viene annotata nel registro consumi
(~/.config/sempreaddue/gemini-usage.tsv) per tenere il conto della fatturazione.

  python3 tools/sad.py genera <slug> [--assets nome,nome] [--modello X]

Brief (packs/<slug>/genera.json):
  { "protagonista": "...", "secondario": "...", "animale": "orange cat"(opz),
    "stanza": "...", "oggetti": ["...","...","..."], "animati": "..." }
"""
import base64, json, os, ssl, sys, urllib.request, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import sprites  # helper: load_rgba_keyed, cells_grid, pack (nessun side-effect all'import)
from PIL import Image

CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
ENV = os.path.expanduser('~/.config/sempreaddue/gemini.env')
DEFAULT_MODEL = 'gemini-3.1-flash-image'
COST = {'gemini-3.1-flash-image': 0.04, 'gemini-2.5-flash-image': 0.04, 'gemini-3-pro-image': 0.13}

# ---- Style Bible (invariato: il DNA visivo SempreAddue) ----
STYLE = ("Cohesive hand-crafted 16-bit pixel art, cozy-JRPG / life-sim quality (Stardew Valley / "
  "Eastward feel). Hand-placed pixels, crisp clean 1px outlines, limited harmonious warm palette "
  "(amber, terracotta, candle-gold) with cool night accents. Soft warm rim-light, subtle ordered "
  "dithering, no smooth blur. Readable silhouette. Premium, intimate.")
GREEN = ("Placed on a SOLID PURE #00FF00 GREEN SCREEN, perfectly flat, hard-edged and uniform, "
  "no gradient, no green light spilling on the subject.")
NEG = ("Avoid: blur, anti-aliased fuzzy edges, glow, 3D render look, text, watermark, extra limbs, "
  "feet cut off, inconsistent proportions between frames.")

def _key():
    if os.environ.get('GEMINI_API_KEY'): return os.environ['GEMINI_API_KEY']
    if os.path.exists(ENV):
        for ln in open(ENV):
            if 'GEMINI_API_KEY' in ln and '=' in ln:
                return ln.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('GEMINI_API_KEY non impostata (vedi ~/.config/sempreaddue/gemini.env)')

def _log(model, n):
    os.makedirs(os.path.dirname(USAGE), exist_ok=True)
    if not os.path.exists(USAGE):
        open(USAGE, 'w').write('quando\tmodello\timmagini\tcosto_stima_eur\n')
    # timestamp passato dall'ambiente per non usare Date/now proibiti altrove
    ts = os.environ.get('SAD_TS', 'genera')
    open(USAGE, 'a').write(f'{ts}\t{model}\t{n}\t{COST.get(model,0.04)*n:.3f}\n')

def gen(model, key, prompt, dest, aspect=None, ref=None):
    """Genera un'immagine (PNG) e la salva in dest. `ref`: path immagine di
    riferimento da passare in input (coerenza del personaggio)."""
    parts = [{'text': prompt}]
    if ref and os.path.exists(ref):
        b = base64.b64encode(open(ref, 'rb').read()).decode()
        parts.insert(0, {'inlineData': {'mimeType': 'image/png', 'data': b}})
    cfg = {'responseModalities': ['IMAGE']}
    if aspect: cfg['imageConfig'] = {'aspectRatio': aspect}
    body = json.dumps({'contents': [{'parts': parts}], 'generationConfig': cfg}).encode()
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=body, headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, context=CTX, timeout=240) as r:
        d = json.load(r)
    for p in d.get('candidates', [{}])[0].get('content', {}).get('parts', []):
        if 'inlineData' in p:
            raw = base64.b64decode(p['inlineData']['data'])
            # normalizza sempre a PNG (l'API può restituire JPEG)
            open(dest + '.raw', 'wb').write(raw)
            Image.open(dest + '.raw').convert('RGB').save(dest)
            os.remove(dest + '.raw')
            _log(model, 1)
            return True
    raise SystemExit('nessuna immagine: ' + json.dumps(d)[:300])

# ---- specifiche degli asset: come costruire il prompt e come processare ----
def build_specs(brief):
    P, S = brief['protagonista'], brief.get('secondario', '')
    tech = ("Four full-body frames in one horizontal row, evenly spaced at identical scale, each frame "
            "an ISOLATED figure with a clear WIDE vertical green gap between figures (they must never "
            "touch). NO ground line, NO floor, NO baseline or connecting shadow between the figures — "
            "only the characters on flat green, nothing else. Feet at the same height in each frame.")
    order = ("Frame order left-to-right: 1) idle; 2) walk step A; 3) walk step B; 4) interaction, "
             "reaching one hand toward an unseen off-frame object (do NOT draw any object).")
    # per il protagonista: 4 direzioni; 'down'=frontale, 'up'=di spalle, right/left=profili
    faces = {'protagonista_down': 'strictly FRONT-FACING (facing the camera) in all four frames, do not turn to profile',
             'protagonista_up':   'seen from BEHIND (back-facing) in all four frames',
             'protagonista_right':'in RIGHT-SIDE profile, walking to the right',
             'protagonista_left': 'in LEFT-SIDE profile, walking to the left'}
    specs = []
    for name, face in faces.items():
        specs.append(dict(name=name, kind='char', frames=4, fh=242, aspect='16:9', green=True,
            ref=(name != 'protagonista_down'),  # gli altri usano il down come riferimento
            prompt=f"{STYLE} A walk-cycle sprite SHEET of {P}, {face}. {tech} {order} "
                   f"Identical character design in every frame. {GREEN} {NEG}"))
    if S:
        specs.append(dict(name='secondario_emo', kind='char', frames=5, fh=262, aspect='16:9', green=True, ref=True,
            prompt=f"{STYLE} Front-view acting SHEET of {S}, 5 frames in one row, stands still. Order: "
                   f"1) idle warm smile; 2) bashful hand behind neck; 3) speaking open-hand gesture; "
                   f"4) thoughtful hand on chin; 5) amused arms crossed. Expressive on-model face. {GREEN} {NEG}"))
        specs.append(dict(name='ballo5', kind='char', frames=5, fh=312, aspect='16:9', green=True, ref=True,
            prompt=f"{STYLE} Five-frame SHEET, one row: {P} and {S} embracing in a slow dance, tender "
                   f"micro-movements chaining smoothly. Same two characters, consistent design. {GREEN} {NEG}"))
    if brief.get('animale'):
        specs.append(dict(name='gatto', kind='char', frames=2, fh=240, aspect='16:9', green=True, ref=False,
            prompt=f"{STYLE} Two-frame SHEET, one row, of {brief['animale']} on the floor: 1) sleeping curled; "
                   f"2) awake head raised. Same animal. {GREEN} {NEG}"))
    # stanza (2 frame, niente verde) + popup
    room = brief.get('stanza', 'cozy candle-lit room')
    objs = brief.get('oggetti', ['a record player', 'a TV with a blanket', 'a writing desk'])
    anim = brief.get('animati', 'candle flames flicker, small reflections shift')
    specs.append(dict(name='stanza_bg', kind='room', aspect='1:1', green=False,
        prompt=f"{STYLE} Top-down 3/4 cozy-sim view, square room, full scene, NO green screen. {room}. "
               f"Back wall occupies the top ~20-25%; rest is warm walkable floor. Clearly separated: "
               f"clue object A ({objs[0]}) on the UPPER-LEFT; clue object B ({objs[1]}) on the RIGHT; "
               f"clue object C ({objs[2]}) LOWER-LEFT on furniture; an open central-bottom space; a "
               f"mid-right spot to stand; a window on the back wall onto the night. Readable, lived-in. {NEG}"))
    specs.append(dict(name='stanza_bg2', kind='room', aspect='1:1', green=False, ref_room=True,
        prompt=f"Take the reference room image and change ONLY the animated elements: {anim}. Keep "
               f"everything else pixel-identical so the two frames loop without jitter. Square, same framing."))
    for i, key in enumerate(['pop_vinile', 'pop_tv', 'pop_scrivania'][:len(objs)]):
        specs.append(dict(name=key, kind='popup', aspect='1:1', green=False,
            prompt=f"{STYLE} Square intimate close-up of {objs[i]}, same world and candlelight as the room, "
                   f"cozy atmosphere. No text. {NEG}"))
    specs.append(dict(name='pop_finestra', kind='popup', aspect='1:1', green=False,
        prompt=f"{STYLE} Square close-up of the view outside the window at night for this scene, atmospheric, "
               f"same palette as the room. No text. {NEG}"))
    return specs

def process_char(srcpng, name, frames, fh, outdir):
    rgba = sprites.load_rgba_keyed(srcpng)
    cells = sprites.cells_grid(rgba)
    if len(cells) != frames:
        print(f'  ⚠ {name}: trovate {len(cells)} celle invece di {frames} — controlla il foglio')
        if len(cells) < frames: return None
        cells = cells[:frames]
    sprites.OUT = outdir
    return sprites.pack(cells, fh, name)

def main(slug, only=None, model=DEFAULT_MODEL):
    key = _key()
    pack_dir = os.path.join(ROOT, 'packs', slug)
    brief_path = os.path.join(pack_dir, 'genera.json')
    assert os.path.exists(brief_path), f'brief mancante: {brief_path} (vedi docs/PROMPT-NANOBANANA.md)'
    brief = json.load(open(brief_path, encoding='utf-8'))
    src = os.path.join(pack_dir, 'assets', '_src'); os.makedirs(src, exist_ok=True)
    spr = os.path.join(pack_dir, 'assets', 'sprites'); os.makedirs(spr, exist_ok=True)
    rooms = os.path.join(pack_dir, 'assets', 'rooms'); os.makedirs(rooms, exist_ok=True)
    pops = os.path.join(pack_dir, 'assets', 'popup'); os.makedirs(pops, exist_ok=True)

    specs = build_specs(brief)
    if only: specs = [s for s in specs if s['name'] in only]
    ref_prota = os.path.join(src, 'protagonista_down.png')
    ref_room = os.path.join(rooms, 'stanza_bg.png')
    dims = {}
    n_before = _count()
    for s in specs:
        print(f'· genero {s["name"]} …')
        if s['kind'] == 'char':
            raw = os.path.join(src, s['name'] + '.png')
            gen(model, key, s['prompt'], raw, aspect=s.get('aspect'),
                ref=ref_prota if s.get('ref') else None)
            d = process_char(raw, s['name'], s['frames'], s['fh'], spr)
            if d: dims[s['name']] = d
        elif s['kind'] == 'room':
            out = os.path.join(rooms, s['name'] + '.png')
            gen(model, key, s['prompt'], out, aspect='1:1',
                ref=ref_room if s.get('ref_room') else None)
            Image.open(out).convert('RGB').resize((1024, 1024), Image.LANCZOS).save(out)
        elif s['kind'] == 'popup':
            out = os.path.join(pops, s['name'] + '.png')
            gen(model, key, s['prompt'], out, aspect='1:1')
            Image.open(out).convert('RGB').resize((512, 512), Image.LANCZOS).save(out)
    if dims:
        print('\nDIMS (aggiorna packs/%s/config/sprites.json con fw):' % slug)
        print(' ', json.dumps(dims))
    print(f'\n💸 immagini generate stavolta: {_count()-n_before} · registro: {USAGE}')
    _report()

def _count():
    if not os.path.exists(USAGE): return 0
    return sum(1 for i, _ in enumerate(open(USAGE)) if i > 0)

def _report():
    tot = 0.0
    for i, ln in enumerate(open(USAGE)):
        if i == 0: continue
        c = ln.rstrip('\n').split('\t')
        if len(c) >= 4:
            try: tot += float(c[3])
            except ValueError: pass
    print(f'   totale stimato registro: ~€{tot:.2f} (verifica il costo reale in Google Cloud)')

if __name__ == '__main__':
    args = sys.argv[1:]
    slug = args[0]
    only = None; model = DEFAULT_MODEL
    if '--assets' in args: only = set(args[args.index('--assets')+1].split(','))
    if '--modello' in args: model = args[args.index('--modello')+1]
    main(slug, only, model)
