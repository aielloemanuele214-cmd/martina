# Prompt standard per Nano Banana (Gemini 2.5 Flash Image)

Kit di prompt riutilizzabili per generare gli asset di ogni ordine in modo
**coerente** e già pronti per la pipeline `sad art`. Le parti tra `{{ }}` si
cambiano per ordine; tutto il resto resta **identico sempre** (è ciò che
standardizza lo stile tra clienti diversi).

I prompt sono in **inglese** (i modelli immagine rendono meglio) con note in
italiano. Vincoli tecnici presi da `GENERAZIONE-ASSET.md`.

---

## Come si lavora (metodo "reference-first")

Nano Banana è forte nella **coerenza da immagine di riferimento** e
nell'**editing mirato**. Quindi:

1. **Genera prima il riferimento**: LEI vista frontale, frame idle singolo.
   Approvalo (viso, capelli, vestito, proporzioni).
2. **Genera tutto il resto passando quel riferimento come immagine input** +
   il prompt: «stesso personaggio dell'immagine, identico vestito/capelli/viso,
   cambia solo [vista/posa]». Così LEI resta la stessa su tutti i fogli.
3. **Correggi il singolo frame** se uno esce storto: reinvia l'immagine e chiedi
   «rigenera SOLO il frame 3, lascia gli altri identici». Non rifare tutto.
4. Salva i file coi nomi di `GENERAZIONE-ASSET.md §3.7` in `packs/<slug>/assets/_src/`
   e lancia `python3 tools/sad.py art` (scontorno + packing + ritratti).

---

## 🎨 INTESTAZIONE DI STILE — anteporre SEMPRE a ogni prompt

```
16-bit pixel art, SNES / Stardew Valley era quality, hand-drawn. Warm cozy
nighttime palette with soft candle lighting and cool accents from the night
outside. Consistent line weight, shading and level of detail across every
sheet — everything must look like the same hand and the same world. Premium,
clean, readable. Solid pure black background #000000: no transparency, no
checkerboard pattern, no gradient, no glow or halo around the figures.
```

## ⚙️ VINCOLI TECNICI — non negoziabili (li richiede la pipeline)

```
Frames in a single horizontal row, evenly spaced, identical scale, character
centered in each cell, with clear empty margin between frames (no frame
touching or overlapping the next). Feet always visible and resting on the same
ground line in every frame. No text, no UI, no borders, no watermark, no extra
background elements — only the subject on solid black.
```

Dimensioni sorgente: **1536×1024** (fogli personaggio, orizzontali) ·
**1254×1254 o più** (stanza e popup, quadrati). Chiedi l'aspect ratio
coerente: *landscape/wide* per i fogli, *square 1:1* per stanza e popup.

---

## 1) LEI — protagonista giocabile · 4 fogli (una vista per foglio)

