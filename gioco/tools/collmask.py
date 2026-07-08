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


def derive(mask_path, wall_top=0.0):
    """Ritorna dict: {walk:{w,h,data}, grid(GRID×GRID bool), bounds, gatto, calpestabile_pct}.

    `wall_top`: frazione superiore dell'immagine forzata NON calpestabile (rete di
    sicurezza: in vista 3/4 dall'alto quella fascia è sempre muro/soffitto; evita
    che i personaggi camminino sulla parete anche se la maschera l'ha sbagliata)."""
    walk, H = _walkable(mask_path)
    if wall_top > 0:
        walk[:int(H * wall_top)] = False
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
    small = np.array(Image.fromarray((walk * 255).astype(np.uint8))
                     .resize((GRID, GRID), Image.NEAREST)) > 128
    packed = np.packbits(small.flatten(), bitorder='little')
    data = base64.b64encode(packed.tobytes()).decode()
    return {
        'walk': {'w': GRID, 'h': GRID, 'data': data},
        'grid': small, 'bounds': bounds, 'gatto': gatto,
        'calpestabile_pct': round(100 * float(walk.mean()), 1),
    }


def _cells(grid):
    ys, xs = np.where(grid)
    return xs, ys


def spread(grid, k):
    """k punti calpestabili ben distanziati (farthest-point sampling), in % 0-100.
    Serve a piazzare oggetti/personaggi lontani tra loro e tutti raggiungibili."""
    G = grid.shape[0]
    xs, ys = _cells(grid)
    if len(xs) == 0:
        return []
    # parti dal centro dell'area libera (max distanza dai bordi)
    dist = ndimage.distance_transform_edt(grid)
    cy, cx = np.unravel_index(int(np.argmax(dist)), dist.shape)
    chosen = [(cx, cy)]
    pool = np.stack([xs, ys], 1).astype(np.float32)
    while len(chosen) < k and len(pool):
        ch = np.array(chosen, np.float32)
        d = np.min(((pool[:, None, :] - ch[None, :, :]) ** 2).sum(2), 1)
        i = int(np.argmax(d))
        chosen.append((int(pool[i, 0]), int(pool[i, 1])))
    return [[round(c[0] / G * 100, 1), round(c[1] / G * 100, 1)] for c in chosen]


def entrance(grid):
    """Punto d'ingresso del protagonista: cella calpestabile nella fascia bassa
    (vicino alla camera) più centrata orizzontalmente. In % 0-100."""
    G = grid.shape[0]
    xs, ys = _cells(grid)
    if len(xs) == 0:
        return [50.0, 50.0]
    ymax = ys.max()
    band = ys >= ymax - max(2, int(G * 0.12))     # ultimo ~12% calpestabile
    bx, by = xs[band], ys[band]
    j = int(np.argmin(np.abs(bx - G / 2)))         # il più centrale in x
    return [round(float(bx[j]) / G * 100, 1), round(float(by[j]) / G * 100, 1)]


def reachable(grid, start, targets):
    """BFS: dallo start (x%,y%) quali target (lista di [x%,y%]) sono raggiungibili."""
    G = grid.shape[0]
    def cell(p): return (min(G - 1, int(p[0] / 100 * G)), min(G - 1, int(p[1] / 100 * G)))
    from collections import deque
    seen = np.zeros_like(grid, bool)
    sx, sy = cell(start)
    if not grid[sy, sx]:
        # aggancia alla cella calpestabile più vicina
        xs, ys = _cells(grid)
        j = int(np.argmin((xs - sx) ** 2 + (ys - sy) ** 2)); sx, sy = xs[j], ys[j]
    q = deque([(sx, sy)]); seen[sy, sx] = True
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < G and 0 <= ny < G and grid[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((nx, ny))
    out = []
    for t in targets:
        tx, ty = cell(t)
        # raggiungibile se una cella calpestabile vista è entro ~2 celle dal target
        r = 2
        block = seen[max(0, ty - r):ty + r + 1, max(0, tx - r):tx + r + 1]
        out.append(bool(block.any()))
    return out


if __name__ == '__main__':
    import sys, json
    print(json.dumps(derive(sys.argv[1]), ensure_ascii=False, indent=2)[:400])
