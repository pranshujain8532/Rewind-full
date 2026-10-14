# Local development and isolation boundaries

## Current P3 update — 2026-10-13

P0 sections below preserve historical verification boundaries. P1 owned tools,
P2 signed capture and P3 isolated simulator are now verified. Playback and
simulated modes are available; real-model modes unavailable. API is still read-only.
Windows host plus Linux Docker worker tested; native Linux/WSL host not_run.

```powershell
.venv/Scripts/python.exe -m rewind_replay.cli setup
.venv/Scripts/python.exe -m rewind_replay.cli probe
.venv/Scripts/python.exe -m rewind_replay.cli run --bundle artifacts/p2/bundle.json --trusted-key data/keys/trusted-public.ed25519
```

Use the bundle's separately trusted key. Linux uses .venv/bin/python (host untested).
Setup builds the pinned dependency image; execution requires successful probe and
uses its exact local image ID. Rebuild/probe after worker edits. All 13 probes
passed; no host bind mounts, external networking or actual email dispatch.
Do not put keys in source or outputs. Real-model setup remains blocked and is
documented in docs/project/evidence/P3-REAL.md.

## Historical P0 guide


P0 implements Windows API/web development. It does not implement replay,
authentication, encrypted payloads, signed evidence or production security.

## Current environment, inspected 2026-10-13 (Asia/Calcutta)

- Windows 11 Home Single Language, 25H2, build 26200, x64.
- Windows PowerShell 5.1.26100.9444; Python 3.13.12 from Miniconda;
  Node 22.18.0; npm 10.9.3. pnpm was detected but not selected; its version query
  refused this npm-owned workspace, so no pnpm version is claimed.
- Git 2.55.0.windows.3. The supplied kit had no Git metadata; P0 initialised
  a repository without committing, deleting or resetting existing work.
  Git metadata was created under the sandbox account. Host status uses
  `git -c safe.directory='D:/projects/REWIND-Implementation-Kit - Cx/rewind-implementation-kit' status --short`.
  This command-scoped flag changes no global settings or filesystem ownership.
  An attempted ownership change was rejected by auto-review and not executed.
- Local uv 0.13.0 manages `.venv`; npm manages the web workspace.
- Docker client/server 29.6.2 / API 1.55 now responds after the user started
  the engine (SESSION-002). Server is Linux/amd64, context `desktop-linux`,
  Docker Desktop 4.84.0; two containers already running during the read-only check.
  The separate WSL listing still reports `Ubuntu` and `docker-desktop` stopped.
  During P0 the daemon was unavailable; that historical result is retained.
  No REWIND container or isolation check has run. Podman and Ollama
  were not found. No model adapter/provider/budget is configured by this project.
- Restricted-shell inspection initially hid Docker and denied WSL/CIM access.
  The subsequent read-only host inspection established the facts above.
- `docs/reference/` exists but contains no dossier file in the supplied workspace.
  Its claimed retention in the planning kit cannot be verified. P0 uses the
  corrected implementation contracts; no substitute dossier was manufactured.

## Commands and state

[README](../../README.md) is the executable command guide. Invoke its Python
entry point without activating a venv or changing PowerShell policy. `.tools`,
`.venv`, dependency caches, database files and generated test artifacts are ignored.
API data defaults to the root's `data/`; `REWIND_DATA_DIR` can select a dedicated
local directory. Do not point demo commands at production data.

Migrations are explicit. An unmigrated schema returns HTTP 503 with
`migration_required`; a schema query failure returns `database_unavailable`.
HTTP 200 health means the P0 API/storage foundation is ready, not that agent
features or security controls exist. All four run modes remain unavailable.

For development backup: stop API processes and copy the complete dedicated
data directory (SQLite plus any WAL/SHM files) to a private backup location.
Restore into a separate directory and set `REWIND_DATA_DIR` to that directory,
then check `/api/health`. Backup/restore is **not_run** in P0. No reset command
exists, and setup never drops existing tables. Schema migration is repeatable.

The web dev proxy forwards `/api` to loopback, keeping browser requests on one
origin; the API enables no broad CORS policy. P0 exposes only read-only system
metadata and OpenAPI. No credentials are sent to the browser. Local session
authentication belongs before later mutation endpoints; remote hosting is outside
this gate. Vite's `dist/` build is verified, but a production serving setup is absent.

## Replay path to implement in P3 (not_run, not a P0 capability)

