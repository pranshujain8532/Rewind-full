# P4 — Build the investigation engine

Prerequisite: P3 validated for the chosen mode. Real-model conclusions require the real-model gate.

~~~text
Implement P4. Read architecture section 10, the domain schemas and
06-VERIFICATION.md. Keep mode eligibility explicit.

Build an observable provenance graph and transparent candidate ranking.
Use captured input relationships, external-origin metadata and proximity.
Ranking cannot see planted ground truth. Preserve low-ranked candidates
in the search coverage report.

Implement bounded discovery: single removals plus selected pair/group
tests for interaction and redundancy, with benign removal and neutral
replacement controls. Log every subset and result. Do not assume
monotonicity, promise logarithmic search, or call untested candidates safe.

Separate adaptive discovery from fresh fixed-plan confirmation.
Before confirmation starts, freeze finalists, N, randomisation, trial
budget, invalid-trial policy, alpha correction and meaningful effect
threshold. Default proposal is N=40 per condition with at most three
finalists, subject to an explicit affordable budget. Do not run paid
inference unless the configured authorised budget permits it.

Compute harmful-action rates, base flip-rate, effect difference and
Newcombe intervals using the documented independent-sample method.
Apply alpha=0.05/m for m predeclared findings and show the actual interval
level. No optional stopping on a fixed-sample CI. No inferential claims
from replaying a fixed recording. Simulator statistics stay simulator-only.

Implement durable jobs, progress events, cancellation, budgets, idempotent
starts, worker heartbeats and interruption handling. Persist before sending
application SSE events. The browser must recover the real status.

GATE:
- unit tests cover boundary counts, negative effects and method assumptions;
- single, pair-dependent, redundant, benign and task-destroying cases are handled;
- incomplete/invalid trials cannot become positive findings;
- no-effect, inconclusive and unsupported states render in the API;
- all reported counts derive from stored trials;
- refresh, cancellation and worker interruption preserve truthful status.

Update EXPERIMENTS with raw result references and limitations; do not copy
dossier numbers. Explain the estimate and uncertainty in plain language.
~~~

