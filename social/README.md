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
  carousel-02/   "Cosa realizziamo" (linea romantica) — 7 slide 1080×1350
  carousel-03/   "Founder −50%" — 7 slide 1080×1350
  post-04-per-chi-ce-da-sempre/        post singolo 1080×1350 (fratelli, sorelle, amici)
  post-05-immagina-la-vostra-avventura/ post singolo 1080×1350 (linea fantasy)
  copy/          caption Instagram + versione TikTok per ogni contenuto
  hashtags/      i 25 hashtag, già in set pronti da copiare
  branding/      identità visiva: palette, font, griglia, regole
  sorgenti/      generatore (Python + Node) per rigenerare tutto
```

## Ordine di pubblicazione consigliato
1. **Carosello 01** — chi siamo, cos'è SempreAddue
2. **Carosello 02** — cosa realizziamo (cuore romantico: anniversario, compleanno, proposta)
3. **Carosello 03** — promo founder −50% (scadenza reale 6 ottobre 2026)
4. **Post 04** — "Per chi c'è da sempre": fratelli, sorelle, migliori amici
5. **Post 05** — "Immagina la vostra avventura": lancio della linea fantasy

La scala di priorità del brand: prima la linea romantica (è il cuore del
prodotto), poi il legame di sempre, infine la linea fantasy come mondo a
parte con il suo nome proprio.

## Pubblicare un carosello
1. Carica le `slide-01.png … slide-07.png` nell'ordine
2. Caption dal file in `copy/` · hashtag nel primo commento
3. Su TikTok usa le stesse immagini come photo-mode + la descrizione dedicata

## Pubblicare un post singolo (04 e 05)
1. Carica `post.png` · caption dal file corrispondente in `copy/`
2. Su TikTok usa l'hook e la CTA indicati nel file di copy

## Rigenerare le grafiche (dopo una modifica)
```bash
cd social/sorgenti
python3 build_all.py                 # SVG → social/*/
node render_svg.js ../carousel-*/slide-*.svg ../post-*/post.svg ../profile/profilo.svg   # PNG
# WebP: Pillow (vedi sorgenti) o qualsiasi convertitore
```
I testi delle slide si modificano in `build_all.py`; i colori, i font e
le primitive grafiche in `gen.py`.

## Promemoria
- La scadenza founder (6 ottobre 2026) è scritta nelle slide del
  carosello 03: a fine promo vanno archiviate o rigenerate.
- Il link nelle bio è `sempreaddue.netlify.app`: da aggiornare col
  dominio definitivo.
