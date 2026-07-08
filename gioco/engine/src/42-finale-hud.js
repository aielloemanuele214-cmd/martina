/* ---------- finale (a regole: STORY.finali) ---------- */
const finaleEl=document.getElementById('finale');
// Aprendo con una regola vera (auto a fine gioco, o passata esplicitamente)
// è il vero finale. Aprendo SENZA regola (tap sui cuori) e la partita non è
// ancora completa, si mostra comunque una schermata di stato: dà sempre
// accesso a "Resta qui"/"Ricomincia", anche a metà avventura.
function showFinale(regola){
  const auto = regola || matchEnding();
  const completo = !!auto;
  regola = auto || { titolo:'', testo: STORY.ui.inCorso || '' };
  if(diagOpen) closeDialog();
  if(completo){ setFlag('finaleMostrato'); vibra([60,60,120]); }
  frozen=true;
  finaleEl.querySelectorAll('.fh').forEach(h=>h.remove());
  finaleEl.querySelector('h2').textContent=String(risolvi(regola.titolo)??'');
  finaleEl.querySelector('.testo').textContent=String(risolvi(regola.testo)??'');
  // contatore "insieme da X giorni"
  const gEl=finaleEl.querySelector('.giorni');
  if(CONFIG.dataInizio){
    const g=Math.max(0, Math.floor((Date.now()-new Date(CONFIG.dataInizio+'T00:00:00'))/864e5));
    gEl.textContent=STORY.ui.giorni.replace('{g}', g.toLocaleString('it-IT'));
  } else gEl.textContent='';
  // contatore segreti (dichiarati in STORY.segreti)
  const tot=STORY.segreti.length;
  const trovati=STORY.segreti.filter(s=>flag(s.flag)).length;
  const segEl=finaleEl.querySelector('.segreti');
  const msg=(trovati>=tot?STORY.ui.segretiCompleti:STORY.ui.segretiParziali)
    .replaceAll('{n}',trovati).replaceAll('{tot}',tot);
  segEl.innerHTML=`<span class="cnt">SEGRETI ${trovati}/${tot}</span>`+msg;
  // pioggia di cuori: solo a partita davvero completa (altrimenti sembrerebbe un finale)
  if(completo) for(let i=0;i<26;i++){
    const h=document.createElement('div');
    h.className='fh'; h.textContent=['❤️','💕','💗','✨'][i%4];
    h.style.left=Math.random()*100+'%';
    h.style.animationDuration=(4+Math.random()*5)+'s';
    h.style.animationDelay=(Math.random()*4)+'s';
    h.style.fontSize=(15+Math.random()*16)+'px';
    finaleEl.appendChild(h);
  }
  finaleEl.classList.add('show');
  if(completo) audio.sfx('fanfare'); else audio.sfx('click');
}
finaleEl.querySelector('.resta').addEventListener('click', ()=>{
  finaleEl.classList.remove('show'); frozen=false; setState('idle'); audio.sfx('click');
});
finaleEl.querySelector('.ricomincia').addEventListener('click', ()=>{ audio.sfx('click'); resetRun(); });
// Ricomincia: riavvia la partita SENZA ricaricare — l'intero state-bag torna vuoto
// (indizi, segreti, eventi una-tantum), e il salvataggio viene azzerato
function resetRun(){
  finaleEl.classList.remove('show');
  finaleEl.querySelectorAll('.fh').forEach(h=>h.remove());
  if(modalOpen) closePopup(); if(diagOpen) closeDialog();
  clearBag();
  cat.awakeUntil=0;
  npc.frame=0; diagEmo=0;
  starFx=null; player.fermoT=0; cine.scene=null; audio.stopDance();
  for(const k in bags) delete bags[k];
  percorso.length=0; pendInter=null; parts.length=0;
  player.x=CONFIG.posizioni.lei.x; player.y=CONFIG.posizioni.lei.y; player.dir='down';
  setState('idle'); camInit=false;
  frozen=false;
  updateHearts(); save();
  document.getElementById('hint').classList.remove('hide');
  setTimeout(()=>document.getElementById('hint').classList.add('hide'), 6000);
}

/* ---------- HUD: un cuore per sorpresa + le ricompense dei segreti ---------- */
function updateHearts(){
  const el=document.getElementById('hearts');
  el.innerHTML=CONFIG.sorprese.map(s=>`<span class="${flag('trovato.'+s.id)?'':'off'}">❤️</span>`).join('')
    + STORY.segreti.filter(s=>s.hud && flag(s.flag)).map(s=>`<span class="oro">${s.hud}</span>`).join('');
}
// un tocco sul contatore apre sempre lo stato di partita: il vero finale se
// completa, altrimenti il progresso — con "Resta qui"/"Ricomincia" comunque
// accessibili in ogni momento (anche a metà avventura)
document.getElementById('hearts').addEventListener('pointerdown', e=>{
  e.stopPropagation();
  if(!frozen) showFinale();
});
// audio in pausa quando la pagina va in background
document.addEventListener('visibilitychange', ()=>{
  if(document.hidden){
    if(audio.ctx) audio.ctx.suspend();
    musMenu.pause(); musGame.pause();
  } else if(started && !audio.muted){
    if(audio.ctx) audio.ctx.resume();
    if(CONFIG.musica) (inGioco?musGame:musMenu).play().catch(()=>{});
  }
});
document.getElementById('mute').addEventListener('click', function(e){
  e.stopPropagation();
  const m=audio.toggle(); this.textContent=m?'🔇':'🔊';
});
document.getElementById('fs').addEventListener('click', function(e){
  e.stopPropagation();
  if(document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen?.().catch(()=>{});
});
const actionEl=document.getElementById('action');
let lastAB='';
actionEl.addEventListener('pointerdown', e=>{
  e.stopPropagation(); e.preventDefault(); firstGesture(); pressInteract();
});

/* ---------- particelle cuore ---------- */
const parts=[];
function burst(px,py,n){
  for(let i=0;i<n;i++)
    parts.push({x:px+(Math.random()-.5)*4, y:py+(Math.random()-.5)*2,
      vy:-(4+Math.random()*5), sway:Math.random()*Math.PI*2, life:1});
}

/* ---------- musica al primo gesto ---------- */
let started=false;
function firstGesture(){
  if(started) return; started=true;
  audio.init();                       // sblocca l'audio su iOS dentro il gesto
}
