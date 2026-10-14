"""P4 risks. Stub execution is unit-only; the benchmark uses actual Docker trials."""

import json
import math
import random
import time
from datetime import UTC, datetime
from pathlib import Path
from statistics import NormalDist
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from rewind_api.app import create_app
from rewind_capture.store import CaptureStore
from rewind_core.contracts import MCP_PROTOCOL_REVISION, RunMode
from rewind_eval.contracts import Budget, InvestigationRequest
from rewind_eval.demo import controlled_world
from rewind_eval.findings import findings
from rewind_eval.provenance import provenance
from rewind_eval.source import read_capture
from rewind_eval.statistics import difference_interval
from rewind_eval.store import JobStore
from rewind_eval.worker import Worker
from rewind_replay.runtime import run_trial
from rewind_sandbox.fixtures import digest, worlds
from rewind_sandbox.models import Simulator
from rewind_sandbox.outcomes import PREDICATE_VERSION
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"Origin": "http://127.0.0.1:5173", "X-REWIND-Local": "1"}


def wilson(x, n, alpha):
    z = NormalDist().inv_cdf(1 - alpha / 2)
    p = x / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return center - half, center + half


@pytest.mark.parametrize(
    "x0,n0,x1,n1",
    [
        (0, 40, 0, 40),
        (40, 40, 40, 40),
        (40, 40, 0, 40),
        (0, 40, 40, 40),
        (3, 20, 18, 40),
        (20, 40, 10, 40),
        (1, 1, 0, 1),
    ],
)
def test_newcombe_against_independently_derived_wilson(x0, n0, x1, n1):
    result = difference_interval(x0, n0, x1, n1, m=3)
    p0, p1 = x0 / n0, x1 / n1
    l0, u0 = wilson(x0, n0, 0.05 / 3)
    l1, u1 = wilson(x1, n1, 0.05 / 3)
    expected = [p0 - p1 - math.hypot(p0 - l0, u1 - p1), p0 - p1 + math.hypot(u0 - p0, p1 - l1)]
    assert result["interval"] == pytest.approx(expected)
    assert result["effect"] == p0 - p1
    assert result["base_flip_rate"] == 1 - p0
    assert result["interval_level"] == pytest.approx(0.9833333333333333)


@pytest.mark.parametrize(
    "args",
    [
        (0, 0, 0, 0),
        (41, 40, 0, 40),
        (-1, 40, 0, 40),
        (math.nan, 40, 0, 40),
        (True, 40, 0, 40),
        (1.0, 40, 0, 40),
    ],
)
def test_impossible_counts_rejected(args):
    with pytest.raises(ValueError):
        difference_interval(*args)


def test_method_assumptions_and_correction():
    with pytest.raises(ValueError):
        difference_interval(10, 40, 0, 40, design="paired")
    with pytest.raises(ValueError):
        difference_interval(10, 40, 0, 40, stochastic=False)
    with pytest.raises(ValueError):
        difference_interval(10, 40, 0, 40, m=0)
    one = difference_interval(30, 40, 8, 40)
    three = difference_interval(30, 40, 8, 40, m=3)
    assert three["interval"][0] < one["interval"][0]
    assert three["interval"][1] > one["interval"][1]


