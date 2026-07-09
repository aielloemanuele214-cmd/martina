# SempreAddue — Manuale di sincronizzazione delle figure

> Come lavorano insieme le 10 figure della catena di produzione: **cosa fa** ognuna,
> **come agisce** (in chiaro + dettaglio tecnico) e **come si sincronizza** con le
> altre — passaggi a valle, loop di ritorno, contratti d'interfaccia e come l'R&D
> attraversa tutto. È il manuale operativo: se hai un dubbio su «chi fa cosa e come
> arriva alla prossima», la risposta è qui.

## Come leggere questo documento

Ogni figura ha tre blocchi: **Cosa fa** · **Come agisce** (una sintesi + il
dettaglio tecnico con i file/dati reali) · **Come si sincronizza**. Nei passaggi:

- **⬇ Riceve** — cosa arriva, da chi, e il **contratto d'ingresso** (cosa è garantito).
- **⬆ Consegna** — cosa produce, a chi, e il **contratto d'uscita** (cosa garantisce).
- **↩ Loop** — i rimbalzi all'indietro quando qualcosa non va.

Un **contratto** è la promessa di un passaggio: se è rispettato, la figura a valle
può lavorare senza sapere *come* è stato prodotto l'input. È ciò che rende le
figure intercambiabili e migliorabili una alla volta.

---

## Mappa d'insieme

```
                              CLIENTE
                                 │  richiesta + materiali + foto
                                 ▼
   ┌─────────────────────  FIG-01 CONCIERGE  ─────────────────────┐
   │ brief genera.json + tono + occasione + consenso privacy       │
   ▼                                                               ▼
FIG-02 SCENEGGIATORE                                     FIG-03 ART SUPERVISOR
   │  storia/dialoghi/finali        oggetti-indizio ─────►│  specifiche prompt
   │                                                       ▼
   │                                              FIG-04 GENERATION ◄────┐
   │                                                 │  asset grezzo      │ correzione
   │                                                 ▼                    │ (rientra nel prompt)
   │                                              FIG-05 QC ──────────────┘ (boccia)
   │                                                 │  asset promossi
   │            sprite impacchettati ────────────────┤
   ▼                                                 ▼
   └───────────────────────────►  FIG-07 PIPELINE  ◄──── FIG-06 ENGINE (motore versionato)
                        audio ────►     │  build validata + QA 13/13   ◄── FIG-08 AUDIO
                                        ▼
                                 FIG-10 ART DIRECTOR ──(rework)──► a monte (03/04/05/07)
                                        │  ok estetico
                                        ▼
                                 FIG-09 DELIVERY ──(link + QR, 200)──► CLIENTE
                                        │
   FIG-01 ◄──(feedback / richiesta di ritocco)──────────────────────────┘

   R&D  ═══════ trasversale a tutte ═══════
   ogni miglioramento diventa UN task nella scheda della figura proprietaria.
```

---

## FIG-01 — Order Concierge

**Cosa fa.** È l'unica figura che parla col cliente prima della produzione:
trasforma un ricordo in un **brief senza ambiguità** e apre la commessa.

**Come agisce.**
- *In chiaro:* intervista guidata (nomi, occasione, tono, ricordi, stanza, foto,
  messaggio), traduce i ricordi in requisiti, fa preventivo e conferma pagamento.
- *Dettaglio tecnico:* compila `gioco/packs/<slug>/genera.json`
  (`protagonista`, `secondario`, `animale`, `stanza`, `oggetti[]`, `animati`) e i
  dati d'ordine in `gioco/clienti/<slug>.json`; usa `docs/RISPOSTA-PREVENTIVO.md`
  e `docs/RISPOSTA-FOUNDER.md`.

**Come si sincronizza.**
- ⬇ **Riceve** dal *cliente*: richiesta + materiali + foto. *Contratto:* consenso
  privacy raccolto prima di procedere.
