"""Backend-owned contracts exported to OpenAPI and generated TypeScript."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

SCHEMA_VERSION = "1.0"
MCP_PROTOCOL_REVISION = "2026-07-28"
CURRENT_PHASE = "P6"


class RunMode(StrEnum):
    PLAYBACK = "playback"
    SIMULATED = "simulated"
    LOCAL_MODEL = "local_model"
    REMOTE_MODEL = "remote_model"


class FeatureMaturity(StrEnum):
    PLANNED = "planned"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    EXPERIMENTAL = "experimental"


class EvidenceStatus(StrEnum):
    UNAVAILABLE = "unavailable"
    PRIOR = "prior"
    EXPLORATORY = "exploratory"
    FIXTURE_EFFECT_OBSERVED = "fixture_effect_observed"
    SUPPORTED_INTERVENTION_EFFECT = "supported_intervention_effect"
    INCONCLUSIVE = "inconclusive"
    NO_DETECTED_EFFECT = "no_detected_effect"
    UNSUPPORTED_REPLAY = "unsupported_replay"
    INVALID_EXPERIMENT = "invalid_experiment"


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["1.0"] = SCHEMA_VERSION


class ModeCapability(Contract):
    mode: RunMode
    label: str
    available: bool
    maturity: FeatureMaturity
    evidence_status: EvidenceStatus
    reason: str


class FeatureCapability(Contract):
    id: str
    label: str
    description: str
    available: bool
    maturity: FeatureMaturity
    evidence_status: EvidenceStatus
    reason: str


class CapabilitiesResponse(Contract):
    phase: str = CURRENT_PHASE
    modes: list[ModeCapability]
    features: list[FeatureCapability]
    mcp_sdk: str
    mcp_protocol_revision: str
    replay_isolation: Literal["unavailable", "verified_no_network"] = "unavailable"


class DatabaseReadiness(Contract):
    ready: bool
    reason: Literal["ready", "migration_required", "database_unavailable"]
    migration_revision: str | None
    journal_mode: str | None


class HealthResponse(Contract):
    status: Literal["ok", "not_ready"]
    ready: bool
    service: Literal["rewind-api"] = "rewind-api"
    version: str
    phase: str = CURRENT_PHASE
    database: DatabaseReadiness
    available_modes: list[RunMode]
    stored_session_count: int = 0
