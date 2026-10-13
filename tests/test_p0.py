"""P0 risks: readiness honesty, migration repeatability and closed capabilities."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from rewind_api.app import create_app
from rewind_core.contracts import (
    MCP_PROTOCOL_REVISION,
    CapabilitiesResponse,
    HealthResponse,
    RunMode,
)
from rewind_core.storage import make_engine
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def migrated_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("REWIND_DATA_DIR", str(tmp_path))
    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    return tmp_path


def test_http_contract_and_empty_capabilities(migrated_directory, monkeypatch):
    # Even a configured-looking environment cannot enable absent adapters.
    monkeypatch.setenv("REWIND_MODEL", "not-a-configured-model")
    monkeypatch.setenv("REWIND_REMOTE_BUDGET", "999")
    with TestClient(create_app(migrated_directory), base_url="http://127.0.0.1") as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        health = HealthResponse.model_validate(response.json())
        assert health.ready
        assert health.database.migration_revision == "0002_capture"
        assert health.database.journal_mode == "wal"
        assert set(health.available_modes) == {RunMode.SIMULATED, RunMode.PLAYBACK}
        matrix = CapabilitiesResponse.model_validate(client.get("/api/capabilities").json())
        assert {mode.mode for mode in matrix.modes} == set(RunMode)
        assert all(mode.reason for mode in matrix.modes)
        assert all(
            not mode.available
            for mode in matrix.modes
            if mode.mode in {RunMode.LOCAL_MODEL, RunMode.REMOTE_MODEL}
        )
        assert all(not feature.available for feature in matrix.features if feature.id != "recorder")
        assert next(feature for feature in matrix.features if feature.id == "recorder").available
        assert matrix.mcp_protocol_revision == MCP_PROTOCOL_REVISION
        assert matrix.replay_isolation == "unavailable"
        assert client.get("/openapi.json").status_code == 200


def test_unmigrated_database_is_not_ready(tmp_path):
    with TestClient(create_app(tmp_path), base_url="http://localhost") as client:
        response = client.get("/api/health")
        assert response.status_code == 503
        assert response.json()["database"]["reason"] == "migration_required"
        assert set(response.json()["available_modes"]) == {"simulated", "playback"}
        assert client.get("/api/capabilities").status_code == 200


def test_broken_schema_never_reports_ready(migrated_directory):
    engine = make_engine(migrated_directory)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE app_metadata"))
    engine.dispose()
    with TestClient(create_app(migrated_directory), base_url="http://localhost") as client:
        response = client.get("/api/health")
        assert response.status_code == 503
        assert response.json()["database"]["reason"] == "database_unavailable"
        assert response.json()["ready"] is False


def test_non_local_host_is_rejected(migrated_directory):
    with TestClient(create_app(migrated_directory), base_url="http://localhost") as client:
        assert client.get("/api/health", headers={"host": "untrusted.example"}).status_code == 400


def test_mcp_selected_revision_in_process():
    # SDK compatibility check only; not a recorder, isolation or stdio coverage claim.
    import anyio
    from mcp import Client
    from mcp.server import MCPServer

    server = MCPServer("REWIND P0 SDK smoke")

    @server.tool()
    def protocol_probe() -> str:
        return MCP_PROTOCOL_REVISION

    async def probe():
        async with Client(server, mode=MCP_PROTOCOL_REVISION, cache=None) as client:
            assert client.protocol_version == MCP_PROTOCOL_REVISION
            result = await client.call_tool("protocol_probe", {})
            assert not result.is_error
            assert MCP_PROTOCOL_REVISION in str(result.content)

    anyio.run(probe)
