"""Synthetic 5m tape for the tests (no market data): random walk with trending stretches, a few missing bars, funding."""
import numpy as np

from context_asof import DAY, HOUR, MIN5

T0 = 1_640_995_200_000   # 2022-01-01 00:00 UTC (a Saturday, like the real DEV start)


def tape(days=130, seed=7, gaps=True):
    rng = np.random.default_rng(seed)
    n = days * 288
    drift = np.repeat(rng.choice([-1.0, 0.0, 0.0, 1.0], size=n // 576 + 1), 576)[:n] * 1e-4
    r = drift + rng.standard_normal(n) * 1.5e-3
    c = 30_000 * np.exp(np.cumsum(r))
    o = np.r_[30_000.0, c[:-1]]
    wick = np.abs(rng.standard_normal((2, n))) * 1e-3 * c
    h = np.maximum(o, c) + wick[0]
    l = np.minimum(o, c) - wick[1]
    v = rng.gamma(2.0, 50.0, n)
    ot = T0 + np.arange(n, dtype=np.int64) * MIN5
    keep = np.ones(n, bool)
    if gaps:
        for g in rng.choice(np.arange(3000, n - 3000), size=6, replace=False):
            keep[g:g + rng.integers(1, 30)] = False
    o, h, l, c, v, ot = (np.round(x[keep], 1) if x is not ot else x[keep] for x in (o, h, l, c, v, ot))
    v = np.maximum(v, 0.1)
    h = np.maximum.reduce([h, o, c]); l = np.minimum.reduce([l, o, c])
    ft = T0 + 6 + np.arange(days * 3, dtype=np.int64) * 8 * HOUR
    fr = rng.choice([0.0001, 0.0001, 0.00005, -0.00002, 0.0003], size=len(ft))
    return {"ot": ot, "o": o, "h": h, "l": l, "c": c, "v": v, "fund_t": ft, "fund_r": fr}


def hour_ts(bars, start_day, every=1):
    """Decision times (whole hours whose closing 5m bar exists) from start_day on."""
    ot = bars["ot"]
    ends = ot + MIN5
    m = (ends % HOUR == 0) & (ends >= T0 + start_day * DAY)
    return ends[m][::every]
