"""Pure owned-world evaluation. Only the container launcher may claim isolation."""

import json
import random
import time
from uuid import uuid4

from rewind_core.contracts import RunMode
from rewind_sandbox.fixtures import digest
from rewind_sandbox.models import model_for
from rewind_sandbox.outcomes import harmful, task_success
from rewind_sandbox.schemas import Action

from rewind_replay.contracts import TrialRequest


class UnsupportedReplay(ValueError):
    pass


def transform(request: TrialRequest):
    subject = request.world.subject.model_copy(deep=True)
    intervention = request.intervention
    targets = set(intervention.targets)
    if intervention.kind == "remove_required_fact":
        if targets != {"ticket:issue"}:
            raise UnsupportedReplay("Unknown required-fact intervention")
        subject = subject.model_copy(
            update={
                "ticket": {key: value for key, value in subject.ticket.items() if key != "issue"}
            }
        )
    elif intervention.kind in {"remove", "neutral_replace"}:
        if not targets <= {item.occurrence_id for item in subject.inputs}:
            raise UnsupportedReplay("Unknown input occurrence")
        changed = []
        for item in subject.inputs:
            if item.occurrence_id not in targets:
                changed.append(item)
            elif intervention.kind == "neutral_replace":
                neutral = ("Neutral support context. " * (len(item.text) // 25 + 2))[
                    : len(item.text)
                ]
                changed.append(item.model_copy(update={"text": neutral}))
        subject = subject.model_copy(update={"inputs": changed})
    elif targets:
        raise UnsupportedReplay("Baseline cannot target occurrences")
    return subject


class StrictResolver:
    def __init__(self, calls: list[dict]):
        self.calls = calls

    def read(
        self, tool: str, schema_digest: str, arguments: dict, occurrence: int, state_digest: str
    ):
        if tool not in {"ticket.read", "files.read"}:
            raise UnsupportedReplay("Strict recorded writes require owned mock mediation")
        key = (tool, schema_digest, digest(arguments), occurrence, state_digest)
        for row in self.calls:
            recorded = (
                row["tool"],
                row["schema_digest"],
                row["arguments_digest"],
                row["occurrence"],
                row["environment_state_digest"],
            )
            if key == recorded:
                return row["response"]
        raise UnsupportedReplay("Unknown or state-incompatible recorded call")


def run_trial(request: TrialRequest) -> dict:
    started = time.perf_counter()
    trial_id = str(uuid4())
    base = {
        "schema_version": "1.0",
        "trial_id": trial_id,
        "mode": request.mode,
        "world_digest": digest(request.world),
        "seed": request.seed,
        "fresh_decision": False,
        "validity": "invalid",
        "reason": None,
    }
    try:
        if request.mode != RunMode.SIMULATED:
            raise UnsupportedReplay("No configured real-model runtime; playback is not a trial")
        resolver = None
        if request.strict_calls is not None:
            resolver = StrictResolver(request.strict_calls)
            recorded = resolver.read(
                "ticket.read",
                (request.strict_schemas or {}).get("ticket", "unsupported_schema"),
                {"ticket_id": request.world.subject.ticket["id"]},
                0,
                digest({"world": request.world.model_dump(mode="json"), "outbox": []}),
            )
            if isinstance(recorded, dict) and "content" in recorded:
                recorded = recorded.get("structured_content") or json.loads(
                    recorded["content"][0]["text"]
                )
            if recorded != {
                "ticket": request.world.subject.ticket,
                "inputs": [item.model_dump(mode="json") for item in request.world.subject.inputs],
            }:
                raise UnsupportedReplay(
                    "Recorded ticket response does not match the declared snapshot"
                )
        subject = transform(request)
        decision = model_for(request.mode, request.trust_external).decide(subject)
        if (
            request.stochastic
            and random.Random(request.seed).random() >= request.attempt_probability
        ):
            decision = decision.model_copy(update={"actions": []})
        # Fresh cloned tools: all writes terminate in this trial's private local state.
        base.update(
            {
                "fresh_decision": True,
                "model_request": subject.model_dump(mode="json"),
                "model_response": decision.model_dump(mode="json"),
                "request_digest": digest(subject),
                "response_digest": digest(decision),
                "attempts": [item.model_dump(mode="json") for item in decision.actions],
            }
        )
        outbox = []
        dispatches: list[Action] = []
        for index, action in enumerate(decision.actions):
            if action.tool != "mail.send_email":
                raise UnsupportedReplay("Unknown sandbox tool")
            recipient = action.arguments.get("recipient", "")
            attachment = action.arguments.get("attachment", "")
            if (
                not recipient.casefold().endswith(".example")
                or attachment not in request.world.files
            ):
                raise UnsupportedReplay("Tool arguments outside owned synthetic world")
            file_data = request.world.files[attachment]
            if resolver is not None:
                state = [
                    {key: item[key] for key in ("recipient", "attachment", "synthetic_rows")}
                    for item in outbox
                ]
                recorded = resolver.read(
                    "files.read",
                    (request.strict_schemas or {}).get("files", "unsupported_schema"),
                    {"file_id": attachment},
                    1 + 2 * index,
                    digest({"world": request.world.model_dump(mode="json"), "outbox": state}),
                )
                if "content" in recorded:
                    recorded = recorded.get("structured_content") or json.loads(
                        recorded["content"][0]["text"]
                    )
                file_data = recorded.get("file", recorded)
                if file_data != request.world.files[attachment]:
                    raise UnsupportedReplay(
                        "Recorded file response does not match the declared snapshot"
                    )
            outbox.append(
                {
                    "recipient": recipient,
                    "attachment": attachment,
                    "synthetic_rows": len(file_data["rows"]),
                    "sink": "isolated_synthetic_outbox",
                }
            )
            dispatches.append(action)
        base.update(
            {
                "fresh_decision": True,
                "validity": "valid",
                "model_request": subject.model_dump(mode="json"),
                "model_response": decision.model_dump(mode="json"),
                "request_digest": digest(subject),
                "attempts": [item.model_dump(mode="json") for item in decision.actions],
                "dispatches": [item.model_dump(mode="json") for item in dispatches],
                "outbox": outbox,
                "harmful_action_attempted": any(
                    harmful(item, request.world) for item in decision.actions
                ),
                "harmful_action_executed": any(harmful(item, request.world) for item in dispatches),
                "task_success": task_success(decision, request.world),
                "stochastic": request.stochastic,
                "distribution": "parsed fixture action gated by independent Bernoulli(p)"
                if request.stochastic
                else "deterministic instruction DSL",
            }
        )
    except (UnsupportedReplay, ValueError, KeyError) as error:
        base.update({"reason": str(error), "evidence_status": "unsupported_replay"})
    base["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 3)
    return base
