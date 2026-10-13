# Interview notes — grow this with the code

Current state: P0 API/storage/web foundation verified. Agent experiments and
product mechanisms are not implemented yet; no model/benchmark result is claimed.

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

