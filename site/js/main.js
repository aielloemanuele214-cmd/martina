/* Sempreaddue — landing page
   Vanilla JS: header, menu mobile, stelle, parallasse, reveal, galleria, demo lazy. */
(() => {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header: sfondo al primo scroll ---------- */
  const header = $('#header');
  const onScroll = () => header.classList.toggle('scrolled', scrollY > 12);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Menu mobile ---------- */
  const toggle = $('#navToggle');
  const links = $('#navLinks');
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Chiudi il menu' : 'Apri il menu');
  });
  links.addEventListener('click', (e) => {
    if (e.target.closest('a')) {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  /* ---------- Stelle nel cielo dell'hero ---------- */
  const stars = $('#stars');
  if (stars && !reduceMotion) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < 40; i++) {
      const s = document.createElement('i');
      // posizioni pseudo-casuali ma deterministiche (niente layout shift tra visite)
      const t = i * 137.508; // angolo aureo
      s.style.left = (t % 100) + '%';
      s.style.top = ((t * 0.61803) % 62) + '%';
      s.style.animationDelay = (i % 10) * -0.35 + 's';
      s.style.opacity = 0.2 + (i % 5) * 0.12;
      frag.appendChild(s);
    }
    stars.appendChild(frag);
  }

  /* ---------- Parallasse leggera sull'hero (GPU, solo desktop con puntatore) ---------- */
  const visual = $('[data-parallax]');
  if (visual && !reduceMotion && matchMedia('(pointer: fine)').matches) {
    let raf = 0;
    addEventListener('scroll', () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const y = Math.min(scrollY, innerHeight);
        visual.style.transform = `translate3d(0, ${y * 0.08}px, 0)`;
      });
    }, { passive: true });
  }

  /* ---------- Reveal allo scroll ---------- */
  const revealEls = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      }
    }, { threshold: 0.15, rootMargin: '0px 0px -40px' });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  /* ---------- Galleria: frecce + dots sincronizzati con lo scroll-snap ---------- */
  const track = $('#galTrack');
  if (track) {
    const items = $$('.gal-item', track);
    const dots = $('#galDots');
    items.forEach((_, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', `Vai all'immagine ${i + 1} di ${items.length}`);
      b.addEventListener('click', () => goTo(i));
      dots.appendChild(b);
    });
    const dotBtns = $$('button', dots);

    const current = () => {
      const center = track.scrollLeft + track.clientWidth / 2;
      let best = 0, dist = Infinity;
      items.forEach((it, i) => {
        const d = Math.abs(it.offsetLeft + it.offsetWidth / 2 - center);
        if (d < dist) { dist = d; best = i; }
      });
      return best;
    };
    const paint = () => {
      const c = current();
      dotBtns.forEach((d, i) => d.setAttribute('aria-current', String(i === c)));
    };
    const goTo = (i) => {
      const it = items[Math.max(0, Math.min(items.length - 1, i))];
      track.scrollTo({
        left: it.offsetLeft - (track.clientWidth - it.offsetWidth) / 2,
        behavior: reduceMotion ? 'auto' : 'smooth'
      });
    };
    $('#galPrev').addEventListener('click', () => goTo(current() - 1));
    $('#galNext').addEventListener('click', () => goTo(current() + 1));
    let raf = 0;
    track.addEventListener('scroll', () => {
      if (raf) return;
      raf = requestAnimationFrame(() => { raf = 0; paint(); });
    }, { passive: true });
    paint();
  }

  /* ---------- Demo: l'iframe (≈4,5 MB) viene caricato solo su richiesta ---------- */
  const start = $('#demoStart');
  if (start) {
    // il video di gameplay parte solo quando la sezione è visibile (e mai con reduced motion)
    const video = $('.demo-video', start);
    if (video && !reduceMotion && 'IntersectionObserver' in window) {
      const vio = new IntersectionObserver((entries) => {
        for (const e of entries) {
          if (e.isIntersecting) video.play().catch(() => {});
          else video.pause();
        }
      }, { threshold: 0.3 });
      vio.observe(video);
    } else if (video) {
      video.remove(); // resta il poster statico
    }
    start.addEventListener('click', () => {
      const frame = $('#demoFrame');
      const label = $('.demo-poster-label', start);
      const play = $('.demo-play', start);
      if (label) label.textContent = 'Caricamento…';
      if (play) play.style.display = 'none';
      const iframe = document.createElement('iframe');
      iframe.src = 'demo.html';
      iframe.title = 'Demo giocabile di Sempreaddue — Il Villaggio Incantato';
      iframe.allow = 'autoplay; fullscreen';
      // il poster resta visibile finché il gioco (≈4,5 MB) non è pronto;
      // niente replaceChildren: spostare un iframe nel DOM lo ricaricherebbe
      iframe.addEventListener('load', () => {
        video?.pause();
        start.remove();
        iframe.style.visibility = '';
        iframe.focus();
      });
      iframe.style.visibility = 'hidden';
      frame.appendChild(iframe);
    }, { once: true });
  }
})();
