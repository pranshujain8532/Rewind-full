// Keep browser downloads inside the workspace on Windows and Linux.
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const mode = process.argv[2];
if (!['install', 'test'].includes(mode)) throw new Error('Use install or test.');
const args = mode === 'install' ? ['install', 'chromium'] : ['test', ...process.argv.slice(3)];
const fs = require('node:fs');
const artifactDir = path.resolve('artifacts/browser', new Date().toISOString().replace(/[:.]/g, '-'));
if (mode === 'test') {
  fs.mkdirSync(artifactDir, { recursive: true });
  fs.writeFileSync(path.resolve('artifacts/browser/latest.txt'), artifactDir);
}
const cli = path.join(path.dirname(require.resolve('playwright/package.json')), 'cli.js');
const result = spawnSync(process.execPath, [cli, ...args], {
  stdio: 'inherit',
  env: { ...process.env, PLAYWRIGHT_BROWSERS_PATH: path.resolve('.tools/playwright'), REWIND_BROWSER_ARTIFACT_DIR: artifactDir },
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
