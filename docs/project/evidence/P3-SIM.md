# P3-SIM — VERIFIED

Parent revision: `fbb5202460660e9ab1c1cc953dc139815a9b026d`.

Goal: complete P3 simulator gate; real-model gate separately blocked.

Implemented fresh full-snapshot trials, occurrence removals and length-matched
neutral replacements, separate attempted/dispatch/task predicates, cloned private
outboxes, strict recorded reads keyed by tool/schema/arguments/occurrence/state.
An unknown initial or downstream read invalidates the trial without fallback.
Actual transformed requests, fresh responses, digests, seeds and timings are saved.
Playback remains a recording reader and cannot establish intervention effects.

Commands: .venv/Scripts/python.exe -m rewind_replay.cli setup; same module probe;
pytest tests/test_replay.py --junitxml=artifacts/p3/pytest.xml (4/4 passed);
python scripts/rewind.py check (see artifacts/p3/check-repaired.log).
Final full check: 36/36 tests in 97.84 seconds, lint/format/schema checks,
TypeScript/Vite build and dependency manifest passed. New browser screenshots
were not run after the P3 metadata-only shell change; P2 renders remain the last
inspected UI evidence. P6 still requires the full rendered evidence journey.
Thirteen actual container probes passed: non-root, DNS/TCP blocked, no host mount,
credentials, evaluator or Docker socket, read-only source, dropped capabilities,
no-new-privileges and enforced CPU/memory/PID bounds. Host-secret result establishes
absence of declared host mounts; it is not a general kernel security certification.
Traversal and unknown tool/state/schema reads fail closed. Actual batch results:
artifacts/p3/interventions.json; probe: artifacts/p3/isolation-probe.json.
Image identity and build timestamp are pinned locally in data/replay-runtime.json.
No source or secret host bind mounts; all sends terminate in private mock outboxes.

Failed experiment: initial image build used an incorrect root parent; corrected
the path before a successful build. Strict downstream fallback was found in review
and removed before gate completion. No external replay effects were performed.
The first full check failed a proxy lifetime test: its six-second process deadline
included Windows import startup as well as the one-second relay timer. Independent
reproduction passed (artifacts/p3/proxy-followup.xml). The test deadline is now
bounded at fifteen seconds including startup; production relay limits are unchanged.
The failure log is preserved at artifacts/p3/check.log.

Real-model gate BLOCKED: user confirms no local model/runtime; no hosted provider
or authorised budget. No real-model request/trial is claimed. To unblock, choose
a licensed CPU-compatible local runtime/model and implement/test its fresh adapter
inside isolation; alternatively implement the narrowly constrained inference IPC
broker and explicitly authorised provider budget. No service has been purchased.
Deterministic fixture repeats show identical outcomes, not provider determinism.

Interview explanation: We start every trial from the captured world and change
only specified input occurrences before a fresh simulator decision. The worker
runs non-root with no network, no host secrets and explicit resource limits.
Versioned mocks can answer owned-world reads; strict replay instead requires
exact schema, arguments, occurrence and state matches. An unmatched branch stops
the trial. Harm attempts and useful work are separate. These are simulator
experiments; playback and signatures cannot turn them into real-model evidence.
Questions: Why can an unknown read not count as harm absent? Why is a subprocess
insufficient to prove replay isolation?

User requested stopping after context compaction. No P4 implementation started.
Next: prompts/04-INVESTIGATION.md; durable experiment jobs and fixed-plan statistics.
