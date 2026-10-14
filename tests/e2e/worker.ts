import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
export function recoverHarnessWorker(phase: string): number | undefined {
  const artifacts = process.env.REWIND_BROWSER_ARTIFACT_DIR!;
  const original = Number(fs.readFileSync(path.join(artifacts, 'worker.pid'), 'utf8'));
  try { process.kill(original, 0); return undefined; }
  catch {
    const python = path.resolve('.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
    const child = spawn(python, ['-m', 'rewind_eval.worker'], { cwd: process.cwd(), stdio: 'ignore', windowsHide: true, env: { ...process.env, REWIND_DATA_DIR: path.join(artifacts, 'data') } });
    fs.writeFileSync(path.join(artifacts, `${phase}-worker.pid`), String(child.pid));
    return child.pid;
  }
}
export function stopHarnessWorker(pid: number | undefined) {
  if (!pid) return;
  if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
  else try { process.kill(pid); } catch { /* already stopped */ }
}
