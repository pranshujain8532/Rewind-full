"""P7 security mechanisms. Owned/unit-only fixtures make no provider requests."""

import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from rewind_api.app import create_app
from rewind_capture.store import CaptureStore
from rewind_core.sentinel.contracts import DecisionRequest, StartRequest
from rewind_core.sentinel.policy import evaluate, sign
from rewind_core.sentinel.store import SentinelStore
from rewind_core.sentinel.verify import verify
from rewind_eval.store import JobStore
from rewind_sandbox.fixtures import canonical, worlds
from rewind_sandbox.schemas import Action
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from test_investigation import HEADERS, captured
from test_p0 import migrated_directory as migrated_directory


@pytest.fixture
def gate(migrated_directory):
    capture = CaptureStore(migrated_directory)
    capture.engine.dispose()
    store = SentinelStore(migrated_directory)
    store.now = datetime.now(UTC)
    store.clock = lambda: store.now
    yield store
    store.engine.dispose()


def start(gate, scenario="authorised", seconds=60):
    jobs = JobStore(gate.directory)
    world = worlds()[scenario]
    source = captured(jobs, world=world)
    jobs.engine.dispose()
    request = StartRequest(source_session_id=source, hold_seconds=seconds)
    identity = gate.start(source, world, True, request, str(uuid4()))
    return gate.snapshot(identity)


def decision(action, kind="approve", **changes):
    body = {
        "decision": kind,
        "action_digest": action.action_digest,
        "args_digest": action.args_digest,
        "session_id": action.session_id,
        "mandate_version": action.mandate_version,
        "reason": "Unit mechanism check",
    }
    return DecisionRequest(**(body | changes))


def replace_mandate(gate, session, changes=None, forged=False):
    mandate = session.mandate.mandate.model_copy(
        update={"version": str(uuid4()), **(changes or {})}
    )
    signed = sign(mandate, gate.keys()[0])
    if forged:
        signed = signed.model_copy(update={"signature": "0" * 128})
    with gate.transaction() as c:
        c.execute(
            text("INSERT INTO sentinel_mandates VALUES(:v,:b)"),
            {"v": mandate.version, "b": canonical(signed).decode()},
        )
        c.execute(
            text("UPDATE sentinel_sessions SET mandate_version=:v WHERE id=:id"),
            {"v": mandate.version, "id": session.id},
        )
    return signed


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"allowed_tools": []}, "tool_outside_scope"),
        ({"denied_tools": ["mail.send_email"]}, "explicit_tool_denial"),
        ({"data_ids": []}, "data_outside_scope"),
        ({"data_classes": []}, "data_outside_scope"),
        ({"denied_data_ids": ["customers"]}, "explicit_data_denial"),
        ({"recipients": []}, "recipient_outside_scope"),
        ({"denied_recipients": ["owner@customer.example"]}, "explicit_recipient_denial"),
        ({"max_dispatches": 0}, "mandate_budget_exhausted"),
        ({"max_export_rows": 1}, "mandate_budget_exhausted"),
        (
            {
                "not_after": datetime(2000, 1, 2, tzinfo=UTC),
                "not_before": datetime(2000, 1, 1, tzinfo=UTC),
            },
            "mandate_not_current",
        ),
        (
            {
                "not_before": datetime(2100, 1, 1, tzinfo=UTC),
                "not_after": datetime(2100, 1, 2, tzinfo=UTC),
            },
            "mandate_not_current",
        ),
        ({"agent_id": "claimed-other-agent"}, "identity_or_world_binding_mismatch"),
        ({"issuer": "claimed-other-issuer"}, "untrusted_issuer"),
    ],
)
def test_scope_and_validity_fail_closed(gate, change, reason):
    session = start(gate)
    mandate = sign(session.mandate.mandate.model_copy(update=change), gate.keys()[0])
    action = Action(tool=session.actions[0].tool, arguments=session.actions[0].arguments)
    verdict, enforcement, actual, _ = evaluate(
        mandate,
        gate.keys()[1],
        action,
        worlds()["authorised"],
        session.agent_id,
        session.id,
        gate.clock(),
        0,
        0,
    )
    assert enforcement == "deny" and actual == reason
    assert verdict in {"undefined", "out_of_scope"}
    assert session.dispatched == 0


