"""Owned host mocks in P1. No claim of network isolation until P3."""

import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from uuid import uuid4

import anyio
from mcp import Client
from mcp.client.stdio import StdioServerParameters
from rewind_core.contracts import MCP_PROTOCOL_REVISION, RunMode

from rewind_sandbox.fixtures import canonical, digest
from rewind_sandbox.models import model_for
from rewind_sandbox.outcomes import PREDICATE_VERSION, harmful, task_success
from rewind_sandbox.schemas import Action, InputOccurrence, RunResult, World


async def run_world(
    world: World, directory: Path, mode: RunMode = RunMode.SIMULATED, trust_external: bool = True
) -> RunResult:
    model = model_for(mode, trust_external)
    world = world.model_copy(deep=True)
    run_id = str(uuid4())
    working = directory / run_id
    working.mkdir(parents=True, exist_ok=False)
    world_path = working / "world.json"
    outbox_path = working / "outbox.jsonl"
    world_path.write_bytes(canonical(world))
    trace = []
    attempts: list[Action] = []
    dispatches: list[Action] = []
    async with AsyncExitStack() as stack:
        clients = {}
        schemas = {}
        for kind in ("ticket", "files", "mail"):
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-m", "rewind_sandbox.server", kind],
                env={
                    "REWIND_WORLD_FILE": str(world_path.resolve()),
                    "REWIND_OUTBOX_FILE": str(outbox_path.resolve()),
                },
            )
            client = await stack.enter_async_context(
                Client(
                    parameters,
                    mode=MCP_PROTOCOL_REVISION,
                    cache=None,
                    read_timeout_seconds=10,
                )
            )
            clients[kind] = client
            schemas[kind] = (await client.list_tools()).model_dump(mode="json")

        async def call(action: Action):
            client = clients[action.tool.split(".")[0]]
            with anyio.fail_after(10):
                response = await client.call_tool(action.tool, action.arguments)
            trace.append(
                {
                    "action": action.model_dump(mode="json"),
                    "result": response.model_dump(mode="json"),
                    "schema_digest": digest(schemas[action.tool.split(".")[0]]),
                    "occurrence": len(trace),
                    "world_digest": digest(world),
                }
            )
            if response.is_error:
                raise RuntimeError("Mock tool returned an error; run is invalid")
            if response.structured_content is not None:
                return response.structured_content
            texts = [item.text for item in response.content if item.type == "text"]
            if len(texts) != 1:
                raise RuntimeError("Expected one JSON mock response")
            return json.loads(texts[0])

        ticket = await call(
            Action(tool="ticket.read", arguments={"ticket_id": world.subject.ticket["id"]})
        )
        request = world.subject.model_copy(
            update={
                "ticket": ticket["ticket"],
                "inputs": [InputOccurrence.model_validate(item) for item in ticket["inputs"]],
            },
            deep=True,
        )
        decision = model.decide(request)
        for action in decision.actions:
            attempts.append(action)
            await call(
                Action(tool="files.read", arguments={"file_id": action.arguments["attachment"]})
            )
            await call(action)
            dispatches.append(action)
    outbox = (
        [json.loads(line) for line in outbox_path.read_text(encoding="utf-8").splitlines()]
        if outbox_path.exists()
        else []
    )
    result = RunResult(
        run_id=run_id,
        mode=mode,
        environment="owned_host_mocks",
        fresh_decision=True,
        evidence_status="fixture_effect_observed",
        world_digest=digest(world),
        config_digest=digest(
            {
                "simulator": "instruction-dsl-v1",
                "trust_external": trust_external,
                "predicate": PREDICATE_VERSION,
                "protocol": MCP_PROTOCOL_REVISION,
            }
        ),
        model_request=request,
        model_response=decision,
        attempts=attempts,
        dispatches=dispatches,
        outbox=outbox,
        harmful_action_attempted=any(harmful(action, world) for action in attempts),
        harmful_action_executed=any(harmful(action, world) for action in dispatches),
        task_success=task_success(decision, world),
        tool_trace=trace,
        limitations=[
            "Deterministic rule-based simulator; no LLM evidence.",
            "P1 owned host mocks; replay network isolation has not been proved.",
        ],
    )
    (working / "result.json").write_bytes(canonical(result) + b"\n")
    return result
