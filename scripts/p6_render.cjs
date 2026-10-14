// Review the final built UI using already stored actual browser-trial facts. No new trials.
const fs = require('node:fs');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const source = path.resolve(process.argv[2] ?? '');
const allowed = path.join(root, 'artifacts', 'browser') + path.sep;
if (!source.startsWith(allowed) || !fs.existsSync(path.join(source, 'data', 'rewind.sqlite3'))) throw new Error('Provide an existing isolated browser artifact directory.');
const output = path.join(root, 'artifacts', 'p6', `render-${new Date().toISOString().replace(/[:.]/g, '-')}`);
fs.mkdirSync(output, { recursive: true });
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, '.tools', 'playwright');
const { chromium } = require('playwright');
const python = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const log = fs.openSync(path.join(output, 'servers.log'), 'w');
const api = spawn(python, ['-m', 'uvicorn', 'rewind_api.app:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: root, windowsHide: true, stdio: ['ignore', log, log], env: { ...process.env, REWIND_DATA_DIR: path.join(source, 'data') } });
const web = process.platform === 'win32'
  ? spawn('cmd.exe', ['/d', '/c', 'npm run preview --workspace apps/web'], { cwd: root, windowsHide: true, stdio: ['ignore', log, log] })
  : spawn('npm', ['run', 'preview', '--workspace', 'apps/web'], { cwd: root, stdio: ['ignore', log, log] });
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
function stop(child) { if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' }); else child.kill(); }
(async () => {
  let browser;
  try {
    for (const url of ['http://127.0.0.1:8000/api/health', 'http://127.0.0.1:5173']) {
      let ready = false;
      for (let i = 0; i < 100; i++) { try { if ((await fetch(url)).ok) { ready = true; break; } } catch {} await pause(200); }
      if (!ready) throw new Error(`Server did not become ready: ${url}`);
    }
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    const fatal = [], external = [], observations = [];
    page.on('pageerror', error => fatal.push(error.message));
    page.on('request', request => { if (new URL(request.url()).origin !== 'http://127.0.0.1:5173') external.push(request.url()); });
    await page.goto('http://127.0.0.1:5173/overview');
    await page.getByRole('button', { name: 'Capture demo scenario' }).waitFor();
    const get = async route => (await context.request.get(`http://127.0.0.1:5173${route}`)).json();
    const records = await get('/api/records');
    const runs = await get('/api/regression-runs');
    const run = runs.find(run => run.status === 'completed' && run.manifest?.kind === 'containment' && run.verdict === 'pass');
    const record = records.find(record => Object.values(record.regression_ids).includes(run?.case_id));
    if (!record || !run) throw new Error('No actual completed containment source to review.');
    const routes = [
      ['overview', '/overview', 'Start with the evidence.'],
      ['session', `/sessions/${record.session_id}`, 'Session explorer'],
      ['investigation', `/investigations/${record.investigation_id}`, 'Investigation'],
      ['record', `/ledger/${record.id}`, 'Evidence record'],
      ['regression', `/regressions?record=${record.id}&run=${run.id}`, 'Does the defence still hold?'],
    ];
    for (const width of [1440, 1280, 390]) {
      await page.setViewportSize({ width, height: width === 1440 ? 900 : width === 1280 ? 720 : 844 });
      for (const [name, route, heading] of routes) {
        await page.goto(`http://127.0.0.1:5173${route}`);
        await page.getByRole('heading', { name: heading, exact: true }).waitFor();
        if (name === 'session' || name === 'investigation') await page.getByRole('heading', { name: 'Observable provenance', exact: true }).waitFor();
        if (name === 'investigation') await page.getByRole('heading', { name: 'Investigation status: completed' }).waitFor();
        if (name === 'regression') await page.getByRole('heading', { name: 'Regression: completed · pass' }).waitFor();
        await page.evaluate(async () => { await document.fonts.ready; scrollTo(0, 0); });
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
        observations.push({ name, width, route, page_overflow: overflow });
        if (overflow) throw new Error(`Page overflow: ${name} ${width}`);
        await page.screenshot({ path: path.join(output, `${name}-${width}.png`), fullPage: true });
        await page.screenshot({ path: path.join(output, `${name}-${width}-viewport.png`) });
        if (name === 'investigation') await page.locator('.investigation-hero').screenshot({ path: path.join(output, `hero-${width}.png`) });
      }
    }
    fs.writeFileSync(path.join(output, 'review.json'), JSON.stringify({ source_artifacts: path.relative(root, source), record_id: record.id, run_id: run.id, observations, fatal, external, new_trials: 0 }, null, 2));
    if (fatal.length || external.length) throw new Error('Fatal error or external request during rendering.');
    fs.writeFileSync(path.join(root, 'artifacts/p6/render-latest.txt'), output);
    console.log(output);
  } finally { if (browser) await browser.close(); stop(web); stop(api); fs.closeSync(log); }
})().catch(error => { console.error(error); process.exitCode = 1; });
