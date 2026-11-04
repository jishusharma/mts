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


# ---------------------------------------------------------------------------------------------------------------------
# Context harness (card context-harness-research-kit, Super Session order d-context-retest-1104): one shared set of
# context tags so no re-run writes another trend tag. Everything is as-of: a tag at time t reads only bars that CLOSED
# at or before t. Times are UTC seconds; a series is (t_close, value) where t_close is when the bar is known.
#
# Reused, loaded by path (research dirs are not packages), not copied:
#   state_asof   backtest/layers/rsi/malkan_mtf.py          latest entry with time <= t (closed-bar alignment)
#   session_of   research/context_factors_pit_2026-10-16/context_asof.py   asia/london/ny/late from minutes
#   ema_np       research/wavetrend_2026-10-17/count_events.py             EMA, seeded with the first value
# The SMA200 side is the same quantity as meta_label_breaks_2026-10-31/meta.py trend_d (close / SMA200 - 1 > 0 on the last
# closed daily bar); features_at itself needs a whole event row, so only its formula is reused, not the call.
#
# malkan_mtf.py decision (DIVERGENCE_RESEARCH_2026-10-09.md:81): its gate takes a 20-bar-window "regime" for weekly and
# monthly, but Malkan's gate is a LEVEL test (MALKAN_RULES_2026-10-31.md:11-16: monthly and weekly RSI >= 60 bull,
# <= 40 bear). WRAPPED, not fixed: malkan_mtf.py is untouched (another Builder owns the Malkan wiring); `rsi_band` below
# is the level test on the last closed weekly/monthly RSI and replaces malkan_regime for this purpose.
#
# Parameter labels:
#   SOURCED (Malkan, MALKAN_RULES_2026-10-31.md:11-16): RSI_BULL = 60, RSI_BEAR = 40, weekly AND monthly must agree.
#   SOURCED-in-repo (meta.py trend_d): daily SMA200 side. EMA200 option follows wavetrend count_events (OURS choice).
#   OURS: the regime = band AND side combination, the tf_break class -> phase mapping, SESSION cutoffs (08/13/21 UTC),
#         retest window N (caller passes it; no default), the retest fill rule (limit at the level, gap fills at the open).
# ---------------------------------------------------------------------------------------------------------------------
import importlib.util as _ilu
from pathlib import Path as _Path

RSI_BULL = 60.0  # SOURCED (Malkan)
RSI_BEAR = 40.0  # SOURCED (Malkan)
MA_N = 200       # SOURCED-in-repo (meta.py trend_d SMA200)
PHASE_OF_CLASS = {"W1": "range", "H": "break", "R": "retest"}  # OURS mapping of tf_break_event_study classes
REGIMES = ("bull", "bear", "range")

_MTS = _Path(__file__).resolve().parents[1]
_REUSED = {}


def _reuse(key, relpath):
    if key not in _REUSED:
        spec = _ilu.spec_from_file_location("rk_reuse_" + key, _MTS / relpath)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _REUSED[key] = mod
    return _REUSED[key]


def _last_closed(series, t):
    """Value of the latest bar with t_close <= t, or None. Reuses malkan_mtf.state_asof."""
    asof = _reuse("mtf", "backtest/layers/rsi/malkan_mtf.py").state_asof
    return asof(list(series[0]), list(series[1]), t)


def rsi_band(weekly_rsi, monthly_rsi):
    """'bull' if both >= 60, 'bear' if both <= 40, else 'mid'; None if either is missing (SOURCED, level test)."""
    if weekly_rsi is None or monthly_rsi is None:
        return None
    if weekly_rsi >= RSI_BULL and monthly_rsi >= RSI_BULL:
        return "bull"
    if weekly_rsi <= RSI_BEAR and monthly_rsi <= RSI_BEAR:
        return "bear"
    return "mid"


