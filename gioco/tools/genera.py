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

# ---- Style Bible (invariato: il DNA visivo SempreAddue) ----
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
  "NO human figures or silhouettes, NO cats, NO dogs, NO animals or pets anywhere. Only "
  "architecture, furniture and inanimate objects. Living things are separate sprites, never "
  "painted into this image.")

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

def gen_qc(model, key, prompt, dest, aspect, ref, qckind, qcfmt, qcref=None):
    """Genera CON controllo qualità: genera → giudica → se bocciato rigenera con i
    difetti in prompt, fino a MAX_QC tentativi; all'ultimo tentativo passa al modello
    pro (più preciso). Ritorna (ok, verdetto). Così ogni asset esce corretto sia
    tecnicamente sia esteticamente prima di entrare nella build."""
    cur, last = prompt, None
    for att in range(1, MAX_QC + 1):
        m = model if att < MAX_QC else PRO_MODEL          # ultimo colpo: modello pro
        gen(m, key, cur, dest, aspect=aspect, ref=ref)
        if not qckind:
            return True, None
        v = qc.judge(qckind, dest, key, ref_path=qcref, **(qcfmt or {}))
        last = v
        if v['ok']:
            print(f'    ✓ qc {qckind} (tentativo {att}/{MAX_QC}, {m.split("-")[-2]})')
            return True, v
        dif = '; '.join(v['difetti'])[:200]
        print(f'    ✗ qc {qckind} [{att}/{MAX_QC}]: {dif}')
        corr = v.get('correzione') or 'Fix all listed defects.'
        cur = (prompt + "\n\nIMPORTANT — the previous attempt was REJECTED by quality control "
               "for these defects: " + ' | '.join(v['difetti']) +
               f". You MUST correct them now: {corr}")
    print(f'    ⚠ {qckind}: ancora imperfetto dopo {MAX_QC} tentativi — segnalato per revisione')
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
        specs.append(dict(name='ballo5', kind='char', frames=5, fh=312, aspect='16:9', green=True, ref=True,
            qckind='sheet', qcfmt=dict(n=5, desc="5 dancing poses of the SAME couple embracing, "
                     "one couple-figure per cell, chained tender micro-movements"),
            prompt=f"{STYLE} Sprite SHEET of EXACTLY five dancing poses in one horizontal row: {P} and {S} "
                   f"embracing in a slow dance, tender micro-movements that chain smoothly. Each of the five "
                   f"poses is a SEPARATE couple-figure with a WIDE vertical green gap between poses — poses "
                   f"never overlap or touch horizontally. NO ground line, NO connecting shadow. Same two "
                   f"characters, consistent design. {GREEN} {NEG}"))
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
    specs.append(dict(name='stanza_bg', kind='room', aspect='1:1', green=False,
        qckind='room', qcfmt={},
        prompt=f"{STYLE} Top-down 3/4 cozy-sim view, square room, EMPTY stage, NO green screen. {room}. "
               f"Back wall occupies the top ~20-25%; rest is warm walkable floor. Clearly separated: "
               f"clue object A ({objs[0]}) on the UPPER-LEFT; clue object B ({objs[1]}) on the RIGHT; "
               f"clue object C ({objs[2]}) LOWER-LEFT on furniture; an open central-bottom space; a "
               f"window on the back wall onto the night. Readable, lived-in but UNOCCUPIED. {NOLIVING} {NEG}"))
    specs.append(dict(name='stanza_bg2', kind='room', aspect='1:1', green=False, ref_room=True,
        qckind='room_anim', qcfmt=dict(anim=anim),
        prompt=f"Take the reference room image and change ONLY these animated elements: {anim}. Do NOT add, "
               f"remove or move anything else — every object, wall and piece of furniture stays pixel-identical "
               f"and in the exact same place, so the two frames loop without jitter. Do NOT add any creature. "
               f"Square, same framing. {NOLIVING}"))
    for i, key in enumerate(['pop_vinile', 'pop_tv', 'pop_scrivania'][:len(objs)]):
        specs.append(dict(name=key, kind='popup', aspect='1:1', green=False,
            qckind='popup', qcfmt=dict(subj=objs[i]),
            prompt=f"{STYLE} Square intimate close-up of {objs[i]}, same world and candlelight as the room, "
                   f"cozy atmosphere. No text. {NEG}"))
    specs.append(dict(name='pop_finestra', kind='popup', aspect='1:1', green=False,
        qckind='popup', qcfmt=dict(subj='the night view outside the window of this scene'),
        prompt=f"{STYLE} Square close-up of the view outside the window at night for this scene, atmospheric, "
               f"same palette as the room. No text. {NEG}"))
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
    for n in ('pop_vinile', 'pop_tv', 'pop_scrivania', 'pop_finestra'):
        if n in produced: amap[n] = f'popup/{n}.png'
    man['assets'] = amap
    json.dump(man, open(os.path.join(pack_dir, 'manifest.json'), 'w'), ensure_ascii=False, indent=2)


