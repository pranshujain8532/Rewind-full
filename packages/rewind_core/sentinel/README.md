# Sentinel — owned simulator policy gate

The local `/sentinel` screen starts fresh stateless simulator decisions from a
complete, trusted, signed source capture. Demo A records the forbidden-export
source; Demo B records an owner-authorised send. Those observation-only sources
have their own mock effects. Sentinel executes a separate protected run, with
all effects restricted to its transactional SQLite synthetic outbox.

Mandates are Ed25519-signed under `rewind:mandate:v1`, using the existing pinned
local key. The owned adapter registers agent/session bindings; HTTP clients cannot
claim an agent or approver identity. The local session cookie authenticates one
`local-user` operator, not an externally verified human identity. Mandates are
immutable and scoped to a world digest, validity, tools, data IDs/classifications,
exact case-insensitive recipient allowlist, explicit denials, dispatch/row budgets
and approval constraints. Provider spend is fixed at $0. No provider calls occur.

Unknown schemas/arguments fail closed. Rules do not inspect scenario names, attack
labels or model-supplied costs. The policy verdict remains separate from the current
enforcement decision. A hard denial never gains an Approve control or override API.
Scope changes require a newly authorised mandate version; a general editing/issuance
API is not provided in this owned demo.

An eligible decision binds both canonical action and arguments digests, session,
mandate version and authenticated approver. It creates and consumes the expiring
approval atomically with the effect. `BEGIN IMMEDIATE`, immutable approval/effect
rows, unique action IDs and idempotency receipts prevent races/retries from sending
twice. Revalidation covers current signature, identity, scope, budget, deadline and
mandate version. The adapter performs no network RPC inside this transaction; a
production transport requires its own reviewed idempotency/uncertain-outcome contract.

Held actions have a server deadline (default 60s, configurable 1–300s). Expiration is
persisted on the next snapshot/decision; even a rejected late approval retains it.
Timeout and cancellation record `agent_can_resume=false`. Terminal non-dispatch
states return a structured policy_denied/policy_cancelled/policy_tool_timeout error,
retained in the signed transition event. The owned stateless adapter can finish
with the recorded policy result after approval/denial. This is a durable
owned adapter, not an open MCP call or generic framework pause/resume protocol.
Process restart preserves pending actions and receipts. There is no execution retry
after a terminal disposition. Task success requires the exact summary and every
owner-requested send; blocking a required send fails useful work.

Deny-and-investigate first commits denial and a durable intent. The API then queues
one bounded simulator investigation with an action-derived idempotency key, recording
the link or an explicit retryable failure. Forensics investigates the earlier full
source capture, not a claimed causal effect of the Sentinel approval. Existing Ledger
records and P5 regression presets are unchanged; policy audits are separate downloads.

The UI polls persisted snapshots/events while visible, replaces complete lists and
reads actual counters. Refresh/reconnect never creates a trial or increases a count.
Audit events have a separate signing domain and ordered linked hashes. A signed
download commits the complete current event head/count and actual effect counts;
verification uses a separately supplied key, not a bundled trust anchor:

```powershell
.venv/Scripts/python.exe -m rewind_core.sentinel.verify sentinel-audit.json --trusted-public-key data/keys/trusted-public.ed25519
.venv/Scripts/python.exe scripts/p7_benchmark.py
.venv/Scripts/python.exe -m pytest tests/test_sentinel.py
```

No anomaly detector/training, false-hold/FPR claim, transformer, real agent support,
production multi-user trust, public deployment or external side effect is included.
Current gate evidence: `docs/project/evidence/P7-SIM.md`.
