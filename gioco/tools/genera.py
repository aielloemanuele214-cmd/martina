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
import collmask  # derivazione collisioni + posizionamento dalla maschera
import qc         # controllo qualità visivo automatico (art director AI)
from PIL import Image
import numpy as np

CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
ENV = os.path.expanduser('~/.config/sempreaddue/gemini.env')
DEFAULT_MODEL = 'gemini-3.1-flash-image'
PRO_MODEL = 'gemini-3-pro-image'      # escalation quando flash non convince il QC
MAX_QC = int(os.environ.get('SAD_QC_RETRY', '3'))   # tentativi per asset prima di arrendersi
COST = {'gemini-3.1-flash-image': 0.04, 'gemini-2.5-flash-image': 0.04, 'gemini-3-pro-image': 0.13}

# ---- Style Bible (rete di sicurezza: il DNA vero è in agenti/art-supervisor-agente.md) ----
STYLE = ("Cohesive hand-crafted 16-bit pixel art, cozy-JRPG / life-sim quality (Stardew Valley / "
  "Eastward feel). Hand-placed pixels, crisp clean 1px outlines, limited harmonious warm palette "
  "(amber, terracotta, candle-gold) with cool night accents. Soft warm rim-light, subtle ordered "
  "dithering, no smooth blur. Readable silhouette. Premium, intimate.")
GREEN = ("Placed on a SOLID PURE #00FF00 GREEN SCREEN, perfectly flat, hard-edged and uniform, "
  "no gradient, no green light spilling on the subject.")
NEG = ("Avoid: blur, anti-aliased fuzzy edges, glow, 3D render look, text, watermark, extra limbs, "
  "feet cut off, inconsistent proportions between frames.")
# Gli sfondi sono un PALCO vuoto: ogni essere vivo è uno sprite separato, mai dipinto qui.
NOLIVING = ("CRITICAL: the scene is completely EMPTY of any living being — absolutely NO people, "
  "NO human figures or silhouettes, NO cats, NO dogs, NO animals or pets anywhere. Only "  # (segue)
  "architecture, furniture and inanimate objects. Living things are separate sprites, never "
  "painted into this image.")

# --- Agente Art Supervisor (FIG-03): il DNA visivo vive in una spec editabile.
# genera.py la carica e la inietta in ogni prompt. Addestrarlo = editare quel
# file. I valori qui sopra restano solo come rete di sicurezza. ---
SPEC_ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agenti', 'art-supervisor-agente.md')
def _load_art():
    global STYLE, GREEN, NEG, NOLIVING, DEFAULT_MODEL, PRO_MODEL
    try:
        cur, buf, sez = None, [], {}
        for line in open(SPEC_ART, encoding='utf-8'):
            if line.startswith('## '):
                if cur: sez[cur] = '\n'.join(buf).strip()
                cur, buf = line[3:].strip(), []
            elif cur:
                buf.append(line.rstrip('\n'))
        if cur: sez[cur] = '\n'.join(buf).strip()
        STYLE = sez.get('STYLE', STYLE); GREEN = sez.get('GREEN', GREEN)
        NEG = sez.get('NEG', NEG); NOLIVING = sez.get('NOLIVING', NOLIVING)
        if sez.get('MODELLO_DEFAULT'): DEFAULT_MODEL = sez['MODELLO_DEFAULT'].splitlines()[0].strip()
        if sez.get('MODELLO_PRO'): PRO_MODEL = sez['MODELLO_PRO'].splitlines()[0].strip()
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'⚠ Art Supervisor: spec agente non caricata ({e}); uso i valori interni')
_load_art()

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
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=240) as r:
            d = json.load(r)
    except Exception as e:
        print(f'    ⚠ generazione fallita ({e})'); return False
    for p in d.get('candidates', [{}])[0].get('content', {}).get('parts', []):
        if 'inlineData' in p:
            raw = base64.b64decode(p['inlineData']['data'])
            # normalizza sempre a PNG (l'API può restituire JPEG)
            open(dest + '.raw', 'wb').write(raw)
            Image.open(dest + '.raw').convert('RGB').save(dest)
            os.remove(dest + '.raw')
            _log(model, 1)
            return True
    # nessuna immagine (spesso contenuto vietato: es. marchi/personaggi protetti):
    # NON far crashare l'intera produzione — segnala e vai avanti.
    fr = d.get('candidates', [{}])[0].get('finishReason', '')
    print(f'    ⚠ nessuna immagine ({fr or "sconosciuto"})'
          + ('  ← contenuto vietato dal modello' if fr == 'PROHIBITED_CONTENT' else ''))
    return False

