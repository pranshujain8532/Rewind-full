# Current project state

Last updated: 2026-10-13  
Phase: P0 VERIFIED; P1 not started  
Software implementation status: working local API/storage/web foundation

## Goal

Implement the accepted REWIND recorder, Forensics, Ledger, Sentinel and Preflight. Make small reliability, evidence and UX improvements without changing the product idea.

## Available now

- FastAPI health/capabilities/OpenAPI endpoints with no credentials exposed.
- Explicit SQLite WAL migration `0001_p0` and honest HTTP 503 readiness states.
- React shell driven by backend state, loading/empty/error/retry states.
- Separate run-mode, feature-maturity and evidence-status enums.
- Generated API types, Python/npm locks, exact version manifest.
- Reproducible setup/dev/check/demo entry points and five backend/four browser checks.
- Corrected implementation specs, phase prompts and living project context.

P0 code now includes typed health/capabilities endpoints, SQLite WAL migration,
an empty React workspace, and setup/dev/check/demo entry points. No agent modes,
trained model, benchmark result or deployment is available.

## Current modes

| Mode | Availability | Verified evidence |
|---|---|---|
| Recorded playback | Not implemented | None |
| Simulator | Not implemented | None |
| Local model re-execution | Not implemented | None |
| Hosted model re-execution | Not implemented | None |

## Environment

Repository: `D:\projects\REWIND-Implementation-Kit - Cx\rewind-implementation-kit`.  
OS: Windows 11 Home Single Language 25H2, build 26200, x64; PowerShell 5.1.  
Python 3.13.12; Node 22.18.0; npm 10.9.3 via npm.cmd; uv 0.13.0 in .tools.  
MCP: official Python SDK 2.3.0 / selected revision 2026-07-28.  
Model / provider / budget: not configured; adapters not implemented.  
Docker client/server 29.6.2 responding; Linux/amd64, `desktop-linux` context.  
Daemon availability rechecked in SESSION-002; two containers currently running.  
WSL2 Ubuntu/docker-desktop still reported stopped by the separate WSL listing.  
Podman/Ollama not found. Container/replay isolation is unimplemented and unverified.  
Full versions: `versions.json`; official sources: `docs/implementation/10-P0-VERSION-SOURCES.md`.

## Actual working commands

All from repository root, Windows PowerShell:

```powershell
python scripts/rewind.py setup
python scripts/rewind.py dev
python scripts/rewind.py check
python scripts/rewind.py demo
npm.cmd run browsers:install
npm.cmd run test:e2e
```

Web: `http://127.0.0.1:5173`; API: `http://127.0.0.1:8000/api/health`.
P0 demo checks HTTP readiness/capabilities, not an agent scenario.
After backend contract edits: `python scripts/rewind.py schemas`.

## Current blocker

No P0 gate blocker remains. No recorder, replay, statistical attribution, signing,
policy enforcement or production security exists. Linux/WSL/container execution,
fresh-machine setup, backup/restore and isolation tests are not_run. The supplied
`docs/reference/` is empty (R-011). Host Git ownership quirk is documented in
`09-LOCAL-DEVELOPMENT.md`; no ownership changed and no commit exists.

## Next action

Exact next assignment: `prompts/01-SANDBOX.md`; precise P1 acceptance tasks in TASKS.md.
This assignment ends at P0; no P1 code has been implemented.

## Active decision references

ADR-001, ADR-005 (P0 scope) and ADR-007–010 accepted with evidence.
ADR-002/003/004/006 retain later-phase verification requirements.

## Last verification

`check`: lint/format, schema/manifest checks, TypeScript/build pass; pytest 5/5.  
`demo`: real HTTP ready, WAL/revision correct, available modes empty.  
Browser: 4/4 pass, no fatal page/console errors on normal startup; 1440×900,
1280×720 and 390×844 visually inspected, plus outage/recovery and keyboard refresh.  
Locked setup and combined dev startup checked; Ctrl+C stops both listeners.  
Docker follow-up: version/info/context queries succeeded; no container launched.
Evidence: `artifacts/environment/SESSION-002-docker.json`; replay isolation unchanged.  
Evidence: `docs/project/evidence/P0.md`, `artifacts/p0/evidence-manifest.json`.  
No Git HEAD; source snapshot SHA-256:
`6c5a0e65706c72f7ee353f9ce615e8bf6b120f32c52fd8a8361427847616d9bc`.

## Operating rule

Keep this file short and current. Link to experiment/decision IDs for detail. Never change a capability to verified without commands and evidence.

