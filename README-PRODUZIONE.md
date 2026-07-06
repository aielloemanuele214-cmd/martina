# Sempreaddue — guida di produzione

Il prodotto è **un solo file**: `stanza.html`. Contiene motore, grafica e
audio incorporati (base64), funziona offline e su qualunque hosting statico.

## Struttura del repo (dopo F1 — engine a moduli + pack)

```
engine/src/                   17 moduli ordinati del motore (css, motore, story, render…)
engine/CHANGELOG.md           versioni del motore (semver)
packs/martina/                IL CONTENUTO: manifest + config/*.json
  config/settings.json          nomi, data, musica, salvataggio
  config/characters.json        posizioni, gatto
  config/dialogues.json         battute di lui, messaggio del gatto
  config/interactions.json      i 3 indizi (posizioni, arrivo, testi) + finestra
  config/cutscenes.json         ballo, contratto
  config/endings.json           finale
  config/room.json              collisioni, limiti, zona dietro-letto
  config/sprites.json           fogli sprite: dimensioni, stati di animazione, altezze
  config/story.json             IL COMPORTAMENTO: eventi (quando/se/fai), scene a
                                passi (ballo, contratto, fusa), dialoghi, segreti,
                                finali a regole — tutto dati, zero codice
assets/                       asset finali (sprites/ rooms/ popup/ audio/) + _src/ (fogli grezzi)
tools/sad.py                  CLI unica: build-base [pack] · build <cliente> · check [pack]
tools/sprites.py              pipeline: scontorno + packing + ritratti da assets/_src/
clienti/*.json                personalizzazioni per cliente (sostituiscono il CONFIG)
dist/                         file consegnabili
legacy/prototipo/             primo prototipo (non più usato)
```

Comandi (CLI unica `tools/sad.py`):

```bash
python3 tools/sad.py ordine <slug>          # nuovo ordine: crea clienti/<slug>/ (json+foto+note)
python3 tools/sad.py validate clienti/<slug>/ordine.json   # schema + lint (id, file, limiti)
python3 tools/sad.py build clienti/<slug>/ordine.json      # → dist/stanza-<slug>.html (valida prima)
python3 tools/sad.py qa [dist/stanza-<slug>.html]          # suite QA Playwright (13 verifiche)
python3 tools/sad.py consegna <slug> [--push]              # build+QA+g/<token>.html+QR: consegna in un comando
python3 tools/sad.py build-base [pack]      # moduli engine + pack + asset → stanza.html
python3 tools/sad.py validate [pack]        # schema + lint dell'intero pack
python3 tools/sad.py new <slug> --da martina# nuovo pack (copia da uno esistente)
python3 tools/sad.py preview                # server locale per provare base e dist/
python3 tools/sad.py art                    # rigenera gli sprite da assets/_src/
python3 tools/sad.py music in.mp3 out.mp3 --strumentale    # loop senza stacco
```

Dipendenze di build: `pip install -r tools/requirements.txt` (+ `npm i playwright` per la QA).
(`python3 build.py …` continua a funzionare: delega a `sad.py`.)

Il motore non contiene alcun contenuto: per cambiare stanza, collisioni,
testi, indizi o sprite si toccano SOLO i JSON del pack e gli asset.

## Template per occasione (packs/)

- **martina** — il pack originale (golden test del motore)
- **romantica** — base neutra: anniversari, dediche, regali di coppia
- **compleanno** — sorprese a tema festa + Buono Regalo elegante
- **proposta** — la lettera apre la Richiesta Ufficiale di Matrimonio 💍

`python3 tools/sad.py build-base <template>` → `dist/base-<template>.html` per provarli.
Un ordine parte dal template dell'occasione: copia i suoi testi in `ordine.json`.
Catalogo e prezzi: `docs/LISTINO.md`.

## Flusso per ogni ordine (5 minuti + QA automatica)

**Un ordine = una cartella** `clienti/<slug>/` — dentro ci sta TUTTO il
materiale di quel cliente (mai file sparsi):

```
clienti/anna-marco/
├── ordine.json      la configurazione (nomi, testi, sorprese, finale)
├── foto/            le foto del cliente → "img": "file:foto/nome.jpg"
└── NOTE.md          contatto, tier, data, link di consegna
```

1. **Scaffolding**: `python3 tools/sad.py ordine anna-marco`
2. **Compila** `ordine.json` col materiale del cliente e metti le foto in `foto/`
3. **Genera**: `python3 tools/sad.py build clienti/anna-marco/ordine.json`
   (la validazione parte da sola: campi mancanti, id sbagliati, foto
   inesistenti e coordinate fuori scala vengono bloccati PRIMA della build)
