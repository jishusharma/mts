"""Tests for nkn03-intraday-sequence-1114. Run: python -m pytest test_study.py -q  (synthetic data only, no cache access, < 20 s).
Negative control: the look-ahead test MUST FAIL under NKN_BUG=1 (daily context read from the same day instead of the previous closed day)."""
import os
import sys
import importlib.util
from pathlib import Path
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study as st

DAY = st.DAY
D0 = 19600  # absolute day number of the first synthetic day (2023-08-21)


def synth(ndays=120, seed=3, vol=0.0012):
    rng = np.random.default_rng(seed)
    n = ndays * 1440
    t = (D0 * DAY + np.arange(n, dtype=np.int64) * 60000)
    r = rng.normal(0, vol, n)
    c = 100 * np.exp(np.cumsum(r))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 3, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 3, n)))
    v = rng.uniform(1, 10, n)
    return dict(t=t, o=o, h=h, l=l, c=c, v=v, key="t_ms")


def truncate(b, upto_ms):
    m = b["t"] < upto_ms
    return {k: (v[m] if isinstance(v, np.ndarray) else v) for k, v in b.items()}


def pipeline(b, side=1, row="NY"):
    D = st.dense(b, 60000)
    F = st.daily_feats(D)
    HM, R4 = st.hm_pack(D), st.rsi4h(D)
    labels = {D0 + i: "MARKUP" for i in range(0, 400)}
    recs, fun, X = st.sim_row(D, F, HM, R4, row, side, ("MARKUP",), labels, F, None, "SYN", "NY1m" if row == "NY" else "UTC1m")
    return D, F, recs, fun, X


# ------------------------------------------------------------------ fee, fills, exits (hand computed)
def test_fee_on_both_legs_hand_number():
    # e=100, x=102, R=2: gross +1R. 12 bp round trip = 6 bp of 100 + 6 bp of 102 = 0.06 + 0.0612 = 0.1212 price units = 0.0606 R
    assert st.fee_r(100.0, 102.0, 2.0, 12.0) == pytest.approx(0.0606, abs=1e-9)
    assert st.fee_r(100.0, 102.0, 2.0, 6.0) == pytest.approx(0.0303, abs=1e-9)
    # fee is on BOTH legs: a loser exiting lower pays less exit fee but the entry leg is always charged
    assert st.fee_r(100.0, 98.0, 2.0, 12.0) == pytest.approx(0.0006 * 198 / 2, abs=1e-9)


def flat(nb=100, px=100.0):
    a = np.full(nb, px)
    return a.copy(), a.copy(), a.copy(), a.copy(), a.copy(), a.copy()


def test_gap_through_stop_fills_at_open():
    O, H, L, C, CF, VW = flat()
    L[:60] = 99.0  # session low through k-1 = 99 -> structural R = 1 > 0.5% floor
    O[70], H[70], L[70], C[70] = 95.0, 95.5, 94.0, 96.0
    x, xm, dist, stop = st.simulate(1, O, H, L, C, CF, VW, 60, 100.0, 0.0, 1, 810)
    assert dist == pytest.approx(1.0) and stop == pytest.approx(99.0)
    assert (x, xm) == (95.0, 70)  # gap: fill at the bar open, not at the stop
    g = (x - 100.0) / dist
    assert g == pytest.approx(-5.0)
    assert st.fee_r(100.0, x, dist, 12.0) == pytest.approx(0.0006 * 195.0)


def test_stop_beats_vwap_close_exit_in_one_bar():
    O, H, L, C, CF, VW = flat()
    L[:60] = 99.0
    # minute 89 of the NY session is 14:59 = last bar of an epoch hour: close below VWAP AND the low touches the stop
    O[89], L[89], C[89] = 100.0, 98.9, 99.5
    x, xm, dist, stop = st.simulate(1, O, H, L, C, CF, VW, 60, 100.0, 0.0, 1, 810)
    assert (x, xm) == (pytest.approx(99.0), 89)  # stop wins, fills at the stop (no gap)


