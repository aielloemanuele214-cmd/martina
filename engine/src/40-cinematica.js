/* ============================================================
   CINEMATICA — fade al nero + testo typewriting (Promise-based)
   ============================================================ */
const cineEl=document.getElementById('cine'), cineTextEl=document.getElementById('cineText');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function fadeNero(on){ cineEl.classList.toggle('on', on); return wait(1050); }
function typeWrite(testo, cps){
  cps=cps||26;
  return new Promise(res=>{
    cineTextEl.textContent='';
    let n=0;
    const iv=setInterval(()=>{
      cineTextEl.textContent=testo.slice(0,++n);
      if(n%2===0 && testo[n-1]!=='\n' && testo[n-1]!==' ') audio.sfx('type');
      if(n>=testo.length){ clearInterval(iv); res(); }
    }, 1000/cps);
  });
}

/* ---------- interazione con un indizio principale ---------- */
function interactClue(i){
  interacted=true;
  const s=CONFIG.sorprese[i];
  // è questo l'ULTIMO indizio ancora da scoprire?
  const ultimo = !found[i] && found.every((f,j)=>j===i || f);
  if(ultimo && s.evento==='ballo' && !danceDone){ found[i]=true; updateHearts(); save(); scenaBallo(); return; }
  if(ultimo && s.evento==='contratto' && !contractDone){ found[i]=true; updateHearts(); save(); scenaContratto(); return; }
  openSorpresa(i);
}

/* ---------- SCENA DEL BALLO (cinematica, una sola volta) ---------- */
const dance={on:false, t:0};
async function scenaBallo(){
  if(diagOpen) closeDialog();
  percorso.length=0; pendInter=null;
  cinematic=true; frozen=true; setState('dance');
  danceDone=true; save();
  document.getElementById('hint').classList.add('hide');
  // 1. sfuma la musica ambiente + 2. fade al nero
  if(CONFIG.musica && !audio.muted) fadeAudio(musGame,0,1400);
  await fadeNero(true);
  // 3. "Ho una sorpresa per te…"
  await typeWrite(CONFIG.ballo.introTesto);
  await wait(1400);
  cineTextEl.textContent='';
  // 4. avvia il ballo e rivela la scena; musica dedicata (valzer)
  dance.on=true; dance.t=0; camInit=false;
  audio.startDance();
  await fadeNero(false);
  // 5. durata esatta
  await wait(CONFIG.ballo.durata*1000);
  // 6. fade al nero + stop musica
  await fadeNero(true);
  dance.on=false; audio.stopDance();
  // 7. "Ti amo"
  await typeWrite(CONFIG.ballo.outroTesto);
  await wait(1800);
  cineTextEl.textContent='';
  // 8. ritorno al gioco
  player.x=CONFIG.ballo.x-5; player.y=CONFIG.ballo.y+2; player.dir='down'; setState('idle'); camInit=false;
  await fadeNero(false);
  if(CONFIG.musica && !audio.muted){ musGame.play().catch(()=>{}); fadeAudio(musGame,.55,1600); }
  cinematic=false; frozen=false;
  concludi();
}

/* ---------- SEGRETO DEL CONTRATTO (cinematica, una sola volta) ---------- */
const contrattoEl=document.getElementById('contratto');
async function scenaContratto(){
  if(diagOpen) closeDialog();
  percorso=[]; pendInter=null;
  cinematic=true; frozen=true;
  contractDone=true; save();
  document.getElementById('hint').classList.add('hide');
  await fadeNero(true);
  await typeWrite(CONFIG.contratto.intro);
  await wait(1400);
  cineTextEl.textContent='';
  contrattoEl.classList.add('show');
  contrattoEl.querySelector('.foglio').scrollTop=0;
  audio.sfx('item');
}
contrattoEl.querySelector('.chiudi').addEventListener('click', async ()=>{
  contrattoEl.classList.remove('show');
  audio.sfx('click');
  await fadeNero(false);
  cinematic=false; frozen=false; setState('idle');
  concludi();
});

/* ---------- segreto FINESTRA (popup, come il gatto: nessun indicatore) ---------- */
function tryWindow(cssX,cssY){
  const wx=(cssX/S+camX)/PCT, wy=(cssY/S+camY)/PCT;
  if(wx>41 && wx<60 && wy>2 && wy<27){ openWindow(); return true; }
  return false;
}
function openWindow(){
  interacted=true;
  windowSeen=true; save();
  openPopup({ img:IMG_FINESTRA, titolo:'', testo:CONFIG.finestra.testo, face:[50,14] });
}

/* ---------- segreto GATTO (tocco diretto da qualsiasi distanza) ---------- */
function tryCat(cssX,cssY){
  const wx=(cssX/S+camX)/PCT, wy=(cssY/S+camY)/PCT;
  const w=cat.larghezza, h=w*ASSETS.gatto.fh/ASSETS.gatto.fw;
  if(wx>cat.x-w/2-1.5 && wx<cat.x+w/2+1.5 && wy>cat.y-h-2 && wy<cat.y+1.5){
    pokeCat(); return true;
  }
  return false;
}

/* dopo un evento dell'ultimo indizio: se tutti scoperti → finale */
function concludi(){
  if(found.every(Boolean) && !finaleShown) setTimeout(showFinale, 650);
}

