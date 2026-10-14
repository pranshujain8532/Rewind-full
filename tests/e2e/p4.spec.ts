import { test, expect as baseExpect, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
test.setTimeout(180000);
const expect = baseExpect.configure({ timeout: 120000 });

async function startJob(page: Page) {
  const response = page.waitForResponse(r => r.url().endsWith('/api/investigations') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Start investigation' }).click();
  const job = await (await response).json();
  await expect(page.locator('.job-result')).toHaveAttribute('data-job-id', job.id);
  return job.id as string;
}

for (const width of [1440, 1280, 390]) {
  test(`unsupported real captures remain visible and ineligible at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    // Display-only admission controls, not model responses or experimental evidence.
    await page.route('**/api/sessions', async route => {
      const response = await route.fetch();
      await route.fulfill({ response, json: [
        { id: 'ui-only-remote-control', sealed: true, metadata: { mode: 'remote_model', task_ref: 'UI control' } },
        { id: 'ui-only-partial-control', sealed: false, metadata: { mode: 'simulated', task_ref: 'UI control' } },
        ...await response.json(),
      ] });
    });
    const unsupportedGraphRequests: string[] = [];
    page.on('request', request => {
      if (request.url().includes('/api/sessions/ui-only-')) unsupportedGraphRequests.push(request.url());
    });
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
    const select = page.getByLabel('Captured session');
    await expect(select.locator('option[value="ui-only-remote-control"]')).toHaveJSProperty('disabled', true);
    await expect(select.locator('option[value="ui-only-partial-control"]')).toHaveJSProperty('disabled', true);
    expect(await select.inputValue()).not.toContain('ui-only-');
    await expect(page.getByText('Hosted model (CLI only)', { exact: true })).toBeVisible();
    expect(unsupportedGraphRequests).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.screenshot({ path: path.join(artifacts, `gemini-eligibility-${width}.png`), fullPage: true });
  });
}

for (const width of [1440, 1280, 390]) {
  test(`actual deterministic investigation at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    const fatal: string[] = [];
    page.on('pageerror', e => fatal.push(e.message));
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
    await page.getByRole('button', { name: 'Capture demo scenario' }).click();
    await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
    await startJob(page);
    await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Recorded sessions are ready.' })).toBeVisible();
    const id = await page.locator('.job-result').getAttribute('data-job-id');
    await page.getByText(/Observable provenance ·/).click();
    await expect(page.getByRole('table', { name: 'Candidate ranking and input provenance' })).toBeVisible();
    await page.getByText(/Search coverage ·/).click();
    await expect(page.getByText('No inferential interval for deterministic or incomplete samples.')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.screenshot({ path: path.join(artifacts, `p4-completed-${width}.png`), fullPage: true });
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
    expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
    expect(fatal).toEqual([]);
  });
}

test('fresh fixed-N confirmation survives refresh and reports stored counts', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
  await page.getByLabel('Stochastic simulator confirmation').check();
  await startJob(page);
  await expect(page.getByText(/Confirmation plan frozen/)).toBeVisible();
  const id = await page.locator('.job-result').getAttribute('data-job-id');
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  const trials = await (await page.request.get(`/api/investigations/${id}/trials?limit=100`)).json();
  expect(snapshot.completed_trials).toBe(trials.filter((t: { result: unknown }) => t.result).length);
  expect(snapshot.plan.n).toBe(40);
  expect(snapshot.findings[0].baseline.valid).toBe(40);
  expect(snapshot.findings[0].interval_level).toBe(0.95);
  await expect(page.getByText(/95.00% Newcombe interval/)).toBeVisible();
  await page.screenshot({ path: path.join(artifacts, 'p4-confirmation.png'), fullPage: true });
});

test('no-effect and unsupported states render from the API', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
  await page.getByLabel('Owned scenario').selectOption('harmless');
  await page.getByRole('button', { name: 'Capture demo scenario' }).click();
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
  await startJob(page);
  await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  await expect(page.getByRole('heading', { name: /comment-0 · no_detected_effect/ })).toBeVisible();
  await page.screenshot({ path: path.join(artifacts, 'p4-no-effect.png'), fullPage: true });
  const session = await page.getByLabel('Captured session').inputValue();
  const response = await page.request.post('/api/investigations', {
    headers: { Origin: 'http://127.0.0.1:5173', 'X-REWIND-Local': '1', 'Idempotency-Key': crypto.randomUUID() },
    data: { session_id: session, mode: 'playback' },
  });
  const unsupported = await response.json();
  expect(unsupported.evidence_status).toBe('unsupported_replay');
  await page.evaluate(id => localStorage.setItem('rewind-investigation-id', id), unsupported.id);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Investigation status: failed' })).toBeVisible();
  await expect(page.getByRole('status')).toContainText('unsupported_replay');
  await page.screenshot({ path: path.join(artifacts, 'p4-unsupported.png'), fullPage: true });
});

test('cancellation preserves the same durable job after refresh', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
  await page.getByLabel('Stochastic simulator confirmation').check();
  await startJob(page);
  await expect(page.getByRole('button', { name: 'Cancel investigation' })).toBeVisible();
  const id = await page.locator('.job-result').getAttribute('data-job-id');
  await page.getByRole('button', { name: 'Cancel investigation' }).click();
  await expect(page.getByRole('heading', { name: 'Investigation status: cancelled' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Investigation status: cancelled' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  expect(snapshot.findings.every((f: { remedy_eligible: boolean }) => !f.remedy_eligible)).toBeTruthy();
  await page.screenshot({ path: path.join(artifacts, 'p4-cancelled.png'), fullPage: true });
});

test('weak-baseline uncertainty renders as inconclusive', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
  await page.getByRole('button', { name: 'Capture demo scenario' }).click();
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
  const session = await page.getByLabel('Captured session').inputValue();
  const response = await page.request.post('/api/investigations', {
    headers: { Origin: 'http://127.0.0.1:5173', 'X-REWIND-Local': '1', 'Idempotency-Key': crypto.randomUUID() },
    data: { session_id: session, stochastic: true, attempt_probability: 0.2, max_finalists: 1 },
  });
  const job = await response.json();
  await page.evaluate(id => localStorage.setItem('rewind-investigation-id', id), job.id);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  await expect(page.getByRole('heading', { name: /comment-0 · inconclusive/ })).toBeVisible();
  await expect(page.getByText(/95.00% Newcombe interval/)).toBeVisible();
  await page.screenshot({ path: path.join(artifacts, 'p4-inconclusive.png'), fullPage: true });
});

test('worker process death becomes interrupted and remains truthful after refresh', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
  await page.getByLabel('Stochastic simulator confirmation').check();
  await startJob(page);
  await expect(page.getByText(/Confirmation plan frozen/)).toBeVisible();
  const id = await page.locator('.job-result').getAttribute('data-job-id');
  const pid = Number(fs.readFileSync(path.join(artifacts, 'worker.pid'), 'utf8'));
  expect(Number.isSafeInteger(pid) && pid > 0).toBeTruthy();
  process.kill(pid, 'SIGKILL'); // Only the worker created by this isolated browser test harness.
  await expect(page.getByRole('heading', { name: 'Investigation status: interrupted' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Investigation status: interrupted' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  expect(snapshot.findings.every((f: { interval: unknown; remedy_eligible: boolean }) => !f.interval && !f.remedy_eligible)).toBeTruthy();
  await page.screenshot({ path: path.join(artifacts, 'p4-interrupted.png'), fullPage: true });
});
