#!/usr/bin/env python3
"""Pipeline asset del pack 'ultima-orbita'.
Affetta i fogli di riferimento AI (personaggi con etichette) in fogli-sprite
pronti per il motore: scontorno (border-flood), packing a altezza uniforme,
piedi centrati. Stampa le dimensioni esatte da riportare in sprites.json.
"""
import os, numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets', '_src') + os.sep
OUT = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets', 'sprites')
DBG = os.path.join(ROOT, 'packs', 'ultima-orbita', 'assets', '_dbg')
os.makedirs(OUT, exist_ok=True); os.makedirs(DBG, exist_ok=True)
BLEED_IT = 10


def key_bg(rgb, ref, dist, dist2=None, dark_neutral=None):
    """alpha=0 per lo sfondo (pixel entro `dist` dal colore di riferimento `ref`):
    - le regioni collegate al bordo (sfondo esterno, anche con gradiente);
    - se `dist2` è dato, le SACCHE di sfondo INTRAPPOLATE il cui colore medio è
      a meno di `dist2` dal riferimento;
    - se `dark_neutral=(soglia, margine)` è dato (fogli su fondo scuro), anche i
      pixel scuri e NEUTRI/bluastri (sfondo navy + ombre nere nei varchi fra
      braccio e busto o fra i due corpi), preservando i capelli castani (R≫B).
    Il resto resta opaco. Poi color-bleed per evitare frange al resize."""
    a = rgb.astype(np.int32)
    d = np.sqrt(((a - np.array(ref)) ** 2).sum(axis=2))
    target = d <= dist
    lbl, n = ndimage.label(target)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    bg = np.isin(lbl, list(border))
    if dist2 is not None and n:
        meand = ndimage.mean(d, lbl, range(1, n + 1))
        trapped = [i + 1 for i, m in enumerate(meand) if m < dist2]
        if trapped:
            bg = bg | np.isin(lbl, trapped)
    if dark_neutral is not None:
        soglia, margine = dark_neutral
        somma = a.sum(axis=2)
        neutro = (somma < soglia) & ((a[:, :, 0] - a[:, :, 2]) < margine)
        bg = bg | neutro
    rgba = np.dstack([a.astype(np.uint8), np.where(bg, 0, 255).astype(np.uint8)])
    rgbf = rgba[:, :, :3].astype(np.float32)
    known = rgba[:, :, 3] > 0
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
                m = ring & shk
                acc[m] += sh[m]; cnt[m] += 1
        m = ring & (cnt > 0)
        rgbf[m] = acc[m] / cnt[m][:, None]
        known |= m
    rgba[:, :, :3] = np.clip(rgbf, 0, 255).astype(np.uint8)
    return rgba


def despeckle(rgba, minsize=550):
    """Elimina i granelli opachi isolati (scintille, rumore) più piccoli di minsize."""
    op = rgba[:, :, 3] > 0
    lbl, n = ndimage.label(op)
    if n <= 1:
        return rgba
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    keep = {i + 1 for i, s in enumerate(sizes) if s >= minsize}
    mask = np.isin(lbl, list(keep))
    rgba = rgba.copy()
    rgba[~mask, 3] = 0
    return rgba


def columns(rgba, gap=22, minw=25, mincol=18):
    """Segmenti di colonne con pixel opachi (celle affiancate).
    Una colonna 'conta' solo se ha almeno `mincol` pixel opachi (ignora il rumore)."""
    op = rgba[:, :, 3] > 0
    colmask = op.sum(axis=0) >= mincol
    segs = []; ins = False; s = 0
    for i, v in enumerate(colmask):
        if v and not ins:
            s = i; ins = True
        elif not v and ins:
            if i - s >= minw and (i - s) and (colmask[s:i].mean() > .3 or i-s>minw):
                segs.append((s, i - 1))
            ins = False
    if ins:
        segs.append((s, len(colmask) - 1))
    # unisci segmenti separati da micro-gap
    merged = []
    for a0, b0 in segs:
        if merged and a0 - merged[-1][1] <= gap:
            merged[-1] = (merged[-1][0], b0)
        else:
            merged.append((a0, b0))
    return [(a0, b0) for a0, b0 in merged if b0 - a0 >= minw]


