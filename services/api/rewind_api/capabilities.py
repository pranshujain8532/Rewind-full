"""Explicit feature matrix; environment hints never enable unfinished code."""

import json
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
    from rewind_replay.container import MANIFEST

    isolated = False
    preflight_ready = False
    try:
        isolated = json.loads(MANIFEST.read_bytes()).get("isolation_verified") is True
        preflight_ready = (
            json.loads(MANIFEST.read_bytes()).get("preflight_runtime_version")
            == "preflight-fixed-v1"
        )
    except (OSError, ValueError):
        pass
    modes = [
        (
            RunMode.PLAYBACK,
            "Recorded playback",
            "CLI reads an explicit saved recording; no fresh inference.",
        ),
        (
            RunMode.SIMULATED,
            "Sandbox simulator",
            "Fresh instruction DSL in a verified no-network container when configured; no LLM.",
        ),
        (
            RunMode.LOCAL_MODEL,
            "Local model re-execution",
            "Model adapter, configured model and verified replay isolation are absent.",
        ),
        (
            RunMode.REMOTE_MODEL,
            "Hosted model (CLI only)",
            "Gemini's budgeted exploratory CLI makes fresh decisions in owned mocks. "
            "Invalid or unsupported tool proposals remain invalid. API/Forensics real-model "
            "eligibility is unsupported; CLI inference needs an explicit billing declaration.",
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
                else FeatureMaturity.EXPERIMENTAL
                if mode == RunMode.REMOTE_MODEL
                else FeatureMaturity.PLANNED,
                evidence_status=EvidenceStatus.FIXTURE_EFFECT_OBSERVED
                if mode == RunMode.SIMULATED
                else EvidenceStatus.EXPLORATORY
                if mode == RunMode.REMOTE_MODEL
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
                available=id_ in {"recorder", "ledger", "sentinel"}
                or (
                    id_ in {"forensics", "preflight"}
                    and isolated
                    and (id_ != "preflight" or preflight_ready)
                ),
                maturity=FeatureMaturity.VERIFIED
                if id_ in {"recorder", "ledger", "sentinel", "preflight"}
                else (
                    FeatureMaturity.IMPLEMENTED
                    if id_ in {"forensics", "sentinel", "preflight"}
                    else FeatureMaturity.PLANNED
                ),
                evidence_status=EvidenceStatus.UNAVAILABLE,
                reason=(
                    "Signed, encrypted owned-stdio capture with explicit simulator adapter; "
                    "other integrations unsupported."
                    if id_ == "recorder"
                    else "P4 simulator discovery, fixed plans and durable jobs. "
                    "Requires locally verified replay isolation; real confirmation unsupported."
                    if id_ == "forensics"
                    else "Signed stored-fact evidence, independent trusted-key verification and "
                    "original-attack simulator regressions. Governance mapping pending."
                    if id_ == "ledger"
                    else "Signed mandates, exact single-use approvals and atomic local mock tools. "
                    "Owned stateless simulator only; generic MCP and real agents unsupported."
                    if id_ == "sentinel"
                    else "Fixed reviewed ticket-comment and mock-file suites in isolation; "
                    "owned target only. Requires rebuilt/probed P8 runtime. "
                    "Generation/classifier absent."
                    if id_ == "preflight"
                    else f"Requires {dependency}; not implemented yet."
                ),
            )
            for id_, label, description, dependency in features
        ],
        mcp_sdk=f"mcp {version('mcp')}",
        mcp_protocol_revision=MCP_PROTOCOL_REVISION,
        replay_isolation="verified_no_network" if isolated else "unavailable",
    )