def test_vwap_hour_close_exit_and_terminal_exit():
    O, H, L, C, CF, VW = flat()
    L[:60] = 99.0
    C[88], C[89] = 99.4, 99.5  # 88 is not an hour end: below VWAP there does not exit. 89 is.
    x, xm, dist, stop = st.simulate(1, O, H, L, C, CF, VW, 60, 100.0, 0.0, 1, 810)
    assert (x, xm) == (99.5, 89)
    O, H, L, C, CF, VW = flat()
    CF[-1] = 100.7
    x, xm, dist, stop = st.simulate(1, O, H, L, C, CF, VW, 60, 100.0, 0.0, 1, 810)
    assert (x, xm) == (100.7, 99)  # session-end close


def test_entry_bar_can_stop_out_and_short_mirror():
    O, H, L, C, CF, VW = flat()
    L[:60] = 99.0
    L[60] = 98.0
    x, xm, dist, stop = st.simulate(1, O, H, L, C, CF, VW, 60, 100.0, 0.0, 1, 810)
    assert (x, xm) == (99.0, 60)
    O, H, L, C, CF, VW = flat()
    H[:60] = 101.0
    O[70], H[70], L[70], C[70] = 106.0, 107.0, 105.0, 105.5
    x, xm, dist, stop = st.simulate(-1, O, H, L, C, CF, VW, 60, 100.0, 0.0, 1, 810)
    assert (x, xm, stop) == (106.0, 70, pytest.approx(101.0))


def test_floor_takes_over_when_structure_is_tiny():
    O, H, L, C, CF, VW = flat()
    L[:60] = 99.9  # structural 0.1 < 0.5% (0.5) and < 0.6 ATR (0.9)
    x, xm, dist, stop = st.simulate(1, O, H, L, C, CF, VW, 60, 100.0, 1.5, 1, 810)
    assert dist == pytest.approx(0.9)


def test_funding_r_hand():
    assert st.funding_r(1, 100.0, 2.0, 950, 960, 0.0001) == pytest.approx(0.005)
    assert st.funding_r(1, 100.0, 2.0, 960, 1000, 0.0001) == 0.0  # stamp exactly at the entry bar start: not held
    assert st.funding_r(-1, 100.0, 2.0, 950, 960, 0.0001) == pytest.approx(-0.005)
    assert st.funding_r(1, 100.0, 2.0, 950, 960, float("nan")) == 0.0


