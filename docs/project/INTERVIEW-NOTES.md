# Interview notes — grow this with the code

Current state: P0-P4 simulator/capture/replay/investigation gates verified with
actual simulator measurements, 64/64 repository and 12/12 browser tests.
Real-model evidence, Ledger, Sentinel and Preflight remain unavailable/unimplemented.

## Explanation to practise now

“REWIND records an AI agent's actions and the inputs it received. It investigates suspicious behaviour by rerunning decisions under controlled input changes, measures what changed, and preserves the evidence in signed reports and regression tests.”

## Understand these before saying “I built it”

- Playback versus fresh re-execution.
- Attempted action versus executed side effect.
- Input occurrence versus deduplicated content.
- MCP proxy visibility versus model-adapter visibility.
- Experimental effect versus universal causation.
- Signature integrity versus truth and legal responsibility.
- Safe regression versus a broken agent that does nothing.
- Simulated, heuristic, trained and independently evaluated features.

## Add after each real phase

~~~text
Feature / phase:
Problem it solves:
What actually works:
My contribution:
How AI assisted:
Important files / functions:
Request data flow:
Design choice and alternative:
Hardest edge case:
Test or experiment proving the claim:
Actual result with denominator:
Limitation:
30-second explanation:
90-second explanation:
Question I initially could not answer:
Answer after learning:
~~~

## Story bank — initially empty

Add actual examples only:
1. A hard bug you reproduced.
2. An alternative you tested and rejected.
3. A performance or correctness trade-off.
4. A scope cut you can justify.
5. A result that was inconclusive and how you handled it.

The dossier's suggested failure stories are hypotheses until you run them.

## P0 — foundation actually implemented

Problem: make the application start reproducibly and accurately show what exists.
What works: migrated SQLite/WAL readiness, explicit capability reasons, an empty
React workspace, generated schemas/types, locked dependencies and cross-platform
command entry points tested on Windows. Five backend/SDK and four browser checks pass.

Pranshu supplied the product direction and boundaries. The coding assistant wrote
and verified this P0 slice; this record does not imply Pranshu has already practised
or mastered its internals. No comprehension answers have been recorded yet.

One request path to trace: App calls readSystem; the web proxy forwards health
and capabilities to FastAPI. Health checks migration revision, schema metadata
and WAL through SQLAlchemy. Capabilities independently returns planned/unavailable
agent features. The generated TypeScript boundary types both responses. The view
renders readiness and empty states; there are no agent results to invent.

Design choice: one installed Python distribution with conceptual module
directories avoids multiple packaging/build services while retaining boundaries.
OpenAPI generation prevents the frontend from drifting from backend contracts.
Separate mode/maturity/evidence lets a simulator eventually work without claiming
real-model evidence; a ready API does not automatically enable agent features.

Actual bug story: desktop worked, but phone CSS hid the Refresh button's text and
accessible name. The browser test failed through its role/name selector. Adding
an explicit aria-label made keyboard refresh work at every checked width. The
failed trace was retained rather than rewriting the test to use an unnamed button.

60-second explanation to practise:
“REWIND keeps its four product modes over one recorder. In P0 we built the
foundation rather than claiming those difficult mechanisms already work: a typed
API, versioned SQLite migration and a web shell reading real capabilities. API
readiness checks the database schema, while every agent run mode has its own
availability and reason. Python owns the contract and generates client types.
Dependencies are locked and a single command sets up the local application.
We verified five backend/SDK checks and four browser cases, including a phone
accessibility bug and backend outage recovery. No GPU or provider key is needed
to start it. Next we add synthetic tools and scenarios; isolated replay and
statistical conclusions have separate later gates.”

Comprehension questions (unanswered):
1. Why can health return ready while local_model and simulated remain unavailable?
2. Why must changing contracts.py regenerate API types and run a drift check?

P1 implemented/verified: the subject receives only typed task/ticket/input/permission
fields; fixture expectations remain separate. Real stdio tools return a ticket and
synthetic attachment, and a send records only a local outbox entry. A harmful
attempt uses recipient permission plus attachment classification, independently
of scenario IDs. Full narrative and two unanswered questions: evidence/P1.md.
Actual debugging story: untyped MCP dict output arrived as JSON text rather than
structured_content; decode both supported result forms and reject ambiguous output.


## P2/P3 — implemented evidence and isolated simulator

The recorder combines transparent owned stdio traffic with exact simulator input
capture, encrypted payloads and signed ordered events. A separately trusted key
verifies integrity relative to the seal, not truth or individual blame.
Fresh simulator trials run in a tested no-network container; strict recorded reads
require matching occurrence and state. Unknown reads are invalid, not harmless.
Playback has no fresh decisions. Removing required task context can stop useful
work, so safety and task checks remain separate. No local model exists here.
Actual failures: incorrect image root path, strict downstream fallback found in
review, and a Windows startup deadline flake; all repaired before SIM gate.
Questions: Why are two identical comments distinct interventions? Why can't a
signed playback establish the effect of removing a comment?


## P4 explanation — 2026-10-14

