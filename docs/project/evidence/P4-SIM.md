# P4-SIM — VERIFIED

Date: 2026-10-14 Asia/Calcutta. Parent revision `ffea7be`; dirty P4 implementation.
Final experiment manifest records 54 source-file digests. Raw artifact hashes and
paths are in `P4-ARTIFACTS.json`. P3-REAL remains blocked; no LLM evidence is claimed.

The browser can capture an owned scenario with a neutral control, inspect observed
input/action relationships and transparent candidate features, start an idempotent
durable investigation, observe real stored progress, refresh, cancel and recover
an expired worker lease. Discovery records every bounded single/pair/group/control
subset; coverage retains every occurrence, including low-ranked untested inputs.
Confirmation freezes finalists/N/order/streams/budgets/invalid policy/alpha/effect
threshold before any fresh confirmation reservation. No playback inference,
deterministic CI, paired-design substitution or fixed-CI optional stopping exists.

| Gate | Actual evidence | Result |
|---|---|---|
| Counts/method boundaries | Independent Wilson/Newcombe derivation, zero/all/negative/unequal counts, invalid counts, paired/deterministic refusal | Passed |
| Multiplicity and uncertainty | m=3 adjusted alpha, actual 98.3333% level; weak-baseline inconclusive and negative effect | Passed |
| Single/pair/redundant/benign/task destruction | Stored discovery controls and ten actual case artifacts | Passed, simulator only |
| Fresh fixed confirmation | Frozen DB trigger, fresh disjoint streams, unique response IDs, duplicate/cache refusal | Passed |
| Invalid/incomplete evidence | Invalid trials abort; partial jobs have no final CI/remedy; useful-task failure remains visible | Passed |
| Durable starts/events | Transactional reservations/results/events, idempotency conflict checks, SSE replay cursors | Passed |
| Refresh/cancel/worker loss | Actual browser refresh/cancellation and actual killed worker with lease recovery | Passed |
| Actual execution isolation | Final image pinned; non-root/no-network/read-only/resource limits, 13 negative probes | Passed |
| Rendered UI | 1440x900, 1280x720, 390x844; stored count refresh and uncertainty/status screens inspected | Passed |

Commands and results:

- `uv lock` / `uv sync --locked`: pinned statsmodels 0.14.6 and transitive stack installed;
  official API/installed Newcombe source/licences inspected. Manifest checks match.
- `.venv/Scripts/python.exe -m rewind_replay.cli setup`: final corrected source image
  `sha256:17f9a28be270109687aa2525f100deec2f5922fc7c0b3a947c0eaef5e4aca537`.
- `.venv/Scripts/python.exe scripts/p4_benchmark.py`: final EXP-003 directory
  `artifacts/p4/EXP-003/20261013T191254500930Z/`; ten cases, 481 valid completed
  outcomes, zero invalids, 173.196 seconds including the kill audit. Actual killed
  worker retains 13 started/5 completed trials; interrupted, no final CI/remedy.
- `python scripts/rewind.py check`: 64/64 tests in 121.89 seconds, lint/format,
  schema drift, TypeScript/Vite build and dependency manifest pass. XML:
  `artifacts/checks/20261013T191430496205Z/pytest.xml`; log `artifacts/p4/check-final.log`.
- `npm run test:e2e`: 12/12 real browser journeys, 2.2 minutes. Raw outputs:
  `artifacts/browser/2026-10-13T19-14-25-635Z/`; log `artifacts/p4/browser-final.log`.
  Inspected p4-completed-{1440,1280,390}.png, p4-confirmation.png and
  p4-inconclusive.png; other status PNGs and Playwright results retained.
- Null calibration: `artifacts/p4/null/20261013T191559638566Z/result.json`,
  89/2000 rejections, 4.45%, Monte Carlo 95% Wilson interval 3.63–5.44%.

Measured single stochastic case: 32/40 versus 0/40 harmful attempts, all useful
tasks retained, difference .80, 95% Newcombe interval [.628374, .895000]. This is
an estimated 80-point reduction in the simulator; the interval quantifies uncertainty
under the declared independent Bernoulli gating, without generalising to an LLM.
Redundant joint removal uses m=3 and a 98.3333% adjusted interval. Low baseline
5/40 versus 0/40 misses the meaningful .20 effect threshold and stays inconclusive.

Limits: only owned stateless synthetic support/stdio schemas and a recorded owned
neutral control. Legacy captures without that control remain stored but unsupported
for this design. Eight selected candidates/top-three pairs/full selected group do
not establish global minimality or safety of untested inputs. Shared baseline with
Bonferroni correction; zero retries; up to eight in-flight outcomes can finish on
cancel. Interrupted work needs a deliberate new experiment. Local trust anchor,
synthetic plaintext developer exports, no private/multi-user deployment assurance.
Native Linux/WSL hosting and fresh-machine setup not_run; real inference blocked.
Ledger signing of investigation records and original-attack regression are P5.

Failures preserved: third unit run depended on temporary live admission state;
sixth unit run caught schema validation ordering; first browser run used five-second
assertions; TypeScript caught an optional field; initial visual QA found stale
session-count metadata. Fixes and successful final evidence are linked in BUGS.