# ------------------------------------------------------------------ split, cells
def test_split_by_signal_bar_not_entry_or_exit():
    assert st.split_label(st.SPLIT_MS - 1) == "DEV"
    assert st.split_label(st.SPLIT_MS) == "VAL"
    b = synth(400, seed=3, vol=0.002)
    D, F, recs, fun, X = pipeline(b)
    assert len(recs) > 0
    for r in recs:
        # the signal time is the session open + 60 min of the session day; entry/exit time never enters the split
        assert r["sig_ms"] == r["abs_day"] * DAY + (810 + 60) * 60000
    # a session on 2023-12-31 stays DEV even though its exit is after any later timestamp, and 2024-01-01 is VAL
    d_dev = (st.SPLIT_MS // DAY - 1) * DAY + (810 + 60) * 60000
    d_val = (st.SPLIT_MS // DAY) * DAY + (810 + 60) * 60000
    assert st.split_label(d_dev) == "DEV" and st.split_label(d_val) == "VAL"


def test_control_phase_trade_never_lands_in_primary_cell():
    n = 8
    T = dict(src=np.array(["NY1m", "NY1m", "NY1m", "NY1m", "UTC1m", "NY15m", "NY1m", "NY1m"]),
             side=np.array([1, 1, 1, -1, 1, 1, 1, 1]),
             ph=np.array(["ACCUM-RANGE", "DISTRIBUTION", "MARKDOWN", "MARKDOWN", "MARKUP", "MARKUP", "MARKUP", "RELIEF"]),
             scan2=np.ones(n, bool), v1=np.ones(n, bool), v2=np.ones(n, bool), atl=np.ones(n, bool))
    m = st.cell_masks(T)
    for cid in st.PRIMARY:
        assert m[cid][[0, 1, 2, 3, 4, 5, 7]].sum() == 0, cid  # control phases, short, UTC row, 15m row, other phases: never primary
        assert m[cid][6]  # the one MARKUP / NY / long trade is in every primary cell here
    assert m["C2"][0] and m["C3"][1] and m["C4"][3] and m["C5"][4] and m["C6"][5]
    assert not m["C4"][2]  # a MARKDOWN LONG is not the mirror short control
    assert not m["C2"][6]


def test_primary_cells_count():
    assert len(st.CELLS) == 15 and len(st.PRIMARY) == 5


# ------------------------------------------------------------------ rule pieces
def make_sess(nd=1, nb=390, px=100.0):
    S = st.Sess()
    S.bm, S.nb, S.open_min = 1, nb, 810
    S.O = np.full((nd, nb), px)
    S.H = np.full((nd, nb), px)
    S.L = np.full((nd, nb), px)
    S.C = np.full((nd, nb), px)
    S.V = np.ones((nd, nb))
    S.PC = np.full(nd, px)
    S.PH = np.full(nd, px + 1.0)
    S.PL = np.full(nd, px - 5.0)
    return S


def test_trap_scanner_confirm_skip_hand_cases():
    S = make_sess()
    # dip below the prior close (100) at minute 3, close back above at minute 8, first hour ends at 102.5 > prior high 101, range small
    S.L[0, 3] = 99.0
    S.C[0, 8:60] = 101.5
    S.H[0, :60] = 102.6
    S.C[0, 59] = 102.5
    c = st.conditions(S, 1)
    assert c["trap"][0] and c["conf"][0] and c["scan_hi"][0] and not c["skip"][0]
    # the dip comes at minute 12 (outside the 10 minute window): no trap
    S2 = make_sess()
    S2.L[0, 12] = 99.0
    S2.C[0, 13:60] = 101.5
    S2.C[0, 59] = 102.5
    assert not st.conditions(S2, 1)["trap"][0]
    # reclaim never closes above before 14:30: no trap
    S3 = make_sess()
    S3.L[0, 3] = 99.0
    S3.C[0, 3:60] = 99.5
    S3.C[0, 59] = 99.5
    assert not st.conditions(S3, 1)["trap"][0]
    # a big first hour range (> 4%) is skipped
    S4 = make_sess()
    S4.H[0, 20] = 105.0
    S4.L[0, 21] = 100.0
    assert st.conditions(S4, 1)["skip"][0]
    # short mirror: pop above the prior close, close back below, first hour close below the prior LOW
    S5 = make_sess()
    S5.PL[0] = 98.0
    S5.H[0, 4] = 101.0
    S5.C[0, 9:60] = 97.0
    S5.C[0, 59] = 97.0
    c5 = st.conditions(S5, -1)
    assert c5["trap"][0] and c5["conf"][0] and c5["scan_hi"][0]


def test_session_anchored_first_hour_uses_minutes_0_to_59_only():
    S = make_sess()
    S.C[0, 59] = 102.5
    S.C[0, 60] = 90.0  # minute 60 (after the first hour) must not change the first-hour return
    assert st.conditions(S, 1)["ret"][0] == pytest.approx(0.025)


def test_pivot_formula_hand():
    P, S1, R1 = st.pivots(110.0, 90.0, 103.0)
    assert P == pytest.approx(101.0)
    assert S1 == pytest.approx(92.0) and R1 == pytest.approx(112.0)
    e = np.array([92.2, 100.0, 96.0])
    assert list(st.at_level(1, e, 101.0, 92.0, 112.0, 4.0)) == [True, True, False]  # band 0.25 x 4 = 1.0


def test_vwap_cum_hand():
    H = np.array([[11.0, 12.0]]); L = np.array([[9.0, 10.0]]); C = np.array([[10.0, 11.0]]); V = np.array([[1.0, 3.0]])
    v = st.vwap_cum(H, L, C, V)
    assert v[0, 0] == pytest.approx(10.0)
    assert v[0, 1] == pytest.approx((10.0 * 1 + 11.0 * 3) / 4)


def test_find_entry_fill_rules():
    S = make_sess(nb=100, px=101.0)  # price trades above VWAP 100
    VW = np.full((1, 100), 100.0)
    S.L[0, 70] = 99.5  # touch at 70, opens at 100 -> fill at VWAP 100
    kk, e = st.find_entry(S, VW, 1, np.array([True]))
    assert kk[0] == 70 and e[0] == pytest.approx(100.0)  # opens at 101 (above vwap): limit fill at VWAP
    S.O[0, 65] = 99.0  # an earlier bar opens BELOW vwap and touches -> fill at the open
    S.L[0, 65] = 98.8
    kk, e = st.find_entry(S, VW, 1, np.array([True]))
    assert kk[0] == 65 and e[0] == pytest.approx(99.0)
    kk, e = st.find_entry(S, VW, 1, np.array([False]))
    assert kk[0] == -1
    S2 = make_sess(nb=100, px=101.0)
    S2.L[0, 59] = 90.0  # no entry before open + 60 min (bar 60)
    kk, e = st.find_entry(S2, VW, 1, np.array([True]))
    assert kk[0] == -1


def test_hm_wma_matches_manual_and_is_causal():
    b = synth(40, seed=9)
    D = st.dense(b, 60000)
    HM = st.hm_pack(D)
    r = HM["r9"]
    i = 300
    w = np.arange(21, 0, -1, dtype=float)
    manual = sum(w[k] * r[i - k] for k in range(21)) / w.sum()
    assert HM["red"][i] == pytest.approx(manual)
    b2 = truncate(b, D["T0"] + (i + 1) * 3600000)
    HM2 = st.hm_pack(st.dense(b2, 60000))
    assert HM2["red"][i] == pytest.approx(HM["red"][i]) and HM2["g"][i] == pytest.approx(HM["g"][i])


def test_epoch_alignment_matches_tf_resample_registry():
    spec = importlib.util.spec_from_file_location("tfr", str(st.LAYERS / "timeframe" / "tf_resample.py"))
    tfr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tfr)
    import json
    reg = json.loads((st.LAYERS / "timeframe" / "registry.json").read_text())
    rng = np.random.default_rng(1)
    for t in rng.integers(1_500_000_000_000, 1_790_000_000_000, 50):
        for tf, ms in (("1h", 3600000), ("4h", 4 * 3600000)):
            assert tfr.bucket_start(int(t), tf, reg) == (int(t) // ms) * ms
    # the study's hour / 4h index uses the same epoch grid: hour index = (t - T0) // 1h with T0 a UTC midnight
    assert st.dense(synth(2), 60000)["T0"] % (4 * 3600000) == 0


# ------------------------------------------------------------------ look-ahead
def day_state(X, i):
    C0, R = X["C0"], X["R"]
    vals = [C0[k][i] for k in ("scan_hi", "scan_lo", "trap", "conf", "skip", "valid")] + [C0["ret"][i]]
    vals += [R[k][i] for k in ("hm", "v1", "v2", "atr", "tag")]
    vals += [X["P"][i], X["S1"][i], X["R1"][i], X["S"].PH[i], X["S"].PL[i], X["S"].PC[i]]
    return np.array(vals, dtype=float)


def test_lookahead_conditions_unchanged_by_truncation():
    b = synth(400, seed=3, vol=0.002)
    D, F, recs, fun, X = pipeline(b)
    rng = np.random.default_rng(4)
    for i in rng.choice(np.arange(60, 380), 6, replace=False):  # index into S.days: session day D0 + i + 1
        day = int(X["S"].abs_day[i])
        read_ms = day * DAY + (810 + 60) * 60000
        b2 = truncate(b, read_ms)  # nothing at or after the read time exists
        D2, F2, recs2, fun2, X2 = pipeline(b2)
        for j in (i - 2, i - 1, i):  # day i and earlier: unchanged
            a, c = day_state(X, j), day_state(X2, j)
            assert np.allclose(a, c, equal_nan=True), (j, a, c)


def test_ladder_frozen_at_window_start():
    b = synth(60, seed=2)
    D, F, recs, fun, X = pipeline(b)
    i = 40
    day = int(X["S"].abs_day[i])
    open_ms = day * DAY + 810 * 60000
    b2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in b.items()}
    m = b2["t"] >= open_ms
    for k in "ohlc":
        b2[k][m] = b2[k][m] * 1.07  # alter day d's bars from its own open on
    D2, F2, recs2, fun2, X2 = pipeline(b2)
    assert np.allclose([X["P"][i], X["S1"][i], X["R1"][i]], [X2["P"][i], X2["S1"][i], X2["R1"][i]])
    m2 = (b["t"] >= open_ms - 3600000 * 5) & (b["t"] < open_ms)  # but a change INSIDE the prior window does move it
    b3 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in b.items()}
    for k in "hlc":
        b3[k][m2] = b3[k][m2] * 1.2
    D3, F3, recs3, fun3, X3 = pipeline(b3)
    assert not np.isclose(X["P"][i], X3["P"][i])


