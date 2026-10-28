"""Backtest statistics: summaries, stationary bootstrap, equity / drawdown / Sharpe, period splits, PBO (CSCV)."""
import itertools
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from instruments import DAY_MS, ms_to_ymd  # noqa: E402

WEEK_MS = 7 * DAY_MS
# periods by (entry) date, inclusive bounds as 'YYYY-MM-DD'; None = open end
PERIODS = [("IS", None, "2024-08-31"), ("OOS1", "2024-09-01", "2025-04-30"), ("OOS2", "2025-05-01", None)]
SKIP_REASONS = ("no_instrument", "no_fill", "filter", "no_settlement", "no_hedge_data")
_NAN = float("nan")


def period_of(ts_ms):
    d = ms_to_ymd(ts_ms)
    for name, lo, hi in PERIODS:
        if (lo is None or d >= lo) and (hi is None or d <= hi):
            return name
    return None


def split_by_period(trades, key="entry_ts"):
    out = {name: [] for name, _, _ in PERIODS}
    for t in trades:
        p = period_of(t[key])
        if p is not None:
            out[p].append(t)
    return out


def split_by_year(trades, key="entry_ts"):
    out = {}
    for t in trades:
        out.setdefault(int(ms_to_ymd(t[key])[:4]), []).append(t)
    return dict(sorted(out.items()))


