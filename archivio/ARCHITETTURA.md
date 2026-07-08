> ⚠️ **Documento storico** — conservato per riferimento, non più operativo.
> Per lavorare oggi vedi il `README.md` alla radice e `docs/`.

# Architettura Scalabile — Piattaforma "Sempreaddue"
### Da gioco-regalo singolo a engine commerciale di mini avventure grafiche personalizzate

**Versione documento:** 1.0 · **Base analizzata:** v1.0.0-rc5 (`stanza.html` 1.566 righe, 60 funzioni, `build.py`, `clienti/*.json`, `assets/pipeline_sprites.py`)

---

## 1. Analisi dell'architettura attuale

### Come funziona oggi

```
stanza.html (file unico, ~3,6 MB)
├── CSS (UI, dialoghi, popup, finale, splash)
├── CONFIG  ← blocco JS tra marcatori ★★, sostituito da build.py
├── COLLIDERS, BEHIND_BED, ASSETS (dimensioni sprite)  ← nel "motore"
└── ~60 funzioni: rendering, FSM, pathfinding, audio, dialoghi,
    popup, segreti, cinematiche, salvataggio, finale

build.py  clienti/<slug>.json ──→ dist/stanza-<slug>.html
assets/pipeline_sprites.py    ──→ scontorno + packing sprite sheet
```

Il seme della separazione motore/contenuti **esiste già**: il blocco `CONFIG`
(nomi, dialoghi, sorprese, gatto, finestra, ballo, finale, contratto,
posizioni) è sostituibile per cliente senza toccare il codice, e la pipeline
asset è riproducibile. È il punto di forza da cui partire.

### Cosa c'è di buono (da conservare)
- **File unico autocontenuto**: zero hosting complesso, si consegna un HTML
  (Netlify Drop + QR). È un *vantaggio commerciale*, non un debito.
- **Motore leggero e testato**: 60 fps su mobile, cache pre-scalate, BFS,
  FSM, audio sbloccato su iOS. Non serve un framework.
- **Pipeline asset in Python** già committata e riproducibile.
- **Builder per cliente** già funzionante (`build.py` + `clienti/*.json`).

## 2. Criticità (ordinate per gravità)

| # | Criticità | Dove | Perché blocca la scalabilità |
|---|-----------|------|------------------------------|
| C1 | **Cinematiche hardcoded**: `scenaBallo()` e `scenaContratto()` sono funzioni del motore | stanza.html | Ogni nuovo tipo di evento (proposta, compleanno, escape room) richiede di scrivere codice. È il vincolo n°1. |
| C2 | **Segreti hardcoded**: gatto, finestra, ballo, contratto sono 4 flag fissi (`SEGRETI_TOTALE=4`, chiavi di salvataggio fisse) | stanza.html | Impossibile aggiungere/togliere segreti o cambiare condizioni di sblocco da configurazione. |
| C3 | **Stanza fusa nel motore**: `COLLIDERS`, `BEHIND_BED`, limiti stanza (`px<2‖px>97.5…`), doppio sfondo animato | stanza.html | Una seconda ambientazione richiede di modificare il sorgente del motore. |
| C4 | **Semantica sprite cablata**: `DIR_SHEET`, `FR_IDLE/WALK_A/WALK_B/INTERACT`, `WALK_SEQ`, `DANCE_SEQ`, altezze `H_LEI/H_LUI` | stanza.html | Un personaggio con 6 frame o 2 direzioni non è rappresentabile. |
| C5 | **Finale unico**: un solo `showFinale()`, messaggio singolo | stanza.html | Niente finali multipli/nascosti/alternativi. |
| C6 | **Entità speciali uniche**: 1 NPC (`npc`), 1 gatto (`cat`), 1 finestra — oggetti singleton con logica dedicata | stanza.html | Non si possono avere 2 NPC, 0 gatti, 3 finestre. |
| C7 | **Doppio builder**: `build_rc.py` (asset→template, vive nello scratchpad) e `build.py` (config→cliente) | repo/scratchpad | Il passaggio asset→HTML non è nel repo: il progetto non è ricostruibile da zero da chi non ha la sessione. |
| C8 | **Schema CONFIG non validato**: un JSON cliente sbagliato produce un gioco rotto scoperto solo a mano | build.py | Impossibile scalare a decine di clienti senza validazione automatica. |
| C9 | **Testi UI hardcoded**: hint ("Clicca dove vuoi andare…"), etichette bottoni, messaggi contatore segreti | stanza.html | Niente localizzazione, niente tono personalizzato per occasione. |
| C10 | **Tema visivo fisso**: palette, font, cuori del HUD nel CSS | stanza.html | Un'avventura "investigativa" o "aziendale" avrebbe lo stesso look romantico. |
| C11 | **Salvataggio a chiavi fisse** (`found`, `segreto`, `purr`, `dance`, `contract`) | stanza.html | Ogni nuovo contenuto richiede di toccare load/save. |
| C12 | Asset legacy morti nel repo (`lei_front.png`, `lei_idle.png`, `ballo.png`, `pt_lui.png`…) | assets/sprites | Confusione su quali file siano davvero usati. |

