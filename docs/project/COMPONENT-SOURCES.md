# Component source and licence register

No third-party UI component has been copied/imported in P0. The shell is original
React/CSS implementation; exact 21st/shadcn sourcing remains a P6 task.

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
| — | None imported yet | — | — | — | — | — | — |

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

