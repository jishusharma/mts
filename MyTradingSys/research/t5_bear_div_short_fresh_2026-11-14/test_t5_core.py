"""Synthetic-bar tests for the T5 core and stats code. No data-cache reads, no scheduler imports, seconds to run."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t5_core as T  # noqa: E402
import t5_stats as S  # noqa: E402
from MyTradingSys.backtest import fees  # noqa: E402

TS0 = 1706745600000   # 2024-02-01 00:00 UTC


def world(seed, n=6000, vol=0.012, drift=0.0004, plant=(), plant_len=15, plant_drift=0.0):
    """Random-walk 4h bars. plant: entry bars after which `plant_drift` is added to each of the next plant_len log returns."""
    rng = np.random.default_rng(seed)
    ret = rng.normal(drift, vol, n)
    for e in plant:
        ret[e:e + plant_len] += plant_drift
    c = 100 * np.exp(np.cumsum(ret))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 2, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 2, n)))
    ts = TS0 + np.arange(n, dtype=np.int64) * T.BAR
    return ts, o, h, l, c


# ---------------------------------------------------------------- look-ahead
def test_signal_causal_by_truncation_and_future_change():
    ts, o, h, l, c = world(2)
    full = T.find_signals(o, h, l, c)
    assert len(full) >= 10
    rng = np.random.default_rng(5)
    for sig in full[:12]:
        cc = sig[0]
        trunc = T.find_signals(o[:cc + 1], h[:cc + 1], l[:cc + 1], c[:cc + 1])
        assert trunc == [s for s in full if s[0] <= cc]          # the list known at the signal close equals the prefix of the full list
        f = np.ones(len(c))
        after = slice(cc + 1, None)
        f[after] = 1 + rng.uniform(-0.2, 0.2, len(c) - cc - 1)
        again = T.find_signals(o * f, h * f, l * f, c * f)
        assert sig in again                                       # same signal tuple (c, j, stop0) after the future is rewritten


def _daily_world():
    n = 760
    rng = np.random.default_rng(11)
    ret = np.concatenate([rng.normal(0.004, 0.02, 400), rng.normal(-0.009, 0.02, n - 400)])
    c = 50 * np.exp(np.cumsum(ret))
    o = np.concatenate([[50.0], c[:-1]])
    h = np.maximum(o, c) * 1.01
    l = np.minimum(o, c) * 0.99
    dts = 1640995200000 + np.arange(n, dtype=np.int64) * T.DAY      # 2022-01-01
    return dts, h, l, c


def test_phase_flag_previous_day_only_and_prefix_causal():
    dts, h, l, c = _daily_world()
    bear, lab = T.daily_bear(h, l, c)
    assert bear.any() and (~bear[400:]).any()
    for k in range(380, 760, 9):                                  # labels built from a prefix equal the prefix of the full labels
        b2, l2 = T.daily_bear(h[:k], l[:k], c[:k])
        assert (b2 == bear[:k]).all() and (l2 == lab[:k]).all()
    for D0 in (440, 450, 460, 470):                               # a spike in FUTURE highs must not move any earlier label
        h_sp = h.copy()
        h_sp[D0:] *= 3
        assert (T.daily_labels(h_sp, l, c)[:D0] == lab[:D0]).all()
    # pick a day D where the flag is true on D-1 and a rewritten future flips the flag on D
    D = next(i for i in range(500, 740) if bear[i] and bear[i - 1])
    f = np.ones(len(c))
    f[D:] = 2.5
    bear2, lab2 = T.daily_bear(h * f, l * f, c * f)
    assert bear2[D] != bear[D]
    n4 = (len(c)) * 6
    ts4 = dts[0] + np.arange(n4, dtype=np.int64) * T.BAR
    base = T.map_day_flag(ts4, dts, bear, False)
    pert = T.map_day_flag(ts4, dts, bear2, False)
    day_idx = (ts4 - dts[0]) // T.DAY
    assert (base[day_idx <= D] == pert[day_idx <= D]).all()       # bars up to and including day D read day D-1 or earlier
    # a same-day read is caught: it sees the rewritten day D on the 4h bars of day D
    same_base = T.map_day_flag(ts4, dts, bear, False, lag_days=0)
    same_pert = T.map_day_flag(ts4, dts, bear2, False, lag_days=0)
    assert (same_base[day_idx == D] != same_pert[day_idx == D]).any()


# ---------------------------------------------------------------- exits
def _flat(n=70, px=100.0):
    a = np.full(n, px)
    return a.copy(), a.copy(), a.copy(), a.copy(), np.full(n, 1.0)    # o, h, l, c, atr


def test_stop_wins_tie_with_time_exit_and_gap_fills():
    e, stop0 = 2, 105.0
    o, h, l, c, atr = _flat()
    h[e + 41] = 103.0                    # trail level at t = min(105, 100 + 2) = 102 -> hit on the very bar of the time exit
    c[e + 41] = 90.0                     # the time exit alone would pay 90
    x, px, why = T.sim_exit(o, h, l, c, atr, e, stop0)
    assert (x, px, why) == (e + 41, 102.0, "trail")               # stop wins the tie, at the level not the close
    o, h, l, c, atr = _flat()
    o[10], h[10] = 110.0, 111.0          # gap above the trailing level: filled at the open
    assert T.sim_exit(o, h, l, c, atr, e, stop0) == (10, 110.0, "trail")
    o, h, l, c, atr = _flat()
    h[e] = 106.0                         # entry bar: only stop0 is checked, fill at max(open, stop0)
    assert T.sim_exit(o, h, l, c, atr, e, stop0) == (e, 105.0, "stop")
    o[e] = 108.0                         # entry bar gaps through stop0
    assert T.sim_exit(o, h, l, c, atr, e, stop0) == (e, 108.0, "stop")


def test_trail_level_hand_number_time_exit_and_data_end():
    e, stop0 = 2, 105.0
    o, h, l, c, atr = _flat()
    l[e] = 98.0                          # level at e+1 = min(105, 98 + 2 x 1) = 100
    h[e + 1], o[e + 1] = 100.0, 99.0     # High >= level exactly -> exit at max(open 99, level 100)
    assert T.sim_exit(o, h, l, c, atr, e, stop0) == (e + 1, 100.0, "trail")
    o, h, l, c, atr = _flat()
    h[:] = 100.5
    l[:] = 99.5                          # level 101.5 never reached
    c[e + 41] = 96.0
    assert T.sim_exit(o, h, l, c, atr, e, stop0) == (e + 41, 96.0, "time")
    assert T.sim_exit(o[:e + 20], h[:e + 20], l[:e + 20], c[:e + 20], atr[:e + 20], e, stop0) is None   # still open at the data end


# ---------------------------------------------------------------- fees and funding
def _decline_bars(n=200, e=110):
    c = np.full(n, 100.0)
    for k in range(T.HOLD):
        bar = e + k
        c[bar] = 100.0 - 5.0 * (k + 1) / T.HOLD         # falls to 95.0 at bar e + 41
    c[e + T.HOLD:] = 95.0
    o = np.concatenate([[100.0], c[:-1]])
    h = o + 0.5
    l = c - 0.5
    ts = TS0 + np.arange(n, dtype=np.int64) * T.BAR
    return ts, o, h, l, c


def test_fee_and_funding_arithmetic_against_hand_numbers():
    assert T.RT_COST == fees.BINANCE_TAKER * 2 + fees.SLIPPAGE_RT_S13
    assert abs(T.RT_COST - 12e-4) < 1e-12 and abs(T.RT_COST_HALF - 6e-4) < 1e-12
    e = 110
    ts, o, h, l, c = _decline_bars(e=e)
    x = e + T.HOLD - 1
    b_pre, b_in, b_open, b_after = e - 10, e + 1, e + 5, x + 1
    prints = [(int(ts[b_pre]), 4e-4),                 # before the entry: not counted, but gives the coin funding coverage
              (int(ts[e]) + 1000, 5e-4),               # inside the entry bar: not counted
              (int(ts[b_in]) + 5, 1e-4),              # counted
              (int(ts[b_open]), 2e-4),                  # exactly at a bar open: counted
              (int(ts[x]) + T.BAR - 1, 3e-4),          # last ms of the exit bar: counted
              (int(ts[b_after]) + 1, 7e-4)]              # after the exit: not counted
    G, first, last = T.funding_cum(ts, prints)
    lab = np.array(["BASE"] * len(c), dtype=object)
    bear = np.ones(len(c), bool)
    ev, cnt = T.build_events("X", ts, o, h, l, c, bear, lab, G, first, last, sigs=[(e - 1, e - 6, 102.0)])
    assert len(ev) == 1
    t = ev[0]
    assert (t["e"], t["x"], t["reason"]) == (e, x, "time")
    assert abs(t["entry"] - 100.0) < 1e-12 and abs(t["px"] - 95.0) < 1e-12
    assert abs(t["r"] - 0.02) < 1e-12 and abs(t["gross"] - 0.05) < 1e-12
    assert abs(t["fund"] - 6e-4) < 1e-12 and t["covered"]
    assert abs(T.trade_R(t["gross"], T.RT_COST, t["fund"], t["r"], False) - 2.44) < 1e-9     # (0.05 - 0.0012) / 0.02
    assert abs(T.trade_R(t["gross"], T.RT_COST, t["fund"], t["r"], True) - 2.47) < 1e-9      # (0.05 - 0.0012 + 0.0006) / 0.02
    # a coin whose funding starts after the entry gets no funding and is flagged
    late = e + 3
    G2, f2, l2 = T.funding_cum(ts, [(int(ts[late]), 9e-4)])
    ev2, _ = T.build_events("X", ts, o, h, l, c, bear, lab, G2, f2, l2, sigs=[(e - 1, e - 6, 102.0)])
    # prints inside the hold count even when the entry bar precedes the coin's first print (PRE_REG: 0 only BEFORE the first print)
    assert not ev2[0]["covered"] and abs(ev2[0]["fund"] - 9e-4) < 1e-12
    after_exit = x + 10                                              # index of the first print, past the exit bar
    G3, f3, l3 = T.funding_cum(ts, [(int(ts[after_exit]), 9e-4)])        # first print after the exit: nothing inside the hold
    ev3, _ = T.build_events("X", ts, o, h, l, c, bear, lab, G3, f3, l3, sigs=[(e - 1, e - 6, 102.0)])
    assert ev3[0]["fund"] == 0.0 and not ev3[0]["covered"]


# ---------------------------------------------------------------- lockout, overlap, drops
def test_lockout_overlap_and_drop_rules():
    n = 400
    rng = np.random.default_rng(3)
    o = 100 + np.cumsum(rng.normal(0, 0.01, n))
    c = np.concatenate([o[1:], [o[-1]]])
    h, l = np.maximum(o, c) + 0.05, np.minimum(o, c) - 0.05
    ts = TS0 + np.arange(n, dtype=np.int64) * T.BAR
    lab = np.array(["BASE"] * n, dtype=object)
    lab[50:60] = ""
    bear = np.ones(n, bool)
    bear[180] = False                                  # a control event (BEAR false) still starts the lockout
    G = np.zeros(n)
    big = 1e9
    sigs = [(e - 1, e - 6, big) for e in (55, 80, 120, 170, 179, 180, 200, 239)]
    sigs += [(249, 244, 0.0001)]                       # e = 250: entry >= stop0, dropped and does NOT start a lockout
    sigs += [(251, 246, big)]                          # e = 252: kept
    sigs += [(389, 384, big)]                          # e = 390: still open at the data end, dropped
    sigs += [(399, 394, big)]                          # e = 400: no entry bar
    ev, cnt = T.build_events("X", ts, o, h, l, c, bear, lab, G, None, None, sigs=sigs)
    assert [t["e"] for t in ev] == [120, 180, 252]
    assert ev[1]["bear"] is False
    assert cnt["drop_warmup_end_nophase"] == 3          # e = 55 (warm-up and no phase), e = 80 (warm-up), e = 400 (no entry bar)
    assert cnt["drop_lockout"] == 4                     # 170 and 179 (after 120), 200 and 239 (after 180); 180 = 120 + 60 is kept
    assert cnt["drop_entry_ge_stop"] == 1 and cnt["drop_open_at_end"] == 1


def test_lockout_boundary_is_exactly_60_bars():
    n = 300
    ts, o, h, l, c = world(8, n=n, vol=0.001, drift=0.0)
    lab = np.array(["BASE"] * n, dtype=object)
    bear = np.ones(n, bool)
    G = np.zeros(n)
    sigs = [(119, 114, 1e9), (178, 173, 1e9), (179, 174, 1e9)]       # entries 120, 179 (59 bars later), 180 (60 bars later)
    ev, _ = T.build_events("X", ts, o, h, l, c, bear, lab, G, None, None, sigs=sigs)
    assert [t["e"] for t in ev] == [120, 180]


# ---------------------------------------------------------------- split by signal bar
def test_split_by_signal_bar_not_entry():
    last_dev = T.VAL_START - T.BAR                      # bar opening 2023-12-31 20:00, closes 2024-01-01 00:00
    assert T.split_of(last_dev) == "DEV"
    assert T.split_of(T.VAL_START) == "VAL"
    entry_ts = last_dev + T.BAR                         # its entry bar opens at the first VAL instant: the trade is still DEV
    assert T.split_of(last_dev) == "DEV" and entry_ts >= T.VAL_START
    assert not T.in_recent(T.RECENT_START - 1) and T.in_recent(T.RECENT_START)


# ---------------------------------------------------------------- stats code: planted edge, placebo, bootstrap
def _planted(seed, planted):
    n = 6000
    rng = np.random.default_rng(99)
    es = np.sort(rng.choice(np.arange(150, n - 80, 70), size=75, replace=False))
    ts, o, h, l, c = world(seed, n=n, vol=0.01, drift=0.0, plant=es if planted else (), plant_drift=-0.006)
    sigs = [(int(e) - 1, int(e) - 6, float(o[e] * 1.03)) for e in es]
    lab = np.array(["RANGE"] * n, dtype=object)
    bear = np.ones(n, bool)
    G = np.zeros(n)
    ev, _ = T.build_events("SYN", ts, o, h, l, c, bear, lab, G, None, None, sigs=sigs)
    tab = S.CoinTable(ts, o, h, l, c, bear, lab, G, None)
    return ev, tab


def test_planted_edge_is_found_and_no_drift_reads_about_zero():
    ev, tab = _planted(21, True)
    R = np.array([T.trade_R(t["gross"], T.RT_COST, 0.0, t["r"], False) for t in ev])
    wk = [T.iso_week(t["entry_ts"]) for t in ev]
    b = S.week_boot(R, wk)
    assert len(ev) >= 70 and R.mean() > 0.3 and b["lo"] > 0 and b["p_one"] < 0.01
    d, nm, nu = S.placebo_draws({"SYN": tab}, [("SYN", t["r"]) for t in ev], "VAL", ndraw=300)
    assert nm == len(ev) and nu == 0
    assert S.beats_placebo(R.mean(), d["12_nofund"]) and S.placebo_percentile(R.mean(), d["12_nofund"]) > 97.5
    ev0, tab0 = _planted(21, False)
    R0 = np.array([T.trade_R(t["gross"], T.RT_COST, 0.0, t["r"], False) for t in ev0])
    b0 = S.week_boot(R0, [T.iso_week(t["entry_ts"]) for t in ev0])
    assert abs(R0.mean()) < 0.35 and b0["lo"] < 0 < b0["hi"]
    d0, _, _ = S.placebo_draws({"SYN": tab0}, [("SYN", t["r"]) for t in ev0], "VAL", ndraw=300)
    assert not S.beats_placebo(R0.mean(), d0["12_nofund"])
    assert 2.5 < S.placebo_percentile(R0.mean(), d0["12_nofund"]) < 97.5


def test_placebo_outcome_equals_event_simulation():
    ts, o, h, l, c = world(31, n=1500, vol=0.01, drift=0.0)
    n = len(c)
    rng = np.random.default_rng(1)
    prints = [(int(ts[i]) + 10, float(x)) for i, x in zip(range(0, n, 2), rng.normal(0, 3e-4, n // 2 + 1))]
    G, first, last = T.funding_cum(ts, prints)
    lab = np.array(["RANGE"] * n, dtype=object)
    bear = np.ones(n, bool)
    es = list(range(200, 1300, 61))
    sigs = [(e - 1, e - 6, float(o[e] * 1.025)) for e in es]
    ev, _ = T.build_events("S", ts, o, h, l, c, bear, lab, G, first, last, sigs=sigs)
    tab = S.CoinTable(ts, o, h, l, c, bear, lab, G, first)
    assert len(ev) == len(es)
    for t in ev:
        g, fu = tab.outcome(np.array([t["e"]]), np.array([t["r"]]))
        assert abs(g[0] - t["gross"]) < 1e-12 and abs(fu[0] - t["fund"]) < 1e-12


def test_placebo_outcome_gap_through_trail_fills_at_open():
    n = 220
    ts = TS0 + np.arange(n, dtype=np.int64) * T.BAR
    c = np.full(n, 100.0)
    o, h, l = c.copy(), c + 0.5, c - 0.5                   # ATR stays 1: trail level 101.5
    o[150], h[150], l[150], c[150] = 110.0, 111.0, 109.0, 110.0
    lab = np.array(["RANGE"] * n, dtype=object)
    bear = np.ones(n, bool)
    G = np.zeros(n)
    tab = S.CoinTable(ts, o, h, l, c, bear, lab, G, None)
    g, fu = tab.outcome(np.array([148]), np.array([0.2]))      # stop0 = 120 is not reached; the bar gaps over the 101.5 level
    assert abs(g[0] - (-0.10)) < 1e-12
    ev, _ = T.build_events("S", ts, o, h, l, c, bear, lab, G, None, None, sigs=[(147, 142, 120.0)])
    assert abs(ev[0]["gross"] - g[0]) < 1e-12 and ev[0]["x"] == 150


def test_bootstrap_best_weeks_top_coin_baseline_hand_numbers():
    R = [3.0, 1.0, -1.0, -1.0, 0.5, 0.5]
    wk = ["A", "A", "B", "C", "D", "E"]
    m, n = S.ex_best_weeks(R, wk, k=1)                  # week A sums to 4: the rest is -1, -1, 0.5, 0.5
    assert n == 4 and abs(m - (-0.25)) < 1e-12
    best, rest, k = S.top_coin_removed([2.0, -1.0, 1.0], ["X", "Y", "Z"])
    assert best == "X" and abs(rest - 0.0) < 1e-12 and k == 2
    day = T.DAY
    coin = dict(dts=np.array([0, day, 2 * day]), close=np.array([100.0, 90.0, 99.0]), bear=np.array([True, False, True]),
                fund_day={1: 0.001})
    r, nd = S.basket_short_daily([coin], 0, 3 * day, True)
    assert nd == 1 and abs(r - (0.10 + 0.001)) < 1e-12   # day 1 counts (flag at bar 0 true); day 2 does not (flag at bar 1 false)
    r2, _ = S.basket_short_daily([coin], 0, 3 * day, False)
    assert abs(r2 - 0.10) < 1e-12


def _info(**kw):
    d = dict(val_n=200, val_weeks=60, val_mean=0.1, val_ci_lo=0.01, dev_mean=0.1, pooled_mean=0.1, val_pct=99.0, val_beats=True,
             exbest5=0.05, sig_rate=0.2, base_rate=0.1, topcoin_rest=0.05, one_year=False, val_p=0.02)
    d.update(kw)
    return d


def test_verdict_order():
    ok = {"12_nofund": _info(), "12_fund": _info()}
    assert S.verdict(ok)["verdict"] == "PASS"
    assert S.verdict({k: _info(val_n=20) for k in ok})["verdict"] == "UNDERPOWERED"
    assert S.verdict({k: _info(pooled_mean=-0.01) for k in ok})["verdict"] == "KILL"
    assert S.verdict({"12_nofund": _info(), "12_fund": _info(val_pct=80.0)})["verdict"] == "KILL"
    assert S.verdict({k: _info(val_ci_lo=-0.05) for k in ok})["verdict"] == "REPLICATED-WEAK"
    v = S.verdict({k: _info(topcoin_rest=-0.1) for k in ok})
    assert v["verdict"] == "REPLICATED-WEAK" and "FRAGILE" in v["labels"]
    assert S.verdict({k: _info(val_mean=-0.1, val_ci_lo=-0.3) for k in ok})["verdict"] == "FAIL"


def test_base_reclaim_prior_window_is_120_bars_ending_at_t_minus_60():
    n = 240
    l = np.full(n, 100.0)
    l[130] = 90.0          # inside t-179..t-60 for t = 200 (index 21..140) but NOT inside t-179..t-120 (21..80)
    rec, pri = T.base_lows(l)
    assert np.isnan(pri[:179]).all() and not np.isnan(pri[179])
    assert pri[200] == 90.0 and rec[200] == 100.0
    assert rec[200] >= pri[200] - 10
    l2 = np.full(n, 100.0)
    l2[30] = 120.0 - 40.0   # low 80 at index 30 is inside t-179..t-120 for t = 200 only if t-179 <= 30 <= t-120 -> 21..80: yes
    l2[130] = 105.0
    rec2, pri2 = T.base_lows(l2)
    assert pri2[200] == 80.0
    l3 = np.full(n, 100.0)
    l3[100] = 70.0         # index 100 is in t-179..t-60 (21..140) for t=200 but not in 21..80
    rec3, pri3 = T.base_lows(l3)
    assert pri3[200] == 70.0
    l4 = np.full(n, 100.0)
    l4[150] = 70.0         # in the recent window (141..200) only
    rec4, pri4 = T.base_lows(l4)
    assert rec4[200] == 70.0 and pri4[200] == 100.0


def test_placebo_pool_splits_by_signal_bar_like_real_trades():
    n = 400
    ts = T.VAL_START + (np.arange(n) - 200) * T.BAR
    x = np.full(n, 100.0)
    lab = np.array(["RANGE"] * n, dtype=object)
    tab = S.CoinTable(ts, x, x + 1, x - 1, x, np.ones(n, bool), lab, np.zeros(n), None)
    first_val_entry = 201                    # entry bar open = VAL_START + 1 bar; its signal bar is the first VAL bar
    dev, val = tab.pool("DEV"), tab.pool("VAL")
    assert first_val_entry in val and first_val_entry not in dev
    assert 200 in dev and 200 not in val     # entry bar opens exactly at VAL_START but its signal bar is still DEV
