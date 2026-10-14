"""Fresh two-arm regression work, outside HTTP handlers, with persisted reservations."""

import threading
import time
from uuid import uuid4

from rewind_replay.container import MANIFEST, execute
from rewind_replay.contracts import BatchRequest
from rewind_sandbox.fixtures import digest
from rewind_sandbox.schemas import World

from rewind_ledger.bundle import verify_bundle
from rewind_ledger.evidence import check_trial
from rewind_ledger.regression import CONFIGURATIONS, case_bound, trial_request
from rewind_ledger.store import LedgerStore


class RegressionWorker:
    def __init__(self, store: LedgerStore, runner=execute):
        self.store, self.runner, self.id = store, runner, str(uuid4())
        self.stop = threading.Event()

    def run_one(self):
        import json

        identity = self.store.claim(self.id)
        if identity is None:
            return False
        done = threading.Event()

        def heartbeat():
            while not done.wait(1):
                try:
                    if not self.store.heartbeat(identity, self.id):
                        return
                except Exception:
                    return  # A failed lease cannot release a successful manifest.

        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
        try:
            row = self.store.raw_run(identity)
            plan, case = json.loads(row["plan"]), self.store.case(row["case_id"])
            source = self.store.bundle(case["record_id"])
            checked = verify_bundle(source, self.store.trusted_public())
            if not checked.integrity_valid or not checked.regression_eligible:
                raise ValueError("source_evidence_invalid")
            if not case_bound(case, source):
                raise ValueError("original_attack_case_binding_invalid")
            world = World.model_validate(case["original_world"])
            for ordinal, spec in enumerate(plan["schedule"], 1):
                if self.stop.is_set():
                    raise InterruptedError("worker_stopping")
                runtime = json.loads(MANIFEST.read_bytes())
                if (
                    not runtime.get("isolation_verified")
                    or runtime["image_id"] != plan["runtime_image_id"]
                ):
                    raise ValueError("runtime_changed_since_frozen_plan")
                self.store.reserve(identity, self.id, ordinal, spec)
                request = trial_request(world, spec)
                remaining = plan["budget"]["max_seconds"] - (time.time() - row["started_at"])
                raw = self.runner(
                    BatchRequest(trials=[request]), timeout=max(1, min(30, int(remaining)))
                )
                if raw.get("environment") != "isolated_sandbox" or len(raw.get("results", [])) != 1:
                    raise ValueError("isolated_regression_result_unavailable")
                result = dict(raw["results"][0])
                if not check_trial(result, request):
                    result.update(validity="invalid", reason="regression_trial_fact_mismatch")
                result.update(
                    configuration_digest=digest(CONFIGURATIONS[spec["configuration"]]),
                    runtime_image_id=plan["runtime_image_id"],
                    usage={
                        "provider_cost_usd": 0,
                        "compute_cost_usd": None,
                        "source": "deterministic simulator; no paid inference",
                    },
                )
                self.store.record(identity, self.id, ordinal, result)
                if result["validity"] != "valid":
                    raise ValueError("regression_trial_invalid")
                if time.time() - row["started_at"] >= plan["budget"]["max_seconds"]:
                    raise InterruptedError("regression_duration_budget")
            self.store.finish(identity, self.id, "completed")
        except InterruptedError:
            self.store.finish(
                identity, self.id, "interrupted", "cancelled_or_interrupted_partial_trials"
            )
        except Exception:
            try:
                self.store.finish(
                    identity, self.id, "failed", "regression_invalid_or_execution_failed"
                )
            except RuntimeError:
                self.store.recover()
        finally:
            done.set()
            thread.join(timeout=2)
        return True
