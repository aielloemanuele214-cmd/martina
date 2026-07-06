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
COLLIDERS.forEach(c=>{
  c.sqz=RY/(c.rx||RX);
  c.spts=c.pts.map(p=>[p[0]*c.sqz, p[1]]);
});
function blocked(px,py){
  for(const c of COLLIDERS){
    if(pointInPoly(px,py,c.pts)) return true;
    if(nearPoly(px*c.sqz,py,c.spts,RY)) return true;
  }
  const B=ROOM.bounds;
  if(px<B.xMin||px>B.xMax||py<B.yMin||py>B.yMax) return true;
  // lui è un ostacolo morbido (ellittico anche lui)
  if(Math.hypot((px-npc.x)*.5, py-npc.y)<1.7) return true;
  return false;
}
const inBehind = (px,py)=>pointInPoly(px,py,BEHIND_BED);

