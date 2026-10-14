"""Authenticated, bounded Ledger API; fresh evaluation runs in the separate worker."""

from fastapi import Depends, Header, HTTPException, Query, Request
from rewind_ledger.bundle import MAX_BUNDLE_BYTES, bounded_json, verify_bundle
from rewind_ledger.contracts import (
    CaseRequest,
    EvidenceRecord,
    RecordRequest,
    RegressionRequest,
    RegressionSnapshot,
    VerificationResult,
)
from rewind_sandbox.fixtures import canonical
from starlette.responses import Response

from rewind_api.investigations import authenticated, mutation


def install_routes(app):
    def translate(action):
        try:
            return action()
        except KeyError as error:
            raise HTTPException(404, "Unknown Ledger artifact") from error
        except (ValueError, OSError) as error:
            raise HTTPException(
                422, "Invalid, incomplete, unavailable or conflicting Ledger input"
            ) from error

    @app.post("/api/records", response_model=EvidenceRecord, dependencies=[Depends(mutation)])
    def create(
        body: RecordRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        return translate(lambda: request.app.state.ledger.create_record(body, idempotency_key))

    @app.get(
        "/api/records", response_model=list[EvidenceRecord], dependencies=[Depends(authenticated)]
    )
    def records(request: Request, limit: int = Query(20, ge=1, le=50)):
        return translate(lambda: request.app.state.ledger.records(limit))

    @app.get(
        "/api/records/{identity}",
        response_model=EvidenceRecord,
        dependencies=[Depends(authenticated)],
    )
    def record(identity: str, request: Request):
        return translate(lambda: request.app.state.ledger.bundle(identity)["report"])

    @app.get("/api/records/{identity}/download", dependencies=[Depends(authenticated)])
    def download(identity: str, request: Request):
        bundle = translate(lambda: request.app.state.ledger.bundle(identity))
        filename = f"rewind-evidence-{bundle['report']['id']}.json"
        return Response(
            canonical(bundle),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-store",
            },
        )

    @app.post(
        "/api/records/verify", response_model=VerificationResult, dependencies=[Depends(mutation)]
    )
    async def verify(
        request: Request,
        trusted_public_key: str | None = Header(
            default=None, alias="X-REWIND-Trusted-Public-Key", min_length=64, max_length=64
        ),
    ):
        raw = bytearray()
        async for chunk in request.stream():
            if len(raw) + len(chunk) > MAX_BUNDLE_BYTES:
                raise HTTPException(413, "Verification input too large")
            raw.extend(chunk)
        try:
            payload = bounded_json(bytes(raw))
            if trusted_public_key is not None:
                # Preserve downloaded integer values; JavaScript JSON round-trips can round seeds.
                bundle, public = payload, bytes.fromhex(trusted_public_key)
            else:
                if set(payload) != {"bundle", "trusted_public_key"}:
                    raise ValueError
                if (
                    not isinstance(payload["trusted_public_key"], str)
                    or len(payload["trusted_public_key"]) != 64
                ):
                    raise ValueError
                bundle, public = payload["bundle"], bytes.fromhex(payload["trusted_public_key"])
            import asyncio

            return await asyncio.to_thread(verify_bundle, bundle, public)
        except (ValueError, KeyError, TypeError):
            raise HTTPException(
                422, "Corrupt input or explicit trusted public key missing"
            ) from None

    @app.post("/api/regressions/from-record/{identity}", dependencies=[Depends(mutation)])
    def case(
        identity: str,
        body: CaseRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        return translate(
            lambda: request.app.state.ledger.create_case(identity, body, idempotency_key)
        )

    @app.post(
        "/api/regression-runs", response_model=RegressionSnapshot, dependencies=[Depends(mutation)]
    )
    def start(
        body: RegressionRequest,
        request: Request,
        idempotency_key: str = Header(min_length=1, max_length=100),
    ):
        return translate(lambda: request.app.state.ledger.start(body, idempotency_key))

    @app.get(
        "/api/regression-runs",
        response_model=list[RegressionSnapshot],
        dependencies=[Depends(authenticated)],
    )
    def runs(request: Request, limit: int = Query(20, ge=1, le=50)):
        store = request.app.state.ledger
        store.recover()
        from sqlalchemy import text

        with store.engine.connect() as connection:
            ids = (
                connection.execute(
                    text("SELECT id FROM regression_runs ORDER BY created_at DESC LIMIT :limit"),
                    {"limit": limit},
                )
                .scalars()
                .all()
            )
        return [store.snapshot(identity) for identity in ids]

    @app.get(
        "/api/regression-runs/{identity}",
        response_model=RegressionSnapshot,
        dependencies=[Depends(authenticated)],
    )
    def snapshot(identity: str, request: Request):
        request.app.state.ledger.recover()
        return translate(lambda: request.app.state.ledger.snapshot(identity))

    @app.post(
        "/api/regression-runs/{identity}/cancel",
        response_model=RegressionSnapshot,
        dependencies=[Depends(mutation)],
    )
    def cancel(identity: str, request: Request):
        return translate(lambda: request.app.state.ledger.cancel(identity))

    @app.get("/api/regression-runs/{identity}/download", dependencies=[Depends(authenticated)])
    def run_download(identity: str, request: Request):
        bundle = translate(lambda: request.app.state.ledger.run_bundle(identity))
        return Response(
            canonical(bundle), media_type="application/json", headers={"Cache-Control": "no-store"}
        )

    @app.get("/api/regression-comparison", dependencies=[Depends(authenticated)])
    def compare(
        request: Request, left: str = Query(max_length=100), right: str = Query(max_length=100)
    ):
        return translate(lambda: request.app.state.ledger.compare(left, right))
