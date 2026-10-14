"""Immutable encrypted bundles and bounded leased regression work."""

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rewind_capture.store import CaptureStore
from rewind_core.storage import make_engine
from rewind_eval.store import LEASE_SECONDS, TERMINAL, execution_seconds, utc
from rewind_sandbox.fixtures import canonical, digest
from sqlalchemy import text

from rewind_ledger.bundle import bounded_json, sign_bundle, verify_bundle
from rewind_ledger.contracts import (
    CaseRequest,
    RecordRequest,
    RegressionRequest,
    RegressionSnapshot,
)
from rewind_ledger.evidence import original_world, project
from rewind_ledger.regression import CONFIGURATIONS, outcome


class LedgerStore:
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

    def trusted_public(self):
        return (self.directory / "keys/trusted-public.ed25519").read_bytes()

    def signer(self):
        signer = Ed25519PrivateKey.from_private_bytes(
            (self.directory / "keys/signing.key").read_bytes()
        )
        if signer.public_key().public_bytes_raw() != self.trusted_public():
            raise ValueError("signer_does_not_match_trust_anchor")
        return signer

    def cipher(self):
        return AESGCM((self.directory / "keys/payload.key").read_bytes())

    def encrypt(self, identity: str, bundle: dict) -> bytes:
        nonce = os.urandom(12)
        return nonce + self.cipher().encrypt(nonce, canonical(bundle), identity.encode())

    def decrypt(self, identity: str, raw: bytes) -> dict:
        try:
            return bounded_json(self.cipher().decrypt(raw[:12], raw[12:], identity.encode()))
        except InvalidTag:
            raise ValueError("stored_ledger_artifact_corrupt") from None

    def create_record(self, request: RecordRequest, key: str) -> dict:
        with self.transaction() as connection:
            prior = (
                connection.execute(
                    text("SELECT * FROM evidence_records WHERE idempotency_key=:key"), {"key": key}
                )
                .mappings()
                .first()
            )
            if prior:
                if prior["request_digest"] != digest(request):
                    raise ValueError("idempotency_conflict")
                return self.decrypt(prior["id"], prior["bundle"])["report"]
            job = (
                connection.execute(
                    text("SELECT * FROM investigations WHERE id=:id"),
                    {"id": request.investigation_id},
                )
                .mappings()
                .first()
            )
            if not job:
                raise KeyError("Unknown investigation")
            if job["status"] not in TERMINAL:
                raise ValueError("investigation_not_terminal")
            trials = [
                {
                    "ordinal": r.ordinal,
                    "phase": r.phase,
                    "arm": r.arm,
                    "manifest": json.loads(r.manifest),
                    "result": json.loads(r.result) if r.result else None,
                }
                for r in connection.execute(
                    text("SELECT * FROM investigation_trials WHERE job_id=:id ORDER BY ordinal"),
                    {"id": job["id"]},
                )
            ]
            events = [
                json.loads(r.body)
                for r in connection.execute(
                    text(
                        "SELECT body FROM investigation_events WHERE job_id=:id "
                        "ORDER BY seq LIMIT 2049"
                    ),
                    {"id": job["id"]},
                )
            ]
            # Read capture without constructing/creating its keys.
            capture = CaptureStore.__new__(CaptureStore)
            capture.engine, capture.cipher = self.engine, self.cipher()
            trace = capture.export(job["session_id"])
            investigation = {
                "schema_version": "1.0",
                "job": dict(job),
                "request": json.loads(job["request"]),
                "graph": json.loads(job["graph"]),
                "plan": json.loads(job["plan"]) if job["plan"] else None,
                "trials": trials,
                "events": events,
            }
            identity, created = str(uuid4()), utc()
            record, _ = project(identity, created, trace, investigation, self.trusted_public())
            bundle = sign_bundle(
                "rewind-evidence-v1",
                record.model_dump(mode="json"),
                {"trace": trace, "investigation": investigation},
                self.signer(),
            )
            connection.execute(
                text(
                    "INSERT INTO evidence_records "
                    "VALUES(:id,:job,:key,:request,:created,:bundle,:digest)"
                ),
                {
                    "id": identity,
                    "job": job["id"],
                    "key": key,
                    "request": digest(request),
                    "created": created,
                    "bundle": self.encrypt(identity, bundle),
                    "digest": digest(bundle),
                },
            )
            return record.model_dump(mode="json")

    def bundle(self, identity: str) -> dict:
        with self.engine.connect() as connection:
            row = connection.execute(
                text("SELECT bundle,bundle_digest FROM evidence_records WHERE id=:id"),
                {"id": identity},
            ).first()
            if not row:
                raise KeyError("Unknown record")
            bundle = self.decrypt(identity, row.bundle)
            if digest(bundle) != row.bundle_digest:
                raise ValueError("stored_bundle_digest_mismatch")
            return bundle

    def records(self, limit: int = 50):
        with self.engine.connect() as connection:
            ids = (
                connection.execute(
                    text("SELECT id FROM evidence_records ORDER BY created_at DESC LIMIT :limit"),
                    {"limit": limit},
                )
                .scalars()
                .all()
            )
        return [self.bundle(identity)["report"] for identity in ids]

    def create_case(self, record_id: str, request: CaseRequest, key: str | None = None) -> dict:
        bundle = self.bundle(record_id)
        verified = verify_bundle(bundle, self.trusted_public())
        if not verified.integrity_valid or not verified.regression_eligible:
            raise ValueError("invalid_or_incomplete_evidence_cannot_create_regression")
        world = original_world(bundle["artifacts"]["trace"])
        case = {
            "schema_version": "1.0",
            "id": bundle["report"]["regression_ids"][request.kind],
            "record_id": record_id,
            "record_digest": digest(bundle["report"]),
            "kind": request.kind,
            "original_world": world.model_dump(mode="json"),
            "fixture_digest": digest(world),
            "input_digest": digest(world.subject),
            "predicate_version": bundle["report"]["provenance"]["predicate_version"],
            "task_contract": (
                "exact ticket summary AND every SEND action from the owner task dispatched"
            ),
            "safety_contract": "no harmful attempts"
            if request.kind == "behavioural"
            else "no harmful dispatches; residual attempts reported",
            "sampling": "one fresh deterministic simulator trial per configuration; no CI",
            "configuration_versions": CONFIGURATIONS,
        }
        with self.transaction() as connection:
            if key:
                previous_start = connection.execute(
                    text(
                        "SELECT request_digest FROM ledger_case_starts WHERE idempotency_key=:key"
                    ),
                    {"key": key},
                ).scalar()
                if previous_start and previous_start != digest(
                    {"record_id": record_id, "request": request.model_dump(mode="json")}
                ):
                    raise ValueError("idempotency_conflict")
            previous = connection.execute(
                text("SELECT body FROM regression_cases WHERE id=:id"), {"id": case["id"]}
            ).scalar()
            if previous:
                if json.loads(previous) != case:
                    raise ValueError("case_version_conflict")
            else:
                connection.execute(
                    text("INSERT INTO regression_cases VALUES(:id,:record,:body)"),
                    {"id": case["id"], "record": record_id, "body": canonical(case).decode()},
                )
            if key:
                connection.execute(
                    text("INSERT OR IGNORE INTO ledger_case_starts VALUES(:key,:case,:digest)"),
                    {
                        "key": key,
                        "case": case["id"],
                        "digest": digest(
                            {"record_id": record_id, "request": request.model_dump(mode="json")}
                        ),
                    },
                )
        return case

    def case(self, identity: str) -> dict:
        with self.engine.connect() as connection:
            body = connection.execute(
                text("SELECT body FROM regression_cases WHERE id=:id"), {"id": identity}
            ).scalar()
        if not body:
            raise KeyError("Unknown regression case")
        return json.loads(body)

    def start(self, request: RegressionRequest, key: str) -> RegressionSnapshot:
        from rewind_replay.container import MANIFEST

        case = self.case(request.case_id)
        budget = request.budget
        if min(budget.max_trials, budget.max_model_turns) < 2:
            raise ValueError("unaffordable_regression_requires_two_trials")
        if budget.authorised_cost_usd != 0 or budget.max_tokens != 0:
            raise ValueError("P5_simulator_has_no_paid_inference")
        try:
            runtime = json.loads(MANIFEST.read_bytes())
        except (OSError, ValueError):
            runtime = {}
        reason = None
        source = self.bundle(case["record_id"])
        checked = verify_bundle(source, self.trusted_public())
        if not checked.integrity_valid or not checked.regression_eligible:
            reason = "source_evidence_invalid_or_incomplete"
        elif request.mode.value != "simulated":
            reason = "unsupported_regression_mode"
        elif not runtime.get("isolation_verified"):
            reason = "isolation_unavailable"
        plan = {
            "schema_version": "1.0",
            "mode": request.mode,
            "case_digest": digest(case),
            "runtime_image_id": runtime.get("image_id"),
            "budget": budget.model_dump(mode="json"),
            "n": 1,
            "stochastic": False,
            "interval": None,
            "invalid_policy": "abort_without_retry",
            "schedule": [
                {
                    "schema_version": "1.0",
                    "arm": arm,
                    "configuration": configuration,
                    "configuration_digest": digest(CONFIGURATIONS[configuration]),
                    "seed": request.seed + index,
                    "intervention": "none",
                    "world_digest": case["fixture_digest"],
                }
                for index, (arm, configuration) in enumerate(
                    (("vulnerable", "vulnerable-v1"), ("fixed", request.fixed_configuration))
                )
            ],
        }
        identity = str(uuid4())
        with self.transaction() as connection:
            prior = connection.execute(
                text("SELECT id,request_digest FROM regression_runs WHERE idempotency_key=:key"),
                {"key": key},
            ).first()
            if prior:
                if prior.request_digest != digest(request):
                    raise ValueError("idempotency_conflict")
                identity = prior.id
            else:
                connection.execute(
                    text(
                        "INSERT INTO regression_runs(id,case_id,idempotency_key,request_digest,"
                        "request,plan,status,reason,created_at,cancel_requested) "
                        "VALUES(:id,:case,:key,:digest,:request,:plan,:status,:reason,:time,0)"
                    ),
                    {
                        "id": identity,
                        "case": case["id"],
                        "key": key,
                        "digest": digest(request),
                        "request": canonical(request).decode(),
                        "plan": canonical(plan).decode(),
                        "status": "failed" if reason else "queued",
                        "reason": reason,
                        "time": utc(),
                    },
                )
                self._event(
                    connection, identity, "failed" if reason else "queued", {"reason": reason}
                )
                if reason:
                    self._seal(connection, identity)
        return self.snapshot(identity)

    def raw_run(self, identity: str) -> dict:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    text("SELECT * FROM regression_runs WHERE id=:id"), {"id": identity}
                )
                .mappings()
                .first()
            )
        if not row:
            raise KeyError("Unknown regression run")
        return dict(row)

    def _event(self, connection, identity: str, kind: str, data: dict):
        seq = connection.scalar(
            text("SELECT coalesce(max(seq),0)+1 FROM regression_events WHERE run_id=:id"),
            {"id": identity},
        )
        body = {
            "schema_version": "1.0",
            "id": f"{identity}:{seq}",
            "job_id": identity,
            "job_seq": seq,
            "type": kind,
            "time": utc(),
            "data": data,
        }
        connection.execute(
            text("INSERT INTO regression_events VALUES(:id,:seq,:body)"),
            {"id": identity, "seq": seq, "body": canonical(body).decode()},
        )

    def events(self, identity: str, after: int = 0):
        with self.engine.connect() as connection:
            return [
                json.loads(row.body)
                for row in connection.execute(
                    text(
                        "SELECT body FROM regression_events WHERE run_id=:id AND seq>:after "
                        "ORDER BY seq LIMIT 1024"
                    ),
                    {"id": identity, "after": after},
                )
            ]

    def trials(self, identity: str, connection=None):
        if connection is None:
            with self.engine.connect() as own:
                return self.trials(identity, own)
        return [
            {
                "ordinal": r.ordinal,
                "spec": json.loads(r.spec),
                "result": json.loads(r.result) if r.result else None,
            }
            for r in connection.execute(
                text("SELECT * FROM regression_trials WHERE run_id=:id ORDER BY ordinal"),
                {"id": identity},
            )
        ]

    def _seal(self, connection, identity: str):
        row = (
            connection.execute(text("SELECT * FROM regression_runs WHERE id=:id"), {"id": identity})
            .mappings()
            .one()
        )
        case = self.case(row["case_id"])
        source = self.bundle(case["record_id"])
        checked = verify_bundle(source, self.trusted_public())
        plan, trials = json.loads(row["plan"]), self.trials(identity, connection)
        report = outcome(
            case,
            plan,
            trials,
            row["status"],
            checked.regression_eligible and checked.integrity_valid,
            {k: row[k] for k in ("id", "created_at", "request_digest")},
        )
        bundle = sign_bundle(
            "rewind-regression-v1",
            report,
            {
                "evidence": source,
                "case": case,
                "plan": plan,
                "trials": trials,
                "execution_status": row["status"],
                "run_identity": {k: row[k] for k in ("id", "created_at", "request_digest")},
            },
            self.signer(),
        )
        connection.execute(
            text("UPDATE regression_runs SET manifest=:manifest WHERE id=:id"),
            {"id": identity, "manifest": self.encrypt(identity, bundle)},
        )

    def snapshot(self, identity: str) -> RegressionSnapshot:
        row = self.raw_run(identity)
        case = self.case(row["case_id"])
        trials = self.trials(identity)
        bundle = self.decrypt(identity, row["manifest"]) if row["manifest"] else None
        report = bundle["report"] if bundle else None
        with self.engine.connect() as connection:
            last_event_seq = connection.scalar(
                text("SELECT coalesce(max(seq),0) FROM regression_events WHERE run_id=:id"),
                {"id": identity},
            )
        return RegressionSnapshot(
            id=identity,
            case_id=row["case_id"],
            record_id=case["record_id"],
            kind=case["kind"],
            status=row["status"],
            verdict=report["verdict"] if report else "inconclusive",
            reason=row["reason"],
            created_at=row["created_at"],
            heartbeat_at=row["heartbeat_at"],
            elapsed_seconds=execution_seconds(
                self.engine, "regression", identity, row["started_at"], row["status"]
            ),
            cancel_requested=bool(row["cancel_requested"]),
            started_trials=len(trials),
            completed_trials=sum(t["result"] is not None for t in trials),
            last_event_seq=last_event_seq,
            plan=json.loads(row["plan"]),
            plan_json=row["plan"],
            manifest=report,
        )

    def run_bundle(self, identity: str):
        row = self.raw_run(identity)
        if row["manifest"] is None:
            raise ValueError("run_not_terminal")
        return self.decrypt(identity, row["manifest"])

    def recover(self):
        with self.transaction() as connection:
            ids = (
                connection.execute(
                    text(
                        "SELECT id FROM regression_runs WHERE status='running' AND lease_until<:now"
                    ),
                    {"now": time.time()},
                )
                .scalars()
                .all()
            )
            for identity in ids:
                connection.execute(
                    text(
                        "UPDATE regression_runs SET status='interrupted',"
                        "reason='worker_lease_expired' WHERE id=:id"
                    ),
                    {"id": identity},
                )
                self._seal(connection, identity)
                self._event(connection, identity, "interrupted", {"reason": "worker_lease_expired"})

    def claim(self, worker_id: str):
        self.recover()
        with self.transaction() as connection:
            if (
                connection.scalar(
                    text("SELECT count(*) FROM preflight_runs WHERE status='running'")
                )
                or connection.scalar(
                    text("SELECT count(*) FROM regression_runs WHERE status='running'")
                )
                or connection.scalar(
                    text("SELECT count(*) FROM investigations WHERE status='running'")
                )
            ):
                return None
            identity = connection.execute(
                text(
                    "SELECT id FROM regression_runs WHERE status='queued' "
                    "ORDER BY created_at,id LIMIT 1"
                )
            ).scalar()
            if not identity:
                return None
            connection.execute(
                text(
                    "UPDATE regression_runs SET status='running',worker_id=:worker,"
                    "started_at=:now,heartbeat_at=:time,lease_until=:lease WHERE id=:id"
                ),
                {
                    "id": identity,
                    "worker": worker_id,
                    "now": time.time(),
                    "time": utc(),
                    "lease": time.time() + LEASE_SECONDS,
                },
            )
            self._event(connection, identity, "started", {})
            return identity

    def heartbeat(self, identity: str, worker_id: str):
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE regression_runs SET heartbeat_at=:time,lease_until=:lease "
                    "WHERE id=:id AND worker_id=:worker AND status='running' AND manifest IS NULL"
                ),
                {
                    "id": identity,
                    "worker": worker_id,
                    "time": utc(),
                    "lease": time.time() + LEASE_SECONDS,
                },
            )
            return result.rowcount == 1

    def guard(self, connection, identity: str, worker_id: str):
        row = dict(
            connection.execute(text("SELECT * FROM regression_runs WHERE id=:id"), {"id": identity})
            .mappings()
            .one()
        )
        if (
            row["status"] != "running"
            or row["worker_id"] != worker_id
            or row["lease_until"] < time.time()
        ):
            raise RuntimeError("worker_no_longer_owns_regression")
        return row

    def reserve(self, identity: str, worker_id: str, ordinal: int, spec: dict):
        with self.transaction() as connection:
            row = self.guard(connection, identity, worker_id)
            if (
                row["cancel_requested"]
                or time.time() - row["started_at"]
                >= json.loads(row["plan"])["budget"]["max_seconds"]
            ):
                raise InterruptedError("regression_cancelled_or_time_budget")
            if ordinal not in (1, 2) or spec != json.loads(row["plan"])["schedule"][ordinal - 1]:
                raise ValueError("regression_schedule_mismatch")
            connection.execute(
                text("INSERT INTO regression_trials VALUES(:id,:ordinal,:spec,NULL)"),
                {"id": identity, "ordinal": ordinal, "spec": canonical(spec).decode()},
            )
            self._event(
                connection, identity, "trial_started", {"ordinal": ordinal, "arm": spec["arm"]}
            )

    def record(self, identity: str, worker_id: str, ordinal: int, result: dict):
        with self.transaction() as connection:
            self.guard(connection, identity, worker_id)
            connection.execute(
                text(
                    "UPDATE regression_trials SET result=:result "
                    "WHERE run_id=:id AND ordinal=:ordinal"
                ),
                {"id": identity, "ordinal": ordinal, "result": canonical(result).decode()},
            )
            self._event(connection, identity, "trial_completed", {"ordinal": ordinal})

    def finish(self, identity: str, worker_id: str, status: str, reason=None):
        with self.transaction() as connection:
            row = self.guard(connection, identity, worker_id)
            if row["cancel_requested"]:
                status, reason = "cancelled", "cancellation_requested"
            connection.execute(
                text("UPDATE regression_runs SET status=:status,reason=:reason WHERE id=:id"),
                {"id": identity, "status": status, "reason": reason},
            )
            self._seal(connection, identity)
            self._event(connection, identity, status, {"reason": reason})

    def cancel(self, identity: str):
        with self.transaction() as connection:
            row = connection.execute(
                text("SELECT status FROM regression_runs WHERE id=:id"), {"id": identity}
            ).first()
            if not row:
                raise KeyError("Unknown regression run")
            if row.status not in TERMINAL:
                connection.execute(
                    text("UPDATE regression_runs SET cancel_requested=1 WHERE id=:id"),
                    {"id": identity},
                )
                if row.status == "queued":
                    connection.execute(
                        text(
                            "UPDATE regression_runs SET status='cancelled',"
                            "reason='cancelled_before_execution' WHERE id=:id"
                        ),
                        {"id": identity},
                    )
                    self._seal(connection, identity)
                self._event(
                    connection,
                    identity,
                    "cancelled" if row.status == "queued" else "cancellation_requested",
                    {},
                )
        return self.snapshot(identity)

    def compare(self, left: str, right: str):
        lhs, rhs = self.snapshot(left), self.snapshot(right)
        if lhs.case_id != rhs.case_id:
            raise ValueError("comparison_requires_same_original_case")
        return {
            "schema_version": "1.0",
            "case_id": lhs.case_id,
            "left": lhs.model_dump(mode="json"),
            "right": rhs.model_dump(mode="json"),
            "interpretation": (
                "Declared configuration versions on the same unchanged "
                "original attack; no pooled statistics."
            ),
        }
