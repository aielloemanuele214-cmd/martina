/* ---------- punta e clicca: tocchi un punto e lei ci va ---------- */
const tap={id:null,x:0,y:0,t0:0,moved:false};
// blocca scroll/zoom del browser sul canvas (iOS/Android)
canvas.addEventListener('touchstart', e=>e.preventDefault(), {passive:false});
canvas.addEventListener('touchmove',  e=>e.preventDefault(), {passive:false});
canvas.addEventListener('pointerdown', e=>{
  e.preventDefault(); firstGesture();
  if(cinematic) return;                 // scene cinematiche: nessun input
  tap.id=e.pointerId; tap.x=e.clientX; tap.y=e.clientY;
  tap.t0=performance.now(); tap.moved=false;
  if(DEBUG){
    const wx=(e.clientX/S+camX)/PCT, wy=(e.clientY/S+camY)/PCT;
    console.log(`[debug] click a x:${wx.toFixed(1)} y:${wy.toFixed(1)}`);
    document.getElementById('dbg-pos').textContent=`x:${wx.toFixed(1)} y:${wy.toFixed(1)}`;
  }
});
canvas.addEventListener('pointermove', e=>{
  if(e.pointerId===tap.id && Math.hypot(e.clientX-tap.x, e.clientY-tap.y)>14) tap.moved=true;
});
function ptrEnd(e){
  if(e.pointerId!==tap.id) return;
  tap.id=null;
  if(performance.now()-tap.t0>450 || tap.moved) return;
  if(frozen){ pressInteract(); return; }   // dialoghi aperti: il tocco fa avanzare
  handleTap(tap.x, tap.y);
}
canvas.addEventListener('pointerup', ptrEnd);
canvas.addEventListener('pointercancel', e=>{ if(e.pointerId===tap.id) tap.id=null; });

/* Smistamento del tocco nel mondo */
function handleTap(cssX,cssY){
  const wx=(cssX/S+camX)/PCT, wy=(cssY/S+camY)/PCT;
  if(EDITOR){ editorTap(wx,wy); return; }        // in editor il tocco disegna, non muove
  // segreti: rispondono al tocco diretto da qualsiasi distanza, senza indicatori
  if(tryCat(cssX,cssY)) return;
  if(tryWindow(cssX,cssY)) return;
  if(tryPuntiSegreti(cssX,cssY)) return;
  // tocco vicino a un interattivo (sull'oggetto): cammina al punto d'arrivo e apri LÌ
  let best=null, bd=1e9;
  for(const it of INTER){
    const d=Math.hypot(wx-it.x, wy-it.y);
    if(d<8 && d<bd){ bd=d; best=it; }
  }
  if(best){
    const tx=best.ax??best.x, ty=best.ay??best.y, ri=best.ri??5;
    if(Math.hypot(player.x-tx, player.y-ty) < ri) dispatchInter(best);   // già sul posto
    else goTo(tx, ty, best);                                             // altrimenti raggiungilo
    return;
  }
  goTo(wx, wy, null);                          // semplice spostamento
}

