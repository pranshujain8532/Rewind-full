# 04 — Build roadmap

## Outcome and assumptions

Deliver a local full-stack demo with all four accepted modes, a real-model experimental path where a compatible model is available, an offline simulator/playback fallback, and documentation that explains the engineering history.

Assume one primary developer with GPT 6.1 Sol, no paid GPU requirement, a small synthetic dataset and a deadline not yet specified. Estimates are planning ranges, not guarantees. Actual phase time goes into SESSION-LOG.md.

## The critical path

P0 → P1 → P2 → P3 → P4 → P5 establishes evidence.
P6 makes that evidence understandable.
P7 and P8 complete the runtime and pre-deployment modes.
P9 provides MCP composability.
P10 validates the finished product.

Frontend structure may begin in P0. Only wire a feature to real domain data when its contract exists. Do not spend the first day polishing a fake dashboard.

## Phase plan

| Phase | Deliverable | Planning effort | Gate / visible proof |
|---|---|---:|---|
| P0 | Repository, environment, contracts and documentation workflow | 2–4 h | Fresh checkout starts API and web; versions and actual commands recorded |
| P1 | Synthetic sandbox, scenarios and explicit run modes | 5–7 h | Clean and attacked runs differ; all side effects terminate in local sinks |
| P2 | Recorder, content store, signing and capture adapter | 8–10 h | End-to-end recorded trace; tampering detected; incomplete capture visible |
| P3 | Isolated replay and fresh model re-execution | 10–14 h | Intervention reaches a fresh decision; unknown tool path fails honestly; egress test |
| P4 | Discovery, confirmation, statistics and live jobs | 8–12 h | Complete counts/CI from real trials; controls and inconclusive cases work |
| P5 | Evidence export, verifier and original-attack regression | 6–8 h | Valid record verifies; altered one fails; patch passes safety and task checks |
| P6 | Polished live investigation UI | 10–14 h | Stage story runs via UI, keyboard and refresh/reconnect |
| P7 | Sentinel policy gate and live approvals | 6–8 h | Denied action never dispatches; valid approval cannot be reused |
| P8 | Preflight evaluation and optional constrained variation | 4–6 h | Connector results use actual trial denominators; tests run only in owned sandbox |
| P9 | REWIND MCP tools and coverage disclosure | 3–5 h | SDK client queries evidence and starts authorised jobs |
| P10 | Evaluation, demo packaging, fresh-machine run and interview readiness | 6–8 h | Rehearsed run, measured results, reproducible setup and final honest feature matrix |

Total: roughly **68–96 focused engineering hours**, normally spread over 10–14 working days with integration contingency. If real-model provisioning or protocol adaptation is difficult, extend the schedule or disclose the blocked capability.

## Must, should and research

### Must for the competition core

- Synthetic incident and benign control.
- Captured model input and tool evidence for the supported agent.
- Clear playback / simulator / local-model / hosted-model distinction.
- Signed event chain and trusted-key verifier.
- Isolated intervention harness with explicit unsupported states.
- Defined harmful-action and useful-task outcomes.
- Honest statistics for fresh stochastic trials.
- Live timeline, input graph, intervention workspace and evidence report.
- Original-attack regression after a real configuration/policy fix.
- State, decisions, experiments, known limits and interview notes updated.

### Complete the four modes next

- Sentinel mandate enforcement and held-action workflow.
- Preflight suite across at least two synthetic input surfaces.
- Evidence mapping with supported / partial / absent controls.
- MCP read tools and authorised investigation start.
- A real-model experiment with baseline and intervention when available.

### Research extension, after P10

The accepted dossier's advanced ideas are retained here rather than silently removed:

