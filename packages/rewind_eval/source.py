"""Read an existing capture under the local pinned trust anchor; never create keys."""

from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rewind_capture.store import CaptureStore
from rewind_capture.verify import verify
from rewind_core.contracts import MCP_PROTOCOL_REVISION, RunMode
from rewind_core.storage import make_engine
from rewind_sandbox.fixtures import digest
from rewind_sandbox.outcomes import PREDICATE_VERSION
from rewind_sandbox.schemas import World

from rewind_eval.tool_contract import supported_schemas


def read_capture(directory: Path, session_id: str) -> tuple[dict, World, bool]:
    # CaptureStore's normal constructor owns key creation. Investigation is read-only.
    public = (directory / "keys/trusted-public.ed25519").read_bytes()
    store = CaptureStore.__new__(CaptureStore)
    store.directory = directory
    store.engine = make_engine(directory)
    store.cipher = AESGCM((directory / "keys/payload.key").read_bytes())
    try:
        bundle = store.export(session_id)
    finally:
        store.engine.dispose()
    checked = verify(bundle, public)
    if not checked["valid"] or not checked["capture_complete"]:
        raise ValueError("unsupported_replay: untrusted, incomplete or unavailable capture")
    payloads = bundle["payloads"]
    world = World.model_validate(
        next(
            payloads[e["body"]["payload_digest"]]
            for e in bundle["events"]
            if e["body"]["kind"] == "initial_world"
        )
    )
    metadata = bundle["metadata"]
    requests = [
        payloads[e["body"]["payload_digest"]]
        for e in bundle["events"]
        if e["body"]["kind"] == "model_request"
    ]
    coverage = bundle["seal"]["body"]["coverage"]
    if not requests or not supported_schemas(requests[0].get("tool_schemas", {}), world.version):
        raise ValueError("unsupported_replay: unsupported or changed owned tool schemas")
    if (
        metadata.get("mode") != RunMode.SIMULATED
        or metadata.get("model") != "instruction-dsl-v1"
        or metadata.get("agent_binding") != "owned-demo-agent"
        or metadata.get("world_digest") != digest(world)
        or coverage.get("state") != "full_initial_world"
        or coverage.get("memory") != "stateless_simulator"
        or coverage.get("protocol") != MCP_PROTOCOL_REVISION
        or len(requests) != 1
        or requests[0]["request"] != world.subject.model_dump(mode="json")
        or requests[0].get("response_cache") is not False
    ):
        raise ValueError("unsupported_replay: configuration or adapter contract mismatch")
    configurations = {
        digest(
            {
                "simulator": "instruction-dsl-v1",
                "trust_external": trust,
                "predicate": PREDICATE_VERSION,
                "protocol": MCP_PROTOCOL_REVISION,
            }
        ): trust
        for trust in (True, False)
    }
    if metadata.get("config_digest") not in configurations:
        raise ValueError("unsupported_replay: unknown subject configuration")
    return bundle, world, configurations[metadata["config_digest"]]
