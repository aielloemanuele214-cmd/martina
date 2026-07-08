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
const npc = { x:CONFIG.posizioni.lui.x, y:CONFIG.posizioni.lui.y, frame:0 };
const cat = { ...CONFIG.gatto, awakeUntil:0 };
let frozen = false;          // input bloccato (dialoghi/modali)
let cinematic = false;       // scena cinematica in corso: nessun input
let clock = 0;

/* ---------- STATE BAG: tutto lo stato di partita è un sacchetto di flag ----------
   Le chiavi le decide la STORY del pack ('trovato.vinile', 'segreto.gatto',
   'fatto.ballo', 'npcParlato', 'interagito', 'finaleMostrato'…).
   Il motore non conosce i nomi: salva, carica e azzera il sacchetto intero. */
const BAG = {};
const flag = k => !!BAG[k];
function setFlag(k, v){
  const val = (v===undefined ? true : v);
  if(BAG[k]===val) return;
  BAG[k]=val;
  updateHearts();
  save();
}
function clearBag(){ for(const k in BAG) delete BAG[k]; }

/* ---------- salvataggio progressi (localStorage) ---------- */
const SAVE_KEY='sempreaddue-save-v4';   // v4: schema a state-bag
try{ localStorage.removeItem('sempreaddue-save');
     localStorage.removeItem('sempreaddue-save-v3'); }catch(e){}  // chiavi legacy
function loadSave(){
  if(!CONFIG.salvaProgressi) return;
  try{
    if(new URLSearchParams(location.search).has('reset')){ localStorage.removeItem(SAVE_KEY); return; }
    const s=JSON.parse(localStorage.getItem(SAVE_KEY)||'null');
    if(!s || s.v!==4) return;
    Object.assign(BAG, s.bag||{});
  }catch(e){}
}
function save(){
  if(!CONFIG.salvaProgressi) return;
  try{ localStorage.setItem(SAVE_KEY, JSON.stringify({v:4, bag:BAG})); }catch(e){}
}
function vibra(pattern){ try{ navigator.vibrate && navigator.vibrate(pattern); }catch(e){} }
