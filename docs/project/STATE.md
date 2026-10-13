# Current project state

Updated 2026-10-13. P3-SIM verified; P3-REAL blocked; P4 next, P1-P10 authorised.

P0-P2 foundation, owned MCP scenarios, bounded recorder, encrypted ordered events,
signed chain/seal, trusted CLI verification and actual session count work.
P3 adds fresh isolated simulator trials and interventions, strict read resolution,
independent private world state, actual request/response digests and timings.
Linux container is non-root, no-network, read-only and resource-limited; 13 probes
passed. Source setup/probe required after worker changes; image ID pinned locally.

Modes: simulated verified (deterministic DSL, no LLM); playback recording only;
local/remote model unavailable. User has no local model; no provider or paid budget.
Forensics statistics/jobs, Ledger records/regression, Sentinel/Preflight still planned.
Resources/prompts/HTTP MCP and arbitrary frameworks unsupported. Local keys have
no independent external anchor; signatures do not prove truth or legal blame.

Commands (PowerShell):
```
python scripts/rewind.py setup
.venv/Scripts/python.exe -m rewind_replay.cli setup
.venv/Scripts/python.exe -m rewind_replay.cli probe
python scripts/rewind.py check
python scripts/rewind.py demo
python scripts/rewind.py dev
```
Linux uses .venv/bin/python; host app on native Linux/WSL not yet tested.
Replay gate: tests/test_replay.py 4/4, artifacts/p3/pytest.xml and intervention/probe
JSON. Full integration check logged artifacts/p3/check-repaired.log; first failure
preserved in check.log. Windows host and
Linux Docker worker tested; fresh machine and real inference not_run.
Next exact prompt: prompts/04-INVESTIGATION.md.
Session stopped at user's request after context compaction. P4-P10 still authorised,
but not implemented. P4 dependency versions were researched, not added or locked.
