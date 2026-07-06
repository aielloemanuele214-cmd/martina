# Engine — changelog

## 1.1.0 (F1 — engine a moduli + pack)
- Il monolite `stanza_template.html` è stato spaccato in 17 moduli ordinati
  in `engine/src/` (css, markup, audio, motore, collisioni, stato, camera,
  tocco, percorso, cinematica, dialoghi, finale, update, render, loop).
- TUTTO il contenuto è migrato in `packs/martina/config/*.json`:
  settings, characters, dialogues, interactions, cutscenes, endings,
  room (colliders + bounds + zona dietro-letto), sprites (dimensioni fogli).
- Il motore non contiene più coordinate della stanza: `blocked()` legge i
  limiti da `ROOM.bounds`; `COLLIDERS`/`BEHIND_BED` arrivano da room.json.
- `tools/sad.py build-base [pack]` assembla moduli + pack + asset base64.
- Golden test: suite Playwright completa identica alla v1.0.0-rc5
  (P1-P5, raggiungibilità, finale, Ricomincia, 61 fps, 0 errori JS).

## 1.0.0-rc5
- Ultima versione monolitica (stanza.html unico file sorgente).
