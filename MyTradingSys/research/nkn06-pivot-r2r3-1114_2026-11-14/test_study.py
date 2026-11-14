"""Tests for NKN-06 (synthetic data only, no cache access). Run: python -m pytest MyTradingSys/research/nkn06-pivot-r2r3-1114_2026-11-14/test_study.py -q"""
import sys, warnings
from pathlib import Path
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nkn06_core as nc
import study as st

DAY, H1, M15 = nc.DAY, nc.H1, nc.M15
D0 = 18000  # an arbitrary UTC day number (a Monday-agnostic start; weeks are handled by id)


def synth(days, seed=3, start_day=D0, vol=0.002):
    rng = np.random.default_rng(seed)
    n = days * 96
    t = (start_day * DAY + np.arange(n) * M15).astype(np.int64)
    r = rng.normal(0, vol, n)
    c = 100 * np.exp(np.cumsum(r))
    o = np.r_[100.0, c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 2, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 2, n)))
    v = np.ones(n)
    return t, o, h, l, c, v


def coin(days, cut=None, seed=3):
    t, o, h, l, c, v = synth(days, seed)
    if cut is not None:
        t, o, h, l, c, v = (a[:cut] for a in (t, o, h, l, c, v))
    cyc_days = np.arange(D0, D0 + days + 2) + 1
    cyc_lab = np.zeros(len(cyc_days), np.int8)
    return nc.build_coin(t, o, h, l, c, v, cyc_days, cyc_lab, cyc_days, np.zeros(len(cyc_days), np.int8))


FIELDS = ["R2", "R3", "S2", "S3", "atr", "trend", "malk", "cycle", "pb", "dayhi", "daylo", "prevok", "first", "btcf", "wR1", "wH"]


def test_lookahead_truncation_invariance():
    """truncate the data after bar t: every condition attached to bars up to t (levels, ATR, trend phase, cycle, Malkan, %B, day extremes) and every signal up to t is unchanged."""
    days = 330
    full = coin(days)
    cut = 250 * 96 + 37  # mid-day cut at a 15m bar
    part = coin(days, cut=cut)
    for tf in ("15m", "1h", "4h"):
        Xf, Xp = nc.tf_ctx(full, tf), nc.tf_ctx(part, tf)
        m = Xp["n"]
        assert m > 100
        assert np.array_equal(Xf["t"][:m], Xp["t"])
        for k in FIELDS:
            a, b = Xf[k][:m], Xp[k]
            assert np.array_equal(a, b, equal_nan=True) if a.dtype.kind == "f" else np.array_equal(a, b), (tf, k)
        for d in (1, -1):
            for mode in ("cross", "away"):
                sf = nc.signals(Xf, d, mode)
                sp = nc.signals(Xp, d, mode)
                assert np.array_equal(sf[sf < m], sp), (tf, d, mode)
    # the trend and Malkan labels of the cut day itself must exist in the full series but never leak into the truncated one
    assert (nc.tf_ctx(part, "1h")["trend"][-1] == nc.tf_ctx(full, "1h")["trend"][: nc.tf_ctx(part, "1h")["n"]][-1])


def test_lookahead_test_has_power():
    """a deliberately leaky label (the SAME day's close) differs between full and truncated data on the cut day, so the invariance test above would catch it."""
    full, part = coin(330), coin(330, cut=250 * 96 + 37)
    day_cut = (250 * 96 + 37) // 96 + D0
    q = np.array([day_cut])
    leaky_full = nc.lookup(full["dn"], full["trend_close"], q, nc.UNK)
    leaky_part = nc.lookup(part["dn"], part["trend_close"], q, nc.UNK)
    assert leaky_full[0] != nc.UNK and leaky_part[0] == nc.UNK
    ok_full = nc.lookup(full["dn"] + 1, full["trend_close"], q, nc.UNK)
    ok_part = nc.lookup(part["dn"] + 1, part["trend_close"], q, nc.UNK)
    assert ok_full[0] == ok_part[0]


