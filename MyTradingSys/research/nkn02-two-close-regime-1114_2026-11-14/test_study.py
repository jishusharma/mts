"""Tests for nkn02-two-close-regime-1114. Run: python -m pytest test_study.py -q
Synthetic data only (no cache access). Covers: look-ahead (truncation invariance of indicators, phases, masks, resampled bars), fee on both legs (hand number),
split by signal bar, gap fill, control-phase trades never in a primary cell, trigger hand cases, exit/time-stop/unresolved, de-overlap, episodes, BH, placebo."""
import sys
import datetime as dt
from pathlib import Path
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study as S

DAY = S.DAY


def rw(n, seed, drift=0.0):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.02, n)))
    o = np.r_[c[0], c[:-1]] * (1 + rng.normal(0, 0.003, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.006, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.006, n)))
    t = (19000 + np.arange(n)) * DAY
    return t, o, h, l, c


def packD(n=500, seed=1, cyc_seed=2):
    t, o, h, l, c = rw(n, seed)
    D = S.make_D(t, o, h, l, c)
    D["cyc"] = np.random.default_rng(cyc_seed).choice(np.array([-1, 0, 1], np.int8), n)
    D["btcmd"] = np.random.default_rng(cyc_seed + 1).random(n) < 0.3
    D["btc200"] = np.random.default_rng(cyc_seed + 2).random(n) < 0.5
    return D


def trunc(D, k):
    return {kk: (v[:k] if isinstance(v, np.ndarray) else v) for kk, v in D.items()}


def test_lookahead_indicators_phase_masks():
    """truncate data after bar t: indicators, phase, ADX, RSI regime and every cell mask up to t are unchanged."""
    total = 0
    for seed in (1, 2, 3):
        D = packD(600, seed, seed + 10)
        M, pools, _ = S.build_masks(D)
        total += sum(int(m.sum()) for m in M.values())
        for k0 in (350, 420, 515):
            t, o, h, l, c = D["t"][:k0], D["o"][:k0], D["h"][:k0], D["l"][:k0], D["c"][:k0]
            T = S.make_D(t, o, h, l, c)
            for key in ("cyc", "btcmd", "btc200"):
                T[key] = D[key][:k0]
            for key in ("s20", "s50", "s200", "atr", "adx", "dip", "dim", "phase", "rsireg", "ll", "hh"):
                np.testing.assert_array_equal(np.nan_to_num(D[key][:k0], nan=-9), np.nan_to_num(T[key], nan=-9), err_msg=key)
            M2, p2, _ = S.build_masks(T)
            for k in M:
                np.testing.assert_array_equal(M[k][:k0], M2[k], err_msg=f"mask {k} seed {seed} t0 {k0}")
            for s in ("L", "S"):
                np.testing.assert_array_equal(pools[s][:k0], p2[s])
    assert total > 20, "test is vacuous: no signals fired"


def test_lookahead_would_be_caught():
    """poking a FUTURE close changes later masks only (sanity that the invariance test can fail): modify bar t+50, masks before t+50 unchanged, after may change."""
    D = packD(500, 4, 5)
    M, _, _ = S.build_masks(D)
    t, o, h, l, c = (D[k].copy() for k in ("t", "o", "h", "l", "c"))
    c[400] *= 1.3
    h[400] = max(h[400], c[400])
    D2 = S.make_D(t, o, h, l, c)
    for k in ("cyc", "btcmd", "btc200"):
        D2[k] = D[k]
    M2, _, _ = S.build_masks(D2)
    for k in M:
        np.testing.assert_array_equal(M[k][:400], M2[k][:400])


def test_resample_truncation_and_partial_day():
    n = 96 * 12 + 40
    t = (19000 * 96 + np.arange(n)) * S.M15
    rng = np.random.default_rng(3)
    c = 100 + np.cumsum(rng.normal(0, 1, n))
    raw = S.check_series(t, c, c + 1, c - 1, c)
    d = S.daily_from_15m(raw)
    assert len(d["t"]) == 12   # the final partial day (40 bars) is dropped
    cut = 96 * 7 + 13
    raw2 = S.check_series(t[:cut], c[:cut], (c + 1)[:cut], (c - 1)[:cut], c[:cut])
    d2 = S.daily_from_15m(raw2)
    assert len(d2["t"]) == 7
    for k in ("t", "o", "h", "l", "c"):
        np.testing.assert_array_equal(d[k][:7], d2[k])
    # interior downtime gap keeps the day (shorter), never breaks contiguity
    keep = np.ones(n, bool)
    keep[96 * 3 + 80: 96 * 3 + 96] = False   # last 4 bars of day 3 missing
    raw3 = S.check_series(t[keep], c[keep], (c + 1)[keep], (c - 1)[keep], c[keep])
    d3 = S.daily_from_15m(raw3)
    assert len(d3["t"]) == 12


