# Figura 03 — AI Art Supervisor / Prompt Lead

> Traduce il brief in prompt standardizzati e garantisce la coerenza del personaggio.

- **Codice**: FIG-03
- **Fase pipeline**: Prompt (fase 04)
- **Tipo**: assistito (umano + `build_specs`)
- **Stato**: attivo

## Mandato
Possiede il **linguaggio dei prompt**: come si descrive un ambiente, un
personaggio, una maschera. Sceglie modello e parametri, imposta il metodo
reference-first per la coerenza. Non genera (FIG-04) e non giudica (FIG-05):
decide *cosa chiedere e come chiederlo*.

## Istruzioni operative
1. Dal brief costruisce le specifiche prompt (`build_specs`): personaggi, stanza,
   frame animato, popup, maschera di collisione.
2. Applica gli standard: chroma verde, misure uniche, `NOLIVING` per gli sfondi,
   una riga di N figure per i fogli sprite.
3. Imposta il riferimento (il primo foglio del protagonista) per la coerenza.
4. Definisce quando scalare al modello **pro** per un asset difficile.

## Interfacce
- **Riceve da**: FIG-01 (brief) e FIG-02 (oggetti-indizio).
- **Consegna a**: FIG-04 — specifiche prompt pronte.
- **Strumenti / moduli**: `docs/PROMPT-NANOBANANA.md`, `docs/STANDARD-PRODUZIONE.md`, `gioco/tools/genera.py` (`build_specs`).

## Metriche
- Tentativi medi per asset (meno = prompt più efficaci).
- Coerenza del personaggio tra i fogli.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-03-01` Libreria di prompt «ambienti» oltre l'attico (salotto, spiaggia, montagna, cucina) — *impatto:* più occasioni servibili.
- [ ] `R&D-03-02` Regola d'escalation flash→pro documentata per tipo asset — *impatto:* costo/qualità prevedibile.
- [ ] `R&D-03-03` Palette per occasione/stagione agganciata allo Style Bible — *impatto:* coerenza col brand.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata. Standard attivi: chroma verde, `NOLIVING`, foglio a una riga.
