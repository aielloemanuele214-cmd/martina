# Figura 10 — Art Director (validazione estetica finale)

> L'ultimo sì umano: «è degno di essere regalato?». Custode del DNA visivo.

- **Codice**: FIG-10
- **Fase pipeline**: Validazione estetica (fase 08)
- **Tipo**: 🟢 **agente AI** (validazione estetica olistica) + supervisione umana
- **Stato**: attivo · addestrabile per direttive
- **Cervello (direttiva editabile)**: `gioco/tools/agenti/art-director-agente.md` → modello [`AGENTI.md`](../AGENTI.md)

## Mandato
Possiede lo **Style Bible** e la **validazione finale**: dà l'ultimo sì estetico
prima della consegna e definisce cosa significhi «premium» per SempreAddue. È la
figura umana che chiude il ciclo dopo il QC automatico (FIG-05): coglie ciò che
la rubrica non misura — emozione, gusto, coerenza col brand.

## Istruzioni operative
1. Riceve la build e le eventuali segnalazioni «imperfette» del QC.
2. Passa la checklist estetica: coerenza col DNA 16-bit, atmosfera, leggibilità, emozione.
3. Approva, oppure rimanda un task alla figura proprietaria (di solito FIG-03/04/05).
4. Aggiorna lo Style Bible quando emerge un nuovo standard.

## Interfacce
- **Riceve da**: FIG-07 (build) e FIG-05 (segnalazioni).
- **Consegna a**: FIG-09 — via libera alla consegna; oppure rimanda task a monte.
- **Strumenti / moduli**: `docs/STANDARD-PRODUZIONE.md` (Style Bible), checklist di validazione.

## Metriche
- % consegne approvate al primo giro.
- Reclami estetici post-consegna (devono tendere a zero).

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-10-04` Passare all'agente anche il conteggio esatto degli oggetti-indizio previsti (oltre al cast) — *impatto:* coglie anche popup/indizi mancanti o doppi.
- [ ] `R&D-10-03` Campionatura periodica delle consegne per aggiornare lo Style Bible — *impatto:* il gusto evolve col brand.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata.
- 2026-07-09 — **Acceso come agente**: `tools/art_director.py` + `scena_shot.js` + direttiva editabile `agenti/art-director-agente.md`; CLI `sad direttore <slug>`. Costruisce/fotografa la scena composita e la giudica in modo olistico («degna di essere regalata?»), indicando la figura da rilavorare. Chiude `R&D-10-01` (checklist) e `R&D-10-02` (criterio «degno di essere regalato»).
- 2026-07-09 — Robustezza: **fallback di modello** (se il modello primario è in avaria passa a quello di riserva) + retry; su indisponibilità totale segnala, non approva al buio.
- 2026-07-09 — Corretto un limite trovato con un test negativo: riceve il **cast atteso** dal pack, così riconosce un doppione (es. due gatti) come difetto e non come «stanza accogliente». Verificato: scena a 1 gatto approvata, scena a 2 gatti bocciata → rework «pipeline».
