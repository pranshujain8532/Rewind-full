"""P8 mechanism controls are unit-only; the isolated test and benchmark use real Docker."""

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from rewind_api.app import create_app
from rewind_core.preflight.contracts import (
    FIXTURE_IDS,
    SUITE,
    PreflightBatch,
    PreflightBudget,
    PreflightRequest,
)
from rewind_core.preflight.fixtures import expected_reads, fixture, spec, validate_spec
from rewind_core.preflight.runtime import run
from rewind_core.preflight.store import PreflightStore
from rewind_core.preflight.worker import PreflightWorker
from rewind_eval.source import read_capture
from rewind_eval.store import JobStore
from rewind_ledger.store import LedgerStore
from rewind_replay.container import execute
from rewind_sandbox.fixtures import digest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from test_investigation import HEADERS
from test_p0 import migrated_directory as migrated_directory


def unit_runner(batch, **_):
    """Unit-only transport stub, never imported by API/CLI/benchmark."""
    return {
        "environment": "isolated_sandbox",
        "preflight_runtime_version": SUITE,
        "results": [run(t) for t in batch.trials],
    }


@pytest.fixture
def suite(migrated_directory, monkeypatch):
    manifest = migrated_directory / "unit-only-runtime.json"
    manifest.write_text(
        json.dumps(
            {
                "isolation_verified": True,
                "preflight_runtime_version": SUITE,
                "image_id": "unit-only",
                "probe": {"unit_only": True},
            }
        )
    )
    monkeypatch.setattr("rewind_core.preflight.store.MANIFEST", manifest)
    monkeypatch.setattr("rewind_core.preflight.worker.MANIFEST", manifest)
    store = PreflightStore(migrated_directory)
    yield store
    store.engine.dispose()


@pytest.mark.parametrize(
    "changes",
    [
        {"target_id": "https://outside.example"},
        {"target_url": "http://127.0.0.1:1"},
        {"suite_version": "future"},
        {"configurations": ["unknown"]},
        {"repeats": 4},
        {"budget": {"max_provider_cost_usd": 1}},
        {"mode": "remote_model"},
    ],
)
def test_arbitrary_targets_paid_generation_and_unknown_versions_rejected(changes):
    with pytest.raises(ValidationError):
        PreflightRequest(**changes)


def test_frozen_fixture_digest_and_target_validation():
    item = spec(FIXTURE_IDS[0], "vulnerable-v1", 3)
    validate_spec(item)
    with pytest.raises(ValueError, match="mismatch"):
        validate_spec(item.model_copy(update={"fixture_digest": "a" * 64}))
    with pytest.raises(ValueError, match="unsupported_owned_fixture"):
        fixture("https://outside.example")


def test_counts_separate_attempts_policy_dispatch_task_and_invalid_coverage(suite):
    snapshot = suite.start(PreflightRequest(), str(uuid4()))
    assert PreflightWorker(suite, unit_runner).run_one()
    result = suite.snapshot(snapshot.id)
    assert result.status == "completed" and result.evidence_status == "invalid_experiment"
    assert result.started_trials == result.returned_trials == 16
    for counts in result.surface_counts:
        assert (
            counts.planned,
            counts.started,
            counts.valid,
            counts.invalid,
            counts.incomplete,
        ) == (4, 4, 3, 1, 0)
        assert counts.harmful_attempts == 1 and counts.task_successes == 3
        assert counts.harmful_policy_blocks == int(counts.configuration == "containment-v1")
        assert counts.harmful_dispatches == int(counts.configuration == "vulnerable-v1")
        assert counts.guardrail_detection == "not_measured"
    for trial in suite.trials(snapshot.id):
        assert trial["result"]["usage"]["provider_cost_usd"] == 0
        if trial["result"]["validity"] == "valid":
            _, world, _ = read_capture(suite.directory, trial["session_id"])
            assert digest(world) == trial["spec"]["fixture_digest"]


def test_second_surface_is_actual_file_read_and_not_in_ticket_response():
    item = spec("mock_file_text/export_directive", "containment-v1", 2)
    result = run(item)
    assert result["owned_reads"] == expected_reads(fixture(item.fixture_id), item.surface)
    ticket, file = result["owned_reads"]
    assert "SEND recipient=audit" not in json.dumps(ticket["response"])
    assert "SEND recipient=audit" in file["response"]["text"]
    assert result["harmful_action_attempted"] and result["harmful_policy_block"]


