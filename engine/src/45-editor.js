/* ============================================================
   EDITOR IN-GIOCO (?editor) — strumento di PRODUZIONE, inattivo
   nelle copie consegnate (il cliente non conosce il parametro).
   · Poligono: ogni tocco aggiunge un vertice; "Chiudi" crea il collider
   · Sposta:   primo tocco seleziona un marker (indizio ● o arrivo ○),
               secondo tocco lo posiziona
   · Elimina:  tocco dentro un collider lo rimuove
   · Esporta:  JSON pronto da incollare in room.json / interactions.json
   Con WASD si cammina anche in editor: si testa subito la raggiungibilità.
   ============================================================ */
const ed={ modo:'poligono', bozza:[], selez:null };
function editorTap(wx,wy){
  wx=Math.round(wx*10)/10; wy=Math.round(wy*10)/10;
  if(ed.modo==='poligono'){
    ed.bozza.push([wx,wy]);
  }
  else if(ed.modo==='sposta'){
    if(ed.selez){
      const {s,tipo}=ed.selez;
      if(tipo==='marker'){ s.x=wx; s.y=wy; } else { s.ax=wx; s.ay=wy; }
      ed.selez=null; buildInter();
    } else {
      for(const s of CONFIG.sorprese){
        if(Math.hypot(wx-s.x, wy-s.y)<3){ ed.selez={s,tipo:'marker'}; return; }
        if(Math.hypot(wx-(s.ax??s.x), wy-(s.ay??s.y))<3){ ed.selez={s,tipo:'arrivo'}; return; }
      }
    }
  }
  else if(ed.modo==='elimina'){
    for(let i=COLLIDERS.length-1;i>=0;i--)
      if(pointInPoly(wx,wy,COLLIDERS[i].pts)){
        COLLIDERS.splice(i,1); prepColliders(); buildGrid(); return;
      }
  }
  edStato();
}
function edChiudiPoligono(){
  if(ed.bozza.length<3) return;
  COLLIDERS.push({t:'nuovo-'+(COLLIDERS.length+1), pts:ed.bozza});
  ed.bozza=[];
  prepColliders(); buildGrid(); edStato();
}
function edEsporta(){
  const room={ ...ROOM,
    colliders: COLLIDERS.map(c=>({t:c.t, ...(c.rx?{rx:c.rx}:{}), pts:c.pts})) };
  delete room.dietroLetto.sqz;
  const out={ 'room.json': room,
    'interactions.json (posizioni)': CONFIG.sorprese.map(s=>(
      {id:s.id, x:s.x, y:s.y, ax:s.ax??s.x, ay:s.ay??s.y, ri:s.ri??5})) };
  const ta=document.getElementById('ed-out');
  ta.value=JSON.stringify(out,null,2);
  ta.style.display='block'; ta.focus(); ta.select();
}
function edStato(){
  const el=document.getElementById('ed-stato');
  el.textContent=`modo: ${ed.modo}`
    + (ed.bozza.length?` · vertici: ${ed.bozza.length}`:'')
    + (ed.selez?` · selezionato: ${ed.selez.s.id} (${ed.selez.tipo}) — tocca la nuova posizione`:'');
}
if(EDITOR){
  const pan=document.createElement('div');
  pan.id='ed-pan';
  pan.style.cssText='position:fixed;left:8px;bottom:8px;z-index:60;display:flex;flex-wrap:wrap;'+
    'gap:6px;align-items:center;background:rgba(10,7,8,.85);padding:8px;border-radius:10px;'+
    'font:12px monospace;color:#FBF3E9;max-width:min(96vw,540px)';
  pan.innerHTML=
    '<button data-m="poligono">✏️ Poligono</button>'+
    '<button data-m="sposta">✥ Sposta indizi</button>'+
    '<button data-m="elimina">🗑 Elimina</button>'+
    '<button id="ed-chiudi">Chiudi poligono</button>'+
    '<button id="ed-annulla">↶ Vertice</button>'+
    '<button id="ed-exp">⇩ Esporta JSON</button>'+
    '<span id="ed-stato"></span>'+
    '<textarea id="ed-out" style="display:none;width:100%;height:160px;font:11px monospace"></textarea>';
  document.body.appendChild(pan);
  pan.querySelectorAll('button').forEach(b=>b.style.cssText=
    'font:12px monospace;padding:6px 8px;border-radius:8px;border:1px solid #7a5c42;'+
    'background:#2a1c16;color:#FBF3E9');
  pan.addEventListener('pointerdown', e=>e.stopPropagation());
  pan.querySelectorAll('[data-m]').forEach(b=>b.addEventListener('click',()=>{
    ed.modo=b.dataset.m; ed.selez=null; edStato(); }));
  document.getElementById('ed-chiudi').addEventListener('click', edChiudiPoligono);
  document.getElementById('ed-annulla').addEventListener('click', ()=>{ ed.bozza.pop(); edStato(); });
  document.getElementById('ed-exp').addEventListener('click', edEsporta);
  edStato();
  console.log('[editor] attivo: poligoni, sposta indizi, esporta. WASD per testare i percorsi.');
}
/* overlay dell'editor, richiamato dal render */
function edDraw(){
  if(!EDITOR) return;
  // bozza del poligono in corso
  if(ed.bozza.length){
    ctx.strokeStyle='#ffd166'; ctx.fillStyle='#ffd166'; ctx.lineWidth=2*dpr;
    ctx.beginPath();
    ed.bozza.forEach((p,i)=>i?ctx.lineTo(cvx(p[0]*PCT),cvy(p[1]*PCT)):ctx.moveTo(cvx(p[0]*PCT),cvy(p[1]*PCT)));
    ctx.stroke();
    for(const p of ed.bozza){ ctx.beginPath(); ctx.arc(cvx(p[0]*PCT),cvy(p[1]*PCT),4*dpr,0,7); ctx.fill(); }
  }
  // marker degli indizi (● oggetto, ○ punto d'arrivo)
  for(const s of CONFIG.sorprese){
    const selM=ed.selez && ed.selez.s===s;
    ctx.fillStyle=selM&&ed.selez.tipo==='marker'?'#ffd166':'#ff6b8a';
    ctx.beginPath(); ctx.arc(cvx(s.x*PCT),cvy(s.y*PCT),6*dpr,0,7); ctx.fill();
    ctx.strokeStyle=selM&&ed.selez.tipo==='arrivo'?'#ffd166':'#7ee787'; ctx.lineWidth=2.5*dpr;
    ctx.beginPath(); ctx.arc(cvx((s.ax??s.x)*PCT),cvy((s.ay??s.y)*PCT),7*dpr,0,7); ctx.stroke();
  }
}
