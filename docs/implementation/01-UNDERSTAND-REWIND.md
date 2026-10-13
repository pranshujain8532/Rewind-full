# 01 — Understand REWIND

## One sentence

**REWIND is an evidence system for AI agents: it records their actions, investigates suspicious behaviour through controlled re-execution, and preserves the findings as verifiable records and regression tests.**

An AI agent is software that uses a model to decide which tools to call. A tool might read a ticket, retrieve a file, or send an email. The useful capability is also the risk: text retrieved from outside can influence the agent's next action.

## The story you must be able to explain

A support agent is asked to summarise ticket TICK-4471. It reads a legitimate issue and an externally written comment. That comment includes an instruction to attach a customer file to an email. The request was never part of the authorised task.

In our demo, every person and record is synthetic. The email tool writes to a local sink; it cannot send real mail. Use a reserved address such as audit@external.example.

| Stage | What happens | What REWIND can honestly say |
|---|---|---|
| Capture | Record tool traffic and, with an adapter, model inputs | This content was supplied; this action was attempted |
| Policy check | Compare the proposed action with a signed mandate | The action exceeded the recorded permission scope |
| Candidate ranking | Rank inputs worth investigating | This input is suspicious; ranking is not a finding |
| Experiment | Rerun the agent with the selected comment removed | Behaviour under this intervention differs by this amount |
| Evidence | Report counts, uncertainty, coverage and limitations | Evidence supports this input's influence in the tested environment |
| Regression | Rerun the original attack after a fix | The fix prevented the harmful action and retained task success in these tests |

**The essential distinction:** a suspicious comment is a hypothesis. A controlled experiment produces evidence about that hypothesis. Neither a classifier nor a coloured graph proves responsibility.

## Four product modes

| Mode | Plain language | First useful implementation |
|---|---|---|
| Forensics | Investigate an incident | Replay, ablation, action outcomes and report |
| Ledger | Keep evidence and prevent recurrence | Sign a record; export and rerun a regression |
| Sentinel | Check before an action proceeds | Mandate rules and a held-action decision |
| Preflight | Rehearse failure before deployment | Run a fixed defensive test suite against our own sandbox |

Atlas, insurer scoring, cross-company attribution and certification are future product hypotheses. They are not necessary for the first convincing demonstration.

## The seven objects to understand

| Object | Analogy | Actual meaning |
|---|---|---|
| Session | One flight | One agent run with task, model, policy and versions |
| Event | One recorder entry | Ordered model/tool/policy/approval activity |
| Content chunk | One piece of evidence | A specific input, with its origin and content reference |
| Mandate | Written permission | What this agent is allowed to do and under whose supervision |
| Intervention | Controlled change | Removing or replacing one input before fresh decisions |
| Finding | Experiment conclusion | Measured effect with conditions and uncertainty |
| Regression case | A permanent exam question | Original attack + fixed agent configuration + success conditions |

## Three things commonly confused

### Playback versus experiment

Playback is watching a recording. The same recorded output appears even if you change the label on the input. It proves the recording can be displayed.

Re-execution makes fresh decisions from the modified input. That is required to investigate whether the input changes behaviour.

The project supports both, and the UI names them differently.

### Attempt versus execution

An agent can attempt to send a file while the policy engine blocks the tool. The attempted unsafe action and the completed side effect are different facts.

The main causal outcome asks whether the agent **attempted the specified harmful action**. A separate field records whether a tool was actually dispatched and whether the mock sink accepted it.

### Record integrity versus truth

A valid signature says the trusted signing key signed these bytes. It does not say the bytes are true, complete, legally sufficient, or impossible for a privileged operator to replace. Evidence must include capture coverage and the verifier's trust assumptions.

## A small numerical example

Suppose fresh baseline runs attempt the harmful action in 18 of 20 trials. Runs with one chunk removed attempt it in 2 of 20 trials.

- Baseline harmful-action rate: 18/20 = 0.90.
- Baseline non-reproduction rate, called base flip-rate in the dossier: 2/20 = 0.10.
- Intervention harmful-action rate: 2/20 = 0.10.
- Estimated reduction: 0.90 − 0.10 = 0.80, or 80 percentage points.

A statistics library must calculate the interval for the **difference between two rates**. The report must also check whether the agent still completed the support task. If it did nothing because the input was destroyed, that is a poor fix.

These numbers are an illustration, not project results.

## What makes this a strong engineering project

The difficult work is preserving event order, knowing what was actually captured, rerunning altered inputs without external side effects, handling diverging tool calls, assessing uncertain results, and carrying that evidence through a usable interface.

The GenAI part is real agent re-execution and, later, constrained narrative generation or defensive test variation. Full-stack depth comes from the typed API, durable jobs, live events, interactive graphs, cryptographic verification, testing and deployment. Deep-learning additions earn their place through evaluation.

## A 30-second explanation

“An AI agent can read a malicious instruction hidden in a ticket and then attempt an action its owner never authorised. REWIND records the run, checks the action against its mandate, and investigates suspicious inputs by rerunning the agent with controlled changes. It reports the measured outcome and uncertainty, signs the evidence, and creates a regression test so later changes can be checked against the same failure.”