**Diagnosi sintetica:** il motore è sano; il problema è che **il 40% del
"contenuto" vive ancora dentro il motore** (stanza, segreti, cinematiche,
semantica sprite, finale). La riprogettazione consiste nel *finire* la
separazione già iniziata, non nel riscrivere.

---

## 3. Nuova architettura proposta

### Principio guida
> **L'Engine è un interprete. L'avventura è un dato.**
> Il motore non conosce "vinile", "gatto" o "ballo": conosce *oggetti
> interattivi*, *trigger condizionati*, *cutscene a passi* e *finali a regole*.

### I due livelli

```
┌─────────────────────────────────────────────────────────┐
│  ADVENTURE PACK (contenuti, 100% dati)                  │
│  manifest + JSON + immagini + audio                     │
│  → definisce COSA succede                               │
├─────────────────────────────────────────────────────────┤
│  ENGINE (codice, versionato, MAI modificato per un      │
│  cliente)                                               │
│  rendering · camera · input · FSM · pathfinding ·       │
│  collisioni · animazioni data-driven · audio · UI ·     │
│  dialoghi · popup · trigger/eventi · cutscene player ·  │
│  achievement (segreti) · selettore finali · salvataggio │
│  → definisce COME succede                               │
└─────────────────────────────────────────────────────────┘
```

### I 5 sottosistemi da generalizzare (il cuore del refactoring)

**A. Animazioni data-driven** (risolve C4)
Ogni sprite sheet dichiara i propri stati e sequenze; il motore ha un
*animation player* generico:
```json
{ "sheet": "lei.png", "fw": 192, "fh": 242,
  "anchor": "feet",
  "states": {
    "idle":     { "frames": [0], "bob": 1.0 },
    "walk":     { "frames": [1,0,2,0], "dur": 0.18 },
    "interact": { "frames": [3], "hold": true },
    "dance":    { "frames": [0,1,2,3,4,3,2,1], "dur": 0.9 }
  },
  "directions": { "down":"lei_down.png", "up":"lei_up.png",
                  "left":"lei_left.png", "right":"lei_right.png" } }
```
Le costanti `WALK_SEQ`, `DANCE_SEQ`, `DIR_SHEET` spariscono dal motore.

**B. Trigger + condizioni dichiarative** (risolve C1, C2, C6)
Un mini-linguaggio JSON interpretato (niente `eval`), con lo stato di partita
come *state bag* generico:
```json
{ "when": "interact:giradischi",
  "if":   { "all": [ "found.tv", "found.lettera", "!done.ballo" ] },
  "do":   [ { "run": "cutscene:ballo" }, { "set": "done.ballo" } ],
  "else": [ { "run": "popup:giradischi" } ] }
```
Il salvataggio diventa la serializzazione dello state bag (risolve C11).