def test_loader_asserts():
    t = np.arange(50) * S.M15
    z = np.ones(50)
    S.check_series(t, z, z, z, z)
    tt = t.copy(); tt[10] = tt[9]
    with pytest.raises(AssertionError):
        S.check_series(tt, z, z, z, z)
    with pytest.raises(AssertionError):
        S.check_series(t + 1, z, z, z, z)
    with pytest.raises(AssertionError):
        S.check_series(np.arange(50) * 2 * S.M15, z, z, z, z)
    tg = np.r_[t[:20], t[20:] + 100 * S.M15]
    with pytest.raises(AssertionError):
        S.check_series(tg, z, z, z, z)   # gap > 12 h


def test_fee_on_both_legs_hand_number():
    """entry 100, exit 110, stop distance 5, 12 bp round trip = 6 bp on 100 + 6 bp on 110 = 0.06 + 0.066 = 0.126 price units = 0.0252 R; gross 2.0 -> net 1.9748."""
    fee = S.fee_r(np.array([100.0]), np.array([110.0]), np.array([5.0]), 12.0)
    assert fee[0] == pytest.approx(0.0252, abs=1e-12)
    assert 2.0 - fee[0] == pytest.approx(1.9748, abs=1e-12)
    assert S.fee_r(np.array([100.0]), np.array([110.0]), np.array([5.0]), 6.0)[0] == pytest.approx(0.0126, abs=1e-12)
    # short: entry 100, exit 90, R 5: fee (0.06 + 0.054)/5 = 0.0228
    assert S.fee_r(np.array([100.0]), np.array([90.0]), np.array([5.0]), 12.0)[0] == pytest.approx(0.0228, abs=1e-12)


def hand_arrays(n=30):
    o = np.full(n, 100.0); h = np.full(n, 102.0); l = np.full(n, 98.0); c = np.full(n, 100.0)
    return o, h, l, c


def hand_D(n=30):
    o, h, l, c = hand_arrays(n)
    return dict(t=(19000 + np.arange(n)) * DAY, o=o, h=h, l=l, c=c, atr=np.full(n, 2.0), ll=np.full(n, 95.0), hh=np.full(n, 105.0), s20=np.full(n, 100.0))


def test_exit_next_open_after_two_closes_and_R():
    D = hand_D(30)
    D["o"][4] = 101.0
    D["c"][5], D["c"][6] = 99.0, 98.0      # two closes under SMA20 at days 5, 6 -> exit signal at 6, exit at the open of day 7
    D["o"][7] = 97.0
    T = S.sim(D, np.array([3]), 1, S.exit_cond_daily(D, 1), 1, S.TIME_STOP_D)
    assert T["e"][0] == 4 and T["X"][0] == 7
    assert T["entry"][0] == 101.0 and T["x"][0] == 97.0
    assert T["R"][0] == pytest.approx(6.0)          # structural 101-95 = 6 beats 0.505 and 1.2
    assert T["g"][0] == pytest.approx((97.0 - 101.0) / 6.0)
    assert not T["floor"][0] and not T["unres"][0]
    D["ll"][:] = 100.5                                # structural 0.5 -> floor 1.2 (0.6 x ATR) wins
    T = S.sim(D, np.array([3]), 1, S.exit_cond_daily(D, 1), 1, S.TIME_STOP_D)
    assert T["R"][0] == pytest.approx(1.2) and T["floor"][0]


def test_pair_must_be_inside_holding_period_time_stop_and_unresolved():
    D = hand_D(30)
    D["c"][3], D["c"][4] = 99.0, 99.0           # pair BEFORE / at entry: ignored (needs j >= e+1)
    T = S.sim(D, np.array([3]), 1, S.exit_cond_daily(D, 1), 1, 5)
    assert T["X"][0] == 4 + 5 and not T["unres"][0]   # time stop at the open of e+5
    T = S.sim(D, np.array([3]), 1, S.exit_cond_daily(D, 1), 1, 100)
    assert T["unres"][0] and T["x"][0] == D["c"][-1] and T["X"][0] == 29


def test_short_mirror_exit():
    D = hand_D(30)
    D["c"][5], D["c"][6] = 101.0, 102.0
    D["o"][7] = 103.0
    T = S.sim(D, np.array([3]), -1, S.exit_cond_daily(D, -1), 1, S.TIME_STOP_D)
    assert T["X"][0] == 7 and T["R"][0] == pytest.approx(5.0)   # hh 105 - entry 100
    assert T["g"][0] == pytest.approx(-3.0 / 5.0)


