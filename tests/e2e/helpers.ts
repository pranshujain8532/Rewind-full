import { expect as baseExpect, type Page } from '@playwright/test';
export const expect = baseExpect.configure({ timeout: 120000 });
export async function captureSession(page: Page, scenario = 'single') {
  await page.goto('/overview');
  await expect(page.getByRole('button', { name: 'Capture demo scenario' })).toBeEnabled();
  await page.getByLabel('Owned scenario').selectOption(scenario);
  const response = page.waitForResponse(r => r.url().endsWith('/api/demo/runs') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Capture demo scenario' }).click();
  const result = await (await response).json();
  await expect(page).toHaveURL(new RegExp(`/sessions/${result.session_id}`));
  await expect(page.getByRole('button', { name: 'Start investigation' })).toBeEnabled();
  return result.session_id as string;
}
export async function startJob(page: Page) {
  const response = page.waitForResponse(r => r.url().endsWith('/api/investigations') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Start investigation' }).click();
  const job = await (await response).json();
  await expect(page.locator('.job-result')).toHaveAttribute('data-job-id', job.id);
  return job.id as string;
}
export async function createRecord(page: Page) {
  await expect(page.getByRole('heading', { name: 'Investigation status: completed' })).toBeVisible();
  const response = page.waitForResponse(r => r.url().endsWith('/api/records') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Create signed record' }).click();
  const record = await (await response).json();
  await expect(page).toHaveURL(new RegExp(`/ledger/${record.id}`));
  await expect(page.getByRole('heading', { name: 'Evidence record', exact: true })).toBeVisible();
  return record;
}
