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

Status: ACCEPTED for P4 simulator; evidence/P4-SIM.md, full check 64/64, browser 12/12.
Choice: bounded discovery, fresh fixed-N confirmation, independent-proportion intervals and multiplicity adjustment.  
Alternative: immediately combine bisection, Shapley and SPRT.  
Reason: simpler to implement and audit; avoids hidden optional stopping.  
Trade-off: potentially higher compute; limited interaction search.  
Revisit: measured compute bottleneck and a reviewed sequential design.
P4 evidence: pinned statsmodels 0.14.6 explicit newcomb/diff API; independent Wilson
derivation and null Monte Carlo tests, fresh fixed plans, alpha=0.05/m, no optional
stopping. Deterministic fixtures use N=1 without CI. EXP-003 retains raw trials.

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

## ADR-011 — Transparent simulator and separate evaluator inputs

Date: 2026-10-13. Status: ACCEPTED for P1.
Question: how can the no-GPU core exercise attacks without claiming LLM evidence?
Context: no configured subject model/provider. Options: fake model responses;
explicit instruction DSL with owned MCP tools; wait for a real model.
Chosen: deterministic DSL interpreting supplied SEND directives, three real stdio
mock servers and separate evaluator expectations. Mode, environment, freshness,
attempt/dispatch/task outcomes and configuration/world digests are retained.
Why: exercises the supported decision/tool boundary honestly and reproducibly.
Trade-offs: artificial rule semantics; no inference interval, LLM or isolation claim.
Evidence: 13 scenario/interface tests, full check 18/18, CLI demo and browser 4/4;
official transport docs https://py.sdk.modelcontextprotocol.io/client/transports/.
Revisit: real subject availability and P3 isolation. Affected: rewind_sandbox,
fixtures/scenarios/evaluation, API capabilities, CLI, generated boundary and tests.

## ADR template

## ADR-012 — Canonical signed capture and bounded transparent stdio relay

Date 2026-10-13; status ACCEPTED after P2 gate.
Question: how to capture complete supported evidence without inventing context or
mixing protocol lifecycles? Context: owned SDK v2 stdio and stateless simulator.
Options: semantic-only reconstructed logs; transparent wire capture plus adapter;
custom protocol implementation. Chosen: byte relay delegating SDK lifecycle,
transaction-sequenced events, encrypted blobs, separate occurrence identities,
Ed25519 chain/seal and independently trusted verifier. Why: test the actual boundary
and detect tampering while exposing partial capture. Trade-offs: synthetic-only
development artifacts, local keys/no external anchor, no resources/prompts/HTTP
or arbitrary frameworks. Limits: frame 262144 bytes, payload 512000 bytes, 512
events, 4MB capture budget, relay lifetime <=60 seconds and bounded shutdown.
Evidence: P2 32/32 full checks, corruption/trust/correlation/cancellation/bounds tests,
actual captured demo and CLI verification; docs/project/evidence/P2.md.
Revisit: private deployments, retention, new adapters/transports and key custody.
Affected: rewind_capture, runner hooks, 0002 migration, health/capabilities/types.

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


## ADR-013 — Isolated owned-world replay and honest divergence

Date: 2026-10-13. Status: ACCEPTED for P3 simulator only.
Question: how to rerun changed inputs without external side effects or stale decisions?
Context: Windows host, working Linux Docker engine, no subject model.
Options: host subprocess; no-network container with full snapshot; cached playback.
Chosen: fresh stateless DSL decisions in non-root, no-network, read-only Linux
container, CPU/memory/PID limits, private outboxes, no bind mounts/host credentials.
Strict reads require tool/schema/arguments/occurrence/environment-state matches;
unknown initial or downstream reads invalidate the trial. Versioned mocks are
labelled sandbox re-execution, not arbitrary production reconstruction.
Why: separates genuine transformed-input harness execution from playback and
establishes a tested side-effect boundary. Trade-offs: Docker required; no kernel
security certification, production tool adapter or real-model claim. The root
launcher uses the host Docker API; workers receive no Docker socket.
Evidence: replay tests 4/4, full check 36/36, thirteen actual isolation probes;
artifacts/p3 and evidence/P3-SIM.md. Revisit: real runtime/provider availability,
new tools or threat model. Affected: rewind_replay, runner state digests,
containers/replay.Dockerfile, capabilities/contracts/generated types and tests.
ADR-002 remains incomplete for real-model paths; this decision accepts only SIM.


## ADR-014 — Frozen simulator plans and a durable single-worker lifecycle

