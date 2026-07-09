#!/usr/bin/env python3
"""Agente Art Director (FIG-10) — validazione estetica finale della scena.

L'ultima porta prima della consegna: guarda la SCENA DI GIOCO COMPOSITA (stanza +
personaggi insieme), non i singoli asset (quelli li ha già controllati il QC), e
decide se è "degna di essere regalata". Se boccia, indica quale figura a monte
deve intervenire.

Flusso: build (se manca) → screenshot della scena (Playwright) → giudizio del
modello con la DIRETTIVA editabile (`tools/agenti/art-director-agente.md`).

  python3 tools/sad.py direttore <slug>
"""
import base64, json, os, ssl, subprocess, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
ENV = os.path.expanduser('~/.config/sempreaddue/gemini.env')
SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agenti', 'art-director-agente.md')
SHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scena_shot.js')
DEFAULT_MODEL = 'gemini-2.5-flash'
COST = 0.004
TRANSIENT = {429, 500, 502, 503, 504}

_DIRETTIVA = ("Sei l'Art Director di SempreAddue: guardi la scena di gioco composita finale e "
    "decidi se è degna di essere regalata (stile 16-bit coerente, leggibilità, nessun "
    "personaggio che fluttua o doppioni, emozione e cura premium).")
_CRITERIO = "Valuta stile, leggibilità, integrità visiva, emozione. Indica la figura da rilavorare se bocci."

SCHEMA = {
    'type': 'object',
    'properties': {
        'ok': {'type': 'boolean'},
        'note': {'type': 'array', 'items': {'type': 'string'}},
        'consiglio': {'type': 'string'},
        'rework': {'type': 'string'},
    },
    'required': ['ok', 'note', 'consiglio'],
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
    prof = {'modello': DEFAULT_MODEL, 'fallback': 'gemini-flash-latest',
            'direttiva': _DIRETTIVA, 'criterio': _CRITERIO}
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
        if sez.get('MODELLO_FALLBACK'):
            prof['fallback'] = sez['MODELLO_FALLBACK'].splitlines()[0].strip()
        if sez.get('DIRETTIVA'):
            prof['direttiva'] = sez['DIRETTIVA']
        if sez.get('CRITERIO scena'):
            prof['criterio'] = sez['CRITERIO scena']
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'⚠ Art Director: spec agente non caricata ({e}); uso i valori interni')
    return prof


AGENTE = _load_agent()


def _log(model):
    try:
        os.makedirs(os.path.dirname(USAGE), exist_ok=True)
        if not os.path.exists(USAGE):
            open(USAGE, 'w').write('quando\tmodello\timmagini\tcosto_stima_eur\n')
        ts = os.environ.get('SAD_TS', 'direttore')
        open(USAGE, 'a').write(f'{ts}\t{model} (art-director)\t0\t{COST:.3f}\n')
    except Exception:
        pass


def _shot(game_file, out_png):
    env = dict(os.environ)
    env['GAME_FILE'] = os.path.abspath(game_file)
    env['OUT'] = os.path.abspath(out_png)
    env.setdefault('NODE_PATH', '/opt/node22/lib/node_modules')
    r = subprocess.run(['node', SHOT], env=env, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out_png):
        sys.exit(f'screenshot fallito: {r.stderr.strip() or r.stdout.strip()}')


def _cast(slug):
    """Cast atteso in scena, letto dal pack: sempre protagonista + partner, e
    l'animale solo se previsto. Dà all'Art Director il contesto per riconoscere
    un doppione (es. due gatti) come DIFETTO, non come 'stanza accogliente'."""
    ani = False
    try:
        ch = json.load(open(os.path.join(ROOT, 'packs', slug, 'config', 'characters.json'), encoding='utf-8'))
        ani = bool(ch.get('gatto'))
    except Exception:
        try:
            g = json.load(open(os.path.join(ROOT, 'packs', slug, 'genera.json'), encoding='utf-8'))
            ani = bool(g.get('animale', '').strip())
        except Exception:
            pass
    esseri = "il protagonista, il partner" + (" e UN solo animale" if ani else "")
    return ("\n\nCAST ATTESO: in scena possono esistere SOLO " + esseri + ". Se vedi PIÙ "
            "persone o PIÙ animali del previsto (es. due gatti identici, un personaggio "
            "duplicato), è un DIFETTO TECNICO: ok=false, rework=\"pipeline\".")


def _judge(model, key, png, extra=''):
    b = base64.b64encode(open(png, 'rb').read()).decode()
    prompt = f"{AGENTE['direttiva']}\n\n{AGENTE['criterio']}{extra}"
    body = json.dumps({
        'contents': [{'parts': [{'inlineData': {'mimeType': 'image/png', 'data': b}}, {'text': prompt}]}],
        'generationConfig': {'responseMimeType': 'application/json',
                             'responseSchema': SCHEMA, 'temperature': 0.2},
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
            out.setdefault('note', []); out.setdefault('consiglio', ''); out.setdefault('rework', '')
            out['stato'] = 'giudicato'
            return out
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
    return {'ok': False, 'note': [f'giudizio non disponibile: {err}'], 'consiglio': '',
            'rework': '', 'stato': 'errore'}


def _judge_chain(key, png, extra=''):
    """Prova il modello primario e, se è in avaria, quello di riserva: una
    singola indisponibilità di un modello non ferma la validazione."""
    modelli = [m for m in (AGENTE['modello'], AGENTE.get('fallback')) if m]
    v = None
    for m in modelli:
        v = _judge(m, key, png, extra)
        if v.get('stato') == 'giudicato':
            return v
        print(f'   · modello {m} non disponibile, provo il successivo…' if m != modelli[-1] else '', end='')
    return v


def valida(slug):
    key = _key()
    game = os.path.join(ROOT, 'dist', f'base-{slug}.html')
    if not os.path.exists(game):
        print(f'· build mancante, la costruisco (base-{slug}.html) …')
        r = subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'sad.py'), 'build-base', slug])
        if r != 0 or not os.path.exists(game):
            sys.exit('build fallita: impossibile validare')
    png = os.path.join(ROOT, 'dist', f'scena-{slug}.png')
    print('· fotografo la scena di gioco …')
    _shot(game, png)
    print('· giudizio estetico dell\'Art Director …')
    v = _judge_chain(key, png, _cast(slug))

    if v.get('stato') == 'errore':
        print(f'⚠ Art Director non disponibile: {v["note"][0]} — validazione da rifare')
        return 2
    print()
    if v['ok']:
        print(f'✅ APPROVATO — la scena è degna di essere consegnata.')
        if v.get('consiglio'):
            print(f'   nota: {v["consiglio"]}')
        print(f'   (scena: dist/scena-{slug}.png)')
        return 0
    print('🔁 DA RILAVORARE — l\'Art Director non approva:')
    for n in v['note']:
        print(f'   • {n}')
    if v.get('consiglio'):
        print(f'   consiglio: {v["consiglio"]}')
    if v.get('rework'):
        print(f'   → figura da far intervenire: FIG «{v["rework"]}»')
    print(f'   (scena: dist/scena-{slug}.png)')
    return 1


if __name__ == '__main__':
    sys.exit(valida(sys.argv[1]))
