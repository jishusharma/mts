"""Tests for nkn01-convergence-breakout-1114. Synthetic data only, no cache access. Run: python -m pytest test_study.py -q
Expected numbers are hand arithmetic or FORMULAS worked examples, never taken from study.py output.
The look-ahead tests MUST FAIL under STUDY_BUG=1 (phase and cycle read at the SAME day); test_bug_flag_is_detected runs them in a subprocess with the flag on."""
import os
import sys
import subprocess
from pathlib import Path
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study as S  # noqa: E402

DAY, H4 = S.DAY, S.H4


# ---------------------------------------------------------------- synthetic data
def make_base(n4=6000, seed=3, t0=1700000000000 // DAY * DAY):
    """4h random walk with slowly switching drift, so falls, bases and rises all occur."""
    rng = np.random.default_rng(seed)
    drift = np.repeat(rng.choice([-0.0015, 0.0, 0.0012], size=n4 // 250 + 1), 250)[:n4]
    r = drift + rng.normal(0, 0.007, n4)
    c = 100 * np.exp(np.cumsum(r))
    o = np.r_[100.0, c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.003, n4)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.003, n4)))
    return dict(t=t0 + np.arange(n4, dtype=np.int64) * H4, o=o, h=h, l=l, c=c)


def make_coin(base, sym="X"):
    d1 = S.resample(base, DAY, H4)
    h4 = S.resample(base, H4, H4)
    co = S.Coin(sym, d1, h4)
    co.add_wt()
    return co