Date: 2026-10-14 (Asia/Calcutta). Status: ACCEPTED for P4 simulator after final gate.
Question: how can P4 report conditional evidence while remaining recoverable and affordable?
Context: P3 simulator is isolated; no real adapter or paid budget exists.
Options: in-request evaluation and ephemeral progress; durable SQLite reservations,
one worker process and committed application events; distributed task services.
Chosen: additive 0003 migration, source trust/config/schema admission, observable
graph and transparent ranking, eight selected candidates with full coverage, bounded
single/top-three-pair/group discovery and captured owned benign/neutral controls.
Freeze finalists, fresh independent streams/order, N, budget, alpha/threshold and
abort-on-invalid policy before confirmation. N=1/no CI for deterministic fixtures;
stochastic default N=40 and at most three finalists. Explicit new starts are required
after interruption; never silently resume, pool experiments or change a plan.
Why: preserve actual trials and truthful UI state without adding infrastructure.
Trade-offs: bounded search lacks global minimality; conservative all-trials task
success rule; up to eight in-flight trials can finish after cancellation. A local
trust anchor and same-origin local cookie handshake do not establish external
identity or a multi-user deployment. Legacy captures lacking the neutral control
are preserved but unsupported for this design. Real-model methods remain blocked.
Evidence: P4 mechanism tests, EXP-003 actual Docker cases/worker kill and browser
refresh/cancellation/interruption journeys; final references in evidence/P4-SIM.md.
Revisit trigger: real adapter availability, independently reviewed retry/sequential
design, measured resource bottleneck or private/remote deployment requirement.
Affected files: rewind_eval, 0003 migration, API routes/auth, Forensics.tsx, command
scripts, dependency locks, generated contracts and tests.

## ADR-015 — Backend-only Gemini broker with an explicit billing declaration

Date: 2026-10-14 (Asia/Calcutta). Status: ACCEPTED for exploratory CLI only.
Question: can the supplied Gemini key enable fresh decisions without granting the
subject agent network, credentials or external tool side effects?
Context: user supplied api.txt and explicitly authorised a free-tier project,
spend $0. Model catalog authentication and actual generateContent calls succeeded.
Options: key/network inside the worker; broad provider SDK/tool execution; narrow
parent HTTPS broker with one bound pipe exchange and structured mock proposals.
Chosen: original standard-library transport, fixed gemini-3.1-flash-lite endpoint,
no redirects/proxies, non-root no-network container, exact transformed-request
validation, token/cost reservation captured before generation and no cache/retry.
Inference defaults disabled. User-declared free-tier requests reserve $0; paid
requests require a positive authorised cap. Key alone cannot verify project billing.
Why: the hosted exception stays explicit while tools and secrets stay isolated.
Trade-offs: structured decisions support only owned synthetic mail mocks; unknown
arguments invalidate trials. CLI budgets are per invocation, not resumable P4 jobs.
The model seed is not a determinism guarantee. Three exploratory calls establish
transport/adapter operation, not provider variability or intervention causality.
Signed capture completeness is distinct from trial and mode eligibility. Real
Forensics admission remains closed; no simulator fallback or real interval exists.
Evidence: EXP-008 raw three-response smoke, two valid/one invalid; signed audits
and actual P4 admission refusals; eight provider-free Gemini tests and 13 isolation
checks. Third outcome recovered from retained raw result after the persistence fix.
Revisit trigger: P4-REAL durable reservations and explicit owned argument schemas,
fresh affordable frozen confirmation plan, provider variability/independence review.
Affected files: rewind_replay/gemini*.py, runtime/worker, capture input envelope,
API capability reasons, browser selection, ignore rules, Gemini tests and guide.
Official protocol/pricing sources are registered in COMPONENT-SOURCES.md.

## ADR-016 — Sign stored-fact bundles and separate original-attack defence contracts

Date: 2026-10-14 (Asia/Calcutta). Status: ACCEPTED for verified P5-SIM.
Question: how can a portable record preserve actual evidence and test a defence
without confusing input ablation, containment and behavioural improvement?
Context: P4-SIM is valid; Gemini is exploratory/ineligible; local trust is explicit.
Options: generated prose-only reports; signatures over a summary alone; canonical
artifact manifests plus code-derived reports and fixed original-input regressions.
Chosen: sign report/trace/investigation digests with existing Ed25519 key under a
separate domain; encrypt immutable bundles with AES-GCM; verify with a supplied
trusted public key outside API/DB; bound JSON sizes/depth/nodes and recompute facts.
Preserve unknown model identity, absent approvals, pending governance and row-instance
impact. Source completeness/validity gates regression separately from integrity.
Regression cases bind the full original world and two documented configuration arms.
N=1 deterministic simulator, no CI; behavioural measures attempts, containment measures
dispatches and residual attempts. Require exact summary AND owner-requested sends.
Why: a signed summary cannot protect detached trials; attack removal tests attribution,
not a patched defence. Blocking all tools is insufficient where tools are needed.
Trade-offs: supported simulator/presets only; no full Sentinel mandate/approval flow,
external legal/compliance mapping or public-app authentication. Local keys are not
independently anchored. No stochastic/real regression claim or pooled run inference.
Browser uploads use original bytes because JSON Number rounding changes 64-bit seeds;
legacy wrappers are for lossless clients only. Export refuses existing filenames.
Evidence: actual EXP-004, source/regression artifacts and CLI outside application;
87 repository tests, post-upload 15 P5 tests, three inspected viewport journeys.
Revisit: real capture eligibility, separately budgeted stochastic regression plan,
approved governance source controls, signed Sentinel mandates and external key custody.
Affected: rewind_ledger, 0004 migration, replay mock enforcement, shared worker/API,
Ledger controls, schema generation, tests, benchmark and documentation.

