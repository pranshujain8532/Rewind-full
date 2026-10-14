"""Python-owned canonical JSON, AEAD content and transaction-ordered signed events."""

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rewind_core.storage import make_engine
from rewind_sandbox.fixtures import canonical, digest
from sqlalchemy import text

MAX_PAYLOAD = 512000
MAX_EVENTS = 512
MAX_CAPTURE_BYTES = 4_000_000
ZERO = "0" * 64


def redact(value):
    if isinstance(value, dict):
        return {
            key: "[redacted]"
            if any(term in key.casefold() for term in ("password", "secret", "token", "credential"))
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value[:32]]
    if isinstance(value, str):
        import re

        return re.sub(r"[\w.+-]+@[\w.-]+", "[email]", value[:2000])
    return value


class CaptureStore:
    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.engine = make_engine(self.directory)
        keys = self.directory / "keys"
        keys.mkdir(exist_ok=True)
        for name, length in [("signing.key", 32), ("payload.key", 32)]:
            path = keys / name
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                continue
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(os.urandom(length))
        self.signer = Ed25519PrivateKey.from_private_bytes((keys / "signing.key").read_bytes())
        self.public = self.signer.public_key().public_bytes_raw()
        self.key_id = hashlib.sha256(self.public).hexdigest()
        self.cipher = AESGCM((keys / "payload.key").read_bytes())
        (keys / "trusted-public.ed25519").write_bytes(self.public)

    def create_session(self, session_id: str, metadata: dict) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text("INSERT INTO sessions(id, metadata, sealed) VALUES(:id,:meta,0)"),
                {"id": session_id, "meta": canonical(metadata).decode()},
            )

    def append(self, session_id: str, kind: str, payload, source: str = "adapter") -> dict:
        plaintext = canonical(payload)
        if len(plaintext) > MAX_PAYLOAD:
            raise ValueError("Capture payload bound exceeded")
        payload_digest = hashlib.sha256(plaintext).hexdigest()
        nonce = os.urandom(12)
        ciphertext = nonce + self.cipher.encrypt(nonce, plaintext, payload_digest.encode())
        with self.engine.connect() as connection:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            session = connection.execute(
                text("SELECT sealed FROM sessions WHERE id=:id"), {"id": session_id}
            ).first()
            if session is None or session.sealed:
                raise ValueError("Missing or sealed session")
            used = connection.scalar(
                text(
                    "SELECT coalesce(sum(length(b.ciphertext)),0) FROM capture_events e "
                    "JOIN capture_blobs b ON b.digest=json_extract(e.body,'$.payload_digest') "
                    "WHERE e.session_id=:id"
                ),
                {"id": session_id},
            )
            if used + len(ciphertext) > MAX_CAPTURE_BYTES:
                raise ValueError("Capture byte budget exceeded")
            previous = connection.execute(
                text(
                    "SELECT seq,event_hash FROM capture_events WHERE session_id=:id "
                    "ORDER BY seq DESC LIMIT 1"
                ),
                {"id": session_id},
            ).first()
            seq = previous.seq + 1 if previous else 1
            if seq > MAX_EVENTS:
                raise ValueError("Capture event bound exceeded")
            body = {
                "schema_version": "1.0",
                "session_id": session_id,
                "event_id": str(uuid4()),
                "seq": seq,
                "kind": kind,
                "source": source,
                "occurred_at": datetime.now(UTC).isoformat(),
                "payload_digest": payload_digest,
                "previous_hash": previous.event_hash if previous else ZERO,
                "signing_key_id": self.key_id,
            }
            event_hash = hashlib.sha256(b"rewind:event:v1\0" + canonical(body)).hexdigest()
            signature = self.signer.sign(
                b"rewind:event-signature:v1\0" + bytes.fromhex(event_hash)
            ).hex()
            connection.execute(
                text(
                    "INSERT OR IGNORE INTO capture_blobs(digest,ciphertext) VALUES(:digest,:cipher)"
                ),
                {"digest": payload_digest, "cipher": ciphertext},
            )
            connection.execute(
                text(
                    "INSERT INTO capture_events(session_id,seq,event_id,"
                    "event_hash,body,signature,display) "
                    "VALUES(:id,:seq,:eid,:hash,:body,:sig,:display)"
                ),
                {
                    "id": session_id,
                    "seq": seq,
                    "eid": body["event_id"],
                    "hash": event_hash,
                    "body": canonical(body).decode(),
                    "sig": signature,
                    "display": canonical(redact(payload)).decode(),
                },
            )
            connection.commit()
        return {"body": body, "event_hash": event_hash, "signature": signature}

    def capture_input(
        self,
        session_id: str,
        request,
        schemas: dict,
        *,
        model_requested: str = "instruction-dsl-v1",
        provider_request: dict | None = None,
        provider_configuration: dict | None = None,
    ) -> None:
        envelope = {
            "schema_version": "1.0",
            "request": request.model_dump(mode="json"),
            "model_requested": model_requested,
            "tool_schemas": schemas,
            "memory": {"stateless": True},
            "response_cache": False,
            "tool_schema_role": "framework configuration for fixed DSL tool calls",
        }
        if provider_request is not None:
            envelope.update(
                provider="gemini",
                provider_request=provider_request,
                provider_configuration=provider_configuration,
                tool_schema_role="owned mock action proposals in constrained JSON",
            )
        event = self.append(session_id, "model_request", envelope)
        for position, item in enumerate(request.inputs):
            blob = self.append(session_id, "input_occurrence", {"text": item.text})
            with self.engine.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO chunk_occurrences(id,session_id,fixture_occurrence,position,"
                        "blob_digest,source_uri,origin,model_call_id) "
                        "VALUES(:id,:session,:fixture,:position,:blob,:uri,:origin,:model)"
                    ),
                    {
                        "id": str(uuid4()),
                        "session": session_id,
                        "fixture": item.occurrence_id,
                        "position": position,
                        "blob": blob["body"]["payload_digest"],
                        "uri": item.source_uri,
                        "origin": item.origin,
                        "model": event["body"]["event_id"],
                    },
                )

    def seal(self, session_id: str, coverage: dict) -> dict:
        with self.engine.connect() as connection:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            row = connection.execute(
                text("SELECT metadata,sealed FROM sessions WHERE id=:id"), {"id": session_id}
            ).one()
            if row.sealed:
                raise ValueError("Already sealed")
            events = connection.execute(
                text("SELECT seq,event_hash FROM capture_events WHERE session_id=:id ORDER BY seq"),
                {"id": session_id},
            ).all()
            body = {
                "schema_version": "1.0",
                "session_id": session_id,
                "first_seq": 1,
                "last_seq": len(events),
                "event_count": len(events),
                "head_hash": events[-1].event_hash if events else ZERO,
                "metadata_digest": digest(json.loads(row.metadata)),
                "coverage": coverage,
                "signing_key_id": self.key_id,
                "occurrences_digest": digest(
                    [
                        dict(item)
                        for item in connection.execute(
                            text(
                                "SELECT * FROM chunk_occurrences WHERE session_id=:id "
                                "ORDER BY position"
                            ),
                            {"id": session_id},
                        ).mappings()
                    ]
                ),
            }
            seal = {
                "body": body,
                "signature": self.signer.sign(b"rewind:seal:v1\0" + canonical(body)).hex(),
            }
            connection.execute(
                text("UPDATE sessions SET sealed=1,seal=:seal WHERE id=:id"),
                {"id": session_id, "seal": canonical(seal).decode()},
            )
            connection.commit()
        return seal

    def export(self, session_id: str, include_payloads: bool = True) -> dict:
        with self.engine.connect() as connection:
            row = connection.execute(
                text("SELECT metadata,seal FROM sessions WHERE id=:id"), {"id": session_id}
            ).one()
            events = connection.execute(
                text(
                    "SELECT body,event_hash,signature FROM capture_events WHERE session_id=:id "
                    "ORDER BY seq"
                ),
                {"id": session_id},
            ).all()
            payloads = {}
            output = []
            for event in events:
                body = json.loads(event.body)
                output.append(
                    {"body": body, "event_hash": event.event_hash, "signature": event.signature}
                )
                key = body["payload_digest"]
                if include_payloads:
                    cipher = connection.scalar(
                        text("SELECT ciphertext FROM capture_blobs WHERE digest=:key"), {"key": key}
                    )
                    payloads[key] = (
                        json.loads(self.cipher.decrypt(cipher[:12], cipher[12:], key.encode()))
                        if cipher
                        else None
                    )
            occurrences = [
                dict(item)
                for item in connection.execute(
                    text("SELECT * FROM chunk_occurrences WHERE session_id=:id ORDER BY position"),
                    {"id": session_id},
                ).mappings()
            ]
        return {
            "schema_version": "1.0",
            "metadata": json.loads(row.metadata),
            "seal": json.loads(row.seal) if row.seal else None,
            "events": output,
            "payloads": payloads,
            "occurrences": occurrences,
        }
