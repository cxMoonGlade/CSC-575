const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require('/tmp/ah-visual-browser-20261019/node_modules/playwright');
const project = '/home/cx/Documents/csc475/Proj';
const stage = '/tmp/csc575-rubric-revision-2026-11-16';
const source = path.join(project, 'results/root_optimization/demo_projection/playback.html');
const csv = path.join(project, 'results/root_optimization/demo_projection/prediction.csv');
const sha256 = filename => crypto.createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
(async () => {
  const browser = await chromium.launch({ executablePath: '/tmp/csc475_browsers/chromium-1248/chrome-linux64/chrome', headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 650, height: 700 }, deviceScaleFactor: 3 });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto('file://' + source);
  await page.waitForFunction(() => document.querySelector('#audio').readyState >= 1);
  const payloadBefore = await page.locator('#payload').textContent();
  await page.locator('#start').fill('0');
  await page.locator('#end').fill('0.3');
  await page.locator('#play-range').click();
  await page.waitForFunction(() => document.querySelector('#audio').paused && Math.abs(document.querySelector('#audio').currentTime - 0.3) < 0.01);
  const playbackStop = await page.locator('#audio').evaluate(a => a.currentTime);
  await page.locator('#audio').evaluate(a => { a.currentTime = 0; });
  await page.locator('#end').fill('8');
  await page.locator('#focus').click();
  const checks = await page.evaluate(() => {
    const data = JSON.parse(document.querySelector('#payload').textContent);
    return { duration: document.querySelector('#audio').duration, visibleInterval: document.querySelector('#zoom-title').textContent, reference: data.tracks[0][1][0], long: data.tracks[1][1][0], projection: data.tracks[2][1][0] };
  });
  if (checks.reference[2] !== 'C:maj/3' || checks.long[2] !== 'E:min' || checks.projection[2] !== 'C:maj') throw new Error('Unexpected saved labels');
  await page.addStyleTag({content: `
    html { background: white; }
    body { margin: 0; padding: 8px; width: 634px; max-width: none; font: 20px Arial, sans-serif; background: white; color: #182831; }
    body > :not(.controls):not(#zoom-title):not(#detail):not(style):not(script) { display: none !important; }
    .controls { margin: 0 0 8px; gap: 8px; display: flex; flex-wrap: nowrap; }
    .controls label:has(#examples), #play-context, #whole { display: none; }
    .controls label { display: flex; align-items: center; gap: 4px; white-space: nowrap; }
    .controls input { width: 45px; padding: 3px; }
    .controls button { padding: 5px 8px; white-space: nowrap; }
    #zoom-title { font-size: 20px; font-weight: 400; margin: 4px 0 8px; }
    #detail { display: block; width: 634px; }
    @page { margin: 0; }
  `});
  await page.evaluate(() => {
    const svg = document.querySelector('#detail');
    const left = 158, inner = 448, originalLeft = 140, originalInner = 995;
    const transformX = x => left + (x - originalLeft) / originalInner * inner;
    svg.setAttribute('viewBox', '0 0 634 183');
    for (const item of svg.children) {
      for (const attr of ['x', 'x1', 'x2']) if (item.hasAttribute(attr)) {
        const x = Number(item.getAttribute(attr));
        if (x >= originalLeft) item.setAttribute(attr, transformX(x));
      }
      if (item.tagName === 'rect') item.setAttribute('width', Number(item.getAttribute('width')) * inner / originalInner);
      if (item.tagName === 'text') item.setAttribute('font-size', '20');
    }
  });
  const payloadAfter = await page.locator('#payload').textContent();
  if (payloadAfter !== payloadBefore) throw new Error('Saved predictions changed');
  const bounds = await page.locator('body').boundingBox();
  const height = Math.ceil(bounds.height);
  await page.setViewportSize({ width: 650, height });
  await page.screenshot({ path: path.join(stage, 'report/figures/demo_progress.png'), fullPage: true });
  await page.pdf({ path: path.join(stage, 'report/figures/demo_progress.pdf'), width: '650px', height: `${height}px`, printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  if (errors.length) throw new Error(errors.join('\n'));
  const provenance = {
    source, source_sha256: sha256(source), csv, csv_sha256: sha256(csv),
    data_unchanged: payloadBefore === payloadAfter,
    capture_width_css_px: 650, capture_height_css_px: height, screenshot_scale: 3,
    presentation: 'Compact view of the existing player. Surrounding prose, full-recording overview, selector, and context/whole-recording buttons hidden for capture. Existing start/end, focus/play controls and selected timeline retained. Text enlarged and SVG x-coordinates rescaled for column legibility. No prediction, audio, label, or feature data changed.',
    displayed_interval_seconds: [0, 8], displayed_timeline_with_context_seconds: [0, 9],
    checks, playback_interval_stop_seconds: playbackStop, csv_header_and_first_row: fs.readFileSync(csv,'utf8').split('\n').slice(0,2),
    caption: 'Compact player view for a GuitarSet development excerpt. Projection recovers C major where Long STFT predicts E minor. Interval controls support listening; CSV output stores each segment’s start, end and label.'
  };
  fs.writeFileSync(path.join(stage, 'demo_work/provenance.json'), JSON.stringify(provenance,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({width:650,height,checks,errors}));
})();