def test_cycle_label_for_day_uses_prior_close_only():
    rng = np.random.default_rng(8)
    n = 1700
    c = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.03, n)))
    h, l = c * 1.01, c * 0.99
    d = np.arange(n) + D0
    days, lab = nc.cycle_labels_from_daily(d, h, l, c)
    assert (days == d + 1).all()
    assert (lab > 0).any()
    for k in (1500, 1600, 1699):
        dd, ll = nc.cycle_labels_from_daily(d[:k + 1], h[:k + 1], l[:k + 1], c[:k + 1])
        assert ll[-1] == lab[k] and dd[-1] == d[k] + 1


def test_daily_trend_causal_and_hand_cases():
    rng = np.random.default_rng(2)
    n = 200
    c = 100 * np.exp(np.cumsum(rng.normal(0.003, 0.01, n)))
    h, l = c * 1.004, c * 0.996
    full = nc.daily_trend(h, l, c)
    for k in (80, 130, 199):
        assert nc.daily_trend(h[:k + 1], l[:k + 1], c[:k + 1])[-1] == full[k]
    assert (full[:60] == nc.UNK).all()
    up = 100 * 1.01 ** np.arange(150)
    assert nc.daily_trend(up * 1.003, up * 0.997, up)[-1] == nc.UP
    dn = 100 * 0.99 ** np.arange(150)
    assert nc.daily_trend(dn * 1.003, dn * 0.997, dn)[-1] == nc.DOWN
    flat = 100 + np.sin(np.arange(150) * 0.9)
    assert nc.daily_trend(flat + 0.3, flat - 0.3, flat)[-1] == nc.RANGE


def test_malkan_codes_causal():
    rng = np.random.default_rng(4)
    c = 100 * np.exp(np.cumsum(rng.normal(0.002, 0.02, 200)))
    full = nc.malkan_codes(c)
    for k in (60, 120, 199):
        assert nc.malkan_codes(c[:k + 1])[-1] == full[k]
    assert (full[:33] == nc.UNK).all()  # needs RSI (14) then 20 values


def test_bb_percent_b_hand_value_and_future_poke():
    c = np.array([10.0] * 19 + [12.0])
    pb = nc.bb_percent_b(c)
    mean, sd = 10.1, np.sqrt((19 * 0.01 + 1.9 ** 2) / 20)
    assert pb[-1] == pytest.approx((12 - (mean - 2 * sd)) / (4 * sd))
    assert np.isnan(pb[:19]).all()
    rng = np.random.default_rng(1)
    x = 100 + np.cumsum(rng.normal(0, 1, 80))
    base = nc.bb_percent_b(x)
    y = x.copy()
    y[50:] = rng.normal(500, 50, 30)  # poke the future
    assert np.array_equal(nc.bb_percent_b(y)[:50], base[:50], equal_nan=True)


def test_pivot_formulas_by_hand():
    p = nc.pivots(np.array([110.0]), np.array([90.0]), np.array([100.0]))
    assert p["P"][0] == pytest.approx(100.0)
    assert p["R2"][0] == pytest.approx(120.0) and p["S2"][0] == pytest.approx(80.0)
    assert p["R3"][0] == pytest.approx(130.0) and p["S3"][0] == pytest.approx(70.0)


def test_fee_on_both_legs_hand_computed():
    # 12 bp round trip = 6 bp of entry notional + 6 bp of exit notional. e=100, x=102, R=1: (100*0.0006 + 102*0.0006)/1 = 0.1212 R
    assert nc.fee_r(100.0, 102.0, 1.0, 12.0) == pytest.approx(0.1212)
    assert nc.fee_r(100.0, 102.0, 1.0, 12.0) != pytest.approx(0.06)  # entry-only charge would be 0.06
    assert nc.fee_r(100.0, 102.0, 0.5, 6.0) == pytest.approx(0.1212)  # 3 bp per leg: 202 * 0.0003 = 0.0606, over R 0.5
    g = np.array([2.0])
    s = nc.cell_stats(g, np.array([100.0]), np.array([102.0]), np.array([1.0]), np.array([nc.SPLIT + 1]), "VAL", full=False)
    assert s["net12"] == pytest.approx(2.0 - 0.1212) and s["net6"] == pytest.approx(2.0 - 0.0606)