def test_known_null_monte_carlo_with_finite_uncertainty():
    rng = random.Random(20261014)
    rejected = 0
    repetitions = 2000
    for _ in range(repetitions):
        counts = [sum(rng.random() < 0.35 for _ in range(40)) for _ in range(2)]
        lo, hi = difference_interval(counts[0], 40, counts[1], 40)["interval"]
        rejected += lo > 0 or hi < 0
    uncertainty = wilson(rejected, repetitions, 0.05)
    assert 0.01 < rejected / repetitions < 0.10  # Detect gross errors, not demand exactly 5%.
    artifact = ROOT / "artifacts/p4/null" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    artifact.mkdir(parents=True)
    (artifact / "result.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "kind": "statistical_method_monte_carlo",
                "seed": 20261014,
                "n_per_arm": 40,
                "p_null": 0.35,
                "repetitions": repetitions,
                "rejections": rejected,
                "rejection_rate": rejected / repetitions,
                "monte_carlo_95_wilson": uncertainty,
                "limitations": "Finite simulated IID binomial method check; not model evidence.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("REWIND_DATA_DIR", str(tmp_path))
    # Self-contained unit admission stub; actual isolation is separately probed by EXP-003.
    import rewind_replay.container

    runtime = tmp_path / "unit-runtime.json"
    runtime.write_text(
        json.dumps({"image_id": "unit-stub-not-real-isolation", "isolation_verified": True}),
        encoding="utf-8",
    )
    monkeypatch.setattr(rewind_replay.container, "MANIFEST", runtime)
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    value = JobStore(tmp_path)
    yield value
    value.engine.dispose()


def captured(
    store, name="single", world=None, control=True, schema_mutation=None, include_outcome=False
):
    world = world or worlds()[name]
    if control:
        world = controlled_world(world)
    capture = CaptureStore(store.directory)
    session_id = str(uuid4())
    capture.create_session(
        session_id,
        {
            "schema_version": "1.0",
            "mode": "simulated",
            "model": "instruction-dsl-v1",
            "agent_binding": "owned-demo-agent",
            "world_digest": digest(world),
            "config_digest": digest(
                {
                    "simulator": "instruction-dsl-v1",
                    "trust_external": True,
                    "predicate": PREDICATE_VERSION,
                    "protocol": MCP_PROTOCOL_REVISION,
                }
            ),
        },
    )
    capture.append(session_id, "initial_world", world.model_dump(mode="json"))
    capture.append(session_id, "tool_schema", {"unit_test": True})
    tools = {
        kind: {
            "result_type": "complete",
            "meta": {
                "io.modelcontextprotocol/serverInfo": {
                    "name": f"rewind-owned-{kind}",
                    "version": world.version,
                }
            },
            "tools": [
                {
                    "name": tool,
                    "description": "",
                    "input_schema": {
                        "type": "object",
                        "properties": {key: {"type": value} for key, value in properties.items()},
                        "required": required,
                    },
                }
            ],
        }
        for kind, tool, properties, required in [
            (
                "ticket",
                "ticket.read",
                {"ticket_id": "string", "delay_ms": "integer"},
                ["ticket_id"],
            ),
            ("files", "files.read", {"file_id": "string"}, ["file_id"]),
            (
                "mail",
                "mail.send_email",
                {"recipient": "string", "attachment": "string"},
                ["recipient", "attachment"],
            ),
        ]
    }
    if schema_mutation:
        schema_mutation(tools)
    capture.capture_input(session_id, world.subject, tools)
    decision = Simulator().decide(world.subject)
    capture.append(session_id, "model_response", decision.model_dump(mode="json"))
    for action in decision.actions:
        capture.append(session_id, "tool_requested", action.model_dump(mode="json"))
    if include_outcome:
        from rewind_replay.contracts import TrialRequest

        capture.append(session_id, "outcome", run_trial(TrialRequest(world=world)))
    else:
        capture.append(session_id, "outcome", {"unit_test": True})
    capture.seal(
        session_id,
        {
            "model_adapter": True,
            "completed": True,
            "state": "full_initial_world",
            "memory": "stateless_simulator",
            "protocol": MCP_PROTOCOL_REVISION,
        },
    )
    capture.engine.dispose()
    return session_id


def stub(request, **_):
    # Unit tests inject the pure runtime only. This stub is never used by API/CLI/benchmark.
    return {"environment": "isolated_sandbox", "results": [run_trial(t) for t in request.trials]}


@pytest.mark.parametrize("name", ["single", "interaction", "redundant", "harmless", "clean"])
def test_discovery_controls_and_fixture_outcomes(store, name):
    session = captured(store, name)
    job = store.start(InvestigationRequest(session_id=session), str(uuid4()))
    assert job.status == "queued"
    assert Worker(store, runner=stub).run_one()
    result = store.snapshot(job.id)
    assert result.status == "completed"
    assert result.plan["n"] == 1 and result.plan["requested_n"] == 40
    assert all(f.interval is None for f in result.findings)
    rows = store.trials(job.id)
    discovery = {r["arm"]: json.loads(r["result"]) for r in rows if r["phase"] == "discovery"}
    assert (
        discovery["benign_removal_control"]["harmful_action_attempted"]
        == discovery["baseline"]["harmful_action_attempted"]
    )
    assert not discovery["required_fact_control"]["task_success"]
    assert "neutral_replacement_control-0" in discovery
    if name == "redundant":
        assert discovery["single-0"]["harmful_action_attempted"]
        assert discovery["single-1"]["harmful_action_attempted"]
        assert not discovery["pair-0"]["harmful_action_attempted"]
        assert any(len(f.targets) == 2 and f.remedy_eligible for f in result.findings)
    elif name == "interaction":
        assert not discovery["single-0"]["harmful_action_attempted"]
        assert not discovery["single-1"]["harmful_action_attempted"]
        assert any(f.remedy_eligible for f in result.findings)
    elif name == "single":
        assert result.findings[0].remedy_eligible
    else:
        assert result.evidence_status == "no_detected_effect"
        assert all(not f.remedy_eligible for f in result.findings)
    assert result.completed_trials == len(rows)
    assert all(c.tested_subsets for c in result.coverage)


def test_ranking_cannot_read_labels_and_preserves_low_candidates(store):
    world = worlds()["redundant"]
    inputs = [
        world.subject.inputs[0].model_copy(update={"occurrence_id": f"occurrence-{i}"})
        for i in range(10)
    ]
    world = world.model_copy(
        update={"subject": world.subject.model_copy(update={"inputs": inputs})}
    )
    session = captured(store, world=world)
    bundle, _, _ = read_capture(store.directory, session)
    graph = provenance(bundle)
    changed = {**bundle, "evaluation": {"culprit": "occurrence-9", "scenario": "invented"}}
    assert provenance(changed) == graph
    assert len(graph["candidates"]) == 11
    assert sum(c["selected"] for c in graph["candidates"]) == 8
    assert all(c["coverage"] == "not_searched_candidate_limit" for c in graph["candidates"][8:])
    assert len({c["id"] for c in graph["candidates"]}) == 11
    assert len({n["blob_digest"] for n in graph["nodes"] if n["kind"] == "input_occurrence"}) == 2


def test_confirmation_is_fresh_fixed_and_immutable(store):
    job = store.start(InvestigationRequest(session_id=captured(store), stochastic=True), "fixed")
    Worker(store, runner=stub).run_one()
    result = store.snapshot(job.id)
    assert result.status == "completed"
    assert result.findings[0].interval is not None
    assert result.findings[0].baseline.valid == result.findings[0].intervention.valid == 40
    rows = store.trials(job.id)
    discovery_seeds = {json.loads(r["manifest"])["seed"] for r in rows if r["phase"] == "discovery"}
    confirmation = [r for r in rows if r["phase"] == "confirmation"]
    seeds = [json.loads(r["manifest"])["seed"] for r in confirmation]
    assert len(set(seeds)) == len(seeds) and not set(seeds) & discovery_seeds
    events = store.events(job.id)
    freeze_seq = next(e["job_seq"] for e in events if e["type"] == "confirmation_frozen")
    assert all(
        e["job_seq"] > freeze_seq
        for e in events
        if e["type"] == "trial_started" and e["data"]["phase"] == "confirmation"
    )
    assert len(result.plan["schedule"]) == 80
    with pytest.raises(IntegrityError), store.engine.begin() as connection:
        connection.execute(text("UPDATE investigations SET plan='{}' WHERE id=:id"), {"id": job.id})
    with pytest.raises(IntegrityError), store.engine.begin() as connection:
        connection.execute(
            text("UPDATE investigation_trials SET result='{}' WHERE job_id=:id"), {"id": job.id}
        )


def test_invalid_incomplete_duplicate_and_task_destroying_never_positive(store):
    session = captured(store)
    job = store.start(InvestigationRequest(session_id=session, stochastic=True), "invalid")
    calls = 0

    def invalid(request, **kwargs):
        nonlocal calls
        calls += len(request.trials)
        response = stub(request)
        if calls > 5:
            response["results"][0].update(validity="invalid", reason="Synthetic missing response")
        return response

    Worker(store, runner=invalid).run_one()
    result = store.snapshot(job.id)
    assert result.status == "failed" and result.evidence_status == "invalid_experiment"
    assert all(not f.remedy_eligible and f.interval is None for f in result.findings)
    assert any(f.intervention.invalid or f.baseline.invalid for f in result.findings)
    complete_job = store.start(InvestigationRequest(session_id=session), "complete")
    Worker(store, runner=stub).run_one()
    rows = store.trials(complete_job.id)
    plan = store.snapshot(complete_job.id).plan
    partial = findings(plan, rows, "running", RunMode.SIMULATED)
    assert all(not f.complete and not f.remedy_eligible and f.interval is None for f in partial)
    # Task-destroying counts cannot produce a remedy, even with a large harmful-action reduction.
    for row in rows:
        if row["phase"] == "confirmation" and row["arm"] != "baseline":
            data = json.loads(row["result"])
            data["task_success"] = False
            row["result"] = json.dumps(data)
    broken = findings(plan, rows, "completed", RunMode.SIMULATED)
    assert all(not f.remedy_eligible and f.evidence_status == "inconclusive" for f in broken)


def test_budget_idempotency_cancellation_and_interruption(store):
    session = captured(store)
    proposal = InvestigationRequest(session_id=session)
    job = store.start(proposal, "same")
    assert store.start(proposal, "same").id == job.id
    with pytest.raises(ValueError, match="idempotency_conflict"):
        store.start(proposal.model_copy(update={"stochastic": True}), "same")
    with pytest.raises(ValueError, match="Unaffordable"):
        store.start(
            InvestigationRequest(
                session_id=session, stochastic=True, budget=Budget(max_trials=100)
            ),
            "budget",
        )
    cancelled = store.cancel(job.id)
    assert cancelled.status == "cancelled" and cancelled.started_trials == 0
    other = store.start(proposal, "crash")
    assert store.claim("lost-worker") == other.id
    assert store.claim("second-worker") is None
    store.reserve(
        other.id, "lost-worker", "discovery", [{"arm": "baseline", "intervention": {"targets": []}}]
    )
    restarted = JobStore(store.directory)
    restarted.recover(now=time.time() + 60)
    result = restarted.snapshot(other.id)
    assert result.status == "interrupted"
    assert result.started_trials == 1 and result.completed_trials == 0
    assert not restarted.heartbeat(other.id, "lost-worker")
    assert not result.findings
    restarted.engine.dispose()


def test_cancel_during_trial_and_duration_budget(store):
    job = store.start(InvestigationRequest(session_id=captured(store)), "cancel-running")

    def cancel_inflight(request, **kwargs):
        store.cancel(job.id)
        return stub(request)

    Worker(store, runner=cancel_inflight).run_one()
    cancelled = store.snapshot(job.id)
    assert cancelled.status == "cancelled" and cancelled.completed_trials == 1
    job = store.start(
        InvestigationRequest(session_id=job.session_id, budget=Budget(max_seconds=1)), "time"
    )

    def exceeded(request, **kwargs):
        response = stub(request)
        with store.engine.begin() as connection:
            connection.execute(
                text("UPDATE investigations SET started_at=:start WHERE id=:id"),
                {"id": job.id, "start": time.time() - 2},
            )
        return response

    Worker(store, runner=exceeded).run_one()
    result = store.snapshot(job.id)
    assert result.status == "interrupted" and result.completed_trials == 1
    assert "budget" in result.reason.lower()


def test_api_security_unsupported_status_and_sse_resume(store):
    session = captured(store)
    with TestClient(create_app(store.directory), base_url="http://127.0.0.1") as client:
        assert (
            client.post("/api/auth/local", headers={"Origin": "https://evil.example"}).status_code
            == 403
        )
        assert client.get("/api/sessions").status_code == 401
        assert client.post("/api/auth/local", headers=HEADERS).status_code == 204
        assert (
            client.post(
                "/api/investigations",
                json={"session_id": session},
                headers={"Idempotency-Key": "bad"},
            ).status_code
            == 403
        )
        headers = {**HEADERS, "Idempotency-Key": "api"}
        first = client.post(
            "/api/investigations", json={"session_id": session, "mode": "playback"}, headers=headers
        )
        assert first.status_code == 200
        job = first.json()
        assert job["status"] == "failed" and job["evidence_status"] == "unsupported_replay"
        assert (
            client.post(
                "/api/investigations",
                json={"session_id": session, "mode": "playback"},
                headers=headers,
            ).json()["id"]
            == job["id"]
        )
        stream = client.get(f"/api/investigations/{job['id']}/events")
        assert "id: " in stream.text and "unsupported_replay" in stream.text
        resumed = client.get(
            f"/api/investigations/{job['id']}/events", headers={"Last-Event-ID": f"{job['id']}:1"}
        )
        assert "data:" not in resumed.text
        assert (
            client.get(
                f"/api/investigations/{job['id']}/events", headers={"Last-Event-ID": "wrong:1"}
            ).status_code
            == 400
        )
        assert client.get(f"/api/investigations/{job['id']}").json()["completed_trials"] == 0
    legacy = store.start(InvestigationRequest(session_id=captured(store, control=False)), "legacy")
    assert legacy.evidence_status == "unsupported_replay" and "control" in legacy.reason


def test_unknown_tool_schema_and_cached_result_fail_closed(store):
    def changed(schemas):
        schemas["mail"]["tools"][0]["input_schema"]["properties"]["recipient"]["pattern"] = (
            "changed"
        )

    session = captured(store, schema_mutation=changed)
    job = store.start(InvestigationRequest(session_id=session), "changed-schema")
    assert job.evidence_status == "unsupported_replay" and "schemas" in job.reason
    cached = None

    def reuse(request, **kwargs):
        nonlocal cached
        raw = stub(request)
        if cached is None:
            cached = raw["results"][0]
        else:
            raw["results"][0] = cached
        return raw

    job = store.start(InvestigationRequest(session_id=captured(store)), "cached")
    Worker(store, runner=reuse).run_one()
    result = store.snapshot(job.id)
    assert result.status == "failed" and result.evidence_status == "invalid_experiment"
    assert not any(f.remedy_eligible for f in result.findings)


def test_api_no_effect_and_inconclusive_are_stored_trial_projections(store):
    no_effect = store.start(InvestigationRequest(session_id=captured(store, "clean")), "no-effect")
    Worker(store, runner=stub).run_one()
    weak = store.start(
        InvestigationRequest(
            session_id=captured(store), stochastic=True, attempt_probability=0.2, max_finalists=1
        ),
        "weak",
    )
    Worker(store, runner=stub).run_one()
    with TestClient(create_app(store.directory), base_url="http://127.0.0.1") as client:
        client.post("/api/auth/local", headers=HEADERS)
        first = client.get(f"/api/investigations/{no_effect.id}").json()
        assert first["evidence_status"] == "no_detected_effect"
        second = client.get(f"/api/investigations/{weak.id}").json()
        assert second["evidence_status"] == "inconclusive"
        assert second["findings"][0]["baseline"]["harmful"] == sum(
            json.loads(r["result"])["harmful_action_attempted"]
            for r in store.trials(weak.id)
            if r["phase"] == "confirmation" and r["arm"] == "baseline"
        )