**C. Cutscene a passi (DSL)** (risolve C1 — il vincolo più grande)
`scenaBallo()` oggi è codice; domani è **questo dato**:
```json
{ "id": "ballo",
  "steps": [
    { "input": "block" },
    { "music": { "fadeOut": 1.4 } },
    { "fade": "in" },
    { "type": "Ho una sorpresa per te…" },
    { "fade": "out" },
    { "actors": { "player": "hide", "npc": "hide" },
      "spawn": { "sprite": "ballo", "state": "dance", "at": [47, 64] } },
    { "music": { "play": "valzer" } },
    { "wait": 15 },
    { "fade": "in" },
    { "type": "Nessuno aveva mai fatto niente di simile per me…\nTi amo." },
    { "fade": "out" }, { "restore": true }, { "input": "release" }
  ] }
```
Con ~12 tipi di passo (`fade`, `type`, `wait`, `music`, `spawn`, `move`,
`popup`, `dialog`, `set`, `sfx`, `shake`, `document`) si coprono ballo,
contratto, proposta di matrimonio, indagine, escape room. Il "contratto"
diventa `{ "document": { "src": "contratto.html.frag", "scrollable": true } }`.

**D. Segreti = achievement generici** (risolve C2)
```json
{ "id": "gatto", "unlock": { "when": "interact:gatto" },
  "reward": { "hud": "💛" },
  "once": { "if": "first_interaction", "do": [ { "run": "cutscene:fusa" } ] } }
```
Contatore, messaggi del finale e HUD si calcolano dalla lista. Ordine
richiesto e combinazioni si esprimono con le stesse condizioni di B
(es. `"if": { "seq": ["interact:tv", "interact:gatto", "interact:finestra"] }`).

**E. Finali a regole ordinate** (risolve C5)
```json
[ { "id": "perfetto", "if": { "all": ["found.*", "secrets.count==4"] }, "…": "…" },
  { "id": "nascosto", "if": { "seq": ["gatto","finestra","gatto"] }, "hidden": true },
  { "id": "standard", "if": "found.*" } ]
```
Prima regola vera (in ordine) → quel finale. Il finale standard è l'ultima.

### La stanza come dato (risolve C3, C10)
`room.json`: sfondi (n frame di animazione, non 2 fissi), poligoni di
collisione, zone di trasparenza (`behind`), limiti, luci/vignetta, palette e
font del tema, punto di spawn. Il debug mode attuale (`?debug`) si estende a
**modalità editor**: click per disegnare i poligoni direttamente in gioco ed
esportarli in JSON (base del futuro editor, §9).

---

## 4. Struttura completa delle cartelle

```
sempreaddue/
├── engine/                      # IL PRODOTTO (versionato semver, mai fork per cliente)
│   ├── src/
│   │   ├── core/      (loop, camera, input, save, statebag)
│   │   ├── world/     (room, colliders, pathfinding, entities)
│   │   ├── anim/      (animation player, spritesheet)
│   │   ├── story/     (triggers, conditions, cutscene player,
│   │   │               dialogues, secrets, endings)
│   │   ├── ui/        (hud, popup, dialog box, finale, splash, theme)
│   │   └── audio/     (music, sfx synth, unlock iOS)
│   ├── engine.js                # bundle unico generato (nessuna dipendenza runtime)
│   └── CHANGELOG.md
│
├── packs/                       # LE AVVENTURE (un pack = un prodotto venduto)
│   └── martina/                 # esempio: il regalo attuale
│       ├── manifest.json        # nome, versione pack, versione engine richiesta
│       ├── config/
│       │   ├── settings.json    # nomi, data, salvataggio, lingua
│       │   ├── room.json        # sfondi, collisioni, zone, tema, luci
│       │   ├── characters.json  # player, npc, gatto… (tutti opzionali, N qualsiasi)
│       │   ├── interactions.json# oggetti interattivi + hitbox + eventi
│       │   ├── dialogues.json   # battute, ritratti, rami, condizioni
│       │   ├── secrets.json     # achievement + condizioni + ricompense
│       │   ├── events.json      # trigger dichiarativi
│       │   ├── cutscenes.json   # scene a passi (DSL)
│       │   ├── endings.json     # regole ordinate dei finali
│       │   ├── music.json       # tracce, ruoli (menu/gioco/scene), loop points
│       │   └── theme.json       # palette, font, testi UI, icone HUD
│       └── assets/
│           ├── characters/  rooms/  objects/  popup/
│           ├── music/  sounds/  photos/  letters/  fonts/
│           └── _src/            # sorgenti grezzi (sheet AI non scontornati)
│
├── templates/                   # pack di partenza per occasioni
│   ├── romantica/  compleanno/  proposta/  investigativa/
│
├── tools/                       # AUTOMAZIONE (CLI unica: `python3 sad.py …`)
│   ├── sad.py                   # entry point: new / build / validate / preview
│   ├── sprites.py               # scontorno flood-fill + packing (già esistente)
│   ├── music.py                 # loop senza stacco (RMS scan + crossfade, già fatto)
│   ├── portraits.py             # ritratti auto dai sheet
│   ├── schemas/                 # JSON Schema di OGNI file di config
│   └── qa.js                    # suite Playwright riusabile su ogni pack
│
├── dist/                        # output: un HTML autocontenuto per pack
└── docs/                        # manuale di produzione, ricette, prezzi
```