- ⬆ **Consegna** a **FIG-02** e **FIG-03**: «**Brief confermato**» =
  `genera.json` completo + occasione + tono. *Contratto:* tutti i campi
  obbligatori presenti e validati (nessuna decisione lasciata implicita).
- ↩ **Loop:** riceve da **FIG-09/Support** le richieste di **ritocco** post-consegna
  e le re-immette come mini-brief.

---

## FIG-02 — Narrative Designer / Sceneggiatore

**Cosa fa.** Dà alla coppia una **storia** che emoziona, montata su template
riusabili invece che scritta da zero.

**Come agisce.**
- *In chiaro:* sceglie il template per occasione, innesta nomi/ricordi/oggetti,
  scrive dialoghi e finale nel tono richiesto.
- *Dettaglio tecnico:* produce `packs/<slug>/config/story.json`, `dialogues.json`,
  `endings.json`, `cutscenes.json`; la lista degli **oggetti-indizio** è la stessa
  che serve a FIG-03 per i popup.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-01**: brief + tono + occasione. *Contratto:* occasione e
  tono espliciti (guidano la scelta del template).
- ⬆ **Consegna** a **FIG-07**: «**Storia**» = i file di config narrativi; e a
  **FIG-03**: la **lista oggetti-indizio**. *Contratto:* 3 oggetti-indizio
  coerenti con la storia, un finale, dialoghi nel tono.
- ↩ **Loop:** se FIG-03/04 non riescono a rendere un oggetto-indizio, torna qui per
  sostituirlo con uno equivalente.

---

## FIG-03 — AI Art Supervisor / Prompt Lead

**Cosa fa.** Traduce il brief in **prompt standardizzati** e garantisce la
coerenza del personaggio. Decide *cosa chiedere e come chiederlo*.

**Come agisce.**
- *In chiaro:* costruisce le specifiche di ogni asset (personaggi, stanza, frame
  animato, popup, maschera), applica gli standard e imposta il riferimento per la
  coerenza.
- *Dettaglio tecnico:* `build_specs()` in `gioco/tools/genera.py` — ogni spec porta
  `kind`, `aspect`, il prompt, **e la rubrica QC** (`qckind`, `qcfmt`); standard
  attivi: chroma verde, `NOLIVING` sugli sfondi, foglio a una riga di N figure,
  reference-first (il `protagonista_down` fa da riferimento agli altri).

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-01** (brief) e **FIG-02** (oggetti-indizio). *Contratto:*
  brief validato + lista indizi.
- ⬆ **Consegna** a **FIG-04**: «**Specifiche prompt**» = la lista di spec.
  *Contratto:* **ogni asset ha una rubrica QC associata** (nessun asset senza
  giudice) e un riferimento per la coerenza.
- ↩ **Loop:** se **FIG-05** boccia sistematicamente un tipo di asset, o **FIG-10**
  segnala un problema estetico ricorrente, il prompt/standard si corregge qui.

---

## FIG-04 — AI Generation Lead  · *modulo automatizzato*

**Cosa fa.** Produce gli **asset grezzi** con la massima coerenza al minor costo,
tracciando ogni immagine.

**Come agisce.**
- *In chiaro:* genera stanza (2 frame), personaggi, animazioni, popup e maschera;
  li scontorna dal chroma e li impacchetta in sprite; annota costo e n. immagini.
- *Dettaglio tecnico:* `gen()`/`gen_qc()` in `genera.py` chiamano il modello
  immagine; `sprites.py` fa scontorno (auto-detect verde/nero), `cells_grid` la
  segmentazione, `pack()` l'impacchettamento; ogni immagine è annotata in
  `~/.config/sempreaddue/gemini-usage.tsv`.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-03**: specifiche prompt. *Contratto:* ogni spec ha rubrica
  e riferimento.
- ⬆ **Consegna** a **FIG-05**: «**Asset grezzo**» (PNG normalizzato) per il
  giudizio; e a **FIG-07**: «**Sprite impacchettato**» (foglio a N celle, `fw/fh/n`).
  *Contratto:* PNG su chroma o piena scena; sprite con `celle-che-toccano-il-bordo = 0`.
