# Investigation boundary

`Worker` executes only through the pinned P3 no-network Docker launcher. The pure
runtime injected by unit tests is never installed as an API or CLI execution path.
Owned captures with a recorded neutral control are eligible. Existing captures
without that control, playback, incomplete/untrusted captures and absent real-model
adapters return explicit `unsupported_replay`. There is no paid inference path.

Ranking receives captured relationships and origin/proximity features, never
scenario names or evaluator expectations. Eight candidates are selected; all
occurrences survive in coverage. Discovery stores baseline, singles, top-three
pairs, selected group, benign/required-context removals and neutral replacements.
Each subset/result is available through the paginated trials API. Search is bounded
and does not establish minimality, monotonicity or safety of untested candidates.

Confirmation freezes a plan/digest before reserving fresh trials. The default
stochastic proposal is N=40 and at most three finalists, checked against an explicit
256-trial/turn, 600-second budget. Independent condition/phase streams derive from
SHA256(root, phase, arm, index), with shuffled fixed ordering. Any invalid trial
aborts: zero retries, replacements or optional stopping. An interrupted experiment
has no final CI. A new investigation is a separate experiment; jobs are not pooled.

The deterministic simulator uses one fresh observation per condition and no CI.
The stochastic simulator gates parsed fixture actions using independent Bernoulli
draws; its Newcombe intervals describe only that declared artificial distribution.
`statsmodels==0.14.6` is pinned, with `compare='diff', method='newcomb'` explicitly
selected. Alpha is 0.05/m and the actual interval level is exported. A positive
simulator result requires complete valid samples, lower bound >0, effect >= the
frozen threshold, and useful-task success in every baseline/intervention trial.
Task-destroying reductions cannot be remedies. No LLM claim is possible.

SQLite commits reservation/result and corresponding events atomically before SSE
can read them. Job starts are idempotent; conflicting reuse returns HTTP 409.
One worker holds a 15-second lease, renewed every second. Cancellation stops new
batches; up to eight in-flight trials can finish and are retained. Stale leases
become `interrupted`, preserving reservations without inventing results. The API
and browser recover status using snapshots and durable SSE cursors. Interrupted
jobs require a deliberate new start rather than silently resuming/altering a plan.

Local HTTP-only SameSite session cookies and Origin/CSRF-header checks protect
mutations. This remains a loopback single-user development app, with a local trust
anchor and owned synthetic data; private/multi-user deployment is unverified.

Commands:

```powershell
python scripts/rewind.py dev
.venv/Scripts/python.exe -m rewind_eval.worker --once
.venv/Scripts/python.exe scripts/p4_benchmark.py
python scripts/rewind.py check
npm run test:e2e
```
