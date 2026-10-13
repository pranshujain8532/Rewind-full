import { defineConfig } from '@playwright/test';
import path from 'node:path';

const python = path.join('.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'artifacts/p0/playwright.json' }]],
  outputDir: 'artifacts/p0/browser-results',
  use: { baseURL: 'http://127.0.0.1:5173', browserName: 'chromium', trace: 'retain-on-failure' },
  webServer: [
    { command: `"${python}" scripts/e2e_api.py`, url: 'http://127.0.0.1:8000/api/health', reuseExistingServer: false, timeout: 30000 },
    { command: 'npm run dev', url: 'http://127.0.0.1:5173', reuseExistingServer: false, timeout: 30000 },
  ],
});
