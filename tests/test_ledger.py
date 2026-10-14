"""Ledger trust/invalid-evidence gates. Pure-runtime unit replies are not live measurements."""

import copy
import json
import os
import subprocess
import sys
import time
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from rewind_api.app import create_app
from rewind_core.contracts import RunMode
from rewind_eval.contracts import InvestigationRequest
from rewind_eval.store import JobStore
from rewind_eval.worker import Worker
from rewind_ledger.bundle import MAX_BUNDLE_BYTES, bounded_json, sign_bundle, verify_bundle
from rewind_ledger.contracts import CaseRequest, RecordRequest, RegressionRequest
from rewind_ledger.store import LedgerStore
from rewind_ledger.worker import RegressionWorker
from rewind_replay.container import ROOT
from rewind_sandbox.fixtures import canonical, worlds
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from test_investigation import HEADERS, captured, stub


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    import rewind_ledger.worker
    import rewind_replay.container

    monkeypatch.setenv("REWIND_DATA_DIR", str(tmp_path))
    runtime = tmp_path / "unit-runtime.json"
    runtime.write_text(
        json.dumps({"image_id": "unit-only-not-isolation-evidence", "isolation_verified": True})
    )
    monkeypatch.setattr(rewind_replay.container, "MANIFEST", runtime)
    monkeypatch.setattr(rewind_ledger.worker, "MANIFEST", runtime)
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    store = LedgerStore(tmp_path)
    yield store
    store.engine.dispose()


def ready_record(ledger, require_owner_action=False):
    jobs = JobStore(ledger.directory)
    world = worlds()["single"]
    if require_owner_action:
        subject = world.subject.model_copy(
            update={
                "task": world.subject.task
                + f" SEND recipient={world.subject.allowed_recipients[0]} attachment=customers"
            }
        )
        world = world.model_copy(update={"subject": subject})
    sid = captured(jobs, world=world, include_outcome=True)
    job = jobs.start(InvestigationRequest(session_id=sid), str(uuid4()))
    assert Worker(jobs, runner=stub).run_one()
    assert jobs.snapshot(job.id).status == "completed"
    record = ledger.create_record(RecordRequest(investigation_id=job.id), str(uuid4()))
    jobs.engine.dispose()
    return record


def run(ledger, case, version, runner=stub):
    request = RegressionRequest(case_id=case["id"], fixed_configuration=version)
    job = ledger.start(request, str(uuid4()))
    assert RegressionWorker(ledger, runner=runner).run_one()
    return ledger.snapshot(job.id)


def test_authentic_bundle_verifies_in_separate_process_without_database(ledger, tmp_path):
    record = ready_record(ledger)
    bundle = ledger.bundle(record["id"])
    checked = verify_bundle(bundle, ledger.trusted_public())
    assert checked.integrity_valid and checked.regression_eligible
    assert record["governance_mapping"]["status"] == "pending"
    assert record["policy_approval_trail"]["status"] == "not_captured"
    assert record["provenance"]["model_returned"] is None
    assert sum(c["started"] for c in record["counts"].values()) == len(
        bundle["artifacts"]["investigation"]["trials"]
    )
    raw, public = tmp_path / "bundle.json", tmp_path / "public.ed25519"
    raw.write_bytes(canonical(bundle))
    public.write_bytes(ledger.trusted_public())
    nonexistent = tmp_path / "verifier-must-not-create-data"
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "rewind_ledger.cli",
            "verify",
            "--bundle",
            str(raw),
            "--trusted-public-key",
            str(public),
        ],
        cwd=tmp_path,
        env={**os.environ, "REWIND_DATA_DIR": str(nonexistent)},
        capture_output=True,
        timeout=30,
    )
    assert process.returncode == 0, process.stdout.decode()
    assert json.loads(process.stdout)["integrity_valid"] is True
    assert not nonexistent.exists()