def cell_crop(rgba, x0, x1):
    sub = rgba[:, x0:x1 + 1]
    op = sub[:, :, 3] > 0
    ys, xs = np.where(op)
    return Image.fromarray(sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def footcx(im):
    a = np.array(im)[:, :, 3]
    ys = np.where(a.any(axis=1))[0]
    band = a[max(0, ys[-1] - 12):ys[-1] + 1]
    xs = np.where(band.any(axis=0))[0]
    return (xs.min() + xs.max()) / 2


def pack(cells, fh, name, quantize=True):
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
    arr = np.array(sheet)[:, :, 3]
    bad = sum(1 for i in range(len(scaled))
              if arr[:, i*fw].any() or arr[:, (i+1)*fw-1].any() or arr[0, i*fw:(i+1)*fw].any())
    if quantize:
        # quantizza SOLO i canali RGB e riattacca l'alpha originale: la
        # quantize su RGBA di Pillow bucava le tute chiare (trasparenze spurie).
        alpha = sheet.split()[3]
        rgb = sheet.convert('RGB').quantize(255, method=Image.FASTOCTREE).convert('RGB')
        sheet = Image.merge('RGBA', (*rgb.split(), alpha))
    path = os.path.join(OUT, name + '.png')
    sheet.save(path)
    print(f'{name}: n={len(scaled)} fw={fw} fh={fh} '
          f'{os.path.getsize(path)//1024}KB  bordi-toccati={bad}')
    return {'fw': fw, 'fh': fh, 'n': len(scaled)}


def process(name, ref, dist, crop, expect, fh, out, dist2=None, dark_neutral=None):
    im = Image.open(SRC + name + '.png').convert('RGB')
    rgb = np.array(im)
    if crop:
        rgb = rgb[crop[1]:crop[3], crop[0]:crop[2]]
    rgba = key_bg(rgb, ref, dist, dist2, dark_neutral)
    rgba = despeckle(rgba)
    # anteprima keyed su fondo magenta per il controllo visivo
    prev = Image.new('RGBA', (rgba.shape[1], rgba.shape[0]), (255, 0, 255, 255))
    prev.alpha_composite(Image.fromarray(rgba))
    prev.convert('RGB').save(os.path.join(DBG, name + '_keyed.png'))
    segs = columns(rgba)
    print(f'{name}: colonne trovate = {len(segs)} -> {segs}')
    if len(segs) != expect:
        print(f'  ⚠ attese {expect} colonne')
    cells = [cell_crop(rgba, a0, b0) for a0, b0 in segs]
    return cells, rgba


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
    # ritratti npc (astro2) 128x128
    sheet = Image.open(OUT + os.sep + 'astro2.png').convert('RGBA'); FW, FH, N = 136, 262, 5
    for i in range(N):
        fr = sheet.crop((i * FW, 0, (i + 1) * FW, FH)); al = np.array(fr)[:, :, 3]
        ys, xs = np.where(al > 10); top = ys.min(); s = min(FW, FH - top)
        hx = np.where(al[top:top + s // 2].any(axis=0))[0]; cxh = (hx.min() + hx.max()) // 2
        x0 = max(0, min(FW - s, cxh - s // 2))
        fr.crop((x0, top, x0 + s, top + s)).resize((128, 128), Image.LANCZOS).save(OUT + os.sep + f'pt_astro_{i}.png')
    # ritratto gatto (frame sveglio)
    g = Image.open(OUT + os.sep + 'gatto.png').convert('RGBA'); GFW = 376
    fr = g.crop((GFW, 0, 2 * GFW, 240)); al = np.array(fr)[:, :, 3]
    ys, xs = np.where(al > 10); s = min(max(xs.max() - xs.min(), ys.max() - ys.min()) + 8, GFW)
    cxh = (xs.min() + xs.max()) // 2; ax = max(0, min(GFW - s, cxh - s // 2)); ay = max(0, min(240 - s, ys.min() - 4))
    fr.crop((ax, ay, ax + s, ay + s)).resize((128, 128), Image.LANCZOS).save(OUT + os.sep + 'pt_gatto.png')
    print('sfondo, popup e ritratti generati')


DIMS = {}
if __name__ == '__main__':
    import sys
    only = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if only in ('all', 'cat'):
        cells, _ = process('cat', (1, 1, 1), 45, (0, 280, 1408, 704), 2, 240, 'gatto', dist2=30)
        if len(cells) == 2:
            DIMS['gatto'] = pack(cells, 240, 'gatto')

    if only in ('all', 'lui'):
        cells, _ = process('lui_emo', (25, 29, 36), 92, (0, 30, 1408, 698), 5, 262, 'astro2',
                           dist2=34, dark_neutral=(150, 18))
        if len(cells) == 5:
            DIMS['astro2'] = pack(cells, 262, 'astro2')

    if only in ('all', 'ballo'):
        cells, _ = process('ballo', (26, 29, 35), 92, (0, 30, 1408, 698), 5, 312, 'coppia',
                           dist2=34, dark_neutral=(150, 18))
        if len(cells) == 5:
            DIMS['coppia'] = pack(cells, 312, 'coppia')

    if only in ('all', 'lei'):
        # lei: fondo bianco, 4 pose (avanti A=fronte, avanti B=lato, dietro A, dietro B)
        cells, _ = process('lei_walk', (254, 254, 254), 42, (0, 95, 1408, 702), 4, 242, 'astro', dist2=24)
        if len(cells) == 4:
            front, side, back, back2 = cells
            DIMS['astro_down'] = pack([front], 242, 'astro_down')
            DIMS['astro_up'] = pack([back], 242, 'astro_up')
            DIMS['astro_right'] = pack([side], 242, 'astro_right')       # profilo verso destra
            DIMS['astro_left'] = pack([side.transpose(Image.FLIP_LEFT_RIGHT)], 242, 'astro_left')

    if only in ('all', 'extra'):
        derivati()

    if only == 'all':
        # sincronizza fw/fh/n dentro sprites.json (preservando alt/asset): mai più
        # dimensioni sfasate rispetto ai PNG effettivi (QA: check dimensioni fogli).
        import json
        spath = os.path.join(ROOT, 'packs', 'ultima-orbita', 'config', 'sprites.json')
        sp = json.load(open(spath, encoding='utf-8'))
        keymap = {'astroDown': 'astro_down', 'astroUp': 'astro_up', 'astroLeft': 'astro_left',
                  'astroRight': 'astro_right', 'astro2': 'astro2', 'coppia': 'coppia', 'gatto': 'gatto'}
        for sk, dk in keymap.items():
            if sk in sp['sheets'] and dk in DIMS:
                for f in ('fw', 'fh', 'n'):
                    sp['sheets'][sk][f] = DIMS[dk][f]
        open(spath, 'w', encoding='utf-8').write(json.dumps(sp, ensure_ascii=False, indent=2) + '\n')
        print('sprites.json: dimensioni fogli sincronizzate')

    print('\nDIMS =', DIMS)