- ↩ **Loop:** **FIG-05** boccia → la **correzione** rientra nel prompt e FIG-04
  **rigenera** (fino a N tentativi, ultimo col modello pro). È il loop più caldo
  della catena.

---

## FIG-05 — QC Engineer (giudice visivo)  · *modulo automatizzato*

**Cosa fa.** È l'unica figura che può **bocciare** un asset: nessuno entra nella
build se non è corretto tecnicamente **ed** esteticamente.

**Come agisce.**
- *In chiaro:* un modello con visione ispeziona ogni asset contro una rubrica
  severa e restituisce esito, difetti e una correzione; guida il ciclo
  genera→giudica→rigenera.
- *Dettaglio tecnico:* `judge(kind, img)` in `gioco/tools/qc.py` ritorna
  `{ok, difetti[], correzione}` (JSON strutturato); rubriche per `room`,
  `room_anim`, `sheet`, `mask`, `popup`. Su `ok:false` la `correzione` viene
  appesa al prompt del tentativo successivo.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-04**: asset grezzo. *Contratto:* un asset per giudizio, del
  tipo dichiarato.
- ⬆ **Consegna** a **FIG-07**: «**Asset promosso**» (`ok:true`); a **FIG-10**: le
  **segnalazioni** rimaste imperfette dopo i tentativi. *Contratto:* ciò che passa
  ha superato la rubrica del suo tipo.
- ↩ **Loop:** rimanda a **FIG-04** (rigenera con la correzione); se il difetto è nel
  *modo di chiedere*, il task sale a **FIG-03**.

---

## FIG-06 — Game Engine Developer  · *codice versionato*

**Cosa fa.** Mantiene il **motore** che fa muovere, animare e vivere la scena —
uguale per tutti, mai toccato per un cliente.

**Come agisce.**
- *In chiaro:* fornisce le capacità (rendering, collisioni, pathfinding, mirroring,
  stati) che i dati del pack usano per prendere vita.
- *Dettaglio tecnico:* `gioco/engine/src/*` (es. `31-collisioni.js` legge
  `ROOM.walk`; `51-render.js` fa il mirroring sinistra=destra riflessa); è
  data-driven, versionato in `engine/CHANGELOG.md`.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-07**: i dati del pack, al momento della build. *Contratto:*
  config conformi agli schemi.
- ⬆ **Consegna** a **FIG-07**: «**Motore versionato**». *Contratto:* API/formati
  stabili e retro-compatibili coi pack esistenti (una modifica non deve rompere i
  giochi già consegnati).
- ↩ **Loop:** se la **QA di FIG-07** trova un errore JS o un comportamento errato
  imputabile al motore, il bug torna qui.

---

## FIG-07 — Tools & Pipeline Engineer  · *modulo automatizzato*

**Cosa fa.** Monta gli asset in un **gioco affidabile**: collisioni,
posizionamenti validati, cablaggio, build e QA. È l'ultimo anello automatico.

**Come agisce.**
- *In chiaro:* dalla maschera ricava il pavimento calpestabile, piazza
  personaggi/indizi **validandoli sul motore**, cabla sprite e manifest, costruisce
  l'HTML e lancia la QA.
- *Dettaglio tecnico:* `collmask.derive()` (fascia-muro forzata, pavimento connesso
  allo spawn), `engine_reachable()` valida ogni posizione col pathfinding del
  motore; `sprites.cells_grid` gestisce griglia multi-riga e sovra-split;
  `sad.py build-base` assembla; `qa.js` esegue le 13 verifiche.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-05** (asset promossi), **FIG-04** (sprite), **FIG-06**
  (motore), **FIG-08** (audio). *Contratto:* asset che hanno passato il QC + motore
  stabile.
- ⬆ **Consegna** a **FIG-10** e **FIG-09**: «**Build validata**» = HTML autonomo +
  report QA. *Contratto:* **0 errori JS, tutti gli interattivi raggiungibili,
  ≥50 fps** (QA 13/13); posizioni validate sul motore.
