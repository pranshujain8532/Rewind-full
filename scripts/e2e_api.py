"""Start the migrated API in Playwright's separate development data directory."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = Path(
    os.environ.get("REWIND_BROWSER_ARTIFACT_DIR", str(ROOT / "artifacts/browser/manual"))
)
os.environ["REWIND_DATA_DIR"] = str(artifacts / "data")
subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, check=True)
worker = subprocess.Popen([sys.executable, "-m", "rewind_eval.worker"], cwd=ROOT)
(artifacts / "worker.pid").write_text(str(worker.pid), encoding="utf-8")
try:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "rewind_api.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        check=True,
    )
finally:
    if worker.poll() is None:
        worker.terminate()
        try:
            worker.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker.kill()
            worker.wait(timeout=5)
