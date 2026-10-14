# Bugs and risks

P0 is verified. Later mechanisms retain the design risks below; a passing shell
does not resolve replay, statistics, signing or approval risks. Observed P0 bugs
and environment limitations follow the retained templates.

| ID | Severity | Risk | Mitigation / gate | Status |
|---|---|---|---|---|
| R-001 | Critical | Cached replies masquerade as counterfactual inference | Mode separation and fresh-request tests | MITIGATED (SIM, EXPLORATORY GEMINI CLI); REAL CONFIRMATION UNSUPPORTED |
| R-002 | Critical | Replay can dispatch real side effects | Runtime isolation and local mock tools | MITIGATED (OWNED SIM/GEMINI MOCKS); OTHER TOOLS UNSUPPORTED |
| R-003 | High | Partial capture produces overconfident findings | Replay-readiness and explicit unsupported states | MITIGATED (SUPPORTED CAPTURE); OTHER INTEGRATIONS UNSUPPORTED |
| R-004 | High | Invalid statistical inference | Frozen confirmation design and tested interval method | MITIGATED (P4 SIM); REAL ASSUMPTIONS UNVERIFIED |
| R-005 | High | Policy approval reused or bypassed | Action binding, expiry, one-time consumption | MITIGATED (P7 OWNED SIMULATOR/SQLITE SINK); GENERIC EXTERNAL DISPATCH UNSUPPORTED |
| R-006 | High | Evidence store leaks content or implies false trust | Synthetic data, encryption, redaction and trusted-key verification | OPEN |
| R-007 | Medium | Real model unavailable on budget/hardware | Explicit capability state and offline fallback | GEMINI CLI AVAILABLE ($0 USER-DECLARED FREE TIER); REAL FORENSICS UNSUPPORTED |
| R-008 | Medium | Protocol/library mismatch | Pin versions and test integration | MITIGATED (OWNED STDIO); OTHER TRANSPORTS UNSUPPORTED |
| R-009 | Medium | UI presents invented progress or certainty | Durable events and shared evidence components | MITIGATED (P6/P7 SUPPORTED UI); REAL-MODE SUPPORT UNVERIFIED |
| R-010 | Medium | Accepted scope expands too far | Phase gates and explicit research backlog | OPEN |

## Bug template

~~~text
BUG-NNN — short title
Severity:
Status: open / investigating / fixed-unverified / verified / accepted limitation
First seen / revision:
Expected:
Actual:
Reproduction:
Environment / mode:
Evidence:
Likely cause:
Fix:
Verification command and actual result:
Affected experiments / reports:
Remaining limitation:
~~~

Do not close a risk just because a mitigation was written in a document. Link implemented evidence.

## P0 observed issues — 2026-10-13

| ID | Severity | Issue | Status | Evidence / next step |
|---|---|---|---|---|
| BUG-001 | Medium | Phone Refresh button lost accessible name when text hidden | VERIFIED FIXED | Explicit aria-label; first browser run 3/4, final 4/4; preserved mobile-refresh-failure.zip |
| BUG-002 | Low | Setup rejected uv 0.13.0 build suffix | VERIFIED FIXED | Parse version token; complete setup rerun succeeds |
| R-011 | Low | Original dossier was absent during P0 | RESOLVED | Present on P1 resume, 126135 bytes; preserved in baseline 7a58bfe; corrected contracts still authoritative |
| ENV-001 | Medium | Docker daemon unavailable during P0 | RESOLVED FOR DAEMON AVAILABILITY | SESSION-002: client/server 29.6.2 responds; no REWIND container/isolation test run; P3 boundary remains required |
| ENV-002 | Low | Git metadata owned by sandbox account; host git status rejects ownership | ACCEPTED LIMITATION | Read-only status works with command-scoped safe.directory for this exact repository; no global setting changed |

