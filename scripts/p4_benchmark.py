"""Actual P4 simulator benchmark with fresh captures, Docker trials and a killed worker."""

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import anyio
from alembic import command
from alembic.config import Config
from rewind_capture.store import CaptureStore
from rewind_eval.contracts import InvestigationRequest
from rewind_eval.demo import controlled_world
from rewind_eval.store import JobStore
from rewind_eval.worker import Worker
from rewind_replay.container import MANIFEST, verify_isolation
from rewind_sandbox.fixtures import canonical, digest, load_world
from rewind_sandbox.runner import run_world

ROOT = Path(__file__).resolve().parents[1]


def save(path: Path, data):
    path.write_bytes(canonical(data) + b"\n")


def main():
    started = time.time()
    output = ROOT / "artifacts/p4/EXP-003" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True)
    directory = output / "data"
    os.environ["REWIND_DATA_DIR"] = str(directory)
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    save(output / "isolation-probe.json", verify_isolation())
    capture, store = CaptureStore(directory), JobStore(directory)
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    revision = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output([*git, "status", "--short"], text=True).strip()
    manifest = {
        "schema_version": "1.0",
        "experiment": "EXP-003",
        "revision": revision,
        "dirty_tree": bool(dirty),
        "source_digests": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("packages", "services", "apps/web/src", "migrations", "scripts")
            for p in (ROOT / folder).rglob("*")
            if p.suffix in {".py", ".tsx", ".ts", ".css"}
        },
        "changes": dirty.splitlines(),
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count(),
        "ram": "not_measured",
        "gpu": "not_used; inventory not_measured",
        "versions": json.loads((ROOT / "versions.json").read_bytes()),
        "runtime": json.loads(MANIFEST.read_bytes()),
        "started_at": datetime.now(UTC).isoformat(),
        "mode": "simulated",
        "model_requested": "instruction-dsl-v1",
        "model_returned": "instruction-dsl-v1",
        "cases": [],
        "cost": {"provider_usd": 0, "compute_cost": None, "source": "no provider inference"},
        "limitations": [
            "Owned synthetic simulator only; no LLM/general causation evidence.",
            "Deterministic cases have N=1 and no CI.",
            "Stochastic distribution is fresh independent Bernoulli action gating.",
            "No held-out model evaluation; bounded subset search, no global minimality.",
        ],
    }
    save(output / "manifest.json", manifest)
    cases = [
        (name, False, 0.8, 3)
        for name in ("single", "interaction", "redundant", "harmless", "clean", "authorised")
    ]
    cases += [
        ("single", True, 0.8, 1),
        ("redundant", True, 0.8, 3),
        ("clean", True, 0.8, 1),
        ("single", True, 0.2, 1),
    ]
    for index, (name, stochastic, probability, max_finalists) in enumerate(cases):
        case_started = time.time()
        world = controlled_world(load_world(ROOT / "fixtures", name))

        async def capture_world(case_world=world):
            return await run_world(case_world, directory / "captures", capture_store=capture)

        result = anyio.run(capture_world)
        save(output / f"capture-{index}.json", capture.export(result.run_id))
        proposal = InvestigationRequest(
            session_id=result.run_id,
            stochastic=stochastic,
            attempt_probability=probability,
            max_finalists=max_finalists,
        )
        job = store.start(proposal, str(uuid4()))
        Worker(store).run_one()
        snapshot = store.snapshot(job.id)
        raw = {
            "schema_version": "1.0",
            "snapshot": snapshot.model_dump(mode="json"),
            "trials": store.trials(job.id),
            "events": store.events(job.id),
            "world_digest": digest(world),
            "elapsed_seconds": time.time() - case_started,
        }
        save(output / f"case-{index}.json", raw)
        entry = {
            "name": name,
            "stochastic": stochastic,
            "probability": probability,
            "proposal": proposal.model_dump(mode="json"),
            "job_id": job.id,
            "world_digest": digest(world),
            "config_digest": result.config_digest,
            "status": snapshot.status,
            "evidence_status": snapshot.evidence_status,
            "raw": f"case-{index}.json",
            "elapsed_seconds": raw["elapsed_seconds"],
        }
        manifest["cases"].append(entry)
        save(output / "manifest.json", manifest)
        print(
            f"Case {index} {name} stochastic={stochastic}: {snapshot.status}, "
            f"{snapshot.evidence_status}, {snapshot.completed_trials} stored outcomes",
            flush=True,
        )
        if snapshot.status != "completed":
            raise RuntimeError(f"Incomplete actual benchmark case; inspect {output}")
    # Kill a real separate worker after it freezes confirmation and persists reservations.
    job = store.start(
        InvestigationRequest(session_id=result.run_id, stochastic=True, max_finalists=1),
        str(uuid4()),
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "rewind_eval.worker", "--once"],
        cwd=ROOT,
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    killed = False
    try:
        deadline = time.time() + 90
        while time.time() < deadline:
            before = store.snapshot(job.id)
            if before.plan and any(
                r["phase"] == "confirmation" and r["result"] is None for r in store.trials(job.id)
            ):
                process.kill()
                process.wait(timeout=5)
                killed = True
                break
            if process.poll() is not None:
                break
            time.sleep(0.05)
        if not killed:
            raise RuntimeError("Worker kill audit missed a pending confirmation reservation")
        print(
            "Real worker killed with pending confirmation; waiting for durable lease expiry.",
            flush=True,
        )
        deadline = time.time() + 25
        while time.time() < deadline:
            store.recover()
            after = store.snapshot(job.id)
            if after.status == "interrupted":
                break
            time.sleep(0.2)
        assert after.status == "interrupted" and after.completed_trials < after.started_trials
        assert all(f.interval is None and not f.remedy_eligible for f in after.findings)
        save(
            output / "worker-interruption.json",
            {
                "before": before.model_dump(mode="json"),
                "after": after.model_dump(mode="json"),
                "trials": store.trials(job.id),
                "events": store.events(job.id),
                "worker_exit_code": process.returncode,
            },
        )
        manifest["worker_interruption"] = "verified_actual_process_kill"
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        capture.engine.dispose()
        store.engine.dispose()
    manifest["ended_at"] = datetime.now(UTC).isoformat()
    manifest["elapsed_seconds"] = time.time() - started
    save(output / "manifest.json", manifest)
    lines = [
        "# EXP-003 — actual simulator investigation",
        "",
        f"Parent revision: `{revision}` (dirty P4 implementation).",
        "",
        "| Case | Distribution | Status | Evidence | Raw results |",
        "|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {c['name']} | "
        f"{'Bernoulli p=' + str(c['probability']) if c['stochastic'] else 'deterministic'} "
        f"| {c['status']} | {c['evidence_status']} | {c['raw']} |"
        for c in manifest["cases"]
    )
    lines += [
        "",
        "Actual worker kill retains incomplete reservations and interrupted status without CIs.",
        "All counts come from the attached stored raw trials. Simulator-only; no paid inference.",
    ]
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"EXP-003 raw artifacts: {output}", flush=True)


if __name__ == "__main__":
    main()
