/* ---------- disegno: tutto da cache pre-scalate (niente riscalature per frame) ---------- */
let PS=1;                              // px mondo -> px canvas
const CACHE={glyphs:{}};
function rebuildCache(){
  PS=S*dpr;
  const mk=(w,h)=>{ const c=document.createElement('canvas');
    c.width=Math.max(1,Math.round(w)); c.height=Math.max(1,Math.round(h)); return c; };
  // sfondi pre-scalati alla risoluzione di disegno
  for(const k of ['bg','bg2']){
    const c=mk(W*PS, W*PS);
    c.getContext('2d').drawImage(IMG[k],0,0,c.width,c.height);
    CACHE[k]=c;
  }
  // spritesheet pre-scalati alla loro altezza in scena (tutte le direzioni di lei = stessa altezza)
  const alt={};
  for(const k in ASSETS) if(ASSETS[k].alt) alt[k]=ASSETS[k].alt*PCT;
  alt[SPR.gatto.foglio]=ASSETS[SPR.gatto.foglio].fh*(cat.larghezza*PCT/ASSETS[SPR.gatto.foglio].fw);
  for(const k in alt){
    const sp=ASSETS[k], f=alt[k]*PS/sp.fh;
    const c=mk(sp.fw*sp.n*f, sp.fh*f);
    c.getContext('2d').drawImage(IMG[k],0,0,c.width,c.height);
    CACHE[k]={c, fw:c.width/sp.n, fh:c.height, n:sp.n};
  }
  // ombra morbida (un solo gradiente, riusato)
  const sh=mk(128,128), g=sh.getContext('2d');
  const rg=g.createRadialGradient(64,64,0,64,64,64);
  rg.addColorStop(0,'rgba(0,0,0,.42)'); rg.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=rg; g.fillRect(0,0,128,128);
  CACHE.shadow=sh;
  // glifi emoji rasterizzati una volta
  for(const ch of ['✨','💬','❤️']){
    const gc=mk(64,64), cg=gc.getContext('2d');
    cg.font='50px serif'; cg.textAlign='center'; cg.textBaseline='middle';
    cg.fillText(ch,32,36);
    CACHE.glyphs[ch]=gc;
  }
}
const cvx = wx=>(wx-camX)*PS;          // px mondo -> px canvas
const cvy = wy=>(wy-camY)*PS;
function blit(key,frame,xPct,yPct,flip,alpha,dyWorld){
  const s=CACHE[key];
  const X=cvx(xPct*PCT), Y=cvy(yPct*PCT)+(dyWorld||0)*PS;
  ctx.globalAlpha=alpha;
  if(flip){
    ctx.save(); ctx.translate(X,0); ctx.scale(-1,1);
    ctx.drawImage(s.c, frame*s.fw,0,s.fw,s.fh, -s.fw/2, Y-s.fh, s.fw, s.fh);
    ctx.restore();
  } else {
    ctx.drawImage(s.c, frame*s.fw,0,s.fw,s.fh, X-s.fw/2, Y-s.fh, s.fw, s.fh);
  }
  ctx.globalAlpha=1;
}
function blitShadow(xPct,yPct,wWorld,alpha){
  const rx=wWorld*.38*PS, ry=rx*.32;
  ctx.globalAlpha=alpha;
  ctx.drawImage(CACHE.shadow, cvx(xPct*PCT)-rx, cvy(yPct*PCT)-ry, rx*2, ry*2);
  ctx.globalAlpha=1;
}
function glyph(ch,xPct,yPct,sizeWorld,alpha,dyCanvas){
  const d=sizeWorld*PS;
  ctx.globalAlpha=alpha;
  ctx.drawImage(CACHE.glyphs[ch], cvx(xPct*PCT)-d/2, cvy(yPct*PCT)-d/2+(dyCanvas||0), d, d);
  ctx.globalAlpha=1;
}
// Frame del giocatore dalla macchina a stati + stati dichiarati nel pack
// (nessun flip: art dedicata per ogni direzione)
function playerFrame(){
  const P=SPR.player, key=P.fogli[player.dir];
  const st=P.stati[player.state]||P.stati.idle;
  if(st.seq){
    const i=Math.floor(player.animT/st.dur)%st.seq.length;
    return {key, frame:st.seq[i], dy:0};
  }
  // frame fisso + eventuale respiro (movimento verticale, non cambio frame)
  const dy=st.bobFreq?Math.sin(clock*st.bobFreq)*-(st.bobAmp??1):0;
  return {key, frame:st.frame||0, dy};
}

