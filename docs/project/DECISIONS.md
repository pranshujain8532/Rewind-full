# Architecture decisions

Initial entries were PROPOSED planning choices. Each current status and its
evidence is recorded below. Later-phase mechanisms remain proposed until their
named tests run. Keep superseded decisions in history.

## ADR-001 — Preserve the accepted product scope

Status: ACCEPTED — 2026-10-13, P0 scope verified.  
Question: should the bootstrap preserve the accepted concept or replace it?  
Context: REWIND's idea was accepted by external reviewers; the user wants targeted improvements.  
Choice: one recorder supporting Forensics, Ledger, Sentinel and Preflight.  
Alternative: replace it with a broader agent platform or new product.  
Reason: strengthen execution without diluting the accepted concept.  
Trade-off: larger future products such as Atlas remain separate scope.  
Revisit: only on explicit product-direction change.
Evidence: backend capability matrix and rendered shell retain recorder plus
Forensics/Ledger/Sentinel/Preflight; P0 browser checks pass. Product functions
are still planned, not claimed as implemented.  
Affected files: `rewind_api/capabilities.py`, `apps/web/src/App.tsx`, STATE/TASKS.

## ADR-002 — Separate playback from fresh experiments

Status: PROPOSED.  
Choice: explicit playback, simulator, local-model and hosted-model modes.  
Reason: recorded replies cannot evaluate changed inputs.  
Trade-off: more visible mode handling and potentially unavailable real-model paths.  
Acceptance evidence: P3 fresh-request and cache-isolation tests.

## ADR-003 — Capture model context with an adapter

Status: PROPOSED.  
Choice: MCP proxy for tool boundary; adapter for replay-capable model input/state.  
Alternative: pretend proxy traffic contains the whole agent context.  
Reason: avoid unsupported causal conclusions from partial capture.  
Trade-off: replay support is integration-specific.  
Acceptance evidence: P2 coverage tests.

## ADR-004 — Fixed-plan statistics before sequential methods

Status: PROPOSED.  
Choice: bounded discovery, fresh fixed-N confirmation, independent-proportion intervals and multiplicity adjustment.  
Alternative: immediately combine bisection, Shapley and SPRT.  
Reason: simpler to implement and audit; avoids hidden optional stopping.  
Trade-off: potentially higher compute; limited interaction search.  
Revisit: measured compute bottleneck and a reviewed sequential design.

## ADR-005 — Local modular application before distributed services

Status: ACCEPTED — 2026-10-13 for P0 API/web/storage only.  
Question: what deployable foundation fits this single-user local build?  
Context: existing laptop supports Python/Node; no working container daemon or model is required for P0.  
Choice: FastAPI, React, SQLite, local payload store, one persistent worker and isolated replay runtime.  
Alternative: microservices, multiple queues, multi-tenant cloud stack.  
Reason: low budget, limited team time, strong reproducible local demo.  
Trade-off: concurrency and deployment scope are limited.  
Revisit: actual load or deployment requirements.
Evidence: locked local setup, five API/SDK tests, four browser checks, Vite build
and real HTTP demo. Payload store, persistent worker and isolated runtime are
future parts of the choice and are not implemented or verified in P0.  
Affected files: pyproject/package manifests, `packages/rewind_core`,
`services/api/rewind_api`, `apps/web`, migration and command scripts.

## ADR-006 — Signed chain before true Merkle proofs

Status: PROPOSED.  
Choice: standard linked event hashes, Ed25519 signatures and signed seal.  
Reason: directly tests integrity requirements with less implementation complexity.  
Trade-off: no compact Merkle inclusion proof or independent external anchoring.  
Revisit: selective verification or externally anchored audit requirement.

## ADR-007 — One Python package, one npm workspace, exact locks

Date: 2026-10-13.  
Status: ACCEPTED.  
Question: how should the conceptual modules be packaged reproducibly?  
Context: the kit contains specs only; Windows Python 3.13.12 / Node 22.18.0 / npm 10.9.3 are available.  
Options: independently built Python subprojects; one editable distribution with explicit module boundaries; distributed services.  
Chosen approach: one Hatch-built `rewind` distribution with core and API packages,
future capture/replay/eval directories, one npm web workspace; local uv 0.13.0
and repository Python/npm locks. Pin compatible dependencies as in versions.json.  
Why: clean installed imports and simple cross-platform commands without service overhead.  
Trade-offs: adding a Python module requires updating wheel inclusion; exact pins
need deliberate upgrades. No statistics/ML/graph dependencies before their phase.  
Evidence: uv lock/sync and npm ci succeed; root setup/check run. npm initially
rejected TypeScript 7.0.2 because openapi-typescript 7.13.0 requires `^5.x`;
TypeScript 5.9.3 resolves and builds without peer overrides.  
Revisit trigger: independent module distribution or measured load requirements.  
Affected files: pyproject.toml, package manifests, locks, versions.json, scripts/rewind.py.

