# Sempreaddue · "Una stanza tutta per voi" — Roadmap verso la Gold

## Stato attuale: v1.0.0-rc1 — ~95% verso la 1.0

Decisioni prese: splash d'ingresso ✅ · musica nuova pronta (default off,
si accende dal CONFIG per il tier Plus) ✅ · demo pubblica nel repo ✅ ·
fallback Safari ✅. **Per la Gold mancano solo: QA su iPhone reale
(CHECKLIST-QA.md) + un ordine pilota end-to-end.**

| Area | Stato | Note |
|---|---|---|
| Core gameplay | ✅ ~100% | Movimento 8 direzioni, 4 direzioni animate con sprite reali, collisioni ellittiche verificate con BFS, camera adattiva, joystick fisso, 60fps misurati |
| Contenuti | ✅ ~95% | 4 sorprese + segreta del gatto 💛, scena ballo, scena fuochi, dialoghi con ritratto, lettera a macchina da scrivere, finale con contatore giorni |
| Tecnica | 🟡 ~90% | File autonomo ~1.6MB, salvataggio progressi, SFX + valzer diegetico, anteprima WhatsApp. **Mai testato su iPhone/Safari reale** |
| Produzione | 🟡 ~80% | Builder (`build.py` + `clienti/*.json`) e guida operativi; manca un ordine pilota end-to-end e una demo vetrina |

## Storico versioni

- **0.1–0.3** — prototipo CSS + porting a canvas con sprite PNG
- **0.5** — fix touch mobile, joystick fisso, sfondo animato a 2 frame
- **0.7** — cache pre-scalate (60fps), scena ballo, dialoghi con ritratto
- **0.8** — scena fuochi, lettera animata, contatore giorni, builder
- **0.9** — hitbox definitive (corpo ellittico + BFS), camminata frontale,
  gatto magico con sorpresa segreta
- **1.0.0-rc1** — splash "tocca per entrare" (unlock audio iOS), nuovo loop
  musicale caldo (84bpm, default off), fallback visualViewport per Safari,
  demo pubblica (`clienti/demo.json`), checklist QA ← **siamo qui**

## Verso la 1.0 Gold — lavori ordinati per rischio

1. **QA su dispositivi reali** *(rischio tecnico più alto)*
   - iOS Safari: sblocco audio, viewport/safe-area, fullscreen, joystick
   - checklist di test da 10 minuti da eseguire su ogni device disponibile
2. **Schermata d'ingresso** *(decisione aperta)*
   - splash "Una stanza tutta per voi — tocca per entrare" coi nomi della coppia
   - risolve strutturalmente l'unlock audio iOS + primo impatto brandizzato
3. **Musica di sottofondo definitiva** *(decisione aperta)*
   - nuovo loop caldo (non chiptune squillante) — default o solo tier Plus
4. **Ordine pilota completo**
   - JSON cliente → `build.py` → verifica → Netlify Drop → QR → consegna
   - cronometrare il flusso: obiettivo < 30 minuti a copia
5. **Demo pubblica @sempreaddue** *(decisione aperta)*
   - copia con testi generici e firma, da linkare in bio: vetrina di vendita
6. **Rifiniture finali**
   - riga credits/firma nel finale, controllo pesi, pass finale di copy

## Post-1.0 (backlog)

- Seconda stanza/tema (terrazza estiva, baita invernale…) — il motore è pronto:
  servono solo sfondo nuovo + hitbox nel CONFIG
- Gatto che segue la protagonista dopo la carezza
- Lui che si gira verso di lei quando le è accanto (i profili esistono già nello sheet)
- Messaggi multipli del gatto (frase diversa a ogni carezza)
- Mini-form web per la raccolta dati clienti (sostituisce il JSON manuale)

## Per chiudere la 1.0 Gold

- [ ] Eseguire `CHECKLIST-QA.md` su un iPhone reale (e sull'Android di casa)
- [ ] Pubblicare la demo: `python3 build.py clienti/demo.json` → Netlify Drop → link in bio
- [ ] Ordine pilota completo: JSON → build → verifica → QR (obiettivo < 30 min)
- [ ] Feature congelate: ogni novità va nel backlog post-1.0
