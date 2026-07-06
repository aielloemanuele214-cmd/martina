/* ============================================================
   MOTORE
   ============================================================ */
const ENGINE_V = '1.0.0-rc3';
console.log('Sempreaddue · stanza v'+ENGINE_V);
const W = 1254;                       // lato stanza in px mondo
const PCT = W/100;                    // 1% in px mondo
const H_LUI = 24.8*PCT;               // altezza di lui (~311px)
const H_LEI = H_LUI*0.95;             // lei: pochissimo più bassa (rapporto preso dai frame del ballo)
const CHAR_H = H_LUI;                 // riferimento per soglie camera
const SPEED = 24*PCT;                 // velocità in px mondo / s (NON modificare: è il gameplay)
// Animazione camminata: sequenza idle→walkA→idle→walkB con frame lunghi (morbida, non tocca la velocità)
const WALK_SEQ = [FR_WALK_A, FR_IDLE, FR_WALK_B, FR_IDLE];
const WALK_FRAME_DUR = 0.18;          // secondi per frame (alto = fluido)
const DANCE_SEQ = [0,1,2,3,4,3,2,1];  // 1→2→3→4→5→4→3→2 (mai 5→1)
const DANCE_FRAME_DUR = 0.9;          // ballo LENTO e romantico: ~7.2s per giro completo
// Corpo ellittico: largo ai fianchi, sottile in profondità (stile Stardew)
const RX = 2.0;                       // semiasse orizzontale (in %)
const RY = 0.8;                       // semiasse verticale (in %)
const SQZ = RY/RX;                    // fattore di schiacciamento X per il test ellittico
const DEBUG = new URLSearchParams(location.search).has('debug');

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

