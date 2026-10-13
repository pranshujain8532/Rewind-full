# Task board and acceptance gates

Status vocabulary: TODO / IN_PROGRESS / BLOCKED / IMPLEMENTED / VERIFIED.
IMPLEMENTED means code exists; VERIFIED means the named gate passed.

| ID | Phase | Task / gate | Status | Depends on | Evidence |
|---|---|---|---|---|---|
| P0 | Bootstrap | API/web startup, versions, commands, context | VERIFIED | None | 5/5 pytest; 4/4 browser; locked setup/check/demo/dev; evidence/P0.md |
| P1 | Sandbox | Synthetic clean/attack/control scenarios and local sinks | VERIFIED | P0 | docs/project/evidence/P1.md |
| P2 | Capture | Recorder + adapter + signed chain + tamper tests | VERIFIED | P1 | docs/project/evidence/P2.md |
| P3-SIM | Replay | Isolated simulator and honest playback separation | TODO | P2 | Not run |
| P3-REAL | Replay | Fresh real-model decisions under controlled intervention | TODO | P2, model availability | Not run |
| P4 | Investigation | Valid discovery/confirmation/statistics/jobs | TODO | Valid P3 mode | Not run |
| P5 | Ledger | Trusted verification and original-attack regression | TODO | P4 | Not run |
| P6 | Frontend | Real-data investigation journey and visual/accessibility QA | TODO | P4, P5 | Not run |
| P7 | Sentinel | Mandate checks and safe approval lifecycle | TODO | P2, P6 | Not run |
| P8 | Preflight | Owned sandbox suite with actual counts and budgets | TODO | P3, P4, P6 | Not run |
| P9 | MCP | Authorised tools via tested pinned protocol | TODO | P5, P8 | Not run |
| P10 | Release | Held-out evaluation, demo, fallback, handoff | TODO | Chosen delivery scope | Not run |
| P11 | Research | Optional methods beat baseline on declared criterion | TODO | P10 or explicit rescope | Not run |

## Current slice

Task: P1 in progress; P0 baseline rechecked and checkpointed.  
Acceptance: P0 gate verified on Windows; Linux/container/fresh-machine not_run.  
Owner: implementation session with Pranshu.  
Next prompt: `prompts/01-SANDBOX.md`; run root `python scripts/rewind.py check` on resume.

## Verified P0 subgates

| ID | Acceptance | Status | Evidence |
|---|---|---|---|
| P0-API | Loopback HTTP starts; migrated storage ready; zero available agent modes | VERIFIED | `artifacts/p0/http-smoke.json`, `tests/test_p0.py` |
| P0-WEB | Live backend state, empty/unavailable states, no fatal console errors | VERIFIED | `artifacts/p0/playwright.json`, three inspected screenshots |
| P0-CONTRACT | Separate enum axes; generated OpenAPI/types with no drift | VERIFIED | `artifacts/p0/check.log`, repository schemas |
| P0-DEPS | Exact requirements/locks/manifest; supported selected MCP revision | VERIFIED | `versions.json`, two locks, explicit SDK revision smoke |
| P0-DEV | Setup, combined dev, check/build and honest demo commands work | VERIFIED | Locked reinstall, HTTP dev checks and Ctrl+C listener cleanup |
| P0-DOCS | Context matches actual files/tests/environment | VERIFIED | STATE/HANDOFF/DECISIONS/SESSION-LOG and evidence/P0.md |

## Precise P1 acceptance tasks (not started)

Environment follow-up ENV-DOCKER (SESSION-002): **VERIFIED** daemon availability.
`docker version`, `docker info` and `docker context show` succeeded: client/server
29.6.2, Linux/amd64, desktop-linux context. Evidence:
`artifacts/environment/SESSION-002-docker.json`. No container launch or REWIND
isolation test was run; P1/P3 task statuses and all run modes remain unchanged.

| ID | User outcome / boundary | Acceptance and proof | Status |
|---|---|---|---|
| P1-MCP | Owned ticket/files/mail mock servers | Stdio calls all three with SDK 2.3.0 / revision 2026-07-28; stdout protocol-only; mail writes local synthetic outbox only | TODO |
| P1-FIXTURES | Versioned reproducible synthetic scenarios | Six manifests: clean, single injection, harmless imperative, pair interaction, redundant sources, authorised external action; `.example` recipients; reproducible digests | TODO |
| P1-TRUTH | Evaluator labels cannot affect decisions/ranking | Separate evaluator metadata/interface; subject-agent/ranking envelopes contain no ground-truth labels or fixture verdict IDs | TODO |
| P1-MODES | Transparent playback/simulator/real-model boundary | Simulator works; playback uses recordings without fresh-trial claims; real modes raise capability errors with no silent fallback | TODO |
| P1-OUTCOMES | Safety and useful work measured separately | Versioned predicates inspect tool/recipient/attachment semantics; attempts separate from execution; required ticket facts checked independently | TODO |
| P1-STATE | Runs cannot inherit earlier side effects/memory | Configuration and initial-world snapshot recorded per run; cloned state and independent outbox tests pass | TODO |
| P1-DEMO | Incident can be explained and reproduced | CLI clean/attacked runs differ as expected, label simulated mode, retain useful-task checks; scenario suite passes with only local sinks | TODO |
| P1-DOCS | Engineering history stays accurate | STATE/TASKS/SESSION-LOG/HANDOFF updated with actual commands/evidence, no P3 isolation or real-model claim | TODO |

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

