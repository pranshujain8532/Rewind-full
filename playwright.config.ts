import { defineConfig } from '@playwright/test';
import path from 'node:path';

const python = path.join('.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR ?? `artifacts/browser/manual-${Date.now()}`;

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: path.join(artifacts, 'playwright.json') }]],
  outputDir: path.join(artifacts, 'results'),
  use: { baseURL: 'http://127.0.0.1:5173', browserName: 'chromium', trace: 'retain-on-failure' },
  webServer: [
    { command: `"${python}" scripts/e2e_api.py`, url: 'http://127.0.0.1:8000/api/health', reuseExistingServer: false, timeout: 30000 },
    { command: 'npm run preview --workspace apps/web', url: 'http://127.0.0.1:5173', reuseExistingServer: false, timeout: 30000 },
  ],
});
