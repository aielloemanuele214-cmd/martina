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

**Base fissa 19,50 € + extra a prezzo pieno; promo founder: −50%
sull'INTERO totale (extra compresi) fino al 6 ottobre 2026** — codice
**FOUNDER26**, inviato via email a chi lo richiede dal popup del sito
(le richieste arrivano via FormSubmit). Il form d'ordine riconosce il
codice, applica lo sconto in tempo reale e manda l'email con il riepilogo
già calcolato riga per riga (campi RIEPILOGO): il totale nell'email, sul
form e sulla pagina Grazie è sempre lo stesso numero.

| Voce | Contenuto | Lavoro | Prezzo |
|---|---|---|---|
| **L'Avventura** (unico pacchetto) | template occasione + **sprite dei due protagonisti inclusi** + nomi, dedica, data, testi delle 3 sorprese, finale, link + QR funzionante | ~30-45 min (form → `ordine.json`, build, QA automatica, Cloudflare+QR) + sprite | **19,50 €** fissi |
| add-on **Foto reali** | fotografie della coppia nei popup, a foto | pochi min/foto | 1 € l'una (0,50 € col codice founder) |
| add-on **Personaggi in più** | sprite aggiuntivi: gatto, amici, famiglia (pipeline `sad art`) | ~15-30 min/sprite | 6 € a sprite (3 € col codice founder) |
| add-on **Biglietto QR da stampare** | PDF di design elegante pronto per la stampa | ~10 min | 10 € (5 € col codice founder) |

La musica **non** è personalizzabile (colonna sonora inclusa del template).
Obiettivo: 19,50 come biglietto d'ingresso (sotto ogni competitor), carrello
medio reale 25–35 € con gli extra.

## Upsell naturali
- **Seconda occasione** per lo stesso cliente (dal compleanno alla proposta…): sconto fedeltà, il materiale c'è già
- **Versione "gemella"** per l'altro partner (dialoghi invertiti): +30%

## Pagamenti — fase di test (preventivo + PayPal manuale)

Finché non è aperta la partita IVA, il sito **non incassa in automatico**.
Motivo: la partita IVA in Italia dipende dal carattere *abituale*
dell'attività (frequenza, organizzazione), non dallo strumento di incasso —
quindi un marketplace o un processore di pagamento dietro un sito già
organizzato (listino, form, consegna automatizzata) non sostituisce
l'obbligo. Per questo il form mostra solo un **totale stimato** ("preventivo
indicativo") e il pagamento resta un passo manuale, fuori dal sito:

1. Leggi la richiesta (email di FormSubmit o cartella `clienti/<slug>/`)
2. Confermi via email/Instagram il preventivo finale (extra, eventuali
   sconti/accordi particolari)
3. Mandi una richiesta di pagamento **PayPal** ("Richiedi denaro" dall'app,
   o un link paypal.me) per l'importo esatto, all'email del cliente —
   un account **PayPal personale** incassa pagamenti "beni e servizi" senza
   bisogno di partita IVA, a differenza di Stripe che in Italia richiede
   tipicamente un'attività registrata per attivare i pagamenti live
4. Ricevuto il pagamento, parti con `sad.py consegna <slug> --push`

L'indirizzo PayPal **non compare sul sito** (scelta di privacy): `grazie.html`
mostra solo «💳 Pagamento sicuro — PayPal». Il cliente vede l'indirizzo dentro
la richiesta di pagamento che gli mandi tu. Riferimento interno: l'incasso va
sull'account PayPal di `aielloemanuele@yahoo.it`.

**Soglia di test auto-imposta:** i primi 5-10 ordini, poi stop e valutazione
col commercialista prima di continuare — per restare genuinamente
un'attività occasionale e non scivolare in "abituale" senza accorgersene.

## Pagamenti automatici (per dopo, con partita IVA aperta)

Lo scaffolding Stripe è già pronto in `grazie.html`, solo spento
(`STRIPE_PAYMENT_LINK = ''`). Per riattivarlo quando avrai la partita IVA:
1. Su dashboard.stripe.com crea 4 prodotti a **prezzo pieno**: **L'Avventura**
   19,50 € (quantità fissa 1), **Foto reale** 1 € (quantità regolabile 0-10),
   **Personaggio extra** 6 € (0-5), **Biglietto QR** 10 € (0-1).
2. Crea un coupon **FOUNDER26** al −50% e abilita "Consenti codici
   promozionali" sul Payment Link (il cliente lo inserisce nel checkout).
3. Crea il **Payment Link** con i 4 prodotti e quantità regolabile sugli extra.
4. Incolla l'URL nella costante `STRIPE_PAYMENT_LINK` in `grazie.html`:
   il bottone "Completa il pagamento" ricompare da solo.
5. Alla fine del periodo founder (6 ottobre 2026): disattiva il coupon
   FOUNDER26. I prezzi dei prodotti restano quelli pieni; aggiorna solo i
   testi del sito che citano lo sconto founder.

## Flusso operativo per ordine
1. `python3 tools/sad.py ordine <slug>` → cartella `clienti/<slug>/`
2. compila `ordine.json` + foto in `foto/` (dal template dell'occasione scelta)
3. `python3 tools/sad.py consegna <slug> --push` → build, QA, pubblicazione
   nella repo privata `sempreaddue-giochi` (Cloudflare Pages, fuori da
   Netlify), QR in `clienti/<slug>/`, link in `NOTE.md`. Vedi
   `README-PRODUZIONE.md` per i dettagli.

## Demo commerciale
`dist/stanza-demo.html` (salvataggio disattivato, watermark @sempreaddue nel
finale) — da tenere pubblicata a un link fisso per Instagram.
