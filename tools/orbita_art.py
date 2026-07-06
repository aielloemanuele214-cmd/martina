#!/usr/bin/env python3
"""Pipeline asset del pack 'ultima-orbita' (stile chibi 16-bit).
Affetta i fogli di riferimento AI (con titoli, etichette, note, diamanti) in
fogli-sprite puliti per il motore:
  - walk16  : camminata 4 direzioni x 4 frame (front/back/left/right)
  - expr16  : NPC, 5 espressioni (idle/sorriso/imbarazzo/sguardo/interazione)
  - dance16 : coppia, 5 pose di ballo rock
Metodo: si ritaglia la fascia dei titoli/etichette, si toglie lo sfondo navy
(flood dal bordo, incl. le ombre a terra), si scartano i frammenti piccoli
(testo, note musicali, diamanti), poi si tagliano le celle della griglia e si
impacchetta a scala comune (piedi a terra). Sincronizza le dimensioni in
sprites.json. Uso: python3 tools/orbita_art.py all
"""
import os, numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets', '_src') + os.sep
OUT = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets', 'sprites')
DBG = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets', '_dbg')
os.makedirs(OUT, exist_ok=True); os.makedirs(DBG, exist_ok=True)
NAVY = np.array([2, 16, 34])       # colore di sfondo dei fogli chibi
BLEED_IT = 26          # abbastanza da riempire di colore anche i buchi tappati


def key_navy(rgb, dist, minsize):
    """alpha=0 per lo sfondo navy collegato al bordo (incluse le ombre a terra);
    poi elimina i frammenti opachi piccoli (testo, note, diamanti). Color-bleed
    dei colori nei pixel trasparenti (niente frange al resize)."""
    a = rgb.astype(np.int32)
    d = np.sqrt(((a - NAVY) ** 2).sum(axis=2))
    # Lo sfondo navy è BLU-dominante; capelli castani e pelle sono CALDI
    # (rosso-dominante). Escludendo i pixel caldi dalla maschera di sfondo, i
    # capelli non vengono mai erosi dove toccano il navy → niente teste/caschi
    # staccati dal corpo (era il difetto della vista di spalle).
    warm = (a[:, :, 0] - a[:, :, 2]) > 8
    m = (d <= dist) & ~warm
    lbl, _ = ndimage.label(m)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    bg = np.isin(lbl, list(border))
    op = ~bg
    ol, n = ndimage.label(op)
    if n:
        sz = ndimage.sum(np.ones_like(ol), ol, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sz) if s >= minsize]
        op = np.isin(ol, keep)
    return np.dstack([a.astype(np.uint8), np.where(op, 255, 0).astype(np.uint8)])


