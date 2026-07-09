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
    # centro-cella: garantisce il round-trip col motore (floor(%/100*G) == indice)
    return [[round((c[0] + 0.5) / G * 100, 1), round((c[1] + 0.5) / G * 100, 1)] for c in chosen]


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
    return [round((float(bx[j]) + 0.5) / G * 100, 1), round((float(by[j]) + 0.5) / G * 100, 1)]


def flood(grid, start):
    """Griglia booleana delle celle calpestabili RAGGIUNGIBILI (4-vicini) dallo
    start (x%,y%). Serve a piazzare personaggi e indizi solo dove il protagonista
    arriva davvero, ignorando sacche di pavimento isolate."""
    from collections import deque
    G = grid.shape[0]
    seen = np.zeros_like(grid, bool)
    sx = min(G - 1, int(start[0] / 100 * G)); sy = min(G - 1, int(start[1] / 100 * G))
    if not grid[sy, sx]:
        xs, ys = _cells(grid)
        if len(xs) == 0:
            return seen
        j = int(np.argmin((xs - sx) ** 2 + (ys - sy) ** 2)); sx, sy = int(xs[j]), int(ys[j])
    q = deque([(sx, sy)]); seen[sy, sx] = True
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < G and 0 <= ny < G and grid[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((nx, ny))
    return seen


def floor_body(grid, min_clear=2.0):
    """Maschera del CORPO navigabile principale: pavimento eroso del raggio del
    personaggio, componente connessa più grande. Le celle qui sono davvero
    raggiungibili dal motore (niente bordi sottili o angoli marginali)."""
    dist = ndimage.distance_transform_edt(grid)
    body = dist >= min_clear
    if not body.any():
        return grid
    lbl, n = ndimage.label(body)
    if n > 1:
        sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
        body = (lbl == int(np.argmax(sz)) + 1)
    return body


def nearest(grid, p):
    """Cella calpestabile più vicina al punto p (x%,y%), in % 0-100."""
    G = grid.shape[0]
    xs, ys = _cells(grid)
    if len(xs) == 0:
        return p
    px, py = p[0] / 100 * G, p[1] / 100 * G
    j = int(np.argmin((xs - px) ** 2 + (ys - py) ** 2))
    return [round((float(xs[j]) + 0.5) / G * 100, 1), round((float(ys[j]) + 0.5) / G * 100, 1)]


def spread_open(grid, k, min_clear=2.0):
    """Come spread(), ma sceglie SOLO celle nel CORPO navigabile principale: il
    pavimento eroso del raggio del personaggio, tenendo la componente connessa più
    grande. Così personaggi e indizi non finiscono su colli sottili o sacche
    isolate (che il pathfinding del motore, senza tagli sugli spigoli, non
    attraversa) e il protagonista può sempre avvicinarsi e interagire."""
    G = grid.shape[0]
    dist = ndimage.distance_transform_edt(grid)
    open_cells = dist >= min_clear
    if open_cells.any():                        # tieni solo il corpo aperto più grande
        lbl, nl = ndimage.label(open_cells)
        if nl > 1:
            sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, nl + 1))
            open_cells = (lbl == int(np.argmax(sz)) + 1)
    else:
        open_cells = grid                       # stanza strettissima: ripiega su tutto
    ys, xs = np.where(open_cells)
    cy, cx = np.unravel_index(int(np.argmax(dist)), dist.shape)
    chosen = [(cx, cy)]
    pool = np.stack([xs, ys], 1).astype(np.float32)
    while len(chosen) < k and len(pool):
        ch = np.array(chosen, np.float32)
        d = np.min(((pool[:, None, :] - ch[None, :, :]) ** 2).sum(2), 1)
        chosen.append((int(pool[int(np.argmax(d)), 0]), int(pool[int(np.argmax(d)), 1])))
    return [[round((c[0] + 0.5) / G * 100, 1), round((c[1] + 0.5) / G * 100, 1)] for c in chosen]


def engine_reachable(grid, bounds, start, targets, obstacle=None, GN=200, GSTEP=0.5):
    """Replica il pathfinding del MOTORE (griglia 200, 8-vicini SENZA tagli sugli
    spigoli, limiti stanza + WALK, più l'ingombro ellittico del secondario se dato
    in `obstacle`) e ritorna, per ogni target, se il protagonista ci arriva
    davvero. Serve a piazzare personaggi/indizi solo dove sono interagibili nel
    gioco — anche quando il corpo del secondario tapperebbe il proprio corridoio."""
    from collections import deque
    W = grid.shape[0]
    ii = np.arange(GN) * GSTEP
    gidx = np.clip((ii / 100 * W).astype(int), 0, W - 1)
    free = grid[np.ix_(gidx, gidx)]                 # free[j,i] = WALK a (i*GSTEP, j*GSTEP)
    inbx = (ii >= bounds['xMin']) & (ii <= bounds['xMax'])
    inby = (ii >= bounds['yMin']) & (ii <= bounds['yMax'])
    free = free & inby[:, None] & inbx[None, :]
    if obstacle is not None:                        # ingombro morbido del secondario (come il motore)
        ox, oy = obstacle
        px = ii[None, :]; py = ii[:, None]
        free = free & ~(np.hypot((px - ox) * 0.5, py - oy) < 1.7)

    def nearest_free(p):
        ci = max(0, min(GN - 1, round(p[0] / GSTEP))); cj = max(0, min(GN - 1, round(p[1] / GSTEP)))
        if free[cj, ci]:
            return (ci, cj)
        for r in range(1, 45):
            for a in range(16):
                i = round(ci + np.cos(a / 16 * 2 * np.pi) * r); j = round(cj + np.sin(a / 16 * 2 * np.pi) * r)
                if 0 <= i < GN and 0 <= j < GN and free[j, i]:
                    return (i, j)
        return None

    s = nearest_free(start)
    seen = np.zeros((GN, GN), bool)
    if s:
        seen[s[1], s[0]] = True
        q = deque([s])
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        while q:
            i, j = q.popleft()
            for di, dj in dirs:
                I, J = i + di, j + dj
                if not (0 <= I < GN and 0 <= J < GN) or seen[J, I] or not free[J, I]:
                    continue
                if di and dj and (not free[j, I] or not free[J, i]):
                    continue                        # niente tagli sugli spigoli
                seen[J, I] = True; q.append((I, J))
    out = []
    for t in targets:
        c = nearest_free(t)
        out.append(bool(c and seen[c[1], c[0]]))
    return out


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
