# Current project state

Updated 2026-10-14 (Asia/Calcutta). P5-SIM VERIFIED. P4-SIM verified.
P3-REAL experimental CLI only; full real gate unverified. P1-P10 authorised.

Working: owned synthetic MCP tools, encrypted ordered capture, trusted signed
trace/seal verification, isolated fresh simulator trials, observable provenance,
transparent ranking/coverage, bounded discovery and frozen independent confirmation.
P4 stochastic default N=40/max three finalists; alpha=.05/m, Newcombe intervals,
threshold .20; deterministic N=1/no CI. No optional stopping or playback inference.
Durable SQLite jobs, local cookie/Origin/CSRF, persisted-before-SSE events,
idempotency, cancellation, leases and interruption preserve actual stored status.

P5: versioned stored-fact records, original seal/config/fixture/tool/model digests,
all candidate scope/counts/interval metadata, captured policy/approval trail,
synthetic row-instance impact and explicit limits. Ed25519 binds report/trace/trials;
AES-GCM encrypts immutable stored bundles. Authenticated download and bounded
independent CLI verification require an explicitly supplied trusted public key.
Governance mapping pending; no exact external source control read.

Original-attack regressions use fresh private worlds and unchanged input. Vulnerable
configuration fails; behavioural fix prevents attempts; containment blocks dispatch
while retaining attempts. Both require exact ticket summary AND owner-requested
sends. Blanket-denial control fails useful work. Preset containment is not full
Sentinel/approval enforcement. Immutable plans/results, two-trial budgets, worker
heartbeats, cancellation/interruption and same-case version comparison work.

Modes: simulator verified; playback recording only; local model absent. Gemini
exploratory CLI works, but real API/Forensics/regressions are unsupported. User
provided ignored api.txt and authorised declared free tier/spend $0. Original
three-request Gemini cap exhausted; P5 made no provider requests. Billing unverified.
No general production agent/tool support, public app deployment or compliance claim.
Local signing trust has no external anchor; integrity is not truth or individual blame.

Storage head: 0004_ledger. Current phase P5. Dependencies/locks unchanged except
additive package inclusion. Worker image sha256:763e9c95f02be674769c4ee285cb039b357a8bc5a5973e72d0e8976a553b1c62;
13 isolation probes pass. Rebuild/probe after replay worker changes.

Commands (PowerShell):
```
python scripts/rewind.py setup
.venv/Scripts/python.exe -m rewind_replay.cli setup
.venv/Scripts/python.exe -m rewind_replay.cli probe
python scripts/rewind.py dev
python scripts/rewind.py check
npm run test:e2e
.venv/Scripts/python.exe scripts/p5_benchmark.py
.venv/Scripts/python.exe -m rewind_ledger.cli verify --bundle docs/project/evidence/p5-example/evidence.json --trusted-public-key docs/project/evidence/p5-example/trusted-public.ed25519
```
Dev starts API, web and shared investigation/regression worker. API alone queues.
CLI guide: packages/rewind_ledger/README.md; Gemini guide: rewind_replay/GEMINI.md.

P5 evidence: docs/project/evidence/P5-SIM.md and P5-ARTIFACTS.json.
Actual EXP-004: artifacts/p5/EXP-004/20261014T101549809036Z/: seven valid source
trials, ten valid regression trials; fail/pass/fail/pass/fail for declared versions.
Original malicious occurrence unchanged; owner-send control added before capture.
Independent CLI authentic verification and three artifact-tamper refusals pass.
Committed p5-example bundles preserve actual synthetic outputs and public demo key.
Full repository check: 87/87 in 373.88s, artifacts/p5/check-first.log and
artifacts/checks/20261014T101550529821Z/pytest.xml. After raw-byte upload fix,
15/15 focused P5 tests in 18.26s; unit-final.xml. Final lint/format/schema/types/
build/manifest pass. Existing 15 browser checks pass in the second full run;
P5 three journeys pass after identity binding, final desktops at
artifacts/browser/2026-10-14T10-43-47-906Z/, mobile at 10-47-39-965Z/.
All required renders inspected. Earlier failures retained; no single 18/18 claim.

GitHub publication authorised: pranshujain8532/Rewind-full, default main. New
commit identity Pranshu Jain / 241415102+pranshujain8532@users.noreply.github.com,
explicitly selected by user. Preserve previous history; no fabricated dates/authorship.
Code e756deb and evidence/context 70d7a01 published to origin/main successfully.
Publication handoff marker follows; no pending P5 implementation/verification.

Next exact product task: prompts/06-FRONTEND.md (P6), full evidence/session explorer,
accessible comparison and remaining rendered journey. Real-mode admission/budgets
remain a separate unfinished follow-up. Native Linux/WSL host, fresh-machine install,
remote/private deployment, full Sentinel and Preflight are unverified/planned.
