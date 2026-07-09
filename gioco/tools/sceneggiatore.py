#!/usr/bin/env python3
"""Agente Sceneggiatore (FIG-02) — dai ricordi del cliente al copione del gioco.

Legge l'intervista (`packs/<slug>/intervista.json|txt`) e, se c'è, il brief
`genera.json` (per allineare gli indizi ai 3 oggetti scelti). Con la DIRETTIVA
editabile (`tools/agenti/sceneggiatore-agente.md`) scrive i TESTI personalizzati
e li incastra nei file del pack:
  - dialogues.json  → battute del partner (+ messaggio del gatto)
  - interactions.json → titolo/testo dei 3 indizi (+ testo finestra)
  - endings.json    → finale
La LOGICA (story.json) non si tocca: cambiano solo i testi.

Non scrive mai un copione incompleto: valida (3 indizi, finale, battute) e in caso
ritenta; se resta invalido NON scrive e segnala.

  python3 tools/sad.py sceneggiatore <slug>
"""
import json, os, ssl, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
ENV = os.path.expanduser('~/.config/sempreaddue/gemini.env')
SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agenti', 'sceneggiatore-agente.md')
DEFAULT_MODEL = 'gemini-2.5-flash'
COST = 0.004
TRANSIENT = {429, 500, 502, 503, 504}

_DIRETTIVA = ("Sei lo Sceneggiatore di SempreAddue: scrivi i testi brevi e sinceri di "
    "un'avventura romantica personalizzata, in italiano, nel tono richiesto, usando i "
    "ricordi veri della coppia. Le battute le dice il partner al protagonista.")
_CRITERIO = ("Produci dialoghi (10–14 battute brevi), indizi (3, nell'ordine degli oggetti, "
    "con titolo e testo), gatto (messaggio se c'è animale), finestra, finale (titolo+testo).")

_IND = {'type': 'object', 'properties': {'titolo': {'type': 'string'}, 'testo': {'type': 'string'}},
        'required': ['titolo', 'testo']}
SCHEMA = {
    'type': 'object',
    'properties': {
        'dialoghi': {'type': 'array', 'items': {'type': 'string'}},
        'indizi': {'type': 'array', 'items': _IND},
        'gatto': {'type': 'string'},
        'finestra': {'type': 'string'},
        'finale': {'type': 'object',
                   'properties': {'titolo': {'type': 'string'}, 'testo': {'type': 'string'}},
                   'required': ['testo']},
    },
    'required': ['dialoghi', 'indizi', 'finestra', 'finale'],
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
        if sez.get('CRITERIO copione'):
            prof['criterio'] = sez['CRITERIO copione']
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'⚠ Sceneggiatore: spec agente non caricata ({e}); uso i valori interni')
    return prof


AGENTE = _load_agent()


def _log(model):
    try:
        os.makedirs(os.path.dirname(USAGE), exist_ok=True)
        if not os.path.exists(USAGE):
            open(USAGE, 'w').write('quando\tmodello\timmagini\tcosto_stima_eur\n')
        ts = os.environ.get('SAD_TS', 'sceneggiatore')
        open(USAGE, 'a').write(f'{ts}\t{model} (sceneggiatore)\t0\t{COST:.3f}\n')
    except Exception:
        pass


def _intervista(pack_dir):
    j = os.path.join(pack_dir, 'intervista.json')
    t = os.path.join(pack_dir, 'intervista.txt')
    if os.path.exists(j):
        return json.dumps(json.load(open(j, encoding='utf-8')), ensure_ascii=False, indent=2)
    if os.path.exists(t):
        return open(t, encoding='utf-8').read()
    sys.exit(f'intervista mancante: crea {j} oppure {t}')


def _oggetti(pack_dir):
    g = os.path.join(pack_dir, 'genera.json')
    if os.path.exists(g):
        return json.load(open(g, encoding='utf-8')).get('oggetti', [])
    return []


def _valido(c, nind=3):
    if not isinstance(c, dict):
        return False
    dia = c.get('dialoghi')
    if not isinstance(dia, list) or len([d for d in dia if isinstance(d, str) and d.strip()]) < 6:
        return False
    ind = c.get('indizi')
    if not isinstance(ind, list) or len(ind) < nind:
        return False
    for i in ind[:nind]:
        if not (isinstance(i, dict) and i.get('titolo', '').strip() and i.get('testo', '').strip()):
            return False
    fin = c.get('finale')
    return isinstance(fin, dict) and isinstance(fin.get('testo'), str) and fin['testo'].strip()


