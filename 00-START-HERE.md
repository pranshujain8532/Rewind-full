# REWIND — implementation kit for GPT 6.1 Sol

Prepared for Pranshu Jain · 9 October 2026

**Start here. This is a build specification and a set of prompts, not a claim that the software has already been built.**

Workspace update, 2026-10-13: P0 API/storage/web is now implemented and verified;
see [STATE](docs/project/STATE.md) and [P0 evidence](docs/project/evidence/P0.md).
P1 now verifies the owned synthetic simulator/tools and saved-recording playback.
The original dossier is now present, preserved in baseline checkpoint 7a58bfe;
its earlier absence was recorded in P0 history (R-011 resolved). Corrected
contracts remain the build authority; real models/replay isolation remain unavailable.

Your goal is a project that you can demonstrate, explain, and defend. A strong presentation depends on a small number of difficult features working together, with evidence for every result. The full product vision stays intact; implementation follows gates.

## Understand the idea first

REWIND records what an AI agent sees and does. When the agent attempts an unsafe action, REWIND runs controlled experiments: change one suspected input, run the decision process again in an isolated environment, and compare the outcomes. It records the evidence and creates a test to detect the same problem after future changes.

**The memorable demo:** a support agent reads a poisoned ticket, attempts to send synthetic customer data, REWIND identifies which tested input changes that behaviour, and a patch prevents the action while the support task still succeeds.

Read [the simple explanation](docs/implementation/01-UNDERSTAND-REWIND.md) before opening the coding agent.

## The files and the order

| Read / use | File | Purpose |
|---|---|---|
| First | [01 — Understand REWIND](docs/implementation/01-UNDERSTAND-REWIND.md) | Plain-language explanation and a worked story |
| Second | [02 — Technical corrections](docs/implementation/02-DOSSIER-CORRECTIONS.md) | Prevent implementation mistakes in the original dossier |
| During development | [03 — Architecture and contracts](docs/implementation/03-ARCHITECTURE.md) | Modules, data, APIs, replay, statistics, isolation |
| Choose your schedule | [04 — Build roadmap](docs/implementation/04-BUILD-ROADMAP.md) | Phases, dependencies, priorities, gates, scope cuts |
| Frontend | [05 — Frontend design](docs/implementation/05-FRONTEND-DESIGN.md) | Beautiful functional screens and 21st.dev sourcing |
| Testing | [06 — Verification](docs/implementation/06-VERIFICATION.md) | Acceptance tests and measurable evidence |
| Demo / interviews | [07 — Demo and interviews](docs/implementation/07-DEMO-AND-INTERVIEWS.md) | Stage story, explanations, honest technical answers |
| Evidence | [08 — Sources](docs/implementation/08-SOURCES.md) | Primary documentation and unverified dossier claims |
| Coding-agent rules | [AGENTS.md](AGENTS.md) | Mandatory code-and-documentation workflow |
| Begin implementation | [Master prompt](prompts/00-MASTER-PROMPT.md) | Copy the prompt block into GPT 6.1 Sol |
| Every later session | [Session control prompts](prompts/90-SESSION-CONTROL.md) | Continue, diagnose, review, freeze, hand off |
| Current context | [Project state](docs/project/STATE.md) | What actually exists and the next action |

## Exactly how to start

1. Create or open the repository in the coding environment you use with GPT 6.1 Sol. Give it filesystem and terminal access.
2. Extract this kit into the repository root. Keep AGENTS.md, docs/, and prompts/ at the root. In an existing repository, merge AGENTS.md carefully; retain applicable existing instructions.
3. The original dossier is preserved at docs/reference/REWIND-complete-dossier.md. It is background. Its copied build prompt is superseded by this kit.
4. Read 01 and 02 above. You do not need to understand every statistical detail before starting.
5. Copy the fenced prompt from prompts/00-MASTER-PROMPT.md. It instructs Sol to execute P0, verify it, and update the context files.
6. Continue with prompts/01 through prompts/10 in order. Each is a bounded implementation assignment with a concrete gate.
7. After every phase, open the app or run the shown command and ask Sol to explain one real code path to you.
8. Before a new chat, use the resume prompt. The next agent reads project state and verifies it against the repository.

**P0 is the bootstrap. P1–P10 are implementation prompts.** The phase number in a filename matches its roadmap phase. Do not paste the original dossier prompt as a second competing instruction.

No API key is required to build the simulator and playback paths. Real model experiments need an available compatible local model or a configured provider. Missing access must be recorded; a simulator must never be presented as a real LLM experiment. Sol is the implementation assistant; the model being investigated is separately configured.

## What “maintain files in parallel” means here

Code and documentation advance together in each implementation slice:

- STATE.md: current truth and exact next action.
- TASKS.md: acceptance gates and blockers.
- DECISIONS.md: why a consequential choice was made.
- SESSION-LOG.md: what changed, commands, results, and evidence.
- EXPERIMENTS.md: real measured results, including failures.
- BUGS-AND-RISKS.md: unresolved problems and limitations.
- INTERVIEW-NOTES.md: your evolving understanding and contributions.
- COMPONENT-SOURCES.md: origins and licences of reused UI.
- HANDOFF.md: minimal restart instructions after a long break.

Templates are already created. They currently say “not implemented” where appropriate. Sol must not pre-fill results that it has not measured.

## Recommended delivery strategy

Build the evidence-producing vertical slice first. Then finish the live Sentinel and Preflight screens. Add advanced learning models only if they improve a measured result over a simpler baseline.

A practical default is **10–14 focused working days** for a competition-ready implementation, plus **2–4 weeks** of optional research and hardening. A 36-hour rescue scope is provided, but a complete, evaluated enterprise platform is not a credible 36-hour promise.

## Your daily learning routine

Spend 20 minutes after each phase:

1. Explain the phase in two sentences without reading.
2. Ask Sol to trace one request from UI to backend to storage.
3. Reproduce one passing and one failing test.
4. Add what you genuinely learned to INTERVIEW-NOTES.md.

The goal is to understand and own the engineering decisions, even when Sol writes much of the code.

