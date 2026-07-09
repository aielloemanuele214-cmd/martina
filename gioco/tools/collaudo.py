#!/usr/bin/env python3
"""Collaudo finale (FIG-05/10) — testa anche ANIMAZIONI e INTERAZIONI, non solo
la scena statica.

Fa tre cose:
  1) QA funzionale (tools/qa.js): interattivi raggiungibili, popup che si aprono,
     dialogo, finale, zero errori JS, fps.
  2) Provino animato: guida il gioco e cattura 3 fotogrammi (fermo, camminata a
     sinistra = test mirroring, interazione) + verifica che l'interazione apra il
     popup.
  3) Giudizio visivo del provino con la direttiva editabile
     (tools/agenti/collaudo-agente.md): animazioni e interazioni coerenti?

  python3 tools/sad.py collaudo <slug>
"""
import base64, json, os, ssl, subprocess, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
ENV = os.path.expanduser('~/.config/sempreaddue/gemini.env')
SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agenti', 'collaudo-agente.md')
DRIVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collaudo_shot.js')
QAJS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qa.js')
COST = 0.004
TRANSIENT = {429, 500, 502, 503, 504}

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
_DIRETTIVA = ("Sei il collaudatore: ricevi 3 fotogrammi (fermo, camminata a sinistra, "
    "interazione) e giudichi se animazioni e interazioni sono coerenti (stesso "
    "personaggio, pose in piedi non spezzate, mirroring corretto, nessun accavallamento).")
_CRITERIO = "Verifica coerenza di camminata e interazione; indica la figura da rilavorare se bocci."


def _key():
    if os.environ.get('GEMINI_API_KEY'):
        return os.environ['GEMINI_API_KEY']
    if os.path.exists(ENV):
        for ln in open(ENV):
            if 'GEMINI_API_KEY' in ln and '=' in ln:
                return ln.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('GEMINI_API_KEY non impostata')


def _load_agent():
    prof = {'modello': 'gemini-2.5-flash', 'fallback': 'gemini-flash-latest',
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
        if sez.get('CRITERIO provino'):
            prof['criterio'] = sez['CRITERIO provino']
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'⚠ Collaudo: spec non caricata ({e})')
    return prof


AGENTE = _load_agent()


def _log(model):
    try:
        os.makedirs(os.path.dirname(USAGE), exist_ok=True)
        ts = os.environ.get('SAD_TS', 'collaudo')
        open(USAGE, 'a').write(f'{ts}\t{model} (collaudo)\t0\t{COST:.3f}\n')
    except Exception:
        pass


def _env_node():
    env = dict(os.environ)
    env.setdefault('NODE_PATH', '/opt/node22/lib/node_modules')
    return env


def _qa(game):
    env = _env_node(); env['GAME_FILE'] = os.path.abspath(game)
    r = subprocess.run(['node', QAJS], env=env, capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if l.strip()]
    ok = 'falliti' not in r.stdout or ', 0 falliti' in r.stdout
    return ok, tail[-1] if tail else '(nessun output)'


def _provino(game, outdir, inter):
    os.makedirs(outdir, exist_ok=True)
    env = _env_node()
    env['GAME_FILE'] = os.path.abspath(game); env['OUTDIR'] = os.path.abspath(outdir)
    env['INTER'] = inter or ''
    r = subprocess.run(['node', DRIVER], env=env, capture_output=True, text=True)
    try:
        info = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        info = {'errs': [r.stderr.strip() or 'driver fallito']}
    return info


def _contact(outdir):
    """Affianca i 3 fotogrammi in un unico provino numerato."""
    from PIL import Image, ImageDraw
    imgs = []
    for i, n in enumerate(('c_idle.png', 'c_walk.png', 'c_interact.png'), 1):
        p = os.path.join(outdir, n)
        if os.path.exists(p):
            im = Image.open(p).convert('RGB').resize((380, 380))
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 84, 26], fill=(0, 0, 0))
            d.text((6, 6), f'{i}', fill=(255, 255, 255))
            imgs.append(im)
    if not imgs:
        return None
    W = sum(x.width for x in imgs) + 8 * (len(imgs) - 1)
    sheet = Image.new('RGB', (W, 380), (18, 14, 20))
    x = 0
    for im in imgs:
        sheet.paste(im, (x, 0)); x += im.width + 8
    out = os.path.join(outdir, 'provino.png'); sheet.save(out)
    return out


