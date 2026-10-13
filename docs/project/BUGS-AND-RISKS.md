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
| R-011 | Low | Claimed original dossier retention cannot be verified; supplied reference directory empty | OPEN | Get-ChildItem returned no files; corrected implementation contracts sufficient for P0; recover source separately if needed |
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

