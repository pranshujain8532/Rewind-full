"""Explicit feature matrix; environment hints never enable unfinished code."""

from importlib.metadata import version

from rewind_core.contracts import (
    MCP_PROTOCOL_REVISION,
    CapabilitiesResponse,
    EvidenceStatus,
    FeatureCapability,
    FeatureMaturity,
    ModeCapability,
    RunMode,
)


def capabilities() -> CapabilitiesResponse:
    modes = [
        (
            RunMode.PLAYBACK,
            "Recorded playback",
            "CLI reads an explicit saved recording; no fresh inference.",
        ),
        (
            RunMode.SIMULATED,
            "Sandbox simulator",
            "Instruction DSL with owned local tools; no LLM or replay isolation claim.",
        ),
        (
            RunMode.LOCAL_MODEL,
            "Local model re-execution",
            "Model adapter, configured model and verified replay isolation are absent.",
        ),
        (
            RunMode.REMOTE_MODEL,
            "Hosted model re-execution",
            "Provider adapter, authorised budget and constrained inference broker are absent.",
        ),
    ]
    features = [
        (
            "recorder",
            "Recorder",
            "One capture layer for every REWIND mode.",
            "P2 capture and signing",
        ),
        (
            "forensics",
            "Forensics",
            "Investigate behaviour through controlled re-execution.",
            "P3 isolation and P4 experiments",
        ),
        (
            "ledger",
            "Ledger",
            "Preserve verifiable evidence and original-attack tests.",
            "P5 records",
        ),
        ("sentinel", "Sentinel", "Check proposed actions against a mandate.", "P7 enforcement"),
        ("preflight", "Preflight", "Rehearse failure in an owned sandbox.", "P8 evaluation"),
    ]
    return CapabilitiesResponse(
        modes=[
            ModeCapability(
                mode=mode,
                label=label,
                available=mode in {RunMode.PLAYBACK, RunMode.SIMULATED},
                maturity=FeatureMaturity.VERIFIED
                if mode in {RunMode.PLAYBACK, RunMode.SIMULATED}
                else FeatureMaturity.PLANNED,
                evidence_status=EvidenceStatus.FIXTURE_EFFECT_OBSERVED
                if mode == RunMode.SIMULATED
                else EvidenceStatus.UNAVAILABLE,
                reason=reason,
            )
            for mode, label, reason in modes
        ],
        features=[
            FeatureCapability(
                id=id_,
                label=label,
                description=description,
                available=False,
                maturity=FeatureMaturity.PLANNED,
                evidence_status=EvidenceStatus.UNAVAILABLE,
                reason=f"Requires {dependency}; not implemented yet.",
            )
            for id_, label, description, dependency in features
        ],
        mcp_sdk=f"mcp {version('mcp')}",
        mcp_protocol_revision=MCP_PROTOCOL_REVISION,
    )
