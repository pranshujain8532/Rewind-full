# Session log

Append factual entries. Do not erase failures or rewrite historical results.

## PLAN-001 — 2026-10-09 — Implementation kit

Goal: convert the user-supplied dossier into an understandable build plan, phased prompts and living documentation.

Completed:
- Preserved the accepted product modes.
- Corrected replay, coverage, statistical and integrity assumptions.
- Defined small current improvements and frontend sourcing workflow.
- Created prompts and context templates.

Software changes: none; this deliverable is planning documentation.  
Runtime tests: not run; application not implemented.  
Next: execute P0 in the build repository.

## Session entry template

~~~text
SESSION-NNN — date/time and timezone
Goal:
Starting revision / dirty-tree status:
Task IDs:
Files changed:
What works now:
Why the change was needed:
Commands run and working directory:
Actual outcomes:
Evidence paths:
Failed attempts / unresolved issue IDs:
Decision IDs:
What Pranshu learned or decided:
Documentation updated:
Exact next action:
Ending revision / dirty-tree status:
~~~

## SESSION-001 — 2026-10-13 — P0 (Asia/Calcutta)

Goal: execute the user's P0 assignment through its verified gate, preserving
the accepted concept and existing planning kit. This assignment stops at P0.

Starting state: specs/prompts/templates only, no application, no Git repository.
Inspected AGENTS, start guide, STATE/HANDOFF, corrected architecture/roadmap,
active task/decisions, frontend/verification docs and P1 boundaries. No secrets printed.

Environment: Windows 11 Home Single Language 25H2 build 26200 x64; PowerShell
5.1.26100.9444; Python 3.13.12; Node 22.18.0; npm 10.9.3; Git 2.55.0.windows.3.
Docker CLI 29.6.2 is installed but Linux-engine daemon unavailable. WSL2 Ubuntu
and docker-desktop are stopped; Podman/Ollama not found. No configured project
model/provider/budget. Restricted-shell inspection initially hid host facts;
read-only host inspection corrected them. docs/reference is empty, recorded R-011.

Modified: new modular directories, one Python distribution, core contracts/storage,
FastAPI read-only endpoints, Alembic 0001_p0, original React/CSS shell,
OpenAPI/generated types, root CLI and browser wrappers, version manifest/two locks,
five API/SDK smoke tests, four browser cases and engineering evidence index.
Captured environment and restart facts; no P1 agent/mocks or ML model scaffolding.

Versions: uv 0.13.0; FastAPI 0.143.0; Pydantic 2.14.1; SQLAlchemy 2.1.4;
Alembic 1.20.0; Uvicorn 0.54.0; official MCP 2.3.0 / protocol 2026-07-28;
React 19.3.0; Vite 8.3.4; plugin-react 6.1.2; TypeScript 5.9.3;
openapi-typescript 7.13.0; Playwright 1.64.0. Full transitive versions/hashes in locks.
Official documentation/registry sources: implementation/10-P0-VERSION-SOURCES.md.

Commands from repository root (exact fuller index in evidence/P0.md):
- `python -m venv .tools`; `.tools/Scripts/python.exe -m pip install uv==0.13.0`.
- `.tools/Scripts/uv.exe lock --cache-dir .tools/uv-cache` and locked sync.
- `npm.cmd install --ignore-scripts --no-audit --no-fund --cache .tools/npm-cache`.
- `python scripts/rewind.py setup`, `check`, `demo`, `dev`.
- `npm.cmd run browsers:install`, `npm.cmd run test:e2e`.
- `.venv/Scripts/python.exe scripts/record_p0_evidence.py`.

Actual outcomes: locked reinstall/migration/generation checks passed. API real
HTTP reports ready WAL/revision, available_modes empty. Final pytest 5/5; type
check/build/lint/format/schema/manifest checks pass. Final browser 4/4 with no fatal
page/console errors on normal startup; backend outage/recovery works. Screenshots
inspected at 1440×900, 1280×720 and 390×844. Combined dev web/API/proxy returned
HTTP 200; Ctrl+C stopped both listeners (interrupted PTY shell returned 1).

Actual failed attempts and repairs:
- Restricted network/CIM/WSL calls denied; host access used for necessary downloads/inspection.
- TypeScript 7.0.2 peer conflict: changed to compatible 5.9.3, no override flags.
- Initial SDK test keyword wrong (4 pass/1 fail): inspected v2 `mode` API, final 5/5.
- uv version build suffix rejected by setup: parser corrected, complete setup passes.
- Playwright wrapper CLI subpath unexported: resolved exported package manifest/installed CLI.
- First browser run 3/4: mobile hidden text removed accessible name; aria-label fixes it, final 4/4.
- Auto-review denied recursive .git ownership change without explicit authorisation.
  Action not executed; command-scoped read-only Git status already works. No global
  trust/ownership settings changed; ENV-002 retained.