**Regola d'oro:** sostituire l'intera cartella `packs/<slug>/` produce una
nuova avventura. `engine/` e `tools/` non si toccano mai per un cliente.

## 5. Struttura dei file JSON (esempi completi)

`settings.json`
```json
{ "titolo": "Una stanza tutta per voi", "lingua": "it",
  "nomi": { "player": "Marti", "npc": "Manu" },
  "dataInizio": "2023-02-14", "musica": true,
  "salvataggio": { "attivo": true, "chiave": "auto" },
  "splash": { "attiva": true, "cuore8bit": true } }
```

`characters.json` — N personaggi, nessuno obbligatorio oltre `player`
```json
{ "player": { "sprite": "characters/lei.json", "spawn": [50, 75], "speed": 24 },
  "npcs": [
    { "id": "manu", "sprite": "characters/lui.json", "at": [72, 60],
      "dialogue": "manu_random", "portraitPerFrame": true,
      "obstacle": { "rx": 0.5, "r": 1.7 } },
    { "id": "gatto", "sprite": "characters/gatto.json", "at": [19, 46],
      "clickAnywhere": true, "dialogue": "gatto" } ] }
```

`interactions.json`
```json
[ { "id": "giradischi", "at": [20, 26], "arrive": [20, 34.5], "radius": 5.5,
    "sparkle": true, "counts": true,
    "on": "walk_then_trigger" },
  { "id": "finestra", "hitbox": [[44,14],[62,14],[62,30],[44,30]],
    "sparkle": false, "counts": false, "on": "trigger" } ]
```

`events.json` + `cutscenes.json` + `secrets.json` + `endings.json`: vedi §3
(B, C, D, E). `dialogues.json`:
```json
{ "manu_random": { "mode": "bag", "portrait": "cycle",
    "lines": [ "Ciao amore mio… ti stavo aspettando. ❤", "…" ] },
  "indizio_tv": { "lines": [ { "text": "Film, coperta e divano…", "sfx": "soft" } ] },
  "bivio_esempio": { "lines": [ { "text": "Apro la scatola?",
    "choices": [ { "label": "Sì", "goto": "apri" },
                  { "label": "No", "goto": "aspetta", "if": "!found.lettera" } ] } ] } }
```

Ogni schema ha il suo file in `tools/schemas/` e viene validato al build:
errore chiaro con percorso del campo, non un gioco rotto.

---

## 6. Piano di refactoring (incrementale, mai "big bang")

Il refactoring avviene **a motore funzionante**: ogni fase termina con la
suite Playwright verde sul pack `martina` (il gioco attuale è il golden test).

