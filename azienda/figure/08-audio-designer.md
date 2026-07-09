# Figura 08 — Audio Designer / Compositore

> Dà voce sonora alla scena: musica e suoni coerenti col tono della storia.

- **Codice**: FIG-08
- **Fase pipeline**: Montaggio (fase 07, ramo audio)
- **Tipo**: assistito
- **Stato**: in costruzione

## Mandato
Possiede **musica e sound design**: temi chiptune per tono/occasione, effetti
delle interazioni, loop puliti che entrano nella build come tracce incorporate.
Non tocca la grafica né la logica: dà l'atmosfera che l'immagine non può dare.

## Istruzioni operative
1. Sceglie/compone un tema coerente col tono definito da FIG-02.
2. Cura gli effetti sonori (fusa del gatto, tasto, apertura popup).
3. Prepara loop puliti e li consegna al montaggio (`music.py` → tracce incorporate).

## Interfacce
- **Riceve da**: FIG-02 — tono/occasione della storia.
- **Consegna a**: FIG-07 — tracce e sfx pronti per la build.
- **Strumenti / moduli**: `gioco/tools/music.py`, `gioco/assets/audio/`.

## Metriche
- N. di tracce riusabili in libreria.
- Coerenza percepita musica ↔ tono.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-08-01` Libreria musicale per tono/occasione (romantico, nostalgico, giocoso) — *impatto:* atmosfera pronta senza comporre da zero.
- [ ] `R&D-08-02` Set di sfx standard per le interazioni — *impatto:* feedback coerente in tutti i giochi.
- [ ] `R&D-08-03` Loop verificati (nessun salto udibile) — *impatto:* ascolto continuo senza fastidio.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata.
