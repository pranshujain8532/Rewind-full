"""EXP-011: actual isolated fixed suites, repeatability, limits and failure investigation."""

import hashlib
import json
import os
import platform
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from rewind_api.app import create_app
from rewind_capture.store import CaptureStore
from rewind_core.preflight.contracts import PreflightBudget, PreflightRequest
from rewind_core.preflight.store import PreflightStore
from rewind_core.preflight.worker import PreflightWorker
from rewind_eval.store import JobStore
from rewind_eval.worker import Worker
from rewind_replay.container import MANIFEST, verify_isolation
from rewind_sandbox.fixtures import canonical

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"Origin": "http://127.0.0.1:5173", "X-REWIND-Local": "1"}


def main():
    output = ROOT / "artifacts/p8/EXP-011" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True)
    directory = output / "data"
    os.environ["REWIND_DATA_DIR"] = str(directory)
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    git = ["git", "-c", "safe.directory=" + ROOT.as_posix()]
    sources = [
        p
        for folder in ("packages", "services", "apps/web/src", "migrations", "tests")
        for p in (ROOT / folder).rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix in {".py", ".tsx", ".ts", ".css"}
    ]
    manifest = {
        "schema_version": "1.0",
        "experiment": "EXP-011",
        "mode": "simulated",
        "parent_revision": subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip(),
        "dirty": bool(subprocess.check_output(git + ["status", "--porcelain"], text=True)),
        "host": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "processor": platform.processor(),
        },
        "versions": json.loads((ROOT / "versions.json").read_bytes()),
        "runtime": json.loads(MANIFEST.read_bytes()),
        "probe": verify_isolation(),
        "design": "Eight fixed cases x two configurations x two deterministic repeats; "
        "no inference/CI/pooling",
        "limits_cases": ["iteration cap 3", "wall time 1s", "queued cancellation"],
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
        "started_at": datetime.now(UTC).isoformat(),
        "provider_requests": 0,
        "guardrail_detection": "not_measured",
        "generation": "not_implemented",
    }
    (output / "manifest.json").write_bytes(canonical(manifest))
    store, jobs = PreflightStore(directory), JobStore(directory)
    worker = PreflightWorker(store)
    began = time.monotonic()
    outcomes = {}
    try:
        requests = {
            "fixed_repeatability": PreflightRequest(
                repeats=2, budget=PreflightBudget(max_seconds=180)
            ),
            "iteration_limit": PreflightRequest(budget=PreflightBudget(max_trials=3)),
            "time_limit": PreflightRequest(budget=PreflightBudget(max_seconds=1)),
            "queued_cancel": PreflightRequest(),
        }
        for name, request in requests.items():
            job = store.start(request, str(uuid4()))
            if name == "queued_cancel":
                store.cancel(job.id)
            else:
                assert worker.run_one()
            snapshot, trials = store.snapshot(job.id), store.trials(job.id)
            outcomes[name] = snapshot.model_dump(mode="json")
            (output / (name + "-snapshot.json")).write_bytes(canonical(snapshot))
            (output / (name + "-trials.json")).write_bytes(canonical(trials))
            if name == "fixed_repeatability":
                assert (
                    snapshot.status == "completed"
                    and snapshot.started_trials == snapshot.returned_trials == 32
                )
                assert sum(c.valid for c in snapshot.surface_counts) == 24
                assert sum(c.invalid for c in snapshot.surface_counts) == 8
                first, second = trials[:16], trials[16:]
                for left, right in zip(first, second, strict=True):
                    assert left["result"]["trial_id"] != right["result"]["trial_id"]
                    assert left["spec"]["fixture_digest"] == right["spec"]["fixture_digest"]
                    assert (
                        left["spec"]["configuration_digest"]
                        == right["spec"]["configuration_digest"]
                    )
                    for key in (
                        "validity",
                        "request_digest",
                        "response_digest",
                        "attempts",
                        "dispatches",
                    ):
                        assert left["result"].get(key) == right["result"].get(key)
            elif name == "iteration_limit":
                assert snapshot.status == "interrupted" and snapshot.started_trials == 3
            elif name == "time_limit":
                assert snapshot.status == "interrupted" and snapshot.started_trials <= 1
            else:
                assert snapshot.status == "cancelled" and snapshot.started_trials == 0
        full_id = outcomes["fixed_repeatability"]["id"]
        failures = [t for t in store.trials(full_id) if t["result"].get("harmful_action_executed")]
        links = []
        with TestClient(create_app(directory), base_url="http://127.0.0.1") as client:
            client.post("/api/auth/local", headers=HEADERS)
            for surface in ("ticket_comments", "mock_file_text"):
                trial = next(t for t in failures if t["spec"]["surface"] == surface)
                response = client.post(
                    f"/api/preflight-runs/{full_id}/trials/{trial['ordinal']}/investigate",
                    json={},
                    headers=HEADERS,
                )
                assert response.status_code == 200
                linked = response.json()
                assert Worker(jobs).run_one()
                source = jobs.snapshot(linked["investigation_id"])
                assert source.status == "completed" and source.session_id == trial["session_id"]
                links.append(
                    {
                        "surface": surface,
                        "link": linked,
                        "investigation": source.model_dump(mode="json"),
                    }
                )
        (output / "failure-investigations.json").write_bytes(canonical(links))
        capture = CaptureStore(directory)
        try:
            example = failures[0]["session_id"]
            (output / "failure-capture.json").write_bytes(canonical(capture.export(example)))
            (output / "trusted-public.ed25519").write_bytes(capture.public)
        finally:
            capture.engine.dispose()
        manifest.update(
            result="passed",
            completed_at=datetime.now(UTC).isoformat(),
            elapsed_seconds=time.monotonic() - began,
            outcomes=outcomes,
            failure_investigation_trials=sum(
                link["investigation"]["completed_trials"] for link in links
            ),
        )
        (output / "summary.md").write_text(
            "# EXP-011 actual fixed-suite results\n\n"
            "32 started/returned, 24 valid and eight deliberate invalid tool-argument cases. "
            "Both surfaces ran in the isolated environment twice per configuration. "
            "Attempts, policy blocks, harmful mock dispatch and owner task "
            "are separate stored facts. "
            "Iteration/time/cancel bounds preserve partial/unknown coverage. "
            "Two failure sources completed isolated investigations. "
            "Provider requests/cost zero; classifier/evasion and compute cost not measured. "
            "No statistical reliability, generation or arbitrary-target capability is claimed.\n",
            encoding="utf-8",
        )
    except BaseException as error:
        manifest.update(result="failed", error=type(error).__name__)
        raise
    finally:
        (output / "manifest.json").write_bytes(canonical(manifest))
        store.engine.dispose()
        jobs.engine.dispose()
        print(str(output))


if __name__ == "__main__":
    main()