| Fase | Contenuto | Come |
|------|-----------|------|
| R1 | **Unificare i builder** | `build_rc.py` entra nel repo dentro `tools/sad.py build`; il template smette di vivere nello scratchpad. Da qui il progetto è ricostruibile da zero. |
| R2 | **Estrarre i moduli engine** | Spaccare `stanza.html` in `engine/src/*` + un template HTML minimo; bundle con concatenazione semplice (niente webpack: zero dipendenze). Output identico byte-per-byte al gioco attuale. |
| R3 | **Config → pack** | Migrare CONFIG, COLLIDERS, ASSETS, testi UI, tema nei JSON del pack `martina`. Il motore legge tutto da lì. |
| R4 | **Animation player generico** | Sostituire `DIR_SHEET`/`WALK_SEQ`/`DANCE_SEQ` con gli stati dichiarati nei JSON sprite (§3A). |
| R5 | **Trigger + state bag + save generico** | Sostituire i flag fissi con lo state bag; il salvataggio serializza il bag con versione dello schema. |
| R6 | **Cutscene DSL** | Riscrivere ballo e contratto come `cutscenes.json`; eliminare `scenaBallo/scenaContratto` dal motore. Test: il gioco Martina è indistinguibile da prima. |
| R7 | **Segreti + finali a regole** | Generalizzare achievement e selettore finali (§3D-E). |
| R8 | **Validazione schemi + QA riusabile** | JSON Schema su ogni file; `tools/qa.js` parametrico sul pack (raggiungibilità di TUTTI gli `arrive`, fps, 0 errori JS, finale raggiungibile, segreti sbloccabili). |

Ordine scelto per rischio: prima si mette in sicurezza la build (R1-R2 senza
cambiare comportamento), poi si sposta il contenuto (R3), poi si
generalizzano i sistemi uno alla volta (R4-R7), ciascuno protetto dal golden
test.

## 7. Strategia di automazione

Obiettivo: **nuova avventura in < 1 ora**. La CLI `sad.py` copre l'intero ciclo:

```
sad new  <slug> --template romantica   # scaffolding pack completo
sad art  <slug>                        # scontorno + packing + ritratti (già fatto ✔)
sad music <slug>                       # loop strumentali senza stacco (già fatto ✔)
sad validate <slug>                    # JSON Schema + lint contenuti
sad build <slug>                       # HTML unico in dist/
sad preview <slug>                     # server locale + QR in console
sad qa <slug>                          # Playwright: raggiungibilità, finali, fps
```

| Attività | Oggi | Automatizzata |
|----------|------|---------------|
| Scontorno + packing sprite | script già pronto | `sad art` (riuso `pipeline_sprites.py`) |
| Loop musicale strumentale | procedura già collaudata | `sad music` (RMS scan + crossfade numpy) |
| Ritratti dai sheet | script già pronto | `sad art` |
| Collisioni | disegnate a mano nel codice | **editor in-game**: `?debug` → click sui vertici → esporta `room.json` |
| Dialoghi | scritti nel JSON | import da `.txt`/foglio Google (una battuta per riga) |
| Verifica qualità | test scritti ad hoc | `sad qa` parametrico su ogni pack |
| Consegna | manuale | `sad build` + guida QR in `docs/` |

Tempo di produzione stimato a regime, partendo da un template:
**asset AI 20' + config 20' + QA automatica 5' + build 1' ≈ 45 minuti.**

## 8. Funzionalità future consigliate

1. **Inventario leggero** (raccogli chiave → apre cassetto): già rappresentabile
   con lo state bag + condizioni; serve solo la UI a slot. Sblocca le escape room.
2. **Multi-stanza**: `rooms: []` con porte come interazioni `{ "goto": "salotto" }`.
   L'architettura a pack lo prevede senza cambiare i sistemi.
3. **Foto/video dei clienti nei popup** (già supportato via `file:` in build) +
   audio-messaggi vocali nei dialoghi.
4. **Temi stagionali** (Natale, San Valentino) come overlay di `theme.json`.
5. **Statistiche opzionali** (il cliente vede se il destinatario ha finito il
   gioco): ping a un endpoint solo se `analytics: true`. Rispetto della privacy
   di default.
6. **PWA offline** (manifest già presente nel repo, va solo collegato).
7. **Modalità "diretta"**: link con `?autoplay` che salta la splash per demo
   commerciali.

## 9. Piano prodotto commerciale

**Prodotto = pack + engine buildati in un HTML consegnato con QR.**

- **Listino a 3 livelli**
  1. *Base* (template + testi/nomi/foto del cliente, asset standard) — produzione ~45'
  2. *Personalizzata* (sprite dei veri protagonisti generati con AI + scontorno
     automatico, musica scelta dal cliente) — ~2-3 h
  3. *Su misura* (ambientazione dedicata, cutscene scritte ad hoc, multi-stanza) — giornate
