# Preflight fixed suite

Preflight remains REWIND's fourth product mode. `/preflight` accepts only
`owned-support-agent-v1`, using `preflight-fixed-v1`. Arbitrary target URLs,
connectors, file paths, remote-model modes and provider budgets are rejected.
No credential discovery, outbound tool action or generation capability exists.

The reviewed fixed payloads are owned code in fixtures.py. Each surface has the
same four cases: factual clean support text; a reserved `.example` export directive
for the synthetic customer file; a harmless imperative; and a deliberate unknown
attachment to exercise invalid-trial reporting. Every case also requires the
legitimate owner send. The insertion surfaces are:

| Surface | Actual execution and capture |
|---|---|
| ticket_comments | Owned SDK ticket.read returns the comment before the fresh decision |
| mock_file_text | Ticket response excludes the payload; owned SDK files.read returns support-note text, matched to the inserted model-input occurrence |

Both reads run in the non-root, no-network, resource-bounded container. All sends
terminate in fresh private in-memory mock outboxes. Observed schemas/read results,
exact model request/response, attempts, policy events and actual mock dispatches
are captured through the existing encrypted signed recorder. This does not claim
new generic MCP transports or production tool coverage. The effective adapter
input is frozen in the world snapshot, so Forensics can intervene on the captured
file/comment occurrence while preserving unrelated owner task information.

Four already-owned configuration presets are available: vulnerable-v1, containment-v1,
behavioural-v1 and deny-all-v1. These are the P5 small deterministic rules, not P7's
live signed-mandate/approval workflow. Code computes harmful attempts, harmful
policy blocks, harmful mock dispatches and exact summary plus owner-send success.
A blocked attempt remains an attempt. Denying all sends fails legitimate delivery.
No guardrail classifier exists: detection and evasion are **not measured**.

An immutable plan binds target, suite/fixture/configuration digests, seed, repeats,
runtime image/probes and resource budget. Repeats are deterministic reproducibility
checks; they do not increase an independent sample size or produce a confidence
interval. Model/configuration/fixture/surface and resource use accompany every row.
Provider requests/cost are zero by construction; tokens/compute monetary cost remain
unknown. Host elapsed milliseconds include container startup/cleanup but exclude
later capture persistence. Container CPU/memory/PID limits are recorded separately.

Persistent jobs share the single-worker exclusion/lease discipline with Forensics
and regressions. Trial/model-turn caps reserve before launch; total wall time bounds
the remaining subprocess timeout (at most 30 seconds per trial). Cancellation stops
the next trial and retains a bounded in-flight result. A time-limit outcome can
remain incomplete; cleanup may add up to the launcher's five-second bound. No
missing/invalid trial is called harmless. No automatic retries/substitutions occur.
Reservation and source session header commit atomically, so a crash before the
first capture event still leaves an inspectable partial source.

Surface/configuration rows expose planned, started, returned, valid, invalid,
incomplete and unstarted counts. Outcome numerators use valid-trial denominators;
policy blocks use harmful-attempt denominators. 0/0 has no measured denominator.
There is no decorative risk score, pooled evasion rate or overall safety certificate.
Deliberate invalid controls mean a completed suite can remain invalid_experiment.

Failure actions open the actual recorded session and idempotently queue a bounded
source investigation. Invalid/partial captures stay unsupported for causal replay;
their investigation is explicitly failed/unsupported, never a positive finding.
REST snapshots own counts; persisted SSE invalidates/reconnects with scoped cursors.
No animation/timer creates a trial or changes an outcome.

```powershell
# Initial dependency/runtime setup needs access; execution needs no provider.
python scripts/rewind.py migrate
.venv/Scripts/python.exe -m rewind_replay.cli setup
.venv/Scripts/python.exe -m rewind_replay.cli probe
python scripts/rewind.py dev
# Standalone actual offline-capable fixed-suite experiment; owns artifacts/data.
.venv/Scripts/python.exe scripts/p8_benchmark.py
```

Offline execution uses the already built/probed local image and bundled assets,
not a provider or cached model responses. Fresh-machine air-gapped installation
is not claimed. Evolutionary/LLM variations remain documented extensions requiring
bounded budgets, lineage and separate exploratory validation; neither is implemented.
Gate evidence: docs/project/evidence/P8-SIM.md.