| Component | First implementation | Promotion evidence needed |
|---|---|---|
| Transformer Sentinel | Rules + n-gram/Markov sequence score | Better detection at comparable false-hold rate on held-out families |
| Goal-drift embeddings | Optional frozen small embedding model | Incremental benefit over sequence/policy baseline |
| Injection classifier | Transparent heuristic prior | Better candidate recall/ranking on held-out input styles |
| GAT prior | Ancestor/proximity ranking | Fewer trials at equal or better recovery and recall |
| Bayesian changepoint | Simple window/change diagnostics | Better search localisation with documented assumptions |
| Shapley estimation | Enumerated small pair/group cases | Correct coalition definition, stochastic uncertainty, bounded cost |
| SPRT / confidence sequences | Fixed-N confirmation | Reviewed stopping rule and error-rate validation |
| Contrastive trajectory encoder | Metadata and sequence similarity | Useful retrieval improvement over simple baseline |
| General graph edit distance | Sequence divergence + explicit provenance | Runtime budget and added signal demonstrated |
| True Merkle proofs | Signed linked hash chain | Correct inclusion-proof implementation and verifier tests |
| OTel import / HTTP MCP | One instrumented local stdio integration | Integration coverage and version compatibility tests |
| Atlas / A2A / insurer scoring | Design notes only | Privacy, consent, cross-org identity and validation beyond this demo |

Do not display a model as trained simply because a class exists. Track unavailable, simulated, heuristic, trained-on-synthetic, evaluated-on-held-out and production-tested as distinct statuses.

## Daily rhythm

**Start:** read AGENTS.md, STATE.md, HANDOFF.md and the current phase. Inspect git status and the relevant tests.

**Build:** deliver one vertical slice with a visible command or screen. Validate before stacking another layer.

**Document:** write what changed and why; attach exact commands and result paths. A failed approach is valuable only when its actual evidence is recorded.

**Review:** Pranshu explains one choice. Sol asks two relevant questions and fills gaps with a short explanation.

**Checkpoint:** keep changes reviewable. Commit only if permitted by the repository/user workflow; never push or overwrite remote history as an incidental phase step.

## 36-hour rescue track

This is a deliberately smaller implementation, not the entire table above.

| Work | Budget |
|---|---:|
| P0 bootstrap and fixed scope | 2 h |
| P1 synthetic scenarios and modes | 3 h |
| P2 minimal complete recording and signed chain | 4 h |
| P3 isolated simulator + real model only if already available | 5 h |
| P4 bounded single/pair experiments and uncertainty display | 4 h |
| P5 signed record and one regression | 3 h |
| P6 timeline, comparison, investigation and report screens | 7 h |
| Integration, isolation checks, offline fallback, rehearsal and fixes | 8 h |
| **Total** | **36 h** |

Use a basic mandate rule in the core. Advanced Sentinel detection, evolutionary Preflight, the public MCP server and training are deferred. If re-execution is only simulated, label the demo a simulated proof of the mechanism; it is not measured evidence of real LLM causal attribution.

## Cut order when late

Cut decorative motion, landing-page extras, optional classifiers, transformer training, graph-learning priors, HTTP MCP, Atlas concepts and ancillary screens in that order.

Never cut mode labels, actual trial provenance, the side-effect boundary, uncertainty, original-input regression, integrity checks or the living project state.

## Definition of implementation complete

P0–P10 gates are evaluated and the feature matrix names every unsupported piece. At least the declared delivery track passes from a clean environment. For a “real-model investigation” claim, P3/P4 must include actual fresh model trials; simulator-only completion cannot satisfy that claim.

Final documentation must list the exact git revision, commands, dependency versions, screenshots, result manifests, known limitations and next steps.

## P8 feature maturity - 2026-10-15

| Accepted feature | Current scope | Maturity |
|---|---|---|
| Preflight fixed suite | One owned synthetic target; ticket comments + actual mock file text; isolated deterministic configurations, budgets, recorded failures | VERIFIED; evidence/P8-SIM.md |
| Preflight LLM variations | Constrained budget/lineage and separate exploratory label required | PLANNED; not implemented |
| Evolutionary generation | Bounded mutation/selection loop, stopping budgets and lineage need actual implementation/tests | PLANNED; not complete |
| Guardrail classifier/evasion | No classifier in the owned suite | ABSENT; detection/evasion not measured |

Completing the fixed-suite P8 gate does not promote generation or real-model support.
