from typing import Any, Literal

from pydantic import Field
from rewind_core.contracts import Contract, RunMode


class InputOccurrence(Contract):
    occurrence_id: str
    text: str = Field(max_length=10000)
    source_uri: str
    origin: Literal["external", "owner", "tool"]


class SubjectInput(Contract):
    task: str = Field(max_length=10000)
    ticket: dict[str, str]
    inputs: list[InputOccurrence] = Field(max_length=16)
    allowed_recipients: list[str]


class World(Contract):
    version: str = "synthetic-support-v1"
    subject: SubjectInput
    files: dict[str, dict[str, Any]]


class Action(Contract):
    tool: str
    arguments: dict[str, Any]


class ModelDecision(Contract):
    actions: list[Action]
    summary: dict[str, str]


class RunResult(Contract):
    run_id: str
    mode: RunMode
    environment: Literal["owned_host_mocks", "isolated_sandbox", "recorded_playback"]
    fresh_decision: bool
    evidence_status: str
    world_digest: str
    config_digest: str
    model_request: SubjectInput
    model_response: ModelDecision
    attempts: list[Action]
    dispatches: list[Action]
    outbox: list[dict[str, Any]]
    harmful_action_attempted: bool
    harmful_action_executed: bool
    task_success: bool
    tool_trace: list[dict[str, Any]]
    limitations: list[str]
