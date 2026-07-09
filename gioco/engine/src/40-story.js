/* ============================================================
   STORY ENGINE — interprete di eventi, condizioni e scene (DSL)
   Il motore non conosce alcun contenuto: legge STORY (eventi,
   scene a passi, dialoghi, segreti, finali) e CONFIG (testi).
   ============================================================ */
const cineEl=document.getElementById('cine'), cineTextEl=document.getElementById('cineText');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function fadeNero(on){ cineEl.classList.toggle('on', on); return wait(1050); }
function typeWrite(testo, cps){
  cps=cps||26;
  return new Promise(res=>{
    cineTextEl.textContent='';
    let n=0;
    const iv=setInterval(()=>{
      cineTextEl.textContent=testo.slice(0,++n);
      if(n%2===0 && testo[n-1]!=='\n' && testo[n-1]!==' ') audio.sfx('type');
      if(n>=testo.length){ clearInterval(iv); res(); }
    }, 1000/cps);
  });
}

/* ---------- risoluzione riferimenti: '$percorso'→CONFIG · '@nome'→asset ---------- */
function risolvi(v){
  if(typeof v!=='string') return v;
  if(v[0]==='$') return v.slice(1).split('.').reduce((o,k)=>o?.[k], CONFIG);
  if(v[0]==='@') return ASSET_URI[v.slice(1)];
  return v;
}

/* ---------- condizioni dichiarative sullo stato di partita ---------- */
function cond(c){
  if(c==null) return true;
  if(typeof c==='string'){
    if(c[0]==='!') return !cond(c.slice(1));
    if(c==='prima_interazione') return !flag('interagito');
    if(c.endsWith('.*')){                       // 'trovato.*' = tutte le sorprese scoperte
      const pre=c.slice(0,-1);
      return CONFIG.sorprese.every(s=>flag(pre+s.id));
    }
    return flag(c);
  }
  if(c.all) return c.all.every(cond);
  if(c.any) return c.any.some(cond);
  return false;
}

/* ---------- azioni ---------- */
async function runActions(list){
  for(const a of (list||[])){
    if(a.set!==undefined){ setFlag(a.set); }
    else if(a.togli!==undefined){ setFlag(a.togli,false); }
    else if(a.sorpresa!==undefined){ apriSorpresa(a.sorpresa); }
    else if(a.popup!==undefined){
      const p=a.popup;
      setFlag('interagito');
      openPopup({ img:risolvi(p.img), titolo:risolvi(p.titolo)||'', testo:risolvi(p.testo),
                  face:p.verso });
    }
    else if(a.dialogo!==undefined){ apriDialogo(a.dialogo); }
    else if(a.scena!==undefined){ await runCutscene(a.scena); }
    else if(a.sfx!==undefined){ audio.sfx(a.sfx); }
    else if(a.vibra!==undefined){ vibra(a.vibra); }
    else if(a.sveglia!==undefined){ if(a.sveglia==='gatto') cat.awakeUntil=clock+5; }
    else if(a.verso!==undefined){
      const t=puntoDi(a.verso); if(t) facePoint(t.x,t.y);
    }
    else if(a.cuori!==undefined){
      const t=puntoDi(a.cuori.su)||a.cuori; burst(t.x, t.y-4, a.cuori.n||8);
    }
    else if(a.se!==undefined){ await runActions(cond(a.se)?a.fai:a.altrimenti); }
  }
}
/* nome simbolico → punto nel mondo ('gatto', 'npc', [x,y]) */
function puntoDi(rif){
  if(Array.isArray(rif)) return {x:rif[0], y:rif[1]};
  if(rif==='gatto') return cat;
  if(rif==='npc')   return npc;
  return null;
}

/* ---------- trigger: smista un'interazione al primo evento che risponde ---------- */
async function trigger(nome){
  const ev=STORY.eventi.find(e=>e.quando===nome);
  if(!ev) return;
  const ramo = cond(ev.se) ? ev.fai : ev.altrimenti;
  await runActions(ramo);
  setFlag('interagito');
}

