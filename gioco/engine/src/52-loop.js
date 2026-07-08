/* ---------- loop ---------- */
let last=0;
function loop(t){
  const dt=Math.min(.05,(t-last)/1000||0); last=t;
  update(dt); render();
  requestAnimationFrame(loop);
}

// se una posizione configurata cade dentro un mobile, trova il punto libero più vicino
function unstuck(p){
  if(!blocked(p.x,p.y)) return;
  for(let r=1;r<45;r++)
    for(let a=0;a<12;a++){
      const x=p.x+Math.cos(a/12*Math.PI*2)*r, y=p.y+Math.sin(a/12*Math.PI*2)*r;
      if(x>2&&x<98&&y>15&&y<97&&!blocked(x,y)){ p.x=x; p.y=y; return; }
    }
}

let ready=false;
function begin(){
  ready=true;
  loadSave();
  resize(); buildInter(); updateHearts();
  unstuck(player);
  buildGrid();                          // griglia per il punta-e-clicca
  document.title=CONFIG.titolo;
  const hintEl=document.getElementById('hint');
  hintEl.textContent =
    isTouch ? 'Tocca dove vuoi andare · i ✨ si aprono da soli'
            : 'Clicca dove vuoi andare · WASD/frecce · E per interagire';
  // splash: da "caricamento" a "tocca per entrare"
  const sp=document.getElementById('splash');
  document.getElementById('spTitolo').textContent=CONFIG.titolo;
  document.getElementById('spNomi').textContent=CONFIG.nomi.protagonista+' ❤ '+CONFIG.nomi.secondario;
  const entra=()=>{
    inGioco=true;
    firstGesture();                       // sblocca l'audio dentro il gesto (iOS)
    avviaMusicaGioco();                   // crossfade: Paper Lantern -> Warm Memories
    sp.classList.add('via');
    setTimeout(()=>sp.remove(), 1000);
    setTimeout(()=>hintEl.classList.add('hide'), 8000);
  };
  if(CONFIG.schermataIngresso===false){ entra(); }
  else {
    // menù a due tocchi: il primo sblocca l'audio e fa partire la musica del menù
    const enterEl=document.getElementById('spEnter');
    enterEl.textContent='TOCCA PER COMINCIARE';
    sp.classList.add('pronto');
    let spStato=0, spT=0;
    sp.addEventListener('pointerdown', ()=>{
      if(performance.now()-spT<220) return;   // evita il doppio-tocco accidentale
      spT=performance.now();
      if(spStato===0){
        spStato=1;
        firstGesture();
        avviaMusicaMenu();
        enterEl.textContent='ENTRA ❤';
        enterEl.classList.add('btn');
      } else entra();
    });
  }
  requestAnimationFrame(loop);
}
