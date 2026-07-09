# Figura 04 — AI Generation Lead

> Produce gli asset grezzi con la massima coerenza al minor costo. **Modulo automatizzato.**

- **Codice**: FIG-04
- **Fase pipeline**: Generazione (fase 05)
- **Tipo**: modulo automatizzato
- **Stato**: attivo

## Mandato
Possiede la **pipeline di generazione**: chiamate al modello immagine, coerenza
reference-first, scontorno chroma e impacchettamento in sprite. Ogni immagine è
tracciata nel registro consumi. Non decide i prompt (FIG-03) né promuove gli
asset (FIG-05): *esegue e consegna materiale grezzo pulito*.

## Istruzioni operative
1. Riceve le specifiche prompt e genera stanza (2 frame), personaggi, animazioni, popup, maschera.
2. Passa i fogli nella pipeline di scontorno (verde/nero auto-detect) e li segmenta in celle.
3. Impacchetta a larghezza uniforme, allineamento ai piedi.
4. Annota costo e n. immagini nel registro `gemini-usage.tsv`.

## Interfacce
- **Riceve da**: FIG-03 — specifiche prompt.
- **Consegna a**: FIG-05 (QC) — asset grezzi; a FIG-07 — sprite impacchettati.
- **Strumenti / moduli**: `gioco/tools/genera.py`, `gioco/tools/sprites.py`, `~/.config/sempreaddue/gemini-usage.tsv`.

## Metriche
- Costo di generazione per ordine (€).
- % di asset promossi al primo colpo dal QC.
- Tentativi medi per asset.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-04-01` Il **ballo** esce a volte a 4 pose invece di 5 → stabilizzare il prompt a 5 pose ben separate — *impatto:* animazione della coppia piena.
- [ ] `R&D-04-02` Il **gatto** talvolta esce a griglia 2×2 → rinforzare a monte «una sola riga» (oggi mitigato dalla segmentazione di FIG-07) — *impatto:* nessun rischio di doppioni.
- [ ] `R&D-04-03` Ridurre i tentativi medi affinando i reference — *impatto:* meno costo per ordine.
- [ ] `R&D-04-04` Cache dei personaggi coerenti tra fogli (riuso del reference) — *impatto:* coerenza + risparmio.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata. Attivi: auto-detect chroma verde/nero, reference-first, registro consumi.
