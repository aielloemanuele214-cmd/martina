# Prompt Nano Banana — livello direzione artistica

Prompt di **art direction** per generare gli asset di ogni ordine con
qualità e coerenza da studio. Preservano il DNA visivo SempreAddue già
consegnato (non lo cambiano: lo codificano). Misure/chroma/layout autorevoli:
`STANDARD-PRODUZIONE.md`. Specifiche di dettaglio: `GENERAZIONE-ASSET.md`.

Prompt in **inglese** (i modelli rendono meglio) con note in italiano.
`{{ }}` = variabile per ordine.

---

## Metodo (reference-first, come in uno studio)
1. Genera il **model sheet**: PROTAGONISTA fronte, frame idle. Approva design,
   palette, proporzioni: diventa la **bibbia del personaggio**.
2. Genera tutto il resto **passando quell'immagine come input**: «same character
   as the reference, identical design — only change the [view/pose]».
3. **Ritocco chirurgico** dei singoli frame: reinvia e «regenerate only frame N,
   keep everything else identical».
4. Salva coi nomi di `GENERAZIONE-ASSET.md §3.7` e lancia `sad art`.

---

## 🎨 STYLE BIBLE — il DNA (anteporre SEMPRE, invariato)
```
Cohesive hand-crafted 16-bit pixel art, cozy-JRPG / life-sim quality
(reference feel: Stardew Valley interiors, Eastward, Sea of Stars backdrops).
Hand-placed pixels, crisp clean 1px outlines, limited harmonious palette:
warm ambers, terracotta and candle-gold for interior light; deep teal and
indigo for the night. Soft volumetric candlelight with gentle warm rim-light
on the subjects and cozy ambient occlusion in the corners. Subtle ordered
dithering for gradients (no smooth blur). Romantic, intimate, premium — never
saccharine, never noisy. Readable silhouettes first, rich detail second.
Everything reads as one hand and one world.
```
Palette d'appoggio (ancora i colori, non è vincolante al pixel):
`#F3E7DC crema · #E8896B corallo · #5E2A47 prugna · #1b2b3a notte · #ffd9a0 candela`.

## 🟩 Sfondo di generazione (due regole)
- **Da ritagliare** (personaggi, oggetti): `on a solid pure #00FF00 green
  screen, perfectly flat and uniform, no green light or reflection spilling
  onto the subject.`
- **Stanze**: **niente green screen** — illustrazione a piena scena.

## ⚙️ Vincoli tecnici (fogli multi-frame)
```
Single horizontal row, frames evenly spaced at identical scale, subject
centered, clear empty margin between frames (none touching). Feet fully visible
and planted on one shared ground line across all frames. Character ~256px tall
reference. No text, no UI, no border, no watermark.
```

## 🚫 Da evitare (negative direction)
```
Avoid: blur, anti-aliased fuzzy edges, glow/halo, JPEG artifacts, 3D-render or
plasticky look, photobashing, gradient banding, muddy palette, extra limbs or
fingers, warped face, feet cut off, inconsistent proportions between frames,
green spill on the subject, text or logos.
```

---

