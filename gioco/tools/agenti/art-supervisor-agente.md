<!--
  CERVELLO dell'agente Art Supervisor (figura FIG-03). È il DNA VISIVO di
  SempreAddue: lo Style Bible, il chroma, i divieti e la regola di escalation.
  Il codice (tools/genera.py) lo carica da qui e lo inietta in OGNI prompt.

  ADDESTRARLO = modificare questo file. Nessun codice da toccare.
  Attenzione: questa figura è DETERMINISTICA (assembla prompt costanti). La
  coerenza qui è ciò che rende affidabile tutta la produzione: modifica con cura.

  Sezioni "## NOME": non rinominarle. I testi in inglese (li legge il modello
  immagine); lascia intatti i termini tecnici (#00FF00, 16-bit).
-->

# Agente Art Supervisor — DNA visivo & standard di prompt

## MODELLO_DEFAULT
gemini-3.1-flash-image

## MODELLO_PRO
gemini-3-pro-image

## STYLE
Authentic SNES-era 16-bit pixel art, cozy lo-fi bedroom mood (Stardew Valley / Eastward feel). TRUE low-resolution pixel grid: crisp HARD-EDGED pixels, clean 1px outlines, absolutely NO anti-aliasing, NO soft gradients, NO blur, NO smeared or painterly look. Warm cozy inviting palette — amber, terracotta, candle-gold, warm browns — with gentle warm lamp light and only soft cool accents at the night window. Subtle ordered dithering for shading. Readable silhouette. Premium, intimate, nostalgic.

## GREEN
Placed on a SOLID PURE #00FF00 GREEN SCREEN, perfectly flat, hard-edged and uniform, no gradient, no green light spilling on the subject.

## NEG
Avoid: blur, anti-aliased fuzzy edges, glow, 3D render look, text, watermark, extra limbs, feet cut off, inconsistent proportions between frames.

## NOLIVING
CRITICAL: the scene is completely EMPTY of any living being — absolutely NO people, NO human figures or silhouettes, NO cats, NO dogs, NO animals or pets anywhere. Only architecture, furniture and inanimate objects. Living things are separate sprites, never painted into this image.

## ESCALATION
Genera prima col MODELLO_DEFAULT (economico). Il QC (FIG-05) può far ripetere un
asset con i difetti in prompt; all'ultimo tentativo si passa al MODELLO_PRO (più
preciso, più costoso). Regola: il modello pro è l'eccezione, non l'abitudine.
