# SEMPREADDUE — Istruzioni ufficiali del gioco per la generazione asset

> 📐 Misure, chroma e layout autorevoli in **`STANDARD-PRODUZIONE.md`**.
> Terminologia: **protagonista** (giocabile) · **secondario** (NPC). Fondo di
> ritaglio: **verde #00FF00** (le stanze no: piena scena).

### Documento da integrare al PROMPT MASTER · v1.0 (motore 1.3.x)

> **Regola di precedenza:** in caso di conflitto tra il PROMPT MASTER e questo
> documento, **vale questo documento**: descrive i formati che il motore usa
> davvero. Un asset fuori standard non è utilizzabile.

---

## 1. Che cos'è il gioco

SempreAddue produce **mini avventure grafiche personalizzate in pixel art**,
consegnate come singolo file HTML giocabile da telefono (link + QR). Ogni
avventura si svolge in **una stanza** vista dall'alto in 3/4 (stile Stardew
Valley / SNES) e racconta la storia di una coppia attraverso oggetti,
dialoghi e segreti.

### Come si gioca (flusso del giocatore)
1. **Splash di ingresso**: cuore 8-bit, titolo, musica del menù. Due tocchi
   per entrare (il primo sblocca l'audio).
2. **Punta-e-clicca**: si tocca un punto della stanza e la protagonista ci
   cammina (pathfinding con collisioni sui mobili). Su desktop anche WASD.
3. **3 indizi principali**, segnalati da una ✨ discreta che pulsa. Toccarne
   uno fa camminare la protagonista fin lì e apre un **popup quadrato 1:1**
   con un'immagine ravvicinata dell'oggetto + un testo personale. Ogni indizio
   trovato accende un ❤️ nel contatore in alto a sinistra.
4. **L'altro protagonista (NPC)** sta in piedi nella stanza: a ogni tocco dice
   una frase personale diversa (mai la stessa due volte di fila) e cambia
   espressione nel ritratto del dialogo.
5. **Segreti** (nessun indicatore, nessuna icona — vanno scoperti):
   l'animale domestico (messaggio poetico + achievement 💛), la finestra
   (popup con immagine dedicata), e i due **eventi cinematografici**.
6. **Eventi cinematografici** (una sola volta per partita): quando un indizio
   "speciale" è l'ULTIMO ancora da scoprire, invece del popup parte una scena:
   - **il ballo**: fade al nero → testo a macchina da scrivere → la coppia
     balla un lento abbracciata (musica dedicata, cuoricini) → dedica finale;
   - **il documento**: fade al nero → testo → si apre un documento elegante
     scorrevole (contratto scherzoso / buono regalo / proposta di matrimonio,
     dipende dall'occasione).
7. **Finale**: trovati tutti e 3 gli indizi appare la dedica finale, con il
   contatore "INSIEME DA X GIORNI ❤" e il contatore "SEGRETI X/4".
   Bottoni: *Resta qui* e *Ricomincia l'avventura* (azzera tutto).

### L'universo grafico "SempreAddue"
Pixel art 16-bit disegnata a mano, atmosfera calda e notturna, luci di
candele, dettagli minuti ovunque, palette armoniosa sui toni caldi con
accenti freddi (notte fuori dalla finestra). Romantico senza essere
zuccheroso. Qualità premium: ogni elemento sembra dello stesso mondo.

---

## 2. Il mondo tecnico (vincoli non negoziabili)

- La stanza è **quadrata**, coordinate interne in % (0–100, origine in alto
  a sinistra). Il **muro di fondo occupa il ~25% superiore**; il resto è
  pavimento calpestabile con i mobili.
- I personaggi in scena sono alti **~25% del lato stanza**. **Lui è
  pochissimo più alto di lei** (lei ≈ 95% dell'altezza di lui).
- Vista 3/4 dall'alto: si vedono la facciata E il piano superiore dei mobili.
  Prospettiva identica per tutti gli elementi.
- Il giocatore cammina "dietro" ad alcuni mobili (diventa semitrasparente):
  serve spazio di passaggio visivamente sensato attorno agli oggetti
  interattivi. **Ogni oggetto interattivo deve essere raggiungibile a piedi.**
- Il gioco gira a 60fps su smartphone: gli asset vengono ridimensionati e
  compressi in automatico dalla pipeline — la pulizia conta più della
  risoluzione.

---

## 3. SPECIFICHE ASSET (sostituiscono la sezione OUTPUT del prompt master)

### Regole globali per OGNI foglio sprite
- **Sfondo VERDE CHROMA PIENO (#00FF00)** — niente trasparenza, niente scacchiera
  (vera o disegnata), niente glow/alone/sfumatura attorno alle figure.
  Il verde è lontano da pelle/capelli/vestiti: il ritaglio è pulito anche sui toni scuri. Lo scontorno lo fa la pipeline automatica.
- Frame **in fila orizzontale, equidistanti**, stessa scala in ogni frame,
  personaggio centrato, **piedi sempre visibili** e appoggiati alla stessa
  linea di terra.
- Nessun frame deve toccare o invadere quello accanto (lasciare aria).
- Ombreggiatura, spessore linee e livello di dettaglio identici tra tutti
  i fogli dello stesso progetto.
- Dimensione sorgente consigliata: **1536×1024** per i fogli personaggio,
  **1254×1254 o più** per la stanza.

### 3.1 PROTAGONISTA — personaggio giocabile · 4 fogli (uno per direzione)
Un foglio per ciascuna vista: **fronte, destra, schiena, sinistra**
(niente specchiature: la sinistra va disegnata, non riflessa).
Ogni foglio contiene **4 frame, in quest'ordine**:

| # | Frame | Note |
|---|-------|------|
| 1 | **Idle** | in piedi, rilassata (il "respiro" lo anima il motore) |
| 2 | **Passo A** | gamba destra avanti, ciclo di camminata |
| 3 | **Passo B** | gamba sinistra avanti (il motore alterna A-idle-B-idle) |
| 4 | **Interazione** | si china / allunga una mano verso un oggetto |

### 3.2 SECONDARIO — NPC (secondo personaggio) · 1 foglio
Il secondario **non cammina**: sta in piedi nella stanza. Un solo foglio frontale con
**5 frame emotivi, in quest'ordine**:

1. **Idle** (sorriso rilassato) · 2. **Imbarazzo** (mano dietro la nuca)
· 3. **Parla** (gesto con la mano) · 4. **Pensa** (mano al mento)
· 5. **Braccia conserte** (sorriso divertito)

I ritratti dei dialoghi vengono ritagliati automaticamente da questi frame:
il viso deve essere curato ed espressivo.

### 3.3 COPPIA CHE BALLA · 1 foglio
**5 pose** dei due protagonisti **abbracciati che ballano un lento**
(il motore le riproduce avanti-e-indietro: 1→2→3→4→5→4→3→2).
Le pose devono concatenarsi con movimenti piccoli e romantici — è un lento,
non un ballo di coppia acrobatico. Proporzioni coerenti coi fogli singoli.

### 3.4 ANIMALE DOMESTICO (se richiesto) · 1 foglio
**2 frame**: dorme · sveglio (testa alzata). Posato a terra o su un mobile.

### 3.5 AMBIENTAZIONE · 2 immagini quadrate identiche tranne l'animazione
- **Frame 1**: la stanza completa.
- **Frame 2**: identico al pixel, **cambiano SOLO gli elementi animati**
  (2–4, scelti per contesto: catalogo in `STANDARD-PRODUZIONE.md §6`). Il motore alterna
  i due frame con ritmo irregolare: l'effetto deve essere discreto e in
  loop perfetto.
- La stanza deve contenere, ben visibili e separati tra loro:
  i **3 oggetti indizio**, la **postazione dell'NPC**, il punto
  dell'**animale**, una **finestra** (o apertura) col mondo di fuori,
  e uno spazio libero centrale per la scena del ballo.
- Ricca di dettagli ma leggibile: gli oggetti interattivi devono "chiamare
  lo sguardo" senza frecce né etichette.

### 3.6 POPUP DEGLI INDIZI · 3 immagini quadrate 1:1
Per ogni oggetto indizio, un'illustrazione **ravvicinata** dell'oggetto nello
stesso stile pixel art (l'oggetto come lo si vedrebbe da vicino, con
atmosfera). Formato quadrato, nessun testo dentro l'immagine.
Una quarta immagine per il segreto della **finestra** (il panorama/momento
che si vede fuori).

### 3.7 Consegna — nomi dei file
```
protagonista_sheet.png  4 direzioni × 4 frame (un file per direzione va bene:
                  protagonista_fronte / _destra / _schiena / _sinistra)
secondario_sheet.png    5 frame emotivi
ballo_sheet.png   5 pose di coppia
gatto_sheet.png   2 frame (se previsto)
stanza_bg.png     frame 1 ambientazione
stanza_bg2.png    frame 2 (solo elementi animati diversi)
pop_<id1>.png     popup indizio 1  (id = nome oggetto, es. pop_vinile)
pop_<id2>.png     popup indizio 2
pop_<id3>.png     popup indizio 3
pop_finestra.png  popup del segreto finestra
```

---

## 4. Che fine fanno gli asset (perché le regole contano)

La pipeline automatica (`sad art`) prende i fogli su fondo verde chroma e:
scontorna il verde chroma collegato al bordo (tutto il resto resta opaco), impacchetta i frame in celle a larghezza garantita,
allinea i piedi, genera i ritratti dai frame di lui, comprime tutto dentro
un unico HTML. Le collisioni dei mobili si disegnano in gioco (`?editor`).

Conseguenze pratiche:
- capelli/vestiti **scuri sono al sicuro** (il verde è lontano dai loro toni),
  ma il fondo deve essere **verde chroma #00FF00 uniforme**;
- ogni sporco tra i frame (frammenti, puntini, pezzi del frame vicino)
  finisce nel gioco: i fogli devono essere puliti;
- se i frame non sono equidistanti o i piedi non sono sulla stessa linea,
  l'animazione "salta".

---

## 5. CONTROLLO QUALITÀ (da verificare prima di consegnare)

- [ ] Tutti i fogli su **fondo verde chroma #00FF00**, zero trasparenze/scacchiere/glow
- [ ] Frame equidistanti, stessa scala, piedi sulla stessa linea di terra
- [ ] Protagonista: 4 direzioni × 4 frame nell'ordine idle/passoA/passoB/interazione
- [ ] Secondario: 5 frame emotivi nell'ordine indicato, viso curato (diventa ritratto)
- [ ] Ballo: 5 pose concatenabili avanti-e-indietro, proporzioni coerenti
- [ ] Secondario poco più alto del protagonista (se previsto dalla coppia), in TUTTI i fogli (ballo compreso)
- [ ] Stanza: 2 frame identici tranne gli elementi animati; loop discreto
- [ ] 3 oggetti indizio + NPC + animale + finestra visibili, separati,
      raggiungibili a piedi; spazio libero per il ballo
- [ ] Popup 1:1 ravvicinati, stesso stile, nessun testo nell'immagine
- [ ] Palette, luce, spessore linee e dettaglio uniformi su TUTTO il set
- [ ] Nomi dei file come da §3.7

---

## 6. Le 7 domande del PROMPT MASTER

Restano valide e vanno fatte PRIMA di generare (ambientazione, protagonisti,
tono, 3 oggetti, segreti, elementi obbligatori, vincoli di colore).
Aggiungine una: **"C'è un animale domestico? Che animale è?"**
Le risposte determinano i contenuti; questo documento determina i formati.
