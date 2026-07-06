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

  /* preselezione pacchetto da ?pacchetto=base|plus|sumisura */
  const pkg = new URLSearchParams(location.search).get('pacchetto');
  const pkgMap = { base: 'Base', plus: 'Plus', sumisura: 'Su misura' };
  if (pkg && pkgMap[pkg]) {
    const radio = [...form.querySelectorAll('input[name="pacchetto"]')]
      .find((r) => r.value.startsWith(pkgMap[pkg]));
    if (radio) radio.checked = true;
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
    const chk = (form.querySelector('input[name="occasione"]:checked') || {}).value || '—';
    const pk = (form.querySelector('input[name="pacchetto"]:checked') || {}).value || '—';
    box.innerHTML =
      `<h3>Riepilogo</h3>
       <p><b>${chk}</b> · pacchetto <b>${pk}</b></p>
       <p>${v('nome-tuo') || '—'} &amp; ${v('nome-partner') || '—'}` +
      (v('scadenza') ? ` · consegna entro <b>${v('scadenza')}</b>` : '') + `</p>`;
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
