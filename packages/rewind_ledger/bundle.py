"""Bounded, database-independent verification with an explicitly supplied trust key."""

import hashlib
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from rewind_capture.verify import verify as verify_trace
from rewind_sandbox.fixtures import canonical, digest

from rewind_ledger.contracts import EvidenceRecord, VerificationResult
from rewind_ledger.evidence import project

MAX_BUNDLE_BYTES = 8_000_000
MAX_DEPTH = 40
DOMAIN = b"rewind:ledger-bundle:v1\0"


def bounded_json(raw: bytes) -> dict:
    if len(raw) > MAX_BUNDLE_BYTES:
        raise ValueError("bundle_too_large")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result

    def invalid_constant(_value):
        raise ValueError("non_finite_json")

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise ValueError("corrupt_json") from None
    stack = [(value, 0)]
    objects = 0
    while stack:
        node, depth = stack.pop()
        objects += 1
        if depth > MAX_DEPTH or objects > 200000:
            raise ValueError("bundle_structure_bound")
        if isinstance(node, dict):
            stack.extend((v, depth + 1) for v in node.values())
        elif isinstance(node, list):
            stack.extend((v, depth + 1) for v in node)
    if not isinstance(value, dict):
        raise ValueError("bundle_shape_invalid")
    return value


def sign_bundle(format_: str, report: dict, artifacts: dict, signer: Ed25519PrivateKey) -> dict:
    manifest = {
        "schema_version": "1.0",
        "format": format_,
        "report_digest": digest(report),
        "artifacts": {k: digest(v) for k, v in artifacts.items()},
        "signing_key_id": hashlib.sha256(signer.public_key().public_bytes_raw()).hexdigest(),
    }
    bundle = {
        "schema_version": "1.0",
        "format": format_,
        "report": report,
        "artifacts": artifacts,
        "manifest": manifest,
        "signature": signer.sign(DOMAIN + canonical(manifest)).hex(),
    }
    if len(canonical(bundle)) > MAX_BUNDLE_BYTES:
        raise ValueError("bundle_too_large")
    return bundle


def verify_bundle(bundle: dict, trusted_public: bytes) -> VerificationResult:
    key_id = None
    trusted = False
    try:
        if len(trusted_public) != 32:
            raise ValueError("trusted_key_invalid")
        key_id = hashlib.sha256(trusted_public).hexdigest()
        if set(bundle) != {
            "schema_version",
            "format",
            "report",
            "artifacts",
            "manifest",
            "signature",
        }:
            raise ValueError("bundle_shape_invalid")
        if bundle["schema_version"] != "1.0" or bundle["manifest"]["schema_version"] != "1.0":
            raise ValueError("unknown_schema")
        if bundle["format"] not in {"rewind-evidence-v1", "rewind-regression-v1"}:
            raise ValueError("unknown_schema")
        manifest = bundle["manifest"]
        if manifest["signing_key_id"] != key_id:
            raise ValueError("untrusted_signer")
        trusted = True
        expected = {
            "schema_version": "1.0",
            "format": bundle["format"],
            "report_digest": digest(bundle["report"]),
            "artifacts": {k: digest(v) for k, v in bundle["artifacts"].items()},
            "signing_key_id": key_id,
        }
        if manifest != expected:
            raise ValueError("artifact_digest_mismatch")
        Ed25519PublicKey.from_public_bytes(trusted_public).verify(
            bytes.fromhex(bundle["signature"]), DOMAIN + canonical(manifest)
        )
        if bundle["format"] == "rewind-regression-v1":
            from rewind_ledger.regression import verify_regression

            complete, eligible = verify_regression(bundle, trusted_public)
        else:
            if set(bundle["artifacts"]) != {"trace", "investigation"}:
                raise ValueError("artifact_set_invalid")
            report = EvidenceRecord.model_validate(bundle["report"])
            trace = bundle["artifacts"]["trace"]
            checked = verify_trace(trace, trusted_public)
            if not checked["valid"]:
                raise ValueError("trace_integrity_invalid")
            projected, eligible = project(
                report.id,
                report.created_at,
                trace,
                bundle["artifacts"]["investigation"],
                trusted_public,
            )
            if report != projected:
                raise ValueError("report_fact_mismatch")
            complete = projected.replay_coverage["complete"]
        return VerificationResult(
            integrity_valid=True,
            trusted=True,
            evidence_complete=complete,
            regression_eligible=eligible,
            reason="verified_under_supplied_trust_key",
            signing_key_id=key_id,
        )
    except InvalidSignature:
        reason = "signature_invalid"
    except (
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        OverflowError,
        RecursionError,
    ) as error:
        # Do not echo malformed content, exceptions or sensitive supplied values.
        codes = {
            "untrusted_signer",
            "unknown_schema",
            "artifact_digest_mismatch",
            "trace_integrity_invalid",
            "report_fact_mismatch",
            "bundle_shape_invalid",
            "source_evidence_invalid",
            "original_attack_binding_invalid",
            "regression_fact_mismatch",
            "artifact_set_invalid",
            "trusted_key_invalid",
        }
        reason = str(error) if str(error) in codes else "corrupt_or_unsupported_bundle"
    return VerificationResult(
        integrity_valid=False,
        trusted=trusted,
        evidence_complete=False,
        regression_eligible=False,
        reason=reason,
        signing_key_id=key_id,
    )
