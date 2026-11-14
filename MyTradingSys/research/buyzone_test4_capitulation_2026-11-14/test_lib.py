import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as T


def series(n=60):
    l = np.full(n, 20.0)
    l[7:14] = [15, 14, 13, 10, 13, 14, 15]          # swing low 10 at bar 10, level S = 10
    l[30] = 9.0                                      # undercut bar u = 30
    c = l + 1.5
    c[30] = 9.5                                      # closes below S
    c[31] = 11.0                                     # first close back above S: s = 31
    o = l + 1.0
    h = l + 2.0
    fund = np.full(n, 0.0001)
    fund[30] = -0.0001
    oi = np.full(n, 100.0)
    oi[30] = 90.0
    ts = (np.arange(n) * T.DAY + 1600000000000 // T.DAY * T.DAY).astype(np.int64)
    return dict(coin="T", ts=ts, o=o, h=h, l=l, c=c, fund=fund, oi=oi, oi_start=int(ts[0]))


def test_signature_found():
    d = series()
    sg = T.signatures(d["l"], d["c"], d["fund"], d["oi"])
    x = next(v for v in sg if v["u"] == 30)
    assert x["s"] == 31 and x["S"] == 10.0 and x["F"] and x["O"] and x["B"]
    assert [(v["u"], v["s"]) for v in T.full_signatures(sg)] == [(30, 31)]


def test_each_condition_is_needed():
    d = series()
    f = d["fund"].copy()
    f[30] = 0.0001                                   # funding positive
    assert T.full_signatures(T.signatures(d["l"], d["c"], f, d["oi"])) == []
    oi = d["oi"].copy()
    oi[30] = 96.0                                    # OI down only 4%
    assert T.full_signatures(T.signatures(d["l"], d["c"], d["fund"], oi)) == []
    c = d["c"].copy()
    c[31:] = 9.0                                     # never closes back above S
    assert T.full_signatures(T.signatures(d["l"], c, d["fund"], d["oi"])) == []
    oi2 = d["oi"].copy()
    oi2[30 - 7] = np.nan                             # OI missing: no unwind claimed
    assert T.full_signatures(T.signatures(d["l"], d["c"], d["fund"], oi2)) == []


def test_causal_truncation():
    d = series()
    assert T.full_signatures(T.signatures(d["l"], d["c"], d["fund"], d["oi"], n_avail=31)) == []   # s=31 not closed
    sg = T.full_signatures(T.signatures(d["l"], d["c"], d["fund"], d["oi"], n_avail=32))
    assert [(v["u"], v["s"]) for v in sg] == [(30, 31)]


def test_reclaim_window_is_14_bars():
    d = series()
    c = d["c"].copy()
    c[31:45] = 9.0
    c[45] = 11.0                                     # bar 45 = u + 15 > u + 14
    assert T.full_signatures(T.signatures(d["l"], c, d["fund"], d["oi"])) == []
    c[44] = 11.0                                     # bar 44 = u + 14: allowed
    assert [v["s"] for v in T.full_signatures(T.signatures(d["l"], c, d["fund"], d["oi"]))] == [44]


def test_sim_trade_stop_and_time_exit():
    d = series()
    o, l, c = d["o"], d["l"].copy(), d["c"]
    assert T.sim_trade(o, d["h"], l, c, 32, 5.0, 3) == (34, c[34])
    l[33] = 4.0
    assert T.sim_trade(o, d["h"], l, c, 32, 5.0, 3) == (33, min(o[33], 5.0))
    assert T.sim_trade(o, d["h"], l, c, 58, 5.0, 3) is None


def test_build_events_stop_entry_and_hold():
    d = series()
    ev, _ = T.build_events(d, 1)
    assert len(ev) == 1
    e = ev[0]
    assert e["u"] == 30 and e["s"] == 31 and e["e"] == 32 and e["phase"] == "NOPHASE"
    atr = T.L.wilder_atr(d["h"], d["l"], d["c"])
    stop = 9.0 - max(0.6 * atr[31], 0.005 * 9.0)
    assert abs(e["r"] - (d["o"][32] - stop) / d["o"][32]) < 1e-12
    assert abs(e["gross"] - (d["c"][32] / d["o"][32] - 1)) < 1e-12
    ev7, _ = T.build_events(d, 7)
    assert ev7[0]["x"] == 38


def test_lows_population():
    n = 200
    h = np.full(n, 100.0)
    l = np.full(n, 90.0)
    l[150] = 60.0                                    # 40% fall from the 100 high
    fund, oi = np.zeros(n), np.full(n, 50.0)
    assert T.lows(h, l, fund, oi) == [150]
    l2 = l.copy()
    l2[150] = 80.0                                   # only a 20% fall
    assert T.lows(h, l2, fund, oi) == []
    oi2 = oi.copy()
    oi2[150] = np.nan
    assert T.lows(h, l, fund, oi2) == []


def test_placebo_deterministic_and_gross_matches_manual():
    d = series(80)
    pools = {"T": T.PlaceboPool(d)}
    ev = [dict(coin="T", phase="NOPHASE", r=0.1)]
    a, sk = T.placebo(pools, ev, "ALL", 3, 0.0012, False, ndraw=50)
    b, _ = T.placebo(pools, ev, "ALL", 3, 0.0012, False, ndraw=50)
    assert sk == 0 and np.allclose(a, b) and len(a) == 50
    e = np.array([40])
    g = pools["T"].gross(e, np.array([0.1]), 3)[0]
    assert abs(g - (d["c"][42] / d["o"][40] - 1)) < 1e-12   # no stop hit: Close[e+hold-1]
    e2 = np.array([20])
    d["l"][21] = 1.0                                         # force the stop on the second bar
    g2 = pools["T"].gross(e2, np.array([0.1]), 3)[0]
    assert abs(g2 - (min(d["o"][21], d["o"][20] * 0.9) / d["o"][20] - 1)) < 1e-12


def test_stop_uses_lowest_low_between_undercut_and_reclaim():
    d = series()
    d["l"][31] = 8.0                                 # deeper low on the reclaim bar
    d["h"][31] = 13.0
    ev, _ = T.build_events(d, 1)
    atr = T.L.wilder_atr(d["h"], d["l"], d["c"])
    stop = 8.0 - max(0.6 * atr[31], 0.005 * 8.0)
    assert abs(ev[0]["r"] - (d["o"][32] - stop) / d["o"][32]) < 1e-12
