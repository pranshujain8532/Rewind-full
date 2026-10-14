import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR ?? 'artifacts/browser/manual';

for (const viewport of [{ width: 1440, height: 900 }, { width: 1280, height: 720 }, { width: 390, height: 844 }]) {
  test(`honest capabilities and rendered shell at ${viewport.width}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const fatal: string[] = [];
    const external: string[] = [];
    page.on('pageerror', error => fatal.push(error.message));
    page.on('console', message => { if (message.type() === 'error') fatal.push(message.text()); });
    page.on('request', request => { if (!new URL(request.url()).hostname.startsWith('127.0.0.1')) external.push(request.url()); });
    await page.goto('/');
    await expect(page.getByText('Foundation is online')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Your first run starts here.' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
    await expect(page.getByText('Unavailable', { exact: true })).toHaveCount(2);
    await expect(page.getByText('Available', { exact: true })).toHaveCount(2);
    await expect(page.getByText('Evidence: unavailable')).toHaveCount(2);
    await expect(page.getByText('Evidence: exploratory')).toHaveCount(1);
    await page.getByRole('button', { name: 'Refresh status' }).focus();
    await expect(page.getByRole('button', { name: 'Refresh status' })).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page.getByText('Foundation is online')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
    fs.mkdirSync(artifacts, { recursive: true });
    await page.screenshot({ path: path.join(artifacts, `overview-${viewport.width}.png`), fullPage: true });
    expect(fatal).toEqual([]);
    expect(external).toEqual([]);
  });
}

test('unreachable API is visible and refresh recovers', async ({ page }) => {
  await page.route('**/api/**', route => route.abort('connectionrefused'));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Backend unavailable' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toHaveCount(0);
  await page.screenshot({ path: path.join(artifacts, 'backend-unavailable.png'), fullPage: true });
  await page.unroute('**/api/**');
  await page.getByRole('button', { name: 'Refresh status' }).click();
  await expect(page.getByText('Foundation is online')).toBeVisible();
});
