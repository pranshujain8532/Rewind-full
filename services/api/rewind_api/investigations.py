"""Authenticated local experiment API. Computation runs in the separate worker."""

import asyncio
import json
import secrets
from uuid import uuid4

import anyio
from fastapi import Depends, Header, HTTPException, Query, Request, Response
from rewind_capture.store import CaptureStore
from rewind_eval.contracts import DemoRequest, GraphResponse, InvestigationRequest, JobSnapshot
from rewind_eval.demo import controlled_world
from rewind_eval.provenance import provenance
from rewind_eval.source import read_capture
from rewind_eval.store import TERMINAL
from rewind_sandbox.fixtures import canonical, digest, load_world
from rewind_sandbox.runner import run_world
from sqlalchemy import text
from starlette.responses import StreamingResponse

ORIGINS = {
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://localhost:5173",
}


def local_origin(request: Request):
    if request.headers.get("origin") not in ORIGINS or request.headers.get("x-rewind-local") != "1":
        raise HTTPException(403, "Local origin and CSRF header required")


def authenticated(request: Request):
    token = request.cookies.get("rewind_session", "")
    if not secrets.compare_digest(token, request.app.state.local_token):
        raise HTTPException(401, "Local session required")


def mutation(request: Request):
    authenticated(request)
    local_origin(request)