def test_signature_and_unknown_trust_anchor(gate):
    session = start(gate)
    action = Action(tool=session.actions[0].tool, arguments=session.actions[0].arguments)
    forged = session.mandate.model_copy(update={"signature": "0" * 128})
    other = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    for signed, key in ((forged, gate.keys()[1]), (session.mandate, other)):
        assert evaluate(
            signed,
            key,
            action,
            worlds()["authorised"],
            session.agent_id,
            session.id,
            gate.clock(),
            0,
            0,
        )[1:3] == ("deny", "invalid_mandate_signature")


def test_forbidden_export_has_no_approve_path_even_via_api(gate):
    session = start(gate, "single")
    action = session.actions[0]
    assert action.state == "denied" and action.policy_verdict == "out_of_scope"
    assert action.result["code"] == "policy_denied" and action.result["is_error"]
    with pytest.raises(ValueError, match="hard_deny"):
        gate.decide(action.id, decision(action), str(uuid4()), "local-user")
    assert gate.snapshot(session.id).dispatched == 0
    with TestClient(create_app(gate.directory), base_url="http://127.0.0.1") as client:
        client.post("/api/auth/local", headers=HEADERS)
        response = client.post(
            f"/api/approvals/{action.id}/decision",
            json=decision(action).model_dump(mode="json"),
            headers=HEADERS | {"Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 409
        assert client.get(f"/api/sentinel/sessions/{session.id}").json()["dispatched"] == 0


@pytest.mark.parametrize(
    "changes",
    [
        {"args_digest": "a" * 64},
        {"action_digest": "a" * 64},
        {"session_id": "other-session"},
        {"mandate_version": "stale-version"},
    ],
)
def test_exact_approval_bindings(gate, changes):
    session = start(gate)
    action = session.actions[0]
    with pytest.raises(ValueError, match="binding_mismatch"):
        gate.decide(action.id, decision(action, **changes), str(uuid4()), "local-user")
    assert gate.snapshot(session.id).dispatched == 0


def test_authenticated_approver_not_claimed_identity(gate):
    action = start(gate).actions[0]
    with pytest.raises(ValueError, match="approver_not_authorised"):
        gate.decide(action.id, decision(action), str(uuid4()), "invented-approver")


@pytest.mark.parametrize("forged", [False, True])
def test_revalidate_active_mandate_before_dispatch(gate, forged):
    session = start(gate)
    action = session.actions[0]
    replace_mandate(gate, session, forged=forged)
    gate.decide(action.id, decision(action), str(uuid4()), "local-user")
    current = gate.snapshot(session.id)
    assert current.dispatched == 0 and current.actions[0].state == "denied"
    assert current.actions[0].approval is None


def test_expired_approval_never_resumes_and_persists_rejection(gate):
    session = start(gate, seconds=1)
    action = session.actions[0]
    gate.now += timedelta(seconds=1)
    with pytest.raises(ValueError, match="not_eligible"):
        gate.decide(action.id, decision(action), str(uuid4()), "local-user")
    current = gate.snapshot(session.id)
    assert current.status == "tool_timeout" and current.dispatched == 0
    assert current.actions[0].state == "expired" and not current.actions[0].agent_can_resume
    assert current.actions[0].result["code"] == "policy_tool_timeout"
    assert current.actions[0].result["agent_can_resume"] is False
    assert any(e["body"]["type"] == "expired" for e in gate.events(session.id))


def test_duplicate_requests_race_and_one_time_consumption(gate):
    session = start(gate)
    action = session.actions[0]
    key = str(uuid4())

    def approve():
        gate.decide(action.id, decision(action), key, "local-user")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: approve(), range(8)))
    current = gate.snapshot(session.id)
    assert current.dispatched == 1 and current.exported_rows == 2 and current.task_success
    approval = current.actions[0].approval
    assert approval["approver_id"] == "local-user" and approval["consumed_at"] is not None
    with pytest.raises(ValueError, match="not_eligible"):
        gate.decide(action.id, decision(action), str(uuid4()), "local-user")
    with pytest.raises(ValueError, match="idempotency_conflict"):
        gate.decide(action.id, decision(action, "deny"), key, "local-user")
    assert gate.snapshot(session.id).dispatched == 1


