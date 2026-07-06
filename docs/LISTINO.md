# Listino e catalogo — @sempreaddue

*I prezzi sono suggerimenti di partenza: aggiustali su margine e mercato.*

## Catalogo template (pronti in `packs/`)

| Template | Occasione | Cosa cambia rispetto alla base |
|---|---|---|
| **romantica** | anniversari, dediche, "senza motivo" | testi neutri pronti da personalizzare |
| **compleanno** | compleanno del/della partner | sorprese a tema festa, **Buono Regalo** elegante al posto del contratto, finale di auguri |
| **proposta** | proposta di matrimonio 💍 | la lettera finale apre la **Richiesta Ufficiale di Matrimonio**, ballo "ultima volta da fidanzati", bottone "Girati…" |

Tutti e tre condividono lo stesso motore, la stessa stanza e la stessa
`story.json`: **cambiano solo i testi** (config). Un nuovo template per
un'occasione diversa = `sad new <slug> --da romantica` + riscrittura dei testi.

## Tier di vendita

| Tier | Contenuto | Lavoro | Prezzo suggerito |
|---|---|---|---|
| **Base** | template a scelta + nomi, dedica, testi delle 3 sorprese, data "insieme da" | ~30-45 min (scaffolding `sad ordine`, compilazione, QA automatica, Netlify+QR) | 29–49 € |
| **Plus** | Base + foto vere della coppia nei popup + documento (contratto/buono/proposta) scritto su misura | ~1-2 h | 59–89 € |
| **Su misura** | Plus + sprite dei veri protagonisti (AI + pipeline `sad art`) + musica scelta dal cliente (`sad music`) + richieste speciali | mezza-una giornata | 149–249 € |

## Upsell naturali
- **QR stampato** in cornice o biglietto (stampa locale): +10–15 €
- **Seconda occasione** per lo stesso cliente (dal compleanno alla proposta…): sconto fedeltà, il materiale c'è già
- **Versione "gemella"** per l'altro partner (dialoghi invertiti): +30%

## Flusso operativo per ordine
1. `python3 tools/sad.py ordine <slug>` → cartella `clienti/<slug>/`
2. compila `ordine.json` + foto in `foto/` (dal template dell'occasione scelta)
3. `python3 tools/sad.py build clienti/<slug>/ordine.json` (valida da solo)
4. `python3 tools/sad.py qa dist/stanza-<slug>.html` → 13 verifiche
5. Netlify Drop → QR → link in `NOTE.md` → commit

## Demo commerciale
`dist/stanza-demo.html` (salvataggio disattivato, watermark @sempreaddue nel
finale) — da tenere pubblicata a un link fisso per Instagram.
