# Sempreaddue — guida di produzione

Il prodotto è **un solo file**: `stanza.html`. Contiene motore, grafica e
audio incorporati (base64), funziona offline e su qualunque hosting statico.

## Flusso per ogni ordine (5 minuti)

1. **Copia** `clienti/esempio.json` → `clienti/nome-cliente.json`
2. **Compila** i campi col materiale del cliente (nomi, dialoghi, testi
   delle sorprese, data di inizio, dedica finale). Per le foto nelle
   sorprese usa `"foto": "file:foto/nomefile.jpg"` (percorso relativo al
   JSON — le immagini vengono incorporate in automatico).
3. **Genera**: `python3 build.py clienti/nome-cliente.json`
   → esce `dist/stanza-nome-cliente.html`
4. **Verifica** aprendo il file nel browser (anche da telefono) e con
   `?debug=1` se hai spostato hotspot/posizioni.
5. **Pubblica**: trascina il file su [Netlify Drop](https://app.netlify.com/drop)
   (gratis) e genera il QR del link da regalare.

## Cosa si personalizza dal JSON (senza toccare il codice)

| Campo | Cosa cambia | Tier suggerito |
|---|---|---|
| `nomi`, `titolo` | nomi della coppia | Base |
| `dialoghi` | battute di lui | Base |
| `sorprese[].titolo/testo` | contenuto delle 4 sorprese | Base |
| `dataInizio` | contatore "insieme da X giorni" nel finale | Base |
| `finale` | dedica finale | Base |
| `sorprese[].foto` | foto reali della coppia nelle card | **Plus** |
| `musica: true` | loop musicale 8-bit di sottofondo | **Plus** |
| `gatto.nome/messaggio` | l'animale di casa | Plus |
| `ballo.didascalia`, `fuochi.didascalia` | didascalie delle scene | Base |
| posizioni/raggi degli hotspot | layout delle sorprese | se serve |

## Personalizzazione grafica (sprite su misura — tier Plus)

Gli sprite sorgente stanno in `assets/sprites/`. Per una coppia con
aspetto personalizzato: genera le immagini con l'AI usando i prompt in
fondo a questa guida (allegando sempre lo sprite esistente come
riferimento di stile), poi ri-esegui la pipeline di slicing e ricostruisci
`stanza.html`. Le regole d'oro per le generazioni:

- PNG con **trasparenza reale** (no scacchiera disegnata, no sfondo sfumato)
- frame **equidistanti in fila orizzontale**, personaggio centrato, piedi visibili
- ciclo di camminata che si chiude: contatto → passo dx → contatto → passo sx

Set minimo per un personaggio giocabile: idle frontale (1 frame),
camminata laterale (4 frame), camminata di schiena (4 frame).
Per l'NPC bastano idle frontale + schiena statica.
Per il ballo: 5 pose di coppia abbracciata, fila orizzontale.

## Architettura (per chi mette le mani nel codice)

- `stanza.html` — prodotto completo. Il blocco tra `★★ INIZIO CONFIG ★★`
  e `★★ FINE CONFIG ★★` è l'unica parte che il builder sostituisce.
- Motore: canvas con cache pre-scalate (60fps su mobile), camera adattiva
  (stanza intera su desktop, zoom+follow su mobile), joystick fisso touch,
  collisioni su poligoni (`COLLIDERS`, editabili visivamente con `?debug=1`).
- Scene: dialoghi con ritratto, 4 sorprese + lettera a macchina da
  scrivere, ballo lento al giradischi, fuochi alla finestra, finale con
  contatore giorni.
- Audio: synth Web Audio (nessun file audio), valzer diegetico nel ballo.
- `build.py` + `clienti/*.json` — produzione copie clienti in `dist/`.

## Prompt di generazione sprite (da adattare)

> Pixel art sprite sheet, 32-bit era style (SNES/Stardew Valley quality).
> Same character as the reference image, identical outfit, hair and
> proportions. 4 walking animation frames side by side in a single
> horizontal row, evenly spaced, character centered in each frame, same
> size in every frame, full body with feet visible. [Front view / Back
> view / Side view walking left]. The frames form a seamless walk cycle.
> Transparent background, no checkerboard pattern, no background color or glow.