def _lontano(a, b, m=14):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 >= m * m


def _clamp(p, B, m=1.0):
    """Riporta il punto dentro i limiti stanza (la griglia 128 può cadere di una
    frazione fuori dai bounds full-res: il motore taglierebbe la cella)."""
    return [min(max(p[0], B['xMin'] + m), B['xMax'] - m),
            min(max(p[1], B['yMin'] + m), B['yMax'] - m)]


def _wire_pack(pack_dir, dims, ncells, produced):
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
    # indizi: punti raggiungibili col secondario piazzato, distanziati tra loro
    okc = collmask.engine_reachable(grid, B, spawn, cand, obstacle=npc_pos)
    pool = [p for p, o in zip(cand, okc) if o and p[1] >= yfloor and _lontano(p, spawn)]
    clues = []
    for p in pool:
        if all(_lontano(p, c, 10) for c in clues) and _lontano(p, npc_pos, 8) and _lontano(p, cat_pos, 8):
            clues.append(p)
        if len(clues) == 3:
            break
    clues = (clues + pool + cand)[:3]
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
    # interactions.json: i 3 indizi su punti calpestabili distanziati
    it = json.load(open(os.path.join(cfg, 'interactions.json'), encoding='utf-8'))
    for s, (x, y) in zip(it.get('sorprese', []), clues):
        s['x'] = x; s['y'] = y; s['ax'] = x; s['ay'] = y; s['ri'] = 6
    json.dump(it, open(os.path.join(cfg, 'interactions.json'), 'w'), ensure_ascii=False, indent=2)
    _wire_sprites(cfg, dims, ncells, produced)
    _wire_manifest(pack_dir, produced, dims)
    # QA raggiungibilità col MODELLO DEL MOTORE (indizi + gatto senza ostacolo,
    # NPC col proprio corpo presente)
    rc = collmask.engine_reachable(grid, bb, spawn, clues + [cat_pos])
    rn = collmask.engine_reachable(grid, bb, spawn, [npc_pos], obstacle=npc_pos)[0]
    reach = rc + [rn]
    labels = ['indizio 1', 'indizio 2', 'indizio 3', 'gatto', 'NPC']
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
            ok, _ = gen_qc(model, key, s['prompt'], raw, s.get('aspect'),
                           ref_prota if s.get('ref') else None, qk, qf)
            if not ok: imperfetti.append(s['name'])
            r = process_char(raw, s['name'], s['frames'], s['fh'], spr)
            if r: dims[s['name']] = r[0]; ncells[s['name']] = r[1]; produced.add(s['name'])
        elif s['kind'] == 'room':
            out = os.path.join(rooms, s['name'] + '.png')
            ok, _ = gen_qc(model, key, s['prompt'], out, '1:1',
                           ref_room if s.get('ref_room') else None, qk, qf,
                           qcref=ref_room if qk == 'room_anim' else None)
            if not ok: imperfetti.append(s['name'])
            Image.open(out).convert('RGB').resize((1024, 1024), Image.LANCZOS).save(out); produced.add(s['name'])
        elif s['kind'] == 'popup':
            out = os.path.join(pops, s['name'] + '.png')
            ok, _ = gen_qc(model, key, s['prompt'], out, '1:1', None, qk, qf)
            if not ok: imperfetti.append(s['name'])
            Image.open(out).convert('RGB').resize((512, 512), Image.LANCZOS).save(out); produced.add(s['name'])
        elif s['kind'] == 'mask':
            ok, _ = gen_qc(model, key, s['prompt'], os.path.join(src, 'mask.png'), '1:1',
                           ref_room if s.get('ref_room') else None, qk, qf)
            if not ok: imperfetti.append(s['name'])
            produced.add('mask')

    if 'secondario_emo' in dims:
        _ritratti(spr, dims['secondario_emo'])
    if 'gatto' in dims:
        _pt_gatto(spr, dims['gatto'])
    if not only:
        _wire_pack(pack_dir, dims, ncells, produced)   # collisioni, posizioni, cablaggio, QA

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
