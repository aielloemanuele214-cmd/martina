# SempreAddue — Modello operativo a figure

> Una sola **figura** per ruolo, altamente specializzata. Ogni figura è un
> **agente/modulo** con una missione, degli strumenti reali e una **lista di
> task**. Quando un aspetto va migliorato non si riorganizza l'azienda: si apre
> la **scheda della figura** che lo possiede e le si aggiunge un task. Il
> miglioramento è chirurgico, tracciabile, reversibile.

## I tre principi

1. **Una figura, un ruolo, un proprietario.** Nessun doppione. Per ogni aspetto
   della produzione esiste una e una sola figura che ne risponde.
2. **Ogni figura lavora su una lista di task.** La scheda non è un profilo: è uno
   strumento vivo con un *backlog* di potenziamenti e correzioni, ordinato per
   priorità, e un *log* di ciò che è già stato fatto.
3. **L'R&D è il motore.** Ogni miglioramento nasce come task nel backlog di *una*
   figura, viene applicato (prompt, rubrica, codice o istruzioni) e registrato
   nel suo log. Vedi [`rnd.md`](rnd.md).

## La catena di produzione (10 figure)

Ogni ordine attraversa queste figure in sequenza. Le tre in **grassetto** sono
i moduli automatizzati.

| # | Figura | Fase | Modulo reale |
|---|--------|------|--------------|
| [01](figure/01-concierge.md) | Order Concierge | Brief | `docs/RISPOSTA-*`, `packs/<slug>/genera.json` |
| [02](figure/02-sceneggiatore.md) | Narrative Designer | Storia | `packs/*/config/story.json` |
| [03](figure/03-art-supervisor.md) | AI Art Supervisor | Prompt | `docs/PROMPT-NANOBANANA.md`, `genera.py` (build_specs) |
| [04](figure/04-generation-lead.md) | **AI Generation Lead** | Generazione | `gioco/tools/genera.py`, `sprites.py` |
| [05](figure/05-qc-engineer.md) | **QC Engineer** | Controllo qualità | `gioco/tools/qc.py` |
| [06](figure/06-engine-developer.md) | Game Engine Developer | Motore | `gioco/engine/src/` |
| [07](figure/07-pipeline-engineer.md) | **Tools & Pipeline Engineer** | Build | `gioco/tools/sad.py`, `collmask.py` |
| [08](figure/08-audio-designer.md) | Audio Designer | Musica | `gioco/tools/music.py` |
| [09](figure/09-delivery-infra.md) | Delivery / Infra | Consegna | `sad.py consegna`, Cloudflare, `_redirects` |
| [10](figure/10-art-director.md) | Art Director | Validazione estetica | Style Bible, checklist |

Trasversale a tutte: **R&D** — non una fase, ma il processo che alimenta le
liste di task. → [`rnd.md`](rnd.md).

> 📖 Per il dettaglio di **come ogni figura agisce e si sincronizza** con le
> altre (passaggi a valle, loop di ritorno, contratti d'interfaccia, R&D
> trasversale): **[`SINCRONIZZAZIONE.md`](SINCRONIZZAZIONE.md)**.
>
> 🤖 Ogni figura tende a diventare un **agente addestrabile per direttive** (si
> migliora modificando un testo versionato, non riscrivendo codice): il modello
> definitivo è in **[`AGENTI.md`](AGENTI.md)**. Primo agente vivo: il QC, con la
> direttiva editabile in `gioco/tools/agenti/qc-agente.md`.

## Come si legge (e si usa) una scheda

Ogni scheda segue [`figure/_TEMPLATE.md`](figure/_TEMPLATE.md):

- **Mandato** — di cosa risponde questa figura (proprietà unica).
- **Istruzioni operative** — come lavora: input → lavorazione → output.
- **Interfacce** — da chi riceve, a chi consegna, quali strumenti possiede.
- **Metriche** — come si misura se sta migliorando.
- **Lista task** — il backlog di potenziamenti/correzioni, per priorità.
- **Log** — cosa è già stato cambiato, con data.

### Per migliorare qualcosa
1. Individua **quale figura** possiede l'aspetto (tabella qui sopra).
2. Apri la sua scheda e aggiungi un task in **Lista task** (usa la sigla `R&D-…`).
3. Applica il potenziamento/correzione al suo modulo reale.
4. Spunta il task e annota il **Log** con la data.

Un aspetto = una figura = un punto di intervento. Niente riunioni, niente
riorganizzazioni: si potenzia la singola figura.