def test_approval_vs_cancel_race_has_one_terminal_outcome(gate):
    session = start(gate)
    action = session.actions[0]

    def decide(kind):
        try:
            gate.decide(action.id, decision(action, kind), str(uuid4()), "local-user")
            return "accepted"
        except ValueError:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(decide, ["approve", "cancel"]))
    assert sorted(results) == ["accepted", "rejected"]
    current = gate.snapshot(session.id)
    assert current.dispatched == int(current.actions[0].state == "dispatched")
    if not current.dispatched:
        assert current.status == "cancelled" and not current.actions[0].agent_can_resume
        assert current.actions[0].result["code"] == "policy_cancelled"


def test_read_allows_and_untrusted_adapter_binding_never_dispatches(gate):
    session = start(gate, "clean")
    with gate.transaction() as c:
        gate.propose(
            c,
            session.id,
            session.agent_id,
            Action(tool="ticket.read", arguments={"ticket_id": "TICK-4471"}),
        )
        denied_id = gate.propose(
            c,
            session.id,
            "claimed-agent",
            Action(tool="files.read", arguments={"file_id": "customers"}),
        )
    assert gate.snapshot(session.id).dispatched == 1
    assert gate.action(denied_id).state == "denied"


def test_deny_and_investigate_is_idempotent_authenticated_and_linked(gate):
    session = start(gate, "single")
    action = session.actions[0]
    body = decision(action, "deny_and_investigate").model_dump(mode="json")
    headers = HEADERS | {"Idempotency-Key": str(uuid4())}
    path = f"/api/approvals/{action.id}/decision"
    with TestClient(create_app(gate.directory), base_url="http://127.0.0.1") as client:
        assert client.post(path, json=body, headers=headers).status_code == 401
        client.post("/api/auth/local", headers=HEADERS)
        assert client.post(path, json=body).status_code == 403
        first = client.post(path, json=body, headers=headers)
        assert first.status_code == 200
        repeat = client.post(path, json=body, headers=headers)
        a = first.json()["actions"][0]
        assert a["investigation_id"] == repeat.json()["actions"][0]["investigation_id"]
        assert a["state"] == "denied" and first.json()["dispatched"] == 0
        job = client.get(f"/api/investigations/{a['investigation_id']}").json()
        assert job["session_id"] == session.source_session_id
        # Fixture/runtime absence can explicitly fail admission; it must not release a tool.
        assert job["status"] in {"queued", "failed"}


def test_start_is_idempotent_and_request_conflicts(gate):
    original = start(gate)
    request = StartRequest(source_session_id=original.source_session_id)
    key = str(uuid4())
    one = gate.start(request.source_session_id, worlds()["authorised"], True, request, key)
    assert gate.start(request.source_session_id, worlds()["authorised"], True, request, key) == one
    with pytest.raises(ValueError, match="idempotency_conflict"):
        gate.start(
            request.source_session_id,
            worlds()["authorised"],
            True,
            request.model_copy(update={"hold_seconds": 1}),
            key,
        )


def test_audit_trust_tampering_and_immutable_effects(gate):
    session = start(gate)
    gate.decide(session.actions[0].id, decision(session.actions[0]), str(uuid4()), "local-user")
    bundle = gate.export(session.id)
    assert verify(bundle, gate.keys()[1])["dispatches"] == 1
    for mutate in (
        lambda b: b["manifest"].update(dispatch_count=2),
        lambda b: b["manifest"]["events"].pop(),
        lambda b: b["manifest"]["events"][0]["body"]["data"].update(agent_id="forged"),
    ):
        altered = copy.deepcopy(bundle)
        mutate(altered)
        with pytest.raises(InvalidSignature):
            verify(altered, gate.keys()[1])
    with pytest.raises(InvalidSignature):
        verify(bundle, Ed25519PrivateKey.generate().public_key().public_bytes_raw())
    for table in (
        "sentinel_events",
        "sentinel_dispatches",
        "sentinel_approvals",
        "sentinel_mandates",
    ):
        with pytest.raises(IntegrityError), gate.transaction() as c:
            c.execute(text(f"DELETE FROM {table}"))


