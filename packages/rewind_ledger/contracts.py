from typing import Any, Literal

from pydantic import Field
from rewind_core.contracts import Contract, EvidenceStatus, RunMode
from rewind_eval.contracts import Budget, Candidate, Counts, Finding


class RecordRequest(Contract):
    investigation_id: str = Field(min_length=1, max_length=100)


class EvidenceRecord(Contract):
    id: str
    created_at: str
    investigation_id: str
    session_id: str
    mode: RunMode
    evidence_status: EvidenceStatus
    session_seal: dict[str, Any] | None
    provenance: dict[str, Any]
    capture_coverage: dict[str, Any]
    replay_coverage: dict[str, Any]
    candidate_scope: list[Candidate] = Field(max_length=16)
    counts: dict[str, Counts]
    findings: list[Finding] = Field(max_length=3)
    policy_approval_trail: dict[str, Any]
    observed_synthetic_impact: dict[str, Any]
    governance_mapping: dict[str, Any]
    regression_ids: dict[str, str]
    limitations: list[str]


class VerificationResult(Contract):
    integrity_valid: bool
    trusted: bool
    evidence_complete: bool
    regression_eligible: bool
    reason: str
    signing_key_id: str | None = None


class CaseRequest(Contract):
    kind: Literal["behavioural", "containment"] = "behavioural"


class RegressionRequest(Contract):
    case_id: str = Field(min_length=1, max_length=100)
    fixed_configuration: Literal[
        "vulnerable-v1", "behavioural-v1", "containment-v1", "deny-all-v1"
    ] = "behavioural-v1"
    mode: RunMode = RunMode.SIMULATED
    seed: int = Field(default=4471, ge=0, le=2**64 - 2)
    budget: Budget = Field(
        default_factory=lambda: Budget(max_trials=2, max_model_turns=2, max_seconds=60)
    )


class RegressionSnapshot(Contract):
    id: str
    case_id: str
    record_id: str | None = None
    kind: Literal["behavioural", "containment"] | None = None
    status: Literal["queued", "running", "completed", "cancelled", "failed", "interrupted"]
    verdict: Literal["pass", "fail", "inconclusive"]
    reason: str | None
    created_at: str
    heartbeat_at: str | None
    elapsed_seconds: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    cancel_requested: bool = False
    started_trials: int
    completed_trials: int
    last_event_seq: int = 0
    plan: dict[str, Any]
    plan_json: str | None = None
    manifest: dict[str, Any] | None
