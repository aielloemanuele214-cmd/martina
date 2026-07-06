/* ---------- finale ---------- */
const finaleEl=document.getElementById('finale');
function showFinale(){
  if(diagOpen) closeDialog();
  finaleShown=true; frozen=true; save(); vibra([60,60,120]);
  finaleEl.querySelectorAll('.fh').forEach(h=>h.remove());
  finaleEl.querySelector('h2').textContent=CONFIG.finale.titolo;
  finaleEl.querySelector('.testo').textContent=CONFIG.finale.testo;
  // contatore "insieme da X giorni"
  const gEl=finaleEl.querySelector('.giorni');
  if(CONFIG.dataInizio){
    const g=Math.max(0, Math.floor((Date.now()-new Date(CONFIG.dataInizio+'T00:00:00'))/864e5));
    gEl.textContent=`INSIEME DA ${g.toLocaleString('it-IT')} GIORNI ❤`;
  } else gEl.textContent='';
  // contatore segreti (gatto, finestra, ballo, contratto): X/4
  const trovati=[cat.trovato, windowSeen, danceDone, contractDone].filter(Boolean).length;
  const segEl=finaleEl.querySelector('.segreti');
  if(trovati>=SEGRETI_TOTALE){
    segEl.innerHTML=`<span class="cnt">SEGRETI ${trovati}/${SEGRETI_TOTALE}</span>`+
      'Complimenti!\nHai scoperto tutti i segreti di questa avventura. ❤️';
  } else {
    segEl.innerHTML=`<span class="cnt">SEGRETI ${trovati}/${SEGRETI_TOTALE}</span>`+
      `Hai trovato ${trovati}/${SEGRETI_TOTALE} segreti.\nRicomincia per scoprirli tutti.\n`+
      '💡 Indizio: prova a modificare l’ordine delle interazioni.';
  }
  // pioggia di cuori
  for(let i=0;i<26;i++){
    const h=document.createElement('div');
    h.className='fh'; h.textContent=['❤️','💕','💗','✨'][i%4];
    h.style.left=Math.random()*100+'%';
    h.style.animationDuration=(4+Math.random()*5)+'s';
    h.style.animationDelay=(Math.random()*4)+'s';
    h.style.fontSize=(15+Math.random()*16)+'px';
    finaleEl.appendChild(h);
  }
  finaleEl.classList.add('show');
  audio.sfx('fanfare');
}
const SEGRETI_TOTALE=4;
finaleEl.querySelector('.resta').addEventListener('click', ()=>{
  finaleEl.classList.remove('show'); frozen=false; setState('idle'); audio.sfx('click');
});
finaleEl.querySelector('.ricomincia').addEventListener('click', ()=>{ audio.sfx('click'); resetRun(); });
// Ricomincia: riavvia la partita SENZA ricaricare — TUTTO torna allo stato iniziale,
// segreti compresi (gatto 💛, finestra, ballo, contratto): contatore da 0
function resetRun(){
  finaleEl.classList.remove('show');
  finaleEl.querySelectorAll('.fh').forEach(h=>h.remove());
  if(modalOpen) closePopup(); if(diagOpen) closeDialog();
  for(let i=0;i<found.length;i++) found[i]=false;
  npc.talked=false; finaleShown=false; interacted=false;
  cat.trovato=false; cat.purrDone=false; cat.awakeUntil=0;
  windowSeen=false; danceDone=false; contractDone=false;
  npc.frame=0; diagEmo=0;
  percorso.length=0; pendInter=null; parts.length=0; luiBag=[]; luiLast=-1;
  player.x=CONFIG.posizioni.lei.x; player.y=CONFIG.posizioni.lei.y; player.dir='down';
  setState('idle'); camInit=false;
  frozen=false;
  updateHearts(); save();
  document.getElementById('hint').classList.remove('hide');
  setTimeout(()=>document.getElementById('hint').classList.add('hide'), 6000);
}

/* ---------- HUD ---------- */
function updateHearts(){
  const el=document.getElementById('hearts');
  el.innerHTML=CONFIG.sorprese.map((s,i)=>`<span class="${found[i]?'':'off'}">❤️</span>`).join('')
    + (cat.trovato?'<span class="oro">💛</span>':'');
}
// col gioco completato, un tocco sul contatore rivede il finale
document.getElementById('hearts').addEventListener('pointerdown', e=>{
  e.stopPropagation();
  if(found.every(Boolean) && !frozen) showFinale();
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

