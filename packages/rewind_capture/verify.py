"""Verifier requires an independent trusted key; bundled keys confer no trust."""

import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from rewind_sandbox.fixtures import canonical, digest

from rewind_capture.store import MAX_EVENTS, ZERO


def verify(bundle: dict, trusted_public: bytes) -> dict:
    try:
        key = Ed25519PublicKey.from_public_bytes(trusted_public)
        key_id = hashlib.sha256(trusted_public).hexdigest()
        seal = bundle["seal"]
        if seal is None:
            raise ValueError("unsealed_session")
        body = seal["body"]
        if body["signing_key_id"] != key_id:
            raise ValueError("untrusted_signer")
        key.verify(bytes.fromhex(seal["signature"]), b"rewind:seal:v1\0" + canonical(body))
        if body["metadata_digest"] != digest(bundle["metadata"]):
            raise ValueError("metadata_modified")
        if body["occurrences_digest"] != digest(bundle["occurrences"]):
            raise ValueError("occurrence_provenance_modified")
        events = bundle["events"]
        if len(events) != body["event_count"] or len(events) > MAX_EVENTS:
            raise ValueError("event_count_mismatch")
        previous = ZERO
        identities = set()
        missing = []
        for seq, event in enumerate(events, 1):
            immutable = event["body"]
            if immutable["seq"] != seq or immutable["previous_hash"] != previous:
                raise ValueError("event_order_mismatch")
            if (
                immutable["session_id"] != body["session_id"]
                or immutable["signing_key_id"] != key_id
            ):
                raise ValueError("event_identity_mismatch")
            if immutable["event_id"] in identities:
                raise ValueError("duplicate_event")
            identities.add(immutable["event_id"])
            expected = hashlib.sha256(b"rewind:event:v1\0" + canonical(immutable)).hexdigest()
            if event["event_hash"] != expected:
                raise ValueError("event_modified")
            key.verify(
                bytes.fromhex(event["signature"]),
                b"rewind:event-signature:v1\0" + bytes.fromhex(expected),
            )
            payload_key = immutable["payload_digest"]
            payload = bundle.get("payloads", {}).get(payload_key)
            if payload is None:
                missing.append(payload_key)
            elif digest(payload) != payload_key:
                raise ValueError("payload_modified")
            previous = expected
        if (
            previous != body["head_hash"]
            or body["last_seq"] != len(events)
            or body["first_seq"] != 1
        ):
            raise ValueError("seal_head_mismatch")
        coverage = body["coverage"]
        required = {"initial_world", "tool_schema", "model_request", "model_response", "outcome"}
        if not required <= {event["body"]["kind"] for event in events}:
            coverage = {**coverage, "model_adapter": False}
        ready = (
            coverage.get("model_adapter", False)
            and not missing
            and coverage.get("completed", False)
        )
        return {
            "valid": True,
            "trusted_key_id": key_id,
            "missing_payloads": sorted(set(missing)),
            "capture_complete": bool(ready),
            "replay_readiness": "eligible_capture" if ready else "insufficient_capture",
            "limitations": [
                "Trusted-key tamper evidence, not truth, legal fault or external anchoring."
            ],
        }
    except (KeyError, ValueError, TypeError, InvalidSignature):
        return {
            "valid": False,
            "reason": "integrity_or_trust_failure",
            "capture_complete": False,
            "replay_readiness": "insufficient_capture",
        }
