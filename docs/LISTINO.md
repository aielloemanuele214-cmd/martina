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

## Modello di prezzo (dal 07/2026 — pacchetto unico + add-on)

Analisi competitor: Gift Games €37,50–60 (template, 4 gg) · Muksun $99 (no iOS) ·
Bday Game $250–450 (file Windows) · love-page self-service $5–10. Nessun player
italiano. Vantaggio nostro: browser via link/QR, mobile-first, pixel art curata.

**Prezzo founder: −50% su tutto per i primi 3 mesi dal lancio del sito.**
I prezzi a sinistra sono il listino pieno, tra parentesi il prezzo founder.

| Voce | Contenuto | Lavoro | Listino (founder) |
|---|---|---|---|
| **L'Avventura** (unico pacchetto) | template occasione + **sprite dei due protagonisti inclusi** + nomi, dedica, data, testi delle 3 sorprese, finale, link + QR funzionante | ~30-45 min (form → `ordine.json`, build, QA automatica, Netlify+QR) + sprite | **39,80 €** (19,90 €) |
| add-on **Foto reali** | fotografie della coppia nei popup, a foto | pochi min/foto | 1 € (0,50 €) l'una |
| add-on **Personaggi in più** | sprite aggiuntivi: gatto, amici, famiglia (pipeline `sad art`) | ~15-30 min/sprite | 6 € (3 €) a sprite |
| add-on **Biglietto QR da stampare** | PDF di design elegante pronto per la stampa | ~10 min | 10 € (5 €) |

La musica **non** è personalizzabile (colonna sonora inclusa del template).
Obiettivo: 19,90 come biglietto d'ingresso (sotto ogni competitor), carrello
medio reale 25–35 € con gli extra.

## Upsell naturali
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
