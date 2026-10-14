"""One isolated fresh trial at a time; record invalid/incomplete evidence without retry."""

import json
import subprocess
import threading
import time
from uuid import uuid4

from rewind_capture.store import CaptureStore
from rewind_eval.tool_contract import supported_schemas
from rewind_ledger.evidence import check_trial
from rewind_replay.container import MANIFEST, execute
from rewind_sandbox.fixtures import digest
from rewind_sandbox.outcomes import PREDICATE_VERSION
from rewind_sandbox.schemas import SubjectInput

from rewind_core.contracts import MCP_PROTOCOL_REVISION

from .contracts import PreflightBatch, PreflightSpec
from .fixtures import expected_reads, fixture, measures, trial_request, validate_spec


class PreflightWorker:
    def __init__(self, store, runner=execute):
        self.store, self.runner, self.id = store, runner, str(uuid4())
        self.stop = threading.Event()

    def run_one(self):
        identity = self.store.claim(self.id)
        if not identity:
            return False
        done = threading.Event()

        def pulse():
            while not done.wait(1):
                try:
                    if not self.store.heartbeat(identity, self.id):
                        return
                except Exception:
                    return

        thread = threading.Thread(target=pulse, daemon=True)
        thread.start()
        try:
            self.evaluate(identity)
            self.store.finish(identity, self.id, "completed")
        except InterruptedError as error:
            try:
                self.store.finish(identity, self.id, "interrupted", str(error))
            except RuntimeError:
                pass
        except subprocess.TimeoutExpired:
            self.store.finish(
                identity, self.id, "interrupted", "isolated_trial_timeout; outcome incomplete"
            )
        except Exception:
            try:
                self.store.finish(
                    identity, self.id, "failed", "preflight_worker_failed; reservations retained"
                )
            except RuntimeError:
                pass
        finally:
            done.set()
            thread.join(timeout=2)
        return True

    def evaluate(self, identity):
        row = self.store.raw(identity)
        plan = json.loads(row["plan"])
        capture = CaptureStore(self.store.directory)
        try:
            seen = set()
            for ordinal, data in enumerate(plan["schedule"], 1):
                if self.stop.is_set():
                    raise InterruptedError("worker_stopping")
                item = PreflightSpec.model_validate(data)
                validate_spec(item)
                runtime = json.loads(MANIFEST.read_bytes())
                if (
                    not runtime.get("isolation_verified")
                    or runtime["image_id"] != plan["runtime_image_id"]
                ):
                    raise ValueError("preflight_runtime_changed")
                world, session = fixture(item.fixture_id), str(uuid4())
                metadata = {
                    "schema_version": "1.0",
                    "mode": "simulated",
                    "model": "instruction-dsl-v1",
                    "agent_binding": "owned-demo-agent",
                    "world_digest": digest(world),
                    "config_digest": digest(
                        {
                            "simulator": "instruction-dsl-v1",
                            "trust_external": trial_request(item).trust_external,
                            "predicate": PREDICATE_VERSION,
                            "protocol": MCP_PROTOCOL_REVISION,
                        }
                    ),
                    "preflight_configuration": item.configuration,
                    "preflight_configuration_digest": item.configuration_digest,
                    "fixture_version": item.suite_version,
                    "fixture_id": item.fixture_id,
                    "surface": item.surface,
                    "preflight_run_id": identity,
                    "task_ref": world.subject.ticket["id"],
                    "owner_ref": "local-user",
                    "capture_scope": "isolated owned SDK reads, fresh simulator, "
                    "private mock state",
                    "external_identity_verified": False,
                }
                self.store.reserve(identity, self.id, ordinal, data, session, metadata)
                capture.append(session, "initial_world", world.model_dump(mode="json"))
                budget = plan["request"]["budget"]
                remaining = budget["max_seconds"] - (time.time() - row["started_at"])
                if remaining <= 0:
                    raise InterruptedError("duration_budget_reached")
                began = time.monotonic()
                raw = self.runner(PreflightBatch(trials=[item]), timeout=min(30, remaining))
                if (
                    raw.get("environment") != "isolated_sandbox"
                    or raw.get("preflight_runtime_version") != item.suite_version
                    or len(raw.get("results", [])) != 1
                ):
                    raise ValueError("isolated_preflight_result_missing")
                result = dict(raw["results"][0])
                invalid = None
                if (
                    result.get("world_digest") != item.fixture_digest
                    or result.get("seed") != item.seed
                    or result.get("configuration_digest") != item.configuration_digest
                    or result.get("fixture_id") != item.fixture_id
                    or result.get("surface") != item.surface
                    or result.get("fixture_version") != item.suite_version
                    or result.get("configuration") != item.configuration
                    or result.get("model") != "instruction-dsl-v1"
                    or result.get("protocol") != MCP_PROTOCOL_REVISION
                    or not result.get("trial_id")
                    or result["trial_id"] in seen
                    or not supported_schemas(result.get("tool_schemas", {}), world.version)
                ):
                    invalid = "isolated_result_identity_or_schema_mismatch"
                if result.get("validity") == "valid" and not check_trial(
                    result, trial_request(item)
                ):
                    invalid = "code_owned_trial_check_failed"
                if result.get("owned_reads") != expected_reads(world, item.surface):
                    invalid = "owned_surface_read_mismatch"
                if invalid:
                    result.update(
                        validity="invalid",
                        reason=invalid,
                        harmful_policy_block=None,
                        legitimate_task_success=None,
                    )
                seen.add(result.get("trial_id"))
                result.update(measures(result, trial_request(item)))
                result.update(
                    runtime_image_id=plan["runtime_image_id"],
                    usage={
                        "reserved_model_turns": 1,
                        "actual_model_turns": int(bool(result.get("fresh_decision"))),
                        "provider_requests": 0,
                        "provider_cost_usd": 0,
                        "compute_cost_usd": None,
                        "input_tokens": None,
                        "output_tokens": None,
                        "host_elapsed_ms": round((time.monotonic() - began) * 1000, 3),
                        "runtime_elapsed_ms": result.get("elapsed_ms"),
                        "source": "local simulator; compute/token billing not measured",
                    },
                )
                for read in result.get("owned_reads", []):
                    capture.append(session, "tool_result", read, read["tool"])
                capture.append(session, "tool_schema", result.get("tool_schemas", {}))
                if result.get("fresh_decision"):
                    capture.capture_input(
                        session,
                        SubjectInput.model_validate(result["model_request"]),
                        result["tool_schemas"],
                    )
                    capture.append(session, "model_response", result["model_response"])
                for kind, values in (
                    ("tool_requested", result.get("attempts", [])),
                    ("policy_decision", result.get("policy_approval_trail", [])),
                    ("tool_dispatched", result.get("dispatches", [])),
                ):
                    for value in values:
                        capture.append(session, kind, value)
                capture.append(session, "outcome", result)
                capture.seal(
                    session,
                    {
                        "model_adapter": bool(result.get("fresh_decision")),
                        "completed": result["validity"] == "valid",
                        "trial_validity": result["validity"],
                        "state": "full_initial_world",
                        "memory": "stateless_simulator",
                        "protocol": MCP_PROTOCOL_REVISION,
                        "tools": ["ticket", "files", "mail"],
                        "unsupported": ["real models", "production tools", "guardrail classifier"],
                    },
                )
                self.store.record(identity, self.id, ordinal, result)
                if time.time() - row["started_at"] >= budget["max_seconds"]:
                    raise InterruptedError("duration_budget_reached; returned outcome retained")
        finally:
            capture.engine.dispose()
