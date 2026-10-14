# Task board and acceptance gates

Status vocabulary: TODO / IN_PROGRESS / BLOCKED / IMPLEMENTED / VERIFIED.
IMPLEMENTED means code exists; VERIFIED means the named gate passed.

| ID | Phase | Task / gate | Status | Depends on | Evidence |
|---|---|---|---|---|---|
| P0 | Bootstrap | API/web startup, versions, commands, context | VERIFIED | None | 5/5 pytest; 4/4 browser; locked setup/check/demo/dev; evidence/P0.md |
| P1 | Sandbox | Synthetic clean/attack/control scenarios and local sinks | VERIFIED | P0 | docs/project/evidence/P1.md |
| P2 | Capture | Recorder + adapter + signed chain + tamper tests | VERIFIED | P1 | docs/project/evidence/P2.md |
| P3-SIM | Replay | Isolated simulator and honest playback separation | VERIFIED | P2 | docs/project/evidence/P3-SIM.md |
| P3-REAL | Replay | Fresh real-model decisions under controlled intervention | IMPLEMENTED | P2, model availability | Gemini exploratory CLI; EXP-008 two valid/one invalid; full real gate unverified |
| P4 | Investigation | Valid discovery/confirmation/statistics/jobs | VERIFIED | Valid P3 mode | Simulator only; evidence/P4-SIM.md; full check 64/64, browser 12/12, actual EXP-003 |
| P5 | Ledger | Trusted verification and original-attack regression | VERIFIED | P4-SIM | evidence/P5-SIM.md; actual EXP-004, independent CLI, 87 tests plus post-upload focused 15, three rendered P5 journeys |
| P6 | Frontend | Real-data investigation journey and visual/accessibility QA | VERIFIED | P4, P5 | Supported API/simulator journey; evidence/P6-UI.md; 92 tests, browser 25 + final targeted checks; 15 reviewed layouts |
| P7 | Sentinel | Mandate checks and safe approval lifecycle | VERIFIED | P2, P6 | Owned simulator/database tools; evidence/P7-SIM.md; root 125, final mechanism 33, full browser 29 plus affected 8; EXP-010 |
| P8 | Preflight | Owned sandbox suite with actual counts and budgets | VERIFIED | P3, P4, P6 | Fixed owned simulator suite; evidence/P8-SIM.md; root 150/150, final mechanism 25/25, full browser 33/33, actual EXP-011 |
| P9 | MCP | Authorised tools via tested pinned protocol | TODO | P5, P8 | Not run |
| P10 | Release | Held-out evaluation, demo, fallback, handoff | TODO | Chosen delivery scope | Not run |
| P11 | Research | Optional methods beat baseline on declared criterion | TODO | P10 or explicit rescope | Not run |

## Current slice

P8 VERIFIED for the fixed owned suite (2026-10-15), recovered clean 709ff0d. Reviewed owned-target
suite across actual isolated ticket comments and mock file text; frozen versions,
resource caps, shared-worker leases, partial captures, invalid coverage and failure
navigation implemented. 150/150 repository tests, 25/25 final mechanisms, initial
4/4 initial browser and EXP-011 actual suites/limits/investigations pass. Final full
browser 33/33 in 8.1m; three viewports reviewed. Local migration preserves all data.
Published source 5e62cc8aa54e4a1491968c6b73e0fc459462344a verified on origin/main;
exact source/artifact hash binding is in evidence/P8-ARTIFACTS.json.
Next task prompts/09-MCP-TOOLS.md; P9 not started.
No provider call, LLM variations, classifier/evasion claim or evolutionary generation.

P7 VERIFIED for owned simulator/database tools (2026-10-15). Recovered clean 373a0e8.
Signed scope evaluator, exact local authenticated single-use approvals, atomic effects,
hard-denial protection, expiry/cancel/denial errors, shared budgets, races/rollback/
restart, source investigation links and real-event UI pass the supported gate.
Root 125/125; full browser 29/29; final affected mechanism 33/33 and P7/P0 browser
8/8 after terminal-result/maturity refinement. Three states at three viewports reviewed.
Additive migration preserves all prior rows; actual EXP-010 and independent verifier
pass. Exact logs/source/artifact references: evidence/P7-SIM.md/P7-ARTIFACTS.json.
$0/zero provider calls, no anomaly/FPR or general MCP/real-agent claim. Historical
P7 next task was P8, now verified above.