@pytest.mark.parametrize("target", ["report", "trace", "trial", "missing", "schema", "signature"])
def test_modified_report_trace_trial_and_unknown_schema_fail(ledger, target):
    record = ready_record(ledger)
    bundle = copy.deepcopy(ledger.bundle(record["id"]))
    if target == "report":
        bundle["report"]["observed_synthetic_impact"]["unit"] = "people exposed"
    elif target == "trace":
        bundle["artifacts"]["trace"]["events"][0]["body"]["kind"] = "altered"
    elif target == "trial":
        bundle["artifacts"]["investigation"]["trials"][0]["result"]["harmful_action_attempted"] = (
            False
        )
    elif target == "missing":
        del bundle["artifacts"]["investigation"]
    elif target == "schema":
        bundle["schema_version"] = "999"
    else:
        bundle["signature"] = "00" * 64
    assert not verify_bundle(bundle, ledger.trusted_public()).integrity_valid


def test_unknown_signer_and_resigned_invented_counts_are_rejected(ledger):
    record = ready_record(ledger)
    bundle = ledger.bundle(record["id"])
    unknown = Ed25519PrivateKey.generate()
    forged = sign_bundle(bundle["format"], bundle["report"], bundle["artifacts"], unknown)
    checked = verify_bundle(forged, ledger.trusted_public())
    assert not checked.integrity_valid and not checked.trusted
    report = copy.deepcopy(bundle["report"])
    report["counts"]["discovery:baseline"]["harmful"] = 0
    resigned = sign_bundle(bundle["format"], report, bundle["artifacts"], ledger.signer())
    assert not verify_bundle(resigned, ledger.trusted_public()).integrity_valid


def test_bounded_corrupt_duplicate_and_nonfinite_inputs():
    for raw in (
        b"x" * (MAX_BUNDLE_BYTES + 1),
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b"[]",
        b"{",
        b'{"x":' + b"[" * 50 + b"0" + b"]" * 50 + b"}",
    ):
        with pytest.raises(ValueError):
            bounded_json(raw)


@pytest.mark.parametrize(
    "kind,version,residual",
    [("behavioural", "behavioural-v1", 0), ("containment", "containment-v1", 1)],
)
def test_original_attack_vulnerable_fails_fixed_passes_and_inputs_unchanged(
    ledger, kind, version, residual
):
    record = ready_record(ledger, require_owner_action=True)
    case = ledger.create_case(record["id"], CaseRequest(kind=kind))
    failed = run(ledger, case, "vulnerable-v1")
    passed = run(ledger, case, version)
    assert failed.verdict == "fail" and passed.verdict == "pass"
    assert passed.manifest["arms"]["vulnerable"]["status"] == "fail"
    assert passed.manifest["arms"]["fixed"]["harmful_attempts"] == residual
    assert passed.manifest["arms"]["fixed"]["harmful_dispatches"] == 0
    assert passed.manifest["arms"]["fixed"]["task_success"]
    assert passed.manifest["interval"] is None
    assert all(
        t["result"]["model_request"] == case["original_world"]["subject"]
        for t in ledger.trials(passed.id)
    )
    assert verify_bundle(ledger.run_bundle(passed.id), ledger.trusted_public()).integrity_valid
    assert ledger.compare(failed.id, passed.id)["left"]["verdict"] == "fail"
    deny_all = run(ledger, case, "deny-all-v1")
    assert deny_all.verdict == "fail"  # Blocking every tool loses the legitimate owner send.


def test_containment_does_not_pass_behavioural_contract_and_invalid_cannot_pass(ledger):
    case = ledger.create_case(ready_record(ledger)["id"], CaseRequest())
    assert run(ledger, case, "containment-v1").verdict == "fail"

    def invalid(request, **kwargs):
        raw = stub(request, **kwargs)
        raw["results"][0]["fresh_decision"] = False
        return raw

    bad = run(ledger, case, "behavioural-v1", runner=invalid)
    assert bad.status == "failed" and bad.verdict == "inconclusive"
    assert not verify_bundle(ledger.run_bundle(bad.id), ledger.trusted_public()).regression_eligible


def test_invalid_source_evidence_refuses_case_creation(ledger):
    jobs = JobStore(ledger.directory)
    sid = captured(jobs, include_outcome=True)
    job = jobs.start(InvestigationRequest(session_id=sid), str(uuid4()))
    jobs.cancel(job.id)
    record = ledger.create_record(RecordRequest(investigation_id=job.id), str(uuid4()))
    checked = verify_bundle(ledger.bundle(record["id"]), ledger.trusted_public())
    assert checked.integrity_valid and not checked.regression_eligible
    with pytest.raises(ValueError):
        ledger.create_case(record["id"], CaseRequest())
    jobs.engine.dispose()


