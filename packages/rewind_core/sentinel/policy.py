"""Rules use tool semantics and a trusted world, never fixture labels or caller costs."""

import hashlib
from datetime import datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from rewind_sandbox.fixtures import canonical, digest
from rewind_sandbox.schemas import Action, World

from .contracts import SignedMandate

DOMAIN = b"rewind:mandate:v1\0"


def sign(mandate, signer):
    public = signer.public_key().public_bytes_raw()
    return SignedMandate(
        mandate=mandate,
        signing_key_id=hashlib.sha256(public).hexdigest(),
        signature=signer.sign(DOMAIN + canonical(mandate)).hex(),
    )


def evaluate(
    signed: SignedMandate,
    public: bytes,
    action: Action,
    world: World,
    agent_id: str,
    session_id: str,
    now: datetime,
    dispatches: int,
    export_rows: int,
):
    """Return policy verdict, enforcement decision, reason and code-derived row cost."""
    m = signed.mandate
    try:
        if signed.signing_key_id != hashlib.sha256(public).hexdigest():
            raise ValueError("unknown_mandate_signer")
        Ed25519PublicKey.from_public_bytes(public).verify(
            bytes.fromhex(signed.signature), DOMAIN + canonical(m)
        )
    except (InvalidSignature, ValueError):
        return "undefined", "deny", "invalid_mandate_signature", 0
    if m.issuer != "owned-local-issuer":
        return "undefined", "deny", "untrusted_issuer", 0
    if (m.agent_id, m.session_id, m.world_digest) != (agent_id, session_id, digest(world)):
        return "undefined", "deny", "identity_or_world_binding_mismatch", 0
    if not m.not_before <= now < m.not_after:
        return "undefined", "deny", "mandate_not_current", 0
    args = action.arguments
    if action.tool in m.denied_tools:
        return "out_of_scope", "deny", "explicit_tool_denial", 0
    if action.tool not in m.allowed_tools:
        return "out_of_scope", "deny", "tool_outside_scope", 0
    schemas = {
        "ticket.read": {"ticket_id"},
        "files.read": {"file_id"},
        "mail.send_email": {"recipient", "attachment"},
    }
    if (
        action.tool not in schemas
        or set(args) != schemas[action.tool]
        or any(not isinstance(v, str) or not 1 <= len(v) <= 200 for v in args.values())
    ):
        return "undefined", "deny", "unsupported_tool_arguments", 0
    if action.tool == "ticket.read" and args["ticket_id"] != world.subject.ticket["id"]:
        return "out_of_scope", "deny", "ticket_outside_scope", 0
    rows = 0
    file_id = args.get("attachment", args.get("file_id"))
    if file_id is not None:
        if file_id in m.denied_data_ids:
            return "out_of_scope", "deny", "explicit_data_denial", 0
        file = world.files.get(file_id)
        if (
            file_id not in m.data_ids
            or file is None
            or file.get("classification") not in m.data_classes
        ):
            return "out_of_scope", "deny", "data_outside_scope", 0
        if action.tool == "mail.send_email":
            recipient = args["recipient"].casefold()
            if recipient in {r.casefold() for r in m.denied_recipients}:
                return "out_of_scope", "deny", "explicit_recipient_denial", 0
            if recipient not in {r.casefold() for r in m.recipients}:
                return "out_of_scope", "deny", "recipient_outside_scope", 0
            if not recipient.endswith(".example"):
                return "undefined", "deny", "non_synthetic_recipient_unsupported", 0
            rows = len(file["rows"])
    if dispatches >= m.max_dispatches or export_rows + rows > m.max_export_rows:
        return "out_of_scope", "deny", "mandate_budget_exhausted", rows
    if action.tool in m.high_impact_tools:
        return "in_scope", "hold", "authorised_high_impact_requires_approval", rows
    return "in_scope", "allow", "authorised_by_mandate", rows