P6 VERIFIED for the supported API/simulator journey. Exact gate, raw references,
licences, fifteen layouts, screenshot-led fixes and limits: evidence/P6-UI.md.
Root 92/92; browser 25/25 plus targeted exact-text/restore/pending checks. Bounded
read-only trace, persisted SSE, lossless seed display, refresh/reconnect/duplicates,
keyboard and offline assets pass. Additive migration preserves existing records.
No provider calls or fabricated Sentinel/Preflight integrations.
Historical P6 next task was P7, now verified above. P3/P4 real gates remain unsupported.

P5-SIM VERIFIED on 2026-10-14. User explicitly requested this phase, superseding
the earlier P4-REAL next task below. Signed stored-fact downloads, independent
trusted-key verification, unchanged original attack, behavioural/containment contracts,
immutable manifests, budgets/leases and same-case comparison pass the supported gate.
Actual EXP-004: seven source trials and ten regression trials; vulnerable fails,
correct fixes pass safety AND owner task, residual attempts remain visible, deny-all
fails useful work. Invalid source/trial evidence cannot pass. No paid/real inference.
Current acceptance matrix and exact paths: evidence/P5-SIM.md. Remaining P5 checks
none. Code/evidence originally e756deb/70d7a01, now d10873c/80cb213 after the user's
explicit Git identity correction; published successfully to origin/main.
Attribution maintenance VERIFIED: four Codex author/committer identities corrected,
seven commit trees/messages/dates preserved, local backup verified, lease-protected
push and remote-head read passed. Evidence: evidence/GIT-IDENTITY-20261014.md.
Historical artifact revisions/signatures remain intact and resolve through that map.
Historical P5 next task was P6; it is now verified. Current next task is P9 above. Preserve user work.

P4-SIM VERIFIED. User's Gemini key authenticates and supports fresh remote CLI
trials on the explicitly declared free-tier project with spend $0. EXP-008 is an
exploratory smoke, not confirmation: two valid trials, one invalid tool proposal.
P3-REAL's repeated-input variability and complete contract gate remain unverified;
P4-REAL source admission, durable budgets and confirmation are unsupported.
Historical post-Gemini next task (superseded by the explicit P5 request): P4-REAL,
starting with explicit captured owned-file/tool argument
schemas; integrate the broker with durable reservations/jobs and reject plans that
cannot fit the explicitly configured request/token/time/$0 budget. No additional
live requests under the exhausted three-call smoke cap. Keep N=40/max-three-finalist
proposal and independent-sample/frozen-plan invariants. P5 Ledger follows this mode
decision. Restart from STATE/HANDOFF/ADR-015/EXP-008; preserve all historical evidence.

Gemini slice checks VERIFIED: 72/72 repository tests, lint/format/schema/types/build/
manifest; 15/15 browser journeys, three target renders inspected. Evidence paths
and the separate real-mode acceptance matrix: evidence/P3-REAL.md. Full P3-REAL
and P4-REAL remain unverified; CLI test success cannot enable those findings.

## Verified P0 subgates

| ID | Acceptance | Status | Evidence |
|---|---|---|---|
| P0-API | Loopback HTTP starts; migrated storage ready; zero available agent modes | VERIFIED | `artifacts/p0/http-smoke.json`, `tests/test_p0.py` |
| P0-WEB | Live backend state, empty/unavailable states, no fatal console errors | VERIFIED | `artifacts/p0/playwright.json`, three inspected screenshots |
| P0-CONTRACT | Separate enum axes; generated OpenAPI/types with no drift | VERIFIED | `artifacts/p0/check.log`, repository schemas |
| P0-DEPS | Exact requirements/locks/manifest; supported selected MCP revision | VERIFIED | `versions.json`, two locks, explicit SDK revision smoke |
| P0-DEV | Setup, combined dev, check/build and honest demo commands work | VERIFIED | Locked reinstall, HTTP dev checks and Ctrl+C listener cleanup |
| P0-DOCS | Context matches actual files/tests/environment | VERIFIED | STATE/HANDOFF/DECISIONS/SESSION-LOG and evidence/P0.md |