“REWIND builds a graph from captured inputs and observed decisions/actions, then
ranks candidate occurrences using visible origin and proximity features. Ranking
cannot see planted answers. A bounded discovery search tries singles, selected
pairs/groups and benign/neutral/task-failure controls, preserving every tested
subset and untested candidate. It freezes a fresh confirmation plan before running
new trials. Code counts harmful attempts and useful work, computes rate differences
and Newcombe intervals, and adjusts alpha for all predeclared finalists. Our
simulator case went from 32 harmful attempts out of 40 to zero out of 40: an
estimated 80-point reduction with a 62.8–89.5-point 95% interval. That uncertainty
belongs only to the declared stochastic simulator. Missing trials cannot become
safe outcomes. Durable jobs and committed events make refresh, cancellation and
worker crashes visible, rather than inventing progress.”

Questions: Why must invalid/missing trials remain outside the harmless denominator?
Why can a positive lower bound still produce an inconclusive finding when the
estimated reduction misses the prespecified meaningful-effect threshold?
Comprehension answers not yet recorded. P5 will sign these investigation records
and regress the original attack against a changed defence, retaining useful work.

## Gemini exploratory adapter — 2026-10-14

60-second explanation: “The API key stays in the backend. A non-root container has
no network and sends one bound request through a pipe. The parent validates the
actual transformed input, reserves an authorised budget and calls only Gemini.
The model returns a structured summary and proposed actions; code checks those
actions against the owned world and writes only to private mock outboxes. We ran
three actual requests: the baseline and removal were valid, while neutral replacement
guessed an invalid attachment and was rejected. We retained that failure rather
than counting it as harmless. Signed captures verify what was recorded, not whether
an experiment is valid. Two individual observations cannot establish a reliable
effect or interval, and real-model Forensics remains ineligible. The free-tier
billing declaration is explicit; it is not something an API key proves.”

Questions: Why does an invalid tool proposal prevent a harmless-outcome count?
Why does authenticating a key fail to establish billing tier or causal evidence?
Comprehension answers not yet recorded. Next: explicit argument schemas and durable
remote budgets/admission before a fresh affordable fixed confirmation plan.

## P5 — 60-second explanation, 2026-10-14

“The record is computed from stored traces and trials. It retains the original seal,
configuration and fixture digests, counts, coverage and limitations. We sign the
report together with its artifacts so someone can verify them outside the app using
a separately trusted public key. That establishes integrity under a key assumption,
not truth or personal blame. The regression uses the whole original attack twice:
first the vulnerable configuration, then a fixed configuration. A behavioural fix
prevents attempts. A containment fix can retain an attempt while preventing dispatch,
and the result must show that distinction. Both must preserve the legitimate task.
Our blanket-denial control blocked a required owner send and failed. Invalid or
missing evidence remains inconclusive. These are simulator results, not LLM reliability
estimates or compliance certificates; external governance mapping remains pending.”

Questions: Why does a trusted signature fail to establish that an observation was
true? Why can a containment patch pass while the behavioural contract fails?
Comprehension answers not yet recorded. Next product phase P6, full evidence UX.

## P6 - 60-second explanation, 2026-10-14

"REWIND now connects the evidence journey. I select a captured input and the graph,
event, details and intervention comparison stay together. The edges show observed
relationships, not proven causes. A separate worker stores trials and progress before
SSE sends them; the browser reads authoritative snapshots and ignores duplicate event
IDs. Refresh, lost connections, cancellation and worker death preserve actual status.
Rates, useful work and independent-sample intervals come from the backend. Mode,
coverage, evidence and integrity are separate. Exact text avoids rounding large seeds.
The signed record can be downloaded and verified with an independently trusted key;
integrity still is not truth or blame. Regressions retain the original attack and
show both safety and useful work, including residual attempts. I reviewed licensed
components, bundled offline assets and fixed the largest screenshot problems at three
sizes. This proves the supported simulator workspace, not real-model or compliance
readiness. Sentinel and Preflight clearly explain their unavailable APIs."

Questions: Why does a provenance edge not establish a cause? Why must an old passing
regression disappear while a new run is pending? Answers not yet recorded. Next P7.
## P7 — 60-second explanation, 2026-10-15

“Sentinel checks a proposed action before any protected tool effect. A signed mandate
binds our owned agent, session, world, validity, tool/data/recipient scope and budget.
Code computes the verdict. A forbidden export is denied and has no approval override.
An otherwise authorised high-impact send is held. The local operator's approval binds
the exact action and arguments digests, session, mandate version and expiry. Before
dispatch, a SQLite transaction rechecks all of those facts, consumes the approval
once and writes the owned mock effect and signed audit together. Retries and races
cannot send twice. Timeout or cancellation makes that call non-resumable; denial can
lead to one bounded investigation of the earlier captured source. The UI reads actual
stored decisions and counters. Our unchanged-attack experiment denies the forbidden
send but permits one approved owner send and preserves the task. Denying every send
fails the owner task. This proves the owned simulator/database adapter, not general
MCP delivery, real-model reliability, external identity or compliance.”

Questions: Why cannot a normal approval override an out-of-scope verdict? Why does
atomic local dispatch not establish at-most-once delivery to an arbitrary remote tool?
Comprehension answers not yet recorded. Next product phase P8, not started in P7.
