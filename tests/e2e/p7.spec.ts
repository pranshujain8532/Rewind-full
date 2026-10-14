import { test, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { expect } from './helpers';
import { recoverHarnessWorker, stopHarnessWorker } from './worker';

const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
test.setTimeout(120000);
let worker: number | undefined;
test.beforeAll(() => { worker = recoverHarnessWorker('p7'); });
test.afterAll(() => stopHarnessWorker(worker));

async function demo(page: Page, kind: 'A' | 'B') {
  const response = page.waitForResponse(r => r.url().endsWith('/api/sentinel/sessions') && r.request().method() === 'POST');
  await page.getByRole('button', { name: kind === 'A' ? 'Demo A · forbidden export' : 'Demo B · approval hold', exact: true }).click();
  const session = await (await response).json();
  await expect(page).toHaveURL(new RegExp(session.id));
  await expect(page.locator(`[data-action-id="${session.actions[0].id}"]`)).toBeVisible();
  return session;
}
async function confirm(page: Page, button: string) {
  await page.getByRole('button', { name: button, exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Confirm policy decision' })).toBeVisible();
  await page.getByLabel('Decision reason').fill('Browser gate: exact owned synthetic action reviewed.');
  const response = page.waitForResponse(r => r.url().includes('/api/approvals/') && r.request().method() === 'POST');
  await page.getByRole('button', { name: button === 'Approve exact action' ? 'Confirm approval' : button === 'Cancel tool call' ? 'Confirm cancellation' : 'Confirm denial', exact: true }).click();
  const result = await (await response).json();
  await expect(page.getByRole('dialog', { name: 'Confirm policy decision' })).not.toBeVisible();
  return result;
}
async function render(page: Page, name: string, width: number) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({ path: path.join(artifacts, `${name}-${width}.png`), fullPage: true });
  await page.screenshot({ path: path.join(artifacts, `${name}-${width}-viewport.png`) });
  await page.locator('.sentinel-action').first().screenshot({ path: path.join(artifacts, `${name}-${width}-action.png`) });
}

for (const width of [1440, 1280, 390]) {
  test(`Sentinel denial approval and source investigation at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : width === 1440 ? 900 : 720 });
    const fatal: string[] = [], external: string[] = [];
    page.on('pageerror', e => fatal.push(e.message));
    page.on('request', r => { if (new URL(r.url()).hostname !== '127.0.0.1') external.push(r.url()); });
    await page.goto('/sentinel');
    await expect(page.getByRole('heading', { name: 'Protected execution' })).toBeVisible();
    const denied = await demo(page, 'A');
    await expect(page.locator('.sentinel-action')).toContainText('recipient outside scope');
    await expect(page.getByRole('button', { name: 'Approve exact action' })).toHaveCount(0);
    await render(page, 'p7-denied', width);
    const investigate = await confirm(page, 'Deny and investigate');
    expect(investigate.dispatched).toBe(0);
    expect(investigate.actions[0].state).toBe('denied');
    await expect(page.getByRole('link', { name: 'Open source investigation' })).toBeVisible();
    await page.reload();
    await expect(page.getByRole('link', { name: 'Open source investigation' })).toHaveAttribute('href', `/investigations/${investigate.actions[0].investigation_id}`);
    const allowed = await demo(page, 'B');
    await expect(page.getByRole('button', { name: 'Approve exact action' })).toBeEnabled();
    await render(page, 'p7-held', width);
    await page.getByRole('button', { name: 'Approve exact action' }).click();
    await expect(page.getByRole('dialog', { name: 'Confirm policy decision' })).toContainText(allowed.actions[0].args_digest);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('button', { name: 'Approve exact action' })).toBeFocused();
    const approved = await confirm(page, 'Approve exact action');
    expect(approved.dispatched).toBe(1); expect(approved.task_success).toBe(true);
    await expect(page.locator('.sentinel-action')).toContainText('consumed once');
    await page.reload();
    await expect(page.locator('.sentinel-action')).toContainText('consumed once');
    await expect(page.getByRole('button', { name: 'Approve exact action' })).toHaveCount(0);
    await render(page, 'p7-dispatched', width);
    const download = await page.request.get(`/api/sentinel/sessions/${approved.id}/download`);
    expect(download.ok()).toBeTruthy();
    fs.writeFileSync(path.join(artifacts, `p7-audit-${width}.json`), await download.body());
    fs.writeFileSync(path.join(artifacts, `p7-review-${width}.json`), JSON.stringify({ denied, investigate, allowed, approved, fatal, external, viewport: { width } }, null, 2));
    expect(fatal).toEqual([]); expect(external).toEqual([]);
  });
}

test('Sentinel timeout cancel deny and offline recovery retain real disposition', async ({ page, context }) => {
  await page.goto('/sentinel');
  await page.getByLabel('Tool-call deadline').selectOption('5');
  const timed = await demo(page, 'B');
  await expect(page.locator('.sentinel-action')).toContainText('This tool call cannot resume');
  const timeout = await (await page.request.get(`/api/sentinel/sessions/${timed.id}`)).json();
  expect(timeout.status).toBe('tool_timeout'); expect(timeout.dispatched).toBe(0);
  expect(timeout.actions[0].result.code).toBe('policy_tool_timeout');
  await expect(page.getByRole('button', { name: 'Approve exact action' })).toHaveCount(0);
  await page.reload();
  await expect(page.locator('.sentinel-action')).toContainText('policy tool timeout');
  await page.getByLabel('Tool-call deadline').selectOption('300');
  const cancelled = await demo(page, 'B');
  const cancel = await confirm(page, 'Cancel tool call');
  expect(cancel.status).toBe('cancelled'); expect(cancel.dispatched).toBe(0);
  expect(cancel.actions[0].result.code).toBe('policy_cancelled');
  const denied = await demo(page, 'B');
  const deny = await confirm(page, 'Deny action');
  expect(deny.actions[0].state).toBe('denied'); expect(deny.task_success).toBe(false);
  expect(deny.actions[0].result.code).toBe('policy_denied');
  await context.setOffline(true);
  await expect(page.getByText('Offline · data may be stale')).toBeVisible();
  await context.setOffline(false); await page.reload();
  await expect(page.locator('.sentinel-action')).toContainText('operator deny');
  expect((await (await page.request.get(`/api/sentinel/sessions/${denied.id}`)).json()).dispatched).toBe(0);
  fs.writeFileSync(path.join(artifacts, 'p7-lifecycle.json'), JSON.stringify({ timed: timeout, cancelled: cancel, denied: deny, ids: [cancelled.id, denied.id] }, null, 2));
});
