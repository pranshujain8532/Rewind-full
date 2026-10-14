# Gemini follow-up limitations and observed fixes

2026-10-14. See EXP-008 and P3-REAL.md for results and acceptance scope.

BUG-008 — Invalid remote trial was not appended as a signed outcome before abort.
Severity: medium. Status: verified fixed by provider-free persistence test.
Observed: smoke's third actual result was in raw results.json and the signed
provider-response event, but its session was unsealed after real_trial_invalid.
Fix: persist/seal returned results before validity abort; completed=false for invalid
trials, no fabricated outcome booleans or dispatches. Recovered original third
result locally from exact retained raw bytes; disclosed in capture-audit.json.
Evidence: persistence-pytest.xml, actual signed capture exports and audit. A CLI
transport failure or process interruption can still leave a partial unsealed capture;
P4 durable remote jobs/resumption remain unsupported.

R-012 — User-declared free-tier billing cannot be independently verified from key.
Status: accepted scope for this authorised three-call smoke. Inference is disabled
by default; explicit free-tier declaration/$0 cap, no retries or paid fallback.
Charged spend is not measured. Never describe a reservation of $0 as a verified bill.

R-013 — Structured proposal guessed an attachment outside the owned world.
Status: observed limitation, fail-closed verified by actual smoke. No dispatch;
invalid trial omitted from successful/harm-absent denominators. Next task needs an
explicit captured available-file argument contract before real confirmation admission.

ENV-004 — Cold scientific imports delayed schema export and API startup.
Status: verified readiness mitigation; final checks referenced in P3-REAL.md.
Bounded stack diagnostic located SciPy import through statsmodels/proportion during
API import. Moved library loading to interval calculation; same version/method.
First check stopped deliberately while stalled; first browser server timed out.
No package replacement or operating-system security-setting changes.
Diagnostic pinned-library import eventually completed in 127.768s; startup no
longer requires it. Root check 72/72 and browser 15/15 pass. No general latency
claim or recording-overhead benchmark is inferred from this import diagnostic.

Browser follow-up: stale assertion expected three unavailable evidence labels;
Gemini now correctly has exploratory evidence. Playwright toBeDisabled did not
recognise the disabled DOM option despite its disabled attribute; the admission
test now checks the actual DOM disabled property and absence of unsupported graph
requests. Display-only controls live in tests, never runtime evidence or model counts.
Original timeout/assertion logs and trace directories remain retained.
