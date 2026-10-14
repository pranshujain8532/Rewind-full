"""Transactional job state, leases, raw trial storage and persisted-before-send SSE."""

import json
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rewind_core.contracts import EvidenceStatus as E
from rewind_core.storage import make_engine
from rewind_sandbox.fixtures import canonical, digest
from sqlalchemy import text

from rewind_eval.contracts import InvestigationRequest, JobSnapshot
from rewind_eval.findings import findings
from rewind_eval.provenance import provenance
from rewind_eval.source import read_capture

TERMINAL = {"completed", "cancelled", "failed", "interrupted"}
LEASE_SECONDS = 15


def utc() -> str:
    return datetime.now(UTC).isoformat()


class JobStore:
    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.engine = make_engine(self.directory)

    @contextmanager
    def transaction(self):
        with self.engine.connect() as connection:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            try:
                yield connection
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    def _event(self, connection, job_id: str, kind: str, data: dict):
        seq = connection.scalar(
            text("SELECT coalesce(max(seq),0)+1 FROM investigation_events WHERE job_id=:id"),
            {"id": job_id},
        )
        body = {
            "schema_version": "1.0",
            "id": f"{job_id}:{seq}",
            "job_id": job_id,
            "job_seq": seq,
            "type": kind,
            "time": utc(),
            "data": data,
        }
        connection.execute(
            text("INSERT INTO investigation_events(job_id,seq,body) VALUES(:id,:seq,:body)"),
            {"id": job_id, "seq": seq, "body": canonical(body).decode()},
        )

    def start(self, request: InvestigationRequest, key: str) -> JobSnapshot:
        if not 1 <= len(key) <= 100:
            raise ValueError("Idempotency key must have 1..100 characters")
        request_digest = digest(request)
        with self.engine.connect() as connection:
            previous = connection.execute(
                text("SELECT id,request_digest FROM investigations WHERE idempotency_key=:key"),
                {"key": key},
            ).first()
            if previous:
                if previous.request_digest != request_digest:
                    raise ValueError("idempotency_conflict")
                return self.snapshot(previous.id)
            if not connection.scalar(
                text("SELECT count(*) FROM sessions WHERE id=:id"), {"id": request.session_id}
            ):
                raise KeyError("Unknown session")
        n = request.n if request.stochastic else 1
        required = request.discovery_budget + n * (1 + request.max_finalists)
        if required > min(request.budget.max_trials, request.budget.max_model_turns):
            raise ValueError(
                f"Unaffordable proposal: reserve {required} trials/turns, including controls"
            )
        graph = {"schema_version": "1.0", "candidates": [], "nodes": [], "edges": []}
        reason = None
        try:
            if request.mode.value != "simulated":
                raise ValueError(
                    "unsupported_replay: playback is not inference; "
                    "real adapters/budgets unavailable"
                )
            from rewind_replay.container import MANIFEST

            runtime = json.loads(MANIFEST.read_bytes())
            if not runtime.get("isolation_verified"):
                raise ValueError("unsupported_replay: isolation probes not verified")
            bundle, world, _ = read_capture(self.directory, request.session_id)
            graph = provenance(bundle)
            graph["runtime_image_id"] = runtime["image_id"]
            from rewind_eval.demo import has_control

            if not has_control(world):
                raise ValueError(
                    "unsupported_replay: no captured owned benign control; create a P4 demo capture"
                )
        except (OSError, ValueError, KeyError) as error:
            reason = (
                str(error)
                if str(error).startswith("unsupported_replay")
                else "unsupported_replay: capture/runtime unavailable"
            )
        job_id = str(uuid4())
        with self.transaction() as connection:
            # A concurrent retry can win between preflight and this transaction.
            previous = connection.execute(
                text("SELECT id,request_digest FROM investigations WHERE idempotency_key=:key"),
                {"key": key},
            ).first()
            if previous:
                if previous.request_digest != request_digest:
                    raise ValueError("idempotency_conflict")
                job_id = previous.id
            else:
                connection.execute(
                    text(
                        "INSERT INTO investigations(id,session_id,idempotency_key,"
                        "request_digest,request,status,reason,created_at,cancel_requested,graph) "
                        "VALUES(:id,:session,:key,:digest,:request,:status,:reason,:time,0,:graph)"
                    ),
                    {
                        "id": job_id,
                        "session": request.session_id,
                        "key": key,
                        "digest": request_digest,
                        "request": canonical(request).decode(),
                        "status": "failed" if reason else "queued",
                        "reason": reason,
                        "time": utc(),
                        "graph": canonical(graph).decode(),
                    },
                )
                self._event(
                    connection, job_id, "failed" if reason else "queued", {"reason": reason}
                )
        return self.snapshot(job_id)

    def raw_job(self, job_id: str) -> dict:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    text("SELECT * FROM investigations WHERE id=:id"), {"id": job_id}
                )
                .mappings()
                .first()
            )
            if not row:
                raise KeyError("Unknown investigation")
            return dict(row)

    def trials(self, job_id: str) -> list[dict]:
        with self.engine.connect() as connection:
            return [
                dict(r)
                for r in connection.execute(
                    text("SELECT * FROM investigation_trials WHERE job_id=:id ORDER BY ordinal"),
                    {"id": job_id},
                ).mappings()
            ]

    def snapshot(self, job_id: str) -> JobSnapshot:
        job = self.raw_job(job_id)
        request = InvestigationRequest.model_validate_json(job["request"])
        plan = json.loads(job["plan"]) if job["plan"] else None
        rows = self.trials(job_id)
        results = [json.loads(r["result"]) for r in rows if r["result"]]
        reported = findings(plan, rows, job["status"], request.mode)
        status = E.EXPLORATORY
        if job["reason"] and job["reason"].startswith("unsupported_replay"):
            status = E.UNSUPPORTED_REPLAY
        elif any(r.get("validity") == "invalid" for r in results):
            status = E.INVALID_EXPERIMENT
        elif job["status"] in {"cancelled", "interrupted", "failed"}:
            status = E.INCONCLUSIVE
        elif reported:
            states = {f.evidence_status for f in reported}
            status = (
                E.FIXTURE_EFFECT_OBSERVED
                if E.FIXTURE_EFFECT_OBSERVED in states
                else E.NO_DETECTED_EFFECT
                if states == {E.NO_DETECTED_EFFECT}
                else E.INCONCLUSIVE
            )
        coverage = json.loads(job["graph"])["candidates"]
        for candidate in coverage:
            tested = [
                r
                for r in rows
                if r["phase"] == "discovery"
                and candidate["target"] in json.loads(r["manifest"])["intervention"]["targets"]
            ]
            candidate["tested_subsets"] = [r["ordinal"] for r in tested]
            if tested:
                candidate["coverage"] = "tested_exploratory"
        with self.engine.connect() as connection:
            last_seq = connection.scalar(
                text("SELECT coalesce(max(seq),0) FROM investigation_events WHERE job_id=:id"),
                {"id": job_id},
            )
        return JobSnapshot(
            id=job_id,
            session_id=job["session_id"],
            mode=request.mode,
            status=job["status"],
            evidence_status=status,
            reason=job["reason"],
            created_at=job["created_at"],
            heartbeat_at=job["heartbeat_at"],
            cancel_requested=bool(job["cancel_requested"]),
            budget=request.budget,
            plan=plan,
            plan_digest=job["plan_digest"],
            completed_trials=len(results),
            started_trials=len(rows),
            model_turns=sum(bool(r.get("fresh_decision")) for r in results),
            last_event_seq=last_seq,
            findings=reported,
            coverage=coverage,
            limitations=[
                "Simulator-only; no real-model causal conclusion.",
                "Bounded subsets; no global minimality, monotonicity or safety guarantee.",
                "Local trust anchor; no independent external checkpoint.",
                "Deterministic repeats do not provide inferential sample size.",
            ],
        )

    def events(self, job_id: str, after: int = 0) -> list[dict]:
        with self.engine.connect() as connection:
            return [
                json.loads(r.body)
                for r in connection.execute(
                    text(
                        "SELECT body FROM investigation_events WHERE job_id=:id AND seq>:seq "
                        "ORDER BY seq LIMIT 1024"
                    ),
                    {"id": job_id, "seq": after},
                )
            ]

    def cancel(self, job_id: str) -> JobSnapshot:
        with self.transaction() as connection:
            row = connection.execute(
                text("SELECT status FROM investigations WHERE id=:id"), {"id": job_id}
            ).first()
            if not row:
                raise KeyError("Unknown investigation")
            if row.status not in TERMINAL:
                connection.execute(
                    text(
                        "UPDATE investigations SET cancel_requested=1,"
                        "status=:status,reason=:reason WHERE id=:id"
                    ),
                    {
                        "id": job_id,
                        "status": "cancelled" if row.status == "queued" else row.status,
                        "reason": "Cancelled before execution" if row.status == "queued" else None,
                    },
                )
                self._event(
                    connection,
                    job_id,
                    "cancelled" if row.status == "queued" else "cancellation_requested",
                    {},
                )
        return self.snapshot(job_id)

    def recover(self, now: float | None = None):
        with self.transaction() as connection:
            expired = connection.execute(
                text("SELECT id FROM investigations WHERE status='running' AND lease_until<:now"),
                {"now": now or time.time()},
            ).all()
            for row in expired:
                # Preserve reservations without outcomes; never fabricate completed/valid trials.
                connection.execute(
                    text(
                        "UPDATE investigations SET status='interrupted',"
                        "reason='Worker lease expired; incomplete trials retained' WHERE id=:id"
                    ),
                    {"id": row.id},
                )
                self._event(connection, row.id, "interrupted", {"reason": "worker_lease_expired"})

    def claim(self, worker_id: str) -> str | None:
        self.recover()
        with self.transaction() as connection:
            if connection.scalar(
                text("SELECT count(*) FROM investigations WHERE status='running'")
            ) or connection.scalar(
                text("SELECT count(*) FROM regression_runs WHERE status='running'")
            ):
                return None
            row = connection.execute(
                text(
                    "SELECT id FROM investigations WHERE status='queued' "
                    "ORDER BY created_at,id LIMIT 1"
                )
            ).first()
            if not row:
                return None
            connection.execute(
                text(
                    "UPDATE investigations SET status='running',started_at=:now,"
                    "worker_id=:worker,lease_until=:lease,heartbeat_at=:time WHERE id=:id"
                ),
                {
                    "id": row.id,
                    "worker": worker_id,
                    "now": time.time(),
                    "lease": time.time() + LEASE_SECONDS,
                    "time": utc(),
                },
            )
            self._event(connection, row.id, "started", {"worker_id": worker_id})
            return row.id

    def heartbeat(self, job_id: str, worker_id: str) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE investigations SET lease_until=:lease,heartbeat_at=:time "
                    "WHERE id=:id AND worker_id=:worker AND status='running'"
                ),
                {
                    "id": job_id,
                    "worker": worker_id,
                    "lease": time.time() + LEASE_SECONDS,
                    "time": utc(),
                },
            )
            return result.rowcount == 1

    def guard(self, connection, job_id: str, worker_id: str) -> dict:
        row = dict(
            connection.execute(text("SELECT * FROM investigations WHERE id=:id"), {"id": job_id})
            .mappings()
            .one()
        )
        if (
            row["status"] != "running"
            or row["worker_id"] != worker_id
            or row["lease_until"] < time.time()
        ):
            raise RuntimeError("Worker no longer owns job")
        return row

    def finish(self, job_id: str, worker_id: str, status: str, reason: str | None = None):
        with self.transaction() as connection:
            row = self.guard(connection, job_id, worker_id)
            if row["cancel_requested"]:
                status, reason = (
                    "cancelled",
                    "Cancellation requested; retained actual in-flight results",
                )
            connection.execute(
                text("UPDATE investigations SET status=:status,reason=:reason WHERE id=:id"),
                {"id": job_id, "status": status, "reason": reason},
            )
            self._event(connection, job_id, status, {"reason": reason})

    def freeze(self, job_id: str, worker_id: str, plan: dict):
        with self.transaction() as connection:
            self.guard(connection, job_id, worker_id)
            connection.execute(
                text("UPDATE investigations SET plan=:plan,plan_digest=:digest WHERE id=:id"),
                {"id": job_id, "plan": canonical(plan).decode(), "digest": digest(plan)},
            )
            self._event(
                connection,
                job_id,
                "confirmation_frozen",
                {"plan_digest": digest(plan), "plan": plan},
            )

    def reserve(self, job_id: str, worker_id: str, phase: str, specs: list[dict]) -> list[int]:
        with self.transaction() as connection:
            row = self.guard(connection, job_id, worker_id)
            request = InvestigationRequest.model_validate_json(row["request"])
            if row["cancel_requested"]:
                raise InterruptedError("Cancellation requested")
            if time.time() - row["started_at"] >= request.budget.max_seconds:
                raise InterruptedError("Duration budget reached")
            used = connection.scalar(
                text("SELECT count(*) FROM investigation_trials WHERE job_id=:id"), {"id": job_id}
            )
            if used + len(specs) > min(request.budget.max_trials, request.budget.max_model_turns):
                raise InterruptedError("Trial/model-turn budget reached")
            if phase == "confirmation" and not row["plan"]:
                raise ValueError("Confirmation must be frozen before reserving trials")
            ordinals = []
            for index, spec in enumerate(specs, used + 1):
                connection.execute(
                    text(
                        "INSERT INTO investigation_trials(job_id,ordinal,phase,arm,manifest) "
                        "VALUES(:id,:ordinal,:phase,:arm,:manifest)"
                    ),
                    {
                        "id": job_id,
                        "ordinal": index,
                        "phase": phase,
                        "arm": spec["arm"],
                        "manifest": canonical(spec).decode(),
                    },
                )
                self._event(
                    connection,
                    job_id,
                    "trial_started",
                    {"ordinal": index, "phase": phase, "manifest": spec},
                )
                ordinals.append(index)
            return ordinals

    def record(self, job_id: str, worker_id: str, ordinals: list[int], results: list[dict]):
        if len(ordinals) != len(results):
            raise ValueError("Incomplete batch response")
        with self.transaction() as connection:
            self.guard(connection, job_id, worker_id)
            for ordinal, result in zip(ordinals, results, strict=True):
                connection.execute(
                    text(
                        "UPDATE investigation_trials SET result=:result "
                        "WHERE job_id=:id AND ordinal=:ordinal AND result IS NULL"
                    ),
                    {"id": job_id, "ordinal": ordinal, "result": canonical(result).decode()},
                )
                self._event(
                    connection,
                    job_id,
                    "trial_completed",
                    {
                        "ordinal": ordinal,
                        "validity": result.get("validity"),
                        "result_digest": digest(result),
                    },
                )
