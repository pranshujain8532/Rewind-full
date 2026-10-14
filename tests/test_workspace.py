"""P6 read-only trace projections and persisted regression-stream recovery."""

import json
from uuid import uuid4

from fastapi.testclient import TestClient
from rewind_api.app import create_app
from rewind_capture.store import CaptureStore
from rewind_eval.store import JobStore
from rewind_ledger.contracts import CaseRequest, RegressionRequest
from rewind_sandbox.fixtures import worlds
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from test_investigation import HEADERS, captured
from test_ledger import ledger as ledger
from test_ledger import ready_record, run


def test_session_selection_projection_redacts_hostile_input_and_never_executes(ledger):
    jobs = JobStore(ledger.directory)
    world = worlds()["single"]
    malicious = '<img src=x onerror="globalThis.attacked=true"> SEND secret=unit-only'
    first = world.subject.inputs[0].model_copy(update={"text": malicious})
    subject = world.subject.model_copy(update={"inputs": [first, *world.subject.inputs[1:]]})
    identity = captured(jobs, world=world.model_copy(update={"subject": subject}))
    with TestClient(create_app(ledger.directory), base_url="http://127.0.0.1") as client:
        assert client.get(f"/api/sessions/{identity}").status_code == 401
        assert client.post("/api/auth/local", headers=HEADERS).status_code == 204
        response = client.get(f"/api/sessions/{identity}")
        assert response.status_code == 200
        result = response.json()
        assert result["integrity"]["status"] == "verified_local_key"
        assert result["replay"]["eligible"]
        view = result["inputs"][0]
        assert view["text"] == malicious  # plain text projection; browser must escape it
        event = next(e for e in result["events"] if e["id"] == view["model_event_id"])
        assert event["kind"] == "model_request"
        assert "[email]" in json.dumps(result)
        assert client.get("/api/sessions/unknown").status_code == 404
    jobs.engine.dispose()


def test_partial_capture_is_inspectable_without_replay_or_positive_integrity(ledger):
    capture = CaptureStore(ledger.directory)
    identity = str(uuid4())
    capture.create_session(identity, {"mode": "simulated"})
    capture.append(identity, "model_request", {"request": {"inputs": []}, "seed": 2**64 - 1})
    with TestClient(create_app(ledger.directory), base_url="http://127.0.0.1") as client:
        client.post("/api/auth/local", headers=HEADERS)
        response = client.get(f"/api/sessions/{identity}")
        assert response.status_code == 200
        result = response.json()
        assert not result["sealed"] and not result["capture_coverage"]["complete"]
        assert result["integrity"]["status"] == "invalid_or_unsealed"
        assert not result["replay"]["eligible"] and result["outcome"] is None
        assert len(result["events"]) == 1
        assert str(2**64 - 1) in result["events"][0]["payload_text"]
    capture.engine.dispose()


def test_explorer_does_not_create_keys_for_missing_payloads(ledger):
    with ledger.engine.begin() as connection:
        connection.execute(text("INSERT INTO sessions VALUES('no-keys','{}',0,NULL)"))
    assert not (ledger.directory / "keys").exists()
    with TestClient(create_app(ledger.directory), base_url="http://127.0.0.1") as client:
        client.post("/api/auth/local", headers=HEADERS)
        assert client.get("/api/sessions/no-keys").status_code == 409
    assert not (ledger.directory / "keys").exists()


def test_regression_events_are_durable_idempotent_immutable_and_resumable(ledger):
    record = ready_record(ledger)
    case = ledger.create_case(record["id"], CaseRequest())
    key = str(uuid4())
    request = RegressionRequest(case_id=case["id"])
    job = ledger.start(request, key)
    assert ledger.start(request, key).id == job.id
    assert len(ledger.events(job.id)) == 1
    cancelled = ledger.cancel(job.id)
    assert cancelled.status == "cancelled" and cancelled.verdict == "inconclusive"
    assert cancelled.cancel_requested
    assert cancelled.elapsed_seconds is None  # queued cancellation did not execute
    events = ledger.events(job.id)
    assert [e["job_seq"] for e in events] == [1, 2]
    assert events[-1]["type"] == "cancelled"
    assert cancelled.last_event_seq == 2
    with TestClient(create_app(ledger.directory), base_url="http://127.0.0.1") as client:
        client.post("/api/auth/local", headers=HEADERS)
        path = f"/api/regression-runs/{job.id}/events"
        response = client.get(path, headers={"Last-Event-ID": f"{job.id}:1"})
        assert response.status_code == 200
        assert f"id: {job.id}:2" in response.text
        assert f"id: {job.id}:1" not in response.text
        assert client.get(path, headers={"Last-Event-ID": "other:1"}).status_code == 400
    try:
        with ledger.engine.begin() as connection:
            connection.execute(
                text("DELETE FROM regression_events WHERE run_id=:id"), {"id": job.id}
            )
    except IntegrityError:
        pass
    else:
        raise AssertionError("Progress events must be immutable")
    assert len(ledger.events(job.id)) == 2


def test_completed_regression_stream_matches_stored_trial_facts(ledger):
    record = ready_record(ledger)
    case = ledger.create_case(record["id"], CaseRequest())
    result = run(ledger, case, "behavioural-v1")
    events = ledger.events(result.id)
    assert [e["job_seq"] for e in events] == list(range(1, len(events) + 1))
    assert [e["type"] for e in events] == [
        "queued",
        "started",
        "trial_started",
        "trial_completed",
        "trial_started",
        "trial_completed",
        "completed",
    ]
    assert result.completed_trials == result.started_trials == 2
    assert result.last_event_seq == len(events)
    assert result.verdict == "pass"
    assert result.record_id == record["id"] and result.kind == "behavioural"
    assert json.loads(result.plan_json) == result.plan
    assert result.elapsed_seconds is not None and result.elapsed_seconds >= 0
    assert ledger.snapshot(result.id).elapsed_seconds == result.elapsed_seconds
    before = len(events)
    try:
        with ledger.transaction() as connection:
            ledger._event(connection, result.id, "unit-only-rollback", {})
            raise RuntimeError("rollback")
    except RuntimeError:
        pass
    assert len(ledger.events(result.id)) == before
