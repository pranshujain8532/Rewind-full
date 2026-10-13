from typing import Any, Literal

from pydantic import Field
from rewind_core.contracts import Contract, RunMode
from rewind_sandbox.schemas import World


class Intervention(Contract):
    kind: Literal["none", "remove", "neutral_replace", "remove_required_fact"] = "none"
    targets: list[str] = Field(default_factory=list, max_length=16)


class TrialRequest(Contract):
    world: World
    mode: RunMode = RunMode.SIMULATED
    intervention: Intervention = Field(default_factory=Intervention)
    trust_external: bool = True
    stochastic: bool = False
    attempt_probability: float = Field(default=0.8, ge=0, le=1)
    seed: int = Field(default=0, ge=0, le=2**64 - 1)
    strict_calls: list[dict[str, Any]] | None = None
    strict_schemas: dict[str, str] | None = None


class BatchRequest(Contract):
    operation: Literal["trials", "probe"] = "trials"
    trials: list[TrialRequest] = Field(default_factory=list, max_length=256)
