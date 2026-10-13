# P0 dependency and protocol selection

Checked 2026-10-13 against official documentation and public registry metadata.
The installed versions are in `versions.json`; transitive dependencies and
integrity hashes are in `uv.lock` and `package-lock.json`.

| Choice | Official evidence | Local verification |
|---|---|---|
| Python 3.13.12 | [Python version status](https://devguide.python.org/versions/) | Runtime and five smoke tests |
| Node 22.18.0, npm 10.9.3 | [Node release lines](https://nodejs.org/en/about/previous-releases) | npm install/ci and Vite build |
| React 19.3.0, Vite 8.3.4, plugin-react 6.1.2 | [Vite guide](https://vite.dev/guide/), [releases](https://vite.dev/releases), official npm metadata | Vite requires Node 20.19+ or 22.12+; selected Node meets requirement |
| TypeScript 5.9.3, openapi-typescript 7.13.0 | [Type generator docs](https://openapi-ts.dev/introduction), installed package peer metadata | TypeScript 7.0.2 was rejected by the generator's `^5.x` peer; compatible 5.9.3 resolves/builds |
| FastAPI 0.143.0, Pydantic 2.14.1 | [Version guidance](https://fastapi.tiangolo.com/deployment/versions/), [release notes](https://fastapi.tiangolo.com/release-notes/), official PyPI metadata | Import, OpenAPI generation, real HTTP and smoke tests |
| SQLAlchemy 2.1.4, Alembic 1.20.0 | [SQLAlchemy overview](https://docs.sqlalchemy.org/en/21/intro.html), [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) | Initial migration, repeated upgrade, WAL/readiness checks |
| Uvicorn 0.54.0 | [Uvicorn settings](https://www.uvicorn.org/settings/), official PyPI metadata | Loopback real HTTP startup |
| uv 0.13.0 | [Lock/sync docs](https://docs.astral.sh/uv/concepts/projects/sync/) | Lock and locked editable install |
| MCP 2.3.0 / protocol 2026-07-28 | [Official SDK](https://github.com/modelcontextprotocol/python-sdk), [client docs](https://py.sdk.modelcontextprotocol.io/client/), [versioning contract](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) | In-process tool call with `Client(..., mode="2026-07-28", cache=None)` |
| Playwright 1.64.0 | [Playwright browser guide](https://playwright.dev/docs/browsers), official npm metadata | Browser gate evidence in `docs/project/evidence/P0.md` |

The selected runtime lines are supported; installed patch versions are recorded
without claiming they are the newest patches. FastAPI's Starlette dependency is
resolved by the framework and locked, rather than pinned independently.

## MCP scope

The official v2 SDK explicitly accepts a revision string via its `mode` argument.
The installed source `mcp/client/client.py` documents direct adoption for that
pin; auto negotiation/fallback is not used by the P0 smoke. Response caching is
disabled for the probe. P0 does not add an MCP service to the application.

Only an **in-process SDK call** is verified here. Stdio framing, cancellation,
request correlation, mock servers, recorder coverage and transport compatibility
must pass P1/P2/P9 tests. Do not claim Streamable HTTP support or use the prior
revision's initialise lifecycle for the selected 2026 revision. Dashboard SSE
remains a separate future application API.

## Dependency updates

Change exact requirements deliberately, resolve both locks, regenerate the API
boundary if affected, run the relevant checks, and record the result in project
context. Do not use `--force` or `--legacy-peer-deps` to suppress compatibility
failures. Optional UI/ML/statistics libraries are added only when needed.
