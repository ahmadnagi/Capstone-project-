// usage: node render2.js page.html times.json total  preview <outdir> t1 t2 ...   |   video <out.mp4> <events.json>
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const { spawn } = require('child_process'); const fs = require('fs');
const [,, html, timesPath, total, mode, out, ...rest] = process.argv; const FPS = 30;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
  p.on('pageerror', e => { console.error('PAGEERR', e.message); process.exitCode = 1; });
  await p.addInitScript(([t, tot]) => { window.TIMES = t; window.TOTAL = tot; }, [JSON.parse(fs.readFileSync(timesPath)), +total]);
  await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready);
  if (mode === 'events') { for (let f = 0; f < Math.ceil(+total*FPS); f++) await p.evaluate(t => render(t), f/FPS); fs.writeFileSync(out, JSON.stringify(await p.evaluate(() => window.__ev))); }
  else if (mode === 'preview') {
    for (const t of rest) { await p.evaluate(t => render(t), +t); await p.screenshot({ path: `${out}/f_${t}.png` }); }
  } else {
    const N = Math.ceil(+total * FPS);
    const ff = spawn('ffmpeg', ['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-level','4.0', out], { stdio:['pipe','inherit','inherit'] });
    for (let f = 0; f < N; f++) {
      await p.evaluate(t => render(t), f / FPS);
      const buf = await p.screenshot({ type:'jpeg', quality:95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    fs.writeFileSync(rest[0], JSON.stringify(await p.evaluate(() => window.__ev)));
    console.log('frames', N);
  }
  await b.close();
})();
