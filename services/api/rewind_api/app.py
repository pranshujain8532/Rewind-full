"""Readiness describes the API, not readiness to run agent experiments."""

import secrets
from contextlib import asynccontextmanager
from importlib.metadata import version
from pathlib import Path

from fastapi import FastAPI, Response
from rewind_core.contracts import CapabilitiesResponse, DatabaseReadiness, HealthResponse
from rewind_core.storage import MIGRATION_REVISION, data_directory, make_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from rewind_api.capabilities import capabilities


def create_app(directory: Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.engine = make_engine(directory or data_directory())
        from rewind_eval.store import JobStore

        app.state.jobs = JobStore(directory or data_directory())
        from rewind_ledger.store import LedgerStore

        app.state.ledger = LedgerStore(directory or data_directory())
        from rewind_core.sentinel.store import SentinelStore

        app.state.sentinel = SentinelStore(directory or data_directory())
        app.state.local_token = secrets.token_urlsafe(32)
        yield
        app.state.jobs.engine.dispose()
        app.state.ledger.engine.dispose()
        app.state.sentinel.engine.dispose()
        app.state.engine.dispose()

    app = FastAPI(title="REWIND API", version=version("rewind"), lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    from rewind_api.investigations import install_routes

    install_routes(app)
    from rewind_api.ledger import install_routes as install_ledger

    install_ledger(app)
    from rewind_api.workspace import install_routes as install_workspace

    install_workspace(app)
    from rewind_api.sentinel import install_routes as install_sentinel

    install_sentinel(app)

    @app.get(
        "/api/health", response_model=HealthResponse, responses={503: {"model": HealthResponse}}
    )
    def health(response: Response) -> HealthResponse:
        stored_sessions = 0
        try:
            with app.state.engine.connect() as connection:
                journal_mode = connection.scalar(text("PRAGMA journal_mode"))
                has_migrations = connection.scalar(
                    text(
                        "SELECT count(*) FROM sqlite_master "
                        "WHERE type='table' AND name='alembic_version'"
                    )
                )
                revision = (
                    connection.scalar(text("SELECT version_num FROM alembic_version"))
                    if has_migrations
                    else None
                )
                schema_version = (
                    connection.scalar(
                        text("SELECT value FROM app_metadata WHERE key='schema_version'")
                    )
                    if revision == MIGRATION_REVISION
                    else None
                )
                ready = (
                    revision == MIGRATION_REVISION
                    and schema_version == "1.0"
                    and journal_mode == "wal"
                )
                if ready:
                    stored_sessions = connection.scalar(text("SELECT count(*) FROM sessions"))
                database = DatabaseReadiness(
                    ready=ready,
                    reason="ready" if ready else "migration_required",
                    migration_revision=revision,
                    journal_mode=journal_mode,
                )
        except SQLAlchemyError:
            database = DatabaseReadiness(
                ready=False,
                reason="database_unavailable",
                migration_revision=None,
                journal_mode=None,
            )
        if not database.ready:
            response.status_code = 503
        return HealthResponse(
            status="ok" if database.ready else "not_ready",
            ready=database.ready,
            version=version("rewind"),
            database=database,
            available_modes=[mode.mode for mode in capabilities().modes if mode.available],
            stored_session_count=stored_sessions,
        )

    @app.get("/api/capabilities", response_model=CapabilitiesResponse)
    def get_capabilities() -> CapabilitiesResponse:
        return capabilities()

    @app.get("/api/scenarios", response_model=list[str])
    def scenarios() -> list[str]:
        from rewind_sandbox.fixtures import NAMES

        return list(NAMES)

    return app


app = create_app()
