/* Playtest visivo + funzionale di L'Ultima Orbita: guida il gioco, scatta
   screenshot nei momenti chiave e verifica i 3 segreti (gatto, stella, abbraccio)
   e il finale. Uso: GAME_FILE=dist/base-ultima-orbita.html node tools/orbita_playtest.js */
const fs = require('fs');
const { chromium } = require('playwright');
const FILE = process.env.GAME_FILE;
const OUT = process.env.SHOT_DIR || '/home/user/martina/packs/ultima-orbita/assets/_dbg';
function chromePath(){ const b='/opt/pw-browsers'; try{ for(const d of fs.readdirSync(b)){ const p=`${b}/${d}/chrome-linux/chrome`; if(fs.existsSync(p)) return p; } }catch(e){} }

(async () => {
  const b = await chromium.launch({ executablePath: chromePath() });
  const p = await b.newPage({ viewport: { width: 900, height: 700 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + FILE + '?reset=1'); await p.waitForTimeout(2200);
  await p.click('#splash'); await p.waitForTimeout(400);
  await p.click('#splash'); await p.waitForTimeout(1200);
  const shot = async n => { await p.screenshot({ path: `${OUT}/pt_${n}.png` }); console.log('  shot', n); };

  // 1. panoramica stanza
  await shot('01_room');

  // 2. cammina verso l'oblò e apri il popup
  await p.evaluate(() => { player.x = 50; player.y = 50; setState('idle'); });
  await p.evaluate(() => trigger('interagisci:oblo')); await p.waitForTimeout(700);
  await shot('02_oblo_popup');
  const oblo = await p.evaluate(() => modalOpen && flag('trovato.oblo'));
  await p.evaluate(() => closePopup()); await p.waitForTimeout(300);

  // 3. diario
  await p.evaluate(() => trigger('interagisci:diario')); await p.waitForTimeout(600);
  await shot('03_diario_popup');
  const diario = await p.evaluate(() => modalOpen && flag('trovato.diario'));
  await p.evaluate(() => closePopup()); await p.waitForTimeout(300);

  // 4. lettore → scena musica (coppia davanti all'oblò)
  await p.evaluate(() => trigger('interagisci:lettore'));
  await p.waitForTimeout(3200); await shot('04_lettore_coppia');
  let guard = 0; while (guard < 15000 && await p.evaluate(() => cinematic)) { await p.waitForTimeout(400); guard += 400; }
  const lettore = await p.evaluate(() => flag('trovato.lettore'));

  // 5. gatto: reveal per vicinanza (lontano = invisibile, vicino = visibile)
  await p.evaluate(() => { player.x = 55; player.y = 70; setState('idle'); });
  await p.waitForTimeout(200); await shot('05a_gatto_lontano');
  await p.evaluate(() => { player.x = 74; player.y = 85; setState('idle'); });
  await p.waitForTimeout(200); await shot('05b_gatto_vicino');
  await p.evaluate(() => trigger('interagisci:gatto')); await p.waitForTimeout(700);
  await shot('05c_gatto_fusa');
  guard = 0; while (guard < 8000 && await p.evaluate(() => cinematic)) { await p.waitForTimeout(300); guard += 300; }
  await p.waitForTimeout(300);
  const gattoDlg = await p.evaluate(() => diagOpen);
  await p.evaluate(() => { if (diagOpen) closeDialog(); }); await p.waitForTimeout(200);
  const gatto = await p.evaluate(() => flag('segreto.gatto'));

  // 6. stella cadente: ferma davanti all'oblò (simulo l'attesa impostando fermoT)
  await p.evaluate(() => { player.x = 50; player.y = 50; setState('idle'); percorso.length = 0; });
  await p.evaluate(() => { player.fermoT = 9.9; });
  await p.waitForTimeout(500); await shot('06_stella');
  guard = 0; while (guard < 8000 && await p.evaluate(() => cinematic)) { await p.waitForTimeout(300); guard += 300; }
  const stella = await p.evaluate(() => flag('segreto.stella'));

  // 7. abbraccio: tocco sul punto invisibile vicino alla porta
  await p.evaluate(() => { const z = CONFIG.puntiSegreti[0].zona;
    const wx = (z[0] + z[1]) / 2, wy = (z[2] + z[3]) / 2;
    handleTap((wx * PCT - camX) * S, (wy * PCT - camY) * S); });
  await p.waitForTimeout(2600); await shot('07_abbraccio');
  guard = 0; while (guard < 18000 && await p.evaluate(() => cinematic)) { await p.waitForTimeout(300); guard += 300; }
  const abbraccio = await p.evaluate(() => flag('segreto.abbraccio'));

  // 8. finale (tutti e 6 i flag → deve comparire)
  await p.waitForTimeout(900); await shot('08_finale');
  const finale = await p.evaluate(() => document.getElementById('finale').className.includes('show'));
  const hudGold = await p.evaluate(() => document.querySelectorAll('#hearts .oro').length);

  console.log('\nRISULTATI:');
  const r = { oblo, diario, lettore, gatto, gattoDlg, stella, abbraccio, finale, hudGold, errs: errs.length };
  for (const [k, v] of Object.entries(r)) console.log(`  ${k}: ${v}`);
  if (errs.length) console.log('  ERRORI JS:', errs.slice(0, 4));
  await b.close();
  const okAll = oblo && diario && lettore && gatto && stella && abbraccio && finale && hudGold === 3 && errs.length === 0;
  console.log(okAll ? '\n✓ TUTTO OK' : '\n✗ QUALCOSA NON VA');
  process.exit(okAll ? 0 : 1);
})();
