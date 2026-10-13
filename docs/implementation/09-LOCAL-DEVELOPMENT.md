# Local development and isolation boundaries

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
outside the worker with credentials and a non-zero authorised budget. It never
grants general networking or arbitrary connector access to the worker.

No runnable `docker run rewind-replay` example is advertised: the image does not
exist yet. Linux setup, WSL startup, container execution and all isolation negative
tests are **not_run** in this session. P1 can implement owned synthetic local
mocks independently; that does not prove P3 isolation.
