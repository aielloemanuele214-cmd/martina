const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
(async () => {
  const files = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const f of files) {
    const abs = path.resolve(f);
    const svg = fs.readFileSync(abs, 'utf8');
    // dimensione dinamica dal viewBox (profilo = 1080x1080)
    const m = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
    const w = Number(m[1]), h = Number(m[2]);
    await p.setViewportSize({ width: w, height: h });
    const style = (svg.match(/<style>([\s\S]*?)<\/style>/) || [,''])[1];
    const html = `<!doctype html><style>*{margin:0}body{width:${w}px;height:${h}px;overflow:hidden}
      svg{display:block}${style}</style>` + svg;
    await p.setContent(html, { waitUntil: 'load' });
    await p.evaluate(async () => {
      await Promise.all([
        document.fonts.load('800 100px "Baloo 2"'),
        document.fonts.load('700 100px "Baloo 2"'),
        document.fonts.load('400 40px Nunito'),
        document.fonts.load('700 40px Nunito'),
        document.fonts.load('400 20px "Press Start 2P"'),
      ]);
      await document.fonts.ready;
    });
    await p.waitForTimeout(120);
    const out = abs.replace(/\.svg$/, '.png');
    await p.screenshot({ path: out });
    console.log('render:', path.relative(process.cwd(), out));
  }
  await b.close();
})();
