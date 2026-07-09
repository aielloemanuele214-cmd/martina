# Figura 06 — Game Engine Developer

> Il motore che fa muovere, animare e vivere la scena, uguale per tutti e mai toccato per un cliente.

- **Codice**: FIG-06
- **Fase pipeline**: Motore (trasversale, usato in fase 07)
- **Tipo**: codice versionato
- **Stato**: attivo

## Mandato
Possiede il **motore** (`engine/`): rendering su canvas, macchina a stati dei
personaggi, collisioni pixel-accurate, pathfinding, mirroring, effetti. È
data-driven: il comportamento del gioco arriva dai pack, il motore resta unico e
versionato. Non genera contenuti: fornisce le **capacità** con cui i contenuti prendono vita.

## Istruzioni operative
1. Legge i dati del pack (config, room, sprites, story) e li rende giocabili.
2. Mantiene le collisioni dalla griglia `ROOM.walk`, il mirroring (sinistra = destra riflessa), la FSM (idle/walk/interact/dance).
3. Aggiunge nuove meccaniche/effetti senza rompere i pack esistenti.
4. Ogni modifica è coperta dalla QA automatica (13 verifiche) di FIG-07.

## Interfacce
- **Riceve da**: FIG-07 — i dati del pack, in build.
- **Consegna a**: il giocatore — l'esperienza in scena.
- **Strumenti / moduli**: `gioco/engine/src/*` (es. `31-collisioni.js`, `51-render.js`), `engine/CHANGELOG.md`.

## Metriche
- fps su mobile, zero errori JS.
- Bug per release; regressioni sui pack storici.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-06-01` **Layer di profondità** «dietro i mobili» (oggi `dietroLetto` è vuoto) per far passare il personaggio dietro gli arredi — *impatto:* profondità estetica della scena.
- [ ] `R&D-06-02` Animazione **ballo a 5 pose** quando disponibili (oggi si adatta a 4) — *impatto:* danza più fluida.
- [ ] `R&D-06-03` Ombra morbida sotto i personaggi — *impatto:* radicamento visivo, meno «figure che fluttuano».

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata. Attivi: collisioni da maschera (`ROOM.walk`), mirroring intelligente.
