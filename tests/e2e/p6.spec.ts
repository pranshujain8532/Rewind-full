import { test } from '@playwright/test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { captureSession, expect, startJob } from './helpers';
import { recoverHarnessWorker, stopHarnessWorker } from './worker';

const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
test.setTimeout(180000);
let recovered: number | undefined;
let controls: { hostile_session: string; performance_session: string };
test.beforeAll(() => {
  recovered = recoverHarnessWorker('p6');
  const python = path.resolve('.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  const result = spawnSync(python, ['scripts/p6_browser_fixture.py', '--directory', path.join(artifacts, 'data')], { encoding: 'utf8', windowsHide: true });
  expect(result.status, result.stderr).toBe(0);
  controls = JSON.parse(result.stdout);
  fs.writeFileSync(path.join(artifacts, 'p6-controls.json'), result.stdout);
});
test.afterAll(() => stopHarnessWorker(recovered));

for (const width of [1440, 1280, 390]) {
  test(`session selection and safe input at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    const fatal: string[] = []; page.on('pageerror', e => fatal.push(e.message));
    await page.goto(`/sessions/${controls.hostile_session}`);
    await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
    const source = await (await page.request.get(`/api/sessions/${controls.hostile_session}`)).json();
    const first = source.inputs[0];
    if (width === 390) {
      if (!await page.getByRole('table', { name: 'Observable provenance nodes' }).isVisible()) await page.getByText(/Accessible provenance table ·/).click();
      await page.getByRole('button', { name: `Select ${first.target}`, exact: true }).click();
    } else await page.locator(`[data-node-id="${first.id}"]`).click();
    await expect(page.locator('.explorer-grid')).toHaveAttribute('data-selected-node', first.id);
    await expect(page.locator('.explorer-grid')).toHaveAttribute('data-selected-event', first.model_event_id);
    if (width < 1360) await page.getByRole('button', { name: 'Inspect selection' }).click();
    await expect(page.getByTestId('input-text').filter({ visible: true })).toContainText('<img src=x');
    expect(await page.evaluate(() => (globalThis as { rewindHostileExecuted?: boolean }).rewindHostileExecuted)).toBeUndefined();
    expect(await page.locator('.hostile-input img').count()).toBe(0);
    if (width < 1360) { await page.keyboard.press('Escape'); await expect(page.getByRole('button', { name: 'Inspect selection' })).toBeFocused(); }
    const modelEvent = source.events.find((e: { id: string }) => e.id === first.model_event_id);
    await page.getByRole('button', { name: `Inspect event ${modelEvent.seq} model request` }).click();
    await expect(page.locator('.explorer-grid')).toHaveAttribute('data-selected-node', first.model_event_id);
    await page.reload();
    await expect(page.locator('.explorer-grid')).toHaveAttribute('data-selected-node', first.model_event_id);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(artifacts, `p6-session-${width}.png`), fullPage: true });
    await page.locator('.provenance-panel').screenshot({ path: path.join(artifacts, `p6-graph-${width}.png`) });
    expect(fatal).toEqual([]);
  });
}

test('keyboard, focus, reduced motion, contrast and unavailable routes', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/overview');
  await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
  await page.getByRole('button', { name: 'Refresh status' }).focus();
  await page.keyboard.press('Control+k');
  await expect(page.getByRole('dialog', { name: 'Jump to workspace' })).toBeVisible();
  await expect(page.getByLabel('Find a workspace')).toBeFocused();
  await page.getByLabel('Find a workspace').fill('session');
  await page.keyboard.press('Tab'); await page.keyboard.press('Tab'); await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/sessions$/);
  await expect(page.locator('main')).toBeFocused();
  await page.goto('/overview');
  const measured = await page.evaluate(() => {
    function luminance(color: string) {
      return (color.match(/[\d.]+/g)!.slice(0, 3).map(v => Number(v) / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)).reduce((a, b, i) => a + b * [.2126, .7152, .0722][i], 0);
    }
    const button = document.querySelector<HTMLElement>('button.primary')!;
    const style = getComputedStyle(button);
    const values = [luminance(style.color), luminance(style.backgroundColor)];
    return { primaryContrast: (Math.max(...values) + .05) / (Math.min(...values) + .05), transition: style.transitionDuration, font: getComputedStyle(document.body).fontFamily };
  });
  expect(measured.primaryContrast).toBeGreaterThanOrEqual(4.5); expect(measured.transition).toBe('0s'); expect(measured.font).toContain('Source Sans 3');
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Sentinel', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Protected execution' })).toBeVisible();
  for (const name of ['Preflight']) {
    await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: new RegExp(name) }).click();
    await expect(page.getByRole('heading', { name: `${name} is unavailable` })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Unavailable', exact: true })).toBeDisabled();
  }
  fs.writeFileSync(path.join(artifacts, 'p6-accessibility.json'), JSON.stringify(measured, null, 2));
});

test('persisted event duplicates and reconnect recover actual counts', async ({ page, context }) => {
  await page.addInitScript(() => {
    const Original = window.EventSource;
    (globalThis as { rewindDuplicateEvents?: number }).rewindDuplicateEvents = 0;
    class Replayed extends Original {
      constructor(url: string | URL, options?: EventSourceInit) {
        super(url, options);
        this.addEventListener('message', event => {
          const scope = globalThis as { rewindDuplicateEvents: number };
          if (scope.rewindDuplicateEvents < 3) {
            scope.rewindDuplicateEvents++;
            // Transport-only control: replay the exact received persisted event, never invent an outcome.
            this.dispatchEvent(new MessageEvent('message', { data: event.data, lastEventId: event.lastEventId }));
          }
        });
      }
    }
    window.EventSource = Replayed;
  });
  await captureSession(page); await page.getByLabel('Stochastic simulator confirmation').check();
  const id = await startJob(page);
  await expect.poll(() => page.evaluate(() => (globalThis as { rewindDuplicateEvents?: number }).rewindDuplicateEvents ?? 0)).toBe(3);
  await context.setOffline(true);
  await expect(page.getByText('Offline · data may be stale')).toBeVisible();
  await context.setOffline(false);
  await expect(page.getByRole('button', { name: 'Cancel investigation' })).toBeEnabled();
  await page.getByRole('button', { name: 'Cancel investigation' }).click();
  await expect(page.getByRole('heading', { name: 'Investigation status: cancelled' })).toBeVisible();
  const snapshot = await (await page.request.get(`/api/investigations/${id}`)).json();
  const numbers = await page.locator('.progress-stats strong').allTextContents();
  expect(Number(numbers[0])).toBe(snapshot.completed_trials); expect(Number(numbers[1])).toBe(snapshot.started_trials);
  expect(snapshot.findings.every((f: { remedy_eligible: boolean }) => !f.remedy_eligible)).toBeTruthy();
  await page.reload(); await expect(page.getByRole('heading', { name: 'Investigation status: cancelled' })).toBeVisible();
  expect(await page.locator('.job-result').getAttribute('data-job-id')).toBe(id);
  fs.writeFileSync(path.join(artifacts, 'p6-reconnect.json'), JSON.stringify({ job_id: id, snapshot, duplicate_events: 3 }, null, 2));
});

test('100-event local fixture records measured interaction and load time', async ({ page }) => {
  const started = performance.now();
  await page.goto(`/sessions/${controls.performance_session}`);
  await expect(page.getByText('100 stored events', { exact: true })).toBeVisible();
  const usableMs = performance.now() - started;
  const beforeSelect = performance.now();
  await page.getByRole('button', { name: 'Go to event 100' }).click();
  await expect(page.locator('.explorer-grid')).toHaveAttribute('data-selected-event', /.+/);
  const interactionMs = performance.now() - beforeSelect;
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeDisabled();
  await page.getByRole('button', { name: 'Inspect selection' }).click();
  await expect(page.getByRole('dialog', { name: 'Selected evidence details' })).toContainText('18446744073709551615');
  await page.keyboard.press('Escape');
  fs.writeFileSync(path.join(artifacts, 'p6-performance.json'), JSON.stringify({ usable_ms: usableMs, interaction_ms: interactionMs, events: 100, cpu: os.cpus()[0]?.model, memory_bytes: os.totalmem(), platform: os.platform(), limits: 'Browser automation and local server timing; labelled display fixture, not fresh agent trials.' }, null, 2));
});

test('offline shell uses bundled fonts/assets and never caches API evidence', async ({ page, context }) => {
  const external: string[] = []; page.on('request', request => { if (new URL(request.url()).origin !== 'http://127.0.0.1:5173') external.push(request.url()); });
  await page.goto('/overview'); await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
  await page.evaluate(async () => { await navigator.serviceWorker.ready; if (!navigator.serviceWorker.controller) await new Promise<void>(resolve => navigator.serviceWorker.addEventListener('controllerchange', () => resolve(), { once: true })); });
  await context.setOffline(true); await page.reload();
  await expect(page.getByText('Offline · data may be stale')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Backend unavailable' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toHaveCount(0);
  const resources = await page.evaluate(async () => {
    await Promise.all([document.fonts.load('16px "Source Sans 3"'), document.fonts.load('12px "IBM Plex Mono"')]);
    await document.fonts.ready;
    const keys = await caches.keys();
    return { fonts: document.fonts.check('16px "Source Sans 3"') && document.fonts.check('12px "IBM Plex Mono"'), urls: (await Promise.all(keys.map(async key => (await (await caches.open(key)).keys()).map(r => r.url)))).flat() };
  });
  expect(resources.fonts).toBeTruthy(); expect(resources.urls.some(url => new URL(url).pathname.startsWith('/api/'))).toBeFalsy(); expect(external).toEqual([]);
  await page.screenshot({ path: path.join(artifacts, 'p6-offline.png'), fullPage: true });
  fs.writeFileSync(path.join(artifacts, 'p6-offline.json'), JSON.stringify(resources, null, 2));
  await context.setOffline(false);
});
