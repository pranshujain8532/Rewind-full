"""Local operator decisions; agent identity comes from the owned adapter, never HTTP fields."""

from fastapi import Depends, Header, HTTPException, Path, Query, Request, Response
from rewind_core.sentinel.contracts import DecisionRequest, SentinelSession, StartRequest
from rewind_eval.contracts import Budget, InvestigationRequest
from rewind_eval.source import read_capture
from rewind_sandbox.fixtures import canonical

from rewind_api.investigations import authenticated, mutation


def install_routes(app):
    def guarded(call):
        try:
            return call()
        except KeyError as error:
            raise HTTPException(404, "Unknown Sentinel session or action") from error
        except (ValueError, OSError) as error:
            raise HTTPException(409, str(error)[:200]) from error

    @app.post(
        "/api/sentinel/sessions", response_model=SentinelSession, dependencies=[Depends(mutation)]
    )
    def start(
        body: StartRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        def create():
            store = request.app.state.sentinel
            _, world, trust = read_capture(store.directory, body.source_session_id)
            identity = store.start(body.source_session_id, world, trust, body, idempotency_key)
            return store.snapshot(identity)

        return guarded(create)

    @app.get(
        "/api/sentinel/sessions",
        response_model=list[SentinelSession],
        dependencies=[Depends(authenticated)],
    )
    def sessions(request: Request):
        return guarded(request.app.state.sentinel.sessions)

    @app.get(
        "/api/sentinel/sessions/{identity}",
        response_model=SentinelSession,
        dependencies=[Depends(authenticated)],
    )
    def detail(request: Request, identity: str = Path(min_length=1, max_length=100)):
        return guarded(lambda: request.app.state.sentinel.snapshot(identity))

    @app.get("/api/sentinel/sessions/{identity}/events", dependencies=[Depends(authenticated)])
    def events(
        request: Request,
        identity: str = Path(min_length=1, max_length=100),
        after: int = Query(0, ge=0, le=1024),
    ) -> list[dict]:
        store = request.app.state.sentinel
        guarded(lambda: store.snapshot(identity))
        return store.events(identity, after)

    @app.get("/api/sentinel/sessions/{identity}/download", dependencies=[Depends(authenticated)])
    def download(request: Request, identity: str = Path(min_length=1, max_length=100)):
        bundle = guarded(lambda: request.app.state.sentinel.export(identity))
        return Response(
            canonical(bundle),
            media_type="application/json",
            headers={
                "Content-Disposition": 'attachment; filename="sentinel-audit.json"',
                "Cache-Control": "no-store",
            },
        )

    @app.post(
        "/api/approvals/{identity}/decision",
        response_model=SentinelSession,
        dependencies=[Depends(mutation)],
    )
    def decision(
        body: DecisionRequest,
        request: Request,
        identity: str = Path(min_length=1, max_length=100),
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        def apply():
            store = request.app.state.sentinel
            # Existing cookie authenticates a single local operator; no claimed approver field.
            store.decide(identity, body, idempotency_key, "local-user")
            action = store.action(identity)
            if action.investigation_requested and not action.investigation_id:
                try:
                    job = request.app.state.jobs.start(
                        InvestigationRequest(
                            session_id=action.source_session_id,
                            discovery_budget=8,
                            max_finalists=1,
                            budget=Budget(max_trials=12, max_model_turns=12, max_seconds=60),
                        ),
                        "sentinel-investigate:" + identity,
                    )
                    store.link_investigation(identity, job.id)
                except (ValueError, OSError, KeyError):
                    # Denial already committed. A failed queue operation never releases a tool.
                    store.link_investigation(
                        identity,
                        error="Investigation unavailable; denial retained. Retry the decision.",
                    )
            return store.snapshot(action.session_id)

        return guarded(apply)