def ma_side(closes, n=MA_N, ma="sma"):
    """'above'/'below' the n-bar average at the LAST close given; None when fewer than n closes (or equal to the average)."""
    if len(closes) < n:
        return None
    if ma == "sma":
        avg = float(np.mean(closes[-n:]))
    elif ma == "ema":
        avg = float(_reuse("wt", "research/wavetrend_2026-10-17/count_events.py").ema_np(np.asarray(closes, float), n)[-1])
    else:
        raise ValueError("ma must be 'sma' or 'ema'")
    c = closes[-1]
    return "above" if c > avg else "below" if c < avg else None


def regime_tag(t, daily, weekly_rsi, monthly_rsi, ma="sma", ma_n=MA_N):
    """As-of regime at time t. daily = (t_close list, close list); weekly_rsi / monthly_rsi = (t_close list, rsi list).

    Returns {'side': above|below|None, 'band': bull|bear|mid|None, 'regime': bull|bear|range|None}.
    regime = 'bull' when band is bull and close is above the average, 'bear' when band is bear and close is below,
    'range' otherwise; None when the side or the band is unavailable.
    """
    td, cd = daily
    k = sum(1 for x in td if x <= t)          # daily bars closed by t (td ascending)
    side = ma_side(list(cd[:k]), ma_n, ma)
    band = rsi_band(_last_closed(weekly_rsi, t), _last_closed(monthly_rsi, t))
    if side is None or band is None:
        regime = None
    elif band == "bull" and side == "above":
        regime = "bull"
    elif band == "bear" and side == "below":
        regime = "bear"
    else:
        regime = "range"
    return {"side": side, "band": band, "regime": regime}


def phase_tag(cls):
    """tf_break_event_study class -> phase: W1 (wick sweep) range, H (break held) break, R (reclaimed) retest."""
    try:
        return PHASE_OF_CLASS[cls]
    except KeyError:
        raise ValueError(f"unknown tf_break class {cls!r}; expected one of {sorted(PHASE_OF_CLASS)}") from None


def session_tag(t):
    """asia / london / ny / late for UTC seconds t (cutoffs 08, 13, 21 UTC from context_asof.session_of; OURS)."""
    return _reuse("ctx", "research/context_factors_pit_2026-10-16/context_asof.py").session_of(int(t) // 60)


def retest_entry(bars, i, level, side, n):
    """First pullback to the signal level within n bars AFTER the signal bar i, instead of entering on bar i.

    bars: (o, h, l, c) tuples. side +1 long (pullback = low <= level), -1 short (high >= level). Bar i's own range never
    counts. Resting limit at `level`: fills at the level, or at the open when the bar gaps through it (min(open, level) for
    long, max(open, level) for short). Returns (bar_index, fill_price) or None (no retest: the trade is skipped). Reads
    bars i+1 .. i+n only, and stops at the first touch.
    """
    for j in range(i + 1, min(i + n, len(bars) - 1) + 1):
        o, h, l, _ = bars[j]
        if side > 0 and l <= level:
            return j, float(min(o, level))
        if side < 0 and h >= level:
            return j, float(max(o, level))
    return None


def weekly_regimes(week_starts, daily, weekly_rsi, monthly_rsi, **kw):
    """regime tag (str or None) at each week start time, as-of."""
    return [regime_tag(t, daily, weekly_rsi, monthly_rsi, **kw)["regime"] for t in week_starts]


def regime_mix_line(window):
    """One line for RESULT.md: weeks in the window by regime. window = list of weekly regime tags (None = no data)."""
    for x in window:
        if x is not None and x not in REGIMES:
            raise ValueError(f"unknown regime {x!r}")
    n = len(window)
    if n == 0:
        return "0 weeks: no data"
    cells = [(name, sum(1 for x in window if x == name)) for name in REGIMES] + [("n/a", sum(1 for x in window if x is None))]
    return f"{n} weeks: " + " | ".join(f"{name} {c} ({100 * c / n:.0f}%)" for name, c in cells)