## ADR-017 — A routed evidence workspace with bounded projections and durable progress

Date: 2026-10-14 (Asia/Calcutta). Status: ACCEPTED for verified P6 supported UI.
Question: how can the frontend connect captured provenance, experimental outcomes,
signed records and regressions without manufacturing live state or requiring a new stack?
Context: P4/P5 have durable facts, but the overview-only UI has no session explorer
and regression progress is polling-only. Real models, Sentinel and Preflight remain unsupported.
Options: presentation-only dashboard; new graph/query/router dependencies; native
React routes, a bounded query cache, stable domain graph and additive stored progress.
Chosen: REST snapshots with persisted SSE for both job types, ID deduplication and
snapshot recovery; 64-entry server-state cache with selection/drawers separate. A
read-only authenticated session projection verifies the local capture key and
redacts/bounds display without creating keys. Complete capture, replay admission,
mode and integrity are separate. 0005_workspace appends immutable regression events
in the same transaction as each transition. Existing signed artifacts are unchanged.
One controlled occurrence selection synchronises graph, event, details and intervention
comparison. Original fixed-layout SVG/HTML and tables avoid inferred causal edges.
Native dialogs provide focus containment; brief CSS transitions respect reduced motion.
Why: real counters/results survive refresh, duplicate events cannot inflate trials,
and a source can remain inspectable while its replay mode is unsupported.
Trade-offs: local single-user auth and owned simulator only; no generic real-model
integration or production deployment. Narrow original routes/cache require explicit
maintenance. Asset-only service worker caches no API evidence and shows offline errors.
Sourcing: 21st-discovered Card/Empty adapted from exact reviewed MIT upstream source,
with local unmodified OFL fonts; no registry installer or extra runtime dependencies.
Evidence: full design/API/source review; root 92/92 tests; browser 25/25 plus final
targeted exact-text/restore/pending checks; fifteen inspected journey layouts.
Exact paths, source provenance, observed fixes and limits: evidence/P6-UI.md.
Revisit: real API admission, full Sentinel/Preflight APIs, larger graph/query scale,
multi-user deployment, offline evidence retention or a separately authorised model budget.
Affected: workspace routes/components/styles, API projection, Ledger events/SSE,
0005 migration, generated contracts, asset build, tests and source/context docs.
## ADR-018 — Atomic owned tool effects and exact mandate-bound operator decisions

Date: 2026-10-15 (Asia/Calcutta). Status: ACCEPTED for P7 owned simulator mechanism.
Question: how can Sentinel fail closed and approve an eligible action exactly once
without implying a generic agent pause/resume or production delivery guarantee?
Context: recorder/P6 UI and P5 presets exist; full signed mandates/approvals do not.
Provider authorisation remains $0; Gemini's exploratory request cap is exhausted.
Options: ordinary click overriding any denial; external RPC with a crash gap;
signed immutable mandates plus transactional owned database tools and durable state.
Chosen: existing pinned Ed25519 key/domain-separated mandates and policy audits;
service-owned agent/session binding; authenticated local-user operator; exact action/
args/session/mandate/actor/expiry grant. BEGIN IMMEDIATE rechecks scope/validity/
budget and atomically consumes approval, writes the local mock effect, appends audit
and records retry receipt. Unique IDs and immutable effect/approval rows prevent reuse.
Explicit denials are terminal; operator denial leaves the in-scope verdict separate
from current deny enforcement. Pending deadlines persist lazily on read/decision;
timeout/cancel records that the tool call cannot resume. Owned stateless continuation
uses the recorded result, with exact summary/owner-send task checks.
Why: a complete, reviewable P7 mechanism can be proved without paid inference or
unreviewed external dispatch. Rules inspect semantics, not planted scenario labels.
Trade-offs: the atomic boundary is the owned SQLite sink, not stdio/remote MCP.
No multi-user/external identity/key anchor, generic framework pause/resume, editing
mandate API, anomaly detector or FPR claim. Policy evidence is a signed sidecar to
the captured source; historical Ledger bundles are unchanged. A new authorised
mandate version would invalidate held old-version approval, not override hard denial.
Deny-and-investigate commits intent/denial first, then queues one action-keyed bounded
Forensics job on the earlier observation-only full source. Queue failure never
releases the tool; intent/link/failure remain reviewable and retryable.
Evidence: root 125/125; risk suite includes scopes, trust, races, stale args/mandates,
shared budget, interrupted atomic commit and restart. EXP-010 actual four protected
executions, seven source investigation trials and separate-process trusted-key check.
UI gate/status/screenshots: evidence/P7-SIM.md. Initial 4/4 browser checks passed;
final full browser 29/29 in 5.4m and final three-viewport renders reviewed.
Revisit trigger: P9/production transport requiring idempotent receiver, unknown
delivery state, agent framework integration, authenticated multi-user mandate issuer,
separately authorised model budget or measured held-out anomaly baseline benefit.
Affected: rewind_core/sentinel, 0006_sentinel, local API/auth integration, Sentinel.tsx,
workspace.css, capability/contracts/schema, tests, benchmark and context/source docs.
