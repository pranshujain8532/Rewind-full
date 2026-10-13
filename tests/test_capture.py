import copy
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anyio
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from mcp import Client
from mcp.client.stdio import StdioServerParameters
from rewind_capture.store import CaptureStore
from rewind_capture.verify import verify
from rewind_sandbox.fixtures import canonical, worlds
from rewind_sandbox.runner import run_world
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("REWIND_DATA_DIR", str(tmp_path / "data"))
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    return CaptureStore(tmp_path / "data")


@pytest.fixture
def captured(store, tmp_path):
    async def execute():
        return await run_world(worlds()["redundant"], tmp_path / "runs", capture_store=store)

    result = anyio.run(execute)
    return store.export(result.run_id)


def test_complete_capture_dedup_and_protocol_ids(store, captured):
    checked = verify(captured, store.public)
    assert checked["valid"] and checked["capture_complete"]
    first, second = captured["occurrences"]
    assert first["id"] != second["id"] and first["source_uri"] != second["source_uri"]
    assert first["blob_digest"] == second["blob_digest"]
    requests, replies = set(), set()
    for event in captured["events"]:
        if event["body"]["kind"] != "protocol_frame":
            continue
        payload = captured["payloads"][event["body"]["payload_digest"]]
        message = payload["message"]
        if "id" in message:
            key = (event["body"]["source"], message["id"])
            (requests if payload["direction"] == "client_to_server" else replies).add(key)
    assert requests == replies and len(requests) >= 6


@pytest.mark.parametrize(
    "mutation", ["edit", "insert", "delete", "reorder", "blob", "origin", "seal", "metadata"]
)
def test_tampering_is_rejected(store, captured, mutation):
    changed = copy.deepcopy(captured)
    if mutation == "edit":
        changed["events"][0]["body"]["kind"] = "changed"
    elif mutation == "insert":
        changed["events"].insert(0, changed["events"][0])
    elif mutation == "delete":
        changed["events"].pop()
    elif mutation == "reorder":
        changed["events"][0], changed["events"][1] = changed["events"][1], changed["events"][0]
    elif mutation == "blob":
        changed["payloads"][next(iter(changed["payloads"]))] = {"different": True}
    elif mutation == "origin":
        changed["occurrences"][0]["source_uri"] = "forged://source"
    elif mutation == "seal":
        changed["seal"]["body"]["event_count"] -= 1
    else:
        changed["metadata"]["mode"] = "local_model"
    assert not verify(changed, store.public)["valid"]


def test_trust_anchor_and_missing_payloads(store, captured):
    wrong = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    captured["public_key"] = wrong.hex()
    assert not verify(captured, wrong)["valid"]
    assert verify(captured, store.public)["valid"]
    captured["payloads"] = {}
    checked = verify(captured, store.public)
    assert checked["valid"] and checked["missing_payloads"]
    assert not checked["capture_complete"]


def test_tool_only_capture_is_partial(store, tmp_path):
    async def execute():
        return await run_world(
            worlds()["clean"], tmp_path / "runs", capture_store=store, adapter_capture=False
        )

    result = anyio.run(execute)
    checked = verify(store.export(result.run_id), store.public)
    assert checked["valid"] and not checked["capture_complete"]


def test_transaction_order_encryption_and_immutability(store):
    store.create_session("ordering", {"schema_version": "1.0", "mode": "simulated"})
    with ThreadPoolExecutor(max_workers=4) as pool:
        events = list(
            pool.map(
                lambda index: store.append(
                    "ordering", "probe", {"index": index, "secret": "TEST_ONLY_PRIVATE_VALUE"}
                ),
                range(16),
            )
        )
    assert sorted(event["body"]["seq"] for event in events) == list(range(1, 17))
    store.seal("ordering", {"model_adapter": False, "completed": True})
    assert verify(store.export("ordering"), store.public)["valid"]
    with store.engine.connect() as connection:
        assert all(
            b"TEST_ONLY_PRIVATE_VALUE" not in row[0]
            for row in connection.execute(text("SELECT ciphertext FROM capture_blobs"))
        )
        assert all(
            "TEST_ONLY_PRIVATE_VALUE" not in row[0]
            for row in connection.execute(text("SELECT display FROM capture_events"))
        )
    with pytest.raises(ValueError):
        store.append("ordering", "late", {})
    with pytest.raises(IntegrityError):
        with store.engine.begin() as connection:
            connection.execute(text("UPDATE capture_events SET signature='x'"))


def test_concurrent_calls_errors_and_cancellation_forwarded(store, tmp_path):
    world_path = tmp_path / "world.json"
    world_path.write_bytes(canonical(worlds()["clean"]))
    store.create_session("wire", {"schema_version": "1.0", "mode": "simulated"})
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "rewind_capture.proxy", "ticket"],
        env={
            "REWIND_CAPTURE_DIR": str(store.directory),
            "REWIND_SESSION_ID": "wire",
            "REWIND_WORLD_FILE": str(world_path),
            "REWIND_OUTBOX_FILE": str(tmp_path / "outbox"),
        },
    )

    async def execute():
        async with Client(parameters, mode="2026-07-28", cache=None) as client:
            results = []

            async def call(ticket_id):
                results.append(await client.call_tool("ticket.read", {"ticket_id": ticket_id}))

            async with anyio.create_task_group() as group:
                group.start_soon(call, "TICK-4471")
                group.start_soon(call, "not-a-ticket")
            assert sorted(item.is_error for item in results) == [False, True]
            with anyio.move_on_after(0.1):
                await client.call_tool("ticket.read", {"ticket_id": "TICK-4471", "delay_ms": 800})
            response = await client.call_tool("ticket.read", {"ticket_id": "TICK-4471"})
            assert not response.is_error

    anyio.run(execute)
    store.seal("wire", {"model_adapter": False, "completed": True})
    bundle = store.export("wire")
    messages = [
        bundle["payloads"][event["body"]["payload_digest"]]["message"] for event in bundle["events"]
    ]
    assert any(message.get("method") == "notifications/cancelled" for message in messages)
    assert verify(bundle, store.public)["valid"]
