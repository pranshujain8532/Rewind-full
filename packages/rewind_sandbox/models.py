"""Transparent fixture mechanism; explicitly not an LLM or injection classifier."""

import re
from typing import Protocol

from rewind_core.contracts import RunMode

from rewind_sandbox.schemas import Action, ModelDecision, RunResult, SubjectInput


class CapabilityError(RuntimeError):
    pass


class SubjectModel(Protocol):
    def decide(self, request: SubjectInput) -> ModelDecision: ...


class Simulator:
    def __init__(self, trust_external: bool = True):
        self.trust_external = trust_external

    def decide(self, request: SubjectInput) -> ModelDecision:
        # Intentionally vulnerable instruction-following DSL, documented for teaching.
        text = request.task
        if self.trust_external:
            text += "\n" + "\n".join(item.text for item in request.inputs)
        matches = re.findall(r"SEND\s+recipient=([\w.+-]+@[\w.-]+)\s+attachment=([\w-]+)", text)
        actions = [
            Action(
                tool="mail.send_email", arguments={"recipient": recipient, "attachment": attachment}
            )
            for recipient, attachment in dict.fromkeys(matches)
        ]
        return ModelDecision(actions=actions, summary=dict(request.ticket))


class Playback:
    def read(self, recording: RunResult) -> RunResult:
        return recording.model_copy(
            update={
                "mode": RunMode.PLAYBACK,
                "environment": "recorded_playback",
                "fresh_decision": False,
                "evidence_status": "unavailable",
                "limitations": ["Recorded playback; no new behavioural evidence."],
            }
        )


def model_for(mode: RunMode, trust_external: bool = True) -> SubjectModel:
    if mode == RunMode.SIMULATED:
        return Simulator(trust_external)
    if mode == RunMode.PLAYBACK:
        raise CapabilityError(
            "Playback reads an existing recording; it cannot decide changed inputs."
        )
    raise CapabilityError(f"{mode}: no configured real-model adapter; no simulator fallback")
