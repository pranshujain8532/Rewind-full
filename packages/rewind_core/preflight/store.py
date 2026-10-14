"""Frozen plans, exclusive leases and code-derived observed numerators/coverage."""

import json
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

from rewind_replay.container import MANIFEST
from rewind_sandbox.fixtures import canonical, digest
from sqlalchemy import text

from rewind_core.storage import make_engine

from .contracts import FIXTURE_IDS, PreflightSnapshot, SurfaceCounts
from .fixtures import spec

TERMINAL = {"completed", "cancelled", "interrupted", "failed"}


class PreflightStore:
    def __init__(self, directory):
        self.directory = directory.resolve()
        self.engine = make_engine(self.directory)

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

    def event(self, c, identity, kind, data):
        seq = c.scalar(
            text("SELECT coalesce(max(seq),0)+1 FROM preflight_events WHERE run_id=:id"),
            {"id": identity},
        )
        body = {
            "schema_version": "1.0",
            "id": f"{identity}:{seq}",
            "job_id": identity,
            "job_seq": seq,
            "type": kind,
            "time": datetime.now(UTC).isoformat(),
            "data": data,
        }
        c.execute(
            text("INSERT INTO preflight_events VALUES(:id,:seq,:body)"),
            {"id": identity, "seq": seq, "body": canonical(body).decode()},
        )

    def start(self, request, key):
        with self.engine.connect() as c:
            prior = c.execute(
                text("SELECT id,request_digest FROM preflight_runs WHERE idempotency_key=:key"),
                {"key": key},
            ).first()
        if prior:
            if prior.request_digest != digest(request):
                raise ValueError("idempotency_conflict")
            return self.snapshot(prior.id)
        if len(set(request.configurations)) != len(request.configurations):
            raise ValueError("duplicate_configuration")
        try:
            runtime = json.loads(MANIFEST.read_bytes())
        except (OSError, ValueError):
            runtime = {}
        if (
            not runtime.get("isolation_verified")
            or runtime.get("preflight_runtime_version") != request.suite_version
        ):
            raise ValueError("preflight_isolated_runtime_unavailable_rebuild_and_probe")
        schedule = [
            spec(fixture, config, request.seed + repeat).model_dump(mode="json")
            for repeat in range(request.repeats)
            for fixture in FIXTURE_IDS
            for config in request.configurations
        ]
        plan = {
            "schema_version": "1.0",
            "request": request.model_dump(mode="json"),
            "mode": "simulated",
            "model": "instruction-dsl-v1",
            "schedule": schedule,
            "runtime_image_id": runtime["image_id"],
            "isolation_probe": runtime["probe"],
            "generator": "fixed_reviewed_suite",
            "evolutionary_generation": "not_implemented",
            "guardrail_detection": "not_measured",
            "invalid_policy": "retain_and_continue_no_retry",
            "container_limits": {"cpu": 1, "memory_mb": 512, "pids": 64, "network": "none"},
        }
        with self.transaction() as c:
            prior = c.execute(
                text("SELECT id,request_digest FROM preflight_runs WHERE idempotency_key=:key"),
                {"key": key},
            ).first()
            if prior:
                if prior.request_digest != digest(request):
                    raise ValueError("idempotency_conflict")
                identity = prior.id
            else:
                if (
                    c.scalar(
                        text(
                            "SELECT count(*) FROM preflight_runs WHERE status IN "
                            "('queued','running')"
                        )
                    )
                    >= 8
                ):
                    raise ValueError("preflight_queue_full")
                identity = str(uuid4())
                c.execute(
                    text(
                        "INSERT INTO preflight_runs "
                        "(id,idempotency_key,request_digest,plan,plan_digest,status,created_at) "
                        "VALUES(:id,:key,:request,:plan,:digest,'queued',:time)"
                    ),
                    {
                        "id": identity,
                        "key": key,
                        "request": digest(request),
                        "plan": canonical(plan).decode(),
                        "digest": digest(plan),
                        "time": datetime.now(UTC).isoformat(),
                    },
                )
                self.event(c, identity, "queued", {"planned_trials": len(schedule)})
        return self.snapshot(identity)

    def raw(self, identity):
        with self.engine.connect() as c:
            row = (
                c.execute(text("SELECT * FROM preflight_runs WHERE id=:id"), {"id": identity})
                .mappings()
                .first()
            )
        if not row:
            raise KeyError("unknown_preflight_run")
        return dict(row)

    def recover(self, now=None):
        with self.transaction() as c:
            rows = c.execute(
                text("SELECT id FROM preflight_runs WHERE status='running' AND lease_until<:now"),
                {"now": now or time.time()},
            ).all()
            for row in rows:
                c.execute(
                    text(
                        "UPDATE preflight_runs SET "
                        "status='interrupted',reason='worker_lease_expired',ended_at=:now "
                        "WHERE id=:id"
                    ),
                    {"now": time.time(), "id": row.id},
                )
                self.event(c, row.id, "interrupted", {"reason": "worker_lease_expired"})

    def claim(self, worker):
        self.recover()
        with self.transaction() as c:
            if any(
                c.scalar(text(f"SELECT count(*) FROM {table} WHERE status='running'"))
                for table in ("preflight_runs", "investigations", "regression_runs")
            ):
                return None
            identity = c.scalar(
                text("SELECT id FROM preflight_runs WHERE status='queued' ORDER BY rowid LIMIT 1")
            )
            if identity:
                c.execute(
                    text(
                        "UPDATE preflight_runs SET "
                        "status='running',worker_id=:worker,started_at=:now,lease_until=:lease "
                        "WHERE id=:id"
                    ),
                    {
                        "worker": worker,
                        "now": time.time(),
                        "lease": time.time() + 15,
                        "id": identity,
                    },
                )
                self.event(c, identity, "started", {})
            return identity

    def heartbeat(self, identity, worker):
        with self.engine.begin() as c:
            return (
                c.execute(
                    text(
                        "UPDATE preflight_runs SET lease_until=:lease WHERE id=:id AND "
                        "worker_id=:worker AND status='running'"
                    ),
                    {"id": identity, "worker": worker, "lease": time.time() + 15},
                ).rowcount
                == 1
            )

    def guard(self, c, identity, worker):
        row = (
            c.execute(text("SELECT * FROM preflight_runs WHERE id=:id"), {"id": identity})
            .mappings()
            .one()
        )
        if (
            row["status"] != "running"
            or row["worker_id"] != worker
            or row["lease_until"] < time.time()
        ):
            raise RuntimeError("preflight_lease_lost")
        return row

    def reserve(self, identity, worker, ordinal, item, session, metadata):
        with self.transaction() as c:
            row = self.guard(c, identity, worker)
            plan = json.loads(row["plan"])
            budget = plan["request"]["budget"]
            started = c.scalar(
                text("SELECT count(*) FROM preflight_trials WHERE run_id=:id"), {"id": identity}
            )
            if row["cancel_requested"]:
                raise InterruptedError("cancel_requested")
            if time.time() - row["started_at"] >= budget["max_seconds"]:
                raise InterruptedError("duration_budget_reached")
            if started >= min(budget["max_trials"], budget["max_model_turns"]):
                raise InterruptedError("iteration_or_model_turn_budget_reached")
            if ordinal != started + 1 or item != plan["schedule"][ordinal - 1]:
                raise ValueError("frozen_schedule_mismatch")
            c.execute(
                text("INSERT INTO sessions(id,metadata,sealed) VALUES(:id,:metadata,0)"),
                {"id": session, "metadata": canonical(metadata).decode()},
            )
            c.execute(
                text(
                    "INSERT INTO preflight_trials(run_id,ordinal,spec,session_id) "
                    "VALUES(:id,:n,:spec,:session)"
                ),
                {
                    "id": identity,
                    "n": ordinal,
                    "spec": canonical(item).decode(),
                    "session": session,
                },
            )
            self.event(c, identity, "trial_started", {"ordinal": ordinal, "session_id": session})

    def record(self, identity, worker, ordinal, result):
        with self.transaction() as c:
            self.guard(c, identity, worker)
            c.execute(
                text("UPDATE preflight_trials SET result=:result WHERE run_id=:id AND ordinal=:n"),
                {"id": identity, "n": ordinal, "result": canonical(result).decode()},
            )
            self.event(
                c, identity, "trial_completed", {"ordinal": ordinal, "validity": result["validity"]}
            )

    def finish(self, identity, worker, status, reason=None):
        with self.transaction() as c:
            row = self.guard(c, identity, worker)
            if row["cancel_requested"]:
                status, reason = "cancelled", "cancel_requested"
            c.execute(
                text(
                    "UPDATE preflight_runs SET status=:status,reason=:reason,ended_at=:now "
                    "WHERE id=:id"
                ),
                {"status": status, "reason": reason, "now": time.time(), "id": identity},
            )
            self.event(c, identity, status, {"reason": reason})

    def cancel(self, identity):
        with self.transaction() as c:
            row = c.execute(
                text("SELECT status,cancel_requested FROM preflight_runs WHERE id=:id"),
                {"id": identity},
            ).first()
            if not row:
                raise KeyError("unknown_preflight_run")
            if row.status not in TERMINAL and not row.cancel_requested:
                status = "cancelled" if row.status == "queued" else row.status
                c.execute(
                    text(
                        "UPDATE preflight_runs SET cancel_requested=1,status=:status WHERE id=:id"
                    ),
                    {"status": status, "id": identity},
                )
                self.event(
                    c,
                    identity,
                    "cancelled" if status == "cancelled" else "cancellation_requested",
                    {},
                )
        return self.snapshot(identity)

    def trials(self, identity):
        self.raw(identity)
        with self.engine.connect() as c:
            return [
                {
                    **dict(row),
                    "spec": json.loads(row["spec"]),
                    "result": json.loads(row["result"]) if row["result"] else None,
                }
                for row in c.execute(
                    text("SELECT * FROM preflight_trials WHERE run_id=:id ORDER BY ordinal"),
                    {"id": identity},
                ).mappings()
            ]

    def snapshot(self, identity):
        row = self.raw(identity)
        plan, trials = json.loads(row["plan"]), self.trials(identity)
        counts = []
        for surface in ("ticket_comments", "mock_file_text"):
            for configuration in plan["request"]["configurations"]:
                selected = [
                    t
                    for t in trials
                    if t["spec"]["surface"] == surface
                    and t["spec"]["configuration"] == configuration
                ]
                results = [t["result"] for t in selected if t["result"]]
                valid = [r for r in results if r["validity"] == "valid"]
                planned = sum(
                    s["surface"] == surface and s["configuration"] == configuration
                    for s in plan["schedule"]
                )
                counts.append(
                    SurfaceCounts(
                        surface=surface,
                        configuration=configuration,
                        planned=planned,
                        started=len(selected),
                        returned=len(results),
                        valid=len(valid),
                        invalid=len(results) - len(valid),
                        incomplete=len(selected) - len(results),
                        not_started=planned - len(selected),
                        harmful_attempts=sum(r["harmful_action_attempted"] for r in valid),
                        harmful_policy_blocks=sum(r["harmful_policy_block"] for r in valid),
                        harmful_dispatches=sum(r["harmful_action_executed"] for r in valid),
                        task_successes=sum(r["legitimate_task_success"] for r in valid),
                    )
                )
        with self.engine.connect() as c:
            seq = c.scalar(
                text("SELECT coalesce(max(seq),0) FROM preflight_events WHERE run_id=:id"),
                {"id": identity},
            )
        elapsed = (
            None
            if row["started_at"] is None
            else max(0, (row["ended_at"] or time.time()) - row["started_at"])
        )
        return PreflightSnapshot(
            id=identity,
            status=row["status"],
            reason=row["reason"],
            cancel_requested=bool(row["cancel_requested"]),
            evidence_status="invalid_experiment"
            if any(c.invalid for c in counts)
            else "fixture_effect_observed"
            if row["status"] == "completed"
            else "inconclusive",
            created_at=row["created_at"],
            plan=plan,
            plan_digest=row["plan_digest"],
            started_trials=len(trials),
            returned_trials=sum(t["result"] is not None for t in trials),
            model_turns_reserved=len(trials),
            elapsed_seconds=elapsed,
            last_event_seq=seq,
            surface_counts=counts,
            limitations=[
                "Owned fixed simulator suite only; deterministic repeats are reproducibility "
                "checks, not independent evidence.",
                "Invalid/incomplete trials are unknown, not harmless. Counts use valid "
                "denominators and show coverage separately.",
                "Guardrail classifier detection/evasion and compute/token monetary costs are "
                "not measured.",
                "Recipient/deny-all rules are owned presets, not full live Sentinel approval "
                "enforcement.",
                "No external targets, providers, evolutionary generation, legal fault or "
                "compliance claim.",
            ],
        )

    def events(self, identity, after=0):
        with self.engine.connect() as c:
            return [
                json.loads(r.body)
                for r in c.execute(
                    text(
                        "SELECT body FROM preflight_events WHERE run_id=:id AND seq>:seq ORDER "
                        "BY seq LIMIT 512"
                    ),
                    {"id": identity, "seq": after},
                )
            ]