def test_entry_and_stop_causal():
    b = synth(400, seed=3, vol=0.002)
    D, F, recs, fun, X = pipeline(b)
    assert len(recs) >= 8, "synthetic data must produce trades"
    r = recs[len(recs) // 2]
    ent_ms = r["abs_day"] * DAY + (810 + r["k"]) * 60000
    b2 = truncate(b, ent_ms + 60000)  # bars up to and including the entry bar only
    D2, F2, recs2, fun2, X2 = pipeline(b2)
    r2 = [q for q in recs2 if q["abs_day"] == r["abs_day"]]
    assert r2 and r2[0]["k"] == r["k"] and r2[0]["e"] == pytest.approx(r["e"])


def test_signal_time_never_before_open_plus_60():
    D, F, recs, fun, X = pipeline(synth(400, seed=3, vol=0.002))
    for r in recs:
        assert r["k"] >= 60


def test_funnel_is_monotone_and_trades_have_finite_numbers():
    D, F, recs, fun, X = pipeline(synth(400, seed=3, vol=0.002))
    order = ["valid", "scan_lo"]
    assert fun["scan_hi"] <= fun["scan_lo"] <= fun["valid"] <= fun["days"]
    assert fun["touch"] <= fun["hm"] <= fun["noskip"] <= fun["conf"] <= fun["trap"] <= fun["scan_hi"]
    for r in recs:
        assert np.isfinite([r["e"], r["x"], r["dist"], r["g"], r["f12"]]).all() and r["dist"] > 0


# ------------------------------------------------------------------ statistics and data checks
def test_bh_hand_example():
    q = st.bh(np.array([0.01, 0.04, 0.03, 0.2, 0.5]))
    assert q == pytest.approx([0.05, 0.0666667, 0.0666667, 0.25, 0.5], abs=1e-5)


def test_ex_best5_removes_best_days():
    R = np.array([10.0, 9, 8, 7, 6, 1, 1, 1, 1, 1])
    day = np.arange(10)
    assert st.ex_best5(R, day) == pytest.approx(1.0)


def test_bootstrap_day_cluster_reproducible_and_stats_keys():
    rng = np.random.default_rng(0)
    n = 300
    T = dict(g=rng.normal(0.05, 1, n), f12=np.full(n, 0.05), f6=np.full(n, 0.025), fund=np.zeros(n), abs_day=rng.integers(0, 120, n), hold=np.full(n, 100))
    a, b = st.stats(T), st.stats(T)
    assert a == b and a["n"] == n and a["ci_day_lo"] <= a["net12"] <= a["ci_day_hi"]
    assert a["net12"] == pytest.approx((T["g"] - 0.05).mean())


def test_time_key_and_step_assertions(tmp_path):
    p = tmp_path / "x.npz"
    t = np.arange(10) * 60000
    np.savez(p, t_ms=t[::-1], o=t, h=t, l=t, c=t, v=t)
    with pytest.raises(AssertionError):
        st.load_npz(p, 60000)
    np.savez(p, t_ms=np.array([0, 60000, 90000]), o=t[:3], h=t[:3], l=t[:3], c=t[:3], v=t[:3])
    with pytest.raises(AssertionError):
        st.load_npz(p, 60000)
    np.savez(p, x=t, o=t, h=t, l=t, c=t, v=t)
    with pytest.raises(AssertionError):
        st.load_npz(p, 60000)
    np.savez(p, ts=t, o=t.astype(float), h=t.astype(float), l=t.astype(float), c=t.astype(float), v=t.astype(float))
    assert st.load_npz(p, 60000)["key"] == "ts"


def test_results_json_size_if_present():
    p = HERE / "results.json"
    if p.exists():
        assert p.stat().st_size < 200_000
    for q in HERE.iterdir():
        assert q.stat().st_size < 5_000_000