def test_budget_is_rechecked_at_consumption_and_expired_stored_grant_rejected(gate):
    session = start(gate)
    action = session.actions[0]
    # Direct unit-only dispatcher probe for stale grants, distinct from fresh operator decisions.
    grant = {
        "action_digest": action.action_digest,
        "args_digest": action.args_digest,
        "session_id": action.session_id,
        "mandate_version": action.mandate_version,
        "approver_id": "local-user",
        "expires_at": gate.clock().timestamp(),
    }
    with pytest.raises(ValueError, match="approval_not_current"), gate.transaction() as c:
        gate.dispatch(c, action.id, grant)
    assert gate.snapshot(session.id).dispatched == 0


def test_competing_holds_recheck_shared_budget_at_dispatch(gate):
    session = start(gate, "clean")
    replace_mandate(gate, session, {"max_export_rows": 3})
    with gate.transaction() as c:
        first = gate.propose(
            c,
            session.id,
            session.agent_id,
            Action(
                tool="mail.send_email",
                arguments={"recipient": "owner@customer.example", "attachment": "customers"},
            ),
        )
        second = gate.propose(
            c,
            session.id,
            session.agent_id,
            Action(
                tool="mail.send_email",
                arguments={"recipient": "OWNER@customer.example", "attachment": "customers"},
            ),
        )
    one, two = gate.action(first), gate.action(second)
    assert one.state == two.state == "held"
    gate.decide(first, decision(one), str(uuid4()), "local-user")
    gate.decide(second, decision(two), str(uuid4()), "local-user")
    result = gate.snapshot(session.id)
    assert result.dispatched == 1 and result.exported_rows == 2
    assert (
        gate.action(second).state == "denied"
        and gate.action(second).reason == "mandate_budget_exhausted"
    )


def test_interrupted_commit_rolls_back_consumption_and_effect(gate, monkeypatch):
    session = start(gate)
    action = session.actions[0]
    key = str(uuid4())
    original = gate.transition

    def interrupted(*args, **kwargs):
        raise RuntimeError("Unit-only fault after mock insert, before commit")

    monkeypatch.setattr(gate, "transition", interrupted)
    with pytest.raises(RuntimeError, match="Unit-only fault"):
        gate.decide(action.id, decision(action), key, "local-user")
    assert gate.snapshot(session.id).dispatched == 0 and gate.action(action.id).approval is None
    monkeypatch.setattr(gate, "transition", original)
    gate.decide(action.id, decision(action), key, "local-user")
    assert gate.snapshot(session.id).dispatched == 1
    restarted = SentinelStore(gate.directory, clock=gate.clock)
    try:
        restarted.decide(action.id, decision(action), key, "local-user")
        assert restarted.snapshot(session.id).dispatched == 1
    finally:
        restarted.engine.dispose()


def test_changed_stored_arguments_and_unsupported_arguments_fail_safely(gate):
    session = start(gate)
    action = session.actions[0]
    with gate.transaction() as c:
        changed = Action(
            tool=action.tool, arguments={**action.arguments, "recipient": "audit@external.example"}
        )
        c.execute(
            text("UPDATE sentinel_actions SET action=:payload WHERE id=:id"),
            {"payload": gate.encrypt(changed, action.action_digest), "id": action.id},
        )
    with pytest.raises(ValueError, match="stored_action_digest_mismatch"):
        gate.decide(action.id, decision(action), str(uuid4()), "local-user")
    with gate.engine.connect() as c:
        assert c.scalar(text("SELECT count(*) FROM sentinel_dispatches")) == 0
    clean = start(gate, "clean")
    with gate.transaction() as c:
        denied = gate.propose(
            c,
            clean.id,
            clean.agent_id,
            Action(
                tool="mail.send_email",
                arguments={
                    "recipient": "owner@customer.example",
                    "attachment": "customers",
                    "cost": 0,
                },
            ),
        )
    assert (
        gate.action(denied).policy_verdict == "undefined" and gate.action(denied).state == "denied"
    )
