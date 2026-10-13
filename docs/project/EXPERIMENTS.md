# Experiment register

No project experiments have been run yet. Dossier examples are not measured results.

P0 update, 2026-10-13: API/SDK/browser engineering checks are verified in
`evidence/P0.md`. They are not agent behavioural trials, effect measurements or
confidence intervals. EXP-001–007 remain PLANNED; no simulator/model experiment
was executed during P0.

## Planned experiments

| ID | Question | Status |
|---|---|---|
| EXP-001 | Does the simulator correctly exercise single, interacting and redundant inputs? | PLANNED |
| EXP-002 | Do interventions reach fresh model decisions without external tool effects? | PLANNED |
| EXP-003 | What effect and interval result from baseline versus finalist interventions? | PLANNED |
| EXP-004 | Does the patch prevent the original attack while retaining task success? | PLANNED |
| EXP-005 | How much overhead does recording add on the named machine? | PLANNED |
| EXP-006 | Does a ranking/model extension outperform the simple baseline? | PLANNED |
| EXP-007 | How do text similarity and action outcomes differ on controlled cases? | PLANNED |

## Experiment template

~~~text
EXP-NNN — title
Status: planned / running / complete / invalid / interrupted
Question and hypothesis:
Predeclared design / stopping rule:
Code revision and dirty-tree status:
Environment and versions:
Run mode:
Model requested / returned:
Fixture/dataset/configuration digests:
Train/calibration/test separation if relevant:
Target outcome and useful-task predicate:
Interventions / controls:
Discovery vs confirmation:
Trial count plan and budget:
Seed policy / independence or pairing:
Failure/retry policy:
Interval method, alpha and multiplicity:
Raw artifact paths:
Actual counts, invalid trials and denominators:
Effect / interval:
Task success:
Elapsed time / usage / cost:
Interpretation:
Limitations and alternative explanations:
Decision made:
Follow-up:
~~~

## Reporting rules

- Keep failed runs and condition-dependent failures visible.
- Preserve raw outcomes; never overwrite them to improve a summary.
- Simulator evidence does not become real-model evidence.
- Identical playback runs do not increase independent sample size.
- “Inconclusive” is a valid result.
- Attach the exact script/command needed to reproduce.

