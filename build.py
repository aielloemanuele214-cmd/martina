#!/usr/bin/env python3
"""Builder Sempreaddue: genera la copia personalizzata per un cliente.

Uso:
    python3 build.py clienti/esempio.json

Prende stanza.html (il modello base), sostituisce il blocco CONFIG con i
dati del cliente e scrive dist/stanza-<slug>.html pronto da consegnare
(trascinalo su https://app.netlify.com/drop e genera il QR del link).

Nel JSON del cliente:
  - "_slug" (obbligatorio): nome del file di output, es. "anna-marco"
  - ogni valore stringa che inizia con "file:" viene sostituito con il
    contenuto del file (percorso relativo al JSON) codificato in base64 —
    utile per le foto delle sorprese, es. "foto": "file:foto/lettera.jpg"
  - tutti gli altri campi rispecchiano il blocco CONFIG di stanza.html
"""
import json, base64, re, sys, os, mimetypes

if len(sys.argv) != 2:
    sys.exit(__doc__)

src = open('stanza.html', encoding='utf-8').read()
cfg = json.load(open(sys.argv[1], encoding='utf-8'))
slug = cfg.pop('_slug', None) or sys.exit("il JSON deve avere '_slug'")
basedir = os.path.dirname(os.path.abspath(sys.argv[1]))

def inline(v):
    """Sostituisce 'file:percorso' con il data-URI base64 del file."""
    if isinstance(v, dict):  return {k: inline(x) for k, x in v.items()}
    if isinstance(v, list):  return [inline(x) for x in v]
    if isinstance(v, str) and v.startswith('file:'):
        p = os.path.join(basedir, v[5:])
        mime = mimetypes.guess_type(p)[0] or 'image/jpeg'
        return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    return v

cfg = inline(cfg)
blocco = ('/* ★★ INIZIO CONFIG ★★ */\nconst CONFIG = '
          + json.dumps(cfg, ensure_ascii=False, indent=2)
          + ';\n/* ★★ FINE CONFIG ★★ — non modificare sotto questa riga */')
out = re.sub(r'/\* ★★ INIZIO CONFIG ★★ \*/.*?/\* ★★ FINE CONFIG ★★[^\n]*\*/',
             lambda _: blocco, src, count=1, flags=re.S)
assert out != src, 'blocco CONFIG non trovato in stanza.html'

os.makedirs('dist', exist_ok=True)
dest = f'dist/stanza-{slug}.html'
open(dest, 'w', encoding='utf-8').write(out)
print(f'creato {dest} ({os.path.getsize(dest)//1024} KB)')