Placeholder da compilare: `{{LEI}}` = descrizione fisica (es. "young woman,
long wavy brown hair, freckles, mustard-yellow sweater, blue jeans, white
sneakers").

**Foglio FRONTE** (genera questo per primo = riferimento):
```
[INTESTAZIONE DI STILE]
Character sprite sheet, front view. Subject: {{LEI}}. Full body, feet visible.
Four frames left-to-right, in this exact order:
1) idle, standing relaxed;
2) walking, right leg forward;
3) walking, left leg forward;
4) interacting, leaning/reaching one hand toward an object.
Same character, identical outfit, hair and proportions in all four frames.
[VINCOLI TECNICI]
```

**Fogli DESTRA / SCHIENA / SINISTRA** (passa il fronte come immagine input):
```
[INTESTAZIONE DI STILE]
Same character as the reference image — keep identical face, hair, outfit,
colors and proportions. Redraw as a sprite sheet in {{VISTA: right-side view /
back view / left-side view}}. Four frames left-to-right, same order:
1) idle, 2) walk step A, 3) walk step B, 4) interaction reach.
The walk cycle must read as a seamless loop. Do NOT mirror the left from the
right — draw it. [VINCOLI TECNICI]
```

## 2) LUI — secondo protagonista (NPC) · 1 foglio, 5 frame emotivi
`{{LUI}}` = descrizione fisica. **Lui poco più alto di lei** (lei ≈ 95%).
```
[INTESTAZIONE DI STILE]
Front-view character sheet, 5 frames left-to-right, of {{LUI}}. He stands
still (does not walk). Frame order and expression:
1) idle, relaxed smile; 2) embarrassed, hand behind the neck; 3) talking,
open-hand gesture; 4) thinking, hand on chin; 5) arms crossed, amused smile.
Expressive, well-drawn face in every frame (these frames become dialogue
portraits). Same man, identical outfit/hair in all five frames; slightly
taller than the female character. [VINCOLI TECNICI]
```

## 3) COPPIA CHE BALLA · 1 foglio, 5 pose
```
[INTESTAZIONE DI STILE]
Sheet of 5 frames left-to-right: the two characters ({{LEI}} and {{LUI}})
embracing and slow-dancing together, small romantic movements that chain
smoothly when played 1→2→3→4→5→4→3→2. Same two characters as the reference
images, consistent outfits and proportions; he is slightly taller. It is a
slow dance, not acrobatic. [VINCOLI TECNICI]
```

## 4) ANIMALE DOMESTICO (se richiesto) · 1 foglio, 2 frame
`{{ANIMALE}}` = es. "orange tabby cat".
```
[INTESTAZIONE DI STILE]
Sheet of 2 frames left-to-right of {{ANIMALE}}, lying on the floor:
1) sleeping, curled; 2) awake, head raised. Same animal in both frames.
[VINCOLI TECNICI]
```

## 5) AMBIENTAZIONE · 2 immagini quadrate (frame 1 e 2)
`{{STANZA}}` = tema/occasione (es. "cozy winter living room, lit fireplace,
red sofa, bookshelf, snow outside the window"). Elementi obbligatori: 3 oggetti
indizio ben distinti, la postazione dell'NPC, il punto dell'animale, una
finestra sul mondo esterno, uno spazio libero centrale per il ballo.

**Frame 1** (genera questo come riferimento della stanza):
```
[INTESTAZIONE DI STILE]
Top-down 3/4 view square room (Stardew-Valley angle). {{STANZA}}. The back wall
occupies the top ~25%; the rest is walkable floor with furniture. Clearly
visible and well separated: three distinct interactive "clue" objects
({{OGGETTO1}}, {{OGGETTO2}}, {{OGGETTO3}}), a spot where a character can stand
(NPC), a spot for the pet, a window showing the night outside, and an open
central space. Rich in detail but readable; the interactive objects should
catch the eye without arrows or labels. Square 1:1.
```
**Frame 2** (passa il frame 1 come input):
```
Take the reference room image and change ONLY the animated elements — candle
flames, screen/TV glow, window light, reflections, small sparkles. Everything
else pixel-identical to the reference, so the two frames form a perfect subtle
loop. Square 1:1, same solid framing.
```

## 6) POPUP DEGLI INDIZI · 3 immagini quadrate 1:1 + finestra
Per ogni oggetto indizio, un primo piano coerente con la stanza.
```
[INTESTAZIONE DI STILE]
Square 1:1 close-up illustration of {{OGGETTO}} in the same pixel-art style and
lighting as the room, as if seen up close with atmosphere. No text in the image.
```
(Ripeti per i 3 oggetti; una quarta per il panorama/momento della finestra.)

---

## ✅ Checklist prima di passare a `sad art`
- [ ] Fondo **nero puro** su tutti i fogli, zero trasparenze/scacchiere/glow
- [ ] Frame equidistanti, stessa scala, **piedi sulla stessa linea**
- [ ] LEI: 4 viste × 4 frame nell'ordine idle/passoA/passoB/interazione
- [ ] LUI: 5 frame emotivi, viso curato; **poco più alto di lei** (tutti i fogli)
- [ ] Ballo: 5 pose concatenabili; proporzioni coerenti coi fogli singoli
- [ ] Stanza: frame 1 e 2 identici tranne gli elementi animati
- [ ] Popup 1:1, stesso stile, nessun testo nell'immagine
- [ ] Stesso personaggio (viso/vestito/capelli) su TUTTI i fogli
- [ ] File nominati come in `GENERAZIONE-ASSET.md §3.7`

## Note su Nano Banana
- Passa **sempre** il riferimento come immagine input per i fogli successivi:
  è ciò che tiene lo stesso personaggio tra le viste.
- Per correggere: reinvia l'immagine e chiedi di **rigenerare solo il frame N**.
- Se i frame non escono perfettamente equidistanti, si può generare ogni frame
  **singolo** su nero e lasciare che il packer li allinei: è la strada che
  `sad genera` automatizzerà (più affidabile del foglio in un colpo solo).
