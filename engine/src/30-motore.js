/* ============================================================
   MOTORE
   ============================================================ */
const ENGINE_V = '1.3.0';
console.log('Sempreaddue · stanza v'+ENGINE_V);
const W = 1254;                       // lato stanza in px mondo
const PCT = W/100;                    // 1% in px mondo
const H_LUI = ASSETS[SPR.npc.foglio].alt*PCT;          // altezze in scena: dal pack (sprites.json)
const H_LEI = ASSETS[SPR.player.fogli.down].alt*PCT;
const CHAR_H = H_LUI;                 // riferimento per soglie camera
const SPEED = 24*PCT;                 // velocità in px mondo / s (NON modificare: è il gameplay)
// Le sequenze di animazione sono dichiarate nel pack (sprites.json → personaggi.stati)
// Corpo ellittico: largo ai fianchi, sottile in profondità (stile Stardew)
const RX = 2.0;                       // semiasse orizzontale (in %)
const RY = 0.8;                       // semiasse verticale (in %)
const SQZ = RY/RX;                    // fattore di schiacciamento X per il test ellittico
const _params = new URLSearchParams(location.search);
const EDITOR = _params.has('editor');           // modalità produzione: disegna hitbox, sposta indizi
const DEBUG = _params.has('debug') || EDITOR;

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d', {alpha:false});
const isTouch = matchMedia('(pointer:coarse)').matches;

/* ---------- caricamento immagini ---------- */
const IMG = {};
let toLoad = 0;
for(const k in ASSETS){
  toLoad++;
  const im = new Image();
  im.onload = ()=>{ if(--toLoad===0) begin(); };
  im.src = ASSETS[k].src;
  IMG[k] = im;
}