- **Canale**: Instagram @sempreaddue → demo giocabile (`packs/demo`, salvataggio
  disattivato, watermark "@sempreaddue" nel finale — già così) → ordine via
  modulo con upload foto/testi → consegna link + QR stampabile.
- **Editor visuale (fase 2 del business)**: siccome tutto è JSON con schema,
  l'editor è un'app che genera i JSON — form per dialoghi/segreti/finali,
  canvas drag&drop per posizioni e collisioni (riusa la modalità editor
  in-game di §7), upload immagini che innesca `sad art` server-side.
  L'engine è già predisposto: non legge codice, legge dati.
- **Proprietà intellettuale**: engine chiuso e versionato; i pack dei clienti
  sono loro, il motore resta tuo. Ogni HTML riporta engine version nel footer
  commentato (già presente come commento di build).

## 10. Manutenibilità pluriennale

1. **Semver sull'engine** + `manifest.json` del pack dichiara la versione
   richiesta (`"engine": ">=2.1 <3"`). I pack vecchi si ricostruiscono sempre.
2. **Schema versionato nel salvataggio** (`sempreaddue-save-v3` già introdotto:
   la convenzione diventa regola: bump a ogni cambio di schema).
3. **Golden pack**: `packs/martina` è la suite di regressione vivente; `sad qa`
   gira su ogni modifica all'engine (raggiungibilità, finali, fps, 0 errori).
4. **Zero dipendenze runtime** (niente framework JS): il rischio di rottura nel
   tempo è quasi nullo; le dipendenze di build (Pillow, numpy, scipy, ffmpeg)
   sono bloccate in `tools/requirements.txt`.
5. **Documentazione nel repo** (`docs/`): manuale di produzione passo-passo,
   ricette per occasioni, checklist QA (evoluzione di `CHECKLIST-QA.md` e
   `README-PRODUZIONE.md` esistenti).
6. **Pulizia asset**: eliminare i file legacy (C12) e tenere in `_src/` i
   sorgenti grezzi di ogni pack.

---

## Roadmap operativa (per priorità)

| Fase | Obiettivo | Attività principali | Stima | Priorità | Impatto |
|------|-----------|---------------------|-------|----------|---------|
| **F0** | Repo ricostruibile | R1: builder unificato nel repo, template fuori dallo scratchpad, pulizia asset legacy | 2-3 h | 🔴 massima | Elimina il rischio "il progetto vive nella sessione"; base di tutto |
| **F1** | Engine estratto | R2 + R3: moduli engine, pack `martina`, output identico all'attuale | 8-12 h | 🔴 alta | Separazione vera motore/contenuti; golden test |
| **F2** | Sistemi generici | R4-R7: animation player, state bag, cutscene DSL, segreti, finali multipli | 10-14 h | 🔴 alta | Sblocca TUTTE le occasioni (proposta, compleanno, escape) senza codice |
| **F3** | Automazione + QA | R8 + CLI `sad` completa (new/art/music/validate/build/preview/qa) | 6-8 h | 🟠 media-alta | Produzione < 1 h; qualità costante su decine di pack |
| **F4** | Libreria template | 3 template (romantica ✔ da Martina, compleanno, proposta) + docs prezzi | 6-10 h | 🟠 media | Catalogo vendibile; il margine si crea qui |
| **F5** | Editor collisioni in-game | modalità `?editor`: disegno poligoni, spostamento interattivi, export JSON | 4-6 h | 🟡 media-bassa | Taglia la parte più lenta della produzione manuale |
| **F6** | Editor visuale completo | app web che genera i pack (form + canvas + upload) | 3-5 gg | 🟢 bassa (fase 2 business) | No-code: produzione delegabile / self-service |

**Totale per essere "in produzione commerciale" (F0-F4): ~35-45 ore di lavoro.**

### Perché quest'ordine
- F0 prima di tutto: oggi una parte della build vive fuori dal repo — è il
  rischio esistenziale del progetto, e costa solo 2-3 ore.
- F1-F2 sono il prodotto: senza cutscene DSL e segreti/finali generici ogni
  vendita "non romantica" richiede codice nuovo.
- F3-F4 trasformano il prototipo in catena di produzione.
- F5-F6 ottimizzano un processo che a quel punto già funziona e fattura.
