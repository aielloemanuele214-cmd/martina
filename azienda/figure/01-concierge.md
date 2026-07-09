# Figura 01 — Order Concierge

> Trasforma un ricordo del cliente in un brief di produzione completo e senza ambiguità.

- **Codice**: FIG-01
- **Fase pipeline**: Brief (fase 01–02)
- **Tipo**: assistito (umano + modulo di raccolta)
- **Stato**: attivo

## Mandato
È l'unica figura che parla col committente prima della produzione. Possiede
l'**intake** (intervista, dati di personalizzazione, consenso privacy delle foto)
e la **commessa** (preventivo, codice founder, conferma). Consegna un brief
pronto: nessuna decisione creativa o tecnica resta implicita.

## Istruzioni operative
1. Intervista guidata: **nomi** (protagonista/secondario), **occasione**, **tono**,
   **ricordi/oggetti**, **stanza**, **foto**, **messaggio finale**.
2. Traduce i ricordi in requisiti concreti (oggetti-indizio, ambientazione, dialoghi chiave).
3. Compila il brief `packs/<slug>/genera.json` e valida che i campi obbligatori ci siano.
4. Gestisce preventivo, codice founder e conferma di pagamento; apre la commessa.

## Interfacce
- **Riceve da**: cliente — richiesta e materiali.
- **Consegna a**: FIG-02 (storia) e FIG-03 (prompt) — brief + tono + occasione.
- **Strumenti / moduli**: `docs/RISPOSTA-PREVENTIVO.md`, `docs/RISPOSTA-FOUNDER.md`,
  `gioco/packs/<slug>/genera.json`, `gioco/clienti/`.

## Metriche
- Completezza del brief al primo giro (niente richiami).
- Tempo di intake dall'ordine confermato.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-01-01` Modulo d'intervista standard (questionario guidato per occasione) — *impatto:* brief completi, meno rimbalzi.
- [ ] `R&D-01-02` Validatore automatico di `genera.json` (campi obbligatori, coerenza) — *impatto:* niente ordini che si bloccano in produzione.
- [ ] `R&D-01-03` Mappa «occasione → template narrativo» condivisa con FIG-02 — *impatto:* handoff netto verso la storia.
- [ ] `R&D-01-04` Raccolta strutturata del consenso privacy sulle foto — *impatto:* conformità e fiducia.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata.
