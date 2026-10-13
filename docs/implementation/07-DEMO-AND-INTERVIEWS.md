# 07 — Competition demo and interview preparation

## Positioning

Keep the accepted positioning: **REWIND — the black box for AI agents.**

Explain the implemented contribution as the connection between captured execution evidence, controlled intervention experiments, policy scope and repeatable regression checks. Avoid unsupported claims of being the world's first, legally certifying agents, or guaranteeing a win.

## Four-minute stage story

| Time | Screen / action | What to say |
|---|---|---|
| 0:00–0:25 | Show task and mandate | “This support agent may read a ticket and summarise it. It is not authorised to export customer data.” |
| 0:25–0:55 | Run poisoned synthetic scenario | “A comment introduces an unrelated instruction. The agent attempts this action. The tool is a local sink.” |
| 0:55–1:25 | Select the attempted action and provenance | “The trace shows what it saw. That alone does not establish which input changed its behaviour.” |
| 1:25–2:10 | Start or inspect an investigation | “We rerun fresh decisions under controlled input changes. Here are baseline and intervention counts, uncertainty and task success.” |
| 2:10–2:45 | Open signed evidence record | “The result includes configuration, coverage and limitations. This verifier checks the bytes against our trusted key.” |
| 2:45–3:15 | Run patched regression | “We keep the original attack and change the defence. The selected safety contract must pass and the support task must still succeed. A policy block can stop dispatch while an unsafe attempt remains.” |
| 3:15–3:40 | Sentinel / Preflight | “The same recording also supports action checks during execution and defensive tests before deployment.” |
| 3:40–4:00 | Feature maturity and next step | “These features are measured; these are simulated or planned. Our next integration target is listed here.” |

If the full experiment takes longer than the available stage time, start one small live job and open a previously completed, verifiable run. Label the completed run with its date/mode; do not pretend it just finished.

## Rehearsal scenarios

**Primary:** working real-model experiment if evaluated and provisioned.

**Offline fallback:** recorded real experiment plus transparent simulator. Saved evidence is still inspectable, but playback is not a fresh experiment.

**Negative example:** partial capture or missing tool branch returns unsupported. This demonstrates disciplined refusal.

Reset scripts must target only a clearly named demo database/directory. Rehearse before the event with the network unavailable.

## What you should learn from each phase

| Phase | Interview skill | Explain using your implementation |
|---|---|---|
| P0 | Repository design and dependency management | Why versions and contracts were fixed first |
| P1 | Controlled test environments | Why every side effect terminates in a local sink |
| P2 | Event design and cryptography | Content identity versus occurrence identity; what signatures establish |
| P3 | Systems and security | Why a process is not a sandbox; how replay handles divergence |
| P4 | Experimental reasoning | Why one changed outcome is insufficient |
| P5 | Software quality | Why the original malicious input stays in a regression |
| P6 | Full-stack development | API snapshot + live events + consistent UI state |
| P7 | Authorisation | Why an approval binds to exact arguments and a mandate version |
| P8 | Evaluation | Why denominators, task success and held-out cases matter |
| P9 | Protocol design | Which MCP revision and primitives you actually support |
| P10 | Engineering judgement | Which goals were measured and which remain unsupported |

## Interview questions and answer structures

These are **proposed design explanations**. Change them to past tense only after implementation and evidence exist.

**What problem does REWIND solve?**  
“Agent traces show events, but investigating which input influenced an unsafe action still requires controlled testing. Our design combines recording, intervention experiments and verifiable results so fixes can be tested again.”

**How is this different from ordinary logging?**  
“The important additional work is changing a captured input and rerunning fresh decisions in a controlled environment, while preserving evidence of the experiment. The action comparison and regression test are the useful outputs.”

**Why is replay difficult?**  
“After an intervention, the agent can take a different tool path. We need a valid environment response for that path. Strict recorded replay refuses unknown paths; our versioned sandbox can model supported ones.”

**Why not use an LLM to name the culprit?**  
“A model can rank candidates, but its opinion is not the experiment. Code determines target actions and computes rates and intervals from fresh trials. I would compare ranking methods empirically before claiming one works better.”

**Why use a model adapter as well as an MCP proxy?**  
“The proxy records traffic it sees. It does not automatically see system instructions, direct model calls or all memory. The adapter captures the supported agent's model input and resumable state.”

**Why not build all the deep-learning components immediately?**  
“Each one must improve a decision. First I establish a baseline, then test whether an added model improves recall, false alarms or compute cost on held-out cases.”

**Is the result causal?**  
“It is evidence about a specified intervention under the captured model and environment. It does not establish universal causation, intent or legal fault. Coverage, task disruption, randomness and unmodelled environment changes limit interpretation.”

**Does a valid signature prove the incident happened?**  
“It proves the trusted key signed the specified bytes. Completeness and faithful capture are separate assumptions. A privileged signer could rewrite local history unless an independent trusted checkpoint exists.”

**What if removing the whole ticket stops the unsafe action?**  
“That may also stop the legitimate task. We report task success separately and include less destructive or neutral replacement controls.”

**How does the interface stay live after a refresh?**  
“Jobs and their progress are persisted. The UI loads a snapshot, receives incremental events and deduplicates them on reconnect. The backend, not the animation, owns the count.”

**What would change for production?**  
“Authentication and tenancy, external trust anchors, retention/key custody, broader replay adapters, provider drift, reliable workers and evaluation on representative traffic. A local demonstration does not prove those deployment properties.”

**What did you personally contribute if GPT wrote much of the code?**  
Use your real contribution: choosing trade-offs, checking experiments, tracing failures, refining the UX, validating outputs and explaining limitations. State AI assistance honestly. Do not claim an architecture choice or failed experiment you did not understand or perform.

## Two high-value experiments to actually run

1. Compare LLM-only candidate ranking with heuristic ranking and intervention-confirmed outcomes. It may work well or poorly; record what happens.
2. Compare output-text similarity with action-based outcomes. Construct cases with equivalent actions but different wording, and different actions with similar summaries.

Only after recording these experiments may you tell a “we tried X, it failed, so we changed Y” story.

## Resume bullets: fill with evidence

- Built an instrumented agent investigation platform with [implemented integrations], [recording/verification feature] and [live UI capability].
- Evaluated [N] held-out [synthetic/realistic] scenarios; achieved [measured result with denominator] under [named model and conditions].
- Implemented [isolation mechanism] and original-attack regression tests, measuring both unsafe actions and legitimate task completion.

Do not use “100% accurate,” “enterprise-ready,” “production-scale,” or “instant hire.” Use actual sample counts and the scope you tested.

## Release evidence to keep

Store screenshots, one short demo recording if available, benchmark manifests, signed sample records, verifier output, architecture decisions and a clear README. Use synthetic identities throughout. These artifacts let you answer “show me” months later.