## Precise P1 acceptance tasks (verified; historical environment notes below)

Environment follow-up ENV-DOCKER (SESSION-002): **VERIFIED** daemon availability.
`docker version`, `docker info` and `docker context show` succeeded: client/server
29.6.2, Linux/amd64, desktop-linux context. Evidence:
`artifacts/environment/SESSION-002-docker.json`. No container launch or REWIND
isolation test was run; P1/P3 task statuses and all run modes remain unchanged.

| ID | User outcome / boundary | Acceptance and proof | Status |
|---|---|---|---|
| P1-MCP | Owned ticket/files/mail mock servers | Stdio calls all three with SDK 2.3.0 / revision 2026-07-28; stdout protocol-only; mail writes local synthetic outbox only | VERIFIED |
| P1-FIXTURES | Versioned reproducible synthetic scenarios | Six manifests: clean, single injection, harmless imperative, pair interaction, redundant sources, authorised external action; `.example` recipients; reproducible digests | VERIFIED |
| P1-TRUTH | Evaluator labels cannot affect decisions/ranking | Separate evaluator metadata/interface; subject-agent/ranking envelopes contain no ground-truth labels or fixture verdict IDs | VERIFIED |
| P1-MODES | Transparent playback/simulator/real-model boundary | Simulator works; playback uses recordings without fresh-trial claims; real modes raise capability errors with no silent fallback | VERIFIED |
| P1-OUTCOMES | Safety and useful work measured separately | Versioned predicates inspect tool/recipient/attachment semantics; attempts separate from execution; required ticket facts checked independently | VERIFIED |
| P1-STATE | Runs cannot inherit earlier side effects/memory | Configuration and initial-world snapshot recorded per run; cloned state and independent outbox tests pass | VERIFIED |
| P1-DEMO | Incident can be explained and reproduced | CLI clean/attacked runs differ as expected, label simulated mode, retain useful-task checks; scenario suite passes with only local sinks | VERIFIED |
| P1-DOCS | Engineering history stays accurate | STATE/TASKS/SESSION-LOG/HANDOFF updated with actual commands/evidence, no P3 isolation or real-model claim | VERIFIED |

P1 depends on P0 and needs no paid service or running Docker daemon. P3 replay
eligibility separately requires proved isolation. No advanced ML scaffolding.

## Add a task

~~~text
ID:
User outcome:
Implementation boundary:
Dependencies:
Acceptance condition:
Test or visible proof:
Status:
Actual evidence:
Blocker and unblock step:
~~~

## Rule

Do not mark the whole phase VERIFIED if only the happy path works. Partial mode completion stays explicit. A screenshot cannot satisfy the replay/statistics/integrity gate.

## P1 — 2026-10-13T06:58:38.786935+00:00 — VERIFIED

Goal: P1 owned synthetic incident. User authorised continuous P1–P10 implementation.

Implemented: typed World/SubjectInput/Action/RunResult, reproducible fixtures and
separate evaluator metadata, three owned stdio tools, explicit model interface,
transparent simulator, saved-recording playback and semantic outcomes. Package
rewind_sandbox joins the single Python distribution. API/empty web shell accurately
expose available CLI modes and unavailable real models. No external tool dispatch.

Commands: local locked uv sync; fixture generate; pytest tests/test_sandbox.py
13/13; root check 18/18 plus lint/format/schema/manifest/types/build; root demo
single scenario succeeds; browser 4/4. See artifacts/p1/check.log, demo.log,
pytest.xml and timestamped artifacts/browser/latest.txt. Screenshots at 1440×900,
1280×720 and 390×844 are inspected. No new dependency versions required.

Failure: first stdio scenario suite 7 failed/6 passed because plain dict MCP
responses had no structured_content. Added bounded single-JSON-text decoding.
First failure XML retained; corrected suite passes. Minor formatting issues fixed.