BUG-001 reproduction: browser width 390, getByRole button name Refresh status
cannot find the icon-only button. Fix is in App.tsx. Final Playwright JSON contains
four expected results, zero unexpected/skipped/flaky; normal viewport cases also
check console/page errors, keyboard refresh and overflow.

BUG-002 reproduction: setup compared uv's entire version string with `uv 0.13.0`,
but installed output includes build metadata. Its second token is now checked.
Both fixes are covered by executed commands in `evidence/P0.md`.

P0 npm peer-resolution and MCP test-keyword failures are recorded in SESSION-001
and ADR-007/008. R-008 is mitigated at SDK compatibility level only; real stdio and
capture coverage remain unverified. R-001–010 remain OPEN for their future gates.

Auto-review rejected an attempted recursive .git ownership change as an
unauthorised persistent mutation. It was not executed and is not required for
P0; ENV-002 uses the read-only command already verified. Do not retry ownership
changes or silently add global Git trust settings.


## P3 boundary review — 2026-10-13

- BUG-003 verified: proxy deadline test flaked in the full suite because its
  six-second process bound included Windows imports before the relay timer.
  Independent run passed; bounded test deadline now fifteen seconds including
  startup. Production relay lifetime unchanged. First failure preserved in
  artifacts/p3/check.log; repaired full suite 36/36 in check-repaired.log.
- BUG-004 verified: strict downstream file read initially fell back to mock world.
  Removed before P3 gate; test_strict_downstream_read_never_falls_back proves
  missing downstream match invalidates a fresh trial. No positive finding shipped.
- ENV-001 now verified for P3 Docker isolation, not just daemon availability;
  thirteen actual probes passed. Native WSL/Linux host app remains not_run.
- Real-model runtime unavailable, confirmed by user. No real-model gate claim.
- Read-only API is still a shell; local authentication must precede P4 mutations.
  No production/private-data deployment, external trust anchoring or kernel security
  guarantee. Last UI inspection P2; P3 metadata changes build/type-checked only.


## P4 observations — 2026-10-14 (Asia/Calcutta)

- BUG-005: unit job tests depended on the mutable live runtime manifest. A rebuild
  temporarily sets isolation_verified=false; the third P4 run consequently failed
  9/26 tests. Fixed with a test-only admission stub, separate from the actual Docker
  benchmark. artifacts/p4/third-pytest.xml is retained; subsequent suite passes.
- BUG-006: tightening schema admission briefly referenced schema before assignment.
  Caught by lint and the sixth suite (13 failed/15 passed), never accepted as a gate.
  Fixed ordering and fail-closed malformed/changed schema handling. New schema and
  cached-result refusal tests pass; artifacts/p4/sixth-pytest.xml and
  seventh-pytest.xml retain failure and corrected 28/28 results.
- BUG-007: visual QA found that the overview retained its initial session count
  after a successful capture (first 1440 screenshot showed zero alongside a stored
  investigation). Implemented a quiet backend metadata refresh and a count-aware
  badge; final 12/12 browser run and inspected count screenshots verify the fix.
- Initial browser P4 assertions used the default five-second wait, shorter than
  actual MCP capture work and the declared 15-second worker lease expiry. First run
  6 failed/5 passed in artifacts/browser/2026-10-13T18-52-54-385Z. Bound assertions
  now allow 60 seconds and bind to the newly returned durable job ID; second run
  11/11 in 2026-10-13T18-55-56-299Z. Final corrected-count run 12/12 in
  artifacts/browser/2026-10-13T19-14-25-635Z; real worker termination verified.
- TypeScript caught an optional generated tested_subsets default; the contract now
  requires the stored coverage array and the renderer handles absent historical
  data defensively. Final build/types/schema drift checks pass.
- ENV-003: sandbox process setup failed (helper setup refresh errors). Authorised
  host execution works with repository-scoped safe.directory. No ownership/global
  Git trust changes, repository reset, paid inference or external message.
