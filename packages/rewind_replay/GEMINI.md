# Gemini exploratory re-execution

The backend reads `GEMINI_API_KEY` or the root `api.txt` file. The file is ignored
by Git and excluded from the Docker build context. Do not put a key in command
arguments, browser configuration or captures. The worker receives no key.

The pinned adapter uses `gemini-3.1-flash-lite` through Google's HTTPS REST API.
It receives only an owned synthetic subject input. Its structured JSON contains
a ticket summary and proposed mock mail actions; it has no executable provider
tools. Unknown tool arguments invalidate the trial before dispatch. Every trial
uses fresh input, provider request and private mock state. No response cache.

After the existing setup, migration, replay setup and isolation probe:

```powershell
.venv/Scripts/python.exe -m rewind_replay.gemini_cli catalog
.venv/Scripts/python.exe -m rewind_replay.gemini_cli smoke --billing-mode declared_free_tier --authorised-cost-usd 0 --max-requests 3
```

`catalog` checks authentication and model metadata, not inference quota or billing.
`smoke` requires an explicit billing declaration; default inference is disabled.
The user authorised a free-tier project and $0 spend. The broker relies on that
project declaration: Google does not expose the billing tier through this key.
There is no paid fallback, provisioning or automatic retry. Each invocation is
bounded by requests (three by default), 32,000 reserved tokens, 180 seconds,
8,192 input tokens and 1,024 output tokens per request. Failed requests retain
their reservations. Paid mode refuses a zero budget. Changing billing permission
requires a separate user instruction.

The no-network container makes one nonce-bound completion request through a
pipe. The parent validates the exact transformed request and permits only the
pinned provider's catalog, countTokens and generateContent endpoints. It reserves
tokens/cost and persists a signed capture event before generation. The HTTP
transport refuses redirects and environment proxies. Captures retain request,
response, requested/returned model, usage and provider response identity, but
never authentication headers. A seed is not a provider determinism guarantee.

Each invocation writes a new `artifacts/gemini/<UTC timestamp>/` directory with
a frozen exploratory plan and raw results. Valid and invalid returned trials are
recorded in SQLite and sealed with distinct completion/validity fields. A transport
failure or killed CLI can leave an explicitly unsealed partial session. This CLI
does not have the durable P4 job/lease lifecycle and cannot resume confirmation.

The 2026-10-14 live smoke made exactly three generation requests: baseline and
removal were valid; neutral replacement proposed an unknown attachment and was
invalid. The invalid result was recovered into its signed capture from the retained
raw result after fixing persistence; that recovery is disclosed in capture-audit.json.
No repeat, replacement sample, pooled estimate or interval was computed.

API and browser Forensics admit only the existing simulator contract. Gemini
captures remain visible but ineligible. General production tools, strict-recorded
remote tool replay, repeated-input variability, P4 real-model discovery/confirmation
and durable remote job budgets are unverified or unsupported. A successful signed
capture establishes integrity, not experimental validity or causal attribution.

Evidence: `docs/project/evidence/P3-REAL.md`, EXP-008 and ADR-015. Provider-free
tests use explicitly labelled unit replies; these are never live model evidence.
