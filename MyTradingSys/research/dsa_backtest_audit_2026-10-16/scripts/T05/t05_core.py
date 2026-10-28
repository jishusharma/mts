"""T05 placebo machinery. Pure numpy, no market data. Index = 1m bar index from 2022-01-01 00:00 UTC (a Saturday).

An arm = events (decision 1m index t, side), hold h minutes, entry at open t+1+d. Per-event result (side-signed, in %):
    g = side * raw[t] - fund[t]      raw[t] = (O[t+1+d+h] / O[t+1+d] - 1) * 100       (the studies' own return function)
Placebo set = same number of events, each redrawn from the bars with the same weekday and 15-minute slot-of-day as the
real event, then redrawn again while two same-side events lie within the cooldown (the studies' cooldown rule).
"""
import numpy as np

TS0 = 1640995200000          # 2022-01-01 00:00 UTC in ms
MS = 60_000
DAYMIN = 1440
WEEKMIN = 10080
PER8H = 8 * 3600 * 1000
FUND_PCT = 0.01              # the studies' flat 1 bp per 00/08/16 UTC settlement crossed
C_PCT = 0.14                 # the studies' round-trip cost
WD0 = 5                      # 2022-01-01 is a Saturday (Monday = 0)
NDAYS = 912


def key_of(t):
    """weekday * 96 + 15-minute slot of the UTC day, for 1m indices t."""
    t = np.asarray(t, np.int64)
    return ((t // DAYMIN + WD0) % 7) * 96 + (t % DAYMIN) // 15


def raw_table(O, h, d):
    """raw[t] in %, NaN where the entry or exit bar is outside the tape or missing."""
    O = np.asarray(O, float)
    n = len(O)
    t = np.arange(n)
    e, x = t + 1 + d, t + 1 + d + h
    ok = (e >= 0) & (x < n)
    pin = np.where(ok, O[np.clip(e, 0, n - 1)], np.nan)
    pout = np.where(ok, O[np.clip(x, 0, n - 1)], np.nan)
    return (pout / pin - 1.0) * 100.0


def fund_table(n, h, d, ts0=TS0):
    t = np.arange(n, dtype=np.int64)
    e, x = t + 1 + d, t + 1 + d + h
    return FUND_PCT * ((ts0 + x * MS) // PER8H - (ts0 + e * MS) // PER8H)


class Pools:
    """Candidate decision bars grouped by (weekday, 15-min slot): CSR layout."""

    def __init__(self, valid):
        valid = np.asarray(valid, np.int64)
        k = key_of(valid)
        o = np.argsort(k, kind="stable")
        self.sorted_idx = valid[o]
        self.count = np.bincount(k, minlength=7 * 96)
        self.start = np.concatenate(([0], np.cumsum(self.count)[:-1]))


class Draw:
    def __init__(self, idx, conflict_share):
        self.idx, self.conflict_share = idx, conflict_share


def _conflicts(idx, side, cd, mode):
    """Boolean (B, n): True for the later event of a same-side pair that violates the cooldown."""
    B, n = idx.shape
    sb = (np.asarray(side) > 0).astype(np.int64)[None, :]
    if mode == "day":                      # at most one event per (side, UTC day)
        key = sb * 10 ** 7 + idx // DAYMIN
        lim = 0
    else:                                  # gap: next same-side event more than cd bars after the kept one
        key = sb * 10 ** 12 + idx
        lim = cd
    o = np.argsort(key, axis=1, kind="stable")
    ks = np.take_along_axis(key, o, axis=1)
    bad_sorted = np.zeros((B, n), bool)
    bad_sorted[:, 1:] = (ks[:, 1:] - ks[:, :-1]) <= lim
    out = np.zeros((B, n), bool)
    np.put_along_axis(out, o, bad_sorted, axis=1)
    return out


def draw_placebo(rng, t_real, side, pool, n_sets=1000, cd=60, mode="gap", max_rounds=200):
    t_real, side = np.asarray(t_real, np.int64), np.asarray(side)
    n = len(t_real)
    k = key_of(t_real)
    cnt = np.maximum(pool.count[k], 1)[None, :]
    st = pool.start[k][None, :]

    def pick(shape):
        u = rng.random(shape)
        pos = st + np.minimum((u * cnt).astype(np.int64), cnt - 1)
        return pool.sorted_idx[np.clip(pos, 0, len(pool.sorted_idx) - 1)]

    idx = pick((n_sets, n))
    rows = np.arange(n_sets)
    for _ in range(max_rounds):
        bad = _conflicts(idx[rows], side, cd, mode)
        has = bad.any(1)
        if not has.any():
            break
        rows = rows[has]
        sub = idx[rows]
        idx[rows] = np.where(bad[has], pick(sub.shape), sub)
    bad = _conflicts(idx, side, cd, mode)
    return Draw(idx, float(bad.mean()))


def set_stats(raw, fund, idx, side, d):
    """Mean and day-clustered SE (the studies' cm_se) of g for each row of idx (B, n)."""
    idx = np.asarray(idx, np.int64)
    B, n = idx.shape
    g = np.asarray(side, float)[None, :] * raw[idx] - fund[idx]
    m = g.mean(1)
    day = (idx + 1 + d) // DAYMIN
    flat = (np.arange(B)[:, None] * (NDAYS + 2) + np.clip(day, 0, NDAYS + 1)).ravel()
    s = np.bincount(flat, weights=(g - m[:, None]).ravel(), minlength=B * (NDAYS + 2)).reshape(B, NDAYS + 2)
    return m, np.sqrt((s ** 2).sum(1)) / n


def empirical_p(real, placebo):
    """One-sided upper-tail rank: (1 + #placebo >= real) / (1 + B)."""
    placebo = np.asarray(placebo)
    return float((1 + (placebo >= real).sum()) / (1 + len(placebo)))


def overlap(entry, h):
    """(share of events whose hold [e, e+h] overlaps another event's hold, number of connected hold groups)."""
    e = np.sort(np.asarray(entry, np.int64))
    n = len(e)
    if n == 0:
        return float("nan"), 0
    ends = e + h
    ov = np.zeros(n, bool)
    ov[1:] |= e[1:] <= ends[:-1]
    ov[:-1] |= e[1:] <= ends[:-1]
    reach = np.maximum.accumulate(ends)
    comps = 1 + int((e[1:] > reach[:-1]).sum())
    return float(ov.mean()), comps


def week_bootstrap_sd(g, entry, n_boot, rng):
    """SD of the mean of g under a week-block bootstrap (weeks resampled with replacement)."""
    g, entry = np.asarray(g, float), np.asarray(entry, np.int64)
    w = entry // WEEKMIN
    uw, inv = np.unique(w, return_inverse=True)
    s = np.bincount(inv, weights=g)
    c = np.bincount(inv).astype(float)
    pick = rng.integers(0, len(uw), (n_boot, len(uw)))
    means = s[pick].sum(1) / c[pick].sum(1)
    return float(means.std(ddof=1))


def half_year_table(g, entry):
    """dict label -> (n, mean g) by DEV half-year of the entry bar."""
    day = np.asarray(entry, np.int64) // DAYMIN
    dates = np.datetime64("2022-01-01") + day.astype("timedelta64[D]")
    y = dates.astype("datetime64[Y]").astype(int) + 1970
    mth = dates.astype("datetime64[M]").astype(int) % 12
    lab = np.array([f"{a}H{1 if b < 6 else 2}" for a, b in zip(y, mth)])
    g = np.asarray(g, float)
    return {k: (int((lab == k).sum()), float(g[lab == k].mean())) for k in sorted(set(lab))}


def best_of_n_bar(pool_t, n_trials, rng, n_sim=20000, q=0.95):
    """q-quantile of the max of n_trials iid draws from the pooled placebo t-statistics (independence assumption)."""
    pool_t = np.asarray(pool_t, float)
    mx = rng.choice(pool_t, (n_sim, int(n_trials))).max(1)
    return float(np.quantile(mx, q))
