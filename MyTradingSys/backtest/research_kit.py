"""Shared screen statistics for research studies: one tested home instead of one copy per study.

Units: return-like inputs share one unit (% per trade, or R). `cost` is in that unit. `day` is any hashable cluster id
(a UTC day number); observations of one day are not independent, so SEs sum the within-day deviations first.

Conventions fixed here (they were silently different between study copies, see tests/test_research_kit.py):
- Clustered SE of a mean: sqrt(sum_d S_d^2) / n with S_d = sum over day d of (x - mean). No small-sample correction.
  Fewer than 2 observations or fewer than 2 distinct days gives NaN: with one cluster the sandwich is exactly 0, which a
  t-test would turn into t = inf.
- MDE at 80 % power, two-sided 5 %: 2.8 x SE (PRE_REG gross_effect_screen s.4). `MDE_Z_EXACT` is 1.96 + 0.8416 for callers
  that want the unrounded multiplier (backtest/power_mde.py uses it).
- Costs: 0.14 % round trip = taker in + taker out (5 + 5 bp fee + 2 + 2 bp slippage), 0.09 % = maker in (2 bp) + taker out
  (5 + 2 bp). Both SOURCED: gross_effect_screen_2026-10-15/PRE_REG.md s.1 rows "Primary round-trip cost C" and "Secondary
  cost readout C_m".
- Holm step-down over m variants: adj_(k) = max_{j<=k} min(1, (m - j + 1) p_(j)), j ranks from 1 (smallest p).
"""
from math import erf, sqrt

import numpy as np

TAKER_RT_PCT = 0.14
MAKER_IN_RT_PCT = 0.09
MDE_Z = 2.8
MDE_Z_EXACT = 1.959963984540054 + 0.8416212335729143


class PowerRefusal(Exception):
    """The design cannot detect an effect that is plausible after costs; do not freeze it."""


def _groups(day):
    """Integer cluster index per observation and the number of distinct clusters."""
    uniq, inv = np.unique(np.asarray(day), return_inverse=True)
    return inv, len(uniq)


def cluster_mean_se(g, day):
    """Mean and day-clustered SE of the mean. NaN SE when n < 2 or only one distinct day; (nan, nan) when empty."""
    g = np.asarray(g, float)
    n = len(g)
    if n == 0:
        return float("nan"), float("nan")
    m = float(g.mean())
    inv, k = _groups(day)
    if n < 2 or k < 2:
        return m, float("nan")
    s = np.bincount(inv, weights=g - m)
    return m, float(np.sqrt((s ** 2).sum()) / n)


def cluster_diff(ga, day_a, gb, day_b):
    """mean(ga) - mean(gb) and its day-clustered SE when the two groups may share days (same-day covariance counted).

    Per-day influence of the difference is S_a,d / n_a - S_b,d / n_b; SE = sqrt(sum_d of its square). This equals the OLS
    of g on [1, group dummy] with a cluster-robust sandwich and no correction. NaN SE when either group has < 2 items or
    the union has one day.
    """
    ga, gb = np.asarray(ga, float), np.asarray(gb, float)
    na, nb = len(ga), len(gb)
    if na == 0 or nb == 0:
        return float("nan"), float("nan")
    ma, mb = float(ga.mean()), float(gb.mean())
    diff = ma - mb
    if na < 2 or nb < 2:
        return diff, float("nan")
    inv, k = _groups(np.concatenate((np.asarray(day_a), np.asarray(day_b))))
    if k < 2:
        return diff, float("nan")
    s = np.bincount(inv[:na], weights=ga - ma, minlength=k) / na - np.bincount(inv[na:], weights=gb - mb, minlength=k) / nb
    return diff, float(np.sqrt((s ** 2).sum()))


def cluster_diff_independent(ga, day_a, gb, day_b):
    """Difference of two clustered means treated as independent: SE = sqrt(se_a^2 + se_b^2). Right only when the groups
    share no days; with shared days it drops the covariance (use `cluster_diff`)."""
    ma, sa = cluster_mean_se(ga, day_a)
    mb, sb = cluster_mean_se(gb, day_b)
    return ma - mb, float(sqrt(sa ** 2 + sb ** 2))


def t_stat(num, se):
    """num / se; NaN when se is NaN; +-inf for se == 0 with a nonzero numerator; NaN for 0 / 0."""
    if se != se:
        return float("nan")
    if se == 0:
        return float("inf") if num > 0 else (float("-inf") if num < 0 else float("nan"))
    return num / se


def norm_p_two(t):
    """Two-sided normal p-value of a t statistic (the screens use |t| >= 2 on large n)."""
    if t != t:
        return float("nan")
    return 1.0 - erf(abs(t) / sqrt(2.0))


def mde(se, z=MDE_Z):
    """Forward-return minimum detectable effect at 80 % power: z x SE (default 2.8)."""
    return z * se


def power_check(n, sd, plausible_effect, cost=0.0, z=MDE_Z):
    """Count-before-freeze power check. n = independent units (days when clustered), sd = SD of the per-unit return at the
    horizon, plausible_effect = the gross effect worth believing, cost = round-trip cost; all in one unit.

    mde = z * sd / sqrt(n). proceed is False when mde + cost > plausible_effect: even a true effect of that size would not
    clear cost with 80 % power at this n.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if sd < 0:
        raise ValueError("sd must be nonnegative")
    m = z * sd / sqrt(n)
    return {"n": n, "sd": sd, "mde": m, "cost": cost, "needed": m + cost, "plausible": plausible_effect,
            "proceed": m + cost <= plausible_effect}


def require_power(n, sd, plausible_effect, cost=0.0, z=MDE_Z):
    """`power_check` that raises PowerRefusal instead of returning proceed = False."""
    r = power_check(n, sd, plausible_effect, cost, z)
    if not r["proceed"]:
        raise PowerRefusal(f"MDE {r['mde']:.4g} + cost {cost:.4g} = {r['needed']:.4g} > plausible effect {plausible_effect:.4g} "
                           f"(n={n}, sd={sd:.4g}); do not freeze this design")
    return r


def holm(p, m=None):
    """Holm adjusted p-values, returned in input order. `m` = number of variants run (default len(p)); when m > len(p)
    the unlisted variants count as p = 1 and only raise the multipliers."""
    p = np.asarray(p, float)
    k = len(p)
    m = k if m is None else int(m)
    if m < k:
        raise ValueError("m must be at least len(p)")
    order = np.argsort(p, kind="stable")
    out = np.empty(k)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i]))
        out[i] = run
    return out


def holm_reject(p, alpha=0.05, m=None):
    """Boolean array: which hypotheses Holm rejects at family-wise level alpha."""
    return holm(p, m) <= alpha


def cost_in_r(cost_pct, stop_pct):
    """Round-trip cost in R: cost_pct / stop_pct (both in %)."""
    if stop_pct <= 0:
        raise ValueError("stop_pct must be positive")
    return cost_pct / stop_pct


def taker_cost_r(stop_pct):
    return cost_in_r(TAKER_RT_PCT, stop_pct)


def maker_in_cost_r(stop_pct):
    return cost_in_r(MAKER_IN_RT_PCT, stop_pct)
