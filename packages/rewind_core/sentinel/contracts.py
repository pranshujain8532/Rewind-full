"""Backend-owned P7 contracts; identity is supplied by authenticated adapters."""

from datetime import datetime
from typing import Any, Literal

from pydantic import AwareDatetime, Field, model_validator

from rewind_core.contracts import Contract


class Mandate(Contract):
    version: str = Field(min_length=1, max_length=100)
    issuer: str = Field(min_length=1, max_length=100)
    agent_id: str = Field(min_length=1, max_length=100)
    session_id: str = Field(min_length=1, max_length=100)
    world_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    not_before: AwareDatetime
    not_after: AwareDatetime
    allowed_tools: list[str] = Field(max_length=16)
    denied_tools: list[str] = Field(default_factory=list, max_length=16)
    data_ids: list[str] = Field(max_length=32)
    data_classes: list[str] = Field(max_length=16)
    recipients: list[str] = Field(max_length=32)
    denied_recipients: list[str] = Field(default_factory=list, max_length=32)
    denied_data_ids: list[str] = Field(default_factory=list, max_length=32)
    high_impact_tools: list[str] = Field(default_factory=list, max_length=16)
    approvers: list[str] = Field(max_length=16)
    max_dispatches: int = Field(ge=0, le=128)
    max_export_rows: int = Field(ge=0, le=10000)
    authorised_cost_usd: Literal[0] = 0
    approval_seconds: int = Field(default=60, ge=1, le=300)

    @model_validator(mode="after")
    def valid_period(self):
        if self.not_before >= self.not_after:
            raise ValueError("invalid_validity_period")
        if len(self.model_dump_json()) > 16000:
            raise ValueError("mandate_too_large")
        return self


class SignedMandate(Contract):
    mandate: Mandate
    signing_key_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    signature: str = Field(pattern=r"^[a-f0-9]{128}$")


class StartRequest(Contract):
    source_session_id: str = Field(min_length=1, max_length=100)
    hold_seconds: int = Field(default=60, ge=1, le=300)


class DecisionRequest(Contract):
    decision: Literal["approve", "deny", "deny_and_investigate", "cancel"]
    action_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    args_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    session_id: str = Field(min_length=1, max_length=100)
    mandate_version: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=500)


class ActionView(Contract):
    id: str
    session_id: str
    source_session_id: str
    agent_id: str
    mandate_version: str
    action_digest: str
    args_digest: str
    tool: str
    arguments: dict[str, Any]
    policy_verdict: Literal["in_scope", "out_of_scope", "undefined"]
    enforcement_decision: Literal["allow", "hold", "deny"]
    state: Literal["held", "dispatched", "denied", "expired", "cancelled"]
    reason: str
    deadline: datetime
    approval: dict[str, Any] | None
    result: dict[str, Any] | None
    agent_can_resume: bool
    investigation_id: str | None
    investigation_error: str | None
    investigation_requested: bool


class SentinelSession(Contract):
    id: str
    source_session_id: str
    agent_id: str
    mode: Literal["simulated"] = "simulated"
    evidence_status: Literal["fixture_effect_observed"] = "fixture_effect_observed"
    maturity: Literal["implemented", "verified"] = "verified"
    coverage: str = "Owned stateless simulator + policy + transactional local mock tools"
    integrity: str
    mandate: SignedMandate
    actions: list[ActionView]
    dispatched: int
    exported_rows: int
    last_event_seq: int
    status: Literal["awaiting_approval", "completed", "tool_timeout", "cancelled"]
    task_success: bool | None
    limitations: list[str]
