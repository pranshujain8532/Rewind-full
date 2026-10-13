# 06 — Verification and measurable evidence

Every table below specifies **tests to build and run**, not results already achieved. Attach command, revision, environment, output path and pass/fail status to each completed gate.

## Test pyramid

Use small deterministic unit tests for policies, signatures, outcome predicates and statistics; integration tests for capture/replay; and a few full browser journeys for the demo. Test actual risks rather than mirroring every helper function.

## Critical acceptance matrix

| ID | Scenario | Required outcome |
|---|---|---|
| V01 | Clean support task | Correct task result; no harmful action |
| V02 | Poisoned input in simulator | Known attempted action reaches local sink only; simulated label |
| V03 | Same input twice in different places | Two occurrence identities; explicit intervention scope |
| V04 | Fresh model re-execution | Modified input produces a new model request; cache does not replay stale decision |
| V05 | Recorded playback repeated | No invented independent trial count or LLM CI |
| V06 | Repeated identical tool arguments at different states | Correct occurrence/state response selected |
| V07 | New counterfactual tool path under strict replay | Unsupported trial, never live fallback |
| V08 | Pair-dependent attack | Joint effect explored; no unjustified single culprit |
| V09 | Redundant attack sources | Single removal may fail; group removal considered |
| V10 | Benign input removal | Does not automatically become a positive finding |
| V11 | Required task input removed | Task failure exposed; not offered as a successful remedy |
| V12 | Weak/noisy baseline | Correct uncertainty or inconclusive result |
| V13 | Incomplete/biased trial failures | Confirmation interrupted or invalid, never counted as harm absent |
| V14 | Modify/reorder/delete an event or payload | Verification fails relative to original trusted seal |
| V15 | Unknown signer / replaced public key | Trust not established |
| V16 | Invalid or expired mandate | Fail closed; no tool dispatch |
| V17 | Approval replay / double-click / altered arguments | At most one authorised dispatch for exact approved action |
| V18 | Explicit hard denial + UI approval attempt | Hard denial cannot be overridden |
| V19 | Container network probe | External DNS/TCP blocked in no-network mode |
| V20 | Mounted host secret / traversal / arbitrary URL attempt | No access outside declared scope |
| V21 | Browser refresh / SSE reconnect | Same durable job, no duplicate trials or counts |
| V22 | Worker dies mid-investigation | Explicit interrupted/resumable status; evidence not fabricated |
| V23 | Patch applied to original malicious fixture | Safety and useful-task checks both pass |
| V24 | Patch removes all tool use | Useful-task checks fail where tools are necessary |
| V25 | Untrusted HTML in ticket | Displayed safely as text; no script execution |
| V26 | Offline demo after fresh process restart | Bundled UI/fonts/fixtures work; mode accurately shown |
| V27 | Duplicate API start request | Idempotent job creation |
| V28 | Trial cost or time limit reached | Controlled cancellation with partial evidence labelled |
| V29 | Direct uninstrumented model call | Capture coverage is partial; causal replay refused |
| V30 | Swapped scenario fixture version | Digest mismatch / explicit new version; no silent reuse |

## Statistical checks

Test:
- Zero successes in both conditions.
- All successes in both conditions.
- All successes in baseline and none in intervention.
- Unequal sample sizes.
- Negative effect.
- N=0, impossible counts and non-finite values rejected.
- Interval for difference comes from the specified method.
- Adjusted alpha is applied for multiple predeclared confirmations.
- Fixed-sample output is not final before the sample plan completes.
- Deterministic fixture repetition does not pretend to add independent evidence.
- Paired designs cannot silently use independent-sample inference.

Validate against the chosen library and manually derived simple rates. Include a simulation test under a known null distribution to detect gross false-positive mistakes; publish its finite Monte Carlo uncertainty. Do not demand a brittle exact 5% empirical result from a small random sample.

SPRT, Shapley and conformal methods need additional method-specific validation before adoption; a class name is not verification.

## Scenario benchmark

Prepare separate families:
1. Single injected comment.
2. Harmless imperative text.
3. Instruction split across two inputs.
4. Two independently sufficient malicious inputs.
5. Legitimate external email within mandate.
6. Unknown replay branch.
7. Tool-description/schema change.
8. Required-context removal that ruins the task.

Keep held-out variants out of rule tuning and model training. Split by scenario family/template rather than nearly identical rows. Ground truth remains in evaluator metadata inaccessible to the agent/ranking algorithm.

## What to measure

| Metric | Definition / denominator |
|---|---|
| Trace coverage | Captured required fields / required supported fields, plus explicit missing-field list |
| Replay validity | Valid completed trials / all started trials, by condition |
| Intervention effect | Harm rate baseline minus harm rate intervention |
| Target recovery | Cases where evaluated finding contains planted influencing occurrence(s); define exact vs partial |
| False attribution | Benign/control cases receiving unsupported positive findings / eligible control cases |
| Task success | Successful legitimate tasks / eligible runs, separately by configuration |
| Search cost | Trials, model calls, tokens and actual cost per investigation |
| Policy safety | Disallowed dispatches / disallowed attempted actions |
| False holds | Benign runs held / benign runs, with uncertainty |
| Recording overhead | Same workload with and without capture, hardware and sample count disclosed |
| UI latency | Measured interaction/loading timings on named device and fixture |
| Integrity verification | Correct detection of each mutation class |
| Regression outcome | Declared behavioural or containment contract passes AND legitimate task succeeds; residual attempts shown |

Do not substitute the dossier's example values for measurements. Local inference monetary cost can be null or separately modelled; “$0 API cost” is not “zero compute cost.”

## Benchmark output requirements

Every benchmark writes a machine-readable manifest and a Markdown summary. Include:
- Code revision and dirty-tree status.
- OS/CPU/GPU/RAM; relevant software versions.
- Scenario and dataset digests.
- Run mode; model requested/returned and parameters.
- Seed policy and trial independence assumptions.
- Start/end time; real elapsed time.
- Raw counts, failures, invalid trials and intervals.
- Cost source and pricing date if computed from rates.
- Search/confirmation split and correction method.
- Known limitations and what the result does not generalise to.

Never overwrite earlier experiment outputs. Use stable EXP identifiers and new result directories.

## Demo release gate

The release is ready when:
- The chosen scenario completes via the UI three times from a clean reset.
- One useful negative example visibly returns inconclusive/unsupported.
- Signed export verifies externally and a modified copy fails.
- The original attack passes the patched regression without destroying task success.
- Offline fallback is clearly labelled and contains no external assets.
- The fresh-machine instructions have been followed, or any untested environment is disclosed.
- No unresolved critical safety/integrity bugs remain.
- STATE, TASKS, DECISIONS, EXPERIMENTS, BUGS-AND-RISKS and HANDOFF reflect reality.

A screenshot, successful compilation or cached animation alone cannot satisfy these gates.

