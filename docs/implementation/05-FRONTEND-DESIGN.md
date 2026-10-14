# 05 — Frontend design and live component plan

## Product direction

Build a polished investigation workspace: calm, precise and immediately understandable. It should feel like an incident-analysis instrument with excellent typography and motion.

The centrepiece is **synchronised before/after evidence**: select an input, see where it entered the run, watch trials complete, compare resulting actions, and inspect the signed finding.

Do not spend the visual budget on a decorative landing page. The main product opens with one clear action: “Run demo scenario” or “Open latest investigation.”

## Design tokens

Proposed starting tokens; verify contrast in the actual browser.

| Token | Dark theme | Light theme |
|---|---|---|
| Canvas | #0B0F14 | #F5F7FA |
| Surface | #141B23 | #FFFFFF |
| Raised surface | #1B2530 | #EEF2F6 |
| Primary text | #EDF2F7 | #17212B |
| Muted text | #A9B7C6 | #526273 |
| Border | #334252 | #CED7E0 |
| Selection / information | #79AFFF | #175CD3 |
| Verified / successful | #5ED6B3 | #087F5B |
| Testing / caution | #F2BC68 | #9A5B00 |
| Harm / deny | #FF8585 | #B42318 |

Use an available, locally bundled sans-serif font and a monospace font for hashes, timings and IDs. Body 14–16px minimum, strong 24–32px page titles, tabular figures for changing values. Use 4/8px spacing increments, restrained 10–14px radii and subtle borders. No essential text over animated backgrounds.

## Layout

At 1440×900:
- Left navigation: approximately 216px.
- Top bar: approximately 56px, with project, session and run-mode badge.
- Main workspace: a flexible centre column plus a 320px details panel.
- Bottom evidence console: collapsible, not permanently stealing half the screen.

At 1280×720, close the details panel into a drawer. At tablet widths use tabs. At phone width provide a readable summary and table alternative to the graph.

Page routes:
- /overview
- /sessions/:sessionId
- /investigations/:investigationId
- /sentinel
- /preflight
- /ledger/:recordId
- /regressions
- /settings

Disabled capabilities display why they are unavailable. A roadmap feature must not have a working-looking button that produces an invented result.

## Screen contracts

| Screen | Main question | Main content | User action |
|---|---|---|---|
| Overview | What needs attention? | Latest runs, held actions, investigations, coverage | Run scenario / open incident |
| Session explorer | What did the agent see and do? | Scrubbable timeline, graph, selected-step evidence | Select step / start investigation |
| Investigation | What changed when this input changed? | Baseline vs intervention, candidate tiles, real counts, intervals | Compare / cancel / inspect trial |
| Sentinel | Can this action proceed? | Proposed action, mandate, reasons, actor and deadline | Approve eligible hold / deny / investigate |
| Preflight | Which tested surfaces failed? | Trials, numerator/denominator, task success, uncertainty | Run suite / open failure |
| Ledger | What evidence can I verify? | Signed report, scope, counts, manifest and limitations | Download / verify / create regression |
| Regressions | Does the fix still work? | Safety + task status, configuration comparison | Rerun original attack suite |

### Session explorer

Use a horizontal overview timeline and a vertically readable event list. Each item has an action icon, text label, sequence, time and mode. Clicking synchronises graph selection and the details drawer.

Graph nodes: input occurrence, tool result, model call, proposed action and policy event. Edges mean observable relationships such as “included in input” or “produced response.” Dashed inferred edges must carry an “inferred” legend. Do not label graph ancestors causal before an intervention has tested them.

Use a stable layered layout rather than a constantly moving force simulation. Preserve node positions when updating evidence.

### Investigation workspace: the signature interaction

The top comparison shows:
- Original input: target attempted x0/n0.
- Intervention: target attempted x1/n1.
- Effect: delta and interval level/method.
- Useful task: separate result in each condition.
- Mode and evidence coverage.

Below, an intervention grid animates only when real backend events arrive:
- Neutral: not tested.
- Amber + text “Testing”: running.
- Blue + text “Inconclusive”: evidence insufficient.
- Muted + text “No detected effect”: this particular test did not support a change.
- Accent + text “Supported effect”: confirmation gate passed.
- Hatched / icon + text “Unsupported”: replay could not evaluate.

The dossier's “grey = ruled out / red = guilty” labels are intentionally replaced. They overstate what an experiment establishes.

Selecting a tile reveals exact occurrences changed, transformation type, actual trials, baseline and intervention action traces, task-success evidence and limitations. Red remains reserved for harmful actions or denials.

Show actual execution duration. If a presentation mode replays saved events slowly, label it “Recorded playback — 0.5×”; do not inflate live compute time to make an animation impressive.

## 21st.dev sourcing workflow

The user's “21devs” request is interpreted as **21st.dev**.