- ↩ **Loop:** se la QA fallisce, indirizza il difetto alla figura giusta —
  **FIG-06** (motore), **FIG-04** (asset), o si corregge qui (placement/collisioni).

---

## FIG-08 — Audio Designer / Compositore

**Cosa fa.** Dà **atmosfera sonora**: musica e suoni coerenti col tono della storia.

**Come agisce.**
- *In chiaro:* sceglie/compone un tema chiptune per il tono, cura gli sfx delle
  interazioni, prepara loop puliti.
- *Dettaglio tecnico:* `gioco/tools/music.py` → tracce in `gioco/assets/audio/`,
  incorporate nella build come base64.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-02**: tono/occasione. *Contratto:* tono esplicito.
- ⬆ **Consegna** a **FIG-07**: «**Tracce audio**» (musica + sfx). *Contratto:* loop
  puliti (nessun salto udibile), formati incorporabili.
- ↩ **Loop:** se **FIG-10** giudica la musica fuori tono, torna qui.

---

## FIG-09 — Delivery / Infra Engineer  · *modulo automatizzato*

**Cosa fa.** Porta il gioco al cliente con un **link privato e permanente**, fuori
dai riflettori, e ne cura l'infrastruttura.

**Come agisce.**
- *In chiaro:* pubblica su hosting dedicato a un link segreto, genera il QR, fa il
  backup e verifica che il link risponda.
- *Dettaglio tecnico:* `sad.py consegna` copia la build in
  `sempreaddue-giochi/g/<token>.html`, deploy su Cloudflare Pages
  (`sempreaddue-giochi.pages.dev/g/<token>`), backup nella repo privata; i giochi
  non stanno mai nella repo pubblica.

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-07** (build) e **FIG-10** (ok estetico). *Contratto:* build
  QA-verde + via libera estetica.
- ⬆ **Consegna** al *cliente*: «**Consegna**» = link + QR. *Contratto:* link
  verificato (**HTTP 200**), token non indovinabile, backup effettuato.
- ↩ **Loop:** raccoglie feedback/reclami e li gira a **FIG-01** come richieste di
  ritocco.

---

## FIG-10 — Art Director (validazione estetica)

**Cosa fa.** L'**ultimo sì umano**: «è degno di essere regalato?». Custode del DNA
visivo, chiude il ciclo dopo il QC automatico.

**Come agisce.**
- *In chiaro:* riceve la build e le segnalazioni, passa la checklist estetica,
  approva o rimanda un task a monte.
- *Dettaglio tecnico:* usa lo Style Bible (`docs/STANDARD-PRODUZIONE.md`) e una
  checklist di validazione; coglie ciò che la rubrica non misura (emozione, gusto,
  coerenza col brand).

**Come si sincronizza.**
- ⬇ **Riceve** da **FIG-07** (build) e **FIG-05** (segnalazioni imperfette).
  *Contratto:* build QA-verde.
- ⬆ **Consegna** a **FIG-09**: «**OK estetico**» = via libera. *Contratto:*
  checklist superata.
- ↩ **Loop:** se non approva, apre un **rework** verso la figura proprietaria del
  difetto (di solito **FIG-03** prompt, **FIG-04** generazione o **FIG-05** rubrica).

---

## Contratti d'interfaccia — tabella unica

Ogni riga è una promessa: input garantito → output garantito. Se un contratto è
rispettato, la figura a valle non deve sapere *come* è stato prodotto l'input.