def test_split_by_signal_bar_not_entry_or_exit():
    t = np.array([nc.SPLIT - H1, nc.SPLIT, nc.SPLIT + 5 * DAY])
    assert list(nc.split_is_val(t)) == [False, True, True]
    # a P3-style trade signalled on the last DEV day whose entry and exit are in 2024 stays DEV
    g, e, x, R = np.array([1.0]), np.array([100.0]), np.array([101.0]), np.array([1.0])
    ts = np.array([nc.SPLIT - DAY])
    assert nc.cell_stats(g, e, x, R, ts, "DEV", full=False)["n"] == 1
    assert nc.cell_stats(g, e, x, R, ts, "VAL", full=False)["n"] == 0


def test_walk_gap_fills_and_ties():
    o = np.array([100.0, 100.0, 97.0, 100.0])
    h = np.array([100.5, 100.5, 98.0, 100.0])
    l = np.array([99.8, 99.6, 96.0, 99.0])
    c = np.array([100.0, 100.0, 97.5, 99.5])
    # long, stop 99, bar 2 opens at 97 (below the stop): fills at the OPEN 97, not at 99
    px, k, kind = nc.walk(o, h, l, c, 0, 3, 1, 99.0, 105.0)
    assert (px, k, kind) == (97.0, 2, "gapstop")
    # gap through the target fills at the open
    o2 = np.array([100.0, 106.0]); h2 = np.array([100.2, 107.0]); l2 = np.array([99.9, 105.5]); c2 = np.array([100.0, 106.5])
    assert nc.walk(o2, h2, l2, c2, 0, 1, 1, 99.0, 105.0) == (106.0, 1, "gaptarget")
    # stop and target inside one bar: stop first
    o3 = np.array([100.0]); h3 = np.array([106.0]); l3 = np.array([98.0]); c3 = np.array([105.0])
    assert nc.walk(o3, h3, l3, c3, 0, 0, 1, 99.0, 105.0) == (99.0, 0, "stop")
    # touch of the target fills at the level
    assert nc.walk(np.array([100.0]), np.array([105.4]), np.array([99.5]), np.array([105.0]), 0, 0, 1, 99.0, 105.0) == (105.0, 0, "target")
    # time exit
    assert nc.walk(np.array([100.0, 100.0]), np.array([100.5, 100.5]), np.array([99.5, 99.5]), np.array([100.1, 100.2]), 0, 1, 1, 99.0, 105.0) == (100.2, 1, "time")
    # short mirror: gap up through the stop fills at the open
    assert nc.walk(np.array([100.0, 103.0]), np.array([100.5, 104.0]), np.array([99.5, 102.5]), np.array([100.0, 103.5]), 0, 1, -1, 101.0, 95.0) == (103.0, 1, "gapstop")
    # close-based exit: a bar closing under the level exits at that close
    assert nc.walk(np.array([100.0, 100.0]), np.array([100.6, 100.6]), np.array([99.7, 99.7]), np.array([100.2, 99.8]), 0, 1, 1, 98.0, 105.0, close_lvl=100.0) == (99.8, 1, "closeexit")