Evidence handling correction: the inherited browser config reused P0 output paths.
Its first P1 run overwrote P0 overview PNGs and playwright.json; those files now
represent P1, not the original P0 revision. The original P0 manifest retains its
old hashes and historical gate record, but affected raw artifacts do not match it.
Future browser runs use distinct timestamped directories; no replacement artifact
is claimed to be an original P0 screenshot. Existing failed mobile trace copies
and P0 API evidence were retained.

Dossier now exists and was included unchanged in the baseline checkpoint; prior
absence corrected in current summaries. No user changes reset/discarded. No paid
service, public deployment or outbound message. Real-model/isolation gates unrun.

Interview explanation: “Our subject is a transparent instruction-following
simulator. It reads a ticket through real MCP stdio, then interprets supplied
directives and may attempt a synthetic attachment send. Code checks recipient
permission and attachment classification independently of scenario labels. Every
send reaches only a local outbox. Scenario expectations live in evaluator files
that the agent never reads. Playback reads a result without deciding again.
Real models have an explicit capability error, never a hidden simulator fallback.
These checks validate the fixture mechanism, not LLM causation or replay isolation.”

Questions: Why must evaluator labels stay out of SubjectInput? Why are attempted
harm and executed mock dispatch separate outcomes? Answers not yet recorded.

Next: P2 stdio recorder/model adapter, encrypted content, signed ordered chain,
seal/verification, partial-capture disclosure and tamper/correlation tests.

## P2 — 2026-10-13T07:28:15.764586+00:00 — VERIFIED

Goal: P2 recorder/integrity gate; continuous P1–P10 authorised.

Changes: rewind_capture package and migration 0002_capture; three transparent
bounded stdio relays, adapter hooks, encrypted content, immutable events allocated
under BEGIN IMMEDIATE, signed linked hash chain and seal, separately bound
occurrence provenance, independent trusted-key verification and CLI export.
Session metadata binds world/model/configuration and configured local agent role;
external source identity remains unverified. Actual capture is synthetic only.

Commands/outcomes: locked uv sync/migrate, captured redundant and single CLI runs,
P2 suite 13/13, full root check 32/32 including oversized-frame/lifetime shutdown,
envelope follow-up 2/2, root captured demo; trusted-key CLI returns valid=true,
capture_complete=true and no missing payloads. Browser 4/4; screenshots inspected
at 1440×900, 1280×720, 390×844. Build/types/schema/manifest checks pass.
Artifacts: artifacts/p2/check.log, pytest.xml, envelope-check.xml, demo.log,
bundle.json and timestamped browser output 2026-10-13T07-24-16-568Z.

Tamper tests cover edits/insertion/deletion/reordering, altered content, forged
occurrence origin, metadata/seal changes and wrong keys. Missing payloads leave
signed-header integrity valid but replay capture insufficient. Tool-only capture
cannot pass the adapter readiness gate. Concurrent writes have unique contiguous
sequences; database triggers and sealed-session checks prevent accidental edits.

Limits: local trust anchor, no external checkpoint/key-custody assurance. Synthetic
development world/result artifacts are plaintext; persisted evidence payloads are
AEAD-encrypted with separate display redaction. Retention/tombstone service absent.
Only owned stdio tool calls and stateless simulator supported; resources/prompts,
HTTP MCP/unproxied calls/real models unsupported. No replay/network isolation yet.
Explicit cryptography 50.0.2 pin matches already locked installed version; no GPU.

Canonical contract: UTF-8 JSON, sorted keys, compact separators, ensure_ascii=False,
allow_nan=False; Python owns canonical signing/verification. Domain-separated
SHA-256 event hashes include previous hash and session/sequence identity. Ed25519
signs event hashes and the seal separately. AES-GCM uses random 96-bit nonce and
payload digest as associated data. Seal binds count/head/metadata/coverage/occurrences.
Official primitive docs: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
and https://cryptography.io/en/latest/hazmat/primitives/aead/; installed APIs tested.

