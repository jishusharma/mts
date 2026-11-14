import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bear4h as B

T0 = 1577836800000  # 2020-01-01 UTC, a multiple of 4h


def flat_series(n=80, vol_window=False):
    t = np.arange(n)
    c = np.full(n, 100.0)
    h = c + 0.5
    l = c - 0.5
    o = c.copy()
    if vol_window:
        c = c.copy()
        c[25:39] = np.where(np.arange(25, 39) % 2 == 0, 80.0, 100.0)
        o = c.copy()
        l = np.minimum(l, c - 0.5)
        h = np.maximum(h, c + 0.01)
        h[25:39] = 100.5
    ts = (T0 + t * B.BAR).astype(np.int64)
    return ts, o, h, l, c


def with_spikes(h, hp=105.0, hj=108.0):
    h = h.copy()
    h[20], h[40] = hp, hj
    return h


def rsi_arr(n, rp=70.0, rj=60.0):
    r = np.full(n, 50.0)
    r[20], r[40] = rp, rj
    return r


def test_signal_at_confirming_close_with_stop():
    ts, o, h, l, c = flat_series()
    h = with_spikes(h)
    atr = B.L1.wilder_atr(h, l, c)
    sig = B.find_signals(o, h, l, c, atr, rsi_arr(len(c)))
    assert [s[:2] for s in sig] == [(43, 40)]          # known only at the close of bar j+3
    assert abs(sig[0][2] - (108 + max(0.6 * atr[43], 0.005 * 108))) < 1e-9


def test_no_signal_when_rsi_not_lower():
    ts, o, h, l, c = flat_series()
    h = with_spikes(h)
    atr = B.L1.wilder_atr(h, l, c)
    assert B.find_signals(o, h, l, c, atr, rsi_arr(len(c), 60.0, 70.0)) == []


def test_no_signal_when_price_high_not_higher():
    ts, o, h, l, c = flat_series()
    h = with_spikes(h, 108.0, 105.0)
    atr = B.L1.wilder_atr(h, l, c)
    assert B.find_signals(o, h, l, c, atr, rsi_arr(len(c))) == []


def test_no_signal_when_inside_bollinger_band():
    ts, o, h, l, c = flat_series(vol_window=True)   # closes swing 80/100 -> upper band about 110 > 108
    h = with_spikes(h)
    atr = B.L1.wilder_atr(h, l, c)
    assert B.bollinger_upper(c)[40] > 108
    assert B.find_signals(o, h, l, c, atr, rsi_arr(len(c))) == []
    ts, o, h, l, c = flat_series()                   # same pivots, flat closes -> outside the band -> signal
    h = with_spikes(h)
    assert len(B.find_signals(o, h, l, c, B.L1.wilder_atr(h, l, c), rsi_arr(len(c)))) == 1


def test_causality_by_truncation():
    for seed in range(4):
        rng = np.random.default_rng(seed)
        n = 3000
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.004, n)))
        l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.004, n)))
        atr, rsi = B.L1.wilder_atr(h, l, c), B.L1.wilder_rsi(c)
        full = B.find_signals(o, h, l, c, atr, rsi)
        assert len(full) > 5
        for cut in (900, 1500, 2200):
            part = B.find_signals(o, h, l, c, atr, rsi, n_avail=cut)
            assert part == [s for s in full if s[0] < cut]


def test_exit_gap_above_stop_exits_at_open():
    n = 60
    c = np.full(n, 100.0); o = c.copy(); h = c + 0.2; l = c - 0.2
    atr = np.full(n, 1.0)
    o[12] = 104.0; h[12] = 105.0; l[12] = 103.8; c[12] = 104.5
    assert B.sim_exit(o, h, l, c, atr, 10, 103.0) == (12, 104.0)


def test_exit_time_and_trail():
    n = 100
    c = np.full(n, 100.0); o = c.copy(); h = c + 0.2; l = c - 0.2
    atr = np.full(n, 1.0)
    assert B.sim_exit(o, h, l, c, atr, 10, 110.0) == (10 + B.HOLD - 1, 100.0)
    # price falls, then bounces 2.5 above the running low: trail = low + 2 x ATR is hit
    for t in range(11, 20):
        l[t] = 100 - (t - 10)
        h[t] = l[t] + 0.5
    h[20] = 100 - 9 + 2.5
    o[20] = 92.0
    l[20] = 100 - 9
    x, px = B.sim_exit(o, h, l, c, atr, 10, 110.0)
    assert x == 20 and abs(px - ((100 - 9) + 2.0)) < 1e-9


