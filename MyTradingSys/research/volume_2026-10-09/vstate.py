"""V2 state variables (PRE_REG_ADDENDUM_A_2026-10-09.md A2). numpy only. Daily bars + 1h bars (for the US-hours / Asia-hours delta split).
No look-ahead: state at daily bar i uses bars <= i (the full UTC day i); rank uses the previous 250 values only.
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

import vfeat

W2 = 350            # first valid daily bar for V2 events (VT needs 100, rank needs 250)
RANK_WIN = 250
STATE_EVENTS = ["D20_HI", "D20_LO", "VT_HI", "VT_LO", "MOM_HI", "MOM_LO", "DUS_HI", "DUS_LO", "DAS_HI", "DAS_LO",
                "BULLR_D20HI", "BULLR_D20LO", "RANGE_D20HI", "RANGE_D20LO", "BEARR_D20HI", "BEARR_D20LO"]
DIRS2 = {k: (1 if k.endswith("HI") else -1) for k in STATE_EVENTS}
DIRS2.update({"BULLR_D20HI": 1, "BULLR_D20LO": -1, "RANGE_D20HI": 1, "RANGE_D20LO": -1, "BEARR_D20HI": 1, "BEARR_D20LO": -1})
assert len(STATE_EVENTS) == 16


def roll_sum(x, w):
    """sum of x[i-w+1..i] (inclusive of i); NaN before w-1."""
    out = np.full(len(x), np.nan)
    if len(x) >= w:
        out[w - 1:] = swv(x, w).sum(axis=1)
    return out


def exante_rank(x, win=RANK_WIN):
    """PR_i = share of x[i-win..i-1] that are <= x_i; NaN where undefined (i < win or x_i NaN)."""
    n = len(x)
    out = np.full(n, np.nan)
    if n > win:
        prev = swv(x, win)[:-1]                       # row r = x[r..r+win-1] -> bar i = r+win
        with np.errstate(invalid="ignore"):
            out[win:] = (prev <= x[win:, None]).mean(axis=1)
        out[np.isnan(x)] = np.nan
        out[win:][np.isnan(prev).any(axis=1)] = np.nan
    return out


def day_split(h1, d1_t):
    """Per daily bar (aligned to d1_t): sum of dv and v over 1h bars 16-23 UTC (US) and 00-07 UTC (Asia). Days without 24 hourly bars -> NaN."""
    day = h1["t"] // 86400000
    hour = ((h1["t"] % 86400000) // 3600000).astype(int)
    dv = 2 * h1["tbv"] - h1["v"]
    out = {k: np.full(len(d1_t), np.nan) for k in ("dv_us", "v_us", "dv_as", "v_as")}
    pos = {int(d): i for i, d in enumerate(d1_t // 86400000)}
    cnt = {}
    for d, hr, a, b in zip(day, hour, dv, h1["v"]):
        i = pos.get(int(d))
        if i is None:
            continue
        cnt[i] = cnt.get(i, 0) + 1
        if hr >= 16:
            out["dv_us"][i] = np.nansum([out["dv_us"][i], a])
            out["v_us"][i] = np.nansum([out["v_us"][i], b])
        elif hr < 8:
            out["dv_as"][i] = np.nansum([out["dv_as"][i], a])
            out["v_as"][i] = np.nansum([out["v_as"][i], b])
    for i, c in cnt.items():
        if c != 24:
            for k in out:
                out[k][i] = np.nan
    return out


def states(d1, h1):
    c, v, tbv = d1["c"], d1["v"], d1["tbv"]
    n = len(c)
    dv = 2 * tbv - v
    s = {}
    with np.errstate(invalid="ignore", divide="ignore"):
        s["D20"] = roll_sum(dv, 20) / roll_sum(v, 20)
        m20, m100 = roll_sum(v, 20) / 20.0, roll_sum(v, 100) / 100.0
        s["VT"] = np.log(m20 / m100)
        mom = np.full(n, np.nan)
        mom[20:] = np.log(c[20:] / c[:-20])
        s["MOM"] = mom
        sp = day_split(h1, d1["t"])
        s["DUS"] = roll_sum(sp["dv_us"], 20) / roll_sum(sp["v_us"], 20)
        s["DAS"] = roll_sum(sp["dv_as"], 20) / roll_sum(sp["v_as"], 20)
    for k in ("D20", "VT", "MOM", "DUS", "DAS"):
        s["PR_" + k] = exante_rank(s[k])
    s["rsi"] = vfeat.rsi_wilder(c, 14)
    return s


def events2(s, n):
    valid = np.arange(n) >= W2
    e = {}
    with np.errstate(invalid="ignore"):
        for k in ("D20", "VT", "MOM", "DUS", "DAS"):
            pr = s["PR_" + k]
            e[k + "_HI"] = (pr >= 2 / 3) & valid
            e[k + "_LO"] = (pr <= 1 / 3) & valid
        rsi = s["rsi"]
        bull, bear = rsi >= 60, rsi <= 40
        rng = (rsi > 40) & (rsi < 60)
        for nm, reg in (("BULLR", bull), ("RANGE", rng), ("BEARR", bear)):
            e[nm + "_D20HI"] = reg & e["D20_HI"]
            e[nm + "_D20LO"] = reg & e["D20_LO"]
    return {k: np.asarray(e[k], dtype=bool) for k in STATE_EVENTS}
