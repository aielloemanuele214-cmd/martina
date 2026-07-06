/* ---------- update ---------- */
function update(dt){
  clock+=dt;
  // ---- input di movimento (tastiera oppure percorso del punta-e-clicca) ----
  let mx=0,my=0;
  if(!frozen){
    if(keys['w']||keys['arrowup'])    my-=1;
    if(keys['s']||keys['arrowdown'])  my+=1;
    if(keys['a']||keys['arrowleft'])  mx-=1;
    if(keys['d']||keys['arrowright']) mx+=1;
    if(mx||my){ percorso.length=0; pendInter=null; }   // la tastiera ha la precedenza
    else if(pendInter && Math.hypot(player.x-(pendInter.ax??pendInter.x), player.y-(pendInter.ay??pendInter.y)) < (pendInter.ri??5)){
      percorso.length=0;   // entrato nel raggio dell'oggetto: basta camminare, si apre
    }
    else if(percorso.length){
      // salta i waypoint già raggiunti, poi punta al prossimo
      while(percorso.length>1 && Math.hypot(percorso[0].x-player.x, percorso[0].y-player.y)<0.35) percorso.shift();
      const w=percorso[0];
      const dx=w.x-player.x, dy=w.y-player.y, dd=Math.hypot(dx,dy);
      if(dd<0.35) percorso.shift();
      else { mx=dx/dd; my=dy/dd; }
    }
  }
  if(tapFx){ tapFx.t+=dt; if(tapFx.t>.55) tapFx=null; }

  // ---- movimento con collisione + macchina a stati ----
  const wantMove = (mx||my) && !frozen && player.state!=='interact' && player.state!=='dance';
  if(wantMove){
    const len=Math.hypot(mx,my)||1;
    const nx=mx/len, ny=my/len;
    const sp=SPEED/PCT*dt;
    const px=player.x+nx*sp, py=player.y+ny*sp;
    let moved=false;
    if(!blocked(px,player.y)){ player.x=px; moved=true; }
    if(!blocked(player.x,py)){ player.y=py; moved=true; }
    // direzione dominante (con isteresi) — nessun salto di frame
    if(Math.abs(nx)>Math.abs(ny)*1.15) player.dir=nx<0?'left':'right';
    else if(Math.abs(ny)>Math.abs(nx)*1.15) player.dir=ny<0?'up':'down';
    if(moved){ setState('walk'); player.stuckT=0; }
    else {
      // ostacolo su entrambi gli assi: stop immediato, niente compenetrazione né camminata infinita
      percorso.length=0; pendInter=null; setState('idle');
    }
  } else if(player.state==='walk'){
    setState('idle');
  }
  player.animT+=dt;   // avanza sempre l'animazione dello stato corrente

  // ---- arrivo a un'interazione pendente (apre SOLO dopo aver raggiunto il punto) ----
  if(!frozen && !percorso.length && pendInter){
    const it=pendInter; pendInter=null;
    const tx=it.ax??it.x, ty=it.ay??it.y, ri=it.ri??5;
    if(Math.hypot(player.x-tx, player.y-ty) < ri+1.0) dispatchInter(it);
    else setState('idle');
  }

  // ---- espressioni di lui: SOLO event-driven (nextEmo), qui garantiamo l'idle fuori dai dialoghi ----
  if(!(diagOpen && dialogEmotivo)) npc.frame=0;

  // bersaglio interazione + bottone azione (DOM toccato solo quando cambia)
  target=frozen?null:nearestTarget();
  const abIcon=target ? (target.tipo==='sorpresa'?'❤':target.icona) : '';
  if(abIcon!==lastAB){
    lastAB=abIcon;
    if(abIcon){ actionEl.textContent=abIcon; actionEl.classList.add('show'); }
    else actionEl.classList.remove('show');
  }

  // vicini vicini: qualche cuoricino quando lei sta accanto a lui
  if(!frozen && Math.hypot(player.x-npc.x, player.y-npc.y)<8 && Math.random()<dt*.6)
    parts.push({x:(player.x+npc.x)/2+(Math.random()-.5)*3, y:Math.min(player.y,npc.y)-20,
      vy:-(2.5+Math.random()*2), sway:Math.random()*Math.PI*2, life:1});

  // durante il ballo: cuoricini che salgono ogni tanto
  if(dance.on){
    dance.t+=dt;
    if(Math.random()<dt*1.1)
      parts.push({x:CONFIG.ballo.x+(Math.random()-.5)*7, y:CONFIG.ballo.y-8-Math.random()*8,
        vy:-(3+Math.random()*3), sway:Math.random()*Math.PI*2, life:1});
  }

  // particelle
  for(let i=parts.length-1;i>=0;i--){
    const p=parts[i];
    p.y+=p.vy*dt; p.x+=Math.sin(clock*4+p.sway)*1.6*dt; p.life-=dt*.55;
    if(p.life<=0) parts.splice(i,1);
  }
  updateCam(dt);
}