Interview explanation: “The proxy records bytes at the tool boundary; the adapter
records the exact input given to our supported subject. Content hashes identify
bytes, while occurrence IDs keep origins separate even when two comments match.
A transaction assigns event order. Payloads are encrypted; events form a signed
linked chain and a signed seal commits to its length and head. An independent
verifier needs a separately trusted key. Tampering fails relative to that seal,
but a signature does not establish truth or legal blame. Tool-only capture and
missing payloads remain visibly insufficient for replay.”
Questions: Why isn't a bundled public key a trust anchor? Why do identical bytes
need different occurrence IDs? No comprehension answers recorded.

Next: P3 isolated fresh simulator decisions, interventions, strict matching,
unsupported branches, negative egress/secret/traversal probes and real-model limits.

## P3-SIM — 2026-10-13T08:09:49.714504+00:00 — VERIFIED

Goal: complete P3 simulator gate; real-model gate separately blocked.

Implemented fresh full-snapshot trials, occurrence removals and length-matched
neutral replacements, separate attempted/dispatch/task predicates, cloned private
outboxes, strict recorded reads keyed by tool/schema/arguments/occurrence/state.
An unknown initial or downstream read invalidates the trial without fallback.
Actual transformed requests, fresh responses, digests, seeds and timings are saved.
Playback remains a recording reader and cannot establish intervention effects.

Commands: .venv/Scripts/python.exe -m rewind_replay.cli setup; same module probe;
pytest tests/test_replay.py --junitxml=artifacts/p3/pytest.xml (4/4 passed);
python scripts/rewind.py check (see artifacts/p3/check-repaired.log).
Final full check: 36/36 tests in 97.84 seconds, lint/format/schema checks,
TypeScript/Vite build and dependency manifest passed. New browser screenshots
were not run after the P3 metadata-only shell change; P2 renders remain the last
inspected UI evidence. P6 still requires the full rendered evidence journey.
Thirteen actual container probes passed: non-root, DNS/TCP blocked, no host mount,
credentials, evaluator or Docker socket, read-only source, dropped capabilities,
no-new-privileges and enforced CPU/memory/PID bounds. Host-secret result establishes
absence of declared host mounts; it is not a general kernel security certification.
Traversal and unknown tool/state/schema reads fail closed. Actual batch results:
artifacts/p3/interventions.json; probe: artifacts/p3/isolation-probe.json.
Image identity and build timestamp are pinned locally in data/replay-runtime.json.
No source or secret host bind mounts; all sends terminate in private mock outboxes.

Failed experiment: initial image build used an incorrect root parent; corrected
the path before a successful build. Strict downstream fallback was found in review
and removed before gate completion. No external replay effects were performed.
The first full check failed a proxy lifetime test: its six-second process deadline
included Windows import startup as well as the one-second relay timer. Independent
reproduction passed (artifacts/p3/proxy-followup.xml). The test deadline is now
bounded at fifteen seconds including startup; production relay limits are unchanged.
The failure log is preserved at artifacts/p3/check.log.

Real-model gate BLOCKED: user confirms no local model/runtime; no hosted provider
or authorised budget. No real-model request/trial is claimed. To unblock, choose
a licensed CPU-compatible local runtime/model and implement/test its fresh adapter
inside isolation; alternatively implement the narrowly constrained inference IPC
broker and explicitly authorised provider budget. No service has been purchased.
Deterministic fixture repeats show identical outcomes, not provider determinism.

Interview explanation: We start every trial from the captured world and change
only specified input occurrences before a fresh simulator decision. The worker
runs non-root with no network, no host secrets and explicit resource limits.
Versioned mocks can answer owned-world reads; strict replay instead requires
exact schema, arguments, occurrence and state matches. An unmatched branch stops
the trial. Harm attempts and useful work are separate. These are simulator
experiments; playback and signatures cannot turn them into real-model evidence.
Questions: Why can an unknown read not count as harm absent? Why is a subprocess
insufficient to prove replay isolation?

User requested stopping after context compaction. No P4 implementation started.
Next: prompts/04-INVESTIGATION.md; durable experiment jobs and fixed-plan statistics.

