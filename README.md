# REWIND

Accountability infrastructure for AI agents: one recorder supporting Forensics,
Ledger, Sentinel and Preflight. Prepared for Pranshu Jain.

P0 implements the local application foundation: typed readiness/capabilities,
migrated SQLite storage and a web workspace. Agent recording, simulation,
replay, experiments, enforcement and signed records belong to later phases.

## Start locally (PowerShell)

Use Python **3.13** (tested 3.13.12), Node **22** (>=22.12, tested 22.18.0),
and npm **10** (tested 10.9.3). Setup downloads dependencies once. No model,
provider key, GPU or paid service is required. Run from the repository root:

```powershell
python scripts/rewind.py setup
python scripts/rewind.py dev
```

Open **http://127.0.0.1:5173**. API health is
http://127.0.0.1:8000/api/health, capabilities are `/api/capabilities`,
and API documentation is `/docs`. Ctrl+C stops the development process trees.
The API and web server bind to loopback. Use `npm.cmd` directly in PowerShell
when the system blocks the `npm.ps1` wrapper; no execution-policy change is needed.

To start each service in a separate terminal:

```powershell
python scripts/rewind.py migrate
python scripts/rewind.py api
# Second terminal
python scripts/rewind.py web
```

## Check and demonstrate the foundation

```powershell
python scripts/rewind.py check
python scripts/rewind.py demo
npm.cmd run browsers:install
npm.cmd run test:e2e
```

`check` runs lint/format verification, generated-schema drift checks, backend
smoke tests, frontend type check/build and dependency-manifest checks. Browser
tests start their own servers, so stop development servers first. Chromium
is downloaded under `.tools/playwright`; later browser runs can be offline.

The current `demo` runs the single-injection deterministic simulator through three
owned stdio MCP tools. Its attempted send reaches only a local synthetic outbox;
this is not an LLM experiment or isolated replay. Browser tests
use a separate database under `artifacts/p0/browser-data`. Evidence is written
in timestamped `artifacts/browser` directories (latest.txt identifies the run).
See [P1 evidence](docs/project/evidence/P1.md) and the historical P0 index.

After changing a backend contract:

```powershell
python scripts/rewind.py schemas
python scripts/rewind.py check
```

Python owns `packages/rewind_core/contracts.py`; repository OpenAPI and generated
TypeScript form the shared boundary. Do not edit generated types by hand.
`uv.lock`, `package-lock.json` and [versions.json](versions.json) record the
selected versions. Setup uses locked installs and disables npm lifecycle scripts.
Runtime patches can be updated deliberately within the selected Python/Node
lines; rerun verification and refresh the manifest when doing so.

## Linux / WSL2 development and future isolation

Linux instructions are **not_run** in P0. Install Python 3.13 and Node 22/npm 10
in the Linux environment and clone/copy source without `.venv`, `.tools`,
`node_modules`, `data` or `artifacts` from Windows. From the repository root:

```bash
python3 scripts/rewind.py setup
python3 scripts/rewind.py check
python3 scripts/rewind.py dev
# Optional browser verification after installing Chromium's Linux system libraries
npm run browsers:install
npm run test:e2e
```

WSL2 is a Linux development path; by itself it does not disable external network
access. [The replay environment guide](docs/implementation/09-LOCAL-DEVELOPMENT.md)
specifies the container boundary to implement and prove in P3. No replay image
or worker exists in P0, and native subprocesses do not provide isolation.

## Repository boundaries

| Path | Role |
|---|---|
| `apps/web` | React client, original REWIND shell, generated API types |
| `services/api/rewind_api` | FastAPI read-only P0 endpoints |
| `packages/rewind_core` | Shared contracts and SQLite bootstrap |
| `packages/rewind_capture` | P2 recorder/adapter boundary, currently documentation |
| `packages/rewind_replay` | P3 isolation/re-execution boundary, currently documentation |
| `packages/rewind_eval` | P4/P5 experiment/regression boundary, currently documentation |
| `sandbox`, `fixtures` | P1 owned mocks and scenario boundaries, no fixtures yet |
| `migrations`, `schemas`, `scripts`, `tests` | Storage, contracts, commands and verification |
| `docs/project` | Current state, decisions, evidence and handoff |

There is one editable Python distribution; later modules can join it without
adding services. Dependencies for graph UI, ML and statistics are deferred until
their implementation phase. See [STATE](docs/project/STATE.md) for current truth.
The exact next assignment after the P0 gate is **`prompts/01-SANDBOX.md`**.
