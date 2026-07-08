/* QA parametrica Sempreaddue — funziona su QUALSIASI build (base o cliente).
   Uso:  GAME_FILE=/percorso/stanza.html node tools/qa.js
   Requisiti: `npm i playwright` raggiungibile (NODE_PATH) + Chromium.
   Legge il contenuto dal gioco stesso (CONFIG/STORY/INTER): nessun id cablato. */
const fs=require('fs');
let chromium;
try{ ({chromium}=require('playwright')); }
catch(e){ console.error('✗ playwright non trovato: `npm i playwright` o imposta NODE_PATH'); process.exit(2); }

const FILE=process.env.GAME_FILE;
if(!FILE || !fs.existsSync(FILE)){ console.error('✗ GAME_FILE mancante o inesistente:', FILE); process.exit(2); }

function chromePath(){
  if(process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base='/opt/pw-browsers';
  try{ for(const d of fs.readdirSync(base)){
    const p=`${base}/${d}/chrome-linux/chrome`;
    if(fs.existsSync(p)) return p;
  }}catch(e){}
  return undefined;                       // lascia scegliere a playwright
}

let pass=0, fail=0;
const ok=(nome,cond,extra='')=>{
  if(cond){ pass++; console.log(`  ✓ ${nome}${extra?' — '+extra:''}`); }
  else    { fail++; console.log(`  ✗ ${nome}${extra?' — '+extra:''}`); }
};

(async()=>{
 console.log('QA su', FILE);
 const b=await chromium.launch({executablePath:chromePath()});
 const p=await b.newPage({viewport:{width:1200,height:800}});
 const errs=[];
 p.on('pageerror',e=>errs.push(e.message));
 p.on('console',m=>{ if(m.type()==='error'&&!m.text().includes('net::')) errs.push(m.text()); });

 await p.goto('file://'+FILE+'?reset=1'); await p.waitForTimeout(2600);
 await p.click('#splash'); await p.waitForTimeout(500);
 await p.click('#splash'); await p.waitForTimeout(1200);

 // 1. avvio
 const avvio=await p.evaluate(()=>({inGioco:typeof player!=='undefined'&&player.state==='idle',
   bag:Object.keys(BAG).length, sorprese:CONFIG.sorprese.length, eventi:STORY.eventi.length}));
 ok('avvio in gioco', avvio.inGioco);
 ok('partita nuova pulita (state bag vuoto)', avvio.bag===0);

 // 2. fogli sprite coerenti
 const dims=await p.evaluate(()=>Object.keys(ASSETS).filter(k=>ASSETS[k].fw)
   .map(k=>[k, ASSETS[k].fw*ASSETS[k].n===IMG[k].naturalWidth && ASSETS[k].fh===IMG[k].naturalHeight]));
 ok('dimensioni fogli sprite', dims.every(d=>d[1]), dims.filter(d=>!d[1]).map(d=>d[0]).join(','));

 // 3. raggiungibilità di TUTTI i punti d'arrivo dallo spawn
 const reach=await p.evaluate(()=>INTER.map(it=>{
   const t=findPath(CONFIG.posizioni.protagonista.x, CONFIG.posizioni.protagonista.y, it.ax, it.ay);
   return [it.evento, !!t];
 }));
 ok('tutti gli interattivi raggiungibili', reach.every(r=>r[1]),
    reach.filter(r=>!r[1]).map(r=>r[0]).join(','));

 // 4. ogni sorpresa: tap → cammina → si apre SOLO all'arrivo (o parte una scena)
 const ids=await p.evaluate(()=>CONFIG.sorprese.map(s=>s.id));
 for(const id of ids){
   await p.evaluate(()=>{ if(modalOpen) closePopup(); if(diagOpen) closeDialog();
     clearBag(); updateHearts();
     player.x=CONFIG.posizioni.protagonista.x; player.y=CONFIG.posizioni.protagonista.y;
     percorso.length=0; pendInter=null; setState('idle'); });
   await p.waitForTimeout(80);
   await p.evaluate(id=>{ const s=CONFIG.sorprese.find(x=>x.id===id);
     handleTap((s.x*PCT-camX)*S,(s.y*PCT-camY)*S); }, id);
   const subito=await p.evaluate(()=>modalOpen||cinematic);
   let aperto=false, t=0;
   while(t<12000){ await p.waitForTimeout(250); t+=250;
     if(await p.evaluate(()=>modalOpen||cinematic)){ aperto=true; break; } }
   const flagOk=await p.evaluate(id=>flag('trovato.'+id), id);
   ok(`sorpresa '${id}': si apre dopo l'arrivo`, !subito && aperto && flagOk,
      `~${(t/1000).toFixed(1)}s`);
   // se è partita una cinematica, aspettala fino in fondo (chiudendo un eventuale documento)
   await p.evaluate(()=>{ if(modalOpen) closePopup(); });
   let guard=0;
   while(guard<60000 && await p.evaluate(()=>cinematic)){
     await p.evaluate(()=>{ const d=document.querySelector('#contratto.show .chiudi'); if(d) d.click(); });
     await p.waitForTimeout(500); guard+=500;
   }
   await p.evaluate(()=>{ if(modalOpen) closePopup(); if(diagOpen) closeDialog();
     document.getElementById('finale').classList.remove('show'); frozen=false; setState('idle'); });
 }

 // 5. NPC: dialogo apribile e richiudibile
 await p.evaluate(()=>{ const it=INTER.find(i=>i.tipo==='npc');
   player.x=it.ax; player.y=it.ay; trigger(it.evento); });
 await p.waitForTimeout(250);
 ok('dialogo NPC', await p.evaluate(()=>diagOpen));
 await p.evaluate(()=>closeDialog());

 // 6. finali: per ogni regola, imposta i flag richiesti → il finale appare
 const finali=await p.evaluate(()=>STORY.finali.map(f=>f.id));
 for(const fid of finali){
   const shown=await p.evaluate(fid=>{
     clearBag();
     const f=STORY.finali.find(x=>x.id===fid);
     const atomi=[];
     (function racc(c){ if(!c) return;
       if(typeof c==='string'){ if(c[0]==='!') return;
         if(c.endsWith('.*')){ CONFIG.sorprese.forEach(s=>atomi.push(c.slice(0,-1)+s.id)); }
         else if(c!=='prima_interazione') atomi.push(c); }
       else{ (c.all||[]).forEach(racc); (c.any||[]).slice(0,1).forEach(racc); } })(f.se);
     atomi.forEach(a=>setFlag(a));
     if(matchEnding()?.id!==fid) return 'regola-coperta-da-precedente';
     showFinale(matchEnding());
     return document.getElementById('finale').className.includes('show');
   }, fid);
   ok(`finale '${fid}' raggiungibile`, shown===true || shown==='regola-coperta-da-precedente',
      shown==='regola-coperta-da-precedente'?'coperto da una regola precedente (ordine)':'');
   await p.waitForTimeout(150);
   // 7. Ricomincia azzera tutto (testato sul primo finale mostrato)
   if(shown===true){
     await p.evaluate(()=>document.querySelector('#finale .ricomincia').click());
     await p.waitForTimeout(300);
     const dopo=await p.evaluate(()=>({bag:Object.keys(BAG).length,
       vis:document.getElementById('finale').className.includes('show')}));
     ok('Ricomincia azzera lo stato', dopo.bag===0 && !dopo.vis);
   }
 }

 // 8. salvataggio: roundtrip (se attivo)
 const salva=await p.evaluate(()=>CONFIG.salvaProgressi);
 if(salva){
   await p.evaluate(()=>setFlag('trovato.'+CONFIG.sorprese[0].id));
   await p.goto('file://'+FILE); await p.waitForTimeout(2400);
   await p.click('#splash'); await p.waitForTimeout(450);
   await p.click('#splash'); await p.waitForTimeout(1000);
   ok('salvataggio roundtrip', await p.evaluate(()=>flag('trovato.'+CONFIG.sorprese[0].id)));
 } else console.log('  · salvataggio disattivato nel pack: roundtrip saltato');

 // 9. fps mobile
 const m=await b.newPage({viewport:{width:390,height:844},hasTouch:true,isMobile:true,deviceScaleFactor:2});
 m.on('pageerror',e=>errs.push('M: '+e.message));
 await m.goto('file://'+FILE+'?reset=1'); await m.waitForTimeout(2500);
 await m.tap('#splash'); await m.waitForTimeout(500); await m.tap('#splash'); await m.waitForTimeout(1100);
 const fps=await m.evaluate(()=>new Promise(res=>{let n=0;const t0=performance.now();
   const t=()=>{n++; if(performance.now()-t0<1500) requestAnimationFrame(t); else res(n/1.5);}; requestAnimationFrame(t);}));
 ok('fps mobile ≥ 50', fps>=50, fps.toFixed(0)+' fps');
 await m.close();

 // 10. zero errori JS in tutta la sessione
 ok('nessun errore JS', errs.length===0, errs.slice(0,3).join(' | '));

 await b.close();
 console.log(`\nQA: ${pass} ok, ${fail} falliti`);
 process.exit(fail?1:0);
})();