/* ---------- scene cinematiche a passi (DSL) ---------- */
const cine={scene:null};                 // scena "coppia" attiva (vignetta + sprite animato)
const contrattoEl=document.getElementById('contratto');
let docClose=null;
contrattoEl.querySelector('.chiudi').addEventListener('click', ()=>{ if(docClose) docClose(); });

async function runCutscene(id){
  const cs=STORY.scene[id];
  if(!cs) return;
  for(const p of cs.passi){
    if(p.inizio){
      if(diagOpen) closeDialog();
      percorso.length=0; pendInter=null;
      cinematic=true; frozen=true;
    }
    else if(p.set!==undefined){ setFlag(p.set); }
    else if(p.statoGiocatore!==undefined){ setState(p.statoGiocatore); }
    else if(p.suggerimento!==undefined){
      document.getElementById('hint').classList.toggle('hide', !p.suggerimento);
    }
    else if(p.musicaSfuma!==undefined){
      if(CONFIG.musica && !audio.muted) fadeAudio(musGame,0,p.musicaSfuma*1000);
    }
    else if(p.musicaRiprendi){
      if(CONFIG.musica && !audio.muted){ musGame.play().catch(()=>{}); fadeAudio(musGame,.55,1600); }
    }
    else if(p.nero!==undefined){ await fadeNero(p.nero); if(!p.nero) cineTextEl.textContent=''; }
    else if(p.scrivi!==undefined){
      const s=typeof p.scrivi==='string'?{testo:p.scrivi}:p.scrivi;
      await typeWrite(String(risolvi(s.testo)));
      await wait((s.pausa??1.4)*1000);
      cineTextEl.textContent='';
    }
    else if(p.attesa!==undefined){ await wait(Number(risolvi(p.attesa))*1000); }
    else if(p.coppia!==undefined){
      const rif=CONFIG[p.coppia.riferimento]||{};
      cine.scene={ pers:p.coppia.foglio, x:p.coppia.x??rif.x, y:p.coppia.y??rif.y, t:0 };
      camInit=false;
    }
    else if(p.coppiaFine){ cine.scene=null; }
    else if(p.stella!==undefined){                 // stella cadente attraverso l'oblò
      const s=(typeof p.stella==='object')?p.stella:{};
      starFx={ t:0, dur:s.durata||1.7, arco:s.arco||(CONFIG.stella&&CONFIG.stella.arco)||[30,8,72,22] };
      audio.sfx('item');
      await wait((s.durata||1.7)*1000);
    }
    else if(p.synth!==undefined){ if(p.synth) audio.startDance(); }
    else if(p.synthStop){ audio.stopDance(); }
    else if(p.posiziona!==undefined){
      const rif=CONFIG[p.posiziona.riferimento]||{x:0,y:0};
      player.x=(p.posiziona.x??rif.x)+(p.posiziona.dx||0);
      player.y=(p.posiziona.y??rif.y)+(p.posiziona.dy||0);
      if(p.posiziona.dir) player.dir=p.posiziona.dir;
      setState('idle'); camInit=false;
    }
    else if(p.documento){
      renderDocumento(CONFIG.contratto.documento||{});
      contrattoEl.classList.add('show');
      contrattoEl.querySelector('.foglio').scrollTop=0;
      audio.sfx('item');
      await new Promise(res=>{ docClose=res; });
      docClose=null;
      contrattoEl.classList.remove('show');
      audio.sfx('click');
      await fadeNero(false);
      setState('idle');
    }
    else if(p.fine){ cinematic=false; frozen=false; maybeEnding(); }
  }
}

/* Il documento elegante (contratto/lettera/buono) è contenuto del pack:
   CONFIG.contratto.documento = { titolo, sotto, sezioni[{titolo,paragrafi[]}],
   meta[], firma, bottone }. I paragrafi possono contenere HTML dell'autore. */
