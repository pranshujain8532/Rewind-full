"""Independent trusted-key verification; no API, database or key creation."""

import argparse
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from rewind_sandbox.fixtures import canonical

from .contracts import SignedMandate
from .policy import DOMAIN
from .store import EVENT_DOMAIN


def verify(bundle, public):
    key = Ed25519PublicKey.from_public_bytes(public)
    manifest = bundle["manifest"]
    key.verify(
        bytes.fromhex(bundle["signature"]), b"rewind:sentinel-manifest:v1\0" + canonical(manifest)
    )
    mandate = SignedMandate.model_validate(manifest["mandate"])
    fingerprint = hashlib.sha256(public).hexdigest()
    if (
        mandate.signing_key_id != fingerprint
        or mandate.mandate.session_id != manifest["session_id"]
    ):
        raise ValueError("untrusted_mandate_binding")
    key.verify(bytes.fromhex(mandate.signature), DOMAIN + canonical(mandate.mandate))
    head, dispatches, rows = "0" * 64, set(), 0
    for seq, event in enumerate(manifest["events"], 1):
        body = event["body"]
        if (body["seq"], body["previous_hash"], body["session_id"], body["signing_key_id"]) != (
            seq,
            head,
            manifest["session_id"],
            fingerprint,
        ):
            raise ValueError("invalid_event_chain")
        hashed = hashlib.sha256(EVENT_DOMAIN + canonical(body)).hexdigest()
        if hashed != event["event_hash"]:
            raise ValueError("event_digest_mismatch")
        key.verify(bytes.fromhex(event["signature"]), EVENT_DOMAIN + bytes.fromhex(hashed))
        if body["type"] == "dispatched":
            action = body["data"]
            if action["id"] in dispatches:
                raise ValueError("duplicate_dispatch")
            dispatches.add(action["id"])
            rows += action["result"].get("synthetic_rows", 0)
        head = hashed
    if (len(manifest["events"]), head, len(dispatches), rows) != (
        manifest["event_count"],
        manifest["head"],
        manifest["dispatch_count"],
        manifest["exported_rows"],
    ):
        raise ValueError("manifest_count_mismatch")
    return {
        "valid": True,
        "events": len(manifest["events"]),
        "dispatches": len(dispatches),
        "trust": "Supplied public key; authenticity does not establish truth or external identity.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--trusted-public-key", type=Path, required=True)
    args = parser.parse_args()
    try:
        from rewind_ledger.bundle import MAX_BUNDLE_BYTES, bounded_json

        if args.bundle.stat().st_size > MAX_BUNDLE_BYTES:
            raise ValueError("bundle_too_large")
        raw = args.bundle.read_bytes()
        result = verify(bounded_json(raw), args.trusted_public_key.read_bytes())
    except Exception as error:
        print(json.dumps({"valid": False, "reason": type(error).__name__}))
        raise SystemExit(1) from error
    print(json.dumps(result))


if __name__ == "__main__":
    main()
