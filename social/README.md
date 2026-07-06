# SempreAddue — Kit social

Materiale pronto per l'apertura di Instagram e TikTok. Ogni grafica
esiste in tre formati: **SVG** (sorgente modificabile, con font e
immagini incorporati), **PNG** (HD, da pubblicare) e **WebP** (leggero,
per anteprime/web).

```
social/
  profile/       immagine profilo 1080×1080 (svg + png + webp)
  bio/           bio Instagram e TikTok pronte da incollare
  carousel-01/   "Cos'è SempreAddue" — 7 slide 1080×1350
  carousel-02/   "Cosa realizziamo" — 7 slide 1080×1350
  carousel-03/   "Founder −50%" — 7 slide 1080×1350
  copy/          caption Instagram + versione TikTok per ogni carosello
  hashtags/      i 25 hashtag, già in set pronti da copiare
  branding/      identità visiva: palette, font, griglia, regole
  sorgenti/      generatore (Python + Node) per rigenerare tutto
```

## Pubblicare un carosello
1. Carica le `slide-01.png … slide-07.png` nell'ordine
2. Caption dal file in `copy/` · hashtag nel primo commento
3. Su TikTok usa le stesse immagini come photo-mode + la descrizione dedicata

## Rigenerare le grafiche (dopo una modifica)
```bash
cd social/sorgenti
python3 build_all.py                 # SVG → social/*/
node render_svg.js ../carousel-*/slide-*.svg ../profile/profilo.svg   # PNG
# WebP: Pillow (vedi sorgenti) o qualsiasi convertitore
```
I testi delle slide si modificano in `build_all.py`; i colori, i font e
le primitive grafiche in `gen.py`.

## Promemoria
- La scadenza founder (6 ottobre 2026) è scritta nelle slide del
  carosello 03: a fine promo vanno archiviate o rigenerate.
- Il link nelle bio è `sempreaddue.netlify.app`: da aggiornare col
  dominio definitivo.
