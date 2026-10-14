# REWIND

Accountability infrastructure for AI agents: one recorder supporting Forensics,
Ledger, Sentinel and Preflight. Prepared for Pranshu Jain.

The local implementation includes encrypted signed capture, isolated simulator
replay, durable investigations, transparent ranking and fixed-plan statistics,
plus signed evidence and original-attack defence regressions. The browser connects
Session Explorer, Investigation, Evidence Record and Regression through stored facts
and durable SSE. Reviewed licensed components, local fonts, keyboard/table alternatives
and an offline asset shell preserve a calm investigation workspace. Sentinel adds
signed mandates, exact single-use approvals, fail-closed scope checks and durable
policy events for owned simulator tools. Preflight remains unavailable.
Gemini has an experimental, explicitly budgeted CLI; real-model confirmation remains
unsupported. Simulator and playback need no GPU or paid model service.

Current UI proof, real screenshots, source licences and limitations:
[P6 verification](docs/project/evidence/P6-UI.md),
[component provenance](docs/project/COMPONENT-SOURCES.md).

Sentinel commands, atomic mock-sink boundary and current gate:
[Sentinel guide](packages/rewind_core/sentinel/README.md),
[P7 verification](docs/project/evidence/P7-SIM.md).

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
# Third terminal: investigations and regression jobs
.venv/Scripts/python.exe -m rewind_eval.worker
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
use a separate database under each browser artifact directory. Evidence is written
in timestamped `artifacts/browser` directories (latest.txt identifies the run).
The demo now also captures and exports a signed bundle. See the phase evidence
under docs/project/evidence. Its host mock run is separate from isolated replay.

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

## Linux / WSL2 development and replay isolation

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
documents the verified P3 Linux Docker boundary. Native Linux/WSL host setup
remains untested; the Linux worker was tested through Windows Docker Desktop.
Native subprocesses do not provide network isolation.

With the Docker Linux engine running, build and probe once (PowerShell):

```powershell
.venv/Scripts/python.exe -m rewind_replay.cli setup
.venv/Scripts/python.exe -m rewind_replay.cli probe
.venv/Scripts/python.exe -m rewind_replay.cli run --bundle artifacts/p2/bundle.json --trusted-key data/keys/trusted-public.ed25519
```

Use your captured bundle and its separately trusted key. Add `--remove` followed
by captured occurrence UUIDs for an intervention. Rebuild/probe after changing
worker code. Execution uses the pinned local image ID, no network, no host mounts,
non-root UID, read-only source and bounded resources. It never starts real inference.
On Linux replace `.venv/Scripts/python.exe` with `.venv/bin/python` (host not_run).

## Repository boundaries

| Path | Role |
|---|---|
| `apps/web` | React client, original REWIND shell, generated API types |
| `services/api/rewind_api` | Authenticated local capture, investigation and Ledger APIs |
| `packages/rewind_core` | Shared contracts and SQLite bootstrap |
| `packages/rewind_capture` | Bounded recorder, encrypted payloads, signed capture/verifier |
| `packages/rewind_replay` | Isolated simulator and strict-read replay worker |
| `packages/rewind_eval` | Provenance, bounded discovery, fixed statistics and durable jobs |
| `packages/rewind_ledger` | Signed stored-fact records, independent verifier and original-attack regressions |
| `sandbox`, `fixtures` | Versioned owned mocks and synthetic scenarios |
| `migrations`, `schemas`, `scripts`, `tests` | Storage, contracts, commands and verification |
| `docs/project` | Current state, decisions, evidence and handoff |

There is one editable Python distribution; later modules can join it without
adding services. Statistics use the documented pinned independent-sample method.
See [STATE](docs/project/STATE.md) for current gates and limitations.

## Evidence and defence regression

Complete an investigation in the browser, create its signed record, download the
bundle and run a behavioural or containment regression. Both arms receive the full
original attack. Containment can block dispatch while retaining harmful attempts;
the result reports those attempts and useful task completion separately.

Independent verification requires a trusted public key supplied explicitly:

```powershell
.venv/Scripts/python.exe -m rewind_ledger.cli verify --bundle evidence.json --trusted-public-key data/keys/trusted-public.ed25519
.venv/Scripts/python.exe scripts/p5_benchmark.py
```

[Ledger guide](packages/rewind_ledger/README.md) documents commands, APIs, bounds,
configuration versions, byte-preserving uploads and the trust assumption. Signing
detects changes relative to a trusted key; it does not prove truth, blame or compliance.
[Gemini guide](packages/rewind_replay/GEMINI.md) describes the exploratory hosted path.
Credentials, private keys and local databases are excluded from version control.
