import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from rewind_core.contracts import RunMode
from rewind_replay.container import MANIFEST, execute, verify_isolation
from rewind_replay.contracts import BatchRequest, Intervention, TrialRequest
from rewind_replay.runtime import StrictResolver, UnsupportedReplay, run_trial
from rewind_sandbox.fixtures import digest, worlds


def test_strict_occurrence_state_schema_and_unknown_branches():
    arguments = {"file_id": "customers"}
    rows = [
        {
            "tool": "files.read",
            "schema_digest": "schema-v1",
            "arguments_digest": digest(arguments),
            "occurrence": index,
            "environment_state_digest": state,
            "response": {"value": index},
        }
        for index, state in [(0, "before"), (1, "after")]
    ]
    resolver = StrictResolver(rows)
    assert resolver.read("files.read", "schema-v1", arguments, 0, "before") == {"value": 0}
    assert resolver.read("files.read", "schema-v1", arguments, 1, "after") == {"value": 1}
    for tool, schema, args, occurrence, state in [
        ("files.read", "schema-v2", arguments, 0, "before"),
        ("files.read", "schema-v1", arguments, 0, "after"),
        ("files.read", "schema-v1", {"file_id": "../../host/secret"}, 0, "before"),
        ("mail.send_email", "schema-v1", arguments, 0, "before"),
    ]:
        with pytest.raises(UnsupportedReplay):
            resolver.read(tool, schema, args, occurrence, state)


def test_real_modes_and_playback_are_not_simulator_trials():
    for mode in [RunMode.PLAYBACK, RunMode.LOCAL_MODEL, RunMode.REMOTE_MODEL]:
        result = run_trial(TrialRequest(world=worlds()["single"], mode=mode))
        assert result["validity"] == "invalid" and not result["fresh_decision"]
        assert result["evidence_status"] == "unsupported_replay"


def test_strict_downstream_read_never_falls_back():
    world = worlds()["single"]
    state = digest({"world": world.model_dump(mode="json"), "outbox": []})
    ticket = {
        "tool": "ticket.read",
        "schema_digest": "ticket-v1",
        "arguments_digest": digest({"ticket_id": world.subject.ticket["id"]}),
        "occurrence": 0,
        "environment_state_digest": state,
        "response": {
            "ticket": world.subject.ticket,
            "inputs": [item.model_dump(mode="json") for item in world.subject.inputs],
        },
    }
    request = TrialRequest(
        world=world,
        strict_calls=[ticket],
        strict_schemas={"ticket": "ticket-v1", "files": "files-v1"},
    )
    result = run_trial(request)
    assert result["validity"] == "invalid" and result["fresh_decision"]
    assert "harmful_action_executed" not in result
    file = {
        "tool": "files.read",
        "schema_digest": "files-v1",
        "arguments_digest": digest({"file_id": "customers"}),
        "occurrence": 1,
        "environment_state_digest": state,
        "response": world.files["customers"],
    }
    result = run_trial(request.model_copy(update={"strict_calls": [ticket, file]}))
    assert result["validity"] == "valid" and result["harmful_action_executed"]


def test_actual_isolated_interventions_and_private_state(tmp_path):
    # Requires explicit setup/probe first; never silently substitutes host execution.
    assert MANIFEST.exists(), "Run rewind_replay.cli setup and probe before this gate"
    host_marker = tmp_path / "rewind-host-secret.txt"
    host_marker.write_text("HOST_ONLY_SYNTHETIC_MARKER")
    probe = verify_isolation()
    assert probe["passed"] and all(probe["checks"].values())
    source = worlds()["single"]
    before = digest(source)
    requests = [
        TrialRequest(world=source),
        TrialRequest(world=source, intervention=Intervention(kind="remove", targets=["comment-0"])),
        TrialRequest(
            world=source, intervention=Intervention(kind="neutral_replace", targets=["comment-0"])
        ),
        TrialRequest(world=source),
        TrialRequest(
            world=source,
            intervention=Intervention(kind="remove_required_fact", targets=["ticket:issue"]),
        ),
        TrialRequest(
            world=worlds()["redundant"],
            intervention=Intervention(kind="remove", targets=["comment-0"]),
        ),
        TrialRequest(
            world=worlds()["redundant"],
            intervention=Intervention(kind="remove", targets=["comment-0", "comment-1"]),
        ),
        TrialRequest(
            world=worlds()["interaction"],
            intervention=Intervention(kind="remove", targets=["comment-0"]),
        ),
        TrialRequest(world=source, strict_calls=[]),
    ]
    result = execute(BatchRequest(trials=requests))
    first, removed, replaced, repeat, broken_task, redundant, group, interaction, unknown = result[
        "results"
    ]
    assert result["environment"] == "isolated_sandbox"
    assert first["harmful_action_attempted"] and first["task_success"]
    assert not removed["harmful_action_attempted"] and removed["task_success"]
    assert not replaced["harmful_action_attempted"] and replaced["task_success"]
    assert removed["request_digest"] != first["request_digest"] != replaced["request_digest"]
    assert len(first["outbox"]) == len(repeat["outbox"]) == 1
    assert first["trial_id"] != repeat["trial_id"]
    assert not broken_task["task_success"]
    assert redundant["harmful_action_attempted"] and not group["harmful_action_attempted"]
    assert not interaction["harmful_action_attempted"]
    assert unknown["validity"] == "invalid" and not unknown["fresh_decision"]
    assert digest(source) == before
    output = Path("artifacts/replay") / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=True)
    (output / "isolation-probe.json").write_text(json.dumps(probe, indent=2))
    (output / "interventions.json").write_text(json.dumps(result, indent=2))
