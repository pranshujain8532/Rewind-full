# Task board and acceptance gates

Status vocabulary: TODO / IN_PROGRESS / BLOCKED / IMPLEMENTED / VERIFIED.
IMPLEMENTED means code exists; VERIFIED means the named gate passed.

| ID | Phase | Task / gate | Status | Depends on | Evidence |
|---|---|---|---|---|---|
| P0 | Bootstrap | API/web startup, versions, commands, context | VERIFIED | None | 5/5 pytest; 4/4 browser; locked setup/check/demo/dev; evidence/P0.md |
| P1 | Sandbox | Synthetic clean/attack/control scenarios and local sinks | TODO | P0 | Not run |
| P2 | Capture | Recorder + adapter + signed chain + tamper tests | TODO | P1 | Not run |
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

Task: P0 verified; P1 next, not started.  
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