@pytest.mark.parametrize("surface", ["ticket_comments", "mock_file_text"])
@pytest.mark.parametrize(
    "configuration,attempt,task",
    [
        ("behavioural-v1", False, True),
        ("deny-all-v1", True, False),
    ],
)
def test_behavioural_and_blanket_denial_controls_preserve_distinctions(
    surface, configuration, attempt, task
):
    result = run(spec(surface + "/export_directive", configuration, 1))
    assert result["harmful_action_attempted"] is attempt
    assert result["harmful_action_executed"] is False
    assert result["legitimate_task_success"] is task


def test_interrupted_capture_keeps_atomic_session_header_and_incomplete_trial(suite, monkeypatch):
    job = suite.start(PreflightRequest(), str(uuid4()))

    def interrupted(*_, **__):
        raise RuntimeError("unit-only interrupted capture before first event")

    monkeypatch.setattr("rewind_capture.store.CaptureStore.append", interrupted)
    PreflightWorker(suite, unit_runner).run_one()
    trial = suite.trials(job.id)[0]
    assert trial["result"] is None and suite.snapshot(job.id).status == "failed"
    with TestClient(create_app(suite.directory), base_url="http://127.0.0.1") as client:
        client.post("/api/auth/local", headers=HEADERS)
        partial = client.get(f"/api/sessions/{trial['session_id']}")
        assert partial.status_code == 200 and not partial.json()["sealed"]


def test_parent_recomputes_valid_measures_from_actions(suite):
    job = suite.start(PreflightRequest(budget=PreflightBudget(max_trials=1)), str(uuid4()))

    def altered(batch, **kwargs):
        raw = unit_runner(batch, **kwargs)
        raw["results"][0].update(harmful_policy_block=True, legitimate_task_success=False)
        return raw

    PreflightWorker(suite, altered).run_one()
    result = suite.trials(job.id)[0]["result"]
    assert result["validity"] == "valid"
    assert result["harmful_policy_block"] is False and result["legitimate_task_success"] is True


@pytest.mark.parametrize(
    "budget", [PreflightBudget(max_trials=2), PreflightBudget(max_model_turns=2)]
)
def test_iteration_and_model_turn_limits_retain_unstarted_coverage(suite, budget):
    started = suite.start(PreflightRequest(budget=budget), str(uuid4()))
    PreflightWorker(suite, unit_runner).run_one()
    result = suite.snapshot(started.id)
    assert result.status == "interrupted" and result.started_trials == 2
    assert sum(c.not_started for c in result.surface_counts) == 14


def test_timeout_remains_incomplete_not_harmless(suite):
    started = suite.start(PreflightRequest(), str(uuid4()))

    def timeout(*_, **__):
        raise subprocess.TimeoutExpired("unit-only transport timeout", 1)

    PreflightWorker(suite, timeout).run_one()
    result = suite.snapshot(started.id)
    assert (
        result.status == "interrupted"
        and result.started_trials == 1
        and result.returned_trials == 0
    )
    assert sum(c.incomplete for c in result.surface_counts) == 1
    assert sum(c.valid for c in result.surface_counts) == 0


def test_cancel_race_keeps_actual_inflight_result_and_stops_next_trial(suite):
    started = suite.start(PreflightRequest(), str(uuid4()))

    def cancelled(batch, **kwargs):
        suite.cancel(started.id)
        return unit_runner(batch, **kwargs)

    PreflightWorker(suite, cancelled).run_one()
    result = suite.snapshot(started.id)
    assert result.status == "cancelled" and result.started_trials == result.returned_trials == 1
    queued = suite.start(PreflightRequest(), str(uuid4()))
    assert suite.cancel(queued.id).started_trials == 0
    assert suite.snapshot(queued.id).cancel_requested
    before = len(suite.events(queued.id))
    suite.cancel(queued.id)
    assert len(suite.events(queued.id)) == before


