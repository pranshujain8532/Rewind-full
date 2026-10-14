from typing import Any, Literal

from pydantic import Field

from rewind_core.contracts import Contract

TARGET = "owned-support-agent-v1"
SUITE = "preflight-fixed-v1"
Surface = Literal["ticket_comments", "mock_file_text"]
Configuration = Literal["vulnerable-v1", "containment-v1", "behavioural-v1", "deny-all-v1"]
FIXTURE_IDS = [
    f"{surface}/{case}"
    for surface in ("ticket_comments", "mock_file_text")
    for case in ("clean", "export_directive", "benign_imperative", "unknown_attachment")
]


class PreflightBudget(Contract):
    max_trials: int = Field(default=32, ge=1, le=96)
    max_model_turns: int = Field(default=32, ge=1, le=96)
    max_seconds: int = Field(default=180, ge=1, le=600)
    max_provider_cost_usd: Literal[0] = 0


class PreflightRequest(Contract):
    target_id: Literal["owned-support-agent-v1"] = TARGET
    suite_version: Literal["preflight-fixed-v1"] = SUITE
    configurations: list[Configuration] = Field(
        default=["vulnerable-v1", "containment-v1"], min_length=1, max_length=4
    )
    repeats: int = Field(default=1, ge=1, le=3)
    seed: int = Field(default=4471, ge=0, le=2**32 - 1)
    budget: PreflightBudget = Field(default_factory=PreflightBudget)


class PreflightSpec(Contract):
    target_id: Literal["owned-support-agent-v1"] = TARGET
    suite_version: Literal["preflight-fixed-v1"] = SUITE
    fixture_id: str = Field(min_length=1, max_length=100)
    fixture_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    surface: Surface
    configuration: Configuration
    configuration_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    seed: int = Field(ge=0, le=2**64 - 1)


class PreflightBatch(Contract):
    operation: Literal["preflight_trials"] = "preflight_trials"
    trials: list[PreflightSpec] = Field(min_length=1, max_length=8)


class SurfaceCounts(Contract):
    surface: Surface
    configuration: str
    planned: int
    started: int
    returned: int
    valid: int
    invalid: int
    incomplete: int
    not_started: int
    harmful_attempts: int
    harmful_policy_blocks: int
    harmful_dispatches: int
    task_successes: int
    guardrail_detection: Literal["not_measured"] = "not_measured"


class PreflightSnapshot(Contract):
    id: str
    mode: Literal["simulated"] = "simulated"
    maturity: Literal["implemented", "verified"] = "verified"
    evidence_status: str
    status: Literal["queued", "running", "completed", "cancelled", "interrupted", "failed"]
    reason: str | None
    cancel_requested: bool = False
    created_at: str
    plan: dict[str, Any]
    plan_digest: str
    started_trials: int
    returned_trials: int
    model_turns_reserved: int
    provider_cost_usd: Literal[0] = 0
    elapsed_seconds: float | None
    last_event_seq: int
    surface_counts: list[SurfaceCounts]
    limitations: list[str]
