"""P0 demo: a real HTTP readiness check, with no simulated agent results."""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    evidence = ROOT / "artifacts/p0"
    evidence.mkdir(parents=True, exist_ok=True)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    # Ignore machine proxy settings for the local development smoke test.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with (evidence / "api-startup.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "rewind_api.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            stdout=log,
            stderr=log,
        )
        try:
            deadline = time.monotonic() + 20
            while True:
                try:
                    with opener.open(f"http://127.0.0.1:{port}/api/health", timeout=2) as response:
                        health = json.load(response)
                    break
                except (urllib.error.URLError, TimeoutError):
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError(
                            "API did not become ready; inspect api-startup.log"
                        ) from None
                    time.sleep(0.1)
            with opener.open(f"http://127.0.0.1:{port}/api/capabilities", timeout=2) as response:
                capabilities = json.load(response)
            if not health["ready"] or health["available_modes"]:
                raise RuntimeError("P0 readiness/capability invariant failed.")
            if any(mode["available"] for mode in capabilities["modes"]):
                raise RuntimeError("P0 must not advertise agent execution.")
            result = {"health": health, "capabilities": capabilities}
            (evidence / "http-smoke.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps(result, indent=2))
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
