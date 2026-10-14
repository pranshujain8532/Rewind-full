# Component source and licence register

No third-party UI component has been copied/imported in P0. The shell is original
React/CSS implementation; current P6 reviewed imports are recorded below.

## Discovery sources

- https://21st.dev/
- https://21st.dev/community/components/s/navigation-menu
- https://21st.dev/community/components/s/card
- https://21st.dev/@dillionverma/library/magic-ui
- https://ui.shadcn.com/docs/registry
- https://reactflow.dev/learn
- https://motion.dev/docs/react

These discovery links do not establish a licence for every component.

## Imported-component register

| ID | Component / purpose | Exact source URL | Author / version | Licence and evidence | Local path | Changes | Verification |
|---|---|---|---|---|---|---|---|
| P6-UI-01 | Card / composable evidence panels | [21st exact listing](https://21st.dev/@shadcn/components/card); [reviewed upstream source](https://github.com/shadcn-ui/ui/blob/30a58d4498f270af1c1e981a7d78a15cf5740841/apps/v4/registry/new-york-v4/ui/card.tsx) | shadcn; revision 30a58d4498f270af1c1e981a7d78a15cf5740841; retrieved 2026-10-14 | MIT; listing and pinned upstream LICENSE.md read; notice in apps/web/public/licenses/shadcn-MIT.txt | apps/web/src/ui/primitives.tsx | Native React props/slots retained; REWIND CSS replaces Tailwind/cn; semantic h2/p title/description | Verified; evidence/P6-UI.md and final three-viewport renders |
| P6-UI-02 | Empty / honest empty and unavailable states | [21st exact listing](https://21st.dev/@shadcn/components/empty/outline); [reviewed upstream source](https://github.com/shadcn-ui/ui/blob/30a58d4498f270af1c1e981a7d78a15cf5740841/apps/v4/registry/new-york-v4/ui/empty.tsx) | shadcn; same pinned revision; retrieved 2026-10-14 | Listing omits licence; linked author's repository MIT licence read at pinned revision, notice retained | apps/web/src/ui/primitives.tsx | Composite structure/slots adapted; removed unused media/CVA variants and cn; semantic headings/paragraphs and original SVG | Verified; actual empty/error/offline screens and three-viewport renders |

For each import record retrieval date, dependencies, local changes, attribution obligations, security review and tested viewports. Preserve required notices.

## Fallback record

~~~text
Wanted component:
Observed blocker:
Source/terms checked:
Permitted alternative:
Why it fits the design:
Local path:
Actual verification:
~~~

Never write “from 21st.dev” unless that source was actually used.

## P0 original UI and runtime dependency review — 2026-10-13

`apps/web/src/App.tsx` and `styles.css` implement the original empty workspace,
capability cards and responsive navigation. No upstream component code, registry
command, remote font, image or telemetry was added. Local system fonts are used.
Screenshots at 1440×900, 1280×720 and 390×844 were inspected; final browser 4/4.

| Dependency | Source / version | Inspected licence evidence | Usage |
|---|---|---|---|
| React | https://github.com/facebook/react / 19.3.0 | installed node_modules/react/LICENSE: MIT | UI runtime, not copied component source |
| Vite | https://github.com/vitejs/vite / 8.3.4 | installed node_modules/vite/LICENSE.md: MIT core plus bundled notices | Dev/build tool; notices retained |
| plugin-react | https://github.com/vitejs/vite-plugin-react / 6.1.2 | installed package metadata: MIT | React integration |
| Playwright | https://github.com/microsoft/playwright / 1.64.0 | installed node_modules/playwright/LICENSE: Apache-2.0 | Browser verification only |
| Official MCP SDK | https://github.com/modelcontextprotocol/python-sdk / 2.3.0 | installed dist-info metadata: MIT; client API/source inspected | In-process P0 SDK smoke only |

Runtime dependency trees are locked. npm lifecycle scripts were disabled during
install/ci; native Vite build still passed. No dependency source was vendored or
its licence notices removed. Future copied components need the full register above.

P1: no copied UI added. Original shell adapted to live simulator/playback capability
states and dynamic backend phase; three target viewport renders inspected. New
browser evidence goes to timestamped artifacts/browser directories. The first P1
run reused inherited P0 paths; overwritten P0 files must not be treated as original
P0 revision artifacts (see evidence/P1.md). Future runs preserve separate output.


## P2/P3 runtime additions — 2026-10-13

No imported UI components. Capture/replay code is original repository code.
Direct cryptography 50.0.2 pin is the already-locked primitive dependency;
official docs: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
and https://cryptography.io/en/latest/hazmat/primitives/aead/.
Container uses official python:3.13.12-slim and uv 0.13.0; resolved runtime image
identity recorded in data/replay-runtime.json. Source/dependency versions in locks.
Exact base digest observed in Docker build output; tag refresh requires deliberate
rebuild/probe. No third-party application source was copied in these phases.

## P4 statistics and original browser controls — 2026-10-14

Forensics.tsx, provenance/ranking, jobs and worker are original repository code.
No UI registry component, external font/image/telemetry or copied application code.
Final corrected-count renders inspected at all three viewports; browser 12/12.

statsmodels 0.14.6 is deliberately pinned, rather than silently adopting a newer
API. Official API inspected: https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html
and release https://pypi.org/project/statsmodels/0.14.6/. Installed proportion.py
was inspected: Newcombe combines Wilson marginal bounds for independent binomial
samples. The API is explicitly called with compare=diff, method=newcomb, alpha=0.05/m.
Installed statsmodels-0.14.6.dist-info/licenses/LICENSE.txt inspected (BSD terms);
notices retained. No source is copied or vendored.

New locked transitive stack: NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, patsy 1.0.3
plus dateutil/six/tzdata. Installed NumPy licence expression includes BSD-3-Clause,
0BSD, MIT, Zlib and CC0-1.0; NumPy LICENSE.txt/libdivide notices inspected.
SciPy dist-info LICENSE.txt and bundled uarray licence, and pandas dist-info LICENSE
were inspected (BSD-3-Clause); bundled notices remain intact. Full resolved pins
and hashes live in uv.lock; selected runtime manifest is versions.json.

## Gemini REST adapter — 2026-10-14

Original repository code; no copied SDK/component source, new dependency or lock
version. Existing Python 3.13 standard-library urllib/ssl/json transport is used.
The provider documentation was inspected for current request schema, authentication,
model availability, token counting, structured JSON, seed and pricing:

- https://ai.google.dev/gemini-api/docs/api-key
- https://ai.google.dev/api/generate-content
- https://ai.google.dev/gemini-api/docs/generate-content/structured-output
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/billing
- https://ai.google.dev/gemini-api/docs/rate-limits

Actual catalog/generation accepted the pinned gemini-3.1-flash-lite model. Text-only
standard paid prices pinned on 2026-10-14: $0.25 input/$1.50 output per million tokens,
used only to reserve a paid cap when paid mode is separately authorised. This user
authorised declared free tier/$0 only. Key identity does not prove project billing.
No provider function executor is enabled: structured proposals go to owned mocks.
The no-network worker contains no credentials; parent transport restricts endpoints.
DOM eligibility controls and updated copy are original UI. Final three-viewport
renders and test paths are referenced in evidence/P3-REAL.md. Tests' display controls
and fake HTTP replies are labelled unit-only; they are not runtime measurements.

## P5 Ledger and original-attack UI — 2026-10-14

rewind_ledger, Ledger.tsx, bundle verifier, regression jobs and mobile scroll region
are original repository code. No copied SDK/UI component, new dependency/version,
external font, telemetry or hosted service. Existing cryptography 50.0.2 Ed25519 and
AES-GCM APIs are reused with a separate signing domain and identity-bound encryption;
official API/licence sources remain in the P2 entry. Source images/protocol remain
the pinned owned runtime; no generative report service is used.
Current API contracts generated from Python. Three Ledger renders inspected; browser
and raw experiment artifacts are referenced in evidence/P5-SIM.md. Public examples
are actual synthetic experiment outputs with explicit trust limitations, not inserted
runtime measurements. No exact external governance control was imported or mapped.

## P6 source review — 2026-10-14

Reopened the verified 21st navigation/card/Magic UI discovery pages. Inspected exact
Card, Empty/Outline and Sidebar pages. Card and Empty fit evidence panels and clear
capability states; upstream source was retrieved and read before adapting it. Their
21st previews contain demo imports, not the complete primitive implementation; the
register links the exact author source used. No registry/install command was run.
Source review does not imply that the unrelated demo code or dependencies were imported.

Raw bounded source retrieval manifest: artifacts/p6/sources/review.json. Pinned
shadcn source SHA-256: Card ef8305b12c3112dab42a4708b41b1ebcc042fa5ab4c20f039da8d45b09ed5059;
Empty 54f529ccf72c18c4b5abd5586a7cf1f2a4c8d207aac366029d66ed095cb2965d;
MIT licence 1564074e13439397221ffd522e2e504d56561994a23d371aa5e3ad43e4f5423f.
Card upstream depends on React/cn and Tailwind classes. Empty additionally uses
class-variance-authority for media variants. Adaptation uses the already locked
React 19.3.0 only; no cn, CVA, Tailwind, icon package, package script or runtime
dependency was added. Full required MIT notice is served and committed locally.

Sidebar was reviewed but not copied: it adds Slot/CVA/lucide and its own provider/
sheet dependencies. Original semantic navigation and native dialogs fit the bounded
workspace. Magic UI collection/Number Ticker was considered but not imported:
interpolated counters would display values that are not stored trial facts. Original
stable SVG/HTML provenance, tables, evidence comparisons and 160ms state transitions
avoid force simulation and additional graph/motion dependencies. These are original
REWIND components; no claim that they were copied from 21st, React Flow or Motion.
There was no login/paywall/licence bypass; no unperformed import is claimed.

Locally bundled fonts, retrieved unchanged with full SIL OFL 1.1 notices from
google/fonts revision e9678a5385322c63730122ba464765baad83cfd8:

| Asset | Exact source | SHA-256 | Local path / notice |
|---|---|---|---|
| Source Sans 3 variable, Adobe | https://raw.githubusercontent.com/google/fonts/e9678a5385322c63730122ba464765baad83cfd8/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf | 042fe2cc0b933e328410d7acbd0aa6a1873dca5aef81875f4bc214b08825c7b9 | public/fonts/SourceSans3.ttf; public/licenses/SourceSans3-OFL.txt |
| IBM Plex Mono Regular, IBM | https://raw.githubusercontent.com/google/fonts/e9678a5385322c63730122ba464765baad83cfd8/ofl/ibmplexmono/IBMPlexMono-Regular.ttf | 6a3412f058c7d8dfd9170c41e85ade48e5156ecb89356110ca57a0a27734af46 | public/fonts/IBMPlexMono-Regular.ttf; public/licenses/IBMPlexMono-OFL.txt |

Both full OFL licences read; font bytes/names unmodified and notices preserved.
Local original icons/favicon have no external asset dependency. The offline shell
caches local assets only, never API/trace/trial responses. No remote fonts, images,
tracking, executable hostile HTML, provider/browser secrets or paid inference added.
Actual final screenshots, behaviours and limitations: evidence/P6-UI.md. Complete
browser suite 25/25 plus targeted final exact-preview/restore checks; all three
viewport journey renders inspected. No registry install or unsupported import claim.

## P7 original Sentinel and reused primitives — 2026-10-15

Sentinel.tsx, policy/lifecycle/audit code, database mock tools and p7_benchmark.py
are original repository code. Existing reviewed Card/Empty, original badges/icons/
dialogs and bundled OFL fonts are reused without copying additional third-party
source. No dependency/version/lock, registry install, remote asset, telemetry,
model training or provider request is added. Existing cryptography 50.0.2 signing/
AES-GCM interfaces and SQLAlchemy/Alembic SQLite APIs remain pinned.

Official primary sources read for the atomic boundary and trust primitive:
https://www.sqlite.org/lang_transaction.html and
https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/.
SQLite permits a single writer; BEGIN IMMEDIATE serialises the critical decisions.
The owned effect lives in that same transaction. No claim extends this property
to an external tool server. Ed25519 verification uses the separate pinned key,
not a key supplied with an untrusted mandate. Installed primitive usage is already
reviewed in P2; no move to the documentation site's development version occurred.

First three-viewpoint renders inspected; review corrected stacked action placement
after a long mobile run list, cramped description headers and inconsistent current
enforcement display. Final exact screenshot paths/status: evidence/P7-SIM.md.
## P8 original Preflight and owned SDK reads - 2026-10-15

Core/preflight, Preflight.tsx, durable APIs/jobs, fixture insertion code and the benchmark
are original repository code. Existing reviewed Card/badges/dialog/table/font assets
are reused; no copied third-party component, remote asset, telemetry, new dependency,
lock version or registry installer. The existing MCP SDK 2.3.0/server implementation
and licence remain the already reviewed official MIT package.

Inspected installed `mcp/server/mcpserver/server.py` list_tools/call_tool and actual
result conversion before using public owned-server calls inside the container. Read
the official SDK repository/README at https://github.com/modelcontextprotocol/python-sdk;
its linked https://py.sdk.modelcontextprotocol.io/ is retained as a reference. No SDK source was
copied; original rewind_sandbox/server.py supplies the same owned tool functions.
Direct in-process SDK reads are disclosed; this does not claim a new MCP transport.

Ticket comments and support-note text are reviewed synthetic repository payloads,
not imported attacks or arbitrary remote content. Scope/lineage/version information:
core/preflight/README.md, fixtures.py and frozen run plans. Existing Docker limits,
Ed25519/AES-GCM recorder and source investigation contracts are reused. Exact build,
probe/source hashes and rendered viewport evidence: evidence/P8-SIM.md/P8-ARTIFACTS.json.
