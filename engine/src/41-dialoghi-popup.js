/* ---------- dialoghi con ritratto ---------- */
const dialogEl=document.getElementById('dialog');
let diagLines=[], diagI=0, diagOpen=false, dialogEmotivo=false;
// Espressioni di lui: SOLO event-driven. L'indice persiste tra i dialoghi e avanza
// di 1 a ogni interazione dell'utente → cicla tutti i frame, mai due volte lo stesso di fila.
let diagEmo=0;
function nextEmo(){
  diagEmo=(diagEmo+1)%ASSETS.luiEmo.n;
  npc.frame=diagEmo;
  dialogEl.querySelector('.portrait').src=PORTRAITS_LUI[diagEmo];
}
function showDialog(nome, righe, opt){
  opt=opt||{};
  percorso.length=0; pendInter=null;
  diagLines=righe; diagI=0; diagOpen=true; frozen=true;
  dialogEmotivo=!!opt.emotivo;
  dialogEl.querySelector('.name').textContent=nome;
  if(opt.emotivo) nextEmo();                       // ogni tocco su Manu = nuova espressione
  else dialogEl.querySelector('.portrait').src = opt.portrait||'';
  dialogEl.querySelector('.text').textContent=righe[0];
  dialogEl.querySelector('.next').style.display = righe.length>1?'block':'none';
  dialogEl.classList.add('show');
  if(opt.face) facePoint(opt.face[0], opt.face[1]);
  setState('interact');
  audio.sfx('click');
}
// Manu: una frase spontanea a ogni tocco, mai ripetuta di fila (sacchetto mescolato)
let luiBag=[], luiLast=-1;
function openDialog(){
  interacted=true; npc.talked=true; save();
  if(luiBag.length===0){
    luiBag=CONFIG.dialoghi.map((_,i)=>i);
    for(let i=luiBag.length-1;i>0;i--){ const j=Math.random()*(i+1)|0; [luiBag[i],luiBag[j]]=[luiBag[j],luiBag[i]]; }
    if(luiBag[0]===luiLast && luiBag.length>1){ [luiBag[0],luiBag[1]]=[luiBag[1],luiBag[0]]; }
  }
  const idx=luiBag.shift(); luiLast=idx;
  showDialog(CONFIG.nomi.lui, [CONFIG.dialoghi[idx]], {emotivo:true, face:[npc.x,npc.y]});
}
function advanceDialog(){
  if(!diagOpen) return;
  diagI++;
  if(diagI>=diagLines.length){ closeDialog(); return; }
  if(dialogEmotivo) nextEmo();                     // avanzare il dialogo = nuova espressione
  dialogEl.querySelector('.text').textContent=diagLines[diagI];
  audio.sfx('click');
}
function closeDialog(){
  diagOpen=false; dialogEmotivo=false; frozen=false;
  npc.frame=0;                                     // fine dialogo → subito primo frame Idle
  dialogEl.classList.remove('show');
  setState('idle');
}
dialogEl.addEventListener('pointerdown', e=>{ e.stopPropagation(); if(!cinematic) advanceDialog(); });

/* ---------- gatto (segreto) ---------- */
function pokeCat(){
  const isFirst = !interacted;   // primissima interazione della partita?
  interacted=true;
  cat.awakeUntil=clock+5;
  facePoint(cat.x, cat.y);
  audio.sfx('meow');
  if(!cat.trovato){ cat.trovato=true; updateHearts(); vibra(40); }  // achievement 💛 invariato
  save();
  const mostra=()=>showDialog(CONFIG.gatto.nome, [cat.messaggio], {portrait:PORTRAIT_GATTO, face:[cat.x,cat.y]});
  if(isFirst && !cat.purrDone){
    // eccezione: fa le fusa e compaiono cuori, poi il messaggio (una sola volta)
    cat.purrDone=true; save();
    frozen=true; percorso.length=0; pendInter=null; setState('interact');
    burst(cat.x, cat.y-4, 14);
    setTimeout(()=>burst(cat.x, cat.y-4, 8), 380);
    setTimeout(mostra, 950);
  } else mostra();
}

/* ---------- popup quadrato (indizi principali + finestra) ---------- */
const veil=document.getElementById('veil'), card=document.getElementById('card');
const cardPic=card.querySelector('.pic'), cardH2=card.querySelector('h2'), cardTesto=card.querySelector('.testo');
let modalOpen=false, popupCb=null;
function openPopup(opt){
  percorso.length=0; pendInter=null;
  if(opt.face) facePoint(opt.face[0], opt.face[1]);
  if(opt.img){ cardPic.src=opt.img; cardPic.style.display='block'; }
  else cardPic.style.display='none';
  cardH2.textContent=opt.titolo||''; cardH2.style.display=opt.titolo?'block':'none';
  cardTesto.textContent=opt.testo||'';
  popupCb=opt.onClose||null;
  veil.classList.add('show'); modalOpen=true; frozen=true;
  setState('interact');
  audio.sfx(opt.sfx||'item');
}
function closePopup(){
  const cb=popupCb; popupCb=null;
  veil.classList.remove('show'); modalOpen=false; frozen=false;
  setState('idle');
  audio.sfx('click');
  if(cb) cb();
}
card.querySelector('button').addEventListener('click', closePopup);

function openSorpresa(i){
  interacted=true;
  const s=CONFIG.sorprese[i];
  const first=!found[i];
  found[i]=true;
  if(first){ updateHearts(); vibra(40); burst(s.x,s.y,10); save(); }
  openPopup({ img:s.img, titolo:s.titolo, testo:s.testo, sfx:first?'item':'click', face:[s.x,s.y],
    onClose:()=>{ if(found.every(Boolean) && !finaleShown) setTimeout(showFinale,500); } });
}
function closeAll(){
  if(cinematic) return;              // le cinematiche non si chiudono a mano
  if(modalOpen) closePopup();
  if(diagOpen) closeDialog();
}