## 1) PROTAGONISTA — giocabile · 4 fogli (una vista per foglio)
`{{PROTA}}` = brief fisico (es. "woman in her late 20s, warm olive skin, long
chestnut waves, mustard knit sweater, high-waist jeans, white sneakers,
gentle confident posture").

**FRONTE** (model sheet, genera per primo):
```
[STYLE BIBLE] [GREEN] [TECH]
Character animation sheet, front 3/4 view. Design: {{PROTA}}. Full body, feet
visible. Four frames, exact order and intent:
1) idle — relaxed weight on both feet, soft breathing pose;
2) walk A — right leg forward, natural arm counter-swing;
3) walk B — left leg forward, mirror of the stride;
4) interact — leaning slightly, one hand reaching toward an object, inviting.
Keep the exact same design, palette and proportions in every frame.
[NEGATIVE]
```
**DESTRA / SCHIENA / SINISTRA** (input = model sheet fronte):
```
[STYLE BIBLE] [GREEN] [TECH]
Same character as the reference image — identical face, hairstyle, outfit,
colors and proportions. Redraw the 4-frame sheet in {{right-side / back /
left-side}} view, same order (idle, walk A, walk B, interact), forming a
seamless loop. Hand-draw the left view — do not mirror the right. [NEGATIVE]
```

## 2) SECONDARIO — NPC · 1 foglio, 5 frame emotivi
`{{SEC}}` = brief fisico. Regola altezza per ordine.
```
[STYLE BIBLE] [GREEN] [TECH]
Front-view acting sheet, 5 frames, of {{SEC}}. Stands in place (no walking) —
this is emotional acting, the face carries it (frames become dialogue
portraits, keep it expressive and on-model). Order and beat:
1) idle — warm relaxed smile; 2) bashful — hand behind the neck, shy;
3) speaking — open-hand gesture, mid-sentence; 4) thoughtful — hand to chin;
5) amused — arms crossed, playful grin. [NEGATIVE]
```

## 3) COPPIA CHE BALLA · 1 foglio, 5 pose
```
[STYLE BIBLE] [GREEN] [TECH]
Five-frame sheet: {{PROTA}} and {{SEC}} embracing in a slow dance, tender
micro-movements that chain smoothly when played 1→2→3→4→5→4→3→2 (a gentle
sway, not acrobatic). Same two characters as the reference images, consistent
design and proportions, believable intimate body contact. [NEGATIVE]
```

## 4) ANIMALE (se richiesto) · 1 foglio, 2 frame
```
[STYLE BIBLE] [GREEN] [TECH]
Two-frame sheet of {{ANIMALE}} on the floor: 1) sleeping, curled and content;
2) awake, head raised, alert-cute. Same animal, same design. [NEGATIVE]
```

## 5) STANZA (SFONDO) · 1024² · niente green · DUE frame
`{{STANZA}}` = mood dell'ambiente. Rispettare lo **STAGE STANDARD**
(`STANDARD-PRODUZIONE.md §4`): oggetti in zone precise.

**Frame 1 — l'ambiente:**
```
[STYLE BIBLE]
Top-down 3/4 cozy-sim view, square 1024×1024 room, full scene, no green screen.
{{STANZA}}. Back wall occupies the top ~20-25%; the rest is warm walkable floor.
Compose, clearly separated and reading at a glance without labels:
- clue object A on the UPPER-LEFT wall zone;
- clue object B on the RIGHT side;
- clue object C on a LOWER-LEFT furniture piece;
- an open, uncluttered central-bottom space (room to dance);
- a mid-right spot for a person to stand;
- a window on the back wall onto the night;
- (optional) a soft pet spot on the left floor.
Layered depth, candle-lit warmth, lived-in intimate detail. [NEGATIVE]
```
**Frame 2 — l'ambiente VIVO** (input = Frame 1):
```
Take the reference room and change ONLY the living/animated elements, keeping
everything else pixel-identical so the two frames alternate without jitter.
Animate 2–4 elements that fit THIS scene (pick from the mood): {{ANIMATI}}.
Keep it subtle — a flame that leans, a reflection that slides, a glow that
breathes. Square 1024×1024, same framing and palette.
```
`{{ANIMATI}}` — scegli per contesto (vedi catalogo in `STANDARD-PRODUZIONE.md §6`):
fuoco→ *candle flames flicker, fireplace fire dances, embers pulse* · acqua→
*water ripples, reflections drift, rain streaks the window* · vento→ *curtains
and plants sway gently* · tech→ *screen/vinyl glow flickers, record spins* ·
notte→ *stars twinkle, snow or leaves fall outside* · fantasy→ *floating
sparkles, runes and crystals pulse*.

## 6) POPUP INDIZI · 512² 1:1 · niente green
```
[STYLE BIBLE]
Square 512×512 intimate close-up of {{OGGETTO}}, same world and candlelight as
the room, shallow cozy framing with atmosphere. No text in the image. [NEGATIVE]
```

---

## Tecnica Nano Banana (per la coerenza)
- **Reference come input**: è la leva n°1 di coerenza — sempre, per ogni foglio
  dopo il model sheet.
- **Ritocco mirato**: «regenerate only frame N / only the flames» invece di
  rifare tutto: sfrutta l'editing del modello.
- **Blocca il design**: «lock the character design and palette from the
  reference; do not reinterpret».
- **Un frame alla volta** se i fogli multipli sbandano: genera i singoli frame
  su verde, il packer li allinea (strada che `sad genera` automatizzerà).

## ✅ Prima di `sad art`
- [ ] Style Bible applicata; negative direction inclusa
- [ ] Personaggi/oggetti su verde #00FF00; stanze/popup a piena scena
- [ ] Stanza 1024², frame 512², popup 512²; piedi su una linea comune
- [ ] Oggetti stanza nelle zone dello stage standard · **Frame 2 vivo** coerente
- [ ] Stesso personaggio su tutti i fogli · file `protagonista_*` / `secondario_*`

## Nota onesta sull'ottimizzazione
Questi prompt sono la **base d'autore**: la vera messa a punto si fa **contro le
immagini reali** di Nano Banana (2–3 iterazioni per calibrare palette,
proporzioni e resa dei frame). Appena c'è la chiave API, affino i prompt sui
risultati veri e li cablo in `sad genera`.