- R-004/R-009 mitigated for the tested simulator/job boundary: stored counts,
  frozen independent plans, refusal of deterministic/paired inference, task checks,
  durable SSE and lease recovery. Real-model assumptions and full P6 evidence UX
  remain unverified. Raw trials are not yet signed Ledger records (P5).

## Gemini follow-up — 2026-10-14

BUG-008, R-012/R-013 and ENV-004 are recorded in
[GEMINI-NOTES.md](evidence/GEMINI-NOTES.md), with original failure artifacts,
the actual invalid-response limitation, signed recovery disclosure and budget scope.
Fresh hosted decisions now work through the exploratory CLI. Remote fixed-plan
investigations and their durable budget/independence gate remain unsupported.

## P5 observed issues — 2026-10-14

- BUG-009 VERIFIED FIXED: browser parse/stringify rounded 64-bit seeds and failed
  genuine downloaded bundles. Exact bytes verified independently. API now accepts
  original bytes with explicit X-REWIND-Trusted-Public-Key; rounded input is rejected
  in unit tests. Schema regenerated. Do not change signing canonicalisation to JS.
- BUG-010 VERIFIED FIXED: starting a new regression temporarily showed the previous
  completed run; the browser test also asserted that old ID. Pending state now clears
  the old result, stored contract/version are shown, and tests bind the returned ID.
- BUG-011 VERIFIED FIXED: readable wide table caused mobile grid min-content overflow.
  Grid child min-width=0 contains a keyboard-scrollable result region; final 390 test
  and inspected render pass. Earlier 2/3 output/trace retained.
- ENV-005: fixed-plan browser wait was 60s; actual queued/batched work and cold
  interval loading exceeded it. Stored job subsequently completed. Test waits now
  bounded at 120s within the unchanged 600s experiment budget. No sample/stopping
  rule changed; successful refresh clears stale transport warnings.
- Initial P5 unit suite 14/15 failed an untyped string injected via model_copy;
  corrected enum construction passes. This is not evidence of a provider attempt.
- R-005 remains OPEN for full Sentinel approvals; P5 only has declared owned
  recipient/deny-all presets. Governance mapping pending; signer trust lacks an
  external anchor. Full real-mode and generic production regression remain unsupported.
- Public GitHub push is explicitly authorised; user selected a real noreply identity.
  Private keys, api.txt, data and ordinary artifacts remain excluded. Previous commit
  authors/timestamps are retained. No fabricated contribution history.

## P6 observed issues - 2026-10-14

- BUG-012 VERIFIED FIXED: JavaScript JSON numbers can round uint64 seeds in plan/
  payload previews. Backend supplies exact plan_json/payload_text; browser asserts
  the frozen N=40 text and 18446744073709551615. Signed downloads remain raw bytes.
- BUG-013 VERIFIED FIXED: refresh restored a containment result while form defaults
  implied behavioural-v1. Snapshot now carries stored source record/contract, and
  controls restore its configuration. Three viewports pass explicit assertions.
  Held actual API transport also verifies that a pending new start clears the old pass.
- UI review corrected stacked provenance, small source labels, clipped mobile menu/
  hidden selection, wrapping times and capture/replay/integrity conflation. Scope and
  exact before/after screenshot paths: evidence/P6-UI.md. No source trial relabelled.
- First browser selectors were ambiguous (multiple accessible statuses); one test
  closed its new default-open mobile table. Offline mono face was bundled but unused
  on an error screen; explicit load verifies availability. Original failures retained.
- ENV-006 resolved: automatic approval review hit usage limit, not an unsafe-action
  rejection. The first call did not save its test file/run validation. On continuation,
  zero-test retry was recorded, file saved, real tests run. No bypass was used.
- Performance proposed <100ms interaction was not met in the first 204.9ms sample;
  later 94.1ms sample is not a distribution guarantee. Native screen-reader/physical-
  device/Linux verification remains unrun. Offline is an asset shell, not live evidence.
