"""Create labelled capture controls only in an isolated browser-test directory."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

import anyio
from rewind_capture.store import CaptureStore
from rewind_eval.demo import controlled_world
from rewind_replay.container import ROOT
from rewind_sandbox.fixtures import worlds
from rewind_sandbox.runner import run_world


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    allowed = (ROOT / "artifacts/browser").resolve()
    if not directory.is_relative_to(allowed) or directory.name != "data":
        raise ValueError("Only an isolated artifacts/browser/*/data directory is permitted")
    capture = CaptureStore(directory)
    world = controlled_world(worlds()["single"])
    first = world.subject.inputs[0]
    hostile = '<img src=x onerror="globalThis.rewindHostileExecuted=true">\n' + first.text
    subject = world.subject.model_copy(
        update={"inputs": [first.model_copy(update={"text": hostile}), *world.subject.inputs[1:]]}
    )
    identity = str(uuid4())
    anyio.run(
        lambda: run_world(
            world.model_copy(update={"subject": subject}),
            directory / "sandbox-runs",
            capture_store=capture,
            run_id=identity,
        )
    )
    performance = str(uuid4())
    capture.create_session(
        performance,
        {
            "mode": "playback",
            "task_ref": "UI performance control: 100 stored events",
            "agent_binding": "labelled-ui-performance-control",
        },
    )
    for i in range(100):
        capture.append(
            performance,
            "ui_performance_control",
            {"ordinal": i, "seed": 2**64 - 1, "text": "Stored display control; not an agent trial"},
        )
    capture.engine.dispose()
    print(json.dumps({"hostile_session": identity, "performance_session": performance}))


if __name__ == "__main__":
    main()
