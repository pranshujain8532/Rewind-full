# Current project state

Updated: 2026-10-13 (Asia/Calcutta). Phase: P1 VERIFIED; P2 next in authorised P1–P10 run.

## Working now

- P0 API/storage/web foundation; generated schemas/types and locked setup/check.
- Six versioned synthetic support scenarios; evaluator expectations stored separately.
- Three owned MCP stdio servers (ticket/files/mail), SDK 2.3.0 / revision 2026-07-28.
- Transparent deterministic instruction DSL simulator; semantic attempted/executed
  harmful-action and required-ticket-fact task-success predicates.
- Per-run cloned world/outbox/configuration and actual result JSON, no external mail.
- Explicit saved-recording playback; no fresh decision or independent evidence claim.
- API reports simulator/playback available, real modes unavailable; CLI-only demo now.

## Modes / limitations

Simulator: verified owned host mocks; no network-isolation or LLM claim.
Playback: verified explicit recording read; no statistical use.
Local/remote model: unavailable; adapters/model/provider/budget absent, no fallback.
Recorder/signing, replay isolation, inference/statistics, Sentinel/Preflight remain future.
Docker 29.6.2 Linux engine responds; container/egress boundary not yet tested.
Original dossier now present (126135 bytes); P0 absence is historical, R-011 resolved.

## Commands (repository root, PowerShell)

```powershell
python scripts/rewind.py setup
python scripts/rewind.py check
python scripts/rewind.py demo
python scripts/rewind.py dev
.venv/Scripts/python.exe -m rewind_sandbox.cli generate
.venv/Scripts/python.exe -m rewind_sandbox.cli playback --recording PATH_TO_RESULT_JSON
npm.cmd run test:e2e
```

Demo now runs the single injected simulator scenario; it does not send real mail.
Checks write timestamped artifacts/checks directories. Browser results/screenshots
write timestamped artifacts/browser directories; latest.txt locates the current run.
P1 evidence: docs/project/evidence/P1.md; artifacts/p1/check.log, demo.log, pytest.xml.

## Gate / next

P1 scenario suite: 13/13; full backend suite: 18/18; type/build/schema/manifest and
four browser cases pass. Initial decoding failure retained in artifacts/p1/first-failure.xml.
Continue prompts/02-CAPTURE.md, through P10 after each gate/docs checkpoint.
Git baseline checkpoint 7a58bfe; subsequent phase commits preserve work; no push.