Evidence: artifacts/p0/check.log, pytest.xml, playwright.json, browser.log,
http-smoke.json, api-startup.log, demo.log, dev-smoke.json, dev-shutdown.json,
three overview PNGs, outage PNG, preserved first mobile failure JSON/log/trace,
evidence-manifest.json. These are engineering checks, not causal experiments.
Revision: no Git HEAD/commit; untracked original/new files. Source SHA-256:
`6c5a0e65706c72f7ee353f9ce615e8bf6b120f32c52fd8a8361427847616d9bc`.

Limits: Linux/WSL/container execution, isolation negative tests, fresh-machine
install and backup/restore not_run. No recorder/replay/statistics/signing/enforcement,
authentication, model trials or production security. Core foundation needs no GPU/paid API.

Decisions: ADR-001 and ADR-005 accepted for observed P0 scope; ADR-007–010 accepted
with evidence. Later mechanism ADRs remain proposed. No numerical result invented.

Docs updated: STATE, TASKS (precise P1 acceptance), DECISIONS, SESSION-LOG, HANDOFF,
BUGS-AND-RISKS, INTERVIEW-NOTES, COMPONENT-SOURCES, EXPERIMENTS, evidence/P0.md,
implementation/03-ARCHITECTURE, 09-LOCAL-DEVELOPMENT, 10-P0-VERSION-SOURCES and README.
Learning: request-flow explanation and two practice questions recorded; no claim
that Pranshu has already answered/mastered them. Session duration not measured.

Final audit: source hash/test counts agree with STATE and evidence; STATE is
94 lines. Lint/format verification passes after documentation edits. Git ignore
checks confirm local raw artifacts, data, tools/venv and node_modules are ignored.
Repository files are created but remain uncommitted; no clean-checkout test is claimed.

Exact next action: `prompts/01-SANDBOX.md`, after user starts the next assignment.
No P1 execution in this session; no public deployment, outbound message or paid provisioning.

## SESSION-002 — 2026-10-13 — Docker availability follow-up (Asia/Calcutta)

Goal: check the Docker engine the user has started. Acceptance: client/server
version and daemon information queries respond, with current facts recorded.
Scope: read-only engine/WSL inspection and environment documentation; no P1 build,
image download, container launch/stop, replay test or dependency change.

Starting/ending revision: initial uncommitted repository, no HEAD; existing work
preserved. P0 gate remains verified and P1 remains TODO. Read repository guidance,
STATE/HANDOFF/TASKS and relevant ADR/environment entries before changing summaries.

Commands from repository root:
- `docker version`: succeeds; client/server Engine 29.6.2, API 1.55;
  server Linux/amd64, Docker Desktop 4.84.0 (234817).
- `docker info --format '{{json .}}'`: selected non-secret fields checked;
  daemon responds, two containers running, zero stopped, 12 CPUs, 8171167744 bytes RAM.
- `docker context show`: desktop-linux.
- `wsl --list --verbose`: Ubuntu/docker-desktop still listed stopped, both WSL2.
- Repository-specific command-scoped `git status --short`: untracked original/new
  files remain; no ownership/global settings changed.

Evidence: `artifacts/environment/SESSION-002-docker.json`, timestamp
2026-10-13T06:31:44.8533111Z. Records selected versions/context/container count,
with REWIND replay unimplemented/unverified and container_launch_test not_run.
No container names, credentials or environment secrets recorded.

Updated: STATE.md, TASKS.md, HANDOFF.md, BUGS-AND-RISKS.md and
implementation/09-LOCAL-DEVELOPMENT.md; this SESSION-LOG entry appended.
ENV-001 resolved for daemon availability only. No application code/lock/manifest
change; prior P0 evidence retained. Application tests not_run on this follow-up
because only environment summaries changed and read-only daemon queries verify
the requested condition. No worker/isolation or real-model capability is enabled.

Next assignment remains `prompts/01-SANDBOX.md`, when requested by the user.


## P1 — 2026-10-13T06:58:38.786935+00:00 — VERIFIED

Starting revision: `7a58bfe57f55f4d2e0b9d36e953bf3bc93f6a64f`.

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

Starting revision: `40a13992483e53d5426d2017e7e9a2461d5dabcb`.

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