def install_routes(app):
    @app.post("/api/auth/local", status_code=204, dependencies=[Depends(local_origin)])
    def local_session(request: Request, response: Response):
        response.set_cookie(
            "rewind_session",
            request.app.state.local_token,
            httponly=True,
            samesite="strict",
            max_age=3600,
        )

    @app.get("/api/sessions", dependencies=[Depends(authenticated)])
    def sessions(request: Request, limit: int = Query(50, ge=1, le=100)) -> list[dict]:
        with request.app.state.jobs.engine.connect() as connection:
            return [
                {"id": r.id, "sealed": bool(r.sealed), "metadata": json.loads(r.metadata)}
                for r in connection.execute(
                    text(
                        "SELECT id,sealed,metadata FROM sessions ORDER BY rowid DESC LIMIT :limit"
                    ),
                    {"limit": limit},
                )
            ]

    @app.get(
        "/api/sessions/{session_id}/graph",
        response_model=GraphResponse,
        dependencies=[Depends(authenticated)],
    )
    def graph(session_id: str, request: Request) -> dict:
        try:
            bundle, _, _ = read_capture(request.app.state.jobs.directory, session_id)
            return provenance(bundle)
        except Exception as error:
            raise HTTPException(
                409, "unsupported_replay: graph requires a trusted complete capture"
            ) from error

    @app.post("/api/demo/runs", dependencies=[Depends(mutation)])
    def demo(
        body: DemoRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ) -> dict:
        store = request.app.state.jobs
        with store.transaction() as connection:
            prior = connection.execute(
                text("SELECT * FROM demo_starts WHERE idempotency_key=:key"),
                {"key": idempotency_key},
            ).first()
            if prior:
                if prior.request_digest != digest(body):
                    raise HTTPException(409, "idempotency_conflict")
                return {"session_id": prior.session_id, "status": prior.status}
            session_id = str(uuid4())
            connection.execute(
                text("INSERT INTO demo_starts VALUES(:key,:digest,:id,'running')"),
                {"key": idempotency_key, "digest": digest(body), "id": session_id},
            )
        from rewind_replay.container import ROOT

        capture = CaptureStore(store.directory)
        try:
            world = controlled_world(load_world(ROOT / "fixtures", body.scenario))
            anyio.run(
                lambda: run_world(
                    world,
                    store.directory / "sandbox-runs",
                    capture_store=capture,
                    run_id=session_id,
                )
            )
            status = "completed"
        except Exception:
            status = "failed"
        finally:
            capture.engine.dispose()
        with store.engine.begin() as connection:
            connection.execute(
                text("UPDATE demo_starts SET status=:status WHERE idempotency_key=:key"),
                {"key": idempotency_key, "status": status},
            )
        return {"session_id": session_id, "status": status}

    @app.post("/api/investigations", response_model=JobSnapshot, dependencies=[Depends(mutation)])
    def start(
        body: InvestigationRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        try:
            return request.app.state.jobs.start(body, idempotency_key)
        except KeyError as error:
            raise HTTPException(404, "Unknown session") from error
        except ValueError as error:
            raise HTTPException(
                409 if str(error) == "idempotency_conflict" else 422, str(error)
            ) from error

    @app.get(
        "/api/investigations",
        response_model=list[JobSnapshot],
        dependencies=[Depends(authenticated)],
    )
    def jobs(request: Request, limit: int = Query(20, ge=1, le=50)):
        store = request.app.state.jobs
        store.recover()
        with store.engine.connect() as connection:
            ids = (
                connection.execute(
                    text("SELECT id FROM investigations ORDER BY created_at DESC LIMIT :limit"),
                    {"limit": limit},
                )
                .scalars()
                .all()
            )
        return [store.snapshot(job_id) for job_id in ids]

    @app.get(
        "/api/investigations/{job_id}",
        response_model=JobSnapshot,
        dependencies=[Depends(authenticated)],
    )
    def snapshot(job_id: str, request: Request):
        store = request.app.state.jobs
        store.recover()
        try:
            return store.snapshot(job_id)
        except KeyError as error:
            raise HTTPException(404, "Unknown investigation") from error

    @app.post(
        "/api/investigations/{job_id}/cancel",
        response_model=JobSnapshot,
        dependencies=[Depends(mutation)],
    )
    def cancel(job_id: str, request: Request):
        try:
            return request.app.state.jobs.cancel(job_id)
        except KeyError as error:
            raise HTTPException(404, "Unknown investigation") from error

    @app.get("/api/investigations/{job_id}/trials", dependencies=[Depends(authenticated)])
    def trials(
        job_id: str,
        request: Request,
        offset: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
    ) -> list[dict]:
        store = request.app.state.jobs
        try:
            store.raw_job(job_id)
        except KeyError as error:
            raise HTTPException(404, "Unknown investigation") from error
        rows = store.trials(job_id)[offset : offset + limit]
        from rewind_capture.store import redact

        return [
            {
                "ordinal": r["ordinal"],
                "phase": r["phase"],
                "arm": r["arm"],
                "manifest": json.loads(r["manifest"]),
                "result": redact(json.loads(r["result"])) if r["result"] else None,
            }
            for r in rows
        ]

    @app.get("/api/investigations/{job_id}/events", dependencies=[Depends(authenticated)])
    async def events(
        job_id: str,
        request: Request,
        after: int = Query(0, ge=0),
        last_event_id: str | None = Header(default=None),
    ):
        store = request.app.state.jobs
        try:
            await asyncio.to_thread(store.raw_job, job_id)
        except KeyError as error:
            raise HTTPException(404, "Unknown investigation") from error
        if last_event_id:
            try:
                prefix, seq = last_event_id.rsplit(":", 1)
                if prefix != job_id or int(seq) < 0:
                    raise ValueError
                after = max(after, int(seq))
            except ValueError as error:
                raise HTTPException(400, "Invalid Last-Event-ID for this job") from error

        async def stream():
            cursor = after
            while not await request.is_disconnected():
                await asyncio.to_thread(store.recover)
                persisted = await asyncio.to_thread(store.events, job_id, cursor)
                for event in persisted:
                    cursor = event["job_seq"]
                    yield f"id: {event['id']}\ndata: {canonical(event).decode()}\n\n"
                job = await asyncio.to_thread(store.raw_job, job_id)
                if job["status"] in TERMINAL:
                    # Re-read after terminal state to drain events committed with that transition.
                    if not await asyncio.to_thread(store.events, job_id, cursor):
                        break
                yield ": heartbeat\n\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
