"""Fast synthetic tests for study.py (no cache access)."""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as S

STEP = 900000
T0 = 1609718400000      # 2021-01-04 00:00 UTC, a Monday


def make_fine(n_weeks, seed=0, drift=0.0):
    rng = np.random.default_rng(seed)
    n = n_weeks * 672
    t = T0 + np.arange(n) * STEP
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.004, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.001, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.001, n)))
    return t, o, h, l, c


def phase_for(fine, lab=3, cyc=2):
    d0 = int(fine[0][0] // S.DAY) - 5
    n = int(fine[0][-1] // S.DAY) - d0 + 10
    return np.full(n, lab), np.full(n, cyc), d0


def btc_week_of(fine):
    wt, _, _, _, wc = S.resample(*fine, S.WEEK, S.MON, STEP, 0.95)
    return (wt - S.MON) // S.WEEK, wc, S.sma(wc, 20)


def test_anchor_is_monday():
    assert (T0 - S.MON) % S.WEEK == 0


def test_resample_complete_weeks_only():
    t, o, h, l, c = make_fine(3)
    wt, wo, wh, wl, wc = S.resample(t, o, h, l, c, S.WEEK, S.MON, STEP, 0.95)
    assert len(wt) == 3 and wt[0] == T0 and wo[0] == o[0] and wc[0] == c[671] and wh[0] == h[:672].max()
    # drop the last bar of week 3: the week must disappear (no close available), incomplete tail week too
    k = slice(0, 3 * 672 - 1)
    wt2 = S.resample(t[k], o[k], h[k], l[k], c[k], S.WEEK, S.MON, STEP, 0.95)[0]
    assert len(wt2) == 2


def test_loader_keys_and_asserts(tmp_path):
    t = T0 + np.arange(100) * STEP
    x = np.arange(100.0) + 1
    np.savez(tmp_path / "a.npz", t=t, o=x, h=x, l=x, c=x, v=x)
    np.savez(tmp_path / "b.npz", ts=t, o=x, h=x, l=x, c=x, v=x)
    np.savez(tmp_path / "c.npz", a=np.c_[t, x, x, x, x, x])
    for f in "abc":
        (tt, *_), pv = S.load_fine(tmp_path / f"{f}.npz", STEP)
        assert pv["n"] == 100 and pv["first"] == T0
    np.savez(tmp_path / "d.npz", t=t[::-1], o=x, h=x, l=x, c=x, v=x)
    with pytest.raises(AssertionError):
        S.load_fine(tmp_path / "d.npz", STEP)
    np.savez(tmp_path / "e.npz", t=T0 + np.arange(100) * 7 * STEP // 4, o=x, h=x, l=x, c=x, v=x)
    with pytest.raises(AssertionError):
        S.load_fine(tmp_path / "e.npz", STEP)
    np.savez(tmp_path / "f.npz", q=t, o=x, h=x, l=x, c=x, v=x)
    with pytest.raises(AssertionError):
        S.load_fine(tmp_path / "f.npz", STEP)


def test_fee_on_both_legs_hand_number():
    # e=100, x=102, stop distance 2 (df 0.02), 12 bp round trip = 6 bp per leg: (0.0006*100 + 0.0006*102)/2 = 0.0606 R
    assert S.fee_r(100.0, 102.0, 0.02, 12.0) == pytest.approx(0.0606)
    assert S.fee_r(100.0, 102.0, 0.02, 6.0) == pytest.approx(0.0303)
    T = dict(e=np.array([100.0]), x=np.array([102.0]), df=np.array([0.02]))
    assert S.grossR(T)[0] == pytest.approx(1.0)
    assert S.netR(T, 12.0)[0] == pytest.approx(1.0 - 0.0606)
    # a stopped trade pays the exit-leg fee on the (lower) exit notional too
    T2 = dict(e=np.array([100.0]), x=np.array([98.0]), df=np.array([0.02]))
    assert S.netR(T2, 12.0)[0] == pytest.approx(-1.0 - 0.0594)


def test_stop_floor_and_atr():
    assert S.stop_frac(0.1, 100.0) == pytest.approx(0.005)          # 0.6*0.1/100 = 0.06% < floor
    assert S.stop_frac(5.0, 100.0) == pytest.approx(0.03)


def test_gap_fill_and_stop_first():
    ft = T0 + np.arange(6) * STEP
    fo = np.array([100, 100, 100, 95, 95, 95.0])
    fl = np.array([99.5, 99.5, 99.5, 94.0, 94.0, 94.0])
    # stop at 98: bar 3 opens at 95 (gap through the stop) -> fill at the OPEN 95, not at 98
    assert S.simulate_trade(ft, fo, fl, ft[0], ft[-1] + STEP, 100.0, 96.0, 0.02) == 95.0
    # intrabar break: opens 100, low 97 < 98 -> fills AT the stop 98
    fo2 = np.array([100.0] * 6)
    fl2 = np.array([99.0, 97.0, 99, 99, 99, 99.0])
    assert S.simulate_trade(ft, fo2, fl2, ft[0], ft[-1] + STEP, 100.0, 101.0, 0.02) == pytest.approx(98.0)
    # never touched -> time exit at the exit-week open
    fl3 = np.full(6, 99.0)
    assert S.simulate_trade(ft, fo2, fl3, ft[0], ft[-1] + STEP, 100.0, 103.0, 0.02) == 103.0
    # bars at/after the exit instant are not checked
    assert S.simulate_trade(ft, fo2, fl2, ft[0], ft[1], 100.0, 101.0, 0.02) == 101.0


def test_split_by_signal_week():
    sig = np.array([1703462400000, 1704067200000, 1704067200000 - 1])   # 2023-12-25 (DEV), 2024-01-01 (VAL), 1 ms before (DEV)
    T = dict(sig_t=sig)
    assert list(S.split_of(T)) == [0, 1, 0]
    # a trade entered in 2024 whose SIGNAL week is 2023-12-25 stays DEV (entry week 2024-01-01)
    assert S.split_of(dict(sig_t=np.array([1703462400000])))[0] == 0


def test_no_lookahead_signals_unchanged_by_truncation():
    fine = make_fine(110, seed=3, drift=0.0002)
    ph = phase_for(fine)
    bw = btc_week_of(fine)
    fund = (T0 + np.arange(0, 110 * 7 * 3) * 8 * 3600000, np.random.default_rng(1).normal(0.0001, 0.0001, 110 * 7 * 3))
    full = S.coin_rows("X", fine, STEP, bw, fund, ph, False)
    cut_weeks = 90
    n = cut_weeks * 672
    cut = tuple(a[:n] for a in fine)
    part = S.coin_rows("X", cut, STEP, btc_week_of(cut), fund, ph, False)
    assert len(part["wn"]) > 10
    m = {w: i for i, w in enumerate(full["wn"])}
    for key in ("hm", "lvl", "v1", "v2", "fund", "lab", "cyc"):
        for i, w in enumerate(part["wn"]):
            a, b = part[key][i], full[key][m[w]]
            assert (a == b) or (isinstance(a, float) and np.isnan(a) and np.isnan(b)), (key, w, a, b)
    # features directly: values up to week t are unchanged when later weeks are removed
    wt, wo, wh, wl, wc = S.resample(*fine, S.WEEK, S.MON, STEP, 0.95)
    F1, F2 = S.week_features(wh, wl, wc), S.week_features(wh[:70], wl[:70], wc[:70])
    for key in ("hm", "atr", "s50", "s20", "lvl"):
        np.testing.assert_array_equal(np.nan_to_num(F1[key][:70], nan=-9), np.nan_to_num(F2[key], nan=-9))
    dc = wc
    np.testing.assert_array_equal(S.daily_gate(dc)[:60], S.daily_gate(dc[:60]))


def test_future_poke_changes_nothing_before_t():
    fine = make_fine(100, seed=5)
    ph, bw = phase_for(fine), btc_week_of(fine)
    a = S.coin_rows("X", fine, STEP, bw, None, ph, False)
    poked = tuple(x.copy() for x in fine)
    poked[4][80 * 672:] *= 3
    poked[1][80 * 672:] *= 3
    poked[2][80 * 672:] *= 3
    poked[3][80 * 672:] *= 3
    b = S.coin_rows("X", poked, STEP, btc_week_of(poked), None, ph, False)
    k = [i for i, w in enumerate(a["wn"]) if w < a["wn"][-1] - 22]
    for key in ("hm", "lvl", "v1", "v2"):
        assert [a[key][i] for i in k] == [b[key][i] for i in k]


def test_hm_states_exclusive_and_neutral():
    c = 100 * np.exp(np.cumsum(np.random.default_rng(2).normal(0, 0.03, 200)))
    s = S.hm_state(c)
    assert set(np.unique(s)) <= {-1, 0, 1} and (s == 0).sum() > 0 and (s == 1).sum() > 0 and (s == -1).sum() > 0
    assert (s[:21] == 0).all()                     # WMA21 not available yet -> NEUTRAL


def test_control_phase_never_in_primary():
    n = 40
    rng = np.random.default_rng(0)
    T = dict(coin=np.array(["ETHUSDT"] * n, dtype=object), wn=np.arange(n), sig_t=np.full(n, S.SPLIT_MS + 1),
             hm=np.ones(n, int), lvl=np.zeros(n, int), v1=np.ones(n, bool), v2=np.ones(n, bool), fund=rng.normal(size=n),
             lab=np.array([S.LAB_ID["MARKUP"]] * 10 + [S.LAB_ID["RELIEF"]] * 10 + [S.LAB_ID["MARKDOWN"]] * 10 + [S.LAB_ID["ACCUM-RANGE"]] * 10),
             cyc=np.array([S.CYC_ID["BULL"]] * 5 + [S.CYC_ID["BASE"]] * 5 + [S.CYC_ID["BULL"]] * 5 + [S.CYC_ID["BEAR"]] * 5 + [S.CYC_ID["BEAR"]] * 10 + [S.CYC_ID["BULL"]] * 5 + [S.CYC_ID["BASE"]] * 5))
    D = {d[0]: d for d in S.cell_defs(T, (-0.5, 0.5))}
    pc = S.pc_mask(T)
    for pid in ("P1", "P2", "P3"):
        m = D[pid][2]
        assert not (m & ~pc).any()
        assert not (m & (T["lab"] == S.LAB_ID["MARKUP"])).any() and not (m & (T["lab"] == S.LAB_ID["MARKDOWN"])).any()
        assert not (m & (T["cyc"] == S.CYC_ID["BULL"])).any()           # RELIEF in a BULL cycle is a control, not PC
        assert not (m & D["C1"][2]).any() and not (m & D["C2"][2]).any()
    assert int(D["P1"][2].sum()) == 10          # RELIEF/BASE (5) + ACCUM-RANGE/BEAR (5); RELIEF/BULL (5) and ACCUM/BULL... are controls
    assert (D["C1"][2] & pc).sum() == 0
    assert len(D) == 22


def test_phase_lag_check_detects_lag():
    days = np.arange(100, 160)
    btc_d = np.arange(90, 170)
    btc_c = 100 + np.arange(80.0)
    lag1 = btc_c[days - 1 - 90]
    lag0 = btc_c[days - 90]
    assert S.phase_lag_check(days, lag1, btc_d, btc_c)["lag1"] == 1.0
    r = S.phase_lag_check(days, lag0, btc_d, btc_c)
    assert r["lag0"] == 1.0 and r["lag1"] == 0.0
    la, ca, d0 = S.phase_arrays(np.array([10, 11, 12]), np.array([3, 4, 5]), np.array([1, 2, 3]), shift=1)
    assert list(la) == [0, 3, 4] and d0 == 10


def test_bh_and_p():
    q = S.bh_q([0.01, 0.04, 0.03])
    assert q[0] == pytest.approx(0.03) and q[2] == pytest.approx(0.04) and q[1] == pytest.approx(0.04)
    assert S.p_one_sided(np.array([-1.0, 1, 2, 3])) == pytest.approx(2 / 5)


def test_placebo_matches_count_and_excludes_cell_state():
    rng = np.random.default_rng(1)
    n = 400
    vals = rng.normal(0, 1, n)
    month = rng.integers(1, 13, n)
    pool = np.ones(n, bool)
    cell = np.zeros(n, bool)
    cell[:50] = True
    d = S.placebo_draws(vals, month, pool, cell, nd=200)
    assert len(d) == 200 and abs(np.mean(d) - vals.mean()) < 0.2
    # a cell whose values are all higher than the pool mean sits above the placebo draws
    vals2 = vals.copy()
    vals2[:50] += 5
    assert (S.placebo_draws(vals2, month, ~cell, cell, nd=200) < vals2[cell].mean()).all()


def test_week_cluster_boot_and_ex5():
    R = np.r_[np.ones(10), np.zeros(10)]
    wk = np.repeat(np.arange(20), 1)
    b = S.boot_mean_week(R, wk, nb=500)
    assert 0.2 < b.mean() < 0.8
    assert S.ex_best5_mean(R, wk) == pytest.approx(5 / 15)
    assert S.ex_best5_diff(R, wk, np.array([0.0, 0.0])) == pytest.approx(5 / 15)


def test_level_buckets():
    wh = np.full(80, 101.0)
    wl = np.full(80, 99.0)
    wc = np.full(80, 100.0)
    wc[-1] = 100.5
    F = S.week_features(wh, wl, wc)
    assert F["lvl"][-1] == 0 and F["lvl"][10] == -1                        # at-level above, no SMA50 yet
    wc2 = wc.copy()
    wc2[-1] = 99.7
    assert S.week_features(wh, wl, wc2)["lvl"][-1] == 1
    wc3 = wc.copy()
    wc3[-1] = 130.0
    assert S.week_features(wh, np.minimum(wl, 90), wc3)["lvl"][-1] == 2


def test_verdict_underpowered_not_fail():
    st = {"P1": {"VAL": dict(n=50, n_tr=50, weeks=10, net12=0.5)}}
    g = {"P1": {"DEV": dict(diff=0.1), "VAL": {}}}
    assert S.verdict_cell("P1", st, g).startswith("UNDERPOWERED")
    st = {"P1": {"VAL": dict(n=500, n_tr=500, weeks=10, net12=0.5)}}
    assert S.verdict_cell("P1", st, g) == "UNDERPOWERED-WEEKS"
    st = {"P1": {"VAL": dict(n=500, n_tr=500, weeks=60, net12=-0.5)}}
    assert S.verdict_cell("P1", st, g) == "FAIL"
    assert S.overall({"a": "UNDERPOWERED", "b": "UNDERPOWERED-WEEKS"}) == "UNDERPOWERED"
    assert S.overall({"a": "UNDERPOWERED", "b": "FAIL"}) == "FAIL"


def test_truncation_test_detects_a_leak(monkeypatch):
    """the look-ahead detector must fail on a deliberately leaky feature (the daily gate read 10 daily bars ahead)."""
    real = S.daily_gate
    monkeypatch.setattr(S, "daily_gate", lambda dc: np.r_[real(dc)[10:], [True] * 10])
    diffs = 0
    for seed in range(7, 15):
        fine = make_fine(60, seed=seed)
        ph, bw = phase_for(fine), btc_week_of(fine)
        full = S.coin_rows("X", fine, STEP, bw, None, ph, False)
        cut = tuple(a[:57 * 672] for a in fine)
        part = S.coin_rows("X", cut, STEP, btc_week_of(cut), None, ph, False)
        m = {w: i for i, w in enumerate(full["wn"])}
        diffs += sum(part["v2"][i] != full["v2"][m[w]] for i, w in enumerate(part["wn"]))
    assert diffs > 0