Inspected source entry points, 9 October 2026:
- [21st.dev](https://21st.dev/)
- [Navigation collection](https://21st.dev/community/components/s/navigation-menu)
- [Card collection](https://21st.dev/community/components/s/card)
- [Magic UI collection](https://21st.dev/@dillionverma/library/magic-ui)
- [shadcn registry documentation](https://ui.shadcn.com/docs/registry)

These are verified discovery pages, **not a claim that a particular component has already been imported or licence-reviewed**. In P6 select exact component pages and inspect their source and terms.

| UI need | Source direction | Integration rule |
|---|---|---|
| Sidebar / command navigation | shadcn sidebar and command; inspect 21st navigation options | Keyboard operable, no hover-only navigation |
| Metric cards | One restrained 21st card pattern | Actual API data, no hard-coded improvement numbers |
| Trial counter | Inspect a number ticker from an available author source | Reduced-motion fallback; semantic live text |
| Details panel | shadcn sheet / resizable primitives | Focus management and mobile drawer |
| Progress and empty state | shadcn base + small sourced animation if useful | Real loading/error/empty semantics |
| Provenance DAG | React Flow | Custom domain nodes, evidence-based edges |
| Intervention grid | Original REWIND component + Motion | This is domain-specific; do not force a marketing block into it |
| Confidence interval chart | Recharts/custom SVG | Honest axis, signed effect range and accessible table |

### How Sol must import a component

1. Discover a candidate from the official page, public registry or author repository.
2. Inspect source, dependencies, licence and accessibility. Verify that reuse is permitted.
3. Record exact URL, author, licence, retrieved date and component path in COMPONENT-SOURCES.md.
4. Copy or install only the chosen component via its observed documented command. Inspect any package scripts before execution.
5. Adapt all colours, spacing, typography and interactions to the REWIND tokens.
6. Remove telemetry, external image/font dependencies or unrelated features where not needed.
7. Connect it to real API state.
8. Build and test it, then capture a screenshot at the target viewport.

Do not invent registry commands. Do not bypass login, paywalls or licence requirements. If a source is inaccessible, use a suitable permitted shadcn component or an original equivalent and record the reason. Aim for at least two genuine sourced components when available, not a large collection of inconsistent styles.

The current 21st site supports component prompts and shadcn registry installation, but access and author terms vary. Inspect each chosen item at implementation time.

## Live data architecture

REST supplies the initial snapshot. Application SSE supplies incremental progress. The query cache owns server state; selection, panels and filters are UI state.

Reconnect behaviour:
1. Keep the last received event ID.
2. Request subsequent events.
3. Deduplicate by ID.
4. Refresh snapshot when history is unavailable.
5. Show reconnecting/offline/stale badges.
6. Stop subscriptions when leaving the job.

Persisted server progress remains authoritative after refresh. A counter cannot run from setInterval and pretend trials are completing.

## Required shared components

- ModeBadge: recorded / simulated / local model / hosted model.
- EvidenceStatus: prior / exploratory / confirmed under test / unavailable.
- EffectEstimate: delta, interval, interval level, method and counts.
- CoverageBadge: complete / partial / replay unavailable.
- IntegrityStatus: trusted-key result and limitations.
- ActionDiff: baseline and intervention action sequences.
- ProvenanceNode: occurrence-specific evidence.
- EmptyState, ErrorState and PermissionState.
- CopyIdentifier: announces success accessibly.

Mode and evidential status are separate dimensions. A measured simulator result is still a simulator result.

## Visual and interaction acceptance

- Inspect actual screenshots at 1440×900, 1280×720 and approximately 390px mobile width.
- No clipped text, overlapping nodes, horizontal page overflow or inaccessible actions.
- Hover, focus, selected, loading, success, error, cancelled, stale and empty states exist.
- All destructive demo resets require clear dataset scope.
- Keyboard can open an incident, inspect evidence and download a record.
- Graph has an accessible event-table alternative.
- Colour never carries meaning alone.
- Motion uses brief transitions, generally 120–240ms; honour prefers-reduced-motion.
- Untrusted ticket text is rendered as text, never executable HTML.
- Actual timings are measured. Proposed target: simple interactions <100ms, usable main view <2s for a 100-event local fixture. Record hardware and results rather than claiming those numbers in advance.

Do not declare frontend finished merely because the dev server compiles. Follow the complete user journey and fix the largest visual or functional problem first.

## P6 implemented design - 2026-10-14

The supported API/simulator journey is verified; exact evidence and reviewed images
are in docs/project/evidence/P6-UI.md. Required routes and shared evidence primitives
work, with original stable SVG/HTML provenance and native focus-contained drawers.
Reviewed MIT Card/Empty adaptations were discovered at exact 21st listings; no registry
command was used. Local unmodified OFL fonts/icons replace external assets.
REST plus persisted application SSE owns both job types. Exact backend plan/payload
text preserves large seeds; capture/replay and record/trace integrity stay distinct.
The final hero pairs provenance with actual before/after actions and scope/estimates.
Mobile uses a readable selection table and native menu. Offline caches only assets.
Sentinel/Preflight and real-mode workflows remain unavailable, with reasons.

