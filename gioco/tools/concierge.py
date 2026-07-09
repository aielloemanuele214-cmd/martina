#!/usr/bin/env python3
"""Agente Concierge (FIG-01) — dall'intervista del cliente al brief genera.json.

Legge l'intervista in `packs/<slug>/intervista.json` (campi dell'intervista, anche
liberi) oppure `packs/<slug>/intervista.txt` (racconto libero), traduce i ricordi
in requisiti di produzione con la DIRETTIVA editabile
(`tools/agenti/concierge-agente.md`) e scrive un `genera.json` valido — pronto per
`sad genera <slug>`.

Non scrive mai un brief incompleto: valida l'output (3 oggetti, campi presenti) e,
se il modello non lo produce, ritenta; se resta invalido, NON scrive e segnala.

  python3 tools/sad.py concierge <slug>
"""
import json, os, ssl, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
ENV = os.path.expanduser('~/.config/sempreaddue/gemini.env')
SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agenti', 'concierge-agente.md')
DEFAULT_MODEL = 'gemini-2.5-flash'
COST = 0.004
TRANSIENT = {429, 500, 502, 503, 504}

# Rete di sicurezza se la spec manca (il vero cervello è in concierge-agente.md).
_DIRETTIVA = ("Sei il Concierge di SempreAddue: trasforma i ricordi di una coppia in un "
    "brief di produzione per un'avventura in pixel art 16-bit. Descrizioni visive in "
    "inglese, nomi reali; 3 oggetti-indizio legati a ricordi veri; inventa dettagli "
    "teneri e coerenti se mancano.")
_CRITERIO = "Produci protagonista, secondario, animale(opz), stanza, 3 oggetti, animati."

SCHEMA = {
    'type': 'object',
    'properties': {
        'protagonista': {'type': 'string'},
        'secondario': {'type': 'string'},
        'animale': {'type': 'string'},
        'stanza': {'type': 'string'},
        'oggetti': {'type': 'array', 'items': {'type': 'string'}},
        'animati': {'type': 'string'},
    },
    'required': ['protagonista', 'secondario', 'stanza', 'oggetti', 'animati'],
}


def _key():
    if os.environ.get('GEMINI_API_KEY'):
        return os.environ['GEMINI_API_KEY']
    if os.path.exists(ENV):
        for ln in open(ENV):
            if 'GEMINI_API_KEY' in ln and '=' in ln:
                return ln.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('GEMINI_API_KEY non impostata (vedi ~/.config/sempreaddue/gemini.env)')


def _load_agent():
    prof = {'modello': DEFAULT_MODEL, 'direttiva': _DIRETTIVA, 'criterio': _CRITERIO}
    try:
        cur, buf, sez = None, [], {}
        for line in open(SPEC, encoding='utf-8'):
            if line.startswith('## '):
                if cur:
                    sez[cur] = '\n'.join(buf).strip()
                cur, buf = line[3:].strip(), []
            elif cur:
                buf.append(line.rstrip('\n'))
        if cur:
            sez[cur] = '\n'.join(buf).strip()
        if sez.get('MODELLO'):
            prof['modello'] = sez['MODELLO'].splitlines()[0].strip()
        if sez.get('DIRETTIVA'):
            prof['direttiva'] = sez['DIRETTIVA']
        if sez.get('CRITERIO brief'):
            prof['criterio'] = sez['CRITERIO brief']
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'⚠ Concierge: spec agente non caricata ({e}); uso i valori interni')
    return prof


AGENTE = _load_agent()


def _log(model):
    try:
        os.makedirs(os.path.dirname(USAGE), exist_ok=True)
        if not os.path.exists(USAGE):
            open(USAGE, 'w').write('quando\tmodello\timmagini\tcosto_stima_eur\n')
        ts = os.environ.get('SAD_TS', 'concierge')
        open(USAGE, 'a').write(f'{ts}\t{model} (concierge)\t0\t{COST:.3f}\n')
    except Exception:
        pass


def _intervista(pack_dir):
    """Legge l'intervista: intervista.json (dict) o intervista.txt (racconto libero)."""
    j = os.path.join(pack_dir, 'intervista.json')
    t = os.path.join(pack_dir, 'intervista.txt')
    if os.path.exists(j):
        return json.dumps(json.load(open(j, encoding='utf-8')), ensure_ascii=False, indent=2)
    if os.path.exists(t):
        return open(t, encoding='utf-8').read()
    sys.exit(f'intervista mancante: crea {j} oppure {t}')


def _valido(b):
    if not isinstance(b, dict):
        return False
    for c in ('protagonista', 'secondario', 'stanza', 'animati'):
        if not isinstance(b.get(c), str) or not b[c].strip():
            return False
    ogg = b.get('oggetti')
    return isinstance(ogg, list) and len([o for o in ogg if isinstance(o, str) and o.strip()]) >= 3


def _call(model, key, prompt):
    body = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'responseMimeType': 'application/json',
                             'responseSchema': SCHEMA, 'temperature': 0.4},
    }).encode()
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=body, headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
    err = None
    for att in range(4):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                d = json.load(r)
            out = json.loads(d['candidates'][0]['content']['parts'][0]['text'])
            _log(model)
            return out, None
        except urllib.error.HTTPError as e:
            err = f'HTTP {e.code}'
            if e.code in TRANSIENT and att < 3:
                time.sleep(2 ** att); continue
            break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = str(e)
            if att < 3:
                time.sleep(2 ** att); continue
            break
        except Exception as e:
            err = str(e); break
    return None, err


def compila(slug):
    key = _key()
    pack_dir = os.path.join(ROOT, 'packs', slug)
    assert os.path.isdir(pack_dir), f'pack inesistente: packs/{slug} (crea prima il pack)'
    intervista = _intervista(pack_dir)
    prompt = (f"{AGENTE['direttiva']}\n\n{AGENTE['criterio']}\n\n"
              f"=== INTERVISTA DEL CLIENTE ===\n{intervista}\n\n"
              "Restituisci SOLO il brief come JSON con i campi richiesti.")
    dest = os.path.join(pack_dir, 'genera.json')
    for tent in range(1, 4):
        brief, err = _call(AGENTE['modello'], key, prompt)
        if brief is None:
            print(f'⚠ Concierge: giudizio non disponibile ({err}) — brief NON scritto, riprova più tardi')
            return 2
        if _valido(brief):
            brief['oggetti'] = [o for o in brief['oggetti'] if isinstance(o, str) and o.strip()][:3]
            json.dump(brief, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            print(f'✅ brief pronto: packs/{slug}/genera.json  (agente Concierge, tentativo {tent})')
            for k in ('protagonista', 'secondario', 'animale', 'stanza'):
                v = brief.get(k, '') or '—'
                print(f'   {k:12} {v[:88]}')
            print(f'   oggetti      {" · ".join(brief["oggetti"])[:100]}')
            print(f'   animati      {brief.get("animati","")[:88]}')
            print(f'\n   → genera gli asset con:  python3 tools/sad.py genera {slug}')
            return 0
        prompt += "\n\nATTENZIONE: l'output precedente era incompleto (servono 3 oggetti e tutti i campi). Riprova completo."
    print('⚠ Concierge: brief incompleto dopo 3 tentativi — NON scritto. Rivedi l\'intervista.')
    return 1


if __name__ == '__main__':
    sys.exit(compila(sys.argv[1]))
