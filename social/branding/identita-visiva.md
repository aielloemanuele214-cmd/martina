# SempreAddue — Identità visiva social

Regole per mantenere ogni post coerente. Derivate dalla Brand Identity v1
e dalle scelte di prodotto (tema notturno del sito confermato; la musica
NON è tra gli elementi del brand).

## Palette

| Nome | Hex | Uso |
|---|---|---|
| Crema | `#FBF3E9` | titoli, testo principale |
| Pesca | `#F6C9A8` | kicker, dettagli, bordi (al 35% di opacità) |
| Corallo | `#E8896B` | parola accento del titolo, CTA, cuore, numeri |
| Rosa antico | `#C65B7C` | glow di sfondo, croci "anti-esempio" |
| Rosa luce | `#E890A8` | tocchi rari (highlight del cuore) |
| Prugna | `#5E2A47` | glow alternativo di sfondo |
| Notte | `#120a10 → #1b0f17` | sfondo (gradiente verticale) |
| Notte 3 | `#241420` | superfici (badge, cornici telefono) |

Regola d'oro: **un solo accento forte per slide** (di norma il corallo
sull'ultima parola del titolo).

## Tipografia

| Ruolo | Font | Peso/corpo |
|---|---|---|
| Kicker, indice slide, handle | Press Start 2P | 400 · 18–23px (su 1080px) |
| Titoli, CTA, numeri grandi | Baloo 2 | 800 · 86–140px (titoli), 700 · 42–45px (voci lista) |
| Testo corrente, sottotitoli | Nunito | 400 · 33–40px |

Il font pixel si usa **con parsimonia**: mai per frasi lunghe.

## Griglia e spacing (canvas 1080×1350)

- Margine laterale: **84px**
- Header (logo + indice): y = 64
- Kicker: y = 238 · Titolo: da y = 360
- Ritmo delle liste: 150–175px per riga
- Footer handle: y = H−74
- Slide quadrata profilo: 1080×1080, cuore centrato

## Elementi ricorrenti (in ogni slide)

1. **Logo lockup** in alto a sinistra: cuore pixel + "sempre" (pixel,
   corallo) sopra "Addue" (Baloo, crema)
2. **Indice** in alto a destra: `01/07` in pixel
3. **Kicker** con trattino corallo prima del titolo
4. **Handle** `@sempreaddue` centrato in basso con mini-cuore
5. **Stelle pixel**: quadratini pesca a bassa opacità, distribuzione
   deterministica (angolo aureo — mai casuale, mai invadente)
6. **Glow**: 1–2 ellissi sfocate (rosa/corallo/prugna, opacità 7–14%)

## Bordi, ombre, cornici

- Cornici immagine: raggio **44px**, bordo pesca 35%, rotazione ±1.2°
- Ombra: rettangolo nero offset (+10, +18) opacità 45% — niente blur
  pesante, il look resta "pixel"
- Badge numerici: 72×72, raggio 20, numero in pixel corallo
- Pill CTA: raggio pieno (999), gradiente corallo, testo Baloo bianco
- Telefono mockup: corpo Notte 3, raggio 72, bordo pesca

## Iconografia

- **Cuore pixel** (dal logo): unico simbolo del brand, sempre con il
  pixel di luce pesca in alto a sinistra
- **Spunte**: quadrato pixel con riempimento corallo (mai ✓ tondo)
- **Croci** (anti-esempi): croce pixel rosa antico
- Niente clipart, niente icone stock, emoji solo nel copy (max 1)

## Fotografia / immagini

Solo **scene vere dei giochi** (screenshot e sprite del motore):
mai stock, mai foto generiche di coppie. Gli sprite si inseriscono
con `image-rendering: pixelated` (nitidezza pixel).

## Tono di voce (riassunto operativo)

Caldo, diretto, dà del tu. Piccola nostalgia. Frasi brevi che scaldano.
MAI: gergo da marketing, urgenza finta, "amore amore amore", maiuscole
urlate, promesse esagerate. La scadenza founder è vera: si dice così.
