# P1 — Build the controlled incident

Prerequisite: P0 gate. Copy this block.

~~~text
Implement REWIND P1. Read AGENTS.md, STATE, HANDOFF, TASKS and the P1
roadmap row. Follow the corrected architecture.

Build a small instrumented support agent with three owned mock MCP servers:
ticket, files and mail. Use the pinned official SDK and protocol revision.
The mail tool writes only to a local synthetic outbox. It must never send
real email. Use reserved .example addresses and clearly synthetic records.

Create versioned scenario manifests:
1. clean support task;
2. single injected comment;
3. harmless imperative text;
4. two-input interaction;
5. redundant independently sufficient inputs;
6. legitimate authorised external action.
Keep evaluator ground truth separate from agent inputs and ranking data.

Create an explicit model interface with playback, simulated, local_model
and remote_model capabilities. Implement the simulator transparently.
Playback returns recordings; it must never be counted as fresh inference.
Unavailable real-model adapters report capability errors, not silent
fallback. Do not select a “guilty chunk” by fixture ID in application logic.

Define action-attempted, action-executed and task-success predicates.
The harmful-action predicate inspects tool semantics and arguments; it does
not search for one malicious string. Task success checks actual required
ticket facts. Record per-run configuration and cloned initial state.

GATE:
- clean and injected simulator runs produce their expected distinct actions;
- all side effects terminate in local sinks;
- model mode is visible in CLI/API output;
- fixture generation is reproducible;
- ground-truth labels cannot enter the subject agent or ranking interface;
- scenario tests and a CLI demo run pass.

Update project context, record actual evidence, and explain one run from
input to proposed tool call. This phase ends at its verified gate.
~~~