def gen_qc(model, key, prompt, dest, aspect, ref, qckind, qcfmt, qcref=None, maxq=None, pro=True):
    """Genera CON controllo qualità: genera → giudica → se bocciato rigenera con i
    difetti in prompt, fino a `maxq` tentativi. `pro`: se True l'ultimo tentativo
    passa al modello pro (utile su stanza/maschera; inutile e costoso sui fogli
    sprite, dove si tiene pro=False). Ritorna (ok, verdetto)."""
    maxq = maxq or MAX_QC
    cur, last = prompt, None
    for att in range(1, maxq + 1):
        m = PRO_MODEL if (pro and maxq > 1 and att == maxq) else model
        if not gen(m, key, cur, dest, aspect=aspect, ref=ref):
            last = {'ok': False, 'stato': 'errore',
                    'difetti': ['immagine non generata (contenuto vietato o errore API)']}
            if att < maxq:
                continue
            print(f'    ⚠ {qckind or "asset"}: immagine non generata dopo {maxq} tentativi — segnalato')
            return False, last
        if not qckind:
            return True, None
        v = qc.judge(qckind, dest, key, ref_path=qcref, **(qcfmt or {}))
        last = v
        if v['ok']:
            print(f'    ✓ qc {qckind} (tentativo {att}/{maxq}, {m.split("-")[-2]})')
            return True, v
        if v.get('stato') == 'errore':        # QC indisponibile: non sprecare rigenerazioni
            print(f'    ⚠ qc {qckind}: {v["difetti"][0]} → asset segnalato per revisione umana')
            return False, v
        dif = '; '.join(v['difetti'])[:200]
        print(f'    ✗ qc {qckind} [{att}/{maxq}]: {dif}')
        corr = v.get('correzione') or 'Fix all listed defects.'
        cur = (prompt + "\n\nIMPORTANT — the previous attempt was REJECTED by quality control "
               "for these defects: " + ' | '.join(v['difetti']) +
               f". You MUST correct them now: {corr}")
    print(f'    ⚠ {qckind}: ancora imperfetto dopo {maxq} tentativi — segnalato per revisione')
    return False, last

