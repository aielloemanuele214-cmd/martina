
/* Glifo del legame: ❤ per gli ordini romantici (default), simbolo neutro
   (es. ✦) per i registri fraterni/amicali. Da settings.json → simbolo. */
const SIM = (typeof CONFIG !== 'undefined' && CONFIG.simbolo) ? CONFIG.simbolo : '❤';

/* ============================================================
   AUDIO — synth chiptune Web Audio (nessun file audio)
   ============================================================ */
class ChiptuneAudio {
  constructor(){
    this.ctx=null; this.muted=false; this.isPlaying=false; this.timer=null;
    /* Loop di sottofondo "caldo": 16 battute, Do–Lam–Fa–Sol, timbri morbidi */
    this.tempo=84; this.beat=60/this.tempo;
    this.melody=[
      ['E',4,2],['G',4,2],['C',5,4], ['B',4,2],['A',4,2],['G',4,4],
      ['A',4,2],['C',5,2],['D',5,4], ['B',4,2],['D',5,2],['G',4,4],
      ['E',5,2],['D',5,2],['C',5,4], ['C',5,2],['B',4,2],['A',4,4],
      ['A',4,2],['B',4,2],['C',5,4], ['D',5,2],['B',4,2],['C',5,4]];
    this.harmony=[['G',3,8],['E',3,8],['A',3,8],['D',4,8],
                  ['G',3,8],['E',3,8],['A',3,8],['D',4,8]];
    this.bass=[['C',3,8],['A',2,8],['F',2,8],['G',2,8],
               ['C',3,8],['A',2,8],['F',2,8],['G',2,8]];
    this.arp=[
      ['C',4,.5],['E',4,.5],['G',4,.5],['C',5,.5],['G',4,.5],['E',4,.5],['C',4,.5],[null,0,4.5],
      ['A',3,.5],['C',4,.5],['E',4,.5],['A',4,.5],['E',4,.5],['C',4,.5],['A',3,.5],[null,0,4.5],
      ['F',3,.5],['A',3,.5],['C',4,.5],['F',4,.5],['C',4,.5],['A',3,.5],['F',3,.5],[null,0,4.5],
      ['G',3,.5],['B',3,.5],['D',4,.5],['G',4,.5],['D',4,.5],['B',3,.5],['G',3,.5],[null,0,4.5],
      ['C',4,.5],['E',4,.5],['G',4,.5],['C',5,.5],['G',4,.5],['E',4,.5],['C',4,.5],[null,0,4.5],
      ['A',3,.5],['C',4,.5],['E',4,.5],['A',4,.5],['E',4,.5],['C',4,.5],['A',3,.5],[null,0,4.5],
      ['F',3,.5],['A',3,.5],['C',4,.5],['F',4,.5],['C',4,.5],['A',3,.5],['F',3,.5],[null,0,4.5],
      ['G',3,.5],['B',3,.5],['D',4,.5],['G',4,.5],['D',4,.5],['B',3,.5],['G',3,.5],[null,0,4.5]];
    this.freqs={C:16.35,'C#':17.32,D:18.35,'D#':19.45,E:20.60,F:21.83,'F#':23.12,G:24.50,'G#':25.96,A:27.50,'A#':29.14,B:30.87};
  }
  init(){ if(!this.ctx) this.ctx=new (window.AudioContext||window.webkitAudioContext)();
    if(this.ctx.state==='suspended') this.ctx.resume(); }
  f(n,o){ return n? this.freqs[n]*Math.pow(2,o) : 0; }
  tone(freq,dur,type,vol,t){ if(!this.ctx) return;
    const o=this.ctx.createOscillator(), g=this.ctx.createGain();
    o.type=type; o.frequency.setValueAtTime(freq,t);
    g.gain.setValueAtTime(vol,t); g.gain.exponentialRampToValueAtTime(.001,t+dur);
    o.connect(g); g.connect(this.ctx.destination); o.start(t); o.stop(t+dur); }
  noise(dur,vol,t){ if(!this.ctx) return;
    const n=this.ctx.sampleRate*dur, b=this.ctx.createBuffer(1,n,this.ctx.sampleRate), d=b.getChannelData(0);
    for(let i=0;i<n;i++) d[i]=Math.random()*2-1;
    const s=this.ctx.createBufferSource(); s.buffer=b;
    const f=this.ctx.createBiquadFilter(); f.type='bandpass'; f.frequency.value=350;
    const g=this.ctx.createGain(); g.gain.setValueAtTime(vol,t); g.gain.exponentialRampToValueAtTime(.001,t+dur);
    s.connect(f); f.connect(g); g.connect(this.ctx.destination); s.start(t); s.stop(t+dur); }
  /* Effetti morbidi e romantici: solo timbri sine/triangle, mai squillanti */
  soft(freq,dur,vol,t,type){ if(!this.ctx) return;
    const o=this.ctx.createOscillator(), g=this.ctx.createGain();
    o.type=type||'sine'; o.frequency.setValueAtTime(freq,t);
    g.gain.setValueAtTime(0.0001,t);
    g.gain.exponentialRampToValueAtTime(vol,t+0.03);      // attacco dolce
    g.gain.exponentialRampToValueAtTime(0.0001,t+dur);     // rilascio lungo
    o.connect(g); g.connect(this.ctx.destination); o.start(t); o.stop(t+dur+.02); }
  sfx(type){ if(this.muted) return; this.init(); const now=this.ctx.currentTime;
    if(type==='click'){                       // tocco leggero
      this.soft(880,.22,.05,now); }
    else if(type==='item'){                    // scoperta: arpeggio caldo
      this.soft(523.25,.5,.06,now); this.soft(659.25,.5,.055,now+.09);
      this.soft(783.99,.6,.05,now+.18); this.soft(1046.5,.9,.05,now+.27); }
    else if(type==='meow'){                    // fusa morbide del gatto
      this.soft(300,.5,.05,now,'triangle'); this.soft(360,.5,.04,now+.18,'triangle'); }
    else if(type==='type'){                    // tasto/lettera, delicatissimo
      this.soft(820+Math.random()*160,.05,.02,now,'sine'); }
    else if(type==='fanfare'){                 // finale: accordo caldo che si apre
      this.soft(392,1.6,.05,now); this.soft(523.25,1.6,.05,now+.05);
      this.soft(659.25,1.8,.05,now+.12); this.soft(783.99,2.0,.045,now+.2);
      this.soft(1046.5,2.2,.04,now+.4); } }
  start(){ if(this.muted||this.isPlaying) return; this.init(); this.isPlaying=true;
    let mi=0,hi=0,bi=0,ai=0;
    let tm=this.ctx.currentTime+.1, th=tm, tb=tm, ta=tm;
    const chans=[
      [this.melody, ()=>tm, v=>tm=v, ()=>mi, v=>mi=v, 'triangle', .05, .04],
      [this.harmony,()=>th, v=>th=v, ()=>hi, v=>hi=v, 'sine',    .022,.05],
      [this.bass,   ()=>tb, v=>tb=v, ()=>bi, v=>bi=v, 'triangle', .055,.05],
      [this.arp,    ()=>ta, v=>ta=v, ()=>ai, v=>ai=v, 'sine',    .014,.02],
    ];
    const loop=()=>{ if(!this.isPlaying) return;
      const now=this.ctx.currentTime, ahead=.3;
      for(const [notes,gt,st,gi,si,type,vol,gap] of chans){
        let t=gt(), i=gi();
        while(t<now+ahead){ const nt=notes[i], dur=nt[2]*this.beat;
          if(nt[0]) this.tone(this.f(nt[0],nt[1]), dur-gap, type, vol, t);
          t+=dur; i=(i+1)%notes.length; }
        st(t); si(i); }
      this.timer=setTimeout(loop,100); };
    loop(); }
  stop(){ this.isPlaying=false; if(this.timer){clearTimeout(this.timer); this.timer=null;} }
  /* Valzer soffuso per la scena del ballo (suona "dal giradischi") */
  startDance(){ if(this.danceOn) return; this.init(); this.danceOn=true;
    const seq=[['C',4],['E',4],['G',4],['A',3],['C',4],['E',4],
               ['F',3],['A',3],['C',4],['G',3],['B',3],['D',4]];
    const beat=.42; let i=0, t=this.ctx.currentTime+.05;
    const loop=()=>{ if(!this.danceOn) return;
      const now=this.ctx.currentTime;
      while(t<now+.5){
        const n=seq[i%seq.length];
        if(!this.muted){
          this.tone(this.f(n[0],n[1]), beat*.92, 'triangle', .05, t);
          this.tone(this.f(n[0],n[1]+1), beat*.8, 'sine', .018, t);
          if(i%3===0) this.tone(this.f(n[0],2), beat*2.7, 'sine', .045, t);
        }
        t+=beat; i++;
      }
      this.danceTimer=setTimeout(loop,120);
    };
    loop();
  }
  stopDance(){ this.danceOn=false; if(this.danceTimer){clearTimeout(this.danceTimer); this.danceTimer=null;} }
  toggle(){ this.muted=!this.muted;
    if(this.muted){ this.stop(); this.stopDance(); musMenu.pause(); musGame.pause(); }
    else { this.init();
      if(CONFIG.musica){
        if(inGioco){ musGame.volume=.55; musGame.play().catch(()=>{}); }
        else avviaMusicaMenu();
      } }
    return this.muted; }
}
const audio = new ChiptuneAudio();

/* ---------- colonna sonora mp3 (menù + gioco, con crossfade) ---------- */
const musMenu=new Audio(), musGame=new Audio();
musMenu.src=MUSICHE.menu;  musMenu.loop=true;  musMenu.volume=.6;
musGame.src=MUSICHE.gioco; musGame.loop=true;  musGame.volume=0;
musMenu.preload='auto'; musGame.preload='auto';
let inGioco=false;
function fadeAudio(el,to,ms){
  const da=el.volume, t0=performance.now();
  const step=()=>{
    const k=Math.min(1,(performance.now()-t0)/ms);
    el.volume=Math.max(0,Math.min(1,da+(to-da)*k));
    if(k<1) requestAnimationFrame(step);
    else if(to===0) el.pause();
  };
  step();
}
function avviaMusicaMenu(){
  if(!CONFIG.musica||audio.muted) return;
  musMenu.volume=.6; musMenu.play().catch(()=>{});
}
function avviaMusicaGioco(){
  if(!CONFIG.musica||audio.muted) return;
  if(!musMenu.paused) fadeAudio(musMenu,0,900);
  musGame.volume=0; musGame.play().catch(()=>{});
  fadeAudio(musGame,.55,1500);
}

