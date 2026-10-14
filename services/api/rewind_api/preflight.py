"""Authenticated owned target evaluation, durable events and failure investigation."""

import asyncio

from fastapi import Depends, Header, HTTPException, Path, Query, Request
from rewind_core.preflight.contracts import (
    FIXTURE_IDS,
    SUITE,
    TARGET,
    PreflightRequest,
    PreflightSnapshot,
)
from rewind_core.preflight.store import TERMINAL
from rewind_eval.contracts import Budget, InvestigationRequest
from rewind_sandbox.fixtures import canonical
from sqlalchemy import text
from starlette.responses import StreamingResponse

from rewind_api.investigations import authenticated, mutation


def install_routes(app):
    def checked(call):
        try:
            return call()
        except KeyError as error:
            raise HTTPException(404, "Unknown Preflight run or trial") from error
        except ValueError as error:
            raise HTTPException(409, str(error)[:200]) from error

    @app.get("/api/preflight/catalog", dependencies=[Depends(authenticated)])
    def catalog() -> dict:
        return {
            "schema_version": "1.0",
            "target_id": TARGET,
            "suite_version": SUITE,
            "surfaces": ["ticket_comments", "mock_file_text"],
            "fixtures": FIXTURE_IDS,
            "fixed_suite": "verified",
            "evolutionary_generation": "not_implemented",
            "llm_variations": "not_implemented",
            "guardrail_detection": "not_measured",
            "target_urls": "not_supported",
        }

    @app.post(
        "/api/preflight-runs", response_model=PreflightSnapshot, dependencies=[Depends(mutation)]
    )
    def start(
        body: PreflightRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        return checked(lambda: request.app.state.preflight.start(body, idempotency_key))

    @app.get(
        "/api/preflight-runs",
        response_model=list[PreflightSnapshot],
        dependencies=[Depends(authenticated)],
    )
    def runs(request: Request):
        store = request.app.state.preflight
        store.recover()
        with store.engine.connect() as c:
            ids = (
                c.execute(text("SELECT id FROM preflight_runs ORDER BY rowid DESC LIMIT 20"))
                .scalars()
                .all()
            )
        return [store.snapshot(i) for i in ids]

    @app.get(
        "/api/preflight-runs/{identity}",
        response_model=PreflightSnapshot,
        dependencies=[Depends(authenticated)],
    )
    def detail(request: Request, identity: str = Path(min_length=1, max_length=100)):
        request.app.state.preflight.recover()
        return checked(lambda: request.app.state.preflight.snapshot(identity))

    @app.get("/api/preflight-runs/{identity}/trials", dependencies=[Depends(authenticated)])
    def trials(request: Request, identity: str = Path(min_length=1, max_length=100)) -> list[dict]:
        return checked(lambda: request.app.state.preflight.trials(identity))

    @app.post(
        "/api/preflight-runs/{identity}/cancel",
        response_model=PreflightSnapshot,
        dependencies=[Depends(mutation)],
    )
    def cancel(request: Request, identity: str = Path(min_length=1, max_length=100)):
        return checked(lambda: request.app.state.preflight.cancel(identity))

    @app.post(
        "/api/preflight-runs/{identity}/trials/{ordinal}/investigate",
        dependencies=[Depends(mutation)],
    )
    def investigate(
        request: Request,
        identity: str = Path(min_length=1, max_length=100),
        ordinal: int = Path(ge=1, le=96),
    ) -> dict:
        store = request.app.state.preflight
        trial = next(
            (t for t in checked(lambda: store.trials(identity)) if t["ordinal"] == ordinal), None
        )
        if not trial:
            raise HTTPException(404, "Unknown trial")
        job = checked(
            lambda: request.app.state.jobs.start(
                InvestigationRequest(
                    session_id=trial["session_id"],
                    discovery_budget=8,
                    max_finalists=1,
                    budget=Budget(max_trials=12, max_model_turns=12, max_seconds=60),
                ),
                f"preflight-investigate:{identity}:{ordinal}",
            )
        )
        with store.transaction() as c:
            previous = c.scalar(
                text(
                    "SELECT investigation_id FROM preflight_trials WHERE run_id=:id AND ordinal=:n"
                ),
                {"id": identity, "n": ordinal},
            )
            if not previous:
                c.execute(
                    text(
                        "UPDATE preflight_trials SET investigation_id=:job "
                        "WHERE run_id=:id AND ordinal=:n"
                    ),
                    {"id": identity, "n": ordinal, "job": job.id},
                )
                store.event(
                    c,
                    identity,
                    "investigation_linked",
                    {"ordinal": ordinal, "investigation_id": job.id},
                )
        return {"session_id": trial["session_id"], "investigation_id": job.id, "status": job.status}

    @app.get("/api/preflight-runs/{identity}/events", dependencies=[Depends(authenticated)])
    async def events(
        request: Request,
        identity: str = Path(min_length=1, max_length=100),
        after: int = Query(0, ge=0, le=512),
        last_event_id: str | None = Header(default=None),
    ):
        store = request.app.state.preflight
        checked(lambda: store.raw(identity))
        if last_event_id:
            try:
                prefix, seq = last_event_id.rsplit(":", 1)
                if prefix != identity or not 0 <= int(seq) <= 512:
                    raise ValueError
                after = max(after, int(seq))
            except ValueError as error:
                raise HTTPException(400, "Invalid event cursor for this run") from error

        async def stream():
            cursor = after
            while not await request.is_disconnected():
                await asyncio.to_thread(store.recover)
                for event in await asyncio.to_thread(store.events, identity, cursor):
                    cursor = event["job_seq"]
                    yield f"id: {event['id']}\ndata: {canonical(event).decode()}\n\n"
                row = await asyncio.to_thread(store.raw, identity)
                if row["status"] in TERMINAL and not await asyncio.to_thread(
                    store.events, identity, cursor
                ):
                    break
                yield ": heartbeat\n\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
        )