## ADR-008 — Official MCP v2, one explicit protocol revision

Date: 2026-10-13.  
Status: ACCEPTED — SDK compatibility only; application transport coverage remains future work.  
Question: which supported SDK/revision should the build use consistently?  
Context: current official SDK/registry docs identify stable MCP Python 2.3.0
and modern revision 2026-07-28; older lifecycle snippets are incompatible.  
Options: official v2/current revision; retained v1/older revision; automatic fallback.  
Chosen approach: mcp 2.3.0, protocol 2026-07-28, explicit client `mode`
revision with caching disabled for compatibility checks.  
Why: installed source documents direct adoption; an in-process SDK tool call
reports the selected revision. No mixed initialise/modern lifecycle.  
Trade-offs: P1 must test stdio framing/errors/mocks; P2/P9 must verify recorder/public-tool
coverage. No HTTP transport support is claimed.  
Evidence: `test_mcp_selected_revision_in_process` passes; installed SDK signature/source inspected;
official links in `docs/implementation/10-P0-VERSION-SOURCES.md`.  
Revisit trigger: SDK security update, supported-revision change or verified client requirement.  
Affected files: contracts.py, capabilities, pyproject/uv.lock, tests/test_p0.py, versions.json.

## ADR-009 — Separate truth axes, generate the client boundary

Date: 2026-10-13.  
Status: ACCEPTED — contract/UI verified; fresh inference remains ADR-002/P3.  
Question: how does the shell distinguish readiness, maturity and evidence?  
Context: SDK installation/environment hints cannot enable an absent agent/replay path.  
Options: one ready flag for everything; separate mode/availability/maturity/evidence;
handwritten frontend schemas.  
Chosen approach: backend-owned Pydantic schemas, separate enums, reason-bearing
capabilities; generated OpenAPI/TypeScript with drift checks. All modes unavailable
in P0; health ready means migrated API/storage only.  
Why: prevents fake live results and contract drift while allowing a useful shell.  
Trade-offs: regeneration required after contract edits; P0 has only read-only metadata,
no generated runtime validator or experiment endpoints.  
Evidence: 5/5 backend/SDK checks, 4/4 browser checks; normal startup has no fatal
console errors; outage remains visible and refresh recovers.  
Revisit trigger: new phase/endpoint or protocol/schema change.  
Affected files: contracts.py, API, schemas/openapi.json, generated/api.d.ts,
App.tsx/api.ts, export_schema.py.

## ADR-010 — Explicit migrations and schema-aware readiness

Date: 2026-10-13.  
Status: ACCEPTED.  
Question: when should the API report storage ready?  
Context: process startup alone does not prove the database has the expected schema.  
Options: create all tables at startup; run Alembic explicitly and check readiness;
health without storage checks.  
Chosen approach: migration `0001_p0` stores schema metadata; setup/dev/demo invoke
Alembic. API verifies head revision, metadata version and WAL; HTTP 503 for missing
migrations/query failure. No automatic reset or synthetic session seed.  
Why: repeatable setup and meaningful failure states preserve existing data.  
Trade-offs: migration needed when running API alone; future tables need later
migrations. Backup/restore documented but not_run.  
Evidence: repeated upgrade, unmigrated and broken-schema tests pass; HTTP demo
reports ready with WAL and revision 0001_p0.  
Revisit trigger: migration head, DB concurrency or production deployment changes.  
Affected files: alembic.ini, migrations/, storage.py, app.py, scripts/rewind.py, tests/test_p0.py.

## New ADR template (retained)

~~~text
ADR-NNN — title
Date:
Status: proposed / accepted / superseded
Question:
Context:
Options:
Chosen approach:
Reason:
Trade-offs and limitations:
Evidence / experiment IDs:
Affected files and contracts:
Revisit trigger:
Supersedes / superseded by:
~~~