def make_market(base):
    d1 = S.resample(base, DAY, H4)
    days = np.arange(d1["t"][0] // DAY, d1["t"][-1] // DAY + 400, dtype=np.int64)
    codes = (days * 7 % 6).astype(np.int8)  # arbitrary but fixed label per date, independent of the price data
    return S.Market(d1, days, codes)


def truncate(base, k):
    return {x: v[:k] for x, v in base.items()}


def pool_attrs(co, mk, tf, sd=1):
    V = co.view(tf, sd)
    b, F = S.pool_bars(V["c"], V["mx"], V["l"])
    s, Fs = S.find_signals(V["c"], V["h"], V["l"], V["mx"], V["mn"], V["atr"], 10.0)
    return S.attrs(co, mk, tf, sd, b, F, False), S.attrs(co, mk, tf, sd, s, Fs, False), V["t"]


FIELDS = ("ph", "cyc", "lvl", "wt", "fund", "c8", "split")


# ---------------------------------------------------------------- indicators
def test_ema_mirror_linearity():
    x = np.random.default_rng(1).normal(100, 3, 300)
    assert np.allclose(S.ema(-x, 50), -S.ema(x, 50))


TOY_H = [10, 11, 12, 11, 13, 14, 13, 12, 11, 12, 13, 15, 14, 13, 12, 11, 12, 14, 15, 14]
TOY_L = [8, 9, 10, 9, 10, 12, 11, 10, 9, 10, 11, 12, 12, 11, 10, 9, 10, 11, 13, 12]
TOY_C = [9, 10, 11, 10, 12, 13, 12, 11, 10, 11, 12, 14, 13, 12, 11, 10, 11, 13, 14, 13]


def test_adx_toy_formulas_s30():
    dip, dim, adx = S.adx_di(TOY_H, TOY_L, TOY_C, 3)
    assert abs(dip[3] - 33.333) < 1e-2 and abs(dim[3] - 16.667) < 1e-2
    assert abs(dip[4] - 47.619) < 1e-2 and abs(dim[4] - 9.524) < 1e-2
    assert abs(adx[5] - 58.586) < 1e-2 and abs(adx[6] - 47.301) < 1e-2


def test_atr_hand():
    atr = S.wilder_atr(np.array([10, 11, 12, 11.0]), np.array([9, 9, 10, 9.0]), np.array([9.5, 10.5, 11.5, 10.0]), 3)
    # TR = 1, max(2,1.5,.5)=2, max(2,1.5,.5)=2 -> seed mean(1,2,2)=5/3; next TR = max(2, .5, 2.5)=2.5 -> (5/3*2+2.5)/3
    assert abs(atr[2] - 5 / 3) < 1e-9 and abs(atr[3] - (5 / 3 * 2 + 2.5) / 3) < 1e-9


# ---------------------------------------------------------------- fees and fills (hand numbers)
def test_fee_on_both_legs_hand():
    # entry 100, all out at 98, R = 2: gross -1; fee 12 bp = 6 bp of 100 + 6 bp of 98 = 0.0600 + 0.0588 = 0.1188 price units = 0.0594 R
    assert abs(S.fee_r(12.0, 100.0, 0, 98.0, False, 2.0) - 0.0594) < 1e-12
    # half out at 104, half at 110: exit notional 0.5*104 + 0.5*110 = 107 -> 6bp*(100+107)=0.1242 -> /2 = 0.0621 R; maker 6 bp: half of that
    assert abs(S.fee_r(12.0, 100.0, 104.0, 110.0, True, 2.0) - 0.0621) < 1e-12
    assert abs(S.fee_r(6.0, 100.0, 104.0, 110.0, True, 2.0) - 0.03105) < 1e-12
    # entry-only charging would give 0.0300 R: the exit leg must add on top
    assert S.fee_r(12.0, 100.0, 0, 98.0, False, 2.0) > 0.03


def _bars(rows):
    a = np.array(rows, float)
    return [a[:, k].tolist() for k in range(4)]  # o h l c


def test_gap_through_stop_fills_at_open():
    # entry 100 at bar 0, R=2 -> stop 98. bar1 opens 95 (gap) -> exit 95, g = -5/2 = -2.5
    o, h, l, c = _bars([(100, 101, 99.5, 100.5), (95, 96, 94, 95.5)])
    g, x1, x2, half, xi, cens = S.sim_long(o, h, l, c, [200.0] * 2, [90.0] * 2, 0, 100.0, 2.0)
    assert x2 == 95 and not half and xi == 1 and abs(g + 2.5) < 1e-12


def test_gap_through_target_fills_at_open_and_blend():
    # target 104. bar1 opens 107 (gap) -> half at 107 (+3.5 R). stack max 100, so bars 2 and 3 close inside (<=100) -> exit at the 3rd bar close 98.5
    rows = [(100, 101, 99.5, 100.5), (107, 108, 106, 107), (99.5, 99.8, 98.6, 99), (99, 99, 98.5, 98.5)]
    o, h, l, c = _bars(rows)
    g, x1, x2, half, xi, cens = S.sim_long(o, h, l, c, [100.0] * 4, [90.0] * 4, 0, 100.0, 2.0)
    assert half and x1 == 107 and x2 == 98.5 and xi == 3
    assert abs(g - (0.5 * 3.5 + 0.5 * (-1.5 / 2))) < 1e-12  # 1.375


def test_stop_first_when_stop_and_target_in_one_bar():
    o, h, l, c = _bars([(100, 101, 99.5, 100.5), (100, 105, 97, 103)])  # bar1 touches both 104 and 98
    g, x1, x2, half, xi, cens = S.sim_long(o, h, l, c, [200.0] * 2, [90.0] * 2, 0, 100.0, 2.0)
    assert not half and x2 == 98 and abs(g + 1.0) < 1e-12


def test_limit_fill_bar_target_not_allowed_and_trail():
    # limit filled inside bar 0; bar 0 high 105 would hit the 104 target, but is not allowed on the fill bar
    o, h, l, c = _bars([(101, 105, 99.5, 104), (103.5, 103.9, 103, 103.5)])
    g, x1, x2, half, xi, cens = S.sim_long(o, h, l, c, [50.0] * 2, [90.0] * 2, 0, 100.0, 2.0, limit_fill=True)
    assert not half and cens  # no stop, never inside the (tiny) stack, runs to the data end
    # same bars as a market entry: target allowed on bar 0
    g2, _, _, half2, _, _ = S.sim_long(o, h, l, c, [50.0] * 2, [90.0] * 2, 0, 100.0, 2.0, limit_fill=False)
    assert half2


def test_trail_under_lowest_ema_after_half():
    # half off bar0? no: bar1 hits target 104 (open 101, high 105), trail starts from bar1 close: mn[1]=102. bar2 low 101.5 <= 102 -> stop at 102 (open 103 above)
    o, h, l, c = _bars([(100, 101, 99.5, 100.5), (101, 105, 100.5, 104.5), (103, 103.5, 101.5, 102)])
    g, x1, x2, half, xi, cens = S.sim_long(o, h, l, c, [50.0] * 3, [90.0, 102.0, 102.0], 0, 100.0, 2.0)
    assert half and x1 == 104 and x2 == 102 and xi == 2
    assert abs(g - (0.5 * 2.0 + 0.5 * 1.0)) < 1e-12


# ---------------------------------------------------------------- split by SIGNAL bar
def test_split_by_signal_bar_not_entry():
    last_dev = S.SPLIT - H4  # 4h bar opening 2023-12-31 20:00 UTC: its entry bar opens at the split but the SIGNAL bar is DEV
    assert S.split_of([last_dev])[0] == 0 and S.split_of([S.SPLIT])[0] == 1
    assert S.split_of([S.SPLIT - 1])[0] == 0


# ---------------------------------------------------------------- hand-built signal
def _stack_case(**kw):
    n = 260
    c = np.full(n, 95.0)
    h = np.full(n, 96.0)
    l = np.full(n, 94.0)
    mx = np.full(n, kw.get("mx", 101.0))
    mn = np.full(n, 100.0)
    atr = np.full(n, kw.get("atr", 5.0))
    h[220] = 130.0
    c[250], c[251] = 102.0, 103.0
    c[240] = kw.get("c240", 95.0)
    c[252] = 104.0  # a third close above must NOT be a new signal
    return c, h, l, mx, mn, atr


def test_find_signals_hand():
    c, h, l, mx, mn, atr = _stack_case()
    s, F = S.find_signals(c, h, l, mx, mn, atr, 0.03)
    assert s.tolist() == [251] and F.tolist() == [94.0]


@pytest.mark.parametrize("kw", [dict(c240=100.5), dict(atr=30.0), dict(mx=110.0)])
def test_find_signals_each_condition_blocks(kw):
    c, h, l, mx, mn, atr = _stack_case(**kw)
    s, _ = S.find_signals(c, h, l, mx, mn, atr, 0.03)
    assert len(s) == 0


# ---------------------------------------------------------------- level
def test_weekly_level_hand():
    import datetime as dt
    mon = (dt.date(2024, 1, 1).toordinal() - 719163)  # a Monday
    assert (mon + 3) % 7 == 0
    start = mon - 7 * 3  # three extra Mondays earlier
    nd = 7 * 16
    t = (start + np.arange(nd)) * DAY
    lows = np.full(nd, 50.0)
    lows[5] = 10.0   # week 0 (oldest)
    lows[7 * 13 + 2] = 20.0  # week 13
    lows[7 * 15 + 1] = 5.0   # week 15 = last week, in progress when queried below
    ends, w12 = S.weekly_low12(t, lows)
    q_in_week15 = (start + 7 * 15 + 3) * DAY
    # complete weeks closed before q: weeks 0..14; the last 12 are weeks 3..14: contains week 13 low 20, not week 0 low 10, not week 15
    assert S.level_at(ends, w12, np.array([q_in_week15]))[0] == 20.0
    q_end15 = (start + 7 * 16) * DAY  # exactly when week 15 closes: now it counts
    assert S.level_at(ends, w12, np.array([q_end15]))[0] == 5.0
    assert np.isnan(S.level_at(ends, w12, np.array([(start + 7 * 11) * DAY]))[0])  # fewer than 12 closed weeks


# ---------------------------------------------------------------- funding
def test_fund_flag_boundary_and_poke():
    ts = np.array([1000, 2000, 3000, 4000], np.int64)
    r = np.array([0.0001, 0.0002, 0.0003, 0.0009])
    assert S.fund_flag((ts, r), [3000])[0] == 1       # mean(.0001,.0002,.0003)=.0002 <= .0003, print at ts==Td counts
    assert S.fund_flag((ts, r), [3999])[0] == 1       # the 4000 print is not settled yet
    assert S.fund_flag((ts, r), [4000])[0] == 0       # mean(.0002,.0003,.0009)=.000467 crowded
    assert S.fund_flag((ts, r), [2000])[0] == -1      # fewer than 3 prints
    r2 = r.copy()
    r2[3] = 0.5                                        # poke a future print
    assert S.fund_flag((ts, r2), [3999])[0] == 1
    assert S.fund_flag(None, [3000])[0] == -1


# ---------------------------------------------------------------- phase, cycle, no look-ahead
def test_prior_day_idx_is_previous_day_bar():
    dt_ = np.arange(10) * DAY
    T = 5 * DAY + 3600000  # inside day 5
    assert S.prior_day_idx(dt_, T) == 4  # the bar of day 4, closed at the start of day 5


def test_lookahead_truncation_invariance():
    base = make_base()
    mk = make_market(base)
    full = make_coin(base)
    A_full, S_full, t_full = pool_attrs(full, mk, "4h")
    for k in (4300, 4713, 5400):  # cut inside a day on purpose
        part = make_coin(truncate(base, k))
        A_p, S_p, t_p = pool_attrs(part, make_market(truncate(base, k)), "4h")
        # market must be the same label table; reuse the full one so only price-derived context is under test
        A_p, S_p, t_p = pool_attrs(part, mk, "4h")
        for (Af, tf_), (Ap, tp_) in (((A_full, t_full), (A_p, t_p)),):
            fmap = {int(t): i for i, t in enumerate(Af["t"])}
            assert len(Ap["t"]) > 100
            for j, t in enumerate(Ap["t"]):
                i = fmap[int(t)]
                for f in FIELDS:
                    assert Ap[f][j] == Af[f][i], (k, f, int(t))
        # signals (generous width so the synthetic path produces some)
        fmap = {int(t): i for i, t in enumerate(S_full["t"])}
        for j, t in enumerate(S_p["t"]):
            i = fmap[int(t)]
            for f in FIELDS:
                assert S_p[f][j] == S_full[f][i]
        # every truncated signal bar exists in the full series (signals up to t unchanged)
        assert set(S_p["t"].tolist()) <= set(S_full["t"].tolist())


def test_lookahead_truncation_daily_rows_too():
    base = make_base(n4=7000, seed=9)
    mk = make_market(base)
    full = make_coin(base)
    A_full, S_full, _ = pool_attrs(full, mk, "1d")
    part = make_coin(truncate(base, 6001))
    A_p, S_p, _ = pool_attrs(part, mk, "1d")
    fmap = {int(t): i for i, t in enumerate(A_full["t"])}
    assert len(A_p["t"]) > 50
    for j, t in enumerate(A_p["t"]):
        for f in FIELDS:
            assert A_p[f][j] == A_full[f][fmap[int(t)]]


def test_wt_and_phase_poke_future_bar():
    base = make_base(n4=3000, seed=5)
    a = make_coin(base)
    b2 = {k: v.copy() for k, v in base.items()}
    b2["c"][2500:] *= 1.3
    b2["h"][2500:] *= 1.3
    b2["l"][2500:] *= 1.3
    b2["o"][2500:] *= 1.3
    b = make_coin(b2)
    kd = int(np.searchsorted(a.B["1d"]["t"], base["t"][2500] // DAY * DAY))  # first daily bar that contains the poke
    assert np.allclose(a.wt1[:kd], b.wt1[:kd], equal_nan=True)
    assert (a.ph[:kd] == b.ph[:kd]).all()
    assert np.allclose(a.ind["1d"]["em"][:, :kd], b.ind["1d"]["em"][:, :kd])


def test_phase_labels_are_causal_states():
    # a long steady uptrend labelled UP, a flat noisy series RANGE, steady fall DOWN (ADX high, DI direction, slope sign)
    n = 200
    up = np.linspace(100, 300, n) * (1 + 0.002 * np.sin(np.arange(n)))
    d = dict(h=up * 1.004, l=up * 0.996, c=up)
    assert S.coin_phase(d)[-1] == S.PH_UP
    dn = dict(h=up[::-1] * 1.004, l=up[::-1] * 0.996, c=up[::-1])
    assert S.coin_phase(dn)[-1] == S.PH_DOWN
    rng = np.random.default_rng(2)
    fl = 100 + rng.normal(0, 0.3, n)
    assert S.coin_phase(dict(h=fl + 0.2, l=fl - 0.2, c=fl))[-1] == S.PH_RANGE
    assert S.coin_phase(d)[10] == S.PH_NA


# ---------------------------------------------------------------- cells
def test_cell_table_shape():
    ids = [c["id"] for c in S.CELLS]
    assert len(ids) == 13 == len(set(ids))
    prim = [c for c in S.CELLS if c["status"] == "PRIMARY"]
    assert [c["id"] for c in prim] == ["P1", "P2", "P3"]
    assert all(c["sd"] == 1 and c["ph"] == S.PH_RANGE and c["cyc"] == ("ACCUM-RANGE",) and c["lvl"] == "at" and c["tf"] == "1d" for c in prim)


def test_control_phase_trade_never_lands_in_primary_cell():
    prim = [c for c in S.CELLS if c["status"] == "PRIMARY"]
    for ph in (S.PH_UP, S.PH_RANGE, S.PH_DOWN, S.PH_NA):
        for cyc in range(-1, 6):
            for lvl in (-1, 0, 1):
                A = dict(ph=np.array([ph], np.int8), cyc=np.array([cyc], np.int8), lvl=np.array([lvl], np.int8), wt=np.array([1], np.int8),
                         fund=np.array([1], np.int8), c8=np.array([1], np.int8))
                in_prim = any(S.cell_mask(A, c)[0] for c in prim)
                is_primary_state = ph == S.PH_RANGE and cyc == S.CYC["ACCUM-RANGE"] and lvl == 1
                assert in_prim == is_primary_state, (ph, cyc, lvl)
    # explicit examples: UP x ACCUM at-level is control C4 only; RANGE x MARKUP is control C2 only
    A = dict(ph=np.array([S.PH_UP], np.int8), cyc=np.array([S.CYC["ACCUM-RANGE"]], np.int8), lvl=np.array([1], np.int8), wt=np.array([1], np.int8),
             fund=np.array([1], np.int8), c8=np.array([0], np.int8))
    hit = [c["id"] for c in S.CELLS if c["tf"] == "1d" and c["sd"] == 1 and c["W"] == .03 and c["entry"] == "mkt" and S.cell_mask(A, c)[0]]
    assert hit == ["C4"]


def test_variant_nesting_and_nodata():
    A = dict(ph=np.zeros(3, np.int8), cyc=np.full(3, S.CYC["ACCUM-RANGE"], np.int8), lvl=np.ones(3, np.int8), wt=np.array([0, 1, 1], np.int8),
             fund=np.array([1, -1, 1], np.int8), c8=np.zeros(3, np.int8))
    m = {c["id"]: S.cell_mask(A, c).tolist() for c in S.CELLS[:3]}
    assert m["P1"] == [True, True, True] and m["P2"] == [False, True, True] and m["P3"] == [False, False, True]


# ---------------------------------------------------------------- stats
def test_bh_hand():
    q = S.bh_q([0.01, 0.04, 0.03])
    assert np.allclose(q, [0.03, 0.04, 0.04])


def test_placebo_p_hand():
    real, rc = np.full(20, 1.0), np.zeros(20, int)
    pool, pc = np.zeros(50), np.zeros(50, int)
    rm, pm, p, nu, cov = S.placebo_p(real, rc, pool, pc, 1)
    assert rm == 1.0 and pm == 0.0 and abs(p - 1 / (S.N_PLACEBO + 1)) < 1e-12 and nu == 20 and cov == 1.0


def test_cluster_boot_zero_mean_not_significant():
    rng = np.random.default_rng(4)
    x = rng.normal(0, 1, 400)
    lo, p = S.cluster_boot(x, np.arange(400) // 3, 1000, 1)
    assert lo < 0 < 1 and p > 0.05


def test_mirror_view():
    base = make_base(n4=1500, seed=2)
    co = make_coin(base)
    v1, v2 = co.view("4h", 1), co.view("4h", -1)
    assert np.allclose(v2["c"], -v1["c"]) and np.allclose(v2["h"], -v1["l"])
    assert np.allclose(v2["mx"], -v1["mn"]) and np.allclose(v2["mn"], -v1["mx"])


def test_loader_asserts_key_and_monotonic(tmp_path):
    p = tmp_path / "a.npz"
    t = np.arange(10, dtype=np.int64) * 900000
    np.savez(p, ts=t, o=t * 1.0, h=t * 1.0, l=t * 1.0, c=t * 1.0, v=t * 1.0)
    b, prov = S.load_base(p, 900000)
    assert prov["key"] == "ts" and prov["gap_events"] == 0
    np.savez(tmp_path / "b.npz", ts=t[::-1], o=t * 1.0, h=t * 1.0, l=t * 1.0, c=t * 1.0, v=t * 1.0)
    with pytest.raises(AssertionError):
        S.load_base(tmp_path / "b.npz", 900000)
    np.savez(tmp_path / "c.npz", x=t, o=t * 1.0, h=t * 1.0, l=t * 1.0, c=t * 1.0, v=t * 1.0)
    with pytest.raises(AssertionError):
        S.load_base(tmp_path / "c.npz", 900000)


def test_resample_drops_incomplete_edges():
    t = (np.arange(8 * 96) + 10) * 900000  # starts 10 bars into a day, ends with a partial day
    b = dict(t=t, o=np.arange(len(t)) * 1.0, h=np.arange(len(t)) + 2.0, l=np.arange(len(t)) - 1.0, c=np.arange(len(t)) + .5)
    d = S.resample(b, DAY, 900000)
    assert (d["n"] == 96).all() and len(d["t"]) == 7


def test_file_sizes():
    for p in HERE.iterdir():
        if p.is_file():
            assert p.stat().st_size < 5_000_000, p
    r = HERE / "results.json"
    if r.exists():
        assert r.stat().st_size < 200_000


def test_phase_read_at_prior_close_exact():
    """phase attached to a signal/pool bar = phase at the close of the daily bar of the day BEFORE the first-close bar's day (hand index arithmetic)."""
    base = make_base(n4=6000, seed=3)
    co, mk = make_coin(base), make_market(base)
    A, _, t4 = pool_attrs(co, mk, "4h")
    d1t = co.B["1d"]["t"]
    V = co.view("4h", 1)
    b, _F = S.pool_bars(V["c"], V["mx"], V["l"])
    Tf = V["t"][b - 1]
    k = Tf // DAY - d1t[0] // DAY  # daily index of the day containing the first-close bar
    expect = np.where(k - 1 >= 0, co.ph[np.maximum(k - 1, 0)], S.PH_NA)
    assert (A["ph"] == expect).all()
    assert len(set(co.ph[1:].tolist())) >= 2 and (co.ph[1:] != co.ph[:-1]).sum() > 20  # the test can tell the lag apart


def test_cycle_read_is_label_of_the_bars_date():
    days = np.arange(19000, 19050, dtype=np.int64)
    codes = (days % 6).astype(np.int8)
    mk = S.Market(dict(t=days * DAY, c=np.linspace(1, 2, 50)), days, codes)
    T = days * DAY + 5 * 3600000
    assert (mk.cycle_at(T) == codes).all()  # label of date d (already built from closes through d-1 in phase_daily.csv)
    assert mk.cycle_at(np.array([60000 * DAY]))[0] == -1


def test_bug_flag_is_detected():
    """The look-ahead tests must fail when the phase / cycle are read at the same day (STUDY_BUG=1)."""
    env = dict(os.environ, STUDY_BUG="1")
    r = subprocess.run([sys.executable, "-m", "pytest", str(HERE / "test_study.py"), "-q", "-k", "phase_read_at_prior_close_exact or cycle_read_is_label", "-p", "no:cacheprovider"],
                       env=env, capture_output=True, text=True)
    assert r.returncode != 0, "look-ahead test did not catch STUDY_BUG=1"
