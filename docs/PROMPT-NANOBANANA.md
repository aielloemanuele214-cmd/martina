# Prompt standard per Nano Banana (Gemini 2.5 Flash Image)

Prompt riutilizzabili per generare gli asset di ogni ordine in modo
**coerente** e già pronti per `sad art`. Le parti tra `{{ }}` cambiano per
ordine; il resto è fisso (standardizza lo stile tra clienti diversi).
Misure, chroma e layout: **fonte unica in `STANDARD-PRODUZIONE.md`**.

Prompt in **inglese** (i modelli rendono meglio) con note in italiano.

---

## Come si lavora (metodo "reference-first")
1. **Genera prima il riferimento**: PROTAGONISTA vista frontale, frame idle.
   Approva viso/capelli/vestito/proporzioni.
2. **Genera tutto il resto passando quel riferimento come immagine input**:
   «stesso personaggio dell'immagine, identico vestito/capelli/viso, cambia
   solo [vista/posa]». Così il personaggio resta lo stesso su tutti i fogli.
3. **Correggi il singolo frame** se serve: reinvia e chiedi «rigenera SOLO il
   frame 3, lascia gli altri identici».
4. Salva coi nomi di `GENERAZIONE-ASSET.md §3.7` in
   `packs/<slug>/assets/_src/` e lancia `python3 tools/sad.py art`.

## 🎨 INTESTAZIONE DI STILE — anteporre SEMPRE
```
16-bit pixel art, SNES / Stardew Valley era quality, hand-drawn. Warm cozy
nighttime palette, soft candle lighting, cool accents from the night outside.
Consistent line weight, shading and detail across every sheet — same hand,
same world. Premium, clean, readable.
```

## 🟩 SFONDO — due regole diverse
- **Personaggi e oggetti da ritagliare** → `Solid pure bright green chroma
  background #00FF00, perfectly uniform, no transparency, no gradient, no
  green tint or shadow on the subject.` (Il verde si ritaglia pulito anche sui
  toni scuri.)
- **Stanze (sfondi)** → **niente chroma**: illustrazione a piena scena.

## ⚙️ VINCOLI TECNICI (fogli con più frame)
```
Frames in a single horizontal row, evenly spaced, identical scale, subject
centered, clear empty margin between frames (none touching). Feet visible and
resting on the same ground line in every frame. No text, no UI, no watermark.
```
Misure: **stanza 1024×1024**, **frame 512×512 ciascuno**, **popup 512×512**
(vedi `STANDARD-PRODUZIONE.md`).

---

## 1) PROTAGONISTA — personaggio giocabile · 4 fogli (una vista per foglio)
`{{PROTA}}` = descrizione fisica (es. "young woman, long wavy brown hair,
mustard sweater, blue jeans, white sneakers").

**Foglio FRONTE** (genera per primo = riferimento):
```
[STILE] Character sprite sheet, front view, on bright green #00FF00. Subject:
{{PROTA}}. Full body, feet visible. Four frames left-to-right, exact order:
1) idle relaxed; 2) walking right leg forward; 3) walking left leg forward;
4) interacting, leaning/reaching one hand toward an object. Same character in
all four frames. [VINCOLI TECNICI]
```
**Fogli DESTRA / SCHIENA / SINISTRA** (passa il fronte come input):
```
[STILE] Same character as the reference image — identical face, hair, outfit,
colors, proportions. Redraw as a sprite sheet in {{right-side / back /
left-side}} view, on bright green #00FF00. Four frames, same order (idle, walk
A, walk B, interaction). Seamless walk cycle. Do NOT mirror — draw it.
[VINCOLI TECNICI]
```

## 2) SECONDARIO — NPC · 1 foglio, 5 frame emotivi
`{{SEC}}` = descrizione fisica. **Poco più alto del protagonista** se la
coppia lo prevede (regolabile per ordine).
```
[STILE] Front-view character sheet on bright green #00FF00, 5 frames
left-to-right, of {{SEC}}. Stands still (does not walk). Order: 1) idle relaxed
smile; 2) embarrassed, hand behind neck; 3) talking, open-hand gesture;
4) thinking, hand on chin; 5) arms crossed, amused smile. Expressive,
well-drawn face in every frame (these become dialogue portraits).
[VINCOLI TECNICI]
```

## 3) COPPIA CHE BALLA · 1 foglio, 5 pose
```
[STILE] Sheet of 5 frames left-to-right on bright green #00FF00: {{PROTA}} and
{{SEC}} embracing and slow-dancing, small romantic movements that chain
smoothly when played 1→2→3→4→5→4→3→2. Same two characters as the reference
images, consistent outfits/proportions. A slow dance, not acrobatic.
[VINCOLI TECNICI]
```

## 4) ANIMALE (se richiesto) · 1 foglio, 2 frame
```
[STILE] Sheet of 2 frames left-to-right on bright green #00FF00 of {{ANIMALE}},
on the floor: 1) sleeping curled; 2) awake head raised. Same animal.
[VINCOLI TECNICI]
```

## 5) STANZA (SFONDO) · 2 immagini quadrate 1024² — NIENTE chroma
`{{STANZA}}` = tema (es. "cozy winter living room, lit fireplace, red sofa,
bookshelf, snowy night outside the window"). **Rispettare lo STAGE STANDARD**
(`STANDARD-PRODUZIONE.md §4`): gli oggetti vanno in zone precise.

**Frame 1** (riferimento stanza):
```
[STILE] Top-down 3/4 view (Stardew angle) square 1024×1024 room, full scene,
NO green background. {{STANZA}}. Back wall occupies the top ~20-25%; the rest
is walkable floor. Place, clearly separated:
- clue object A on the UPPER-LEFT wall area;
- clue object B on the RIGHT side;
- clue object C on a LOWER-LEFT piece of furniture;
- an open central space (bottom-center) kept clear;
- a spot mid-right where a character can stand (NPC);
- a window on the back wall showing the night outside;
- (optional) a pet spot on the left floor.
Rich but readable; interactive objects catch the eye without arrows or labels.
```
**Frame 2** (passa il frame 1 come input):
```
Take the reference room and change ONLY the animated elements — candle flames,
TV/screen glow, window light, reflections, small sparkles. Everything else
pixel-identical, so the two frames loop subtly. Square 1024×1024.
```

## 6) POPUP INDIZI · 3 immagini 512² 1:1 (+ finestra) — NIENTE chroma
```
[STILE] Square 512×512 close-up of {{OGGETTO}}, same pixel-art style and
lighting as the room, seen up close with atmosphere. No text in the image.
```

---

## ✅ Prima di `sad art`
- [ ] Personaggi/oggetti su **verde #00FF00**; stanze/popup a piena scena
- [ ] Stanza 1024², frame 512², popup 512²; piedi sulla stessa linea
- [ ] Oggetti della stanza nelle **zone dello stage standard**
- [ ] Stesso personaggio su tutti i fogli · file `protagonista_*` / `secondario_*`

## Note su Nano Banana
- Passa **sempre** il riferimento come input per i fogli successivi (coerenza).
- Per correggere: reinvia e chiedi di **rigenerare solo il frame N**.
- Se i fogli multi-frame escono imperfetti, genera ogni **frame singolo** su
  verde: il packer li allinea. È la strada che `sad genera` automatizzerà.
