/* ---------- dialoghi con ritratto ---------- */
const dialogEl=document.getElementById('dialog');
let diagLines=[], diagI=0, diagOpen=false, dialogEmotivo=false;
// Espressioni dell'NPC: SOLO event-driven. L'indice persiste tra i dialoghi e avanza
// di 1 a ogni interazione dell'utente → cicla tutti i frame, mai due volte lo stesso di fila.
let diagEmo=0;
function nextEmo(){
  diagEmo=(diagEmo+1)%ASSETS[SPR.npc.foglio].n;
  npc.frame=diagEmo;
  dialogEl.querySelector('.portrait').src=PORTRAITS_LUI[diagEmo];
}
function showDialog(nome, righe, opt){
  opt=opt||{};
  percorso.length=0; pendInter=null;
  diagLines=righe; diagI=0; diagOpen=true; frozen=true;
  dialogEmotivo=!!opt.emotivo;
  dialogEl.querySelector('.name').textContent=nome;
  if(opt.emotivo) nextEmo();                       // ogni tocco sull'NPC = nuova espressione
  else dialogEl.querySelector('.portrait').src = opt.portrait||'';
  dialogEl.querySelector('.text').textContent=righe[0];
  dialogEl.querySelector('.next').style.display = righe.length>1?'block':'none';
  dialogEl.classList.add('show');
  if(opt.face) facePoint(opt.face[0], opt.face[1]);
  setState('interact');
  audio.sfx('click');
}

/* Dialogo dichiarato in STORY.dialoghi:
   - modo "sacchetto": una riga a caso dalla fonte, mai ripetuta di fila
   - "righe": sequenza fissa (avanza al tocco)                              */
const bags={};
function apriDialogo(id){
  const d=STORY.dialoghi[id];
  if(!d) return;
  const versoPt=puntoDi(d.verso);
  let righe;
  if(d.modo==='sacchetto'){
    const fonte=risolvi(d.fonte)||[];
    const b=bags[id]||(bags[id]={resto:[],ultimo:-1});
    if(b.resto.length===0){
      b.resto=fonte.map((_,i)=>i);
      for(let i=b.resto.length-1;i>0;i--){ const j=Math.random()*(i+1)|0; [b.resto[i],b.resto[j]]=[b.resto[j],b.resto[i]]; }
      if(b.resto[0]===b.ultimo && b.resto.length>1){ [b.resto[0],b.resto[1]]=[b.resto[1],b.resto[0]]; }
    }
    const idx=b.resto.shift(); b.ultimo=idx;
    righe=[fonte[idx]];
  } else {
    righe=(d.righe||[]).map(r=>String(risolvi(r)));
  }
  showDialog(String(risolvi(d.nome)||''), righe,
    { emotivo:!!d.emotivo, portrait:risolvi(d.ritratto),
      face:versoPt?[versoPt.x,versoPt.y]:undefined });
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

/* ---------- popup quadrato ---------- */
const veil=document.getElementById('veil'), card=document.getElementById('card');
const cardPic=card.querySelector('.pic'), cardH2=card.querySelector('h2'), cardTesto=card.querySelector('.testo');
let modalOpen=false;
function openPopup(opt){
  percorso.length=0; pendInter=null;
  if(opt.face) facePoint(opt.face[0], opt.face[1]);
  if(opt.img){ cardPic.src=opt.img; cardPic.style.display='block'; }
  else cardPic.style.display='none';
  cardH2.textContent=opt.titolo||''; cardH2.style.display=opt.titolo?'block':'none';
  cardTesto.textContent=opt.testo||'';
  veil.classList.add('show'); modalOpen=true; frozen=true;
  setState('interact');
  audio.sfx(opt.sfx||'item');
}
function closePopup(){
  veil.classList.remove('show'); modalOpen=false; frozen=false;
  setState('idle');
  audio.sfx('click');
  maybeEnding();               // alla chiusura: se una regola di finale è vera → finale
}
card.querySelector('button').addEventListener('click', closePopup);

/* Sorpresa (indizio principale): segna il flag 'trovato.<id>' e apre il popup */
function apriSorpresa(id){
  const s=CONFIG.sorprese.find(x=>x.id===id);
  if(!s) return;
  setFlag('interagito');
  const primaVolta=!flag('trovato.'+id);
  setFlag('trovato.'+id);
  if(primaVolta){ vibra(40); burst(s.x,s.y,10); }
  openPopup({ img:s.img, titolo:s.titolo, testo:s.testo,
              sfx:primaVolta?'item':'click', face:[s.x,s.y] });
}
function closeAll(){
  if(cinematic) return;              // le cinematiche non si chiudono a mano
  if(modalOpen) closePopup();
  if(diagOpen) closeDialog();
}
