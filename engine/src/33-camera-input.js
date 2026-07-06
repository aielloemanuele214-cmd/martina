/* ---------- camera ---------- */
let vw=0, vh=0, dpr=1, S=1, followMode=false, camX=0, camY=0, camInit=false;
function resize(){
  vw=innerWidth; vh=innerHeight;
  dpr=Math.min(devicePixelRatio||1, 2);
  canvas.width=Math.round(vw*dpr); canvas.height=Math.round(vh*dpr);
  const fit=Math.min(vw/W, vh/W);
  if(CHAR_H*fit < 150){
    // mobile: riempi lo schermo ma un po' più da lontano (-25%)
    S=Math.max(fit, Math.max(vw/W, vh/W)*0.75); followMode=true;
  }
  else { S=fit; followMode=false; }
  camInit=false;
  if(ready) rebuildCache();
}
addEventListener('resize', resize);
// iOS Safari: la barra degli indirizzi cambia il viewport senza evento resize classico
if(window.visualViewport) visualViewport.addEventListener('resize', resize);
function camFocus(){
  if(dance.on)  return {x:CONFIG.ballo.x, y:CONFIG.ballo.y-8};
  return player;
}
function camTarget(axis){
  const view = (axis==='x'?vw:vh)/S;
  if(view>=W) return (W-view)/2;
  const f=camFocus();
  const p=(axis==='x'?f.x:f.y)*PCT;
  return Math.max(0, Math.min(W-view, p-view/2));
}
function updateCam(dt){
  const tx=camTarget('x'), ty=camTarget('y');
  if(!camInit){ camX=tx; camY=ty; camInit=true; return; }
  const k=Math.min(1, dt*5);
  camX+=(tx-camX)*k; camY+=(ty-camY)*k;
}
const sx = wx=>(wx-camX)*S;   // mondo px -> schermo
const sy = wy=>(wy-camY)*S;

/* ---------- input tastiera ---------- */
const keys={};
addEventListener('keydown', e=>{
  if(cinematic){ e.preventDefault(); return; }   // nessun input durante le scene
  if(['arrowup','arrowdown','arrowleft','arrowright',' '].includes(e.key.toLowerCase())) e.preventDefault();
  keys[e.key.toLowerCase()]=true;
  if(e.key==='e'||e.key==='E'||e.key===' '||e.key==='Enter') pressInteract();
  if(e.key==='Escape') closeAll();
  firstGesture();
});
addEventListener('keyup', e=>{ keys[e.key.toLowerCase()]=false; });

