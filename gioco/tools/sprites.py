# Pipeline scontorno sprite v3 — "solo nero puro collegato al bordo"
#  · alpha=0 SOLO per i pixel quasi-neri (somma RGB<=10) raggiungibili dal bordo
#  · le ombre nere RACCHIUSE (varchi tra i ricci) restano opache -> chioma piena
#  · il bordo scuro di transizione resta opaco -> outline pixel-art, zero buchi
#  · color-bleed nei pixel trasparenti per evitare frange al ridimensionamento
#  · pack: celle a larghezza garantita (nessun frame tocca il bordo cella),
#    allineamento al centro-piedi, altezza uniforme per sheet
from PIL import Image
import numpy as np
from scipy import ndimage

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = os.path.join(ROOT, 'assets', '_src') + os.sep
OUT = os.path.join(ROOT, 'assets', 'sprites')
THR = 10          # somma RGB massima per "nero di sfondo" (chroma nero, legacy)
GREEN_MIN = 90    # G minimo per considerare un pixel "verde chroma"
GREEN_DOM = 40    # di quanto G deve superare R e B
BLEED_IT = 10     # iterazioni di color-bleed

def _chroma_mask(a):
    """Maschera dei pixel di SFONDO + tipo di chroma rilevato dai bordi.
    Auto-detect: se il bordo è verde acceso → chroma key VERDE (consigliato:
    ritaglio pulito anche con capelli/vestiti scuri, che col nero erano il
    punto critico); altrimenti → NERO puro (sorgenti legacy). Ritorna anche una
    versione 'larga' della maschera per i seed di regioni intrappolate."""
    r, g, bl = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    green = (g >= GREEN_MIN) & (g - r >= GREEN_DOM) & (g - bl >= GREEN_DOM)
    bordo = np.concatenate([green[0, :], green[-1, :], green[:, 0], green[:, -1]])
    if bordo.mean() > 0.5:                       # bordo prevalentemente verde
        largo = (g >= 60) & (g - r >= 20) & (g - bl >= 20)   # verde anche sfumato
        return green, largo, 'verde'
    s = a.sum(axis=2)
    return s <= THR, s <= 30, 'nero'