function render(){
  ctx.setTransform(1,0,0,1,0,0);
  ctx.fillStyle='#0a0708'; ctx.fillRect(0,0,canvas.width,canvas.height);

  // stanza (due frame alternati irregolarmente: candele/fiamme/vinile animati)
  const flick=(Math.sin(clock*6.3)+Math.sin(clock*11.7+2))>0;
  ctx.drawImage(flick?CACHE.bg:CACHE.bg2, Math.round(-camX*PS), Math.round(-camY*PS));

  // debug hitbox
  if(DEBUG){
    ctx.lineWidth=1.5*dpr;
    for(const c of COLLIDERS){
      ctx.beginPath();
      c.pts.forEach((p,i)=>i?ctx.lineTo(cvx(p[0]*PCT),cvy(p[1]*PCT)):ctx.moveTo(cvx(p[0]*PCT),cvy(p[1]*PCT)));
      ctx.closePath(); ctx.fillStyle='rgba(255,80,80,.22)'; ctx.fill();
      ctx.strokeStyle='rgba(255,120,120,.8)'; ctx.stroke();
    }
    ctx.beginPath();
    BEHIND_BED.forEach((p,i)=>i?ctx.lineTo(cvx(p[0]*PCT),cvy(p[1]*PCT)):ctx.moveTo(cvx(p[0]*PCT),cvy(p[1]*PCT)));
    ctx.closePath(); ctx.fillStyle='rgba(80,140,255,.25)'; ctx.fill();
    for(const it of INTER){
      ctx.beginPath(); ctx.arc(cvx(it.x*PCT),cvy(it.y*PCT),it.r*PCT*PS,0,Math.PI*2);
      ctx.strokeStyle='rgba(120,255,120,.5)'; ctx.stroke();
    }
    document.getElementById('dbg-pos').style.display='block';
  }

  // guida discreta: un ✨ solo sugli indizi principali ancora da scoprire
  // (gatto e finestra sono segreti: NESSUN indicatore)
  const scena=!!cine.scene;
  if(!scena){
    for(let i=0;i<CONFIG.sorprese.length;i++){
      const s=CONFIG.sorprese[i];
      if(flag('trovato.'+s.id)) continue;
      const a=.55+.3*Math.sin(clock*3+i);
      const size=26+Math.sin(clock*3+i)*3;
      glyph('✨', s.x, s.y, size, a, -Math.sin(clock*2+i)*3*PS);
    }
  }

  // entità ordinate per profondità (piedi più in basso = davanti)
  const catFrame=clock<cat.awakeUntil?1:0;
  // rivelazione morbida del gatto per vicinanza (se cat.rivelaVicino è impostato)
  let catA=1;
  if(cat.rivelaVicino && !flag('segreto.gatto')){
    const d=Math.hypot(player.x-cat.x, player.y-cat.y);
    catA=Math.max(0, Math.min(1, (cat.rivelaVicino - d)/2.5));
  }
  const ents = catA>0.01 ? [
    {y:cat.y, draw(){          // gatto: elemento decorativo (eventuale fade di rivelazione)
      blitShadow(cat.x, cat.y, cat.larghezza*PCT*.8, .8*catA);
      blit(SPR.gatto.foglio, catFrame, cat.x, cat.y, false, catA, 0);
    }},
  ] : [];
  if(!scena){
    ents.push({y:npc.y, draw(){          // lui: idle=frame0, durante i dialoghi cicla i frame emotivi
      const a=inBehind(npc.x,npc.y)?.45:1;
      blitShadow(npc.x, npc.y, H_LUI*.42, a);
      blit(SPR.npc.foglio, npc.frame||0, npc.x, npc.y, false, a,
           Math.sin(clock*(SPR.npc.bobFreq||1.6))*-(SPR.npc.bobAmp??1));
      if(!flag('npcParlato'))
        glyph('💬', npc.x, npc.y, 27, .9, -(H_LUI*1.12)*PS - Math.sin(clock*2.5)*4*PS);
    }});
    ents.push({y:player.y, draw(){
      const a=inBehind(player.x,player.y)?.45:1;
      const pf=playerFrame();
      blitShadow(player.x, player.y, H_LEI*.45, a);
      blit(pf.key, pf.frame, player.x, player.y, false, a, pf.dy);
    }});
  }
  ents.sort((a,b)=>a.y-b.y).forEach(e=>e.draw());

  // scena di coppia (es. ballo): vignetta + sprite animato secondo il pack
  if(cine.scene){
    ctx.fillStyle='rgba(8,4,6,.45)';
    ctx.fillRect(0,0,canvas.width,canvas.height);
    const pers=SPR[cine.scene.pers], an=pers.anim;
    const fr=an?an.seq[Math.floor(cine.scene.t/an.dur)%an.seq.length]:0;
    blitShadow(cine.scene.x, cine.scene.y, H_LUI*.7, 1);
    blit(pers.foglio, fr, cine.scene.x, cine.scene.y, false, 1,
         Math.sin(cine.scene.t*(pers.bobFreq||1))*-(pers.bobAmp??1));
  }

  // particelle (cuori e scintille)
  for(const p of parts) glyph(p.ch||'❤️', p.x, p.y, p.size||20, Math.max(0,p.life), 0);

  if(starFx) drawStar();                 // stella cadente attraverso l'oblò

  edDraw();                              // overlay dell'editor (?editor)

  // anello di conferma del tocco (dove hai puntato)
  if(tapFx){
    const k=tapFx.t/.55;
    ctx.globalAlpha=(1-k)*.8;
    ctx.strokeStyle='#FBF3E9';
    ctx.lineWidth=2*dpr;
    ctx.beginPath();
    ctx.arc(cvx(tapFx.x*PCT), cvy(tapFx.y*PCT), (10+k*26)*dpr, 0, Math.PI*2);
    ctx.stroke();
    ctx.globalAlpha=1;
  }
}

