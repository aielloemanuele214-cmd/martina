/* Collaudo ANIMATO + INTERAZIONI: guida il gioco e cattura tre stati del
   personaggio (fermo, in camminata riflessa, in interazione) + verifica che
   un'interazione apra davvero il popup. Salva 3 png e stampa i flag funzionali.
   Uso: GAME_FILE=<html> OUTDIR=<dir> INTER=<id> node tools/collaudo_shot.js */
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { console.error('playwright non trovato'); process.exit(2); }
const FILE = process.env.GAME_FILE, OUTDIR = process.env.OUTDIR, INTER = process.env.INTER || '';
function chromePath() {
  const b = '/opt/pw-browsers';
  try { for (const d of fs.readdirSync(b)) { const p = `${b}/${d}/chrome-linux/chrome`; if (fs.existsSync(p)) return p; } } catch (e) {}
  return undefined;
}
(async () => {
  const br = await chromium.launch({ executablePath: chromePath() });
  const pg = await br.newPage({ viewport: { width: 900, height: 900 } });
  const errs = [];
  pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + FILE);
  await pg.waitForTimeout(1600);
  for (let i = 0; i < 2; i++) { await pg.mouse.click(450, 450); await pg.waitForTimeout(800); }
  // 1) FERMO
  await pg.evaluate(() => { player.state = 'idle'; player.dir = 'down'; });
  await pg.waitForTimeout(200);
  await pg.screenshot({ path: OUTDIR + '/c_idle.png' });
  // 2) CAMMINATA a SINISTRA (testa il mirroring): blocco il loop su un frame di passo
  const walk = await pg.evaluate(() => {
    if (typeof loop === 'function') { /* no-op */ }
    player.dir = 'left'; player.state = 'walk'; player.animT = 0.18;
    const pf = (typeof playerFrame === 'function') ? playerFrame() : null;
    return pf ? { key: pf.key, frame: pf.frame, flip: pf.flip } : null;
  });
  await pg.waitForTimeout(120);
  await pg.screenshot({ path: OUTDIR + '/c_walk.png' });
  // 3) INTERAZIONE: innesco un'interazione e catturo l'esito (popup/scena)
  let popupOpened = false;
  if (INTER) {
    await pg.evaluate((id) => {
      player.state = 'interact';
      if (typeof trigger === 'function') trigger('interagisci:' + id);
    }, INTER);
    await pg.waitForTimeout(900);
    popupOpened = await pg.evaluate(() => (typeof modalOpen !== 'undefined' && modalOpen) ||
      (typeof cinematic !== 'undefined' && cinematic) || (typeof diagOpen !== 'undefined' && diagOpen));
    await pg.screenshot({ path: OUTDIR + '/c_interact.png' });
  }
  console.log(JSON.stringify({ walk, popupOpened, errs }));
  await br.close();
})().catch(e => { console.error(e.message); process.exit(1); });