def stationary_bootstrap_ci(x, block_len=5, n_boot=2000, seed=12345, alpha=0.05):
    """Politis-Romano stationary bootstrap (geometric blocks, mean length block_len) 95 % CI of the mean."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    if n == 0:
        return (_NAN, _NAN)
    if n == 1:
        return (float(x[0]), float(x[0]))
    rng = np.random.default_rng(seed)
    p = 1.0 / float(block_len)
    new = rng.random((n_boot, n)) < p
    new[:, 0] = True
    starts = rng.integers(0, n, size=(n_boot, n))
    j = np.arange(n)
    pos = np.where(new, j, 0)
    bs_ = np.maximum.accumulate(pos, axis=1)
    st = np.take_along_axis(starts, bs_, axis=1)
    idx = (st + j - bs_) % n
    means = x[idx].mean(axis=1)
    lo, hi = np.quantile(means, [alpha / 2.0, 1.0 - alpha / 2.0])
    return (float(lo), float(hi))


def summarize(trades, skipped=None, *, block_len=5, n_boot=2000, seed=12345):
    pnl = np.asarray([t["pnl_btc"] for t in trades], dtype=np.float64)
    n = int(pnl.size)
    by_reason = {}
    for s in (skipped or []):
        by_reason[s["reason"]] = by_reason.get(s["reason"], 0) + 1
    out = {"n": n, "n_skipped": int(sum(by_reason.values())), "n_skipped_by_reason": by_reason}
    if n == 0:
        out.update(win_rate=_NAN, mean_pnl_btc=_NAN, median_pnl_btc=_NAN, worst_pnl_btc=_NAN, best_pnl_btc=_NAN,
                   total_pnl_btc=0.0, t_stat=_NAN, boot_ci_lo=_NAN, boot_ci_hi=_NAN)
    else:
        mean = float(pnl.mean())
        sd = float(pnl.std(ddof=1)) if n > 1 else _NAN
        t = mean / (sd / math.sqrt(n)) if (n > 1 and sd > 0.0) else _NAN
        lo, hi = stationary_bootstrap_ci(pnl, block_len, n_boot, seed)
        out.update(win_rate=float((pnl > 0).mean()), mean_pnl_btc=mean, median_pnl_btc=float(np.median(pnl)),
                   worst_pnl_btc=float(pnl.min()), best_pnl_btc=float(pnl.max()), total_pnl_btc=float(pnl.sum()),
                   t_stat=float(t), boot_ci_lo=lo, boot_ci_hi=hi)
    out.update(mean=out["mean_pnl_btc"], median=out["median_pnl_btc"], worst=out["worst_pnl_btc"],
               best=out["best_pnl_btc"], total=out["total_pnl_btc"])
    return out


def max_drawdown_pct(equity):
    """Largest peak-to-trough decline of an equity path, in percent (positive number; 12.5 = -12.5 %)."""
    e = np.asarray(equity, dtype=np.float64)
    if e.size == 0:
        return 0.0
    peak = np.maximum.accumulate(e)
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = np.where(peak > 0, (peak - e) / peak, 0.0)
    return float(dd.max() * 100.0)


def weekly_pnl(trades, key="exit_ts"):
    """pnl_btc aggregated per week (weeks since 1970-01-05 Monday), zero-filled between first and last week."""
    if not trades:
        return np.zeros(0)
    monday0 = 4 * DAY_MS  # 1970-01-05 is a Monday
    wk = np.asarray([(t[key] - monday0) // WEEK_MS for t in trades], dtype=np.int64)
    pnl = np.asarray([t["pnl_btc"] for t in trades], dtype=np.float64)
    lo, hi = int(wk.min()), int(wk.max())
    out = np.zeros(hi - lo + 1)
    np.add.at(out, wk - lo, pnl)
    return out


def sharpe_weekly(trades):
    """mean/std(ddof=1) of weekly aggregated pnl_btc * sqrt(52); rf = 0; nan when < 2 weeks or zero variance."""
    w = weekly_pnl(trades)
    if w.size < 2:
        return _NAN
    sd = w.std(ddof=1)
    if not sd > 0.0:
        return _NAN
    return float(w.mean() / sd * math.sqrt(52.0))


def equity_btc(trades):
    """Sequential (additive) equity in BTC starting from 1 BTC, trades ordered by exit_ts.
    Returns dict: exit_ts, equity (after each trade), final_equity_btc, max_drawdown_pct (incl. the starting 1.0),
    sharpe_weekly, spot (spot_exit at each exit), equity_usd = equity * spot, hodl_usd = spot (1 BTC held),
    usd_ratio_vs_hodl = equity_usd / spot, max_drawdown_usd_pct, hodl_max_drawdown_pct."""
    ts = sorted(trades, key=lambda t: (t["exit_ts"], t.get("entry_ts", 0)))
    pnl = np.asarray([t["pnl_btc"] for t in ts], dtype=np.float64)
    eq = 1.0 + np.cumsum(pnl)
    spot = np.asarray([t.get("spot_exit", _NAN) for t in ts], dtype=np.float64)
    eq_usd = eq * spot
    path = np.concatenate([[1.0], eq]) if eq.size else np.asarray([1.0])
    return {
        "exit_ts": [t["exit_ts"] for t in ts],
        "equity": [float(x) for x in eq],
        "final_equity_btc": float(eq[-1]) if eq.size else 1.0,
        "max_drawdown_pct": max_drawdown_pct(path),
        "sharpe_weekly": sharpe_weekly(ts),
        "spot": [float(x) for x in spot],
        "equity_usd": [float(x) for x in eq_usd],
        "hodl_usd": [float(x) for x in spot],
        "usd_ratio_vs_hodl": [float(x) for x in eq],
        "max_drawdown_usd_pct": max_drawdown_pct(eq_usd) if eq.size else 0.0,
        "hodl_max_drawdown_pct": max_drawdown_pct(spot) if eq.size else 0.0,
    }


def es_mean_worst(returns, frac=0.05):
    """Mean of the worst `frac` of returns (ES5 for frac=0.05): k = max(1, ceil(frac*n)) lowest values."""
    r = np.sort(np.asarray(returns, dtype=np.float64))
    if r.size == 0:
        return _NAN
    k = max(1, int(math.ceil(frac * r.size - 1e-12)))
    return float(r[:k].mean())


def overlay_metrics(equity_usd, hodl_usd):
    """Daily-USD comparison of an overlay account vs holding 1 BTC. Inputs are aligned daily series."""
    e = np.asarray(equity_usd, dtype=np.float64)
    h = np.asarray(hodl_usd, dtype=np.float64)
    out = {"n_days": int(e.size)}
    if e.size < 2:
        out.update(maxdd_overlay_pct=_NAN, maxdd_hodl_pct=_NAN, es5_overlay=_NAN, es5_hodl=_NAN,
                   final_ratio_vs_hodl=_NAN)
        return out
    re_ = e[1:] / e[:-1] - 1.0
    rh = h[1:] / h[:-1] - 1.0
    out.update(maxdd_overlay_pct=max_drawdown_pct(e), maxdd_hodl_pct=max_drawdown_pct(h),
               es5_overlay=es_mean_worst(re_), es5_hodl=es_mean_worst(rh),
               final_ratio_vs_hodl=float((e[-1] / e[0]) / (h[-1] / h[0])))
    return out


def pbo_cscv(matrix, n_slices=8):
    """Probability of Backtest Overfitting by combinatorially symmetric cross-validation (Bailey, Borwein,
    Lopez de Prado, Zhu). matrix: configs x periods (higher = better; entries are per-period performance, e.g.
    pnl per month). Columns are cut into n_slices contiguous slices; for every choice of n_slices/2 slices as
    in-sample (IS) the config with the best IS performance (mean over the IS columns) is ranked on the
    complementary OOS slices (mid-rank, omega = rank/(N+1)); PBO = share of splits with logit(omega) <= 0."""
    m = np.asarray(matrix, dtype=np.float64)
    if m.ndim != 2:
        raise ValueError("matrix must be 2-D (configs x periods)")
    n_cfg, n_per = m.shape
    if n_slices < 2 or n_slices % 2:
        raise ValueError("n_slices must be an even integer >= 2")
    if n_per < n_slices:
        raise ValueError("need at least n_slices columns (got %d < %d)" % (n_per, n_slices))
    if n_cfg < 2:
        return _NAN
    groups = np.array_split(np.arange(n_per), n_slices)
    n_le = 0
    n_tot = 0
    for is_idx in itertools.combinations(range(n_slices), n_slices // 2):
        oos_idx = [g for g in range(n_slices) if g not in is_idx]
        cols_is = np.concatenate([groups[g] for g in is_idx])
        cols_oos = np.concatenate([groups[g] for g in oos_idx])
        perf_is = m[:, cols_is].mean(axis=1)
        perf_oos = m[:, cols_oos].mean(axis=1)
        best = int(np.argmax(perf_is))
        v = perf_oos[best]
        rank = 1.0 + float((perf_oos < v).sum()) + 0.5 * float((perf_oos == v).sum() - 1)
        omega = rank / (n_cfg + 1.0)
        logit = math.log(omega / (1.0 - omega))
        n_tot += 1
        if logit <= 0.0:
            n_le += 1
    return n_le / n_tot
