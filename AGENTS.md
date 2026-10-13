# REWIND — repository instructions for coding assistants

These instructions govern implementation work in this repository. Respect higher-priority platform instructions and explicit user directions. Merge with relevant existing repository guidance rather than deleting it.

## Purpose

Implement the accepted REWIND vision: recorder + Forensics + Ledger + Sentinel + Preflight. Improve engineering detail without replacing the product concept.

The supplied dossier is retained in docs/reference/. Its original implementation prompt and unsupported claims are superseded by docs/implementation/02-DOSSIER-CORRECTIONS.md and 03-ARCHITECTURE.md for this build.

## At the start of every session

1. Read this file.
2. Read docs/project/STATE.md and HANDOFF.md.
3. Inspect git status, repository layout and actual available commands.
4. Read the active task in TASKS.md, relevant DECISIONS.md entries and the current phase prompt.
5. Verify that state documentation matches the files and last test evidence; repair stale summaries.
6. State the concrete slice you will implement and its acceptance condition.

Do not load every historical log into context unnecessarily. Follow links/IDs to the relevant decision, experiment or bug. Do not assume another chat's memory contains repository truth.

## Build behaviour

- Execute the requested phase; do not only describe a plan.
- Prefer a small complete code path over disconnected scaffolding.
- Keep the accepted scope; put larger ideas in the backlog.
- Use typed interfaces, migrations, explicit error states and bounded resource use.
- Read official documentation for version-sensitive integrations.
- Inspect third-party component code/licensing before incorporating it.
- Keep credentials out of source, browser bundles and logs.
- No fabricated data presented as live measurements.
- No hard-coded scenario labels in the ranking or verdict path.
- No cached model responses used as evidence of changed-input re-execution.
- No external tool side effects from replay or Preflight.
- No unapproved public deployment, outbound message or paid provisioning as an incidental build step.
- Do not discard user changes or reset the repository to hide a failed experiment.
- Core must work without a GPU and without paid services in clearly labelled simulator/playback modes.

## Truth and experimental invariants

Maintain separate run mode, evidence status and feature maturity.
A model can make subject-agent decisions, propose rankings and phrase checked facts.
Code computes outcomes, rates, intervals, policy decisions and integrity verification.
No LLM may invent numeric evidence, declare legal fault, or certify compliance.

A causal report is conditional experimental evidence. Unsupported replay, invalid trials, partial capture, task failure and uncertainty remain visible. Regressions run the original attack against the changed defence.

Use the protocol revision and statistics design documented in the repository. Do not switch methods or dependency versions silently.

## Documentation alongside code — required definition of done

After every meaningful slice, update:
- STATE.md: current phase, working capabilities, mode availability, commands, next action.
- TASKS.md: gate status with evidence.
- SESSION-LOG.md: append date, goal, modifications, commands, outcomes and next step.
- HANDOFF.md: smallest sufficient restart context.

When relevant, also update:
- DECISIONS.md for nontrivial alternatives/trade-offs.
- EXPERIMENTS.md for a measured result or failed experiment.
- BUGS-AND-RISKS.md for newly found or resolved issues.
- INTERVIEW-NOTES.md for what was actually implemented and learned.
- COMPONENT-SOURCES.md for imported UI/code.
- Implementation docs if contracts change.

Do not write “passed” for tests you did not run. Use not_run plus the reason. Do not write “we tried” without an actual experiment. Planned / implemented / verified / blocked are distinct.

Keep STATE.md concise, ideally under 150 lines. Append historical logs; do not rewrite previous entries to make the project look more successful. Archive oversized histories under docs/project/archive/ with a linked index. Preserve experiment and decision IDs.

## Decision record format

ADR-NNN: question; status; context; options; chosen approach; why; trade-offs; evidence; revisit trigger; affected files. Initial ADRs are proposed until implementation verifies them.

## End of phase response

Report:
1. What now works, in plain language.
2. What changed and why.
3. Commands run and actual outcomes.
4. Remaining limitations/blockers.
5. Exact docs updated and next phase.
6. One 60-second interview explanation and two comprehension questions.

Do not claim total completion while a gate is failed or unsupported. If a blocker affects only one mode, continue authorised independent work and mark that mode accurately. Stop optional testing once the relevant risk is resolved.

## Verification and review

Test the risky mechanism, not implementation trivia. Review replay isolation, trial validity, approval binding, SSE durability, signature trust and original-attack regressions.

Inspect rendered UI at the specified viewports; a successful build alone is insufficient. Keep screenshots and test artifacts referenced by path and revision. Never place synthetic presentation results into live runtime code.

## Change boundaries

Small improvements that strengthen evidence, reliability, current protocol compatibility, accessibility or clarity are permitted and should be recorded. Replacing REWIND's accepted idea, adding a major product, or introducing costly infrastructure requires user direction.

