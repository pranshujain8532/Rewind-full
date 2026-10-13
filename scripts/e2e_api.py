"""Start the migrated API in Playwright's separate development data directory."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["REWIND_DATA_DIR"] = str(ROOT / "artifacts/p0/browser-data")
subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, check=True)
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
