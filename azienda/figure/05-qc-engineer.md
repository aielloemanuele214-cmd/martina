# Figura 05 — QC Engineer (giudice visivo automatico)

> Nessun asset entra nella build se non è corretto tecnicamente **ed** esteticamente. **Modulo automatizzato.**

- **Codice**: FIG-05
- **Fase pipeline**: Controllo qualità (fase 06)
- **Tipo**: modulo automatizzato (art director AI)
- **Stato**: attivo

## Mandato
Possiede il **controllo qualità visivo**: un modello con visione ispeziona ogni
asset contro una rubrica severa e restituisce `{ok, difetti, correzione}`. Guida
il ciclo genera→giudica→rigenera. È l'unica figura che può **bocciare** un asset.

## Istruzioni operative
1. Per ogni asset applica la rubrica del suo tipo (stanza, frame animato, foglio sprite, maschera, popup).
2. Se boccia, restituisce i difetti e una correzione, che rientrano nel prompt del tentativo successivo.
3. Ripete fino a promozione (max tentativi; ultimo colpo col modello pro).
4. Segnala gli asset ancora imperfetti per revisione umana (FIG-10).

## Interfacce
- **Riceve da**: FIG-04 — asset grezzi.
- **Consegna a**: FIG-07 (build) — asset promossi; a FIG-10 — segnalazioni imperfette.
- **Strumenti / moduli**: `gioco/tools/qc.py` (rubriche + giudice).

## Metriche
- Tasso di bocciatura **corretta** (difetti veri intercettati).
- Falsi positivi / falsi negativi.
- Tentativi medi indotti dal QC.

## Lista task (backlog R&D · priorità alto→basso)
- [ ] `R&D-05-01` Rigenerare `pop_scrivania` e `pop_finestra` della build di prova con la rubrica popup ammorbidita — *impatto:* ultimi due asset «sufficienti» portati a pieno.
- [ ] `R&D-05-02` Ridurre la pignoleria su purezza-pixel dei popup (falsi positivi) — *impatto:* meno tentativi inutili, meno costo.
- [ ] `R&D-05-03` Tracciare falsi positivi/negativi su un campione e tarare le soglie — *impatto:* QC affidabile e misurabile.
- [ ] `R&D-05-04` Soglia di severità per tipo asset (scena vs popup) — *impatto:* rigore dove serve, tolleranza dove non nuoce.

## Log (potenziamenti e correzioni)
- 2026-07-09 — Scheda creata. Aggiunto check «foglio = una riga di N figure»; rubrica popup ammorbidita (contesto e scrittura in-world ammessi).
