"""Bounded, redacted projections of recorded facts for the session explorer."""

from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Depends, HTTPException, Path, Request
from pydantic import Field
from rewind_capture.store import MAX_CAPTURE_BYTES, MAX_EVENTS, CaptureStore, redact
from rewind_capture.verify import verify
from rewind_core.contracts import Contract
from rewind_eval.source import read_capture
from rewind_sandbox.fixtures import canonical
from sqlalchemy import text

from rewind_api.investigations import authenticated


class UnknownSession(KeyError):
    pass


class TraceEvent(Contract):
    id: str
    seq: int
    kind: str
    source: str
    time: str
    payload_digest: str
    payload: Any
    payload_text: str


class InputView(Contract):
    id: str
    target: str
    model_event_id: str
    origin: str
    source_uri: str
    blob_digest: str
    text: str
    display_truncated: bool


class SessionDetail(Contract):
    id: str
    sealed: bool
    metadata: dict[str, Any]
    capture_coverage: dict[str, Any]
    integrity: dict[str, Any]
    replay: dict[str, Any]
    events: list[TraceEvent] = Field(max_length=MAX_EVENTS)
    inputs: list[InputView] = Field(max_length=16)
    outcome: dict[str, Any] | None
    limitations: list[str]


def session_detail(directory, engine, identity):
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT sealed FROM sessions WHERE id=:id"), {"id": identity}
        ).first()
        if not row:
            raise UnknownSession(identity)
        count, size = connection.execute(
            text(
                "SELECT count(*),coalesce(sum(length(b.ciphertext)),0) "
                "FROM capture_events e LEFT JOIN capture_blobs b "
                "ON b.digest=json_extract(e.body,'$.payload_digest') WHERE e.session_id=:id"
            ),
            {"id": identity},
        ).one()
    if count > MAX_EVENTS or size > MAX_CAPTURE_BYTES:
        raise ValueError("capture_bounds_exceeded")
    # Opening an explorer must never create a signing or payload key.
    store = CaptureStore.__new__(CaptureStore)
    store.directory, store.engine = directory, engine
    store.cipher = AESGCM((directory / "keys/payload.key").read_bytes())
    bundle = store.export(identity)
    checked = verify(bundle, (directory / "keys/trusted-public.ed25519").read_bytes())
    replay = {"eligible": False, "reason": "Unsupported or incomplete capture"}
    if checked["valid"] and checked["capture_complete"]:
        try:
            read_capture(directory, identity)
            replay = {"eligible": True, "reason": "Complete owned simulator capture"}
        except (ValueError, OSError, KeyError, StopIteration):
            replay["reason"] = "Mode or adapter contract is unsupported for investigation"
    payloads = bundle["payloads"]
    events = []
    input_text = {}
    outcome = None
    for event in bundle["events"]:
        body = event["body"]
        payload = payloads.get(body["payload_digest"])
        events.append(
            TraceEvent(
                id=body["event_id"],
                seq=body["seq"],
                kind=body["kind"],
                source=body["source"],
                time=body["occurred_at"],
                payload_digest=body["payload_digest"],
                payload=redact(payload),
                payload_text=canonical(redact(payload)).decode(),
            )
        )
        if body["kind"] == "model_request" and isinstance(payload, dict):
            for item in payload.get("request", {}).get("inputs", []):
                input_text[(body["event_id"], item["occurrence_id"])] = item["text"]
        if body["kind"] == "outcome" and isinstance(payload, dict):
            outcome = {
                key: payload.get(key)
                for key in ("harmful_action_attempted", "harmful_action_executed", "task_success")
            }
    inputs = []
    for occurrence in bundle["occurrences"]:
        content = input_text.get(
            (occurrence["model_call_id"], occurrence["fixture_occurrence"]), ""
        )
        inputs.append(
            InputView(
                id=occurrence["id"],
                target=occurrence["fixture_occurrence"],
                model_event_id=occurrence["model_call_id"],
                origin=occurrence["origin"],
                source_uri=redact(occurrence["source_uri"]),
                blob_digest=occurrence["blob_digest"],
                text=redact(content),
                display_truncated=len(content) > 2000,
            )
        )
    coverage = (bundle.get("seal") or {}).get("body", {}).get("coverage", {})
    return SessionDetail(
        id=identity,
        sealed=bool(row.sealed),
        metadata=redact(bundle["metadata"]),
        capture_coverage={**coverage, "complete": checked["capture_complete"]},
        integrity={
            "status": "verified_local_key" if checked["valid"] else "invalid_or_unsealed",
            "reason": checked.get("reason", "Signature checked against local pinned key"),
            "trust": "Local pinned public key; no external trust anchor",
        },
        replay=replay,
        events=events,
        inputs=inputs,
        outcome=outcome,
        limitations=[
            "Display is redacted and bounded; use the signed bundle for integrity verification.",
            "Observable input relationships do not prove causes or individual blame.",
            "Partial capture, unsupported modes and unknown origin identity remain visible.",
        ],
    )


def install_routes(app):
    @app.get(
        "/api/sessions/{identity}",
        response_model=SessionDetail,
        dependencies=[Depends(authenticated)],
    )
    def detail(request: Request, identity: str = Path(min_length=1, max_length=100)):
        try:
            return session_detail(
                request.app.state.jobs.directory, request.app.state.jobs.engine, identity
            )
        except UnknownSession as error:
            raise HTTPException(404, "Unknown session") from error
        except (ValueError, OSError, InvalidTag, KeyError, TypeError, RecursionError) as error:
            raise HTTPException(
                409, "Capture unavailable or corrupt; no evidence projected"
            ) from error
