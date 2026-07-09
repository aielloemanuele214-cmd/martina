# SempreAddue — Il modello degli agenti (definitivo)

> Ogni figura tende a diventare un **agente**: un lavoratore specializzato guidato
> da una **direttiva editabile**, non da codice da riscrivere. Addestrarlo
> significa cambiare la sua direttiva — versionata in git, reversibile,
> economica. Questo è il modello che rende SempreAddue **premium e sostenibile a
> lungo termine**: la qualità si alza modificando testo, non rifacendo software.

## Cos'è un agente, qui

Un agente SempreAddue è fatto di cinque parti, tutte già presenti nella
scheda-figura (`figure/NN-*.md`):

| Parte | Dove vive | È il... |
|---|---|---|
| **Direttiva** | *Istruzioni operative* / file-spec | system prompt: chi è e come ragiona |
| **Criteri** | rubriche / *contratti d'interfaccia* | metro di giudizio e promesse verso le altre figure |
| **Strumenti** | i moduli reali del repo | ciò che sa fare (generare, giudicare, costruire) |
| **Modello** | la spec dell'agente | il "motore cognitivo" (es. `gemini-2.5-flash`) |
| **Memoria** | *Lista task* + *Log* | cosa deve migliorare e cosa ha già imparato |

Un agente è definito quando queste cinque parti stanno in **un unico posto
editabile**. Vedi l'esempio vivo: [`../gioco/tools/agenti/qc-agente.md`](../gioco/tools/agenti/qc-agente.md).

## Le tre nature (stato reale, oggi)

Non tutte le figure sono già agenti. Onestà prima di tutto:

- 🟢 **Agente AI** — guidato da modello + direttiva: **Concierge (01)**,
  **Sceneggiatore (02)**, **Generation (04)**, **QC (05)**.
- ⚙️🟢 **Deterministico ma addestrabile per direttive** — assembla in modo
  costante, ma il suo DNA vive in una spec editabile: **Art Supervisor (03)**.
  Non tutto ciò che è addestrabile deve essere un LLM: qui la *coerenza* dei
  prompt è ciò che rende affidabile la produzione, quindi si tiene il
  determinismo e si rende editabile la direttiva.
- ⚙️ **Codice deterministico** — esegue regole, non "ragiona": **Engine (06)**,
  **Pipeline (07)**.
- 👤 **Umano / checklist** — per ora presidiato da persone: **Audio (08)**,
  **Art Director (10)**, **Delivery (09)** (la relazione col cliente resta umana).

L'architettura è fatta perché ognuna possa **diventare** un agente quando ha
senso: la scheda è già la sua specifica.

## Come si addestra un agente — per direttive (il metodo del 95%)

Niente re-training dei pesi. Si agisce su cinque leve, tutte testuali:

1. **Direttiva** — cambi chi è e come giudica/agisce.
2. **Criteri** — aggiungi o allenti una regola.
3. **Esempi** — casi-oro (few-shot) positivi/negativi.
4. **Modello** — scegli un motore più capace dove serve.
5. **Memoria** — chiudi task nel Log: l'agente non ripete gli stessi errori.

### Esempio reale, verificato
Il QC ha la direttiva e i criteri nel file [`qc-agente.md`](../gioco/tools/agenti/qc-agente.md).
Aggiungendo una sola regola («boccia se nella stanza c'è un televisore»), **sulla
stessa immagine** il verdetto è passato da *OK* a *BOCCIATO — «Televisore presente
nell'angolo in basso a destra»*. Nessun codice toccato: solo la direttiva. Questo
è «addestrare con nuove direttive».

## Fine-tuning dei pesi — l'opzione avanzata (raramente serve)

Riaddestrare davvero il modello su un dataset proprietario. Costa dati, tempo e
denaro; si giustifica solo per uno stile/giudizio molto specifico e stabile. È
competenza della figura **Research/ML** (area R&D). Regola pratica: si prova
*prima* per direttive + esempi; il fine-tuning è l'ultima risorsa, non la prima.

## Governance & sostenibilità (perché regge nel tempo)

- **Un'unica fonte di verità** per agente: la sua spec. Niente deriva tra
  documentazione e comportamento.
- **Ogni addestramento è un commit**: `git log` sulla spec = lo storico di come
  l'agente è stato educato. Reversibile con un `revert`.
- **Mai un pass silenzioso**: se un agente-giudice non è disponibile (errore API),
  ritenta con backoff e, se proprio non può giudicare, **segnala per revisione
  umana** invece di promuovere al buio. La qualità non dipende dalla fortuna.
- **Costi tracciati**: ogni giudizio/generazione è annotato nel registro consumi.
- **Modello economico di default, pro solo dove serve**: si scala il motore per
  eccezione, non per abitudine.

## Come aggiungere (o «accendere») un agente

1. Parti dalla sua scheda-figura: hai già mandato, interfacce e task.
2. Crea la sua **spec** in `gioco/tools/agenti/<figura>-agente.md` con le sezioni
   `MODELLO`, `DIRETTIVA`, e i `CRITERIO …` che gli servono.
3. Fai in modo che il suo modulo **carichi la spec** (come `qc.py` fa con
   `_load_agent()`), con i valori interni solo come rete di sicurezza.
4. Verifica che il comportamento resti identico, poi addestralo cambiando la spec.

## Roadmap — le prossime figure a diventare agenti

In ordine di valore/fattibilità:

1. ✅ **Concierge (01)** — *acceso*: dall'intervista scrive il brief `genera.json`
   (`sad concierge <slug>`). Direttiva in `agenti/concierge-agente.md`.
2. ✅ **Sceneggiatore (02)** — *acceso*: dai ricordi scrive battute, indizi e
   finale (`sad sceneggiatore <slug>`). Direttiva in `agenti/sceneggiatore-agente.md`.
3. **Art Director (10)** — agente di validazione estetica: una seconda opinione
   sopra il QC tecnico. Direttiva = lo Style Bible reso operativo.
4. **Delivery (09)** e **Audio (08)** — quando la relazione/infra saranno pronte
   a essere guidate da direttiva.

Ognuna nasce come oggi il QC: una spec editabile, un loader, e da lì si addestra
per direttive.

## In una frase

Ogni figura è (o diventa) un **agente addestrabile per direttive**: si migliora
modificando un testo versionato, non riscrivendo software — e nessun giudizio
passa mai al buio. È così che un atelier resta artigianale nel gusto e
industriale, e sostenibile, nella resa.
