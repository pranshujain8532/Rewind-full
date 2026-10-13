import os
import subprocess
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from rewind_capture.store import CaptureStore
from rewind_sandbox.fixtures import canonical, worlds


def test_frame_and_lifetime_bounds(tmp_path, monkeypatch):
    monkeypatch.setenv("REWIND_DATA_DIR", str(tmp_path))
    command.upgrade(Config(str(Path(__file__).resolve().parents[1] / "alembic.ini")), "head")
    store = CaptureStore(tmp_path)
    world = tmp_path / "world.json"
    world.write_bytes(canonical(worlds()["clean"]))
    for session_id in ["frame", "lifetime"]:
        store.create_session(session_id, {"schema_version": "1.0", "mode": "simulated"})
        env = {
            **os.environ,
            "REWIND_CAPTURE_DIR": str(tmp_path),
            "REWIND_SESSION_ID": session_id,
            "REWIND_WORLD_FILE": str(world),
            "REWIND_OUTBOX_FILE": str(tmp_path / "outbox"),
            "REWIND_PROXY_LIFETIME": "1",
        }
        process = subprocess.Popen(
            [sys.executable, "-m", "rewind_capture.proxy", "ticket"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        if session_id == "frame":
            output, error = process.communicate(b"X" * 262145, timeout=6)
            assert not output and b"ValueError" in error
            assert b"XXXX" not in error
        else:
            process.wait(timeout=6)
            process.stdin.close()
        assert process.poll() is not None