# ---- specifiche degli asset: come costruire il prompt e come processare ----
def build_specs(brief):
    P, S = brief['protagonista'], brief.get('secondario', '')
    tech = ("Four full-body frames in one horizontal row, evenly spaced at identical scale, each frame "
            "an ISOLATED figure with a clear WIDE vertical green gap between figures (they must never "
            "touch). NO ground line, NO floor, NO baseline or connecting shadow between the figures — "
            "only the characters on flat green, nothing else. Feet at the same height in each frame.")
    order = ("Frame order left-to-right: 1) idle; 2) walk step A; 3) walk step B; 4) interaction, "
             "reaching one hand toward an unseen off-frame object (do NOT draw any object).")
    # Solo 3 direzioni: 'down'=frontale, 'up'=di spalle, 'right'=profilo destro.
    # La SINISTRA non si genera: il motore la ottiene riflettendo la destra
    # (mirroring) — meno sprite, meno costi, orientamento sempre corretto.
    faces = {'protagonista_down': 'strictly FRONT-FACING (facing the camera) in all four frames, do not turn to profile',
             'protagonista_up':   'seen from BEHIND (back-facing) in all four frames',
             'protagonista_right':'in RIGHT-SIDE profile, walking to the right'}
    specs = []
    dirdesc = {'protagonista_down': 'frontal', 'protagonista_up': 'back-facing',
               'protagonista_right': 'right-side profile'}
    for name, face in faces.items():
        specs.append(dict(name=name, kind='char', frames=4, fh=242, aspect='16:9', green=True,
            ref=(name != 'protagonista_down'),  # gli altri usano il down come riferimento
            qckind='sheet', qcfmt=dict(n=4,
                desc=f"{dirdesc[name]} walk cycle: 1) idle, 2) walk step A, 3) walk step B, "
                     f"4) interaction reaching one hand — ALL standing, NO sitting/crouching"),
            prompt=f"{STYLE} A walk-cycle sprite SHEET of {P}, {face}. {tech} {order} "
                   f"Every frame is STANDING on both feet (never sitting, kneeling or crouching). "
                   f"Identical character design in every frame. {GREEN} {NEG}"))
    if S:
        specs.append(dict(name='secondario_emo', kind='char', frames=5, fh=262, aspect='16:9', green=True, ref=True,
            qckind='sheet', qcfmt=dict(n=5, desc="front-view acting: idle smile, bashful, speaking, "
                     "thoughtful, amused — one standing figure per cell, same character"),
            prompt=f"{STYLE} Front-view acting SHEET of {S}, 5 frames in one row, stands still. Order: "
                   f"1) idle warm smile; 2) bashful hand behind neck; 3) speaking open-hand gesture; "
                   f"4) thoughtful hand on chin; 5) amused arms crossed. Expressive on-model face. {GREEN} {NEG}"))
        # momento speciale: di default un ballo lento a 5 pose; personalizzabile
        # (es. i due fratelli che esultano). Il numero di pose è configurabile:
        # per gesti statici (esultanza) 2 pose sono più affidabili di 5.
        # momento speciale: di default un ballo lento a 5 pose; personalizzabile
        # (es. i fratelli che esultano). momento_frames=0 → nessuno sprite coppia
        # (la scena speciale è testuale, es. il gol): non si genera ballo5.
        momento = brief.get('momento_speciale',
                            'embracing in a slow romantic dance, tender micro-movements')
        nm = int(brief.get('momento_frames', 5))
        num = {2: 'two', 3: 'three', 4: 'four', 5: 'five'}.get(nm, 'five')
        if nm >= 2:
            specs.append(dict(name='ballo5', kind='char', frames=nm, fh=312, aspect='16:9', green=True, ref=True,
                qckind='sheet', qcfmt=dict(n=nm, desc=f"{num} poses of the SAME two characters TOGETHER in ONE "
                         "single row, one two-figure group per cell, the special moment"),
                prompt=f"{STYLE} Sprite SHEET, ONE SINGLE HORIZONTAL ROW of EXACTLY {num} cells side by side (NOT a "
                       f"grid, NOT two rows): in EACH cell the SAME two people, {P} and {S}, TOGETHER {momento}. "
                       f"The {num} cells are {num} slightly different frames of that same two-person pose (small "
                       f"movement between them). WIDE vertical green gap between cells; cells never overlap. NO "
                       f"ground line, NO connecting shadow. Consistent design. {GREEN} {NEG}"))
    if brief.get('animale'):
        specs.append(dict(name='gatto', kind='char', frames=2, fh=240, aspect='16:9', green=True, ref=False,
            qckind='sheet', qcfmt=dict(n=2, desc="2 poses of the SAME cat: sleeping curled, then awake head "
                     "raised — one cat per cell"),
            prompt=f"{STYLE} SHEET of EXACTLY TWO cells in ONE SINGLE HORIZONTAL ROW, side by side "
                   f"(NOT a 2x2 grid, NOT stacked, NEVER more than two): {brief['animale']} on the floor — "
                   f"left cell 1) sleeping curled; right cell 2) awake head raised. The SAME single animal in "
                   f"both cells, wide green gap between them. {GREEN} {NEG}"))
    # stanza (2 frame, niente verde) + popup
    room = brief.get('stanza', 'cozy candle-lit room')
    objs = brief.get('oggetti', ['a record player', 'a TV with a blanket', 'a writing desk'])
    anim = brief.get('animati', 'candle flames flicker, small reflections shift')
    objlist = '; '.join(f'{chr(65+i)}) {o}' for i, o in enumerate(objs))
    specs.append(dict(name='stanza_bg', kind='room', aspect='1:1', green=False,
        qckind='room', qcfmt={},
        prompt=f"{STYLE} Top-down 3/4 cozy-sim view, square room, EMPTY stage, NO green screen. {room}. "
               f"Back wall occupies the top ~20-25%; rest is walkable floor. Place these clue objects, each "
               f"clearly separated and readable, spread around the room (some on the walls, some on furniture, "
               f"some on the floor): {objlist}. Keep an open central-bottom space to stand and a window on the "
               f"back wall onto the night. Readable, lived-in but UNOCCUPIED. {NOLIVING} {NEG}"))
    specs.append(dict(name='stanza_bg2', kind='room', aspect='1:1', green=False, ref_room=True,
        qckind='room_anim', qcfmt=dict(anim=anim),
        prompt=f"Take the reference room image and change ONLY these animated elements: {anim}. Do NOT add, "
               f"remove or move anything else — every object, wall and piece of furniture stays pixel-identical "
               f"and in the exact same place, so the two frames loop without jitter. Do NOT add any creature. "
               f"Square, same framing. {NOLIVING}"))
    # NB: i popup NON si generano più — si RITAGLIANO dalla stanza (vedi _crop_popup
    # in main, dopo la localizzazione): zero generazioni e allineamento garantito
    # all'oggetto reale della scena.
    # maschera di collisione della stanza (per le collisioni pixel-accurate)
    specs.append(dict(name='mask', kind='mask', aspect='1:1', green=False, ref_room=True,
        qckind='mask', qcfmt={},
        prompt="Redraw this room as a FLAT STENCIL COLLISION MASK: solid filled silhouettes ONLY. "
               "ABSOLUTELY NO line art, NO outlines, NO plank lines, NO patterns, NO text, NO shading — "
               "every area is ONE uniform flat fill. Exactly two colors: PURE WHITE #FFFFFF for the entire "
               "walkable floor (rugs, mats and small floor items are WHITE/walkable); PURE BLACK #000000 "
               "for everything a person cannot walk through — ALL walls, the ENTIRE top back-wall and sloped "
               "ceiling band (this whole upper area MUST be black), the round window, and the FOOTPRINT of "
               "volumetric furniture (fireplace, bookshelf, sofa, armchair, tables, chairs), plus everything "
               "outside the room. There are NO people or animals in this room: draw NO character silhouettes. "
               "Big solid black shapes for walls and furniture, big solid white for the floor."))
    return specs

