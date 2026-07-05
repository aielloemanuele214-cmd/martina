# Checklist di Validazione — Specifica Ufficiale (v1.0.0-rc3)

Ogni voce è stata verificata automaticamente con Playwright (`test_rc.js`) e/o
visivamente con screenshot. Legenda: ✅ verificato · 👁️ verificato a schermo.

## Indizi e progressione
- ✅ Gli indizi principali sono **3** (vinile, TV, lettera-e-fiori). Il vino è stato rimosso (privo di immagine e non citato nella spec).
- ✅ Solo i 3 indizi principali contano nella progressione (contatore = 3 cuori + eventuale 💛 segreto).
- ✅ Gatto e finestra **non** contano come indizi.
- ✅ Il finale (messaggio "Ad oggi siamo un bellissimo miracolo…") appare quando tutti e 3 gli indizi sono scoperti.

## Scena del ballo (segreto)
- ✅ Parte **solo** se il vinile è l'ultimo indizio principale ancora da scoprire.
- ✅ Se il vinile è scoperto quando mancano ancora altri indizi → popup normale, niente ballo.
- ✅ Gatto e finestra non influenzano questa logica (non sono conteggiati).
- 👁️ Sequenza: blocco input → sfuma musica ambiente → fade al nero → typewriter "Ho una sorpresa per te…".
- ✅ Ballo di durata **15 secondi** (configurabile in `CONFIG.ballo.durata`), nessun input, nessuno skip.
- 👁️ Fine: fade al nero → stop musica → typewriter "Nessuno aveva mai fatto niente di simile per me… / Ti amo." → ritorno al gioco.
- ✅ Non ripetibile (flag `danceDone`, salvato): re-interagendo il vinile appare il popup normale.

## Segreto del contratto
- ✅ Indipendente dalla scena del ballo.
- ✅ Parte **solo** se "Lettera e Fiori" è l'ultimo indizio principale ancora da scoprire.
- 👁️ Sequenza: blocco input → fade al nero → typewriter "C'è qualcosa qui… / Sembra molto importante." → apertura contratto.
- 👁️ Documento elegante, leggibile, **scrollabile**, in sovraimpressione, con testo **identico** alla spec, richiudibile dall'utente.
- ✅ Alla chiusura: ritorno al gioco. Non ripetibile (flag `contractDone`, salvato).

## Gatto (segreto)
- 👁️ Nessuna icona / alone / indicatore / scintilla / suggerimento: appare come semplice elemento decorativo.
- ✅ Al click mostra il messaggio romantico previsto (da qualsiasi distanza).
- ✅ Eccezione: se è la **primissima** interazione della partita → fusa + cuori animati **prima** del messaggio, una sola volta (`purrDone`).
- ✅ Achievement cuore dorato 💛 invariato.

## Lettera e fiori
- ✅ Aperti normalmente mostrano **esclusivamente**: "All'amore della mia vita / Sono immensamente fiero di te. / Tuo, Manu".

## Finestra (segreto)
- 👁️ Nessun indicatore visivo (stesse regole del gatto).
- 👁️ Al click apre il popup con l'immagine dedicata e il messaggio "Questo è un giorno importante…".

## Interazioni di Manu
- ✅ Ampliate (14 frasi) su temi: cura, protezione, orgoglio, sostegno, amore.
- ✅ Spontanee e mai ripetitive: una frase a caso per tocco, sacchetto mescolato senza ripetizioni immediate.

## Popup oggetti
- 👁️ Popup quadrato **1:1** con l'immagine ravvicinata allegata, per ognuno dei 3 indizi.
- ✅ Usate esclusivamente le immagini fornite.

## Audio
- ✅ Rimossi gli effetti dei passi.
- ✅ Effetti di interazione sostituiti con suoni morbidi/romantici (solo timbri sine/triangle, attacco e rilascio dolci).
- ✅ Colonna sonora: **Warm Memories** in gioco, **Paper Lantern Promise** nel menù (crossfade all'ingresso).

## Messaggio finale
- ✅ Sostituito integralmente con "Ad oggi siamo un bellissimo miracolo… / Sei il mio mondo."

## Requisiti tecnici
- 👁️ Transizioni cinematografiche e graduali (fade 1s, typewriter, crossfade audio).
- ✅ Tutti gli eventi segreti eseguibili **una sola volta** (danceDone / contractDone / cat.purrDone, salvati).
- ✅ Nessun input durante gli eventi cinematici (flag `cinematic`).
- ✅ Nessuna regressione: movimento, camera, salvataggio, splash, dialoghi, finale funzionano. 0 errori JS, 61 fps su mobile.
- ✅ Tutti gli asset provengono dagli allegati forniti.

## Note di interpretazione (decisioni prese dove la spec lasciava spazio)
- **Musica dedicata del ballo**: durante i 15s suona il valzer sintetizzato dedicato (l'ambiente è sfumato), poi l'ambiente rientra.
- **Finale dopo gli eventi**: al termine della scena dell'ultimo indizio (ballo o contratto) si mostra il messaggio finale, così è sempre raggiungibile.
- **Movimento**: mantenuto il punta-e-clicca (joystick rimosso su richiesta precedente), coerente con le interazioni a click della spec.
