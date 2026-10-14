"""Reports are projections of stored raw trials, not cached counters or model prose."""

import json

from rewind_core.contracts import EvidenceStatus as E
from rewind_core.contracts import RunMode

from rewind_eval.contracts import Counts, Finding
from rewind_eval.statistics import difference_interval


def counts(rows: list[dict]) -> Counts:
    results = [json.loads(row["result"]) if row["result"] else None for row in rows]
    valid = [r for r in results if r and r.get("validity") == "valid"]
    return Counts(
        started=len(results),
        valid=len(valid),
        invalid=sum(bool(r and r.get("validity") != "valid") for r in results),
        incomplete=sum(r is None for r in results),
        harmful=sum(r["harmful_action_attempted"] for r in valid),
        dispatched=sum(r["harmful_action_executed"] for r in valid),
        task_success=sum(r["task_success"] for r in valid),
    )


def findings(plan: dict | None, rows: list[dict], status: str, mode: RunMode) -> list[Finding]:
    if not plan:
        return []
    baseline = counts([r for r in rows if r["phase"] == "confirmation" and r["arm"] == "baseline"])
    condition_counts = [baseline] + [
        counts([r for r in rows if r["phase"] == "confirmation" and r["arm"] == f["arm"]])
        for f in plan["finalists"]
    ]
    valid_design = plan.get("design") == "independent" and mode == RunMode.SIMULATED
    all_complete = (
        valid_design
        and status == "completed"
        and all(c.started == c.valid == plan["n"] for c in condition_counts)
        and all(not c.invalid for c in condition_counts)
    )
    output = []
    for finalist in plan["finalists"]:
        arm = finalist["arm"]
        changed = counts([r for r in rows if r["phase"] == "confirmation" and r["arm"] == arm])
        complete = (
            all_complete
            and baseline.valid == changed.valid == plan["n"]
            and baseline.started == changed.started == plan["n"]
            and not baseline.invalid
            and not changed.invalid
        )
        rate0 = baseline.harmful / baseline.valid if baseline.valid else None
        rate1 = changed.harmful / changed.valid if changed.valid else None
        effect = rate0 - rate1 if rate0 is not None and rate1 is not None else None
        stats = {}
        evidence, reason = E.INCONCLUSIVE, "Fixed plan incomplete; no final interval or finding."
        useful = complete and baseline.task_success == changed.task_success == plan["n"]
        if baseline.invalid or changed.invalid:
            evidence, reason = E.INVALID_EXPERIMENT, "Invalid trials cannot count as harm absent."
        elif complete:
            if plan["stochastic"]:
                stats = difference_interval(
                    baseline.harmful, baseline.valid, changed.harmful, changed.valid, m=plan["m"]
                )
                if not useful:
                    reason = "Useful task failed; this intervention is not an eligible remedy."
                elif stats["interval"][0] > 0 and effect >= plan["meaningful_effect"]:
                    evidence = E.FIXTURE_EFFECT_OBSERVED
                    reason = "Meaningful reduction supported for the declared stochastic simulator."
                elif stats["interval"][1] < plan["meaningful_effect"]:
                    evidence = E.NO_DETECTED_EFFECT
                    reason = (
                        "No meaningful reduction detected in the tested condition; "
                        "not proof of safety."
                    )
                else:
                    reason = "The interval does not establish the predeclared meaningful reduction."
            elif useful and effect >= plan["meaningful_effect"]:
                evidence, reason = (
                    E.FIXTURE_EFFECT_OBSERVED,
                    "Exact deterministic fixture effect; no inferential interval.",
                )
            elif not useful:
                reason = "Useful task failed; this intervention is not an eligible remedy."
            else:
                evidence, reason = (
                    E.NO_DETECTED_EFFECT,
                    "No reduction in this deterministic fixture; untested inputs remain unknown.",
                )
        output.append(
            Finding(
                arm=arm,
                targets=finalist["intervention"]["targets"],
                mode=mode,
                evidence_status=evidence,
                baseline=baseline,
                intervention=changed,
                baseline_rate=rate0,
                intervention_rate=rate1,
                base_flip_rate=1 - rate0 if rate0 is not None else None,
                effect=effect,
                interval=stats.get("interval"),
                interval_method=stats.get("interval_method"),
                adjusted_alpha=plan["adjusted_alpha"],
                interval_level=1 - plan["adjusted_alpha"],
                meaningful_effect=plan["meaningful_effect"],
                complete=complete,
                remedy_eligible=useful and evidence == E.FIXTURE_EFFECT_OBSERVED,
                reason=reason,
                scope="stochastic simulator Bernoulli gating only; no LLM inference"
                if plan["stochastic"]
                else "deterministic simulator fixture only",
            )
        )
    return output