def process_char(srcpng, name, frames, fh, outdir):
    """Ritorna (fw, n_celle) oppure None se il foglio ha troppe poche celle."""
    rgba = sprites.load_rgba_keyed(srcpng)
    cells = sprites.cells_grid(rgba)
    n = len(cells)
    if n > frames:
        if sprites.n_bands(rgba) > 1:    # griglia multi-riga: prendi la prima riga
            cells = cells[:frames]       # (ordine di lettura: alto→basso, sx→dx)
        else:                            # riga unica sovra-segmentata (arto staccato)
            cells = sprites.cells_grid(rgba, expect=frames)
        n = len(cells)
    if n != frames:
        print(f'  ⚠ {name}: trovate {n} celle invece di {frames}')
        if n < 2: return None
        if n > frames: cells = cells[:frames]; n = frames
    sprites.OUT = outdir
    return sprites.pack(cells, fh, name), n


def _ritratti(spr_dir, fw, prefix='pt_secondario', sheet='secondario_emo', fh=262, N=5):
    """Ritaglia i ritratti (volto) dai frame del foglio impacchettato."""
    im = Image.open(os.path.join(spr_dir, sheet + '.png')).convert('RGBA')
    for i in range(N):
        fr = im.crop((i * fw, 0, (i + 1) * fw, fh)); al = np.array(fr)[:, :, 3]
        ys, xs = np.where(al > 10)
        if not len(ys): continue
        top = ys.min(); side = min(fw, fh - top)
        head = al[top:top + side // 2]; hx = np.where(head.any(axis=0))[0]
        cx = (hx.min() + hx.max()) // 2; x0 = max(0, min(fw - side, cx - side // 2))
        fr.crop((x0, top, x0 + side, top + side)).resize((128, 128), Image.LANCZOS)\
          .save(os.path.join(spr_dir, f'{prefix}_{i}.png'))

def _pt_gatto(spr, fw):
    im = Image.open(os.path.join(spr, 'gatto.png')).convert('RGBA')
    fr = im.crop((fw, 0, 2 * fw, im.size[1])); al = np.array(fr)[:, :, 3]
    ys, xs = np.where(al > 10)
    if len(ys):
        fr.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))\
          .resize((128, 128), Image.LANCZOS).save(os.path.join(spr, 'pt_gatto.png'))


