# Conferma preventivo + richiesta di pagamento

Da inviare **dopo** aver letto l'ordine (email FormSubmit «Nuovo ordine
dal sito»). L'email d'ordine ti arriva già coi conti fatti nei campi
RIEPILOGO: base, extra riga per riga, subtotale, sconto founder, TOTALE.
Ricopia quelle stesse cifre qui sotto — così form, email e preventivo
dicono lo stesso numero.

Campi tra parentesi quadre = da sostituire. `[NOME]`, `[PARTNER]`,
`[VOCI]`, `[TOTALE]`, `[GIORNI]`.

**Flusso:** 1) confermi il preventivo → 2) alla loro «ok» mandi la
richiesta PayPal → 3) a pagamento ricevuto, parti con la costruzione.

---

## 1) Email — conferma del preventivo (primo invio)

**Oggetto:** Il preventivo per la vostra avventura 💛

> Ciao [NOME]!
>
> Abbiamo letto la vostra storia e non vediamo l'ora di costruirla.
> Ecco il riepilogo, così è tutto chiaro prima di partire:
>
> • [VOCI — es. L'Avventura completa … 19,50 €]
> • [es. 2 foto reali … 2,00 €]
> • [es. Codice FOUNDER26 · −50% su tutto … −10,75 €]
> **Totale: [TOTALE] €**
>
> Tempi: pronta in circa **[GIORNI] giorni** dal pagamento. La consegniamo
> con un link privato + QR code, si gioca da qualsiasi telefono.
>
> Se per te va bene, rispondi con un semplice «ok» e ti mando subito la
> richiesta di pagamento con PayPal per l'importo esatto. Da lì partiamo.
>
> Se invece vuoi aggiungere o togliere qualcosa, dimmelo pure: aggiorno
> il totale in un attimo.
>
> A presto 🕹
> — SempreAddue
> *Un posto a due. Per sempre.*

---

## 2) Email — invio della richiesta di pagamento (dopo il loro «ok»)

**Oggetto:** Ecco la richiesta di pagamento 💛

> Perfetto [NOME]!
>
> Ti ho appena inviato con **PayPal** una richiesta di pagamento da
> **[TOTALE] €**, all'indirizzo di questa email. Ti basta aprirla e
> confermare.
>
> Appena risulta pagata, iniziamo subito a costruire la vostra avventura
> e ti aggiorno lungo il percorso. Se preferisci un altro modo, dimmelo.
>
> Grazie di cuore per la fiducia — soprattutto da founder 🕹
> — SempreAddue · *Un posto a due. Per sempre.*

---

## 3) Come mandare la richiesta PayPal (fase test, senza P.IVA)

1. App **PayPal** → **Richiedi** (o «Richiedi denaro»).
2. Inserisci l'**email del cliente** e l'importo esatto `[TOTALE]`.
3. Causale: «Avventura SempreAddue — [PARTNER] & [NOME]».
4. Invia. Il cliente riceve la richiesta e paga con un tap.
5. A pagamento **ricevuto**, avvia la produzione:
   `python3 tools/sad.py consegna <slug> --push`

Nota: un account PayPal **personale** incassa pagamenti "beni e servizi"
senza partita IVA. L'indirizzo PayPal NON compare sul sito: il cliente lo
vede solo dentro la richiesta che gli mandi tu. (Riferimento in
`docs/LISTINO.md`.)

---

## 4) Email — consegna finale (quando il gioco è pronto)

**Oggetto:** La vostra avventura è pronta 🕹💛

> Ciao [NOME]!
>
> Ci siamo: la vostra avventura è pronta. La trovate qui 👇
>
> 🔗 [LINK]
>
> Si apre da qualsiasi telefono, senza installare niente. In allegato
> trovate anche il **QR code** (se avete preso il biglietto stampabile, è
> pronto per la stampa). Consiglio: apritela con calma, insieme.
>
> Se qualcosa non torna, scrivetemi: sistemo subito. E se vi va, mandateci
> una foto mentre la giocate — ci fa più felici di quanto immaginiate.
>
> Grazie di aver scelto SempreAddue da founder 🕹
> — SempreAddue · *Un posto a due. Per sempre.*

---

## Promemoria
- **Ricopia le cifre dai campi RIEPILOGO** dell'email d'ordine: non
  rifare i conti a mano, eviti errori.
- Manda la richiesta PayPal **solo dopo il loro «ok»** sul preventivo.
- Non avviare `consegna --push` prima che il pagamento risulti ricevuto.
- Soglia test: primi 5–10 ordini, poi valutazione col commercialista
  prima di continuare (vedi `docs/LISTINO.md`).