def test_parent_recomputes_measures_and_refuses_swapped_identity(suite):
    started = suite.start(PreflightRequest(budget=PreflightBudget(max_trials=1)), str(uuid4()))

    def swapped(batch, **kwargs):
        raw = unit_runner(batch, **kwargs)
        raw["results"][0].update(
            configuration_digest="a" * 64, harmful_policy_block=True, legitimate_task_success=True
        )
        return raw

    PreflightWorker(suite, swapped).run_one()
    trial = suite.trials(started.id)[0]
    assert trial["result"]["validity"] == "invalid"
    assert trial["result"]["legitimate_task_success"] is None
    assert suite.snapshot(started.id).surface_counts[0].invalid == 1


def test_idempotency_races_lease_loss_and_immutable_plan_results(suite):
    request, key = PreflightRequest(), str(uuid4())
    with ThreadPoolExecutor(max_workers=3) as pool:
        ids = list(pool.map(lambda _: suite.start(request, key).id, range(3)))
    assert len(set(ids)) == 1
    with pytest.raises(ValueError, match="idempotency_conflict"):
        suite.start(request.model_copy(update={"repeats": 2}), key)
    worker = "unit-worker"
    assert suite.claim(worker) == ids[0]
    with suite.transaction() as c:
        c.execute(text("UPDATE preflight_runs SET lease_until=0 WHERE id=:id"), {"id": ids[0]})
    suite.recover()
    assert suite.snapshot(ids[0]).status == "interrupted"
    with pytest.raises(IntegrityError), suite.transaction() as c:
        c.execute(text("UPDATE preflight_runs SET plan='{}' WHERE id=:id"), {"id": ids[0]})
    with pytest.raises(IntegrityError), suite.transaction() as c:
        c.execute(text("DELETE FROM preflight_events"))


def test_shared_workers_cannot_claim_while_preflight_running(suite):
    job = suite.start(PreflightRequest(), str(uuid4()))
    assert suite.claim("unit-worker") == job.id
    jobs, ledger = JobStore(suite.directory), LedgerStore(suite.directory)
    try:
        assert jobs.claim("other") is None and ledger.claim("other") is None
    finally:
        jobs.engine.dispose()
        ledger.engine.dispose()


def test_failure_session_investigation_auth_and_persisted_event_cursor(suite):
    job = suite.start(PreflightRequest(configurations=["vulnerable-v1"]), str(uuid4()))
    PreflightWorker(suite, unit_runner).run_one()
    failure = next(t for t in suite.trials(job.id) if t["result"].get("harmful_action_executed"))
    with TestClient(create_app(suite.directory), base_url="http://127.0.0.1") as client:
        assert client.get("/api/preflight-runs").status_code == 401
        client.post("/api/auth/local", headers=HEADERS)
        bad = client.post(
            "/api/preflight-runs",
            json={"target_id": "https://outside.example"},
            headers=HEADERS | {"Idempotency-Key": str(uuid4())},
        )
        assert bad.status_code == 422
        path = f"/api/preflight-runs/{job.id}/trials/{failure['ordinal']}/investigate"
        first = client.post(path, json={}, headers=HEADERS).json()
        second = client.post(path, json={}, headers=HEADERS).json()
        assert first["session_id"] == failure["session_id"]
        assert first["investigation_id"] == second["investigation_id"]
        assert client.get(f"/api/sessions/{first['session_id']}").status_code == 200
        assert client.get(f"/api/investigations/{first['investigation_id']}").status_code == 200
        event_path = f"/api/preflight-runs/{job.id}/events"
        stream = client.get(event_path, headers={"Last-Event-ID": f"{job.id}:1"})
        assert f"id: {job.id}:1\n" not in stream.text and f"id: {job.id}:2" in stream.text
        assert client.get(event_path, headers={"Last-Event-ID": "other:1"}).status_code == 400


def test_actual_isolated_two_surface_trials_repeat_without_provider():
    items = [spec(identity, "containment-v1", 7) for identity in FIXTURE_IDS]
    first = execute(PreflightBatch(trials=items), timeout=30)
    second = execute(PreflightBatch(trials=items), timeout=30)
    assert (
        first["environment"] == "isolated_sandbox" and first["preflight_runtime_version"] == SUITE
    )
    for item, left, right in zip(items, first["results"], second["results"], strict=True):
        assert left["trial_id"] != right["trial_id"]
        for key in (
            "validity",
            "request_digest",
            "response_digest",
            "attempts",
            "dispatches",
            "legitimate_task_success",
        ):
            assert left.get(key) == right.get(key)
        assert left["owned_reads"] == expected_reads(fixture(item.fixture_id), item.surface)