def _call(model, key, prompt):
    body = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'responseMimeType': 'application/json',
                             'responseSchema': SCHEMA, 'temperature': 0.6},
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


def _wire_copione(cfg, cop):
    """Incastra i testi nei file del pack, lasciando intatta la struttura/logica."""
    dpath = os.path.join(cfg, 'dialogues.json')
    dia = json.load(open(dpath, encoding='utf-8'))
    dia['dialoghi'] = [d for d in cop['dialoghi'] if isinstance(d, str) and d.strip()]
    if cop.get('gatto', '').strip():
        dia.setdefault('gatto', {})['messaggio'] = cop['gatto'].strip()
    json.dump(dia, open(dpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    ipath = os.path.join(cfg, 'interactions.json')
    it = json.load(open(ipath, encoding='utf-8'))
    for s, ind in zip(it.get('sorprese', []), cop['indizi']):
        s['titolo'] = ind['titolo'].strip()
        s['testo'] = ind['testo'].strip()
    if cop.get('finestra', '').strip():
        it.setdefault('finestra', {})['testo'] = cop['finestra'].strip()
    json.dump(it, open(ipath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    epath = os.path.join(cfg, 'endings.json')
    en = json.load(open(epath, encoding='utf-8'))
    en.setdefault('finale', {})
    en['finale']['titolo'] = cop['finale'].get('titolo', '').strip()
    en['finale']['testo'] = cop['finale']['testo'].strip()
    json.dump(en, open(epath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def compila(slug):
    key = _key()
    pack_dir = os.path.join(ROOT, 'packs', slug)
    assert os.path.isdir(pack_dir), f'pack inesistente: packs/{slug}'
    cfg = os.path.join(pack_dir, 'config')
    intervista = _intervista(pack_dir)
    oggetti = _oggetti(pack_dir)
    nind = len(oggetti) or 3
    ogg_txt = ('\n'.join(f'{i+1}. {o}' for i, o in enumerate(oggetti))
               if oggetti else '(oggetti non ancora definiti: deducili dai ricordi)')
    prompt = (f"{AGENTE['direttiva']}\n\n{AGENTE['criterio']}\n\n"
              f"=== INTERVISTA DEL CLIENTE ===\n{intervista}\n\n"
              f"=== I {nind} OGGETTI-INDIZIO ===\nDevi scrivere il campo 'indizi' con "
              f"ESATTAMENTE {nind} elementi, UNO per ciascun oggetto qui sotto e nello "
              f"stesso ordine. NON unirne due, NON saltarne nessuno (inclusa "
              f"l'eventuale TV/videogioco, che è un indizio come gli altri):\n{ogg_txt}\n\n"
              "Restituisci SOLO il copione come JSON coi campi richiesti.")
    for tent in range(1, 4):
        cop, err = _call(AGENTE['modello'], key, prompt)
        if cop is None:
            print(f'⚠ Sceneggiatore: modello non disponibile ({err}) — copione NON scritto, riprova')
            return 2
        got = len(cop.get('indizi', [])) if isinstance(cop, dict) else 0
        if not _valido(cop, nind):
            prompt += (f"\n\nATTENZIONE: hai prodotto {got} indizi ma ne servono ESATTAMENTE "
                       f"{nind} (uno per oggetto, TV/videogioco compreso), più ≥10 battute e il finale. Riprova completo.")
            continue
        if True:
            _wire_copione(cfg, cop)
            print(f'✅ copione pronto e incastrato nel pack "{slug}"  (agente Sceneggiatore, tentativo {tent})')
            print(f'   battute      {len(cop["dialoghi"])} · es. «{cop["dialoghi"][0][:60]}»')
            for i, ind in enumerate(cop['indizi'], 1):
                print(f'   indizio {i}    {ind["titolo"][:26]} — {ind["testo"].splitlines()[0][:52]}')
            if cop.get('gatto', '').strip():
                print(f'   gatto        {cop["gatto"].splitlines()[0][:60]}')
            print(f'   finale       {cop["finale"]["testo"].splitlines()[0][:60]}')
            print('\n   → scritti: config/dialogues.json · interactions.json · endings.json')
            return 0
        prompt += "\n\nATTENZIONE: output incompleto (servono ≥10 battute, 3 indizi con titolo+testo, finale). Riprova completo."
    print('⚠ Sceneggiatore: copione incompleto dopo 3 tentativi — NON scritto.')
    return 1


if __name__ == '__main__':
    sys.exit(compila(sys.argv[1]))
