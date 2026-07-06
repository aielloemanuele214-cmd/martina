# Engine — changelog

## 1.4.0 (nuove meccaniche additive per pack diversi — es. "L'Ultima Orbita")
Tutte le aggiunte sono **opzionali e attivate dalla config del pack**: se un
pack non le usa, il comportamento è identico alla 1.3.0 (martina: QA 13/13).
- **Asset per-pack**: `manifest.assets` mappa i nomi asset ai file dentro
  `packs/<slug>/assets/`, sovrascrivendo i default globali. sprites.json può
  dichiarare `embed` (asset '@'), `portraitsNpc` (ritratti dell'NPC) e
  `musiche`. Il motore non ha più grafica cablata a un solo pack.
- **Finestra opzionale**: la finestra-segreto si disattiva con
  `finestra.attiva:false` e la sua zona è configurabile (`finestra.zona`).
- **Gatto a rivelazione per vicinanza**: `gatto.rivelaVicino` (raggio) —
  il gatto compare (fade) e diventa cliccabile solo avvicinandosi.
- **Trigger a inattività** (`CONFIG.stella`): resta fermi in una zona per N
  secondi → evento. Passo scena `stella` = scia luminosa (stella cadente).
- **Punti segreti invisibili** (`CONFIG.puntiSegreti`): hotspot a tocco
  diretto che lanciano un evento (es. l'abbraccio vicino alla porta).
- `closeDialog` verifica il finale: un'interazione conclusa da un dialogo può
  completare la missione (no-op sui pack che concludono già via popup/scena).

## 1.3.0 (F5 — editor di produzione in-gioco)
- Modalità `?editor`: disegno di poligoni di collisione a tocchi (chiudi/
  annulla vertice), spostamento dei marker degli indizi (oggetto ● e punto
  d'arrivo ○), eliminazione collider al tocco, export JSON pronto da
  incollare in room.json / interactions.json. WASD attivo per testare
  subito i percorsi. `prepColliders()` + `buildGrid()` rieseguiti a ogni
  modifica: le hitbox nuove valgono immediatamente.
- Inattivo e invisibile nelle copie consegnate (nessun peso a runtime).
- QA 13/13 invariata in modalità normale.

## 1.2.0 (F2 — sistemi generici: il motore è un interprete)
- **State bag**: tutto lo stato di partita è un sacchetto di flag con chiavi
  decise dal pack ('trovato.vinile', 'segreto.gatto', 'fatto.ballo'…);
  salvataggio v4 = serializzazione del sacchetto. Ricomincia lo azzera intero.
- **Eventi dichiarativi** (STORY.eventi): quando/se/fai/altrimenti con
  condizioni ('!x', 'trovato.*', all/any, 'prima_interazione') e azioni
  (set, sorpresa, popup, dialogo, scena, sfx, vibra, cuori, verso, se annidato).
- **Cutscene DSL** (STORY.scene): scene a passi — inizio, nero, scrivi,
  attesa, coppia, synth, documento, posiziona, musica, fine. Ballo, contratto
  e fusa del gatto sono ora DATI del pack, non funzioni del motore.
- **Animazioni data-driven**: stati del giocatore (idle/walk/interact) e
  sequenza del ballo dichiarati in sprites.json (seq, dur, bob); altezze in
  scena per foglio. Rimossi WALK_SEQ/DANCE_SEQ/DIR_SHEET dal motore.
- **Segreti generici** (STORY.segreti): flag + eventuale ricompensa HUD;
  contatore del finale calcolato dalla lista.
- **Finali a regole** (STORY.finali): la prima condizione vera sceglie il
  finale → finali multipli/nascosti pronti senza codice.
- **Dialoghi dichiarati** (STORY.dialoghi): modo "sacchetto" (mai due volte
  la stessa battuta di fila) o righe fisse; riferimenti '$config' e '@asset'.
- Golden test: comportamento identico alla 1.1.0 (indizi, gatto con fusa,
  finestra, ballo lento 0.9s/frame, contratto, finale 3/4 segreti,
  Ricomincia, salvataggio-roundtrip, 61 fps, 0 errori JS).

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
