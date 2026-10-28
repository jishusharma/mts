"""Pure verdict and planning helpers for the context composite V2 MDE rule."""

from math import ceil, isfinite, sqrt

Z_HOLM = 3.241
Z_POWER_80 = 0.8416
PLAUSIBLE_OURS_R = 0.375
SENSITIVITY_R = 0.30
SD_OURS_R = 1.5
MDE_MULTIPLIER_OURS = 2.8


def n_needed(effect_r, *, cost_r=0.066, sd_r=SD_OURS_R, z=Z_HOLM, power_z=Z_POWER_80):
    """Return whole matched days required for 80% power at a net effect.

    ``effect_r`` is gross of the fixed cost in R. Parameters are OURS, matching
    PRE_REG_V2; this is a planning calculation, not a data-derived estimate.
    """
    values = (effect_r, cost_r, sd_r, z, power_z)
    if not all(isfinite(value) for value in values):
        raise ValueError("inputs must be finite")
    if cost_r < 0 or sd_r <= 0 or z < 0 or power_z < 0:
        raise ValueError("cost must be nonnegative; sd positive; z values nonnegative")
    net_effect = effect_r - cost_r
    if net_effect <= 0:
        raise ValueError("effect_r must exceed cost_r")
    return ceil(((z + power_z) * sd_r / net_effect) ** 2)


def verdict(*, mean_e, day_se, week_se, cost_r, t_day, t_week,
            mde_multiplier=MDE_MULTIPLIER_OURS, sensitivity_r=SENSITIVITY_R,
            t_threshold=Z_HOLM):
    """Apply V2 gates: powered nonpositive E can FAIL; PASS requires both t bars.

    Underpowered or otherwise nonpassing cells are INCONCLUSIVE. The realised
    MDE is ``mde_multiplier * day_se`` and must fit within sensitivity less cost.
    """
    values = (mean_e, day_se, week_se, cost_r, t_day, t_week,
              mde_multiplier, sensitivity_r, t_threshold)
    if not all(isfinite(value) for value in values):
        raise ValueError("inputs must be finite")
    if day_se <= 0 or week_se <= 0 or cost_r < 0:
        raise ValueError("standard errors must be positive and cost nonnegative")
    if mde_multiplier <= 0 or sensitivity_r <= 0 or t_threshold < 0:
        raise ValueError("MDE multiplier and sensitivity must be positive; t threshold nonnegative")

    realised_mde_plus_cost = mde_multiplier * day_se + cost_r
    if mean_e <= 0 and realised_mde_plus_cost <= sensitivity_r:
        return "FAIL"
    if mean_e > 0 and abs(t_day) >= t_threshold and abs(t_week) >= t_threshold:
        return "PASS"
    return "INCONCLUSIVE"
