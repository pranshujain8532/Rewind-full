from typing import Any, Literal

from pydantic import Field
from rewind_core.contracts import Contract, EvidenceStatus, RunMode


class Budget(Contract):
    max_trials: int = Field(default=256, ge=1, le=512)
    max_model_turns: int = Field(default=256, ge=1, le=512)
    max_seconds: int = Field(default=600, ge=1, le=3600)
    max_tokens: int = Field(default=0, ge=0, le=1000000)
    authorised_cost_usd: float = Field(default=0, ge=0, le=100, allow_inf_nan=False)


class InvestigationRequest(Contract):
    session_id: str = Field(min_length=1, max_length=100)
    mode: RunMode = RunMode.SIMULATED
    stochastic: bool = False
    attempt_probability: float = Field(default=0.8, ge=0, le=1, allow_inf_nan=False)
    n: int = Field(default=40, ge=20, le=100)
    max_finalists: int = Field(default=3, ge=1, le=3)
    discovery_budget: int = Field(default=24, ge=5, le=40)
    meaningful_effect: float = Field(default=0.20, gt=0, le=1, allow_inf_nan=False)
    seed: int = Field(default=4471, ge=0, le=2**64 - 1)
    budget: Budget = Field(default_factory=Budget)


class DemoRequest(Contract):
    scenario: Literal["clean", "single", "harmless", "interaction", "redundant", "authorised"]


class Counts(Contract):
    started: int
    valid: int
    invalid: int
    incomplete: int
    harmful: int
    dispatched: int
    task_success: int


class Candidate(Contract):
    id: str
    target: str
    origin: str
    position: int
    score: float
    features: dict[str, float | None]
    rank: int
    selected: bool
    coverage: str
    tested_subsets: list[int]


class GraphResponse(Contract):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, str]]
    target_nodes: list[str] = Field(default_factory=list)
    candidates: list[Candidate]
    ranking_formula: str = "4*present + before + 2*external + 1/(1+graph_distance)"
    limitations: list[str] = Field(default_factory=list)


class Finding(Contract):
    arm: str
    targets: list[str]
    mode: RunMode
    evidence_status: EvidenceStatus
    baseline: Counts
    intervention: Counts
    baseline_rate: float | None
    intervention_rate: float | None
    base_flip_rate: float | None
    effect: float | None
    interval: list[float] | None
    interval_method: str | None
    nominal_level: float = 0.95
    adjusted_alpha: float
    interval_level: float
    meaningful_effect: float
    complete: bool
    remedy_eligible: bool
    reason: str
    scope: str


class JobSnapshot(Contract):
    id: str
    session_id: str
    mode: RunMode
    status: Literal["queued", "running", "completed", "cancelled", "failed", "interrupted"]
    evidence_status: EvidenceStatus
    reason: str | None
    created_at: str
    heartbeat_at: str | None
    cancel_requested: bool
    budget: Budget
    plan: dict[str, Any] | None
    plan_digest: str | None
    completed_trials: int
    started_trials: int
    model_turns: int
    last_event_seq: int
    findings: list[Finding]
    coverage: list[Candidate]
    limitations: list[str]


class ProgressEvent(Contract):
    id: str
    job_id: str
    job_seq: int
    type: str
    time: str
    data: dict[str, Any]
