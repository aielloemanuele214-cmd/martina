# Figura 07 — Tools & Pipeline Engineer

> Monta gli asset in un gioco affidabile: collisioni, posizionamenti validati, build, QA. **Modulo automatizzato.**

- **Codice**: FIG-07
- **Fase pipeline**: Montaggio & build (fase 07)
- **Tipo**: modulo automatizzato
- **Stato**: attivo

## Mandato
Possiede la **CLI di produzione** e la **preparazione dei dati del pack**: dalla
maschera ricava la griglia di calpestabilità, piazza personaggi e indizi
validandoli sul modello di pathfinding del motore, cabla sprite/manifest,
costruisce il file HTML e lancia la QA. È l'ultimo anello automatico prima
dell'occhio umano.

## Istruzioni operative
1. Deriva le collisioni dalla maschera (fascia-muro forzata, solo pavimento connesso allo spawn).
2. Piazza spawn/NPC/gatto/indizi solo nel corpo navigabile, **validati** con `engine_reachable`.
3. Cabla `sprites.json`/`manifest.json`; segmenta i fogli (griglia multi-riga → prima riga; sovra-split → varchi maggiori).
4. Costruisce la build e lancia la QA (13 verifiche); segnala gli scarti.

## Interfacce
- **Riceve da**: FIG-05 (asset promossi) e FIG-06 (motore).
- **Consegna a**: FIG-10 (validazione) e FIG-09 (consegna) — la build giocabile.
- **Strumenti / moduli**: `gioco/tools/sad.py`, `gioco/tools/collmask.py`, `gioco/tools/sprites.py`, `gioco/tools/qa.js`.

## Metriche
- Peso del file consegnato (MB).
- Tempo di build; QA verde al primo colpo.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-07-01` **Compressione asset** (JPEG per stanze/popup, PNG solo dove serve alpha) per portare il file da ~7,8 MB a 3–4 MB — *impatto:* consegna più leggera e veloce.
- [ ] `R&D-07-02` `wall_top` adattivo se la stanza ha soffitto molto basso/alto — *impatto:* meno pavimento sprecato in stanze inusuali.
- [ ] `R&D-07-03` Report di build unico (peso, QA, costi, QC) per ogni ordine — *impatto:* tracciabilità della commessa.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata. Attivi: `engine_reachable` (posizionamenti validati sul motore), segmentazione griglia/sovra-split, conversione centro-cella.