def test_previous_day_mapping_no_same_day_leak():
    dts = np.array([T0 + i * B.DAY for i in range(10)], np.int64)
    arr = np.arange(10)
    ts4 = np.array([T0 + 5 * B.DAY + k * B.BAR for k in range(6)], np.int64)   # all inside day 5
    assert (B.map_prev_day(ts4, dts, arr, -1) == 4).all()
    arr2 = arr.copy(); arr2[5:] = 999                                          # day 5 and later change
    assert (B.map_prev_day(ts4, dts, arr2, -1) == 4).all()
    assert B.map_prev_day(np.array([T0 - B.DAY], np.int64), dts, arr, -1)[0] == -1


def test_funding_cum_bar_assignment():
    ts4 = np.array([T0 + k * B.BAR for k in range(5)], np.int64)
    G, first = B.funding_cum(ts4, [[T0 + 2 * B.BAR, 0.001], [T0 + 3 * B.BAR + 5, -0.0004]])
    assert first == T0 + 2 * B.BAR
    assert np.allclose(G, [0, 0, 0.001, 0.0006, 0.0006])


def test_daily_flags_bear_vs_uptrend():
    n = 800
    up = 100 * np.exp(np.linspace(0, 2, n))
    down = np.concatenate([up[:400], up[399] * np.exp(-np.linspace(0, 1.4, 400))])
    for arr, expect_any in ((up, False), (down, True)):
        h, l = arr * 1.01, arr * 0.99
        bear, lab = B.daily_flags(h, l, arr)
        assert bool(bear[-1]) is expect_any
        assert not bear[:340].any()   # no flag before 350 daily bars exist


def synth(seed, n=6000):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.004, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.004, n)))
    ts = (T0 + np.arange(n) * B.BAR).astype(np.int64)
    fund = [[int(ts[i]), float(rng.normal(0.0001, 0.0003))] for i in range(8, n, 2)]
    return ts, o, h, l, c, fund


def coin_dict(seed):
    ts, o, h, l, c, fund = synth(seed)
    G, first = B.funding_cum(ts, fund)
    bearA = np.ones(len(c), bool)
    labA = np.array(["RANGE"] * len(c), dtype=object)
    return dict(ts=ts, o=o, h=h, l=l, c=c, bearA=bearA, labA=labA, G=G, first=first)


def test_events_lockout_and_no_overlap():
    d = coin_dict(1)
    ev, _ = B.build_events("X", d["ts"], d["o"], d["h"], d["l"], d["c"], d["bearA"], d["labA"], d["G"], d["first"])
    assert len(ev) > 10
    for a, b in zip(ev, ev[1:]):
        assert b["e"] >= a["e"] + B.LOCK and b["e"] > a["x"]
    assert all(e["r"] > 0 for e in ev)


def test_placebo_table_reproduces_real_events():
    """The vectorised placebo path must give the same gross and funding as the event simulator for the same entry bar and r."""
    d = coin_dict(2)
    ev, _ = B.build_events("X", d["ts"], d["o"], d["h"], d["l"], d["c"], d["bearA"], d["labA"], d["G"], d["first"])
    assert len(ev) > 10
    tab = B.PlaceboTable({"X": d})
    off, _n = tab.rows["X"]
    idx = np.array([[off + e["e"]] for e in ev])
    r = np.array([[e["r"]] for e in ev])
    g, fu = tab.outcome(idx, r)
    assert np.allclose(g[:, 0], [e["gross"] for e in ev], atol=1e-5)
    assert np.allclose(fu[:, 0], [e["fund"] for e in ev], atol=1e-6)


def test_placebo_draws_count_and_degenerate_pool():
    d = coin_dict(3)
    ev, _ = B.build_events("X", d["ts"], d["o"], d["h"], d["l"], d["c"], d["bearA"], d["labA"], d["G"], d["first"])
    tab = B.PlaceboTable({"X": d})
    draws = B.placebo(tab, ev[:20], "ALL", ndraw=1000)
    assert all(len(v) == 1000 for v in draws.values())
    # a pool restricted to exactly one bar reproduces the real mean R for that bar
    tab.KEY[:] = ""
    e0 = ev[0]
    tab.KEY[tab.rows["X"][0] + e0["e"]] = "BEAR"
    dr = B.placebo(tab, [e0], "ALL", ndraw=100)
    want = B.R_of(e0, 0.0012, True)
    assert np.allclose(dr[("12", True)], want, atol=1e-4)
    assert np.allclose(dr[("12", False)], B.R_of(e0, 0.0012, False), atol=1e-4)
