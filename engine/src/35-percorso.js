/* ---------- pathfinding su griglia (BFS con diagonali) ---------- */
const GSTEP=0.5, GN=200;
let GFREE=null;
function buildGrid(){
  GFREE=new Uint8Array(GN*GN);
  for(let j=0;j<GN;j++) for(let i=0;i<GN;i++)
    GFREE[j*GN+i]=blocked(i*GSTEP, j*GSTEP)?0:1;
}
function nearestFreeCell(x,y){
  let ci=Math.max(0,Math.min(GN-1,Math.round(x/GSTEP)));
  let cj=Math.max(0,Math.min(GN-1,Math.round(y/GSTEP)));
  if(GFREE[cj*GN+ci]) return [ci,cj];
  for(let r=1;r<45;r++)
    for(let a=0;a<16;a++){
      const i=Math.round(ci+Math.cos(a/16*2*Math.PI)*r);
      const j=Math.round(cj+Math.sin(a/16*2*Math.PI)*r);
      if(i>=0&&j>=0&&i<GN&&j<GN&&GFREE[j*GN+i]) return [i,j];
    }
  return null;
}
function findPath(x0,y0,x1,y1){
  const s=nearestFreeCell(x0,y0), t=nearestFreeCell(x1,y1);
  if(!s||!t) return null;
  const sk=s[1]*GN+s[0], tk=t[1]*GN+t[0];
  const prev=new Int32Array(GN*GN).fill(-1);
  prev[sk]=sk;
  const q=[sk]; let head=0;
  while(head<q.length){
    const k=q[head++];
    if(k===tk) break;
    const i=k%GN, j=(k/GN)|0;
    for(const [di,dj] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){
      const I=i+di, J=j+dj;
      if(I<0||J<0||I>=GN||J>=GN) continue;
      const K=J*GN+I;
      if(prev[K]!==-1 || !GFREE[K]) continue;
      if(di&&dj && (!GFREE[j*GN+I] || !GFREE[J*GN+i])) continue; // niente tagli sugli spigoli
      prev[K]=k; q.push(K);
    }
  }
  if(prev[tk]===-1) return null;
  const path=[];
  for(let k=tk;k!==sk;k=prev[k]) path.push({x:(k%GN)*GSTEP, y:((k/GN)|0)*GSTEP});
  path.reverse();
  return path;   // percorso completo cella-per-cella (niente scorciatoie negli angoli)
}
let percorso=[], pendInter=null, tapFx=null;
function goTo(x,y,inter){
  const p=findPath(player.x, player.y, x, y);
  if(!p || !p.length){ percorso=[]; pendInter=null; return; }
  percorso=p; pendInter=inter||null;
  tapFx={x, y, t:0};
  audio.sfx('click');
}
function dispatchInter(it){ trigger(it.evento); }

/* ---------- interattivi (lista costruita una volta) ---------- */
let INTER=[];
function buildInter(){
  // solo i 3 indizi principali + Manu (gatto e finestra sono segreti a tocco diretto)
  // x,y = marker sull'oggetto · ax,ay = punto d'arrivo calpestabile · ri = raggio d'apertura
  INTER=[
    ...CONFIG.sorprese.map(s=>({tipo:'sorpresa', evento:'interagisci:'+s.id, x:s.x, y:s.y,
        ax:s.ax??s.x, ay:s.ay??s.y, ri:s.ri??5})),
    {tipo:'npc', evento:'interagisci:npc', x:npc.x, y:npc.y, ax:npc.x, ay:npc.y, ri:5.5, icona:'💬'},
  ];
}
function nearestTarget(){
  let best=null, bd=1e9;
  for(const it of INTER){
    const d=Math.hypot(player.x-(it.ax??it.x), player.y-(it.ay??it.y));
    if(d<(it.ri??5)+.5 && d<bd){ bd=d; best=it; }
  }
  return best;
}
let target=null;

function pressInteract(){
  if(cinematic) return;
  if(frozen){ advanceDialog(); return; }
  if(target) dispatchInter(target);
}

