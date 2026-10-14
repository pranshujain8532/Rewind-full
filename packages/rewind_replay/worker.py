"""Bounded JSON stdin/stdout interface inside the no-network replay container."""

import json
import os
import socket
import sys
from pathlib import Path

from rewind_replay.contracts import BatchRequest
from rewind_replay.runtime import run_trial


def probe() -> dict:
    checks = {
        "non_root": os.geteuid() != 0,
        "no_docker_socket": not Path("/var/run/docker.sock").exists(),
        "no_host_secret": not Path("/host/rewind-host-secret.txt").exists(),
        "no_evaluator_fixture": not Path(
            "/opt/rewind/fixtures/evaluation/expectations.json"
        ).exists(),
    }
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=1).close()
        checks["tcp_blocked"] = False
    except OSError:
        checks["tcp_blocked"] = True
    try:
        socket.getaddrinfo("example.com", 443)
        checks["dns_blocked"] = False
    except OSError:
        checks["dns_blocked"] = True
    try:
        Path("/opt/rewind/write-probe").write_text("probe")
        checks["source_readonly"] = False
    except OSError:
        checks["source_readonly"] = True
    checks["no_host_credentials"] = not any(
        key in os.environ
        for key in (
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "AWS_SECRET_ACCESS_KEY",
            "REWIND_AUTH_TOKEN",
        )
    )
    status = Path("/proc/self/status").read_text()
    checks["dropped_capabilities"] = "CapEff:\t0000000000000000" in status
    checks["no_new_privileges"] = "NoNewPrivs:\t1" in status
    try:
        checks["memory_limited"] = (
            Path("/sys/fs/cgroup/memory.max").read_text().strip() == "536870912"
        )
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        checks["cpu_limited"] = int(quota) <= int(period)
        checks["pids_limited"] = int(Path("/sys/fs/cgroup/pids.max").read_text()) <= 64
    except (OSError, ValueError):
        checks["resource_limits_observed"] = False
    return {
        "schema_version": "1.0",
        "checks": checks,
        "passed": all(checks.values()),
        "preflight_runtime_version": "preflight-fixed-v1",
    }


def main():
    raw = sys.stdin.buffer.readline(8_000_001)
    if len(raw) > 8_000_000:
        raise SystemExit("Replay input bound exceeded")
    decoded = json.loads(raw)
    if decoded.get("operation") == "preflight_trials":
        from rewind_core.preflight.contracts import PreflightBatch
        from rewind_core.preflight.runtime import run

        raw += sys.stdin.buffer.read(8_000_001 - len(raw))
        if len(raw) > 8_000_000:
            raise SystemExit("Preflight input bound exceeded")
        batch = PreflightBatch.model_validate_json(raw)
        print(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "environment": "isolated_sandbox",
                    "preflight_runtime_version": "preflight-fixed-v1",
                    "results": [run(item) for item in batch.trials],
                },
                allow_nan=False,
            )
        )
        return
    if decoded.get("operation") == "gemini_trial":
        from rewind_replay.gemini_runtime import worker_trial

        result = worker_trial(decoded, sys.stdin, sys.stdout)
        print(json.dumps({"type": "trial_result", "result": result}, allow_nan=False), flush=True)
        return
    raw += sys.stdin.buffer.read(8_000_001 - len(raw))
    if len(raw) > 8_000_000:
        raise SystemExit("Replay input bound exceeded")
    request = BatchRequest.model_validate_json(raw)
    result = (
        probe()
        if request.operation == "probe"
        else {
            "schema_version": "1.0",
            "environment": "isolated_sandbox",
            "results": [run_trial(trial) for trial in request.trials],
        }
    )
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
