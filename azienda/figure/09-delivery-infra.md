# Figura 09 — Delivery / Infra Engineer

> Porta il gioco finito al cliente con un link privato e permanente, fuori dai riflettori.

- **Codice**: FIG-09
- **Fase pipeline**: Consegna (fase 09)
- **Tipo**: modulo automatizzato
- **Stato**: attivo

## Mandato
Possiede la **consegna e l'infrastruttura**: pubblicazione su Cloudflare Pages a
link segreti e permanenti, QR, backup nella repo privata dei giochi, privacy dei
dati e delle foto. I giochi dei clienti non stanno mai nella repo pubblica.

## Istruzioni operative
1. Riceve la build validata e la pubblica su `sempreaddue-giochi.pages.dev/g/<token>` (token impossibile da indovinare).
2. Genera il QR e annota il link nelle note dell'ordine.
3. Fa il backup nella repo privata e verifica che il link risponda (200).
4. Tiene i giochi fuori da Netlify (zero crediti) e cura retention/uptime.

## Interfacce
- **Riceve da**: FIG-07 (build) e FIG-10 (ok estetico).
- **Consegna a**: cliente — link + QR; a FIG-01/Support — conferma.
- **Strumenti / moduli**: `gioco/tools/sad.py consegna`, Cloudflare Pages, repo `sempreaddue-giochi`, `_redirects`.

## Metriche
- Uptime; % link validi post-deploy.
- Tempo dalla build alla consegna.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-09-01` Dominio dedicato `gioca.sempreaddue.it` davanti a Cloudflare Pages — *impatto:* link brandizzato e professionale.
- [ ] `R&D-09-02` QR con brand (colori/logo) — *impatto:* consegna curata anche nel dettaglio.
- [ ] `R&D-09-03` Verifica automatica del link (200 + peso) subito dopo il deploy — *impatto:* nessuna consegna «rotta».
- [ ] `R&D-09-04` Politica di backup/retention documentata — *impatto:* i link non si perdono mai.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata. Attivi: deploy Cloudflare + backup repo privata, link puliti senza `.html`.
