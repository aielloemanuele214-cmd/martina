# SempreAddue — Archivio aziendale

Mini avventure grafiche in pixel art, personalizzate per ogni coppia e regalate
con un link o un QR. Questo repository è l'**archivio degli strumenti**
dell'azienda, diviso in 4 aree chiare.

---

## Le 4 aree

### 🌐 SITO — la radice → in vetrina su **https://sempreaddue.netlify.app**
Le pagine pubbliche stanno alla radice della repo (Netlify pubblica da qui a
ogni push):
- `index.html` — la landing · `ordina.html` — il modulo d'ordine ·
  `grazie.html` — pagina post-ordine · `privacy.html` · `demo.html` — la demo giocabile
- `site/` — css, javascript, immagini, font del sito
- meta: `robots.txt`, `sitemap.xml`, `site.webmanifest`, `_redirects`

### 🎮 GIOCO — motore + produzione → cartella **`gioco/`**
Tutto ciò che serve a costruire e consegnare un'avventura:
- `gioco/engine/` — il motore (codice versionato, **mai** modificato per un cliente)
- `gioco/packs/` — i template per occasione (romantica, compleanno, proposta, …)
- `gioco/tools/` — la CLI `sad.py` (build, QA, consegna) + pipeline sprite/musica
- `gioco/clienti/` — gli ordini (in pubblico solo gli esempi; i reali restano privati)
- `gioco/assets/` — grafica e audio del motore

→ Guida operativa: **`docs/README-PRODUZIONE.md`**

### 🎁 GIOCHI CONSEGNATI → repo **privata** separata `sempreaddue-giochi`
I giochi finiti dei clienti (con foto e messaggi reali) vivono in una repository
**privata**, pubblicati da **Cloudflare Pages** a link segreti e permanenti
(`sempreaddue-giochi.pages.dev/g/<token>`). Non stanno mai in questa repo pubblica.

### 📣 SOCIAL & MARKETING → cartella **`social/`**
Caroselli, post, bio, hashtag, kit di branding e i generatori delle grafiche.
→ Guida: **`social/README.md`**

---

## 📚 Documenti — cartella `docs/`

| File | A cosa serve |
|---|---|
| `README-PRODUZIONE.md` | come costruire e consegnare un'avventura, passo-passo |
| `GENERAZIONE-ASSET.md` | specifiche per generare gli sprite/asset con l'AI |
| `CHECKLIST-QA.md` | i controlli sul telefono prima di consegnare |
| `LISTINO.md` | catalogo, prezzi, modello founder, pagamenti PayPal |
| `RISPOSTA-FOUNDER.md` | email pronta per chi richiede il codice founder |
| `RISPOSTA-PREVENTIVO.md` | email preventivo → richiesta pagamento → consegna |

## 🗄️ Archivio — cartella `archivio/`
Materiale storico, non più operativo ma conservato: `ARCHITETTURA.md` (piano di
refactoring, ormai realizzato), `ROADMAP.md` e `VALIDAZIONE.md` (percorso verso
la 1.0), `legacy/` (il primo prototipo). Non serve per lavorare oggi.

---

## Come si fa — le operazioni di ogni giorno

- **Pubblicare un post** → grafiche e testi in `social/` (parti dal kit: `social/README.md`)
- **Ricevere un ordine** → arriva via email (FormSubmit) dal modulo del sito
- **Rispondere a un founder** → `docs/RISPOSTA-FOUNDER.md`
- **Fare un preventivo** → `docs/RISPOSTA-PREVENTIVO.md`
- **Costruire e consegnare un gioco** → `cd gioco`, poi segui `docs/README-PRODUZIONE.md`
  (in breve: `python3 tools/sad.py ordine <slug>` → compili → `consegna <slug> --push`)

## Le due repository

| Repo | Cosa contiene | Visibilità | Hosting |
|---|---|---|---|
| **`martina`** (questa) | sito + motore + produzione + social + documenti | pubblica | sito su Netlify |
| **`sempreaddue-giochi`** | i giochi consegnati ai clienti | **privata** | Cloudflare Pages |

*Nota: il nome tecnico della repo pubblica è ancora `martina` (il primo gioco);
il brand è SempreAddue.*
