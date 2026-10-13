# Session control prompts

Use the block matching the situation. These prompts keep context durable without pasting the entire dossier into every chat.

## Resume after a break or in a new chat

~~~text
Continue the existing REWIND repository. First read AGENTS.md,
docs/project/STATE.md, HANDOFF.md, TASKS.md and relevant recent decision/
experiment/bug entries. Inspect git status and verify the documented
state against the files.

In six bullets, tell me what actually works, which modes are available,
what failed, what is unverified, the current gate and the exact next task.
Then implement that next authorised task, validate it and update context.
Do not restart, redesign the product or overwrite existing user work.
~~~

## Diagnose a failing gate

~~~text
REWIND's current gate is failing. Reproduce the failure before changing
code. Record the exact command, environment, error and smallest reliable
case in BUGS-AND-RISKS.md.

List the plausible causes, gather discriminating evidence and fix the
root cause with the smallest coherent change. Preserve the failing test
where it tests a real risk. Do not weaken the assertion, skip the gate or
silently replace real inference with a fixture.

After the fix, run the relevant verification and update the bug entry,
state, session log and handoff. Explain the cause and why the fix works.
~~~

## Replay is inconsistent

~~~text
Audit REWIND replay. Distinguish expected model randomness from harness
bugs. Check initial memory/tool state, content occurrence mapping,
model/tool versions, request construction, cache key, environment snapshot,
random streams, tool response occurrence and unsupported branches.

Prove interventions reach fresh model input and no downstream cached
decision survives. Report original vs repeated action counts and task
success. Do not claim deterministic hosted inference or increase trials
merely to hide a systematic mismatch.
~~~

## Improve the UI after it works

~~~text
Inspect the actual REWIND screens and screenshots at the required widths.
Identify the three biggest problems in hierarchy, spacing, readability,
interaction or evidence clarity. Fix them using the agreed design system.

Verify any 21st.dev components and record their source/licence. Keep
real data, uncertainty and mode labels readable. Test keyboard, reduced
motion, loading/error states and SSE reconnect. Do not turn the app into
a decorative landing page or invent live counters.
~~~

## Explain the code for an interview

~~~text
Teach me the REWIND feature we just implemented using our real repository.
Explain the problem, data flow, main files/functions, chosen design,
alternatives, hardest edge case and the test proving it works.

Use one concrete request from start to finish. Ask two short questions to
check my understanding. Write an accurate interview explanation in
INTERVIEW-NOTES.md, distinguishing my contributions and AI assistance.
Do not invent results or past failures.
~~~

## Audit documentation against code

~~~text
Compare STATE, TASKS, DECISIONS, EXPERIMENTS, INTERVIEW-NOTES and HANDOFF
against the repository and retained test artifacts. Find claims that are
stale, unsupported, contradictory or too strong.

Fix the documentation without rewriting historical evidence. Mark tests
not run and features not verified. Check that exact paths, commands,
versions and next actions are usable. Keep STATE concise.
~~~

## Final independent engineering review

~~~text
Review the implementation against the critical acceptance matrix.
Prioritise replay validity, tool isolation, statistical assumptions,
approval binding, signature trust, original-attack regression, SSE
durability and UI truthfulness.

For every finding, state severity, reproduction, impact and smallest fix.
Repair verified defects, rerun only the relevant gates and update the
records. Separate defects from optional improvements. Do not mark a
capability complete on the basis of a screenshot or cached animation.
~~~

## Freeze before the event

~~~text
Feature freeze. Complete only stability fixes, relevant validation,
offline fallback, screenshot review, evidence export verification and
demo rehearsal. Hide unfinished features behind accurate capability
states. Preserve real-model versus simulator labels.

Update README commands, feature maturity, measured results, known limits
and the four-minute script. Make HANDOFF sufficient for a teammate to
start the application. Add no new product features.
~~~