- User subsequently authorised the old commit identity correction; historical hashes
  resolve through GIT-IDENTITY-20261014.md. P6 makes ordinary new commits, no backdating.
## P7 observations — 2026-10-15

- BUG-014 VERIFIED FIXED: initial operator denial/expiry/approved snapshots retained
  hold enforcement despite a terminal disposition. Current enforcement now changes
  to deny/allow; policy verdict remains separate and initial signed hold persists.
  Full 125-test check, EXP-010 and all three-viewpoint browser states verify the fix.
- BUG-015 VERIFIED FIXED: narrow-screen run list pushed active actions far down.
  Active workspace now precedes the bounded run list; descriptions stack and action
  controls remain readable. Final nine action screenshots reviewed, zero page overflow.
- Terminal denied/cancelled/expired actions now expose structured policy errors,
  including non-resumable timeout/cancel. Post-refinement 33 mechanism and 8 affected
  browser checks pass; earlier full root/browser results remain separate evidence.
- First migration preservation query used the wrong Ledger table name; it failed
  before migration. Corrected inspected names preserve every old row digest/count.
  Lint/format failures and earlier experiment/render artifacts remain retained.
- ENV-007 ACCEPTED LIMITATION: sandbox helper failed before any command could start;
  scoped escalated commands worked. Per-command Git ownership exception retained.
  No global safe.directory, history rewrite, paid service or deployment occurred.
- R-005 is mitigated only for the owned transactional database tools. Generic remote
  delivery/cancellation/unknown tool outcome, production identity/key custody and
  universal framework pause/resume remain unsupported. Deadlines materialise lazily
  on read/decision; no background open MCP call is claimed. No anomaly/FPR guarantee.
- Deny-and-investigate cannot release an action if admission/queue/link fails; its
  durable intent and stable job key allow retry. Source Forensics is conditional
  evidence on the earlier observation-only capture. Historical Ledger approvals
  remain absent; no bundle is rewritten to imply newly captured policy evidence.
- Gate/source/commands/limits: evidence/P7-SIM.md. No unresolved critical supported
  P7 gate failure remains. Native Linux/WSL/fresh-machine/physical-device checks unrun.
## P8 observations - 2026-10-15

- BUG-016 VERIFIED FIXED: first mechanism suite returned valid simulator outcomes but
  their source captures lacked explicit tool_schema events. Trusted integrity passed;
  completeness correctly failed. Added the actual observed SDK schemas to the existing
  recorder, preserving the readiness invariant. First 17 pass/1 fail log remains;
  corrected 25/25 and full 150/150 pass, including actual source admission/navigation.
- Review found a crash gap between reservation and source-header creation. They now
  share one transaction. Actual unit fault injection before the first event retains
  an inspectable unsealed source and incomplete trial, never a completed outcome.
- Parent recomputes policy-block/useful-task facts and validates fixture/config/model/
  protocol/read identities. Deliberate invalid argument cases stay in coverage with
  unknown outcome cells. Duplicate cancellation no longer appends unbounded events.
- P8 rebuild/probe required for the new surface operation; old image admission fails
  closed. Runtime 27023d71a5287de03e5f6ae0888e68640bd47f59a81188e483ada96b905ebc96,
  all 13 isolation probes pass. Existing P3/P4/P5/P7 semantics remain covered by the
  full repository/browser checks; no runtime protocol/dependency version changed.
- Policy rules are owned P5 presets. Guardrail classifier detection/evasion, compute
  monetary cost, evolutionary generation, LLM variations and general external targets
  remain absent/not measured. Repeated deterministic fixtures do not create IID rates.
- Offline execution needs the already built/probed local image and installed assets.
  Native Linux/WSL/fresh-machine/physical-device/screen-reader certification remains unrun.
- Exact fixed-suite counts, bounded timeout/cancel coverage and source investigation
  evidence are in EXP-011/evidence/P8-SIM.md; raw failures are not relabelled successes.
