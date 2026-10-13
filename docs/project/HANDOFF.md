# Handoff

Read AGENTS, STATE, TASKS, relevant DECISIONS and the current prompt.
Checkpoint parent: `7a58bfe57f55f4d2e0b9d36e953bf3bc93f6a64f`. Latest continuation: P1 VERIFIED.

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


Goal: P1 owned synthetic incident. User authorised continuous P1–P10 implementation.

Implemented: typed World/SubjectInput/Action/RunResult, reproducible fixtures and
separate evaluator metadata, three owned stdio tools, explicit model interface,
transparent simulator, saved-recording playback and semantic outcomes. Package
rewind_sandbox joins the single Python distribution. API/empty web shell accurately
expose available CLI modes and unavailable real models. No external tool dispatch.

Commands: local locked uv sync; fixture generate; pytest tests/test_sandbox.py
13/13; root check 18/18 plus lint/format/schema/manifest/types/build; root demo
single scenario succeeds; browser 4/4. See artifacts/p1/check.log, demo.log,
pytest.xml and timestamped artifacts/browser/latest.txt. Screenshots at 1440×900,
1280×720 and 390×844 are inspected. No new dependency versions required.

Failure: first stdio scenario suite 7 failed/6 passed because plain dict MCP
responses had no structured_content. Added bounded single-JSON-text decoding.
First failure XML retained; corrected suite passes. Minor formatting issues fixed.

Evidence handling correction: the inherited browser config reused P0 output paths.
Its first P1 run overwrote P0 overview PNGs and playwright.json; those files now
represent P1, not the original P0 revision. The original P0 manifest retains its
old hashes and historical gate record, but affected raw artifacts do not match it.
Future browser runs use distinct timestamped directories; no replacement artifact
is claimed to be an original P0 screenshot. Existing failed mobile trace copies
and P0 API evidence were retained.

Dossier now exists and was included unchanged in the baseline checkpoint; prior
absence corrected in current summaries. No user changes reset/discarded. No paid
service, public deployment or outbound message. Real-model/isolation gates unrun.

Interview explanation: “Our subject is a transparent instruction-following
simulator. It reads a ticket through real MCP stdio, then interprets supplied
directives and may attempt a synthetic attachment send. Code checks recipient
permission and attachment classification independently of scenario labels. Every
send reaches only a local outbox. Scenario expectations live in evaluator files
that the agent never reads. Playback reads a result without deciding again.
Real models have an explicit capability error, never a hidden simulator fallback.
These checks validate the fixture mechanism, not LLM causation or replay isolation.”

Questions: Why must evaluator labels stay out of SubjectInput? Why are attempted
harm and executed mock dispatch separate outcomes? Answers not yet recorded.

Next: P2 stdio recorder/model adapter, encrypted content, signed ordered chain,
seal/verification, partial-capture disclosure and tamper/correlation tests.