def refine(sub):
    """Su una singola figura ritagliata: tappa i buchi RACCHIUSI (varchi scuri
    fra testa e casco, ecc.) e fa il color-bleed dei colori veri nei pixel
    trasparenti (buchi + bordo) → silhouette piena, niente frange né buchi."""
    op = sub[:, :, 3] > 0
    # chiude i varchi trasparenti SOTTILI interni (contorni scuri rimossi, l'anello
    # fra testa e casco) senza saldare i varchi larghi (gambe, spazio fra i due
    # ballerini), poi tappa tutto ciò che resta racchiuso.
    filled = ndimage.binary_fill_holes(ndimage.binary_closing(op, iterations=2))
    rgbf = sub[:, :, :3].astype(np.float32)
    known = op.copy()
    for _ in range(BLEED_IT):
        grown = ndimage.binary_dilation(known)
        ring = grown & ~known
        if not ring.any():
            break
        acc = np.zeros_like(rgbf); cnt = np.zeros(rgbf.shape[:2], np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                sh = np.roll(np.roll(rgbf, dy, 0), dx, 1)
                shk = np.roll(np.roll(known, dy, 0), dx, 1)
                mm = ring & shk
                acc[mm] += sh[mm]; cnt[mm] += 1
        mm = ring & (cnt > 0)
        rgbf[mm] = acc[mm] / cnt[mm][:, None]
        known |= mm
    out = sub.copy()
    out[:, :, :3] = np.clip(rgbf, 0, 255).astype(np.uint8)
    out[:, :, 3] = np.where(filled, 255, 0).astype(np.uint8)
    return out


def bands(occ, gap, minlen):
    """Segmenti dove occ>0, unendo i buchi <= gap; scarta i segmenti < minlen."""
    on = occ > 0
    segs = []; s = None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            segs.append((s, i - 1)); s = None
    if s is not None:
        segs.append((s, len(on) - 1))
    merged = []
    for a0, b0 in segs:
        if merged and a0 - merged[-1][1] <= gap:
            merged[-1] = (merged[-1][0], b0)
        else:
            merged.append((a0, b0))
    return [(a0, b0) for a0, b0 in merged if b0 - a0 >= minlen]


def cell(rgba, x0, x1, y0, y1):
    """Ritaglia la regione [x0:x1, y0:y1] stretta sui pixel opachi (una figura),
    poi ne rifinisce lo scontorno (tappa buchi + color-bleed)."""
    sub = rgba[y0:y1, x0:x1]
    op = sub[:, :, 3] > 0
    if not op.any():
        return None
    ys, xs = np.where(op)
    tight = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    return Image.fromarray(refine(tight))


def footcx(im):
    a = np.array(im)[:, :, 3]
    ys = np.where(a.any(axis=1))[0]
    band = a[max(0, ys[-1] - 12):ys[-1] + 1]
    xs = np.where(band.any(axis=0))[0]
    return (xs.min() + xs.max()) / 2


def pack(cells, fh, name, quantize=True):
    """Impacchetta a SCALA COMUNE (il frame più alto riempie fh): il corpo resta
    della stessa dimensione in tutti i frame (le braccia alzate escono in alto).
    Piedi a terra, centro-piedi al centro cella."""
    hmax = max(c.size[1] for c in cells)
    sc = (fh - 4) / hmax
    scaled = []
    for c in cells:
        w, h = c.size
        s = c.resize((max(1, round(w * sc)), max(1, round(h * sc))), Image.LANCZOS)
        scaled.append((s, footcx(s)))
    half = max(max(f, s.size[0] - f) for s, f in scaled)
    fw = int(np.ceil(half)) * 2 + 6
    sheet = Image.new('RGBA', (fw * len(scaled), fh), (0, 0, 0, 0))
    for i, (s, f) in enumerate(scaled):
        x = i * fw + round(fw / 2 - f)
        x = max(i * fw, min(x, (i + 1) * fw - s.size[0]))
        y = fh - 2 - s.size[1]
        sheet.paste(s, (x, y), s)
    if quantize:
        # quantizza solo RGB, riattacca l'alpha originale (niente trasparenze spurie)
        alpha = sheet.split()[3]
        rgb = sheet.convert('RGB').quantize(255, method=Image.FASTOCTREE).convert('RGB')
        sheet = Image.merge('RGBA', (*rgb.split(), alpha))
    path = os.path.join(OUT, name + '.png')
    sheet.save(path)
    print(f'{name}: n={len(scaled)} fw={fw} fh={fh} {os.path.getsize(path)//1024}KB')
    return {'fw': fw, 'fh': fh, 'n': len(scaled)}


def keyed(name, crop, dist, minsize):
    a = np.array(Image.open(SRC + name + '.png').convert('RGB'))[crop[1]:crop[3], crop[0]:crop[2]]
    rgba = key_navy(a, dist, minsize)
    prev = Image.new('RGBA', (rgba.shape[1], rgba.shape[0]), (255, 0, 255, 255))
    prev.alpha_composite(Image.fromarray(rgba))
    prev.convert('RGB').save(os.path.join(DBG, name + '_keyed.png'))
    return rgba


def dance_bounds():
    """5 pose del ballo: confini di cella dai marker rosa numerati (1..5)."""
    a = np.array(Image.open(SRC + 'dance16.png').convert('RGB')).astype(np.int32)
    top = a[250:360]
    R, G, B = top[:, :, 0], top[:, :, 1], top[:, :, 2]
    pink = (R > 200) & (G > 120) & (G < 200) & (B > 150) & (B < 220)
    lbl, n = ndimage.label(pink)
    sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    cx = sorted(int(np.where(lbl == i + 1)[1].mean()) for i, s in enumerate(sz) if s > 200)
    assert len(cx) == 5, f'attesi 5 marker, trovati {len(cx)}: {cx}'
    return [0] + [(cx[i] + cx[i + 1]) // 2 for i in range(4)] + [a.shape[1]]


def derivati():
    """Sfondo stanza (bg/bg2), popup (oblò, diario) e ritratti (npc, gatto)."""
    PK = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets') + os.sep
    ROOMS = PK + 'rooms' + os.sep; POP = PK + 'popup' + os.sep
    os.makedirs(ROOMS, exist_ok=True); os.makedirs(POP, exist_ok=True)
    Image.open(SRC + 'room.png').convert('RGB').save(ROOMS + 'orbita.jpg', quality=90)
    Image.open(SRC + 'oblo_round.png').convert('RGB').save(POP + 'pop_oblo.jpg', quality=90)
    d = Image.open(SRC + 'diario.png').convert('RGB'); w, h = d.size
    side = int(w * 0.82); cx = w // 2; cy = int(h * 0.62)
    d.crop((cx - side // 2, min(cy - side // 2, h - side),
            cx + side // 2, min(cy + side // 2, h))).save(POP + 'pop_diario.jpg', quality=90)
    # ritratti npc dal foglio astro2 impacchettato (testa di ogni frame)
    sheet = Image.open(OUT + os.sep + 'astro2.png').convert('RGBA')
    FW = sheet.width // 5; FH = sheet.height
    for i in range(5):
        fr = sheet.crop((i * FW, 0, (i + 1) * FW, FH)); al = np.array(fr)[:, :, 3]
        ys, xs = np.where(al > 10); top = ys.min(); s = min(FW, FH - top)
        hx = np.where(al[top:top + s // 2].any(axis=0))[0]; cxh = (hx.min() + hx.max()) // 2
        x0 = max(0, min(FW - s, cxh - s // 2))
        fr.crop((x0, top, x0 + s, top + s)).resize((128, 128), Image.LANCZOS).save(OUT + os.sep + f'pt_astro_{i}.png')
    # ritratto gatto (frame sveglio) dal vecchio foglio gatto
    g = Image.open(OUT + os.sep + 'gatto.png').convert('RGBA'); GFW = g.width // 2
    fr = g.crop((GFW, 0, 2 * GFW, g.height)); al = np.array(fr)[:, :, 3]
    ys, xs = np.where(al > 10); s = min(max(xs.max() - xs.min(), ys.max() - ys.min()) + 8, GFW)
    cxh = (xs.min() + xs.max()) // 2; ax = max(0, min(GFW - s, cxh - s // 2)); ay = max(0, min(g.height - s, ys.min() - 4))
    fr.crop((ax, ay, ax + s, ay + s)).resize((128, 128), Image.LANCZOS).save(OUT + os.sep + 'pt_gatto.png')
    print('sfondo, popup e ritratti generati')


DIMS = {}
if __name__ == '__main__':
    import sys, json
    only = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if only in ('all', 'walk'):
        rgba = keyed('walk16', (175, 165, 1254, 1254), 88, 700)
        rb = bands(rgba[:, :, 3].sum(1), 20, 40)
        cb = bands(rgba[:, :, 3].sum(0), 20, 25)
        assert len(rb) == 4 and len(cb) == 4, f'walk: griglia {len(rb)}x{len(cb)}'
        dirs = ['astro_down', 'astro_up', 'astro_left', 'astro_right']
        for r, dname in enumerate(dirs):
            frames = [cell(rgba, cb[c][0], cb[c][1] + 1, rb[r][0], rb[r][1] + 1) for c in range(4)]
            DIMS[dname] = pack([f for f in frames if f], 240, dname)

    if only in ('all', 'expr'):
        rgba = keyed('expr16', (0, 410, 1536, 860), 88, 900)
        cb = bands(rgba[:, :, 3].sum(0), 30, 40)
        assert len(cb) == 5, f'expr: colonne {len(cb)}'
        ry = np.where((rgba[:, :, 3] > 0).any(axis=1))[0]
        frames = [cell(rgba, cb[c][0], cb[c][1] + 1, ry.min(), ry.max() + 1) for c in range(5)]
        DIMS['astro2'] = pack(frames, 240, 'astro2')

    if only in ('all', 'dance'):
        rgba = keyed('dance16', (0, 360, 1536, 800), 90, 700)
        xb = dance_bounds()
        ry = np.where((rgba[:, :, 3] > 0).any(axis=1))[0]
        frames = [cell(rgba, xb[c], xb[c + 1], ry.min(), ry.max() + 1) for c in range(5)]
        DIMS['coppia'] = pack([f for f in frames if f], 300, 'coppia')

    if only in ('all', 'extra'):
        derivati()

    if only == 'all':
        spath = os.path.join(ROOT, 'packs', 'ultima-orbita', 'config', 'sprites.json')
        sp = json.load(open(spath, encoding='utf-8'))
        keymap = {'astroDown': 'astro_down', 'astroUp': 'astro_up', 'astroLeft': 'astro_left',
                  'astroRight': 'astro_right', 'astro2': 'astro2', 'coppia': 'coppia'}
        for sk, dk in keymap.items():
            if sk in sp['sheets'] and dk in DIMS:
                for f in ('fw', 'fh', 'n'):
                    sp['sheets'][sk][f] = DIMS[dk][f]
        open(spath, 'w', encoding='utf-8').write(json.dumps(sp, ensure_ascii=False, indent=2) + '\n')
        print('sprites.json: dimensioni fogli sincronizzate')

    print('\nDIMS =', DIMS)
