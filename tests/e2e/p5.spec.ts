import { test, expect as baseExpect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';

const expect = baseExpect.configure({ timeout: 90000 });
const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
test.setTimeout(180000);

// The P4 kill probe deliberately ends its worker. Restart only that harness worker.
test.beforeAll(() => {
  const pid = Number(fs.readFileSync(path.join(artifacts, 'worker.pid'), 'utf8'));
  try { process.kill(pid, 0); }
  catch {
    const python = path.resolve('.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
    const child = spawn(python, ['-m', 'rewind_eval.worker'], { cwd: process.cwd(), stdio: 'ignore', windowsHide: true,
      env: { ...process.env, REWIND_DATA_DIR: path.join(artifacts, 'data') } });
    fs.writeFileSync(path.join(artifacts, 'p5-worker.pid'), String(child.pid));
  }
});
test.afterAll(() => {
  const p = path.join(artifacts, 'p5-worker.pid');
  if (fs.existsSync(p)) {
    const pid = Number(fs.readFileSync(p, 'utf8'));
    if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
    else try { process.kill(pid); } catch { /* already stopped */ }
  }
});

for (const width of [1440, 1280, 390]) {
  test(`signed bundle and original-attack regression at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
    await page.getByRole('button', { name: 'Capture demo scenario' }).click();
    await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
    await page.getByRole('button', { name: 'Start investigation' }).click();
    await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
    await page.getByRole('button', { name: 'Create signed record' }).click();
    await expect(page.getByText(/Governance mapping pending/)).toBeVisible();
    const downloadEvent = page.waitForEvent('download');
    await page.getByRole('link', { name: 'Download signed evidence bundle', exact: true }).click();
    const download = await downloadEvent;
    const destination = path.join(artifacts, `p5-evidence-${width}.json`);
    await download.saveAs(destination);
    const bundle = JSON.parse(fs.readFileSync(destination, 'utf8'));
    expect(bundle.format).toBe('rewind-evidence-v1');
    expect(bundle.report.mode).toBe('simulated');
    expect(bundle.report.governance_mapping.entries).toEqual([]);
    const publicKey = fs.readFileSync(path.join(artifacts, 'data', 'keys', 'trusted-public.ed25519')).toString('hex');
    const verification = await page.request.post('/api/records/verify', { headers: { Origin: 'http://127.0.0.1:5173', 'X-REWIND-Local': '1', 'Content-Type': 'application/json', 'X-REWIND-Trusted-Public-Key': publicKey }, data: fs.readFileSync(destination) });
    expect((await verification.json()).integrity_valid).toBeTruthy();
    const firstResponse = page.waitForResponse(r => r.url().endsWith('/api/regression-runs') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Run original-attack regression' }).click();
    const firstRun = await (await firstResponse).json();
    await expect(page.locator('[data-regression-id]')).toHaveAttribute('data-regression-id', firstRun.id);
    await expect(page.getByRole('heading', { name: 'Regression: completed · pass' })).toBeVisible();
    await expect(page.getByRole('table', { name: 'Original-attack safety and useful task' })).toContainText('vulnerable');
    const id = await page.locator('[data-regression-id]').getAttribute('data-regression-id');
    const result = await (await page.request.get(`/api/regression-runs/${id}`)).json();
    expect(result.manifest.arms.vulnerable.status).toBe('fail');
    expect(result.manifest.arms.fixed.harmful_attempts).toBe(0);
    expect(result.manifest.arms.fixed.task_success).toBeTruthy();
    expect(result.manifest.interval).toBeNull();
    await page.getByLabel('Regression contract').selectOption('containment');
    const secondResponse = page.waitForResponse(r => r.url().endsWith('/api/regression-runs') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Run original-attack regression' }).click();
    const secondRun = await (await secondResponse).json();
    await expect(page.locator('[data-regression-id]')).toHaveAttribute('data-regression-id', secondRun.id);
    await expect(page.getByRole('heading', { name: 'Regression: completed · pass' })).toBeVisible();
    const containmentId = await page.locator('[data-regression-id]').getAttribute('data-regression-id');
    const containment = await (await page.request.get(`/api/regression-runs/${containmentId}`)).json();
    expect(containment.manifest.arms.fixed.harmful_attempts).toBe(1);
    expect(containment.manifest.arms.fixed.harmful_dispatches).toBe(0);
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Regression: completed · pass' })).toBeVisible();
    expect(await page.locator('[data-regression-id]').getAttribute('data-regression-id')).toBe(containmentId);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.screenshot({ path: path.join(artifacts, `p5-ledger-${width}.png`), fullPage: true });
    await page.locator('.ledger-panel').screenshot({ path: path.join(artifacts, `p5-detail-${width}.png`) });
  });
}