def _judge(key, png):
    b = base64.b64encode(open(png, 'rb').read()).decode()
    prompt = f"{AGENTE['direttiva']}\n\n{AGENTE['criterio']}"
    body = json.dumps({
        'contents': [{'parts': [{'inlineData': {'mimeType': 'image/png', 'data': b}}, {'text': prompt}]}],
        'generationConfig': {'responseMimeType': 'application/json', 'responseSchema': SCHEMA, 'temperature': 0.2},
    }).encode()
    for m in [x for x in (AGENTE['modello'], AGENTE.get('fallback')) if x]:
        err = None
        for att in range(4):
            try:
                req = urllib.request.Request(
                    f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent',
                    data=body, headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                    d = json.load(r)
                out = json.loads(d['candidates'][0]['content']['parts'][0]['text'])
                _log(m); out.setdefault('note', []); out.setdefault('consiglio', '')
                out.setdefault('rework', ''); out['stato'] = 'giudicato'
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
    return {'ok': False, 'note': [f'giudizio non disponibile: {err}'], 'consiglio': '', 'rework': '', 'stato': 'errore'}


def collauda(slug):
    key = _key()
    game = os.path.join(ROOT, 'dist', f'base-{slug}.html')
    if not os.path.exists(game):
        print(f'· build mancante, la costruisco …')
        if subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'sad.py'), 'build-base', slug]) != 0:
            sys.exit('build fallita')
    # primo indizio del pack, per provare un'interazione reale
    inter = ''
    try:
        it = json.load(open(os.path.join(ROOT, 'packs', slug, 'config', 'interactions.json'), encoding='utf-8'))
        inter = (it.get('sorprese') or [{}])[0].get('id', '')
    except Exception:
        pass
    print('· QA funzionale (qa.js) …')
    qa_ok, qa_line = _qa(game)
    print('  ' + qa_line)
    print('· provino animato (fermo · camminata · interazione) …')
    outdir = os.path.join(ROOT, 'dist', f'collaudo-{slug}')
    info = _provino(game, outdir, inter)
    if info.get('errs'):
        print('  ⚠ errori JS durante il provino:', '; '.join(info['errs'])[:160])
    print(f"  camminata a sinistra: {info.get('walk')} · interazione apre popup: {info.get('popupOpened')}")
    sheet = _contact(outdir)
    vis = _judge(key, sheet) if sheet else {'ok': False, 'note': ['provino non catturato'], 'stato': 'errore'}
    print('\n=== ESITO COLLAUDO ===')
    print(f"  QA funzionale:      {'✅' if qa_ok else '❌'}")
    print(f"  interazione→popup:  {'✅' if info.get('popupOpened') else '❌'}")
    print(f"  errori JS:          {'✅ nessuno' if not info.get('errs') else '❌ ' + str(info['errs'][:1])}")
    if vis.get('stato') == 'errore':
        print(f"  giudizio animazioni: ⚠ non disponibile ({vis['note'][0]})")
    else:
        print(f"  animazioni/interaz.: {'✅ coerenti' if vis['ok'] else '❌ ' + '; '.join(vis['note'])[:160]}")
        if not vis['ok'] and vis.get('rework'):
            print(f"     → figura da rilavorare: {vis['rework']}")
    ok = qa_ok and info.get('popupOpened') and not info.get('errs') and vis.get('ok')
    print(f"\n  PROVINO: {'✅ TUTTO COERENTE' if ok else '🔁 DA RIVEDERE'}  (provino: {sheet})")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(collauda(sys.argv[1]))
