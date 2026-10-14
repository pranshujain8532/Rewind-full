"""Fixed-plan independent-binomial Newcombe intervals, never paired/playback inference."""


def difference_interval(
    x0: int,
    n0: int,
    x1: int,
    n1: int,
    *,
    m: int = 1,
    design: str = "independent",
    stochastic: bool = True,
) -> dict:
    if design != "independent" or not stochastic:
        raise ValueError("Independent binomial samples required; paired/deterministic refused")
    if any(type(value) is not int for value in (x0, n0, x1, n1, m)):
        raise ValueError("Counts, sample sizes and multiplicity must be integers")
    if n0 <= 0 or n1 <= 0 or not 0 <= x0 <= n0 or not 0 <= x1 <= n1 or not 1 <= m <= 3:
        raise ValueError("Impossible counts or multiplicity")
    # Readiness, capture and schema export do not need the scientific runtime.
    from statsmodels.stats.proportion import confint_proportions_2indep

    alpha = 0.05 / m
    low, high = confint_proportions_2indep(
        x0, n0, x1, n1, compare="diff", method="newcomb", alpha=alpha
    )
    return {
        "baseline_rate": x0 / n0,
        "intervention_rate": x1 / n1,
        "base_flip_rate": 1 - x0 / n0,
        "effect": x0 / n0 - x1 / n1,
        "interval": [float(low), float(high)],
        "adjusted_alpha": alpha,
        "interval_level": 1 - alpha,
        "interval_method": "newcomb_independent",
    }
