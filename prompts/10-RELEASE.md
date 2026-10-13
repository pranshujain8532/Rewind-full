# P10 — Final evaluation, demo and handoff

Prerequisites: chosen scope implemented; any blocked capability documented.

~~~text
Execute P10. This is feature freeze: fix, evaluate and explain; do not add
new product ideas.

Read 06-VERIFICATION.md and 07-DEMO-AND-INTERVIEWS.md. Run the critical
acceptance gates for the chosen delivery track. Fix concrete failures.
Test independent held-out cases and keep ground-truth labels outside the
subject agent and ranking algorithm.

Produce real benchmark manifests and a concise report with counts,
intervals, modes, hardware, versions, trial failures, task success, cost
and limits. A simulator result must not be generalised to real LLMs.
Never substitute example numbers from the dossier.

Run the complete stage story three times from a clean demo reset.
Test the offline fallback, saved evidence verification, tamper rejection,
original-attack regression, browser refresh and worker interruption.
Inspect the final UI screenshots and fix remaining material problems.

Write actual setup, run, test, seed, verify and demo commands in README.
Record PowerShell and WSL/container instructions; distinguish tested
platforms from untested ones. Create an environment/configuration example
with no secrets and explain provider budget configuration.

Finish the feature matrix with:
implemented/verified, simulated, heuristic, trained/evaluated,
blocked and planned. Identify any missing real-model gate explicitly.

Update all living context files. Prepare a four-minute demo script and
interview notes grounded in the implementation, including your real failed
experiments and architectural decisions. Do not invent a success story.

FINAL REPORT:
- what works and how to run it;
- exact acceptance/benchmark results and evidence paths;
- known limitations and blocked capabilities;
- current code revision and dirty-tree status;
- next three sensible improvements;
- a 90-second explanation Pranshu can practise.

The application is ready only within the tested scope. Do not claim
enterprise production readiness or guaranteed competition outcomes.
~~~

