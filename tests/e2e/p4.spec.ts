import { test, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { captureSession, expect, startJob } from './helpers';
const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
test.setTimeout(180000);
for (const width of [1440, 1280, 390]) {
  test(`unsupported real captures remain visible and ineligible at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    // Display-only controls, not fresh model responses or experimental evidence.
    await page.route('**/api/sessions', async route => {
      const response = await route.fetch();
      await route.fulfill({ response, json: [
        { id: 'ui-only-remote-control', sealed: true, metadata: { mode: 'remote_model', task_ref: 'UI control' } },
        { id: 'ui-only-partial-control', sealed: false, metadata: { mode: 'simulated', task_ref: 'UI control' } },
        ...await response.json(),
      ] });
    });
    await page.goto('/sessions');
    await expect(page.getByRole('table', { name: 'Latest captured sessions' })).toContainText('Hosted model');
    await expect(page.getByRole('table', { name: 'Latest captured sessions' })).toContainText('Partial / unsealed');
    await page.goto('/settings');
    await expect(page.getByRole('heading', { name: 'Hosted model (CLI only)' })).toBeVisible();
    await expect(page.getByText(/API\/Forensics real-model eligibility is unsupported/)).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(artifacts, `gemini-eligibility-${width}.png`), fullPage: true });
  });
  test(`actual deterministic investigation at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    const fatal: string[] = []; page.on('pageerror', e => fatal.push(e.message));
    await captureSession(page); const id = await startJob(page);
    await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
    if (!await page.getByRole('table', { name: 'Observable provenance nodes' }).isVisible()) await page.getByText(/Accessible provenance table ·/).click();
    await expect(page.getByRole('table', { name: 'Observable provenance nodes' })).toBeVisible();
    await page.getByText(/Evidence console ·/).click();
    await expect(page.getByRole('table', { name: 'Every stored subset and outcome' })).toBeVisible();
    await expect(page.getByText('No inferential interval for deterministic or incomplete samples.')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(artifacts, `p4-completed-${width}.png`), fullPage: true });
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
    expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id); expect(fatal).toEqual([]);
  });
}
test('fresh fixed-N confirmation survives refresh and reports stored counts', async ({ page }) => {
  await captureSession(page); await page.getByLabel('Stochastic simulator confirmation').check();
  const id = await startJob(page);
  await expect(page.getByText(/Confirmation plan frozen ·/)).toBeVisible();
  await page.reload(); await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  const trials = await (await page.request.get(`/api/investigations/${id}/trials?limit=100`)).json();
  expect(snapshot.completed_trials).toBe(trials.filter((t: { result: unknown }) => t.result).length);
  expect(snapshot.plan.n).toBe(40); expect(snapshot.findings[0].baseline.valid).toBe(40);
  expect(snapshot.findings[0].interval_level).toBe(0.95);
  await page.getByText(/Confirmation plan frozen ·/).click();
  await expect(page.locator('.progress-panel details pre')).toHaveText(snapshot.plan_json);
  await expect(page.getByText(/95.00% .* interval:/)).toBeVisible();
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({ path: path.join(artifacts, 'p4-confirmation.png'), fullPage: true });
});
test('no effect and unsupported replay are API-derived', async ({ page }) => {
  const session = await captureSession(page, 'harmless'); await startJob(page);
  await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  await expect(page.getByText('Evidence: no detected effect', { exact: true }).first()).toBeVisible();
  await page.screenshot({ path: path.join(artifacts, 'p4-no-effect.png'), fullPage: true });
  const response = await page.request.post('/api/investigations', { headers: { Origin: 'http://127.0.0.1:5173', 'X-REWIND-Local': '1', 'Idempotency-Key': crypto.randomUUID() }, data: { session_id: session, mode: 'playback' } });
  const unsupported = await response.json(); expect(unsupported.evidence_status).toBe('unsupported_replay');
  await page.goto(`/investigations/${unsupported.id}`);
  await expect(page.getByRole('heading', { name: 'Investigation status: failed' })).toBeVisible();
  await expect(page.getByText('Evidence: unsupported replay', { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(artifacts, 'p4-unsupported.png'), fullPage: true });
});
test('cancellation preserves the same durable job after refresh', async ({ page }) => {
  await captureSession(page); await page.getByLabel('Stochastic simulator confirmation').check(); const id = await startJob(page);
  await page.getByRole('button', { name: 'Cancel investigation' }).click();
  await expect(page.getByRole('heading', { name: 'Investigation status: cancelled' })).toBeVisible();
  await page.reload(); await expect(page.getByRole('heading', { name: 'Investigation status: cancelled' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  expect(snapshot.findings.every((f: { remedy_eligible: boolean }) => !f.remedy_eligible)).toBeTruthy();
  await page.screenshot({ path: path.join(artifacts, 'p4-cancelled.png'), fullPage: true });
});
test('weak-baseline uncertainty renders as inconclusive', async ({ page }) => {
  const session = await captureSession(page);
  const response = await page.request.post('/api/investigations', { headers: { Origin: 'http://127.0.0.1:5173', 'X-REWIND-Local': '1', 'Idempotency-Key': crypto.randomUUID() }, data: { session_id: session, stochastic: true, attempt_probability: 0.2, max_finalists: 1 } });
  const job = await response.json(); await page.goto(`/investigations/${job.id}`);
  await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  await expect(page.getByText('Evidence: inconclusive', { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/95.00% .* interval:/)).toBeVisible();
  await page.screenshot({ path: path.join(artifacts, 'p4-inconclusive.png'), fullPage: true });
});
test('worker process death becomes interrupted and remains truthful after refresh', async ({ page }) => {
  await captureSession(page); await page.getByLabel('Stochastic simulator confirmation').check(); const id = await startJob(page);
  await expect(page.getByText(/Confirmation plan frozen ·/)).toBeVisible();
  const pid = Number(fs.readFileSync(path.join(artifacts, 'worker.pid'), 'utf8'));
  expect(Number.isSafeInteger(pid) && pid > 0).toBeTruthy(); process.kill(pid, 'SIGKILL');
  await expect(page.getByRole('heading', { name: 'Investigation status: interrupted' })).toBeVisible();
  await page.reload(); await expect(page.getByRole('heading', { name: 'Investigation status: interrupted' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  expect(snapshot.findings.every((f: { interval: unknown; remedy_eligible: boolean }) => !f.interval && !f.remedy_eligible)).toBeTruthy();
  await page.screenshot({ path: path.join(artifacts, 'p4-interrupted.png'), fullPage: true });
});