def test_idempotency_immutability_cancellation_interruption_and_unsupported(ledger):
    record = ready_record(ledger)
    case = ledger.create_case(record["id"], CaseRequest())
    request = RegressionRequest(case_id=case["id"])
    job = ledger.start(request, "same-start")
    assert ledger.start(request, "same-start").id == job.id
    with pytest.raises(ValueError):
        ledger.start(request.model_copy(update={"seed": 42}), "same-start")
    assert ledger.cancel(job.id).verdict == "inconclusive"
    job = ledger.start(request, "interrupted")
    worker = "unit-worker"
    assert ledger.claim(worker) == job.id
    ledger.reserve(job.id, worker, 1, job.plan["schedule"][0])
    with ledger.engine.begin() as connection:
        connection.execute(
            text("UPDATE regression_runs SET lease_until=:time WHERE id=:id"),
            {"id": job.id, "time": time.time() - 1},
        )
    ledger.recover()
    interrupted = ledger.snapshot(job.id)
    assert interrupted.status == "interrupted" and interrupted.verdict == "inconclusive"
    assert interrupted.started_trials == 1 and interrupted.completed_trials == 0
    unsupported = ledger.start(
        request.model_copy(update={"mode": RunMode.REMOTE_MODEL}), "unsupported"
    )
    assert unsupported.verdict == "inconclusive" and unsupported.status == "failed"
    with ledger.engine.begin() as connection:
        for statement in (
            "UPDATE evidence_records SET created_at='changed'",
            "DELETE FROM regression_trials",
            "UPDATE regression_runs SET status='completed'",
        ):
            with pytest.raises(IntegrityError):
                connection.execute(text(statement))


def test_authenticated_api_download_verify_and_regression(ledger):
    record = ready_record(ledger)
    with TestClient(create_app(ledger.directory), base_url="http://127.0.0.1") as client:
        assert client.get("/api/records").status_code == 401
        client.post("/api/auth/local", headers=HEADERS, json={})
        download = client.get(f"/api/records/{record['id']}/download")
        assert (
            download.status_code == 200 and "attachment" in download.headers["content-disposition"]
        )
        checked = client.post(
            "/api/records/verify",
            headers=HEADERS,
            json={"bundle": download.json(), "trusted_public_key": ledger.trusted_public().hex()},
        )
        assert checked.json()["integrity_valid"]
        raw_verified = client.post(
            "/api/records/verify",
            headers={**HEADERS, "X-REWIND-Trusted-Public-Key": ledger.trusted_public().hex()},
            content=download.content,
        )
        assert raw_verified.json()["integrity_valid"]
        rounded = json.loads(
            download.content, parse_int=lambda n: int(float(n)) if abs(int(n)) > 2**53 else int(n)
        )
        changed = client.post(
            "/api/records/verify",
            headers={**HEADERS, "X-REWIND-Trusted-Public-Key": ledger.trusted_public().hex()},
            content=canonical(rounded),
        )
        assert not changed.json()["integrity_valid"]
        assert (
            client.post(
                "/api/records/verify", headers=HEADERS, content=b"x" * (MAX_BUNDLE_BYTES + 1)
            ).status_code
            == 413
        )
        assert (
            client.post(
                "/api/records/verify", headers=HEADERS, json={"bundle": download.json()}
            ).status_code
            == 422
        )
        case = client.post(
            f"/api/regressions/from-record/{record['id']}",
            headers={**HEADERS, "Idempotency-Key": "case"},
            json={},
        ).json()
        job = client.post(
            "/api/regression-runs",
            headers={**HEADERS, "Idempotency-Key": "run"},
            json={"case_id": case["id"]},
        ).json()
        assert job["status"] == "queued"
        RegressionWorker(ledger, runner=stub).run_one()
        assert client.get(f"/api/regression-runs/{job['id']}").json()["verdict"] == "pass"
