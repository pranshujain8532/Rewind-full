# Handoff

Updated 2026-10-14 (Asia/Calcutta). P5-SIM VERIFIED; real investigations unsupported.
User explicitly requested P5 and authorised GitHub pushes, superseding the P4-REAL
next-task note. Do not restart, reset user work, alter old authors or backdate commits.

Read AGENTS, STATE, TASKS, ADR-014/015/016, EXP-003/008/004 and recent bugs.
Current code: rewind_ledger contracts/evidence/bundle/store/regression/worker/CLI;
0004_ledger migration; authenticated API; original Ledger.tsx browser controls.
Shared persistent worker handles investigation and regression queues exclusively.
Original attack world/input is bound to the signed source; no ablation in regression.

Evidence record fields derive from trace/trial artifacts, not a model. Counts,
findings/intervals, coverage, original seal/config/fixture/tool digests, actual mock
impact, uncaptured approvals and pending governance stay explicit. Stored bundles
are encrypted and immutable. Trusted-key verification is independent of API/DB;
8 MB JSON limit, depth/node bounds, schema/signer/digest checks and fact projection.
Unknown/incomplete/invalid evidence cannot become a successful regression.

Regression versions: vulnerable-v1 interprets original directives, no enforcement;
behavioural-v1 retains input but ignores external executable directives;
containment-v1 retains attempts and checks owned recipient allowlist;
deny-all-v1 is a negative task-failure control. Exact summary and required owner
SEND dispatches must both succeed. N=1 per arm, no CI, two fresh trials/turns,
60s default, no paid inference. No full Sentinel signature/approval lifecycle claim.
15s lease/1s heartbeat; interrupted/cancelled trials stay incomplete/inconclusive.
Plans/trials/results/cases/records are immutable; comparisons use the same case.

IMPORTANT: browser verification sends downloaded bytes directly and a separately
selected key hex in X-REWIND-Trusted-Public-Key. JavaScript JSON round-trips round
64-bit seeds and correctly fail signatures. Legacy object wrapper is supported only
for lossless clients. CLI output refuses existing filenames. Local trust is not
external anchoring, observed truth, blame or a compliance certificate.

Actual EXP-004: artifacts/p5/EXP-004/20261014T101549809036Z/. Seven source
Docker trials, ten regression trials. Expected version verdicts fail/pass/fail/pass/
fail; containment residual attempt=1, dispatch=0, task true. Deny-all fails owner
send. Owner send was added before capture; malicious occurrence unchanged. Raw
requests/results and original seals preserved. Independent CLI in separate cwd/no
DB verifies; report/trace/trial modifications fail. Public synthetic example files:
docs/project/evidence/p5-example/. Public key is a demonstration trust assumption.

Checks: root 87/87 in 373.88s, check-first.log and checks/20261014T101550529821Z/pytest.xml;
post-upload-fix focused P5 15/15 in 18.26s; final lint/format/schema/build/manifest pass.
Second full browser run passes 15 existing checks; corrected P5 journeys pass at all
three viewports. Final desktop renders: browser/2026-10-14T10-43-47-906Z/;
mobile: browser/2026-10-14T10-47-39-965Z/. Inspected detail/full renders. Original
failures retained: unit fixture used untyped mode; browser rounded seeds, old-run
assertion race, short confirmation wait and mobile min-content overflow. No single
18/18 browser result is claimed. No optional P5 checks remain.

Image 763e9c95f02be674769c4ee285cb039b357a8bc5a5973e72d0e8976a553b1c62,
13 actual isolation probes pass. Runtime image contains the new mock enforcement.
P4 source/statistics protocol unchanged, statsmodels 0.14.6. Core remains CPU-only.
Gemini key in ignored api.txt; never show its contents. User authorisation declared
free-tier project/$0, previous three-call cap exhausted. P5 performs no provider call.
Gemini CLI exploratory only, two valid/one invalid prior smoke; no real confirmation.

Commands: python scripts/rewind.py dev; check; npm run test:e2e;
.venv/Scripts/python.exe -m rewind_ledger.cli {record,verify,case,run,compare};
.venv/Scripts/python.exe scripts/p5_benchmark.py. API alone leaves jobs queued.
Existing data migrated additively to 0004; no reset/deletion. Git host needs command-
scoped safe.directory for this exact repo; do not change ownership/global trust.

GitHub: https://github.com/pranshujain8532/Rewind-full.git, public empty remote/main
verified. User selected noreply identity 241415102+pranshujain8532@users.noreply.github.com;
name pranshu jain. New commits/push authorised; preserve older Codex-authored history.
Code/context commits and push still pending final delivery; secrets/private keys/local
DB/artifacts excluded, actual public synthetic sample retained for review.

Next exact task: prompts/06-FRONTEND.md. Full session/evidence explorer and accessible
comparison journeys. Real P3/P4 gates, native Linux/WSL host/fresh machine, remote
hosting, Sentinel and Preflight remain unsupported/not_run/planned respectively.