Run API/web natively or in WSL2. Run replay in a **separate non-root Linux
container** via Docker Desktop/WSL2 or a Linux Docker engine. Merely installing
Docker or starting WSL does not make REWIND replay eligible. P3 must build a
pinned offline image containing the worker, owned mock tools, supported model
(where available), dependency lock and fixture versions.

The runtime contract for that future image is:

- `--network none`, `--read-only`, `--cap-drop ALL`,
  `--security-opt no-new-privileges`, explicit non-root UID/GID;
- read-only source/fixture mounts; a bounded writable temporary directory;
- explicit CPU, memory, PID, trial, model-turn and wall-time limits;
- no host home, credentials, environment secrets or Docker socket mounted;
- a new cloned world/memory per trial; every send/write reaches local mocks;
- negative tests for DNS/TCP egress, host secret access, traversal and unknown
  tools before advertising simulator/local-model **replay** readiness.

Hosted re-execution additionally needs a bounded provider-only inference broker
outside the worker with credentials and an explicit affordable billing/budget policy. It never
grants general networking or arbitrary connector access to the worker.

No runnable `docker run rewind-replay` example is advertised: the image does not
exist yet. Linux setup, WSL startup, container execution and all isolation negative
tests are **not_run** in this session. P1 can implement owned synthetic local
mocks independently; that does not prove P3 isolation.

## Current P4 development commands — 2026-10-14

The preceding P0 sections are historical environment/gate notes. The current API
head is `0003_investigation`. Simulator and playback are available; only verified
simulator isolation is eligible for fresh investigation. Gemini has an exploratory
CLI; real fixed-plan Forensics remains unsupported.
`python scripts/rewind.py dev` now starts API, web and one separate persistent
`rewind_eval.worker` process. `api` alone does not start a worker: queued jobs remain
truthfully queued. Run `.venv/Scripts/python.exe -m rewind_eval.worker` separately,
or `--once` to process one job. Setup/migrate remain additive and preserve captures.

The browser establishes a local HttpOnly/SameSite session via `/api/auth/local`.
Mutation requests require an allowed loopback Origin, `X-REWIND-Local: 1`, and
idempotency keys on starts. No broad CORS or remote/private deployment is enabled.
Capture an owned demo in the browser to record P4's benign neutral control. Legacy
captures without that control remain stored but cannot fulfil this experiment plan.

Run `.venv/Scripts/python.exe scripts/p4_benchmark.py` for actual fresh MCP/Docker
experiments; it writes unique EXP-003 directories and a real worker-kill audit.
Run `npm run test:e2e` for real browser journeys and unique screenshot/trace/data
directories. Unit execution stubs stay in tests and never enable production modes.

## Gemini CLI follow-up — 2026-10-14

The user supplied root api.txt and authorised a free-tier project, spend $0. That
file remains unchanged, Git-ignored and Docker-excluded. Backend-only credential
loading, actual catalog access and three live smoke requests were tested. See
packages/rewind_replay/GEMINI.md for commands, limits and capture behavior.
Inference defaults disabled; no paid provisioning/fallback or automatic retry.
The three-call smoke cap is exhausted; browser checks make no provider requests.
Catalog cannot establish project billing; the explicit free-tier declaration is
the configured policy for this slice. New invocations need an explicitly affordable
request/token/time plan and must remain within the user's $0 authorisation.

The API exposes remote mode as experimental CLI-only, unavailable for API/Forensics
investigations. Its signed captures are listed but disabled in the simulator picker.
CLI partial captures and invalid proposals are not findings. STATE and P3-REAL
evidence describe the failed neutral control and next admission/budget task.

## Current P5 Ledger — 2026-10-14

Storage head 0004_ledger is additive. The shared rewind_eval.worker now handles
queued investigations and regressions with exclusive claims. API alone queues work.
Use the browser's signed-record/download/original-attack controls after an investigation,
or rewind_ledger.cli {record,verify,case,run,compare}. Guide:
packages/rewind_ledger/README.md. Reviewable actual synthetic samples and separately
selected demonstration public key: docs/project/evidence/p5-example/.
Independent verification opens no DB/API and never infers trust from a bundled key.
CLI exports refuse existing filenames; stored bundles/manifests are encrypted and
immutable. Only bounded simulator regressions are supported; no P5 provider call.
For API verification send original bytes and X-REWIND-Trusted-Public-Key. Lossy
JS parse/stringify alters large seeds and must fail verification.
P5 acceptance evidence: docs/project/evidence/P5-SIM.md. P6 is the next product
phase; native Linux/WSL host/fresh-machine/public serving remain not_run/unsupported.
