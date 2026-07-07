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
  carousel-02/   "Cosa costruiamo" (cuore romantico) — 7 slide 1080×1350
  carousel-03/   "Founder −50%" — 7 slide 1080×1350
  post-04-per-chi-ce-da-sempre/        post singolo 1080×1350 (fratelli, sorelle, amici)
  post-05-immagina-la-vostra-avventura/ post singolo 1080×1350 (il mondo fantasy)
  copy/          caption Instagram (brevi) + versione TikTok + hashtag pronti per ogni contenuto
  hashtags/      strategia hashtag: max 5 proprietari + blocchi pronti per post
  branding/      identità visiva: palette, font, griglia, regole
  sorgenti/      generatore (Python + Node) per rigenerare tutto
```

## Ordine di pubblicazione consigliato
1. **Carosello 01** — chi siamo, cos'è SempreAddue
2. **Carosello 02** — cosa costruiamo (cuore romantico: anniversario, compleanno, proposta)
3. **Carosello 03** — promo founder −50% (scadenza reale 6 ottobre 2026)
4. **Post 04** — "Per chi c'è da sempre": fratelli, sorelle, migliori amici
5. **Post 05** — "Immagina la vostra avventura": il mondo fantasy

La scala di priorità del brand: prima il cuore romantico, poi il legame
di sempre, infine il mondo fantasy — che ha un nome proprio e si
racconta come un luogo, mai come una "linea" (vedi il lessico in
`branding/identita-visiva.md`).

## Pubblicare un carosello
1. Carica le `slide-01.png … slide-07.png` nell'ordine
2. Caption (breve) dal file in `copy/` · il blocco hashtag pronto è in fondo
   allo stesso file, va incollato nel **primo commento** (max 5 proprietari)
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
- Il link nelle bio è `sempreaddue.netlify.app`: da sostituire con il
  dominio definitivo, quando ci sarà.
