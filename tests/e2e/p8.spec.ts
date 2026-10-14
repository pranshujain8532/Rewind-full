import { test, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { expect } from './helpers';
import { recoverHarnessWorker, stopHarnessWorker } from './worker';

const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
test.setTimeout(180000);
let worker: number | undefined;
test.beforeAll(() => { worker = recoverHarnessWorker('p8'); });
test.afterAll(() => stopHarnessWorker(worker));

async function start(page: Page) {
  const response = page.waitForResponse(r => r.url().endsWith('/api/preflight-runs') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Run fixed suite' }).click();
  const job = await (await response).json();
  await expect(page.locator('.preflight-status')).toHaveAttribute('data-run-id', job.id);
  return job.id;
}

for (const width of [1440,1280,390]) {
  test(`actual Preflight counts and failure evidence at ${width}`, async ({page}) => {
    await page.setViewportSize({width,height:width===390?844:width===1440?900:720});
    const fatal: string[] = [], external: string[] = [];
    page.on('pageerror',e=>fatal.push(e.message));
    page.on('request',r=>{if(new URL(r.url()).hostname!=='127.0.0.1')external.push(r.url());});
    await page.goto('/preflight');
    await expect(page.getByRole('heading',{name:'Run the reviewed suite'})).toBeVisible();
    const id=await start(page);
    await expect(page.getByRole('heading',{name:'Suite status: completed'})).toBeVisible();
    const snapshot=await(await page.request.get(`/api/preflight-runs/${id}`)).json();
    const trials=await(await page.request.get(`/api/preflight-runs/${id}/trials`)).json();
    expect(snapshot.started_trials).toBe(16);expect(snapshot.returned_trials).toBe(16);
    for(const count of snapshot.surface_counts){expect(count.valid).toBe(3);expect(count.invalid).toBe(1);}
    await expect(page.getByRole('table',{name:/Attempt and dispatch counts/})).toContainText('Not measured');
    await expect(page.locator('.preflight-stats')).toContainText('12/16');
    await page.reload();
    await expect(page.getByRole('heading',{name:'Suite status: completed'})).toBeVisible();
    const failure=trials.find((t: {result: {harmful_action_executed?:boolean};spec:{surface:string}})=>t.result?.harmful_action_executed&&t.spec.surface==='mock_file_text');
    const detail=page.locator(`[data-trial-ordinal="${failure.ordinal}"]`);
    await detail.locator('> summary').click();
    await expect(detail.getByRole('link',{name:`Open recorded session ${failure.ordinal}`})).toHaveAttribute('href',`/sessions/${failure.session_id}`);
    await expect(detail).toContainText('Guardrail detection');
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
    await page.evaluate(()=>scrollTo(0,0));
    await page.screenshot({path:path.join(artifacts,`p8-suite-${width}.png`),fullPage:true});
    await page.screenshot({path:path.join(artifacts,`p8-suite-${width}-viewport.png`)});
    await detail.screenshot({path:path.join(artifacts,`p8-failure-${width}.png`)});
    const response=page.waitForResponse(r=>r.url().endsWith(`/trials/${failure.ordinal}/investigate`));
    await detail.getByRole('button',{name:`Investigate trial ${failure.ordinal}`}).click();
    const link=await(await response).json();
    await expect(page).toHaveURL(new RegExp(`/investigations/${link.investigation_id}`));
    const source=await(await page.request.get(`/api/investigations/${link.investigation_id}`)).json();
    expect(source.session_id).toBe(failure.session_id);
    await page.goto(`/sessions/${failure.session_id}`);
    await expect(page.getByRole('heading',{name:'Session explorer'})).toBeVisible();
    await expect(page.getByRole('button',{name:'Start investigation'})).toBeEnabled();
    fs.writeFileSync(path.join(artifacts,`p8-review-${width}.json`),JSON.stringify({snapshot,trials,link,fatal,external,viewport:{width}},null,2));
    expect(fatal).toEqual([]);expect(external).toEqual([]);
  });
}

test('budget stop cancellation and offline stored results stay truthful',async({page,context})=>{
  await page.goto('/preflight');
  await page.getByLabel('Iteration limit').fill('2');
  const bounded=await start(page);
  await expect(page.getByRole('heading',{name:'Suite status: interrupted'})).toBeVisible();
  let result=await(await page.request.get(`/api/preflight-runs/${bounded}`)).json();
  expect(result.started_trials).toBe(2);
  expect(result.surface_counts.reduce((sum:number,c:{not_started:number})=>sum+c.not_started,0)).toBe(14);
  await context.setOffline(true);
  await expect(page.getByText('Offline · data may be stale')).toBeVisible();
  await context.setOffline(false);await page.reload();
  await expect(page.getByRole('heading',{name:'Suite status: interrupted'})).toBeVisible();
  const cancelled=await start(page);
  await expect(page.getByRole('button',{name:'Cancel suite'})).toBeVisible();
  await page.getByRole('button',{name:'Cancel suite'}).click();
  await expect(page.getByRole('heading',{name:'Suite status: cancelled'})).toBeVisible();
  result=await(await page.request.get(`/api/preflight-runs/${cancelled}`)).json();
  expect(result.started_trials).toBeLessThanOrEqual(1);
  fs.writeFileSync(path.join(artifacts,'p8-budget.json'),JSON.stringify({bounded,cancelled:result},null,2));
});