def load_rgba_keyed(path, seeds=()):
    """alpha=0 per lo sfondo chroma (verde acceso o nero puro) collegato al bordo.
    `seeds`: punti (x,y) dentro regioni di sfondo INTRAPPOLATO (es. tra i due
    corpi nel ballo) da rimuovere esplicitamente — tutto il resto (ombre della
    chioma, occhi, pieghe) resta opaco."""
    im = Image.open(path).convert('RGB')
    a = np.array(im).astype(np.int32)
    key, key_largo, modo = _chroma_mask(a)
    lbl, nlab = ndimage.label(key)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    bg = np.isin(lbl, list(border))
    if seeds:
        # maschera 'larga' per non far scappare il flood lungo pieghe/cinture
        enc = key_largo & ~bg
        l2, _ = ndimage.label(enc)
        for (sx, sy) in seeds:
            lab = l2[sy, sx]
            if lab: bg |= (l2 == lab)
            else: print(f'  [seed ({sx},{sy}) fuori da una regione di sfondo: ignorato]')
    rgba = np.dstack([a.astype(np.uint8), np.where(bg, 0, 255).astype(np.uint8)])
    if modo == 'verde':
        # spill suppression: sui pixel OPACHI con alone verdastro, riporta il
        # verde al massimo tra R e B → via le frange verdi ai bordi del soggetto
        op = rgba[:, :, 3] > 0
        r0, g0, b0 = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2]
        spill = op & (g0 > r0) & (g0 > b0)
        g0[spill] = np.maximum(r0[spill], b0[spill])
    # color-bleed: copia i colori dei vicini opachi dentro i pixel trasparenti
    rgb = rgba[:, :, :3].astype(np.float32)
    alpha = rgba[:, :, 3] > 0
    known = alpha.copy()
    for _ in range(BLEED_IT):
        grown = ndimage.binary_dilation(known)
        ring = grown & ~known
        if not ring.any(): break
        acc = np.zeros_like(rgb); cnt = np.zeros(rgb.shape[:2], np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0: continue
                sh = np.roll(np.roll(rgb, dy, 0), dx, 1)
                shk = np.roll(np.roll(known, dy, 0), dx, 1)
                m = ring & shk
                acc[m] += sh[m]; cnt[m] += 1
        m = ring & (cnt > 0)
        rgb[m] = acc[m] / cnt[m][:, None]
        known |= m
    rgba[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return rgba

def cells_grid(rgba):
    """Trova le celle (bande di righe -> segmenti di colonne) dai pixel opachi."""
    op = rgba[:, :, 3] > 0
    rows = np.where(op.any(axis=1))[0]
    bands = []
    start = rows[0]
    for i in range(1, len(rows)):
        if rows[i] - rows[i-1] > 8:          # gap verticale => nuova banda
            bands.append((start, rows[i-1])); start = rows[i]
    bands.append((start, rows[-1]))
    cells = []
    for (y0, y1) in bands:
        seg = op[y0:y1+1]
        cols = np.where(seg.any(axis=0))[0]
        s = cols[0]
        for i in range(1, len(cols)):
            if cols[i] - cols[i-1] > 8:      # gap orizzontale => nuova cella
                cells.append((s, cols[i-1], y0, y1)); s = cols[i]
        cells.append((s, cols[-1], y0, y1))
    out = []
    for (x0, x1, y0, y1) in cells:
        sub = op[y0:y1+1, x0:x1+1]
        ys, xs = np.where(sub)
        out.append(Image.fromarray(rgba[y0+ys.min():y0+ys.max()+1, x0+xs.min():x0+xs.max()+1]))
    return out

def footcx(im):
    """Centro orizzontale dei piedi (ultime 12 righe opache)."""
    a = np.array(im)[:, :, 3]
    ys = np.where(a.any(axis=1))[0]
    band = a[max(0, ys[-1]-12):ys[-1]+1]
    xs = np.where(band.any(axis=0))[0]
    return (xs.min() + xs.max()) / 2

def pack(cells, fh, name):
    """Impacchetta le celle a altezza uniforme fh, piedi in basso, centro-piedi al centro cella."""
    hmax = max(c.size[1] for c in cells)
    sc = (fh - 4) / hmax
    scaled = []
    for c in cells:
        w, h = c.size
        s = c.resize((max(1, round(w*sc)), max(1, round(h*sc))), Image.LANCZOS)
        scaled.append((s, footcx(s)))
    half = max(max(f, s.size[0]-f) for s, f in scaled)
    fw = int(np.ceil(half))*2 + 6
    sheet = Image.new('RGBA', (fw*len(scaled), fh), (0, 0, 0, 0))
    for i, (s, f) in enumerate(scaled):
        x = i*fw + round(fw/2 - f)
        x = max(i*fw, min(x, (i+1)*fw - s.size[0]))          # mai oltre la cella
        y = fh - 2 - s.size[1]
        sheet.paste(s, (x, y), s)
    # verifica: nessuna cella tocca il bordo cella
    arr = np.array(sheet)[:, :, 3]
    bad = 0
    for i in range(len(scaled)):
        cell = arr[:, i*fw:(i+1)*fw]
        if cell[:, 0].any() or cell[:, -1].any() or cell[0, :].any(): bad += 1
    q = sheet.quantize(256, method=Image.FASTOCTREE).convert('RGBA')
    Image.fromarray(np.array(q)).save(f'{OUT}/{name}.png')
    import os
    print(f'{name}: n={len(scaled)} fw={fw} fh={fh} {os.path.getsize(f"{OUT}/{name}.png")//1024}KB  celle-che-toccano-il-bordo={bad}')
    return fw

# ---- LEI: 4 righe x 4 colonne ----
rgba = load_rgba_keyed(U+'protagonista_sheet.png')
cells = cells_grid(rgba)
assert len(cells) == 16, f'attese 16 celle lei, trovate {len(cells)}'
dims = {}
for row, nome in enumerate(['protagonista_down', 'protagonista_right', 'protagonista_up', 'protagonista_left']):
    dims[nome] = pack(cells[row*4:(row+1)*4], 242, nome)

# ---- LUI: 5 frame emotivi ----
rgba = load_rgba_keyed(U+'secondario_sheet.png')
cells = cells_grid(rgba)
assert len(cells) == 5, f'attese 5 celle lui, trovate {len(cells)}'
dims['secondario_emo'] = pack(cells, 262, 'secondario_emo')

# ---- BALLO: 5 frame di coppia ----
# semi = sfondo intrappolato fra i due corpi (misurato sul foglio sorgente 1536x1024)
BALLO_SEEDS = [(160,360),(160,470),(160,630),   # frame 1: colonna fra i corpi
               (760,370),(760,600),             # frame 3: colonna fra i corpi
               (1300,700)]                      # frame 5: varco fra le gambe
rgba = load_rgba_keyed(U+'ballo_sheet.png', seeds=BALLO_SEEDS)
cells = cells_grid(rgba)
assert len(cells) == 5, f'attese 5 celle ballo, trovate {len(cells)}'
dims['ballo5'] = pack(cells, 312, 'ballo5')

print('DIMS =', dims)

# ---- RITRATTI di lui (dal foglio appena impacchettato) ----
sheet = Image.open(f'{OUT}/secondario_emo.png').convert('RGBA')
FW, FH, N = dims['secondario_emo'], 262, 5
for i in range(N):
    fr = sheet.crop((i*FW, 0, (i+1)*FW, FH))
    al = np.array(fr)[:, :, 3]
    ys, xs = np.where(al > 10)
    top = ys.min()
    side = min(FW, FH - top)
    head = al[top:top + side//2]
    hx = np.where(head.any(axis=0))[0]
    cx = (hx.min() + hx.max()) // 2
    x0 = max(0, min(FW - side, cx - side//2))
    fr.crop((x0, top, x0 + side, top + side)).resize((128, 128), Image.LANCZOS)\
      .save(f'{OUT}/pt_secondario_{i}.png')
print('ritratti pt_secondario_0..4 rigenerati')
