# Bugs and risks

P0 is verified. Later mechanisms retain the design risks below; a passing shell
does not resolve replay, statistics, signing or approval risks. Observed P0 bugs
and environment limitations follow the retained templates.

| ID | Severity | Risk | Mitigation / gate | Status |
|---|---|---|---|---|
| R-001 | Critical | Cached replies masquerade as counterfactual inference | Mode separation and fresh-request tests | OPEN |
| R-002 | Critical | Replay can dispatch real side effects | Runtime isolation and local mock tools | OPEN |
| R-003 | High | Partial capture produces overconfident findings | Replay-readiness and explicit unsupported states | OPEN |
| R-004 | High | Invalid statistical inference | Frozen confirmation design and tested interval method | OPEN |
| R-005 | High | Policy approval reused or bypassed | Action binding, expiry, one-time consumption | OPEN |
| R-006 | High | Evidence store leaks content or implies false trust | Synthetic data, encryption, redaction and trusted-key verification | OPEN |
| R-007 | Medium | Real model unavailable on budget/hardware | Explicit capability state and offline fallback | OPEN |
| R-008 | Medium | Protocol/library mismatch | Pin versions and test integration | OPEN |
| R-009 | Medium | UI presents invented progress or certainty | Durable events and shared evidence components | OPEN |
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

