"""Non-root no-network sandbox launcher; image identity is pinned after setup."""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rewind_sandbox.fixtures import canonical

from rewind_replay.contracts import BatchRequest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/replay-runtime.json"


def setup() -> dict:
    subprocess.run(
        ["docker", "build", "-f", "containers/replay.Dockerfile", "-t", "rewind-replay:p3", "."],
        cwd=ROOT,
        check=True,
    )
    identity = subprocess.check_output(
        ["docker", "image", "inspect", "rewind-replay:p3", "--format", "{{.Id}}"], text=True
    ).strip()
    manifest = {
        "schema_version": "1.0",
        "image_id": identity,
        "built_at": datetime.now(UTC).isoformat(),
        "isolation_verified": False,
    }
    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_bytes(canonical(manifest))
    return manifest


def execute(request: BatchRequest, timeout: int = 30, require_verified: bool = True) -> dict:
    if not MANIFEST.exists():
        raise RuntimeError("Replay runtime not set up; run replay CLI setup")
    manifest = json.loads(MANIFEST.read_bytes())
    if require_verified and not manifest.get("isolation_verified"):
        raise RuntimeError("Replay isolation probes not verified")
    name = "rewind-trial-" + str(uuid4())
    command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        name,
        "--network",
        "none",
        "--dns",
        "127.0.0.1",
        "--read-only",
        "--user",
        "10001:10001",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--pids-limit",
        "64",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=32m,uid=10001,gid=10001,mode=0700",
        manifest["image_id"],
    ]
    try:
        process = subprocess.run(
            command, input=canonical(request), capture_output=True, timeout=timeout, check=True
        )
        if len(process.stdout) > 8_000_000:
            raise RuntimeError("Replay output bound exceeded")
        return json.loads(process.stdout)
    finally:
        # Only remove this invocation's explicitly named transient container.
        subprocess.run(
            ["docker", "rm", "-f", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )


def verify_isolation() -> dict:
    result = execute(BatchRequest(operation="probe"), require_verified=False)
    manifest = json.loads(MANIFEST.read_bytes())
    manifest["isolation_verified"] = result["passed"]
    manifest["probe"] = result
    manifest["preflight_runtime_version"] = result.get("preflight_runtime_version")
    MANIFEST.write_bytes(canonical(manifest))
    if not result["passed"]:
        raise RuntimeError("Isolation negative probe failed")
    return result
