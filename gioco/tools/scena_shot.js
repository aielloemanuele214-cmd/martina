/* Screenshot della SCENA di gioco composita (stanza + personaggi), superata la
   schermata d'ingresso. Uso: GAME_FILE=<html> OUT=<png> node tools/scena_shot.js
   Serve all'agente Art Director (FIG-10) per giudicare l'estetica finale. */
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { console.error('playwright non trovato (NODE_PATH)'); process.exit(2); }
const FILE = process.env.GAME_FILE, OUT = process.env.OUT;
if (!FILE || !fs.existsSync(FILE)) { console.error('GAME_FILE mancante:', FILE); process.exit(2); }
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
  // supera la schermata d'ingresso (tap al centro / bottone ENTRA), due volte per sicurezza
  for (let i = 0; i < 2; i++) { await pg.mouse.click(450, 450); await pg.waitForTimeout(900); }
  await pg.waitForTimeout(700);
  await pg.screenshot({ path: OUT });
  console.log(JSON.stringify({ ok: true, errs }));
  await br.close();
})().catch(e => { console.error(e.message); process.exit(1); });