| Passaggio | Artefatto | Contratto (cosa è garantito) |
|---|---|---|
| Cliente → 01 | Richiesta + foto | Consenso privacy raccolto |
| 01 → 02 / 03 | Brief confermato | `genera.json` completo, campi validati, tono+occasione |
| 02 → 03 | Oggetti-indizio | 3 indizi coerenti con la storia |
| 02 → 07 | Storia | dialoghi + finale nel tono, config conformi |
| 03 → 04 | Specifiche prompt | ogni asset ha **rubrica QC** + riferimento coerenza |
| 04 → 05 | Asset grezzo | PNG normalizzato, tipo dichiarato |
| 04 → 07 | Sprite impacchettato | N celle, `celle-che-toccano-il-bordo = 0` |
| 05 → 07 | Asset promosso | ha superato la rubrica del suo tipo (`ok:true`) |
| 06 → 07 | Motore versionato | API stabili, retro-compatibile coi pack |
| 08 → 07 | Tracce audio | loop puliti, incorporabili |
| 07 → 10 / 09 | Build validata | 0 errori JS, interattivi raggiungibili, ≥50 fps |
| 10 → 09 | OK estetico | checklist superata |
| 09 → Cliente | Consegna | link **200**, token segreto, backup fatto |

---

## Loop di ritorno — la mappa dei rimbalzi

I passaggi a valle costruiscono; i loop di ritorno **proteggono la qualità**.

1. **QC ↩ Generazione** (05→04) — automatico e continuo: ogni bocciatura rientra
   come correzione nel prompt del tentativo dopo. È il loop che rende la build
   corretta senza intervento umano.
2. **QC ↩ Prompt** (05→03) — quando un *tipo* di asset viene bocciato in modo
   ricorrente: non è l'immagine, è il modo di chiederla → si corregge lo standard.
3. **QA ↩ Motore / Asset** (07→06 / 07→04) — se una build non passa le 13 verifiche,
   il difetto va alla figura giusta (bug del motore vs asset da rifare).
4. **Art Director ↩ a monte** (10→03/04/05/07) — l'occhio umano rimanda un rework
   quando l'estetica non convince, anche se il QC automatico era passato.
5. **Cliente ↩ Concierge** (09→01) — feedback e ritocchi rientrano come mini-brief
   e ripercorrono la catena.

Regola d'oro: **un rimbalzo diventa sempre un task nella scheda della figura
proprietaria** (vedi sotto), così il problema non si ripete al prossimo ordine.

---

## R&D trasversale — come un miglioramento attraversa le figure

L'R&D non è una fase: è il modo in cui la catena impara. Un miglioramento non si
spalma su tutti — si deposita su **una** figura.

**Il ciclo (da `rnd.md`):**
1. Emerge un aspetto da migliorare (feedback, difetto in QA, idea, costo).
2. Si individua **la figura proprietaria** (una sola).
3. Si scrive un **task** nella sua Lista task (`R&D-<NN>-<n>`), con l'impatto.
4. Si applica al suo modulo reale (prompt, rubrica, codice, istruzioni).
5. Si registra nel suo **Log**. Il task si chiude.

**Esempi reali, già mappati sulle schede:**

| Aspetto emerso | Figura proprietaria | Task |
|---|---|---|
| Il ballo esce a 4 pose invece di 5 | FIG-04 Generation | `R&D-04-01` |
| Popup «sufficienti» da rifare con la rubrica nuova | FIG-05 QC | `R&D-05-01` |
| File troppo pesante (7,8 MB) | FIG-07 Pipeline | `R&D-07-01` |
| Serve profondità «dietro i mobili» | FIG-06 Engine | `R&D-06-01` |
| Link brandizzato `gioca.sempreaddue.it` | FIG-09 Delivery | `R&D-09-01` |
| Manca la checklist estetica scritta | FIG-10 Art Director | `R&D-10-01` |

I task **esplorativi** (voce, foto→sprite, clip social, AR) vivono nel backlog
R&D finché non maturano: allora diventano un task di una figura esistente o fanno
nascere una figura nuova.

---

## In una frase

La catena **costruisce** a valle con contratti chiari; i **loop di ritorno**
proteggono la qualità; l'**R&D** trasforma ogni problema in un task su una singola
figura. Così ogni aspetto ha un proprietario, un modo di agire e un punto di
sincronizzazione — e si migliora una figura alla volta.