def _wire_sprites(cfg, dims, ncells, produced):
    KEEP = {'bg', 'bg2'}                    # fondali: sempre presenti, il motore li usa
    sp = json.load(open(os.path.join(cfg, 'sprites.json'), encoding='utf-8'))
    sheets, pers = sp['sheets'], sp['personaggi']
    for key in list(sheets.keys()):
        a = sheets[key].get('asset')
        if a in KEEP:
            continue
        if a in dims:
            sheets[key]['fw'] = dims[a]
            if a in ncells: sheets[key]['n'] = ncells[a]
        else:
            del sheets[key]                 # protagonista_left (mirroring) o foglio non generato (modulare)
    pers.get('player', {}).get('fogli', {}).pop('left', None)
    for role in ('npc', 'coppia', 'gatto'):
        if role in pers and pers[role].get('foglio') not in sheets:
            del pers[role]
    # il ballo può uscire con meno pose del previsto: adatta la seq ai frame reali
    cop = pers.get('coppia')
    if cop and cop.get('foglio') in sheets:
        n = sheets[cop['foglio']].get('n', 5)
        seq = list(range(n)) + list(range(n - 2, 0, -1))   # ping-pong 0..n-1..1
        cop.setdefault('anim', {})['seq'] = seq
    json.dump(sp, open(os.path.join(cfg, 'sprites.json'), 'w'), ensure_ascii=False, indent=2)


def _wire_manifest(pack_dir, produced, dims):
    man = json.load(open(os.path.join(pack_dir, 'manifest.json'), encoding='utf-8'))
    amap = {n: f'sprites/{n}.png' for n in
            ('protagonista_down', 'protagonista_up', 'protagonista_right',
             'secondario_emo', 'ballo5', 'gatto') if n in dims}
    if 'secondario_emo' in dims:
        amap.update({f'pt_secondario_{i}': f'sprites/pt_secondario_{i}.png' for i in range(5)})
    if 'gatto' in dims: amap['pt_gatto'] = 'sprites/pt_gatto.png'
    amap['bg'] = 'rooms/stanza_bg.png'; amap['bg2'] = 'rooms/stanza_bg2.png'
    for n in sorted(produced):
        if n.startswith('pop_'):
            amap[n] = f'popup/{n}.png'
    man['assets'] = amap
    json.dump(man, open(os.path.join(pack_dir, 'manifest.json'), 'w'), ensure_ascii=False, indent=2)


def _crop_popup(room_png, center, out, w=0.12, h=0.16):
    """Ritaglia il primo piano di un oggetto DALLA stanza (allineamento garantito:
    è esattamente lo stesso oggetto), lo rende quadrato e lo porta a 340px con
    upscale NEAREST (pixel netti). Zero generazioni."""
    im = Image.open(room_png).convert('RGB')
    W, H = im.size
    cx, cy = center[0] / 100 * W, center[1] / 100 * H
    x0 = max(0, int(cx - w * W)); y0 = max(0, int(cy - h * H))
    x1 = min(W, int(cx + w * W)); y1 = min(H, int(cy + h * H))
    crop = im.crop((x0, y0, x1, y1))
    side = max(crop.size)
    sq = Image.new('RGB', (side, side), (20, 15, 12))
    sq.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2))
    sq.resize((340, 340), Image.NEAREST).save(out)


