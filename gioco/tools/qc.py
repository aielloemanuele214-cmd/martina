"""Controllo qualità visivo AUTOMATICO degli asset generati (art director AI).

Un modello Gemini con visione ispeziona ogni asset contro una rubrica severa e
ritorna un verdetto strutturato: {ok, difetti[], correzione}. È il cuore del
loop di rigenerazione in genera.py — genera → GIUDICA → se bocciato rigenera con
i difetti in prompt — così la build esce corretta tecnicamente ED esteticamente,
senza personaggi incorporati nello sfondo, animali dipinti, oggetti che si
spostano tra i due frame o frame di animazione incoerenti.

Il giudizio costa pochissimo (poco testo, 1-2 immagini) e viene annotato nel
registro consumi come le generazioni.
"""
import base64, json, os, ssl, time, urllib.request, urllib.error

CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
USAGE = os.path.expanduser('~/.config/sempreaddue/gemini-usage.tsv')
SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agenti', 'qc-agente.md')
JUDGE_MODEL = 'gemini-2.5-flash'      # visione capace ed economica; override da genera
JUDGE_COST = 0.004                    # stima prudente per giudizio (testo+1-2 img)
TRANSIENT = {429, 500, 502, 503, 504}  # errori API da riprovare con backoff

# Schema della risposta: JSON rigido, niente parsing fragile.
SCHEMA = {
    'type': 'object',
    'properties': {
        'ok': {'type': 'boolean'},
        'difetti': {'type': 'array', 'items': {'type': 'string'}},
        'correzione': {'type': 'string'},
    },
    'required': ['ok', 'difetti', 'correzione'],
}

# Regole comuni a tutta la produzione SempreAddue.
_ART = ("Sei un ART DIRECTOR severissimo di pixel art 16-bit per un gioco romantico. "
        "Giudichi UN asset di produzione. Sii rigoroso: al minimo difetto ok=false. "
        "In 'difetti' elenca ogni problema concreto (cosa e DOVE). In 'correzione' "
        "scrivi UNA istruzione in inglese, imperativa e specifica, da aggiungere al "
        "prompt di rigenerazione per eliminare quei difetti.")

# Rubriche per tipo di asset. {n},{desc},{anim},{subj} riempiti da genera.
RUBRICHE = {
    'room': (
        "ASSET: SFONDO STANZA statico (il palco del gioco). REGOLE:\n"
        "1) NESSUN essere vivente dipinto nello sfondo: niente persone, figure/"
        "silhouette umane, gatti, cani, animali o animaletti. Ogni essere vivo è uno "
        "sprite separato, MAI nello sfondo.\n"
        "2) Solo architettura, mobili e oggetti inanimati.\n"
        "3) Deve esistere un'ampia area di PAVIMENTO libero e leggibile.\n"
        "4) Niente testo, watermark, cornici.\n"
        "Se vedi anche UNA persona o UN animale => ok=false e indicali con posizione."),
    'room_anim': (
        "ASSET: DUE frame (1 = riferimento, 2 = variante animata) di uno sfondo che "
        "deve andare in LOOP fluido. REGOLE:\n"
        "1) Possono cambiare SOLTANTO questi elementi animati: {anim}.\n"
        "2) Tutto il resto deve essere IDENTICO: nessun oggetto che appare, sparisce o "
        "si sposta tra i due frame (es. un gatto in più, una candela spostata, mobili "
        "che ballano).\n"
        "3) In NESSUNO dei due frame ci devono essere persone o animali (gli sfondi non "
        "ne hanno mai).\n"
        "Se un oggetto si sposta/compare o c'è un essere vivente => ok=false, di' quale "
        "e in quale frame."),
    'sheet': (
        "ASSET: FOGLIO SPRITE su UNA SOLA RIGA orizzontale che deve contenere "
        "ESATTAMENTE {n} celle affiancate dello STESSO identico personaggio. Pose "
        "attese: {desc}. REGOLE:\n"
        "0) DEVE essere una sola riga di {n} figure. Se le figure sono disposte su più "
        "righe (griglia 2x2), o se il numero TOTALE di figure è diverso da {n} => "
        "ok=false (conta tutte le figure nell'immagine).\n"
        "1) Ogni cella = UNA sola figura del personaggio, coerente col design delle "
        "altre celle (stessi capelli, vestiti, colori, proporzioni).\n"
        "2) NESSUna posa incoerente col ciclo: in un ciclo di camminata NON ci devono "
        "essere pose sedute/accovacciate/inginocchiate.\n"
        "3) MAI due figure sovrapposte nella stessa cella; MAI una persona o un animale "
        "in più.\n"
        "4) Piedi mai tagliati; scala uniforme tra le celle.\n"
        "Conta le figure: se sono != {n}, se una è seduta/doppia o fuori design => "
        "ok=false, indica quale cella."),
    'mask': (
        "ASSET: MASCHERA DI COLLISIONE della stanza. REGOLE:\n"
        "1) SOLO due colori: bianco puro e nero puro, riempimenti piatti (no linee, "
        "trame, sfumature, testo).\n"
        "2) BIANCO = pavimento calpestabile. NERO = muri, TUTTA la fascia del muro/"
        "soffitto in alto, l'ingombro dei mobili volumetrici e tutto ciò che è fuori "
        "stanza.\n"
        "3) La fascia alta (muro/soffitto in prospettiva) DEVE essere nera: se lassù è "
        "bianca è un errore grave (i personaggi camminerebbero sul muro).\n"
        "4) NESSUna silhouette di persona o animale nella maschera.\n"
        "Se la parete in alto è bianca, o c'è una sagoma di personaggio, o ci sono più "
        "di due toni => ok=false."),
    'popup': (
        "ASSET: illustrazione quadrata primo piano ambientata, soggetto principale: "
        "{subj}. È NORMALE e DESIDERABILE che intorno ci sia l'atmosfera della stanza "
        "(mobili, candele, luci): NON è un difetto. Boccia (ok=false) SOLO se: c'è "
        "testo o watermark; oppure compare una PERSONA o un ANIMALE (che non sia il "
        "soggetto richiesto); oppure il soggetto principale {subj} non è riconoscibile. "
        "La scrittura a mano ILLEGGIBILE su un oggetto del mondo (una lettera, un "
        "libro) NON è un difetto: è testo-UI/didascalie/watermark sovrapposti a "
        "essere vietati. Altrimenti ok=true."),
}


