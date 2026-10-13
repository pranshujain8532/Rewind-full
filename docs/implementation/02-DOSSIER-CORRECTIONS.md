# 02 — Corrections before implementation

The original dossier is the product vision. This document changes implementation assumptions that would otherwise produce misleading results or a brittle demo. It is not evidence that any experiment has already been performed.

## Required corrections

| Dossier assumption | Problem | Implementation decision |
|---|---|---|
| An MCP proxy captures everything needed for causal replay | It sees proxied tool/resource traffic, not all prompts, memory, model requests or direct API calls | Add a model/agent adapter; expose capture coverage per session |
| Cached model replies support ablation | Reusing the original reply after changing its input prevents a real counterfactual | Separate PLAYBACK, SIMULATED and real REEXECUTION modes |
| Replay is deterministic for hosted LLMs | Seeds, temperature and model names do not guarantee identical behaviour | Pin what is available; measure fresh-run variability; store provider identity and limitations |
| Offline fixture repetition gives an LLM confidence interval | Repeating the same recording adds no independent evidence | No inferential interval for fixed playback; label simulator statistics as simulator-only |
| Lookup by tool name and argument hash is enough | Identical calls can occur at different states; altered inputs can create unseen calls | Include occurrence and environment state; return unsupported for unknown strict-replay calls |
| Delete PII at capture and still replay exact original context | Lost content cannot be reconstructed; redaction may change model behaviour | Exact synthetic traces for MVP; distinguish exact encrypted capture, redacted-only and unavailable replay coverage |
| Bisection always finds the cause in logarithmic time | Multiple, redundant and interacting inputs break monotonicity | Start with bounded single removals plus pair/group checks; log incomplete search |
| One failed ablation rules a candidate out | Weak or interacting influence can remain | Use “no detected effect under this test”; preserve untested / inconclusive states |
| Wilson interval alone covers the effect difference | A one-proportion interval is not a difference-of-proportions interval | Use a specified two-independent-proportion method for the effect |
| Repeatedly look at a 95% CI and stop when positive | Optional stopping invalidates the intended fixed-sample interpretation | Freeze sample size before confirmation; use a future reviewed sequential method only if justified |
| Arbitrary Shapley + SPRT handles all interactions | Coalition design, stochastic outcomes and hypotheses need explicit definitions | Defer both; bounded factorial cases first |
| Conformal calibration guarantees deployment FPR | Guarantees require assumptions, including exchangeability; step-level and run-level error differ | Start with measured empirical FPR; calibrate run-level scores on separate data |
| Goal drift and surprise are independent | They may be correlated | Evaluate combined decision rules; do not multiply their false-positive rates |
| Rules cannot capture context | Rules and simple sequence models can capture useful context | Rules first, then n-gram/Markov baseline, then transformer only if evaluation warrants |
| A linked hash chain is a Merkle tree | These are different structures | MVP signed hash chain + signed session seal; add a true Merkle tree only with separate proof tests |
| Signatures establish legal blame or non-repudiation automatically | Identity, key custody and record completeness remain assumptions | State tamper-evidence under a trusted key; show role provenance, not legal fault |
| A local seal prevents a privileged operator rewriting history | An attacker with the signing key could replace the chain and seal | External trusted checkpoint is a future strengthening; disclose absence |
| Removing an input creates the regression test | That only tests an artificial input deletion | Regression runs the original attack against the patched agent and checks useful task completion |
| “Nobody does this”, “incidents approach zero”, precise industry numbers | Broad claims are not established by a prototype | Use measured differentiation and cited, current evidence; do not repeat unverified assertions |
| Governance mapping equals conformance certification | A mapping cannot establish all applicable obligations | Label it “evidence mapping”; never a compliance percentage or certificate |
| Original §14 failure stories describe our work | No logs establish that those experiments happened | Treat them as proposed experiments; tell them as history only after reproducing and recording them |
| Full vision fits in 36 hours | Dossier phase estimates already total roughly 40 hours before integration | Use the roadmap's smaller rescue slice or the full 10–14 day schedule |

## The important architecture consequence

There are two integration levels:

1. **Tool recording:** proxy configuration captures traffic on that route.
2. **Replay-capable recording:** the agent adapter captures the full supported model input, tool definitions, state and versions.

A session can support level 1 while failing level 2. The UI must show “recorded, insufficient capture for re-execution” rather than manufacturing missing context.

## The important privacy consequence

The recorder becomes a sensitive system. Redaction is useful but changes evidence. There is no magical configuration that simultaneously stores nothing sensitive, perfectly replays everything, and allows unrestricted inspection.

For the competition use synthetic data. Implement authenticated encryption for private payload storage, a separately redacted display view, and a coverage flag. Do not claim tenant-held keys or zero operator access unless the deployment actually enforces that design.

## The important experiment consequence

Supported wording:

“Removing chunk C reduced the target action rate under environment E, model M and intervention I. The interval and trial counts are shown. Search coverage was limited to these candidates.”

Unsupported wording:

“We proved employee X caused the incident, all other inputs are innocent, and future attacks cannot succeed.”

## Protocol versions need an explicit decision

The current MCP documentation inspected on 9 October 2026 describes changes in revision 2026-07-28, including changes to Streamable HTTP. The original dossier uses older lifecycle assumptions. Select one **SDK-supported protocol revision** in P0; record it and test that revision. Do not combine snippets from different revisions or silently claim broad client compatibility.

Browser SSE for the REWIND dashboard is a separate application API. Its reconnection behaviour is not inherited from the MCP transport specification.

## Clarify the role of the model

The original “no LLM in the causal path” wording is too broad: an LLM must run inside a real LLM behavioural experiment. The intended rule is:

**The subject model makes agent decisions. Deterministic code computes outcomes and statistics. No LLM is allowed to invent measurements or decide the causal verdict from prose.**

A narrative generator may restate validated facts and must cite their record fields. The system remains usable if it is unavailable.

## Scope that survives these corrections

The core remains ambitious: instrumented agent + MCP recorder + safe re-execution + controlled interventions + live investigation interface + policy engine + signed report + regression suite.

This is enough for a technically credible competition demonstration and substantial interview discussion. Advanced ML is an extension, not a substitute for that foundation.