4. **QA**: `python3 tools/sad.py qa dist/stanza-anna-marco.html` — 13 verifiche
   automatiche (raggiungibilità, apertura all'arrivo, finali, reset, save, fps)
5. **Pubblica**: trascina il file su [Netlify Drop](https://app.netlify.com/drop)
   (gratis), genera il QR, segna il link in `NOTE.md`, **committa la cartella**.

## Editor in-gioco (?editor) — per nuove ambientazioni

Apri una build con `?editor` in fondo all'URL: pannello in basso a sinistra.
- **✏️ Poligono**: ogni tocco un vertice → "Chiudi poligono" crea la hitbox
  (subito attiva: prova a camminarci contro con WASD)
- **✥ Sposta indizi**: tocca un marker (● oggetto · ○ punto d'arrivo), poi
  tocca la nuova posizione
- **🗑 Elimina**: tocca dentro un collider per rimuoverlo
- **⇩ Esporta JSON**: copia il risultato in `room.json` e `interactions.json`

È lo strumento per calibrare una stanza nuova in minuti invece che a
tentativi nel JSON. Nelle copie consegnate non esiste (parametro ignoto al cliente).

## Cosa si personalizza dal JSON (senza toccare il codice)

| Campo | Cosa cambia | Tier suggerito |
|---|---|---|
| `nomi`, `titolo` | nomi della coppia | Base |
| `dialoghi` | battute di lui | Base |
| `sorprese[].titolo/testo` | contenuto delle 4 sorprese | Base |
| `dataInizio` | contatore "insieme da X giorni" nel finale | Base |
| `finale` | dedica finale | Base |
| `sorprese[].foto` | foto reali della coppia nelle card | **Plus** |
| `musica: true` | loop musicale 8-bit di sottofondo | **Plus** |
| `gatto.nome/messaggio` | l'animale di casa | Plus |
| `ballo.didascalia`, `fuochi.didascalia` | didascalie delle scene | Base |
| posizioni/raggi degli hotspot | layout delle sorprese | se serve |

## Personalizzazione grafica (sprite su misura — tier Plus)

Gli sprite sorgente stanno in `assets/sprites/`. Per una coppia con
aspetto personalizzato: genera le immagini con l'AI usando i prompt in
fondo a questa guida (allegando sempre lo sprite esistente come
riferimento di stile), poi ri-esegui la pipeline di slicing e ricostruisci
`stanza.html`. Le regole d'oro per le generazioni:

- PNG con **trasparenza reale** (no scacchiera disegnata, no sfondo sfumato)
- frame **equidistanti in fila orizzontale**, personaggio centrato, piedi visibili
- ciclo di camminata che si chiude: contatto → passo dx → contatto → passo sx

Set minimo per un personaggio giocabile: idle frontale (1 frame),
camminata laterale (4 frame), camminata di schiena (4 frame).
Per l'NPC bastano idle frontale + schiena statica.
Per il ballo: 5 pose di coppia abbracciata, fila orizzontale.

## Architettura (per chi mette le mani nel codice)

- `engine/stanza_template.html` — sorgente del gioco con i placeholder
  `{{B64:*}}`; `tools/sad.py build-base` lo trasforma in `stanza.html`.
- In `stanza.html` il blocco tra `★★ INIZIO CONFIG ★★` e `★★ FINE CONFIG ★★`
  è l'unica parte che il builder cliente sostituisce.
- Motore: canvas con cache pre-scalate (60fps su mobile), camera adattiva,
  punta-e-clicca con pathfinding BFS + WASD, macchina a stati
  (idle/walk/interact/dance), collisioni su poligoni (`COLLIDERS`,
  ispezionabili con `?debug=1`).
- Scene: dialoghi con ritratti emotivi event-driven, 3 indizi con popup 1:1,
  4 segreti (gatto 💛, finestra, ballo, contratto), cinematiche una-tantum,
  finale con contatore giorni e contatore segreti.
- Audio: mp3 in loop senza stacco (Warm Memories in gioco, Paper Lantern nel
  menù), effetti soft Web Audio, valzer synth nel ballo.
- Il prossimo passo architetturale è descritto in `ARCHITETTURA.md` (F1+).

## Prompt di generazione sprite (da adattare)

> Pixel art sprite sheet, 32-bit era style (SNES/Stardew Valley quality).
> Same character as the reference image, identical outfit, hair and
> proportions. 4 walking animation frames side by side in a single
> horizontal row, evenly spaced, character centered in each frame, same
> size in every frame, full body with feet visible. [Front view / Back
> view / Side view walking left]. The frames form a seamless walk cycle.
> Transparent background, no checkerboard pattern, no background color or glow.
