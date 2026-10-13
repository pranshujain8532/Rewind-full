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

