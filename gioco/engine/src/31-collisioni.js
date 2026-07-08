/* ---------- geometria collisioni (in %) ---------- */
function pointInPoly(px,py,pts){
  let inside=false;
  for(let i=0,j=pts.length-1;i<pts.length;j=i++){
    const xi=pts[i][0],yi=pts[i][1],xj=pts[j][0],yj=pts[j][1];
    if(((yi>py)!==(yj>py)) && (px<(xj-xi)*(py-yi)/(yj-yi)+xi)) inside=!inside;
  }
  return inside;
}
function distToSeg(px,py,ax,ay,bx,by){
  const dx=bx-ax,dy=by-ay,l2=dx*dx+dy*dy;
  let t=l2?((px-ax)*dx+(py-ay)*dy)/l2:0;
  t=Math.max(0,Math.min(1,t));
  return Math.hypot(px-(ax+t*dx), py-(ay+t*dy));
}
function nearPoly(px,py,pts,m){
  for(let i=0,j=pts.length-1;i<pts.length;j=i++)
    if(distToSeg(px,py,pts[j][0],pts[j][1],pts[i][0],pts[i][1])<m) return true;
  return false;
}
// poligoni pre-schiacciati per la distanza ellittica (rx personalizzabile per collider)
// (funzione richiamabile: l'editor la riesegue dopo ogni modifica ai poligoni)
function prepColliders(){
  COLLIDERS.forEach(c=>{
    c.sqz=RY/(c.rx||RX);
    c.spts=c.pts.map(p=>[p[0]*c.sqz, p[1]]);
  });
}
prepColliders();
/* Bitmap di calpestabilità (opzionale): se il pack fornisce ROOM.walk (griglia
   1-bit ricavata dalla maschera di collisione della stanza generata), il motore
   usa quella — collisioni pixel-accurate coerenti con l'arte, senza poligoni a
   mano. Se assente, si usano i COLLIDERS poligonali (compatibilità). */
let WALK=null, WALKW=0, WALKH=0;
(function initWalk(){
  const w=(typeof ROOM!=='undefined') && ROOM.walk;
  if(w && w.data){
    const raw=atob(w.data); WALKW=w.w; WALKH=w.h;
    WALK=new Uint8Array(raw.length);
    for(let i=0;i<raw.length;i++) WALK[i]=raw.charCodeAt(i);
  }
})();
function walkableAt(px,py){
  const gx=Math.floor(px/100*WALKW), gy=Math.floor(py/100*WALKH);
  if(gx<0||gy<0||gx>=WALKW||gy>=WALKH) return false;
  const idx=gy*WALKW+gx;
  return (WALK[idx>>3]>>(idx&7))&1;
}
function blocked(px,py){
  const B=ROOM.bounds;
  if(px<B.xMin||px>B.xMax||py<B.yMin||py>B.yMax) return true;
  if(WALK){
    if(!walkableAt(px,py)) return true;
  } else {
    for(const c of COLLIDERS){
      if(pointInPoly(px,py,c.pts)) return true;
      if(nearPoly(px*c.sqz,py,c.spts,RY)) return true;
    }
  }
  // lui è un ostacolo morbido (ellittico anche lui)
  if(Math.hypot((px-npc.x)*.5, py-npc.y)<1.7) return true;
  return false;
}
const inBehind = (px,py)=>pointInPoly(px,py,BEHIND_BED);