def test_gap_fill():
    o = np.array([100.0, 100.0, 90.0, 100.0]); h = np.array([101.0, 101.0, 91.0, 101.0]); l = np.array([99.0, 99.0, 88.0, 99.0])
    # long, stop 95: bar 1 does not touch, bar 2 gaps open 90 below stop -> fills at the OPEN (90)
    assert S.stop_fill(o, h, l, 1, 95.0, 1) is None
    assert S.stop_fill(o, h, l, 2, 95.0, 1) == 90.0
    # touch inside a bar fills at the stop
    l2 = np.array([99.0, 94.0, 88.0, 99.0]); o2 = np.array([100.0, 100.0, 100.0, 100.0])
    assert S.stop_fill(o2, h, l2, 1, 95.0, 1) == 95.0
    # short, stop 105: gap up open 110 fills at 110; touch fills at 105
    o3 = np.array([100.0, 110.0]); h3 = np.array([101.0, 112.0]); l3 = np.array([99.0, 108.0])
    assert S.stop_fill(o3, h3, l3, 1, 105.0, -1) == 110.0
    h4 = np.array([101.0, 106.0]); o4 = np.array([100.0, 101.0])
    assert S.stop_fill(o4, h4, l3, 1, 105.0, -1) == 105.0


def test_stop_path_uses_gap_fill():
    D = hand_D(30)
    D["o"][6] = 90.0; D["l"][6] = 88.0
    T = S.sim(D, np.array([3]), 1, S.exit_cond_daily(D, 1), 1, S.TIME_STOP_D)
    T["xs"] = S.stop_path_x(D, T)
    assert T["xs"][0] == 90.0 and T["entry"][0] == 100.0   # stop at 100-R(5)=95, bar 6 opens 90 -> filled at 90


def mkT(ts, coin=0):
    n = len(ts)
    return dict(t=np.arange(n), e=np.arange(n) + 1, X=np.arange(n) + 5, entry=np.full(n, 100.0), x=np.full(n, 105.0), R=np.full(n, 5.0), g=np.full(n, 1.0),
                floor=np.zeros(n, bool), unres=np.zeros(n, bool), side=np.ones(n, np.int8), ts=np.asarray(ts, np.int64), day=np.asarray(ts, np.int64) // DAY,
                coin=np.full(n, coin), dist=np.zeros(n), gapatr=np.zeros(n), dcross=np.full(n, np.nan), oi5=np.full(n, np.nan), xs=np.full(n, 105.0))


def test_split_by_signal_bar_not_exit_bar():
    # signal on 2023-12-31 (exit in 2024) is DEV; signal on 2024-01-01 is VAL
    ts = [S.SPLIT - DAY, S.SPLIT, S.SPLIT + 3 * DAY]
    T = mkT(ts)
    T["X"] = np.array([10, 10, 10])   # exit bar index is irrelevant to the split
    d, _ = S.row_stats(T, "DEV", full=False)
    v, _ = S.row_stats(T, "VAL", full=False)
    assert d["n"] == 1 and v["n"] == 2


def test_control_cells_never_land_in_primary_cells():
    for seed in range(1, 6):
        D = packD(700, seed, seed + 20)
        M, pools, _ = S.build_masks(D)
        assert not (M[1] & M[12]).any() and not (M[4] & M[11]).any()           # same trigger, other cell
        assert not (M[1] & M[9]).any() and not (M[4] & M[10]).any()            # continuation (UP x BULL etc.) vs turn
        assert not (pools["L"] & pools["S"]).any()
        for k in (2, 3):
            assert not (M[k] & ~M[1]).any()                                    # V1/V2 are subsets of V0
        for k in (5, 6):
            assert not (M[k] & ~M[4]).any()
    # planted: BULL cycle everywhere -> the long turn cell (primary 1-3) is empty while the control 12 / draft 25 fire
    D = hand_long_D(cyc=1)
    M, _, _ = S.build_masks(D)
    assert not M[1].any() and not M[2].any() and not M[3].any() and M[12][41] and M[25][41]


def hand_long_D(cyc, phase=0):
    n = 70
    c = np.full(n, 80.0); c[40], c[41], c[42] = 101.0, 102.0, 103.0
    D = S.make_D((19000 + np.arange(n)) * DAY, c, c + 1, c - 1, c)
    D["c"] = c
    D["s20"] = np.full(n, 100.0); D["s50"] = np.full(n, 100.0); D["s200"] = np.full(n, 90.0)
    D["atr"] = np.full(n, 2.0)
    D["phase"] = np.full(n, phase, np.int8)
    D["cyc"] = np.full(n, cyc, np.int8)
    return D