def mkX(o, h, l, c, R2=99.8, R3=102.0, S2=96.0, S3=94.0, atr=0.4):
    n = len(o)
    t = (D0 * DAY + np.arange(n) * H1).astype(np.int64)
    return dict(n=n, step=H1, t=t, o=np.array(o, float), h=np.array(h, float), l=np.array(l, float), c=np.array(c, float), day=t // DAY,
                R2=np.full(n, R2), R3=np.full(n, R3), S2=np.full(n, S2), S3=np.full(n, S3), atr=np.full(n, atr), dcomp=np.ones(n, bool),
                dayend=np.full(n, n - 1), prevok=np.r_[False, np.ones(n - 1, bool)], first=(t % DAY) == 0, dayhi=np.maximum.accumulate(np.array(h, float)),
                daylo=np.minimum.accumulate(np.array(l, float)), trend=np.full(n, nc.UP, np.int8), cycle=np.full(n, nc.MARKUP, np.int8), malk=np.full(n, nc.BULL, np.int8),
                pb=np.full(n, 0.6), btcf=np.ones(n, np.int8), hour=((t % DAY) // H1).astype(np.int8), wR1=np.full(n, np.nan), wH=np.full(n, np.nan))


def test_sim_bar_trade_hand_numbers():
    # bar 3 closes above R2=99.8 after bar 2 closed below: signal at 3; entry at the open of bar 4 = 100; R = max(0.5, 0.24, 0.2) = 0.5; stop 99.5; target 102
    o = [99.0] * 3 + [99.5, 100.0, 100.5, 101.0, 101.6, 100.0]
    c = [99.0] * 3 + [100.0, 100.4, 100.9, 101.5, 102.4, 100.0]
    h = [99.2] * 3 + [100.1, 100.6, 101.0, 101.8, 102.6, 100.2]
    l = [98.8] * 3 + [99.4, 99.9, 100.3, 100.9, 101.9, 99.8]
    X = mkX(o, h, l, c)
    idx = nc.signals(X, 1, "cross")
    assert list(idx) == [3]
    r = nc.sim_bar_trade(X, 3, 1)
    assert r["status"] == "ok" and r["e"] == 100.0 and r["R"] == pytest.approx(0.5)
    assert r["kind"] == "target" and r["x"] == pytest.approx(102.0) and r["g"] == pytest.approx(4.0) and r["xi"] == 7
    # room rule: target 100.6 gives room 0.6 < 1.5 x 0.5 -> skipped
    X2 = mkX(o, h, l, c, R3=100.6)
    assert nc.sim_bar_trade(X2, 3, 1)["status"] == "room"
    assert nc.sim_bar_trade(X2, 3, 1, skip_room=False)["status"] == "ok"
    # a bar that OPENS above the target fills at the open (gap), not at the level
    o3 = list(o); o3[7] = 102.5
    rg = nc.sim_bar_trade(mkX(o3, h, l, c), 3, 1)
    assert rg["kind"] == "gaptarget" and rg["x"] == pytest.approx(102.5) and rg["g"] == pytest.approx(5.0)
    # signal on the last bar of the day: no next bar in the day -> no entry
    assert nc.sim_bar_trade(X, X["n"] - 1, 1)["status"] == "no_entry"


def test_signal_rules_first_cross_00utc_cond7_and_cap():
    n = 24
    c = np.full(n, 99.0)
    h = np.full(n, 99.3)
    l = np.full(n, 98.7)
    c[0] = 100.5  # the 00:00 UTC bar closes above R2: skipped (no previous bar either)
    c[5], c[6], c[7], c[8] = 100.0, 99.0, 100.1, 100.2  # fresh cross at 5 (first of the day); a later fresh cross at 7 is NOT taken
    c[10], c[11] = 99.0, 99.5
    X = mkX(c, h, l, c)
    X["h"][5] = 100.2
    X["dayhi"] = np.maximum.accumulate(X["h"])
    assert list(nc.signals(X, 1, "cross")) == [5]
    # at-level cap: first fresh cross closing more than 1 ATR above R2 (atr 0.4) is not an at-level signal, and no later bar of that day replaces it
    c2 = np.full(n, 99.0); c2[5] = 100.5; c2[7] = 100.0; c2[6] = 99.0
    X2 = mkX(c2, np.full(n, 99.3), np.full(n, 98.7), c2)
    X2["h"][5] = 100.6; X2["dayhi"] = np.maximum.accumulate(X2["h"])
    assert len(nc.signals(X2, 1, "cross")) == 0
    # away mode takes the first close beyond R2 + 1 ATR (100.2): bar 5
    assert list(nc.signals(X2, 1, "away")) == [5]
    # cond 7: the day high so far already reached R3 (102): no trigger
    c3 = np.full(n, 99.0); c3[4] = 99.0; c3[5] = 100.0
    X3 = mkX(c3, np.full(n, 99.3), np.full(n, 98.7), c3)
    X3["h"][3] = 102.5; X3["dayhi"] = np.maximum.accumulate(X3["h"])
    assert len(nc.signals(X3, 1, "cross")) == 0
    # short mirror: close below S2 (96) after a close above it
    c4 = np.full(n, 97.0); c4[6] = 95.9
    X4 = mkX(c4, c4 + 0.3, c4 - 0.3, c4)
    assert list(nc.signals(X4, -1, "cross")) == [6]


def test_control_phase_never_lands_in_primary_cell():
    trend = np.array([nc.UP, nc.UP, nc.RANGE, nc.DOWN, nc.UP, nc.UP, nc.UNK, nc.UP])
    cycle = np.array([nc.MARKUP, 3, nc.MARKUP, nc.MARKDOWN, nc.MARKDOWN, 0, nc.MARKUP, nc.MARKUP])
    R = dict(trend=trend, cycle=cycle, malk=np.full(8, nc.BULL), pb=np.full(8, 0.7), btcf=np.ones(8, np.int8))
    cells = {c["id"]: c for c in st.CELLS}
    p1 = st.cell_mask(cells["P1"], R)
    assert list(p1) == [True, False, False, False, False, False, False, True]
    p2 = st.cell_mask(cells["P2"], R)
    assert list(p2) == [False, False, False, True, False, False, False, False]
    c1 = st.cell_mask(cells["C1"], R); c2 = st.cell_mask(cells["C2"], R); c3 = st.cell_mask(cells["C3"], R)
    assert list(c1) == [False, False, True, False, False, False, False, False]
    assert list(c2) == [False, True, False, False, True, False, False, False]  # unknown cycle (0) never counts as "not MARKUP"
    assert list(c3) == list(p2)
    for ctl in (c1, c2, c3):
        assert not (ctl & p1).any()
    # layer variants only narrow the V0 cell, the opposite variant is disjoint from V1
    R["malk"] = np.array([nc.BEAR] * 8)
    assert not st.cell_mask(cells["C4"], R).any() and list(st.cell_mask(cells["C5"], R)) == list(p1)
    R["malk"] = np.array([nc.BULL] * 8); R["pb"] = np.full(8, 0.4)
    assert not st.cell_mask(cells["C6"], R).any()


def test_cell_table_counts():
    ids = [c["id"] for c in st.CELLS]
    assert len(ids) == 14 and len(set(ids)) == 14  # 3 primary + 11 controls here; C12 (placebo) is the 15th
    assert st.TOTAL_CELLS == 15 and [c["id"] for c in st.CELLS if c["role"] == "PRIMARY"] == ["P1", "P2", "P3"]


def test_p3_three_days_at_r3_hand_case():
    n = 20
    dn = np.arange(100, 100 + n)
    o = np.full(n, 125.0); h = np.full(n, 126.0); l = np.full(n, 124.0); c = np.full(n, 125.0)
    j = 10
    # day j-1: H 130.0, L 129.6, C 129.8 -> P = 129.8, R3 = (5H - 4L + 2C) / 3 = 130.4 in force on day j
    h[j - 1], l[j - 1], c[j - 1] = 130.0, 129.6, 129.8
    c[j - 2], c[j] = 130.0, 130.2  # all three closes within 0.5% under 130.4 (>= 129.748) and none above
    h[j - 2], l[j - 2] = 130.1, 129.5
    h[j], l[j] = 130.3, 129.9
    o[j + 1] = 130.2; h[j + 1] = 130.6; l[j + 1] = 130.0; c[j + 1] = 130.4
    for k in range(j + 2, j + 6):
        o[k], h[k], l[k], c[k] = 130.0, 130.3, 129.8, 130.1
    CB = dict(B={"1d": dict(t=dn * DAY, o=o, h=h, l=l, c=c)}, dn=dn, atr_d=np.full(n, 0.3), trend_close=np.full(n, nc.UP, np.int8), malk_close=np.full(n, nc.BULL, np.int8),
              cyc_days=dn + 1, cyc_lab=np.full(n, nc.MARKUP, np.int8))
    rows = nc.p3_rows(CB)
    sig = [r for r in rows if r["t"] == dn[j] * DAY]
    assert len(sig) == 1 and sig[0]["status"] == "room"  # R3 - entry = 0.2 < 1.5 R: skipped by the literal rule
    rows0 = nc.p3_rows(CB, skip_room=False)
    r = [r for r in rows0 if r["t"] == dn[j] * DAY][0]
    R = max(0.005 * 130.2, 0.6 * 0.3)
    assert r["status"] == "ok" and r["R"] == pytest.approx(R) and r["x"] == pytest.approx(130.4) and r["kind"] == "target" and r["g"] == pytest.approx((130.4 - 130.2) / R)
    assert r["trend"] == nc.UP and r["cycle"] == nc.MARKUP
    # a close above R3 on day 3 breaks the pattern
    c[j] = 130.5
    assert not [r for r in nc.p3_rows(CB, skip_room=False) if r["t"] == dn[j] * DAY]


def test_bh_and_placebo_and_verdict():
    q = nc.bh_q(np.array([0.01, 0.04, 0.03]))
    assert q == pytest.approx([0.03, 0.04, 0.04])
    same = nc.placebo_test(np.array([0.0, 0.0, 0.0]), [[0.0], [0.0], [0.0]])
    assert same["p"] > 0.9
    better = nc.placebo_test(np.array([1.0, 1.0]), [[0.0, 0.1], [0.0]])
    assert better["p"] == pytest.approx(1 / 1001) and better["matched"] == 2
    dropped = nc.placebo_test(np.array([1.0, 5.0]), [[0.0], []])
    assert dropped["matched"] == 1 and dropped["real_mean_matched"] == 1.0
    ok = dict(n=250, net12=0.1, trade_ci_low=0.01, day_ci_low=0.01, ex5=0.02)
    assert nc.cell_verdict(ok, 0.01, 0.05) == "PASS"
    assert nc.cell_verdict(ok, 0.2, 0.05) == "FAIL"  # profitable but does not beat placebo
    assert nc.cell_verdict(dict(ok, n=150), 0.01, 0.05) == "UNDERPOWERED"
    assert nc.cell_verdict(dict(ok, n=99), 0.01, 0.05) == "UNDERPOWERED"
    assert nc.cell_verdict(dict(ok, n=150, net12=-0.1), 0.01, 0.05) == "FAIL"
    assert nc.overall_verdict(["UNDERPOWERED", "FAIL", "UNDERPOWERED"]) == "FAIL"
    assert nc.overall_verdict(["UNDERPOWERED"] * 3) == "UNDERPOWERED"


def test_loader_asserts_and_resample():
    t = np.arange(0, 400) * M15
    assert nc.check_series(t)["gaps"] == 0
    with pytest.raises(AssertionError):
        nc.check_series(np.r_[t[:200], t[199:-1]])  # repeated timestamp
    with pytest.raises(AssertionError):
        nc.check_series(t + 1)  # not aligned
    ts, o, h, l, c, v = synth(2)
    keep = np.ones(len(ts), bool)
    keep[10] = False  # a hole inside the first hour group: that 1h bar must be dropped
    b = nc.resample(ts[keep], o[keep], h[keep], l[keep], c[keep], v[keep], 4)
    assert len(b["t"]) == len(ts) // 4 - 1 and (b["t"] % H1 == 0).all()
    bd = nc.resample(ts, o, h, l, c, v, 96)
    assert len(bd["t"]) == 2 and bd["h"][0] == h[:96].max() and bd["c"][0] == c[95] and bd["o"][1] == o[96]


def test_no_syntax_warnings_and_small_files():
    for p in HERE.glob("*.py"):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            compile(p.read_text(encoding="utf-8"), str(p), "exec")
    for p in HERE.iterdir():
        assert p.suffix not in (".npz", ".csv", ".pkl"), p
        assert p.stat().st_size < 200_000, p
