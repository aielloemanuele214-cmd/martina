# Standard di produzione SempreAddue — misure, chroma, layout

Fonte unica di verità per generare gli asset di ogni ordine in modo
**coerente, veloce e già ottimizzato**. Prompt operativi in
`PROMPT-NANOBANANA.md`; specifiche di dettaglio in `GENERAZIONE-ASSET.md`.

---

## 1. Terminologia (vale per tutto il progetto)
- **protagonista** = il personaggio **giocabile** (cammina, 4 direzioni × 4
  frame). È chi riceve il regalo. Neutro: può essere lei, lui, chiunque.
- **secondario** = l'**NPC fermo** (5 frame emotivi, non cammina).
- Niente più "lei/lui" nei nomi file, config, prompt e documenti.

## 2. Sfondo di generazione: CHROMA KEY VERDE
- Personaggi e oggetti da ritagliare → **fondo verde acceso puro `#00FF00`**,
  pieno e uniforme. Niente trasparenza, niente sfumature, niente ombre verdi.
  Il verde è lontano da pelle/capelli/vestiti → ritaglio pulito anche sui
  toni scuri (col nero erano il caso critico). La pipeline `sad art`
  riconosce il verde da sola.
- **Gli SFONDI (stanze) NON usano il chroma**: sono immagini a piena scena,
  non si ritagliano. Vanno generati come illustrazione completa.

## 3. Misure uniche (profilo "leggero", ottimizzato mobile)
| Asset | Dimensione | Note |
|---|---|---|
| **Stanza** (sfondo) | **1024 × 1024** px, quadrata | muro di fondo in alto ~20-25% |
| **Frame personaggio** (protagonista/secondario) | generare **512 × 512** per frame su verde, soggetto centrato, **piedi sulla stessa linea di base** | la pipeline ritaglia e impacchetta; altezza a schermo = **25% della stanza** |
| **Foglio** (in fila) | frame equidistanti, stessa scala | 4 frame (protagonista/vista), 5 (secondario, ballo) |
| **Popup indizio** | **512 × 512** px, quadrato | primo piano dell'oggetto, nessun testo |
| **Coordinate di gioco** | percentuali **0–100**, origine in alto a sx | il motore lavora in %, non in px |

Peso gioco atteso: ~3 MB (file unico autocontenuto). Regola: **la pulizia
conta più della risoluzione** — la pipeline comprime comunque.

## 4. STAGE STANDARD — layout unico condiviso (il cuore dell'ottimizzazione)

Tutti gli ordini della stessa famiglia riusano **lo stesso scheletro
spaziale**: collisioni, punti d'arrivo e spawn sono **già validati** (QA verde
sul pack `martina`). Si cambia solo l'ARTE; **le collisioni non si ricalibrano
mai a mano** → fluidità garantita, produzione più veloce.

Posizioni-slot (in % `x,y`) che l'immagine della stanza deve rispettare:

| Slot | Oggetto @ | Il giocatore arriva @ | Zona schermo |
|---|---|---|---|
| **Indizio A** | 20, 26 | 20, 34.5 | parete sinistra, in alto |
| **Indizio B** | 79, 38 | 78, 50 | parete/mobile a destra |
| **Indizio C** | 31, 79 | 41, 70 | mobile in basso a sinistra |
| **Secondario (NPC)** | 72, 60 | — (sta fermo) | centro-destra |
| **Animale** (se c'è) | 19, 46 | — | sinistra, a terra |
| **Finestra** (segreto) | parte alta | — | sul muro di fondo |
| **Zona ballo / libera** | ~50, 55 | — | centro, sgombra |
| **Spawn protagonista** | 50, 75 | — | centro-basso |

**Regole di disposizione per la fluidità** (già rispettate dallo stage):
- Ogni oggetto interattivo ha **spazio calpestabile davanti** (il punto
  d'arrivo) e non è incastrato in un angolo.
- Lo **spawn** e la **zona centrale** restano **sgombri** (serve spazio per il
  ballo e per non nascere dentro un mobile).
- Oggetti **ben distanziati** tra loro → il pathfinding non si incastra.
- Il muro di fondo (alto ~20-25%) non è calpestabile: gli oggetti-indizio
  stanno sul pavimento o su mobili raggiungibili.

Chi disegna la stanza deve solo **mettere i 3 oggetti-indizio, l'NPC,
l'animale e la finestra nelle zone qui sopra**: il resto (collisioni,
arrivi, spawn) è già pronto in `room.json` + `interactions.json`.

## 5. Nuove ambientazioni (oltre lo stage standard)
Se un'occasione richiede una stanza con disposizione diversa (es.
`ultima-orbita`), si crea un **nuovo stage** una volta sola: si disegna la
stanza, si calibrano collisioni e arrivi con l'editor in-gioco (`?editor`,
vedi `README-PRODUZIONE.md`) e si salva il nuovo `room.json`. Da lì diventa
un altro layout riutilizzabile — non si ricalibra a ogni ordine.

## 6. Ambiente vivo — il SECONDO frame della stanza (obbligatorio)

Ogni stanza va consegnata in **due frame** (`stanza_bg` + `stanza_bg2`). Il
motore li alterna con un ritmo irregolare (sfarfallio tipo candela) e
l'ambiente prende vita. Regole:

- **Frame 2 = Frame 1 identico pixel per pixel, TRANNE gli elementi animati.**
  Se cambia qualcos'altro (mobili, luci statiche, prospettiva) la stanza
  "vibra". Perciò il Frame 2 si genera **partendo dal Frame 1** (in Nano Banana:
  passa il Frame 1 come immagine input e chiedi di cambiare *solo* quegli
  elementi).
- **Scegli 2–4 elementi animati coerenti col contesto** e tienili **discreti**
  (piccole differenze: una fiamma che si piega, un riflesso che scivola).

**Catalogo — cosa animare per contesto:**
| Contesto | Elementi animati (Frame 2) |
|---|---|
| Fuoco / calore | fiamme di candele, camino, lanterne, braci: la fiamma si piega/oscilla, il bagliore pulsa |
| Acqua | mare, lago, piscina, fontana, pioggia sul vetro: increspature, riflessi che scivolano, gocce |
| Vento / aria | tende, piante, alberi, erba, capelli, bucato, bandiere: leggera oscillazione |
| Luce / tech | TV/schermo/monitor, insegne, lucine, giradischi: bagliore che sfarfalla, disco che gira |
| Cielo / notte | stelle che brillano, luna, aurora, lucciole, neve/foglie che scendono fuori dalla finestra |
| Fantasy / magia | scintille sospese, rune luminose, pozione che ribolle, cristalli che pulsano |

Il resto della scena (mobili, pareti, oggetti-indizio) resta **congelato**.

## 7. Checklist di conformità (prima di `sad art`)
- [ ] Personaggi/oggetti su **verde `#00FF00`** pieno; stanze a piena scena
- [ ] Stanza 1024², popup 512², frame generati 512² su verde
- [ ] Piedi dei personaggi sulla **stessa linea di base**, frame equidistanti
- [ ] I 3 indizi, NPC, animale e finestra nelle **zone dello stage standard**
- [ ] **Frame 2 vivo**: identico al Frame 1 tranne 2–4 elementi animati coerenti col contesto
- [ ] Stesso personaggio (viso/vestito/capelli) su TUTTI i fogli
- [ ] Nomi file: `protagonista_*`, `secondario_*` (vedi `GENERAZIONE-ASSET.md`)
