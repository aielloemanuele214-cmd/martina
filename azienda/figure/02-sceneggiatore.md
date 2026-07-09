# Figura 02 — Narrative Designer / Sceneggiatore

> Dà alla coppia una storia che commuove, costruita su template solidi e riusabili.

- **Codice**: FIG-02
- **Fase pipeline**: Storia (fase 03)
- **Tipo**: 🟢 **agente AI** (dai ricordi al copione)
- **Stato**: attivo · addestrabile per direttive
- **Cervello (direttiva editabile)**: `gioco/tools/agenti/sceneggiatore-agente.md` → modello [`AGENTI.md`](../AGENTI.md)

## Mandato
Possiede la **struttura narrativa**: archi emotivi, dialoghi, indizi, finali.
Adatta un template al brief del cliente senza riscrivere da zero. Non decide
l'estetica (FIG-03/10) né la tecnica (FIG-06): decide *cosa si racconta e come si sente*.

## Istruzioni operative
1. Sceglie il template per **occasione** (anniversario, proposta, compleanno, scuse, «ti va di…»).
2. Innesta i dati del brief: nomi, ricordi, oggetti-indizio, messaggio finale.
3. Scrive/rifinisce dialoghi e finale nel tono richiesto (giocoso, romantico, nostalgico).
4. Consegna i file di storia pronti per il montaggio.

## Interfacce
- **Riceve da**: FIG-01 — brief, tono, occasione.
- **Consegna a**: FIG-07 (build) — storia/dialoghi/finali; a FIG-03 — lista oggetti-indizio.
- **Strumenti / moduli**: `gioco/packs/*/config/story.json`, `dialogues.json`, `endings.json`, `cutscenes.json`.

## Metriche
- Quota di storie **riusate da template** vs scritte da zero.
- Reazione emotiva (feedback/recensioni sulla storia).

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-02-04` Ordinare gli oggetti-indizio per il ruolo-slot (1° = canzone/ballo, 3° = lettera/finale) così l'evento del template combacia col significato — *impatto:* la cutscene finale scatta sull'oggetto giusto.
- [ ] `R&D-02-01` Libreria di template narrativi per occasione — *impatto:* consegne più rapide e coerenti.
- [ ] `R&D-02-03` Varianti di finale (aperto, dichiarazione, sorpresa) — *impatto:* stessa storia, chiusure diverse.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata.
- 2026-07-09 — **Acceso come agente**: `tools/sceneggiatore.py` + direttiva editabile `agenti/sceneggiatore-agente.md`; CLI `sad sceneggiatore <slug>`. Dai ricordi (+ i 3 oggetti del brief) scrive battute, indizi, gatto, finestra e finale e li incastra in `dialogues/interactions/endings.json` senza toccare la logica di `story.json`; non scrive mai un copione incompleto. Chiude `R&D-02-02` (tono applicato ai dialoghi).