/* Stella cadente: una scia luminosa che attraversa l'oblò (arco=[x0,y0,x1,y1] in %). */
function drawStar(){
  const [ax,ay,bx,by]=starFx.arco;
  const k=Math.min(1, starFx.t/starFx.dur);
  const x=ax+(bx-ax)*k, y=ay+(by-ay)*k;
  const a=Math.sin(k*Math.PI);                 // dissolve in entrata/uscita
  const hx=cvx(x*PCT), hy=cvy(y*PCT);
  const tx=cvx((x-(bx-ax)*.16)*PCT), ty=cvy((y-(by-ay)*.16)*PCT);
  ctx.save();
  ctx.globalAlpha=a;
  const g=ctx.createLinearGradient(tx,ty,hx,hy);
  g.addColorStop(0,'rgba(255,246,210,0)'); g.addColorStop(1,'rgba(255,248,225,1)');
  ctx.strokeStyle=g; ctx.lineWidth=3*dpr; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(tx,ty); ctx.lineTo(hx,hy); ctx.stroke();
  ctx.fillStyle='rgba(255,252,235,'+a+')';
  ctx.beginPath(); ctx.arc(hx,hy,3.4*dpr,0,Math.PI*2); ctx.fill();
  ctx.globalAlpha=a*.5;
  ctx.beginPath(); ctx.arc(hx,hy,7*dpr,0,Math.PI*2); ctx.fillStyle='rgba(255,240,190,.5)'; ctx.fill();
  ctx.restore();
}

