# P7 — Sentinel signed mandates and exact approval lifecycle

Date: 2026-10-15 (Asia/Calcutta). **VERIFIED for the owned simulator/database adapter.**
Recovered clean source checkpoint 373a0e8eb3c0ae72e9965c4a121936c362a90aa1,
master tracking origin/main. Implementation uses ordinary new commits and retains
all prior signed artifacts, logs and unrelated work. Source/artifact hashes and
publication revision mapping: P7-ARTIFACTS.json. Implementation
aca72bd2f0d0278ee1b323a0a318d51fc92d2ff9 is published to origin/main and remote
SHA verified. Git author and committer are the user's authorised Pranshu Jain identity.

## Working behaviour

Signed immutable mandate binds issuer, owned agent/session/world, UTC validity,
tool/data/classification/recipient scope, explicit denial, $0 provider spend and
dispatch/export-row budgets. Unknown identity/signature/schema/scope fails closed.
The local operator's cookie authenticates local-user; caller identity fields are
not accepted. Policy verdict and current enforcement are separate. A hard-denied
export has no Approve control and API approval is rejected.

An in-scope high-impact send is held with a bounded server deadline. Approval binds
exact action/arguments digests, session, mandate version, authenticated actor and
expiry. Revalidation, one-time consumption, immutable local effect, signed event
and idempotency receipt share BEGIN IMMEDIATE. Concurrent decisions/retries do not
dispatch twice. The atomic effect is the owned SQLite mock sink, not an external RPC.

Deny/cancel/expiry are durable. Non-dispatch terminal actions return structured
policy_denied/policy_cancelled/policy_tool_timeout results. Timeout/cancel explicitly
record agent_can_resume=false. The owned stateless adapter can finish with its
recorded approval/denial result; no generic open MCP pause/resume is claimed.
Expiry is materialised on the next snapshot/decision. A late rejected approval
still commits expiration. Restart preserves holds, effects and receipts.

Deny-and-investigate commits denial and intent first, then queues one action-keyed
bounded source investigation. Failure retains denial, records error and supports
retry. The evidence link identifies the earlier full observation-only source;
Forensics does not claim an approval's intervention effect. Original Ledger bundles
and P5 defence presets remain unchanged.

The Sentinel UI reads persisted actions/events and real counts, polls every 1.5s
while visible and recovers across refresh/offline. It displays exact arguments,
mandate/budgets, actor/consumption, deadlines, task success and signed audit download.
Backend digests are compared directly; JS never rebuilds signed bytes.

## Gate evidence

| Requirement | Actual proof |
|---|---|
| Disallowed invocation never dispatches | Scope/signature/identity/rule tests, hard-denial API rejection; EXP-010 forbidden send remains denied in four protected executions |
| Expired/forged mandate fails closed | Signature/unknown-key/issuer/UTC validity matrix and active-mandate revalidation |
| Changed args, stale approval and double requests safe | Exact four-way digest/session/version bindings, altered stored arguments, expired grant, duplicate key conflicts and eight concurrent approvals |
| Eligible action dispatches at most once | Unique immutable effect/consumption, shared-budget competition, approve-vs-cancel race, interrupted-commit rollback and restart/retry tests |
| Timeout/cancel consistent | Server-expiry persistence, explicit policy errors/non-resumability, actual browser/experiment deadline and cancel cases |
| Deny-and-investigate consistent | Denial-first durable intent, same idempotent source job on retry; actual seven completed source investigation trials |
| False holds if anomaly claimed | not_applicable: rule-only policy holds; no anomaly detector/FPR or signal-independence claim |

## Commands and actual outcomes

| Command/check | Outcome / retained evidence |
|---|---|
| python scripts/rewind.py check | 125/125 in 161.93s; lint/format/schema/types/build/manifest pass; artifacts/p7/check-first.log; artifacts/checks/20261014T191823250072Z/pytest.xml |
| pytest tests/test_sentinel.py tests/test_p0.py tests/test_workspace.py | 43/43 in 20.58s; artifacts/p7/affected.log/xml |
| Final affected pytest tests/test_sentinel.py | 33/33 in 15.63s after explicit terminal policy errors; artifacts/p7/mechanism-final.log/xml |
| npm.cmd run test:e2e | 29/29 in 5.4m; artifacts/p7/browser-final.log; browser/2026-10-14T19-20-33-860Z/playwright.json |
| Final affected browser P7 + P0 | 8/8 in 1.5m, explicit three terminal policy errors; artifacts/p7/browser-errors-final.log; final render directory browser/2026-10-14T19-29-02-472Z/ |
| Final schema/static/type/build/manifest | Pass after terminal-error/maturity refinement; generated schema matches; no dependency/lock change |
| p7_benchmark.py | EXP-010 actual source capture, four protected cases, seven source trials, 12.077406s; raw 20261014T192818971254Z |
| Independent CLI | Supplied trusted key, separate cwd/nonexistent data dir; valid=true, nine events, one dispatch; directory remains absent |
| Existing local migration | 0005→0006; every pre-existing table count/content digest unchanged; seven sessions/one investigation/one record/five runs preserved; artifacts/p7/migration.json |

The full root/browser runs precede the final terminal-result/maturity refinement;
affected mechanism/browser checks and static/build checks cover those final changes.
Results are separate runs, never combined into a fabricated total. Provider requests=0.

## Render review and retained failures

Three states (denied, held, dispatched) × 1440×900, 1280×720 and 390×844 are rendered.
Full-page, viewport and action-detail PNGs use p7-{denied,held,dispatched}-{width}
filenames in the final browser directory above. Reviewed final desktop/phone layouts
and exact action controls: no page overflow/fatal JavaScript/external asset requests.
Escape restores focus; refresh keeps approval consumption and source links. Review
moved the active workspace ahead of a long narrow-screen run list, bounded that list,
stacked descriptions and corrected current enforcement from hold to allow/deny while
preserving the initial signed hold event. Accepted P6 fonts/navigation/panels remain.

First mechanism run 30/30; initial browser 4/4 in 1.6m. Lint-first/second/third logs
retain formatting/unused-import issues, then static checks pass. The first local
migration snapshot named nonexistent ledger_records, failed before running migration;
the corrected inspected schema check preserved all old rows (migration-first.json).
Sandbox helper failed before commands; scoped escalated execution and per-command
Git ownership exception worked without changing global trust. No approval rejection,
lost sample or failed run was relabelled a success. Earlier EXP-010 artifacts remain.

## Limits and next phase

Simulator only. No real-model call, training, anomaly/FPR guarantee, generic MCP tool
dispatch, production multi-user identity, external signing anchor, legal fault or
compliance claim. Data effects are synthetic. Mandate template issuance is owned;
a general mandate editing/revocation API is not exposed. Remote transport crash gaps
remain unsupported and cannot inherit the database sink's atomic guarantee. Native
Linux/WSL/fresh-machine, screen-reader and physical-device checks remain not_run.
Next: prompts/08-PREFLIGHT.md. P8 has not started in this phase.
