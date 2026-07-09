# Figura 01 — Order Concierge

> Trasforma un ricordo del cliente in un brief di produzione completo e senza ambiguità.

- **Codice**: FIG-01
- **Fase pipeline**: Brief (fase 01–02)
- **Tipo**: 🟢 **agente AI** (dall'intervista al brief) + relazione umana
- **Stato**: attivo · addestrabile per direttive
- **Cervello (direttiva editabile)**: `gioco/tools/agenti/concierge-agente.md` → modello [`AGENTI.md`](../AGENTI.md)

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

L'**agente** automatizza il passo 2–3: legge `packs/<slug>/intervista.json|txt` e
scrive un `genera.json` valido con `python3 tools/sad.py concierge <slug>`. La
relazione col cliente (passi 1 e 4) resta umana.

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
- 2026-07-09 — **Acceso come agente**: `tools/concierge.py` + direttiva editabile `agenti/concierge-agente.md`; CLI `sad concierge <slug>`. Dall'intervista scrive un `genera.json` valido (3 oggetti-indizio dai ricordi reali); non scrive mai un brief incompleto (valida + ritenta + segnala). Chiude `R&D-01-01` (modulo d'intervista) e `R&D-01-02` (validatore brief).