def _localizza(room_png, objs, key, model='gemini-2.5-flash'):
    """Agente-vista: trova nella stanza il CENTRO di ogni oggetto-indizio (x%,y%),
    così la stellina va SULL'oggetto (non su un punto vuoto del pavimento). In caso
    di errore ritorna [] e il piazzamento ripiega sui punti calpestabili."""
    import ssl as _ssl
    numbered = '\n'.join(f'{i+1}. {o}' for i, o in enumerate(objs))
    schema = {'type': 'object', 'properties': {'posizioni': {'type': 'array', 'items': {
        'type': 'object', 'properties': {'x': {'type': 'number'}, 'y': {'type': 'number'}},
        'required': ['x', 'y']}}}, 'required': ['posizioni']}
    b = base64.b64encode(open(room_png, 'rb').read()).decode()
    prompt = ("Guarda l'immagine della stanza. Per ognuno di questi oggetti indica il CENTRO come "
              "percentuali x,y (0-100; x=da sinistra a destra, y=dall'alto in basso), NELLO STESSO "
              f"ORDINE e stesso numero:\n{numbered}\nRitorna 'posizioni' con un {{x,y}} per oggetto.")
    body = json.dumps({'contents': [{'parts': [{'inlineData': {'mimeType': 'image/png', 'data': b}},
        {'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json',
        'responseSchema': schema, 'temperature': 0.1}}).encode()
    for m in (model, 'gemini-flash-latest'):
        try:
            req = urllib.request.Request(
                f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent',
                data=body, headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
                d = json.load(r)
            pos = json.loads(d['candidates'][0]['content']['parts'][0]['text'])['posizioni']
            _log(m + ' (localizza)', 0)
            return [[max(0, min(100, float(p['x']))), max(0, min(100, float(p['y'])))] for p in pos]
        except Exception:
            continue
    return []


def _lontano(a, b, m=14):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 >= m * m


def _clamp(p, B, m=1.0):
    """Riporta il punto dentro i limiti stanza (la griglia 128 può cadere di una
    frazione fuori dai bounds full-res: il motore taglierebbe la cella)."""
    return [min(max(p[0], B['xMin'] + m), B['xMax'] - m),
            min(max(p[1], B['yMin'] + m), B['yMax'] - m)]


def _wire_pack(pack_dir, dims, ncells, produced, markers=None):
    cfg = os.path.join(pack_dir, 'config')
    # wall_top: fascia alta forzata a muro (i personaggi non fluttuano sulla parete)
    info = collmask.derive(os.path.join(pack_dir, 'assets', '_src', 'mask.png'), wall_top=0.15)
    grid = info['grid']; B = info['bounds']
    spawn = _clamp(collmask.entrance(grid), B)    # ingresso: basso-centro (non sul gatto)
    reach = collmask.flood(grid, spawn)           # SOLO il pavimento connesso allo spawn
    # candidati con spazio libero attorno, nel corpo navigabile principale
    cand = collmask.spread_open(reach, 24, min_clear=2.0)
    yfloor = B['yMin'] + 0.28 * (B['yMax'] - B['yMin'])   # niente personaggi sul muro alto
    # gatto: punto ampio raggiungibile dal protagonista (il gatto non è un ostacolo)
    g0 = collmask.nearest(reach, info['gatto'])
    cat_pos = g0 if (g0[1] >= yfloor and collmask.engine_reachable(grid, B, spawn, [g0])[0]) \
        else next((p for p in cand if p[1] >= yfloor
                   and collmask.engine_reachable(grid, B, spawn, [p])[0]), cand[0])
    # NPC: il primo candidato ben distanziato la cui APPROACH resta raggiungibile
    # anche col PROPRIO corpo presente (così non tappa il suo corridoio)
    npc_pos = next((p for p in cand
                    if p[1] >= yfloor and _lontano(p, spawn) and _lontano(p, cat_pos)
                    and collmask.engine_reachable(grid, B, spawn, [p], obstacle=p)[0]), None)
    if npc_pos is None:
        npc_pos = next((p for p in cand if collmask.engine_reachable(grid, B, spawn, [p], obstacle=p)[0]), spawn)
    # quanti indizi vuole il pack (N variabile): lo dice interactions.json
    it = json.load(open(os.path.join(cfg, 'interactions.json'), encoding='utf-8'))
    nclue = max(1, len(it.get('sorprese', [])))
    # indizi: punti raggiungibili col secondario piazzato, distanziati tra loro
    okc = collmask.engine_reachable(grid, B, spawn, cand, obstacle=npc_pos)
    pool = [p for p, o in zip(cand, okc) if o and p[1] >= yfloor and _lontano(p, spawn)]
    clues = []
    for p in pool:
        if all(_lontano(p, c, 9) for c in clues) and _lontano(p, npc_pos, 8) and _lontano(p, cat_pos, 8):
            clues.append(p)
        if len(clues) == nclue:
            break
    clues = (clues + pool + cand)[:nclue]
    # tutti i punti sono già centro-cella dentro `reach`: nessun clamp che li sposti fuori
    # room.json: collisioni dalla maschera. bounds allargati di ~1 cella così il
    # limite duro non blocca mai una cella calpestabile di bordo.
    room = json.load(open(os.path.join(cfg, 'room.json'), encoding='utf-8'))
    bb = dict(info['bounds']); mg = 100.0 / 128
    bb['xMin'] -= mg; bb['yMin'] -= mg; bb['xMax'] += mg; bb['yMax'] += mg
    room['bounds'] = bb; room['colliders'] = []
    room['dietroLetto'] = {'pts': []}; room['walk'] = info['walk']
    json.dump(room, open(os.path.join(cfg, 'room.json'), 'w'), ensure_ascii=False, indent=2)
    # characters.json: spawn/npc/gatto su punti calpestabili
    ch = json.load(open(os.path.join(cfg, 'characters.json'), encoding='utf-8'))
    ch['posizioni']['protagonista'] = {'x': spawn[0], 'y': spawn[1]}
    ch['posizioni']['secondario'] = {'x': npc_pos[0], 'y': npc_pos[1]}
    if 'gatto' in dims:
        ch.setdefault('gatto', {}); ch['gatto']['x'] = cat_pos[0]; ch['gatto']['y'] = cat_pos[1]
    json.dump(ch, open(os.path.join(cfg, 'characters.json'), 'w'), ensure_ascii=False, indent=2)
    # interactions.json: la STELLINA (x,y) va SULL'oggetto localizzato nella
    # stanza; il punto d'ARRIVO (ax,ay) è il pavimento raggiungibile più vicino
    # (il protagonista ci cammina e apre lì). Ogni sorpresa punta al proprio popup.
    sorprese = it.get('sorprese', [])
    body = collmask.floor_body(reach, 2.0)             # corpo navigabile (arrivi sempre raggiungibili)
    arrivi = []
    for i, s in enumerate(sorprese):
        mk = markers[i] if (markers and i < len(markers)) else None
        if mk:
            arr = collmask.nearest(body, mk)           # pavimento NAVIGABILE più vicino all'oggetto
            s['x'] = round(mk[0], 1); s['y'] = round(mk[1], 1)      # stellina sull'oggetto
        else:
            arr = clues[i] if i < len(clues) else spawn
            s['x'] = arr[0]; s['y'] = arr[1]
        s['ax'] = arr[0]; s['ay'] = arr[1]; s['ri'] = 6
        arrivi.append(arr)
        if f'pop_indizio_{i+1}' in produced:
            s['img'] = f'{{{{B64:pop_indizio_{i+1}}}}}'
    json.dump(it, open(os.path.join(cfg, 'interactions.json'), 'w'), ensure_ascii=False, indent=2)
    _wire_sprites(cfg, dims, ncells, produced)
    _wire_manifest(pack_dir, produced, dims)
    # QA raggiungibilità col MODELLO DEL MOTORE (indizi + eventuale gatto senza
    # ostacolo, NPC col proprio corpo presente)
    targets = list(arrivi) + ([cat_pos] if 'gatto' in dims else [])
    labels = [f'indizio {i+1}' for i in range(len(arrivi))] + (['gatto'] if 'gatto' in dims else [])
    reach = collmask.engine_reachable(grid, bb, spawn, targets)
    reach.append(collmask.engine_reachable(grid, bb, spawn, [npc_pos], obstacle=npc_pos)[0])
    labels.append('NPC')
    print('\n🧭 QA raggiungibilità nel gioco (dallo spawn):')
    allok = True
    for lab, ok in zip(labels, reach):
        print(f'   {"✓" if ok else "✗"} {lab}'); allok = allok and ok
    print(f'   calpestabile {info["calpestabile_pct"]}% · spawn {spawn} · gatto {cat_pos}')
    if not allok:
        print('   ⚠ punti non raggiungibili: la stanza è troppo chiusa, rigenera stanza+maschera')
    return allok


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
    dims = {}; ncells = {}; produced = set(); imperfetti = []
    n_before = _count()
    for s in specs:
        print(f'· genero {s["name"]} …')
        qk, qf = s.get('qckind'), s.get('qcfmt')
        if s['kind'] == 'char':
            raw = os.path.join(src, s['name'] + '.png')
            # fogli sprite: cap a 2 tentativi e NIENTE pro (non aiuta, costa)
            ok, _ = gen_qc(model, key, s['prompt'], raw, s.get('aspect'),
                           ref_prota if s.get('ref') else None, qk, qf, maxq=2, pro=False)
            if not ok: imperfetti.append(s['name'])
            if not os.path.exists(raw): continue      # immagine non prodotta: salta
            r = process_char(raw, s['name'], s['frames'], s['fh'], spr)
            if r:
                dims[s['name']] = r[0]; ncells[s['name']] = r[1]; produced.add(s['name'])
                sprites.pixelate(os.path.join(spr, s['name'] + '.png'), colors=64)  # palette 16-bit + caldo
        elif s['kind'] == 'room':
            out = os.path.join(rooms, s['name'] + '.png')
            # stanza: fino a 3 tentativi, pro all'ultimo (qui il pro aiuta davvero)
            ok, _ = gen_qc(model, key, s['prompt'], out, '1:1',
                           ref_room if s.get('ref_room') else None, qk, qf,
                           qcref=ref_room if qk == 'room_anim' else None, maxq=3, pro=True)
            if not ok: imperfetti.append(s['name'])
            if not os.path.exists(out): continue
            sprites.pixelate(out, target=448, colors=64)   # vero 16-bit netto + grade caldo
            produced.add(s['name'])
        elif s['kind'] == 'mask':
            mp = os.path.join(src, 'mask.png')
            ok, _ = gen_qc(model, key, s['prompt'], mp, '1:1',
                           ref_room if s.get('ref_room') else None, qk, qf, maxq=3, pro=True)
            if not ok: imperfetti.append(s['name'])
            if os.path.exists(mp): produced.add('mask')

    if 'secondario_emo' in dims:
        _ritratti(spr, dims['secondario_emo'])
    if 'gatto' in dims:
        _pt_gatto(spr, dims['gatto'])
    if not only:
        # agente-vista: dove sta ogni oggetto-indizio nella stanza (per stelline + ritagli)
        markers = _localizza(ref_room, brief.get('oggetti', []), key) if os.path.exists(ref_room) else []
        if markers:
            print(f'   📍 oggetti localizzati nella stanza: {len(markers)}')
        # popup RITAGLIATI dalla stanza sull'oggetto localizzato: 0 generazioni,
        # allineamento garantito (è esattamente lo stesso oggetto della scena)
        if os.path.exists(ref_room):
            for i, mk in enumerate(markers):
                _crop_popup(ref_room, mk, os.path.join(pops, f'pop_indizio_{i+1}.png'))
                produced.add(f'pop_indizio_{i+1}')
            _crop_popup(ref_room, [50, 13], os.path.join(pops, 'pop_finestra.png'), w=0.16, h=0.13)
            produced.add('pop_finestra')
        _wire_pack(pack_dir, dims, ncells, produced, markers)   # collisioni, posizioni, cablaggio, QA

    if imperfetti:
        print(f'\n⚠ asset ancora imperfetti dopo il QC ({MAX_QC} tentativi): {", ".join(imperfetti)}')
        print('   → rilancia `sad genera {slug} --assets ' + ','.join(imperfetti) + '` o rivedi il brief')
    else:
        print('\n✅ QC visivo superato da tutti gli asset')
    print(f'💸 immagini generate stavolta: {_count()-n_before} · registro: {USAGE}')
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
