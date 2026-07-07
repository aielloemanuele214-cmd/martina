/* Sempreaddue — form d'ordine multi-step */
(() => {
  'use strict';

  const form = document.getElementById('orderForm');
  const steps = [...form.querySelectorAll('.step')];
  const dots = [...document.querySelectorAll('.steps-dot')];
  const lines = [...document.querySelectorAll('.steps-line')];
  const label = document.getElementById('stepLabel');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnSend = document.getElementById('btnSend');
  const NAMES = ['L’occasione', 'Voi due', 'I dettagli', 'Come ricontattarti'];
  let current = 0;

  /* Totale in tempo reale. Listino pieno (19,50 € base + extra a prezzo
     pieno); il codice founder vale −50% sull'INTERO totale, extra compresi
     — stessa promessa del popup e del carosello social. Il riepilogo coi
     conti fatti viaggia anche nell'email (campi nascosti RIEPILOGO) e sulla
     pagina Grazie (localStorage): il cliente e noi leggiamo le stesse cifre. */
  const BASE = 19.5;
  const PROMO = { codice: 'FOUNDER26', sconto: 0.5 };
  const euro = (n) => n.toFixed(2).replace('.', ',') + ' €';
  const righeExtra = () => {
    const r = [];
    const nFoto = Math.max(0, Number(form.elements['foto-reali']?.value) || 0);
    const nSprite = Math.max(0, Number(form.elements['sprite-extra']?.value) || 0);
    if (nFoto) r.push([`${nFoto} foto real${nFoto === 1 ? 'e' : 'i'}`, nFoto * 1]);
    if (nSprite) r.push([`${nSprite} personagg${nSprite === 1 ? 'io' : 'i'} in più`, nSprite * 6]);
    if (form.elements['qr-stampabile']?.checked) r.push(['Biglietto QR da stampare', 10]);
    return r;
  };
  const subtotale = () => BASE + righeExtra().reduce((s, [, v]) => s + v, 0);
  const promoValido = () =>
    (form.elements['codice-promo']?.value || '').trim().toUpperCase() === PROMO.codice;
  const totaleFinale = () => subtotale() * (promoValido() ? 1 - PROMO.sconto : 1);

  const paintTotal = () => {
    const el = document.getElementById('orderTotal');
    if (!el) return;
    el.innerHTML = promoValido()
      ? `<s>${euro(subtotale())}</s> ${euro(totaleFinale())}`
      : euro(totaleFinale());
  };
  const paintPromo = () => {
    const fb = document.getElementById('promoFeedback');
    const val = (form.elements['codice-promo']?.value || '').trim();
    if (!fb) return;
    fb.hidden = !val;
    if (val) {
      if (promoValido()) {
        fb.textContent = `✓ Codice founder valido — −50% applicato su tutto: ${euro(totaleFinale())}`;
        fb.className = 'promo-feedback ok';
      } else {
        fb.textContent = 'Codice non riconosciuto — il totale resta a prezzo pieno';
        fb.className = 'promo-feedback no';
      }
    }
    paintTotal();
    recap();
  };

  /* I campi nascosti RIEPILOGO finiscono nella tabella dell'email:
     chi legge l'ordine trova i conti già fatti, riga per riga. */
  const syncEmailRecap = () => {
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
    const extra = righeExtra();
    const codice = (form.elements['codice-promo']?.value || '').trim();
    set('rBase', euro(BASE));
    set('rExtra', extra.length ? extra.map(([n, v]) => `${n} = ${euro(v)}`).join(' · ') : 'nessuno');
    set('rSubtotale', euro(subtotale()));
    set('rPromo', promoValido()
      ? `${PROMO.codice} valido → −50% (−${euro(subtotale() * PROMO.sconto)})`
      : codice ? `«${codice}» NON riconosciuto — nessuno sconto applicato` : 'non inserito');
    set('rTotale', euro(totaleFinale()));
  };

  form.addEventListener('input', (e) => {
    if (e.target.matches('[data-prezzo]')) { paintTotal(); recap(); }
    if (e.target.name === 'codice-promo') paintPromo();
    if (e.target.name === 'foto-reali') paintFotoField();
  });

  /* Caricamento foto: il campo compare solo se è stata dichiarata almeno
     1 foto extra; il numero che conta per il prezzo resta quello dichiarato
     sopra — le foto caricate qui in più vengono scelte/scartate a nostra
     discrezione (vedi la nota in fondo al form). Max 5 file per invio. */
  const MAX_FOTO_FILE = 5;
  const fotoField = document.getElementById('fotoUploadField');
  const fotoInput = document.getElementById('fotoInput');
  const fotoHint = document.getElementById('fotoHint');

  const paintFotoField = () => {
    if (!fotoField) return;
    const n = Number(form.elements['foto-reali']?.value) || 0;
    fotoField.hidden = n <= 0;
  };

  if (fotoInput) {
    fotoInput.addEventListener('change', () => {
      let files = [...fotoInput.files];
      if (files.length > MAX_FOTO_FILE) {
        const dt = new DataTransfer();
        files.slice(0, MAX_FOTO_FILE).forEach((f) => dt.items.add(f));
        fotoInput.files = dt.files;
        files = [...fotoInput.files];
        fotoHint.textContent = `Hai selezionato più di ${MAX_FOTO_FILE} foto: abbiamo tenuto le prime ${MAX_FOTO_FILE}. Le altre mandacele via email a sempreaddue@gmail.com.`;
        fotoHint.className = 'foto-hint warn';
      } else if (files.length) {
        const mb = (files.reduce((s, f) => s + f.size, 0) / 1024 / 1024).toFixed(1);
        fotoHint.textContent = `${files.length} foto selezionate (${mb} MB totali)`;
        fotoHint.className = 'foto-hint';
      } else {
        fotoHint.textContent = '';
      }
    });
  }

  const paint = () => {
    steps.forEach((s, i) => { s.hidden = i !== current; });
    dots.forEach((d, i) => {
      d.classList.toggle('active', i === current);
      d.classList.toggle('done', i < current);
    });
    lines.forEach((l, i) => l.classList.toggle('done', i < current));
    label.textContent = `Passo ${current + 1} di ${steps.length} · ${NAMES[current]}`;
    btnPrev.hidden = current === 0;
    btnNext.hidden = current === steps.length - 1;
    btnSend.hidden = current !== steps.length - 1;
    if (current === steps.length - 1) recap();
    steps[current].querySelector('input,textarea')?.focus({ preventScroll: true });
    scrollTo({ top: 0, behavior: 'smooth' });
  };

  const validStep = () => {
    const fields = [...steps[current].querySelectorAll('input,textarea')];
    for (const f of fields) {
      if (!f.checkValidity()) { f.reportValidity(); return false; }
    }
    return true;
  };

  const recap = () => {
    const v = (n) => (form.elements[n]?.value || '').trim();
    const box = document.getElementById('orderRecap');
    if (!box) return;
    const chk = (form.querySelector('input[name="occasione"]:checked') || {}).value || '—';
    const righe = [["L'Avventura — tutto incluso", BASE], ...righeExtra()];
    const conPromo = promoValido();
    let html = `<h3>Riepilogo del vostro ordine</h3>
      <p>${chk} · <b>${v('nome-tuo') || '—'} &amp; ${v('nome-partner') || '—'}</b>` +
      (v('scadenza') ? ` · consegna entro <b>${v('scadenza')}</b>` : '') + `</p>`;
    for (const [nome, val] of righe)
      html += `<p class="recap-row"><span>${nome}</span><span>${euro(val)}</span></p>`;
    if (conPromo) {
      html += `<p class="recap-row"><span>Subtotale</span><span>${euro(subtotale())}</span></p>`;
      html += `<p class="recap-row"><span>Codice ${PROMO.codice} · −50% su tutto</span><span>−${euro(subtotale() * PROMO.sconto)}</span></p>`;
    }
    if (fotoInput?.files.length)
      html += `<p class="recap-row"><span>${fotoInput.files.length} foto allegate</span><span>—</span></p>`;
    html += `<p class="recap-row recap-total"><span>TOTALE <small>(da confermare via email)</small></span><b>${euro(totaleFinale())}</b></p>`;
    box.innerHTML = html;
    syncEmailRecap();
  };

  btnNext.addEventListener('click', () => {
    if (!validStep()) return;
    current = Math.min(current + 1, steps.length - 1);
    paint();
  });
  btnPrev.addEventListener('click', () => {
    current = Math.max(current - 1, 0);
    paint();
  });
  form.addEventListener('submit', (e) => {
    if (!validStep()) { e.preventDefault(); return; }
    syncEmailRecap();
    /* la pagina Grazie rilegge questo riepilogo e lo mostra al cliente:
       le stesse cifre che arrivano a noi via email */
    try {
      const righe = [["L'Avventura — tutto incluso", euro(BASE)],
        ...righeExtra().map(([n, v]) => [n, euro(v)])];
      if (promoValido()) {
        righe.push(['Subtotale', euro(subtotale())]);
        righe.push([`Codice ${PROMO.codice} · −50% su tutto`, '−' + euro(subtotale() * PROMO.sconto)]);
      }
      localStorage.setItem('sad-ordine', JSON.stringify(
        { righe, totale: euro(totaleFinale()), ts: Date.now() }));
    } catch { /* storage pieno o negato: la pagina Grazie farà senza */ }
  });

  paintFotoField();
  paintTotal();
  paint();
})();
