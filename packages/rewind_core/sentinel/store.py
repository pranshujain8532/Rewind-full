"""Persist-before-display policy state; atomic effects are restricted to owned SQLite mocks."""

import hashlib
import json
import os
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rewind_sandbox.fixtures import canonical, digest
from rewind_sandbox.models import Simulator
from rewind_sandbox.schemas import Action, World
from sqlalchemy import text

from rewind_core.storage import make_engine

from .contracts import ActionView, DecisionRequest, Mandate, SentinelSession, SignedMandate
from .policy import evaluate, sign

EVENT_DOMAIN = b"rewind:sentinel-event:v1\0"


class SentinelStore:
    def __init__(self, directory: Path, clock=None):
        self.directory = directory.resolve()
        self.engine = make_engine(self.directory)
        self.clock = clock or (lambda: datetime.now(UTC))

    def keys(self):
        keys = self.directory / "keys"
        public = (keys / "trusted-public.ed25519").read_bytes()
        signer = Ed25519PrivateKey.from_private_bytes((keys / "signing.key").read_bytes())
        if signer.public_key().public_bytes_raw() != public:
            raise ValueError("local_key_mismatch")
        return signer, public, AESGCM((keys / "payload.key").read_bytes())

    def encrypt(self, value, identity):
        nonce = os.urandom(12)
        return nonce + self.keys()[2].encrypt(nonce, canonical(value), identity.encode())

    def decrypt(self, value, identity):
        return json.loads(self.keys()[2].decrypt(value[:12], value[12:], identity.encode()))

    @contextmanager
    def transaction(self):
        with self.engine.connect() as c:
            c.exec_driver_sql("BEGIN IMMEDIATE")
            try:
                yield c
                c.commit()
            except BaseException:
                c.rollback()
                raise

    def event(self, c, session, kind, data):
        prior = c.execute(
            text(
                "SELECT seq,event_hash FROM sentinel_events WHERE session_id=:id "
                "ORDER BY seq DESC LIMIT 1"
            ),
            {"id": session},
        ).first()
        seq = prior.seq + 1 if prior else 1
        if seq > 1024:
            raise ValueError("sentinel_event_bound")
        signer, public, _ = self.keys()
        body = {
            "schema_version": "1.0",
            "id": f"{session}:{seq}",
            "session_id": session,
            "seq": seq,
            "type": kind,
            "time": self.clock().isoformat(),
            "data": data,
            "previous_hash": prior.event_hash if prior else "0" * 64,
            "signing_key_id": hashlib.sha256(public).hexdigest(),
        }
        hashed = hashlib.sha256(EVENT_DOMAIN + canonical(body)).hexdigest()
        signature = signer.sign(EVENT_DOMAIN + bytes.fromhex(hashed)).hex()
        c.execute(
            text("INSERT INTO sentinel_events VALUES(:id,:seq,:body,:hash,:sig)"),
            {
                "id": session,
                "seq": seq,
                "body": canonical(body).decode(),
                "hash": hashed,
                "sig": signature,
            },
        )

    def start(self, source_id, world, trust_external, request, key):
        """Only the owned authenticated adapter creates agent/session bindings and mandates."""
        request_digest = digest(request)
        with self.transaction() as c:
            prior = c.execute(
                text("SELECT id,request_digest FROM sentinel_sessions WHERE idempotency_key=:key"),
                {"key": key},
            ).first()
            if prior:
                if prior.request_digest != request_digest:
                    raise ValueError("idempotency_conflict")
                return prior.id
            session = str(uuid4())
            now = self.clock()
            mandate = Mandate(
                version=str(uuid4()),
                issuer="owned-local-issuer",
                agent_id="owned-demo-agent",
                session_id=session,
                world_digest=digest(world),
                not_before=now,
                not_after=now + timedelta(minutes=10),
                allowed_tools=["ticket.read", "files.read", "mail.send_email"],
                data_ids=list(world.files),
                data_classes=sorted({f["classification"] for f in world.files.values()}),
                recipients=world.subject.allowed_recipients,
                high_impact_tools=["mail.send_email"],
                approvers=["local-user"],
                max_dispatches=32,
                max_export_rows=100,
                approval_seconds=request.hold_seconds,
            )
            signed = sign(mandate, self.keys()[0])
            decision = Simulator(trust_external).decide(world.subject)
            if len(decision.actions) > 32:
                raise ValueError("owned_adapter_action_bound")
            c.execute(
                text("INSERT INTO sentinel_mandates VALUES(:version,:body)"),
                {"version": mandate.version, "body": canonical(signed).decode()},
            )
            c.execute(
                text(
                    "INSERT INTO sentinel_sessions VALUES "
                    "(:id,:source,:agent,:version,:world,:digest,:summary,:key,:request)"
                ),
                {
                    "id": session,
                    "source": source_id,
                    "agent": mandate.agent_id,
                    "version": mandate.version,
                    "world": self.encrypt(world, digest(world)),
                    "digest": digest(world),
                    "summary": canonical(decision.summary).decode(),
                    "key": key,
                    "request": request_digest,
                },
            )
            self.event(
                c,
                session,
                "session_started",
                {
                    "source_session_id": source_id,
                    "agent_id": mandate.agent_id,
                    "mandate_version": mandate.version,
                    "mandate_digest": digest(signed),
                    "mode": "simulated",
                    "world_digest": digest(world),
                },
            )
            self.event(
                c,
                session,
                "model_request",
                {
                    "request_digest": digest(world.subject),
                    "model": "instruction-dsl-v1",
                    "fresh_decision": True,
                    "response_cache": False,
                },
            )
            self.event(c, session, "model_response", decision.model_dump(mode="json"))
            for action in decision.actions:
                self.propose(c, session, mandate.agent_id, action)
            return session

    def context(self, c, session):
        row = c.execute(
            text("SELECT * FROM sentinel_sessions WHERE id=:id"), {"id": session}
        ).first()
        if row is None:
            raise KeyError("unknown_sentinel_session")
        world = World.model_validate(self.decrypt(row.world, row.world_digest))
        raw = c.scalar(
            text("SELECT body FROM sentinel_mandates WHERE version=:v"), {"v": row.mandate_version}
        )
        signed = SignedMandate.model_validate_json(raw)
        counts = c.execute(
            text(
                "SELECT count(*),coalesce(sum(export_rows),0) FROM sentinel_dispatches "
                "WHERE session_id=:id"
            ),
            {"id": session},
        ).one()
        return row, world, signed, counts

    def check(self, c, session, agent, action):
        row, world, signed, counts = self.context(c, session)
        return evaluate(
            signed, self.keys()[1], action, world, agent, session, self.clock(), *counts
        )

    def propose(self, c, session, agent, action):
        if len(canonical(action)) > 4096:
            raise ValueError("action_too_large")
        row, world, signed, _ = self.context(c, session)
        # Adapter principal must also match the registered session, before policy evaluation.
        verdict, enforcement, reason, _ = self.check(c, session, agent, action)
        if row.agent_id != agent:
            verdict, enforcement, reason = "undefined", "deny", "untrusted_agent_identity"
        identity = str(uuid4())
        deadline = min(
            self.clock() + timedelta(seconds=signed.mandate.approval_seconds),
            signed.mandate.not_after,
        )
        state = "denied" if enforcement == "deny" else "held"
        c.execute(
            text(
                "INSERT INTO sentinel_actions "
                "(id,session_id,mandate_version,action,action_digest,args_digest,verdict,"
                "enforcement,state,reason,deadline,agent_can_resume) "
                "VALUES(:id,:session,:version,:action,:digest,:args,:verdict,:enforcement,"
                ":state,:reason,:deadline,1)"
            ),
            {
                "id": identity,
                "session": session,
                "version": row.mandate_version,
                "action": self.encrypt(action, digest(action)),
                "digest": digest(action),
                "args": digest(action.arguments),
                "verdict": verdict,
                "enforcement": enforcement,
                "state": state,
                "reason": reason,
                "deadline": deadline.timestamp(),
            },
        )
        self.event(
            c, session, "policy_decision", self.action_view(c, identity).model_dump(mode="json")
        )
        if enforcement == "allow":
            self.dispatch(c, identity, None)
        return identity

    def action_view(self, c, identity):
        r = c.execute(
            text(
                "SELECT a.*,s.source_session_id,s.agent_id FROM sentinel_actions a "
                "JOIN sentinel_sessions s ON s.id=a.session_id WHERE a.id=:id"
            ),
            {"id": identity},
        ).first()
        if r is None:
            raise KeyError("unknown_action")
        action = Action.model_validate(self.decrypt(r.action, r.action_digest))
        if digest(action) != r.action_digest or digest(action.arguments) != r.args_digest:
            raise ValueError("stored_action_digest_mismatch")
        approval = c.scalar(
            text("SELECT body FROM sentinel_approvals WHERE action_id=:id"), {"id": identity}
        )
        result = c.scalar(
            text("SELECT result FROM sentinel_dispatches WHERE action_id=:id"), {"id": identity}
        )
        resolved = self.decrypt(result, r.id) if result else None
        if not result and r.state in {"denied", "expired", "cancelled"}:
            resolved = {
                "is_error": True,
                "code": "policy_tool_timeout"
                if r.state == "expired"
                else "policy_cancelled"
                if r.state == "cancelled"
                else "policy_denied",
                "reason": r.reason,
                "action_id": r.id,
                "agent_can_resume": bool(r.agent_can_resume),
            }
        return ActionView(
            id=r.id,
            session_id=r.session_id,
            source_session_id=r.source_session_id,
            agent_id=r.agent_id,
            mandate_version=r.mandate_version,
            action_digest=r.action_digest,
            args_digest=r.args_digest,
            tool=action.tool,
            arguments=action.arguments,
            policy_verdict=r.verdict,
            enforcement_decision=r.enforcement,
            state=r.state,
            reason=r.reason,
            deadline=datetime.fromtimestamp(r.deadline, UTC),
            approval=json.loads(approval) if approval else None,
            result=resolved,
            agent_can_resume=bool(r.agent_can_resume),
            investigation_id=r.investigation_id,
            investigation_error=r.investigation_error,
            investigation_requested=bool(r.investigation_requested),
        )

    def transition(self, c, identity, state, reason, resumable=True):
        c.execute(
            text(
                "UPDATE sentinel_actions SET state=:state,enforcement=:enforcement,"
                "reason=:reason,agent_can_resume=:resume "
                "WHERE id=:id"
            ),
            {
                "id": identity,
                "state": state,
                "reason": reason,
                "resume": int(resumable),
                "enforcement": "allow" if state == "dispatched" else "deny",
            },
        )
        action = self.action_view(c, identity)
        self.event(c, action.session_id, state, action.model_dump(mode="json"))

    def expire(self, c, session):
        ids = (
            c.execute(
                text(
                    "SELECT id FROM sentinel_actions WHERE session_id=:id AND state='held' "
                    "AND deadline<=:now"
                ),
                {"id": session, "now": self.clock().timestamp()},
            )
            .scalars()
            .all()
        )
        for identity in ids:
            self.transition(c, identity, "expired", "policy_tool_timeout: deadline elapsed", False)

    def dispatch(self, c, identity, approval):
        a = self.action_view(c, identity)
        if a.state != "held" or self.clock() >= a.deadline:
            raise ValueError("action_not_dispatchable")
        session, world, signed, _ = self.context(c, a.session_id)
        action = Action(tool=a.tool, arguments=a.arguments)
        verdict, enforcement, reason, rows = self.check(c, a.session_id, session.agent_id, action)
        if session.mandate_version != a.mandate_version:
            verdict, enforcement, reason = "undefined", "deny", "stale_mandate_version"
        if enforcement == "deny" or verdict != "in_scope":
            c.execute(
                text("UPDATE sentinel_actions SET verdict=:v,enforcement='deny' WHERE id=:id"),
                {"id": identity, "v": verdict},
            )
            self.transition(c, identity, "denied", reason)
            return
        if enforcement == "hold":
            if approval is None or (
                approval["action_digest"],
                approval["args_digest"],
                approval["session_id"],
                approval["mandate_version"],
            ) != (a.action_digest, a.args_digest, a.session_id, a.mandate_version):
                raise ValueError("approval_binding_mismatch")
            if (
                approval["approver_id"] not in signed.mandate.approvers
                or self.clock().timestamp() >= approval["expires_at"]
            ):
                raise ValueError("approval_not_current_or_authorised")
            # Consumption and local effect share a transaction, unique action IDs prevent reuse.
            c.execute(
                text("INSERT INTO sentinel_approvals VALUES(:id,:body,:now)"),
                {
                    "id": identity,
                    "body": canonical(approval).decode(),
                    "now": self.clock().timestamp(),
                },
            )
            self.event(c, a.session_id, "approval_consumed", approval)
        if action.tool == "mail.send_email":
            result = {
                "accepted": True,
                "sink": "transactional_local_synthetic_outbox",
                "recipient": action.arguments["recipient"],
                "attachment": action.arguments["attachment"],
                "rows": world.files[action.arguments["attachment"]]["rows"],
                "synthetic_rows": rows,
            }
        elif action.tool == "files.read":
            result = world.files[action.arguments["file_id"]]
        else:
            result = {
                "ticket": world.subject.ticket,
                "inputs": [i.model_dump(mode="json") for i in world.subject.inputs],
            }
        c.execute(
            text("INSERT INTO sentinel_dispatches VALUES(:id,:session,:rows,:result)"),
            {
                "id": identity,
                "session": a.session_id,
                "rows": rows,
                "result": self.encrypt(result, identity),
            },
        )
        self.transition(
            c,
            identity,
            "dispatched",
            "approved_exact_action" if approval else "authorised_by_mandate",
        )

    def decide(self, identity, request: DecisionRequest, key, approver):
        request_digest = digest(
            {"request": request.model_dump(mode="json"), "approver": approver, "action": identity}
        )
        # Commit expiration even when the following decision is rejected.
        self.action(identity)
        with self.transaction() as c:
            a = self.action_view(c, identity)
            self.expire(c, a.session_id)
            a = self.action_view(c, identity)
            prior = c.execute(
                text("SELECT * FROM sentinel_receipts WHERE key=:key"), {"key": key}
            ).first()
            if prior:
                if prior.request_digest != request_digest or prior.action_id != identity:
                    raise ValueError("idempotency_conflict")
                return identity
            if (
                request.action_digest,
                request.args_digest,
                request.session_id,
                request.mandate_version,
            ) != (a.action_digest, a.args_digest, a.session_id, a.mandate_version):
                raise ValueError("decision_binding_mismatch")
            _, _, signed, _ = self.context(c, a.session_id)
            if approver not in signed.mandate.approvers:
                raise ValueError("approver_not_authorised")
            if request.decision == "approve":
                if (
                    a.state != "held"
                    or a.enforcement_decision != "hold"
                    or a.policy_verdict != "in_scope"
                ):
                    raise ValueError("hard_deny_or_action_not_eligible")
                now = self.clock().timestamp()
                approval = {
                    "schema_version": "1.0",
                    "action_id": identity,
                    "action_digest": a.action_digest,
                    "args_digest": a.args_digest,
                    "session_id": a.session_id,
                    "mandate_version": a.mandate_version,
                    "approver_id": approver,
                    "decision": "approve",
                    "reason": request.reason,
                    "created_at": now,
                    "expires_at": min(
                        a.deadline.timestamp(), now + signed.mandate.approval_seconds
                    ),
                    "consumed_at": now,
                }
                self.dispatch(c, identity, approval)
            else:
                if a.state != "held" and not (
                    request.decision == "deny_and_investigate" and a.state == "denied"
                ):
                    raise ValueError("terminal_action")
                state = "cancelled" if request.decision == "cancel" else "denied"
                if request.decision == "deny_and_investigate":
                    c.execute(
                        text("UPDATE sentinel_actions SET investigation_requested=1 WHERE id=:id"),
                        {"id": identity},
                    )
                if a.state == "held":
                    self.transition(
                        c, identity, state, "operator_" + request.decision, state != "cancelled"
                    )
                self.event(
                    c,
                    a.session_id,
                    "operator_decision",
                    {
                        "action_id": identity,
                        "decision": request.decision,
                        "approver_id": approver,
                        "reason": request.reason,
                        "action_digest": a.action_digest,
                        "session_id": a.session_id,
                        "mandate_version": a.mandate_version,
                    },
                )
            c.execute(
                text("INSERT INTO sentinel_receipts VALUES(:key,:digest,:id)"),
                {"key": key, "digest": request_digest, "id": identity},
            )
        return identity

    def link_investigation(self, identity, job_id=None, error=None):
        with self.transaction() as c:
            a = self.action_view(c, identity)
            if not a.investigation_requested or a.state != "denied":
                raise ValueError("investigation_not_requested_after_denial")
            if a.investigation_id:
                return
            if a.investigation_error == error and not job_id:
                return
            c.execute(
                text(
                    "UPDATE sentinel_actions SET investigation_id=:job,investigation_error=:error "
                    "WHERE id=:id"
                ),
                {"id": identity, "job": job_id, "error": error},
            )
            self.event(
                c,
                a.session_id,
                "investigation_linked" if job_id else "investigation_unavailable",
                {"action_id": identity, "investigation_id": job_id, "reason": error},
            )

    def action(self, identity):
        with self.transaction() as c:
            a = self.action_view(c, identity)
            self.expire(c, a.session_id)
            return self.action_view(c, identity)

    def snapshot(self, identity):
        with self.transaction() as c:
            self.expire(c, identity)
            row, world, signed, counts = self.context(c, identity)
            ids = (
                c.execute(
                    text("SELECT id FROM sentinel_actions WHERE session_id=:id ORDER BY rowid"),
                    {"id": identity},
                )
                .scalars()
                .all()
            )
            actions = [self.action_view(c, i) for i in ids]
            seq = c.scalar(
                text("SELECT coalesce(max(seq),0) FROM sentinel_events WHERE session_id=:id"),
                {"id": identity},
            )
            status = (
                "awaiting_approval"
                if any(a.state == "held" for a in actions)
                else (
                    "tool_timeout"
                    if any(a.state == "expired" for a in actions)
                    else "cancelled"
                    if any(a.state == "cancelled" for a in actions)
                    else "completed"
                )
            )
            required = Simulator(False).decide(world.subject).actions
            dispatched = {a.action_digest for a in actions if a.state == "dispatched"}
            task = (
                None
                if status == "awaiting_approval"
                else (
                    status == "completed"
                    and json.loads(row.summary) == world.subject.ticket
                    and all(digest(a) in dispatched for a in required)
                )
            )
            return SentinelSession(
                id=identity,
                source_session_id=row.source_session_id,
                agent_id=row.agent_id,
                integrity="local_signed_audit; no external trust anchor",
                mandate=signed,
                actions=actions,
                dispatched=counts[0],
                exported_rows=counts[1],
                last_event_seq=seq,
                status=status,
                task_success=task,
                limitations=[
                    "Owned simulator adapter and transactional SQLite mocks only; "
                    "no external dispatch.",
                    "Source recording is an earlier observation-only run; "
                    "linked Forensics investigates that source.",
                    "Stateless adapter continues with policy results until the deadline; "
                    "timeout/cancel cannot resume this call.",
                    "No anomaly detector, false-positive guarantee, "
                    "generic MCP pause/resume or real-model support.",
                ],
            )

    def sessions(self):
        with self.engine.connect() as c:
            ids = (
                c.execute(text("SELECT id FROM sentinel_sessions ORDER BY rowid DESC LIMIT 30"))
                .scalars()
                .all()
            )
        return [self.snapshot(i) for i in ids]

    def events(self, session, after=0):
        with self.engine.connect() as c:
            return [
                {"body": json.loads(r.body), "event_hash": r.event_hash, "signature": r.signature}
                for r in c.execute(
                    text(
                        "SELECT * FROM sentinel_events WHERE session_id=:id AND seq>:seq "
                        "ORDER BY seq LIMIT 1024"
                    ),
                    {"id": session, "seq": after},
                )
            ]

    def export(self, session):
        # Snapshot, head and events must be from one transaction to avoid a torn signed view.
        self.snapshot(session)
        with self.transaction() as c:
            row, _, mandate, counts = self.context(c, session)
            events = [
                {"body": json.loads(r.body), "event_hash": r.event_hash, "signature": r.signature}
                for r in c.execute(
                    text("SELECT * FROM sentinel_events WHERE session_id=:id ORDER BY seq"),
                    {"id": session},
                )
            ]
            manifest = {
                "schema_version": "1.0",
                "session_id": session,
                "source_session_id": row.source_session_id,
                "mandate": mandate.model_dump(mode="json"),
                "events": events,
                "dispatch_count": counts[0],
                "exported_rows": counts[1],
                "event_count": len(events),
                "head": events[-1]["event_hash"],
            }
            return {
                "manifest": manifest,
                "signature": self.keys()[0]
                .sign(b"rewind:sentinel-manifest:v1\0" + canonical(manifest))
                .hex(),
            }
