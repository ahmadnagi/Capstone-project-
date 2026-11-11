const { chromium } = require('/opt/node-tools/node_modules/playwright');
const { spawn } = require('child_process');
const [,, html, out] = process.argv; const FPS = 30;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready);
  const total = await p.evaluate(() => TOTAL), N = Math.ceil(total * FPS);
  const ff = spawn('ffmpeg', ['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart', out], { stdio:['pipe','inherit','inherit'] });
  for (let f = 0; f < N; f++) {
    await p.evaluate(t => render(t), f / FPS);
    const buf = await p.screenshot({ type:'jpeg', quality:95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log('frames', N, 'seconds', total.toFixed(2));
})();