# La DIRETTIVA e i CRITERI dell'agente vivono in un file editabile (SPEC): il
# codice li carica da lì. Addestrare l'agente = modificare quel file. I valori
# qui sopra restano solo come rete di sicurezza se la spec manca o è illeggibile.
def _load_agent():
    prof = {'modello': JUDGE_MODEL, 'direttiva': _ART, 'rubriche': dict(RUBRICHE)}
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
        for k, v in sez.items():
            if k.startswith('CRITERIO '):
                prof['rubriche'][k.split(' ', 1)[1].strip()] = v
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'⚠ QC: spec agente non caricata ({e}); uso i valori interni')
    return prof


AGENTE = _load_agent()


def _img_part(path):
    b = base64.b64encode(open(path, 'rb').read()).decode()
    return {'inlineData': {'mimeType': 'image/png', 'data': b}}


def _log(model):
    try:
        os.makedirs(os.path.dirname(USAGE), exist_ok=True)
        if not os.path.exists(USAGE):
            open(USAGE, 'w').write('quando\tmodello\timmagini\tcosto_stima_eur\n')
        ts = os.environ.get('SAD_TS', 'qc')
        open(USAGE, 'a').write(f'{ts}\t{model} (qc)\t0\t{JUDGE_COST:.3f}\n')
    except Exception:
        pass


def judge(kind, image_path, key, ref_path=None, model=None, **fmt):
    """Giudica un asset con la DIRETTIVA e i CRITERI dell'agente (spec editabile).
    Ritorna {ok, difetti[], correzione, stato}. `stato`: 'giudicato' oppure
    'errore'. Su errore API riprova con backoff; se il giudizio resta
    indisponibile ritorna ok=False + stato='errore' — così un asset NON passa mai
    in silenzio: viene segnalato per revisione umana (mai auto-promosso al buio)."""
    rubrica = AGENTE['rubriche'][kind]
    rubrica = rubrica.format(**fmt) if fmt else rubrica
    model = model or AGENTE['modello']
    parts = []
    if kind == 'room_anim' and ref_path:
        parts += [{'text': 'FRAME 1 (riferimento):'}, _img_part(ref_path),
                  {'text': 'FRAME 2 (variante animata):'}, _img_part(image_path)]
    elif kind == 'popup_ref' and ref_path:
        parts += [{'text': 'IMMAGINE 1 (la STANZA di riferimento):'}, _img_part(ref_path),
                  {'text': 'IMMAGINE 2 (il PRIMO PIANO da verificare):'}, _img_part(image_path)]
    else:
        parts.append(_img_part(image_path))
    parts.append({'text': AGENTE['direttiva'] + '\n\n' + rubrica})
    body = json.dumps({
        'contents': [{'parts': parts}],
        'generationConfig': {'responseMimeType': 'application/json',
                             'responseSchema': SCHEMA, 'temperature': 0.1},
    }).encode()
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    req = urllib.request.Request(url, data=body,
        headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
    err = None
    for att in range(4):                       # 1 tentativo + 3 retry (2s,4s,8s)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                d = json.load(r)
            out = json.loads(d['candidates'][0]['content']['parts'][0]['text'])
            _log(model)
            out.setdefault('difetti', []); out.setdefault('correzione', '')
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
        except Exception as e:                 # risposta malformata: non riprovare
            err = str(e); break
    return {'ok': False, 'difetti': [f'giudizio non disponibile: {err}'],
            'correzione': '', 'stato': 'errore'}


if __name__ == '__main__':
    import sys
    key = os.environ['GEMINI_API_KEY']
    kind, path = sys.argv[1], sys.argv[2]
    print(json.dumps(judge(kind, path, key), ensure_ascii=False, indent=2))