function renderDocumento(doc){
  const h=[];
  if(doc.titolo) h.push(`<h2>${doc.titolo}</h2>`);
  if(doc.sotto)  h.push(`<div class="sub">${doc.sotto}</div>`);
  for(const sez of (doc.sezioni||[])){
    if(sez.titolo) h.push(`<h3>${sez.titolo}</h3>`);
    for(const par of (sez.paragrafi||[]))
      h.push(typeof par==='object' ? `<p class="nb">${par.nb}</p>` : `<p>${par}</p>`);
  }
  if(doc.meta && doc.meta.length)
    h.push('<div class="meta">'+doc.meta.map(m=>`<p>${m}</p>`).join('')+'</div>');
  if(doc.firma) h.push(`<div class="firma">${doc.firma}</div>`);
  contrattoEl.querySelector('.contenuto').innerHTML=h.join('\n');
  contrattoEl.querySelector('.chiudi').textContent=doc.bottone||('Chiudi '+SIM);
}

/* ---------- segreti a tocco diretto (nessun indicatore) ---------- */
function tryWindow(cssX,cssY){
  // gestita solo se il pack la vuole (CONFIG.finestra.attiva!==false); zona
  // personalizzabile (CONFIG.finestra.zona=[x0,x1,y0,y1]) o default in alto al centro
  if(CONFIG.finestra && CONFIG.finestra.attiva===false) return false;
  const z=(CONFIG.finestra && CONFIG.finestra.zona) || [41,60,2,27];
  const wx=(cssX/S+camX)/PCT, wy=(cssY/S+camY)/PCT;
  if(wx>z[0] && wx<z[1] && wy>z[2] && wy<z[3]){ trigger('interagisci:finestra'); return true; }
  return false;
}
// Il gatto può essere "rivelato per vicinanza": se cat.rivelaVicino è impostato,
// prima di sbloccarlo è visibile e cliccabile solo entro quel raggio.
function catVisibile(){
  if(!cat.rivelaVicino) return true;
  if(flag('segreto.gatto')) return true;
  return Math.hypot(player.x-cat.x, player.y-cat.y) < cat.rivelaVicino;
}
function tryCat(cssX,cssY){
  if(typeof SPR==='undefined' || !SPR.gatto) return false;   // ordini senza gatto
  if(!catVisibile()) return false;
  const wx=(cssX/S+camX)/PCT, wy=(cssY/S+camY)/PCT;
  const w=cat.larghezza, h=w*ASSETS.gatto.fh/ASSETS.gatto.fw;
  if(wx>cat.x-w/2-1.5 && wx<cat.x+w/2+1.5 && wy>cat.y-h-2 && wy<cat.y+1.5){
    trigger('interagisci:gatto'); return true;
  }
  return false;
}
// Punti segreti invisibili (es. l'abbraccio vicino alla porta): tocco diretto.
function tryPuntiSegreti(cssX,cssY){
  if(!CONFIG.puntiSegreti) return false;
  const wx=(cssX/S+camX)/PCT, wy=(cssY/S+camY)/PCT;
  for(const ps of CONFIG.puntiSegreti){
    const z=ps.zona;
    if(wx>z[0] && wx<z[1] && wy>z[2] && wy<z[3]){ trigger(ps.evento); return true; }
  }
  return false;
}
/* stella cadente: streak animato che attraversa l'oblò (impostato da una scena) */
let starFx=null;

/* ---------- finali a regole: la prima che si avvera vince ---------- */
function matchEnding(){ return STORY.finali.find(f=>cond(f.se)); }
function maybeEnding(){
  if(flag('finaleMostrato')) return;
  const r=matchEnding();
  if(r) setTimeout(()=>{ if(!flag('finaleMostrato')) showFinale(r); }, 550);
}
