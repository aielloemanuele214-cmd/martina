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

  /* totale in tempo reale: base 19,50 € + extra, −50% col codice promo */
  const BASE = 19.5;
  const PROMO = { codice: 'FOUNDER26', sconto: 0.5 };
  const euro = (n) => n.toFixed(2).replace('.', ',') + ' €';
  const totale = () => {
    let t = BASE;
    for (const el of form.querySelectorAll('[data-prezzo]')) {
      const unit = Number(el.dataset.prezzo);
      if (el.type === 'checkbox') t += el.checked ? unit : 0;
      else t += unit * Math.max(0, Number(el.value) || 0);
    }
    return t;
  };
  const promoValido = () =>
    (form.elements['codice-promo']?.value || '').trim().toUpperCase() === PROMO.codice;
  const paintTotal = () => {
    const el = document.getElementById('orderTotal');
    if (el) el.textContent = euro(totale());
  };
  const paintPromo = () => {
    const fb = document.getElementById('promoFeedback');
    const val = (form.elements['codice-promo']?.value || '').trim();
    if (!fb) return;
    fb.hidden = !val;
    if (!val) return;
    if (promoValido()) {
      fb.textContent = '✓ Codice valido: −50% sul totale';
      fb.className = 'promo-feedback ok';
    } else {
      fb.textContent = 'Codice non riconosciuto';
      fb.className = 'promo-feedback no';
    }
    recap();
  };
  form.addEventListener('input', (e) => {
    if (e.target.matches('[data-prezzo]')) paintTotal();
    if (e.target.name === 'codice-promo') paintPromo();
  });

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
    const chk = (form.querySelector('input[name="occasione"]:checked') || {}).value || '—';
    const extras = [];
    const nFoto = Number(v('foto-reali')) || 0;
    const nSprite = Number(v('sprite-extra')) || 0;
    if (nFoto) extras.push(`${nFoto} foto reali`);
    if (nSprite) extras.push(`${nSprite} personaggi in più`);
    if (form.elements['qr-stampabile']?.checked) extras.push('biglietto QR da stampare');
    const t = totale();
    const conPromo = promoValido();
    const riga = conPromo
      ? `<s>${euro(t)}</s> <b>${euro(t * (1 - PROMO.sconto))}</b> <small>(codice ${PROMO.codice}: −50%)</small>`
      : `<b>${euro(t)}</b>`;
    box.innerHTML =
      `<h3>Riepilogo</h3>
       <p><b>${chk}</b> · L'Avventura 19,50 €` +
      (extras.length ? ` + ${extras.join(' + ')}` : '') + `</p>
       <p>${v('nome-tuo') || '—'} &amp; ${v('nome-partner') || '—'}` +
      (v('scadenza') ? ` · consegna entro <b>${v('scadenza')}</b>` : '') +
      ` · totale ${riga}</p>`;
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
    if (!validStep()) e.preventDefault();
  });

  paint();
})();
