# Handoff — read with STATE.md

Last updated: 2026-10-13 (Asia/Calcutta)

## Where we are

P0 is verified on the existing Windows laptop. One editable Python distribution
contains shared contracts/storage and FastAPI; one npm workspace contains React/Vite.
All four agent run modes and recorder/product capabilities are unavailable.
No agent trials or experimental findings exist. HTTP health describes API/storage only.

## User constraints

- Preserve REWIND's globally reviewed idea.
- Make targeted present-day improvements without a major change.
- Implement with GPT 6.1 Sol.
- Build a beautiful live frontend, using permitted 21st.dev or similar components.
- Maintain Markdown context alongside implementation.
- Make the project understandable for future interviews.
- Prefer a low-budget core that does not require a paid GPU.

## Start here

Read AGENTS.md, STATE.md, TASKS.md, relevant DECISIONS.md and the P1 prompt.
Inspect status/files and run relevant P0 checks before modifying anything.

Next task: P1 owned synthetic sandbox (not started).  
Exact prompt: `prompts/01-SANDBOX.md`.  
Commands from root:

```powershell
git -c safe.directory='D:/projects/REWIND-Implementation-Kit - Cx/rewind-implementation-kit' status --short
python scripts/rewind.py setup
python scripts/rewind.py check
python scripts/rewind.py dev
```

Use `npm.cmd` when PowerShell blocks npm.ps1. API/web bind to loopback at 8000/5173.
Stop dev servers before `npm.cmd run test:e2e`. Git was initialised under the agent
sandbox account, so host Git needs command-scoped trust for this known directory.
No global Git setting, ownership, commit, reset, clean or push was changed.

## Critical design boundaries

- Recorder proxy alone is not full model-context capture.
- Playback and simulation are labelled separately from fresh model trials.
- Replay must not execute real external actions.
- Statistics come from completed valid trials under a specified design.
- Regression retains the original malicious input.
- Signatures do not prove truth or legal blame.
- Frontend counters reflect persisted backend progress.

## What to fill after every coding session

Current revision / dirty changes: initial Git repository with no HEAD; files untracked.
Source SHA-256: `6c5a0e65706c72f7ee353f9ce615e8bf6b120f32c52fd8a8361427847616d9bc`.
Last passed gate: P0, five backend/SDK and four browser checks plus build/schema/manifest.
Last exact commands: above; also `python scripts/rewind.py demo` and browser install/tests.
Available agent modes: none; never fall back automatically to simulation.
Environment follow-up (SESSION-002): Docker client/server 29.6.2 responds,
Linux/amd64 in desktop-linux context; two containers already running. WSL2
Ubuntu/docker-desktop still list as stopped. Sanitised daemon evidence:
`artifacts/environment/SESSION-002-docker.json`. No container was started or changed.
Limits: REWIND Linux/container execution and replay isolation remain not_run;
no worker/model/provider/budget configured. Daemon availability alone enables no mode.
Unresolved IDs: R-001–010 (later mechanisms); R-011 (empty supplied reference directory).
Resolved bugs: BUG-001 mobile Refresh accessible name; BUG-002 uv build-suffix parsing.
Decisions: ADR-007 packaging/locks, ADR-008 pinned MCP, ADR-009 enum/schema boundary,
ADR-010 explicit migrations; initial later-phase ADRs remain proposed as recorded.
Next step: three owned mock MCP servers, six scenarios, model boundary, semantic
outcomes and cloned world-state checks. Host-local mocks are not isolated replay.
Evidence/screenshots: `docs/project/evidence/P0.md`, `artifacts/p0/` (including preserved
mobile failure trace). No experimental result is claimed by these engineering checks.

Keep this sufficient for a new session to continue without retelling the project.