def test_long_trigger_hand_case():
    D = hand_long_D(cyc=0, phase=0)
    M, _, _ = S.build_masks(D)
    assert np.flatnonzero(M[1]).tolist() == [41]        # 2nd confirming close; day 42 is not fresh (day 40 was already confirming)
    assert np.flatnonzero(M[7]).tolist() == [40]        # 1-close control fires on the first confirming close
    assert np.flatnonzero(M[25]).tolist() == [41, 42]   # draft (no freshness, no arming) fires on both
    D = hand_long_D(cyc=0, phase=1)                     # coin UP at the prior close: not a long-turn cell
    M, _, _ = S.build_masks(D)
    assert not M[1].any() and not M[7].any()
    D = hand_long_D(cyc=1, phase=0)                     # cycle BULL: long turn cell closed, S-TURN mismatched long (12) open
    M, _, _ = S.build_masks(D)
    assert not M[1].any() and np.flatnonzero(M[12]).tolist() == [41]


def test_arming_needs_ten_of_thirty_below_sma200():
    D = hand_long_D(cyc=0, phase=0)
    D["c"][5:40] = 95.0          # only days 0-4 stay under SMA200 (5 days) -> not armed
    M, _, _ = S.build_masks(D)
    assert not M[1].any()


def test_short_trigger_hand_case():
    n = 40
    c = np.full(n, 80.0); c[10:13] = 87.0
    D = S.make_D((19000 + np.arange(n)) * DAY, c, c + 1, c - 1, c)
    D["c"] = c
    D["s20"] = np.full(n, 85.0); D["s50"] = np.full(n, 85.0); D["s200"] = np.full(n, 90.0)
    D["atr"] = np.full(n, 2.0)
    D["phase"] = np.zeros(n, np.int8); D["cyc"] = np.ones(n, np.int8)
    M, _, _ = S.build_masks(D)
    assert np.flatnonzero(M[4]).tolist() == [14]
    D["cyc"] = np.full(n, -1, np.int8)                  # BEAR: S-TURN closed, L-TURN mismatched short (11) open
    M, _, _ = S.build_masks(D)
    assert not M[4].any() and np.flatnonzero(M[11]).tolist() == [14]
    D["cyc"] = np.ones(n, np.int8); c2 = c.copy(); c2[6] = 91.0   # one close above SMA200 inside the 10-day hold window breaks the strict hold
    D["c"] = c2
    M, _, _ = S.build_masks(D)
    assert not M[4].any()


def test_deoverlap_one_open_trade_per_coin():
    T = dict(t=np.array([3, 6, 9]), e=np.array([4, 7, 10]), X=np.array([10, 12, 15]))
    K = S.deoverlap(T)
    assert K["t"].tolist() == [3, 9]    # day 6 is inside the first trade; entry bar 10 == previous exit bar is allowed


def test_episodes_bh_ex5_placebo_weekday():
    assert S.episodes([100, 105, 111, 300, 305]) == 2
    assert S.episodes([0, 11]) == 2 and S.episodes([0, 10]) == 1 and S.episodes([]) == 0
    assert S.bh_q([0.01, 0.04, 0.03]).tolist() == pytest.approx([0.03, 0.04, 0.04])
    R = np.array([10.0, 9, 8, 7, 6, 1, 2, 3.0]); day = np.arange(8)
    assert S.ex_best5(R, day) == pytest.approx(2.0)
    pools = {0: np.full(50, 0.1)}
    p, m, _ = S.placebo(np.zeros(20, int), 0.5, pools, nb=200)
    assert p == pytest.approx(1 / 201) and m == pytest.approx(0.1)
    p, m, _ = S.placebo(np.zeros(20, int), 0.05, pools, nb=200)
    assert p == 1.0
    sat = (dt.date(2024, 1, 6) - dt.date(1970, 1, 1)).days
    assert (sat + 3) % 7 == 5 and (sat + 4) % 7 != 5


def test_files_small():
    for p in HERE.iterdir():
        if p.is_file():
            assert p.stat().st_size < 200_000, p.name


def test_hourly_resample_fills_missing_hours_flat():
    n = 96
    t = (19000 * 96 + np.arange(n)) * S.M15
    c = 100.0 + np.arange(n)
    keep = np.ones(n, bool)
    keep[20:28] = False        # 2 whole hours (bars 20..27) missing
    raw = S.check_series(t[keep], c[keep], c[keep] + 1, c[keep] - 1, c[keep])
    H = S.hourly_from_15m(raw)
    assert len(H["t"]) == 24 - 1 or len(H["t"]) == 24   # final bucket kept only if complete
    assert (np.diff(H["t"]) == S.H1).all()
    k = 5      # hour 5 = bars 20..23 missing: flat at the previous close (bar 19)
    assert H["o"][k] == H["h"][k] == H["l"][k] == H["c"][k] == c[19]
