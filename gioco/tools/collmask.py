"""Derivazione collisioni dalla MASCHERA di collisione della stanza.

Dato un PNG maschera "flat stencil" (bianco = pavimento calpestabile — tappeti
e piccoli oggetti a terra inclusi; nero = muri/mobili volumetrici/fuori stanza),
ricava:
  - una griglia di calpestabilità 1-bit (per ROOM.walk, letta dal motore),
  - i bounds in % (0-100),
  - una posizione credibile per il gatto (centro dell'area libera più ampia).

Il motore usa la griglia direttamente (collisioni pixel-accurate coerenti con
l'arte generata), senza poligoni disegnati a mano.
"""
import base64
import numpy as np
from PIL import Image
from scipy import ndimage

GRID = 128          # risoluzione della griglia salvata nel pack
ERODE = 0.008       # erosione (~mezzo corpo) per non clippare i bordi
HOLE = 0.06         # buchi neri < 6% area = oggetti a terra → calpestabili


def _walkable(mask_path):
    m = np.array(Image.open(mask_path).convert('L'))
    H = m.shape[0]
    white = m > 140
    white = ndimage.binary_closing(white, iterations=2)
    # buchi piccoli dentro il pavimento (scarpe, cesti, tappeti scuri) = calpestabili
    holes = ndimage.binary_fill_holes(white) & ~white
    hl, hn = ndimage.label(holes)
    if hn:
        sz = ndimage.sum(np.ones_like(hl), hl, range(1, hn + 1))
        thr = white.size * HOLE
        for i, s in enumerate(sz, 1):
            if s < thr:
                white[hl == i] = True
    # tieni la componente calpestabile principale (il pavimento)
    lbl, n = ndimage.label(white)
    if n:
        sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
        white = (lbl == int(np.argmax(sz)) + 1)
    walk = ndimage.binary_erosion(white, iterations=max(1, int(H * ERODE)))
    return walk, H


def derive(mask_path):
    """Ritorna dict: {walk:{w,h,data}, bounds:{...}, gatto:[x,y], calpestabile_pct}."""
    walk, H = _walkable(mask_path)
    ys, xs = np.where(walk)
    if len(xs) == 0:
        raise SystemExit('maschera senza area calpestabile: controlla la maschera')
    bounds = {
        'xMin': round(float(xs.min()) / H * 100, 1), 'xMax': round(float(xs.max()) / H * 100, 1),
        'yMin': round(float(ys.min()) / H * 100, 1), 'yMax': round(float(ys.max()) / H * 100, 1),
    }
    dist = ndimage.distance_transform_edt(walk)
    cy, cx = np.unravel_index(int(np.argmax(dist)), dist.shape)
    gatto = [round(float(cx) / H * 100, 1), round(float(cy) / H * 100, 1)]
    # griglia GRID×GRID, bit-pack LSB-first (combacia col decode del motore)
    small = np.array(Image.fromarray((walk * 255).astype(np.uint8))
                     .resize((GRID, GRID), Image.NEAREST)) > 128
    packed = np.packbits(small.flatten(), bitorder='little')
    data = base64.b64encode(packed.tobytes()).decode()
    return {
        'walk': {'w': GRID, 'h': GRID, 'data': data},
        'bounds': bounds, 'gatto': gatto,
        'calpestabile_pct': round(100 * float(walk.mean()), 1),
    }


def spawn_point(info):
    """Un punto di spawn sicuro: il centro dell'area libera più ampia (come il gatto)."""
    return list(info['gatto'])


if __name__ == '__main__':
    import sys, json
    print(json.dumps(derive(sys.argv[1]), ensure_ascii=False, indent=2)[:400])
