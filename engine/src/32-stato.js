/* ---------- stato di gioco ---------- */
// Macchina a stati del personaggio: 'idle' | 'walk' | 'interact' | 'dance'
const player = {
  x:CONFIG.posizioni.lei.x, y:CONFIG.posizioni.lei.y,
  dir:'down', state:'idle', animT:0, stuckT:0,
};
function setState(s){ if(player.state!==s){ player.state=s; player.animT=0; } }
function facePoint(tx,ty){
  const dx=tx-player.x, dy=ty-player.y;
  if(Math.abs(dx)>Math.abs(dy)) player.dir = dx<0?'left':'right';
  else player.dir = dy<0?'up':'down';
}
const npc = { x:CONFIG.posizioni.lui.x, y:CONFIG.posizioni.lui.y, talked:false, frame:0 };
const cat = { ...CONFIG.gatto, awakeUntil:0, trovato:false, purrDone:false };  // segreto 💛
const found = CONFIG.sorprese.map(()=>false);
let frozen = false;          // input bloccato (dialoghi/modali)
let cinematic = false;       // scena cinematica in corso: nessun input
let finaleShown = false;
let interacted = false;      // il giocatore ha già interagito almeno una volta
let danceDone = false;       // la scena del ballo è già avvenuta (una sola volta)
let contractDone = false;    // il contratto è già stato aperto (una sola volta)
let windowSeen = false;      // il segreto della finestra è già stato visto
let clock = 0;

/* ---------- salvataggio progressi (localStorage) ---------- */
const SAVE_KEY='sempreaddue-save-v3';   // versionata: i salvataggi vecchi (schema diverso) non vengono letti
try{ localStorage.removeItem('sempreaddue-save'); }catch(e){}  // pulizia chiave legacy
function loadSave(){
  if(!CONFIG.salvaProgressi) return;
  try{
    if(new URLSearchParams(location.search).has('reset')){ localStorage.removeItem(SAVE_KEY); return; }
    const s=JSON.parse(localStorage.getItem(SAVE_KEY)||'null');
    if(!s) return;
    (s.found||[]).forEach((v,i)=>{ if(i<found.length) found[i]=!!v; });
    windowSeen=!!s.windowSeen;
    npc.talked=!!s.npc;
    finaleShown=!!s.finale;
    cat.trovato=!!s.segreto;
    cat.purrDone=!!s.purr;
    danceDone=!!s.dance;
    contractDone=!!s.contract;
  }catch(e){}
}
function save(){
  if(!CONFIG.salvaProgressi) return;
  try{
    localStorage.setItem(SAVE_KEY, JSON.stringify(
      {found, windowSeen, npc:npc.talked, finale:finaleShown,
       segreto:cat.trovato, purr:cat.purrDone, dance:danceDone, contract:contractDone}));
  }catch(e){}
}
function vibra(pattern){ try{ navigator.vibrate && navigator.vibrate(pattern); }catch(e){} }

