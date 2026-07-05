# Checklist QA su dispositivo reale (~10 minuti)

Apri il link della build sul telefono e spunta ogni voce.
Fondamentale farla almeno una volta su **iPhone/Safari** prima della 1.0.

## Avvio
- [ ] La splash appare con titolo e nomi, "TOCCA PER ENTRARE" lampeggia
- [ ] Il tocco fa entrare nella stanza con dissolvenza (niente doppio tap zoom)
- [ ] Nessuna barra bianca ai bordi; la stanza riempie lo schermo

## Movimento
- [ ] La levetta risponde subito, senza scatti, in tutte le direzioni
- [ ] Camminata fluida: laterale, schiena, frontale animate
- [ ] Trascinando fuori dalla levetta il personaggio si ferma correttamente
- [ ] Non ci si incastra: bordo letto, strettoia letto-tavolino, angoli scrivania
- [ ] Il corridoio dietro il letto è percorribile e lei diventa semi-trasparente

## Interazioni
- [ ] Tap su un ✨ da vicino apre la sorpresa; bottone ❤ visibile quando sei vicino
- [ ] La lettera si scrive da sola; un tocco la completa; "Chiudi" funziona al primo colpo
- [ ] Dialogo con lui: ritratto visibile, si avanza toccando, si chiude a fine battute
- [ ] Tap sul gatto da lontano: si sveglia, alone dorato, quinto cuore 💛 nel contatore
- [ ] Giradischi dopo la prima sorpresa (🎶): parte il ballo col valzer; un tocco lo ferma
- [ ] Tap sul cielo della finestra: scena fuochi con i due di spalle; un tocco chiude

## Audio (iPhone in particolare)
- [ ] Dopo l'ingresso dalla splash gli SFX si sentono (passi, scoperta, miao)
- [ ] Con la suoneria fisica in silenzioso: comportamento accettabile (iOS può tacere)
- [ ] Il valzer del ballo parte e si ferma con la scena
- [ ] Bottone 🔊 silenzia e riattiva
- [ ] Bloccando/riattivando lo schermo il gioco riprende senza audio impazzito

## Finale e salvataggio
- [ ] Trovate tutte le sorprese parte il finale con pioggia di cuori
- [ ] Contatore giorni corretto (se dataInizio impostata)
- [ ] Chiudendo e riaprendo il link i progressi restano
- [ ] `?reset=1` azzera tutto

## Robustezza
- [ ] Ruotando lo schermo il layout si riadatta senza rompersi
- [ ] Ricevendo una notifica/chiamata e tornando, il gioco riprende
- [ ] 5 minuti di gioco continuo: niente lag crescente o surriscaldamento anomalo
