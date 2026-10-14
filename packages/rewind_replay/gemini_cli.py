"""Credential catalog check and explicitly budgeted, captured Gemini trials."""

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rewind_capture.store import CaptureStore
from rewind_core.contracts import MCP_PROTOCOL_REVISION, RunMode
from rewind_core.storage import data_directory
from rewind_eval.demo import controlled_world
from rewind_sandbox.fixtures import canonical, digest, load_world

from rewind_replay.container import ROOT, verify_isolation
from rewind_replay.contracts import Intervention, TrialRequest
from rewind_replay.gemini import (
    MODEL,
    GeminiBroker,
    GeminiError,
    GeminiHTTP,
    GeminiModelConfig,
    GeminiPolicy,
    load_key,
    provider_request,
)
from rewind_replay.gemini_runtime import execute_gemini


def persist_trial(capture: CaptureStore, session_id: str, result: dict) -> None:
    """Seal actual invalid results too; integrity is distinct from trial validity."""
    if result.get("fresh_decision"):
        capture.append(
            session_id,
            "model_response",
            {
                "decision": result["model_response"],
                "provider_response": result["provider_response"],
            },
        )
    for kind, actions in (
        ("tool_requested", result.get("attempts", [])),
        ("tool_dispatched", result.get("dispatches", [])),
    ):
        for action in actions:
            capture.append(session_id, kind, action)
    capture.append(session_id, "outcome", result)
    capture.seal(
        session_id,
        {
            "model_adapter": True,
            "completed": result["validity"] == "valid",
            "trial_validity": result["validity"],
            "state": "full_initial_world",
            "memory": "stateless_gemini_adapter",
            "protocol": MCP_PROTOCOL_REVISION,
            "read_policy": "versioned_owned_snapshot",
            "unsupported": ["P4 real confirmation", "arbitrary production tools"],
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["catalog", "smoke"])
    parser.add_argument("--key-file", type=Path, default=ROOT / "api.txt")
    parser.add_argument(
        "--billing-mode", choices=["disabled", "declared_free_tier", "paid"], default="disabled"
    )
    parser.add_argument("--authorised-cost-usd", type=float, default=0)
    parser.add_argument("--max-requests", type=int, default=3)
    args = parser.parse_args()
    output = ROOT / "artifacts/gemini" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    config = GeminiModelConfig()
    http = GeminiHTTP(load_key(args.key_file))
    if args.command == "catalog":
        result = http.catalog()
        result["configured_model_listed"] = any(
            m["name"] == f"models/{MODEL}" for m in result["models"]
        )
        result["configured_model"] = MODEL
        (output / "catalog.json").write_bytes(canonical(result))
        print(json.dumps({k: v for k, v in result.items() if k != "models"}, indent=2))
        return
    if args.billing_mode == "disabled" or (
        args.billing_mode == "paid" and args.authorised_cost_usd <= 0
    ):
        raise GeminiError("inference_budget_not_authorised")
    # Invocation declares a bounded experiment, without independently proving project billing tier.
    policy = GeminiPolicy(
        billing_mode=args.billing_mode,
        authorised_cost_usd=args.authorised_cost_usd,
        max_requests=args.max_requests,
        declared_at=datetime.now(UTC).isoformat(),
    )
    probe = verify_isolation()
    world = controlled_world(load_world(ROOT / "fixtures", "single"))
    capture = CaptureStore(data_directory())
    trials, session_ids = [], []
    active = {"session_id": None}

    def reserved(record):
        capture.append(active["session_id"], "provider_request_reserved", record)

    def completed(record):
        capture.append(active["session_id"], "provider_response_received", record)

    broker = GeminiBroker(config, policy, http, on_reserve=reserved, on_result=completed)
    started = time.monotonic()
    plan = {
        "schema_version": "1.0",
        "mode": "remote_model",
        "provider": "gemini",
        "configuration": config.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
        "trial_plan": ["baseline", "remove_comment_0", "neutral_replace_comment_0"],
        "inference_interval": None,
        "interpretation": "exploratory adapter smoke; no attribution finding",
        "invalid_policy": "abort_without_retry",
        "isolation_probe": probe,
        "limitations": [
            "Project billing tier is user-declared, not independently verified.",
            "Seed is a sampling parameter, not a determinism guarantee.",
            "P4 real-model investigation eligibility remains unsupported.",
        ],
    }
    (output / "plan.json").write_bytes(canonical(plan))
    try:
        for index, intervention in enumerate(
            [
                Intervention(),
                Intervention(kind="remove", targets=["comment-0"]),
                Intervention(kind="neutral_replace", targets=["comment-0"]),
            ]
        ):
            session_id = str(uuid4())
            active["session_id"] = session_id
            session_ids.append(session_id)
            request = TrialRequest(
                world=world,
                mode=RunMode.REMOTE_MODEL,
                stochastic=True,
                seed=4471 + index,
                intervention=intervention,
            )
            from rewind_replay.runtime import transform

            subject = transform(request)
            body = provider_request(subject, config, request.seed)
            capture.create_session(
                session_id,
                {
                    "schema_version": "1.0",
                    "mode": "remote_model",
                    "provider": "gemini",
                    "world_digest": digest(world),
                    "config_digest": digest(config),
                    "model": MODEL,
                    "task_ref": world.subject.ticket["id"],
                    "agent_binding": "owned-gemini-agent",
                    "capture_scope": "isolated owned snapshot/mock runtime + hosted model adapter",
                    "owner_ref": "local-user",
                    "external_identity_verified": False,
                },
            )
            capture.append(session_id, "initial_world", world.model_dump(mode="json"))
            capture.append(
                session_id,
                "tool_schema",
                {"decision_schema": body["generationConfig"]["responseJsonSchema"]},
            )
            capture.capture_input(
                session_id,
                subject,
                {},
                model_requested=MODEL,
                provider_request=body,
                provider_configuration=config.model_dump(mode="json"),
            )
            result = execute_gemini(request, broker, timeout=90)
            trials.append(result)
            persist_trial(capture, session_id, result)
            if result["validity"] != "valid" or not result["fresh_decision"]:
                raise GeminiError("real_trial_invalid")
            print(
                f"Gemini trial {index}: valid; "
                f"harmful_attempt={result['harmful_action_attempted']}; "
                f"task_success={result['task_success']}",
                flush=True,
            )
    finally:
        (output / "results.json").write_bytes(
            canonical(
                {
                    "schema_version": "1.0",
                    "plan": plan,
                    "trials": trials,
                    "sessions": session_ids,
                    "provider_records": broker.records,
                    "elapsed_seconds": time.monotonic() - started,
                    "complete": len(trials) == 3 and all(t["validity"] == "valid" for t in trials),
                    "inference_interval": None,
                }
            )
        )
        capture.engine.dispose()
    print(f"Captured actual Gemini smoke artifacts: {output}")


if __name__ == "__main__":
    try:
        main()
    except GeminiError as error:
        # Never echo key/file/HTTP exception contents or raw provider responses to the terminal.
        print(
            json.dumps({"status": "unavailable", "reason": str(error), "inference_interval": None})
        )
        raise SystemExit(1) from None
