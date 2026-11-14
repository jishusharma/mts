"""Synthetic-bar tests for T11 (core + stats). No data cache, no files outside the repo.
Run: python -m pytest test_t11_core.py   (or python -m unittest test_t11_core)
Weekly bars are NOT used by T11 (daily breadth), so the weekly-resample Sunday-spike test of the shared rules does not
apply; the equivalent daily look-ahead test (future bars cannot change a signal through t) is test_no_lookahead_*.
"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t11_core as core  # noqa: E402
import t11_stats as st  # noqa: E402

DAY = 86400000
RT_HAND = 12 / 10000.0          # hand number: 12 bp round trip (2 x 5 bp taker + 2 bp slippage)


def eday(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


def rows_from(closes, start, r=0.01, over=None):
    over = over or {}
    out = []
    for i, c in enumerate(closes):
        o = closes[i - 1] if i else c
        row = (o, max(o, c) * (1 + r), min(o, c) * (1 - r), c)
        row = over.get(i, row)
        out.append(((start + i) * DAY,) + tuple(row))
    return np.array(out, float)


def mk(closes, start=None, over=None, r=0.01, name="SYN", ended=False):
    start = eday(2023, 1, 1) if start is None else start
    rows = rows_from(closes, start, r, over)
    pull = rows[-1, 0] + (400 * DAY if ended else DAY)
    return core.Coin(name, rows, pull_ms=int(pull))


# ------------------------------------------------------------------ indicators
def test_rsi_hand_values():
    c = [10, 11, 10, 12, 13, 12, 14]
    r = core.rsi_wilder(c, 3)
    assert np.all(np.isnan(r[:3]))
    assert abs(r[3] - 75.0) < 1e-9                              # gains (1,0,2)/3 = 1, losses (0,1,0)/3 = 1/3
    assert abs(r[4] - (100 - 100 / (1 + 4.5))) < 1e-9          # ag 1, al 2/9, rs 4.5
    assert core.rsi_wilder([5.0] * 10, 3)[5] == 50.0           # flat -> 50 (FORMULAS.md)
    assert core.rsi_wilder(list(range(1, 12)), 3)[5] == 100.0   # only gains -> 100


def test_atr_hand_value():
    h = np.array([11.0, 12.0, 13.0]); l = np.array([9.0, 10.0, 11.0]); c = np.array([10.0, 11.0, 12.0])
    a = core.wilder_atr(h, l, c, 3)
    # TR0 = 2 (own close as previous), TR1 = max(2, |12-10|, |10-10|) = 2, TR2 = max(2, 2, 0) = 2
    assert abs(a[2] - 2.0) < 1e-12


# ------------------------------------------------------------------ events, episodes, states
def test_event_gap_rule():
    nan = float("nan")
    b = [0.0] * 7 + [0.2, 0.3, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.16]
    # event at 7 (7 days below before), no event at 8 (already above), 13 has only 3 days below -> no, 20 has >= 7 below
    ev = core.find_events(b)
    assert ev == [7, 20], ev
    assert core.find_events([nan] * 7 + [0.2]) == [7]           # undefined days count as below
    assert core.find_events([0.14] * 7 + [0.15]) == [7]         # >= 15% includes exactly 15%
    assert core.find_events([0.14] * 6 + [0.15, 0.15]) == []    # fewer than 7 prior days: none


def test_merge_episodes_14_day_chain():
    assert core.merge_episodes([0, 8, 22, 40]) == [0, 0, 0, 1]   # gaps 8, 14 merge (14 inclusive), 18 splits
    assert core.merge_episodes([0, 15]) == [0, 1]
    assert core.merge_episodes([0, 14, 28, 42]) == [0, 0, 0, 0]  # chain: each within 14 of the previous


def test_smooth_state_ten_days():
    raw = ["BASE"] * 5 + ["BEAR"] * 9 + ["BASE"] + ["BEAR"] * 10
    sm = core.smooth_state(raw)
    assert sm[:5] == ["BASE"] * 5
    assert sm[5:14] == ["BASE"] * 9                              # 9 BEAR days: prior holds
    assert sm[14] == "BASE"                                      # interruption resets the count
    assert sm[15:24] == ["BASE"] * 9 and sm[24] == "BEAR"        # adopted on the 10th consecutive day, not earlier


def test_sma_flag_strict_and_causal():
    c = [1.0] * 199 + [2.0, 0.5]
    f = core.sma_flag(c, 200)
    assert np.all(np.isnan(f[:199]))
    assert f[199] == 1.0 and f[200] == 0.0                       # 2.0 > mean(1x199, 2) ; 0.5 below
    assert core.sma_flag([1.0] * 200, 200)[199] == 0.0           # equal is not above


def test_split_boundary():
    assert st.split_of_day(eday(2023, 12, 31)) == "DEV"
    assert st.split_of_day(eday(2024, 1, 1)) == "VAL"


# ------------------------------------------------------------------ synthetic market
def synth_market(seed=3, ncoin=35, n=900, crash_days=(), edge=0.0, start=None):
    """Random-walk coins with a common factor; at each crash day all coins lose ~22% in one day, then `edge` per day
    for 10 days (planted drift). Returns (Market, funds)."""
    rs = np.random.RandomState(seed)
    start = eday(2023, 1, 1) if start is None else start
    common = rs.normal(0, 0.01, n)
    drift = np.zeros(n)
    for cd in crash_days:
        common[cd] -= 0.25
        drift[cd + 1:cd + 11] += edge
    coins = []
    for k in range(ncoin):
        ret = common + drift + rs.normal(0, 0.02, n)
        closes = 100 * np.exp(np.cumsum(ret))
        coins.append(mk(list(closes), start=start, name="C%02d" % k))
    return core.Market(coins), {}


CRASHES = tuple(range(260, 880, 55))                            # about 11 crashes, spaced > 14 days


def run_synth(edge, seed=3):
    mkt, funds = synth_market(seed=seed, crash_days=CRASHES, edge=edge)
    legs = st.make_legs(mkt, funds, lambda d: "BASE", lambda d: 1.0)
    pools = st.pool_entries(mkt, funds, lambda d: "BASE")
    st.assign_episodes(legs)
    return legs, st.run_cell(legs, pools, nboot=400, ndraw=200)


def test_no_lookahead_breadth_events_and_legs():
    mkt, funds = synth_market(seed=4, crash_days=CRASHES, edge=0.0)
    ev = core.find_events(mkt.breadth)
    assert len(ev) >= 5
    T = ev[3] + 1
    cut = [core.Coin(c.name, np.column_stack([c.ms[:T + 1], c.o[:T + 1], c.h[:T + 1], c.l[:T + 1], c.c[:T + 1]]))
           for c in mkt.coins]
    m2 = core.Market(cut)
    assert np.allclose(m2.breadth[:T + 1], mkt.breadth[:T + 1], equal_nan=True)
    assert core.find_events(m2.breadth[:T + 1]) == [e for e in ev if e <= T]
    # signal flags and the entry price of the legs of event ev[3] do not depend on anything after the signal bar
    s_full = core.leg_signals(mkt, ev[3])
    # change every bar after the signal bar except the entry open: legs and RSI flags are identical
    pert = []
    for c in mkt.coins:
        a = np.column_stack([c.ms, c.o, c.h, c.l, c.c]).copy()
        a[ev[3] + 1:, 2:] *= 1.37                                # future highs/lows/closes changed (open of t+1 kept)
        pert.append(core.Coin(c.name, a))
    m3 = core.Market(pert)
    s_pert = core.leg_signals(m3, ev[3])
    assert [(s["coin"], s["entry"]) for s in s_full] == [(s["coin"], s["entry"]) for s in s_pert]


def test_entry_is_next_open_and_rsi_filter():
    mkt, funds = synth_market(seed=5, crash_days=CRASHES)
    ev = core.find_events(mkt.breadth)
    d = ev[2]
    for s in core.leg_signals(mkt, d):
        c = mkt.coins[s["ci"]]
        t_loc = mkt.dmin + d - c.day0
        assert s["d0"] == t_loc + 1 and s["entry"] == c.o[t_loc + 1]
        assert mkt.rsi[s["ci"], d] <= 35.0 and mkt.alive[s["ci"], d]
    # a coin with RSI > 35 is never in the legs
    names = {s["coin"] for s in core.leg_signals(mkt, d)}
    for i, c in enumerate(mkt.coins):
        if mkt.alive[i, d] and mkt.rsi[i, d] > 35.0:
            assert c.name not in names


def test_alive_needs_200_bars():
    c = mk(list(100 + np.arange(250) * 0.5))
    m = core.Market([c])
    assert not m.alive[0, 198] and m.alive[0, 199]


# ------------------------------------------------------------------ simulator
def flat_coin(n=40, price=100.0, over=None, ended=False, name="SYN"):
    closes = [price] * n
    return mk(closes, over=over, r=0.0, name=name, ended=ended)


def test_stop_wins_ties_and_gap():
    # entry open = 100 at bar 5, stop 8% -> 92. bar 8 low 91 but close 110: stop wins, fill at 92.
    over = {8: (100.0, 111.0, 91.0, 110.0)}
    c = flat_coin(over=over)
    r = core.simulate_leg(c, 5, 0.08)
    assert r["exit_reason"] == "STOP" and abs(r["gross"] - (-0.08)) < 1e-12 and r["days_held"] == 4
    assert abs(r["net_R"] - (-0.08 - RT_HAND) / 0.08) < 1e-9
    # same on the very last day of the window (day 10 = bar 14)
    c = flat_coin(over={14: (100.0, 120.0, 90.0, 115.0)})
    r = core.simulate_leg(c, 5, 0.08)
    assert r["exit_reason"] == "STOP" and r["days_held"] == 10 and abs(r["gross"] + 0.08) < 1e-12
    # gap through the stop: open 85 fills at 85
    c = flat_coin(over={7: (85.0, 90.0, 84.0, 88.0)})
    r = core.simulate_leg(c, 5, 0.08)
    assert r["exit_reason"] == "STOP-GAP" and abs(r["gross"] + 0.15) < 1e-12
    # low exactly at the stop counts as a hit
    c = flat_coin(over={6: (100.0, 101.0, 92.0, 100.0)})
    assert core.simulate_leg(c, 5, 0.08)["exit_reason"] == "STOP"
    # no hit: time exit at the close of day 10 (bar 14), 10 days
    c = flat_coin(over={14: (100.0, 106.0, 99.0, 105.0)})
    r = core.simulate_leg(c, 5, 0.08)
    assert r["exit_reason"] == "TIME" and r["days_held"] == 10 and abs(r["gross"] - 0.05) < 1e-12


def test_fee_arithmetic_from_fees_py():
    import fees
    assert abs(core.FEE_RT - (2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13)) < 1e-15
    assert abs(core.FEE_RT - RT_HAND) < 1e-15
    c = flat_coin(over={14: (100.0, 106.0, 99.0, 105.0)})
    r = core.simulate_leg(c, 5, 0.10)
    assert abs(r["net"] - (0.05 - RT_HAND)) < 1e-12 and abs(r["fee_R"] - RT_HAND / 0.10) < 1e-12
    assert abs(r["net_R"] - (0.05 - RT_HAND) / 0.10) < 1e-12 and abs(r["gross_R"] - 0.5) < 1e-12


def test_funding_window_and_not_in_data():
    c = flat_coin(over={14: (100.0, 106.0, 99.0, 105.0)})
    e_ms = int(c.ms[5])
    end_ms = int(c.ms[14]) + DAY
    # prints: exactly at entry (excluded), inside (included x2), exactly at end (included), after end (excluded)
    ts = [e_ms - 8 * 3600000, e_ms, e_ms + 8 * 3600000, e_ms + 16 * 3600000, end_ms, end_ms + 8 * 3600000]
    rt = [0.5, 0.01, 0.002, -0.001, 0.003, 0.9]
    f = core.Funding(ts, rt)
    r = core.simulate_leg(c, 5, 0.10, f)
    assert abs(r["funding"] - (0.002 - 0.001 + 0.003)) < 1e-12 and r["funding_rule"] == "REAL"
    assert abs(r["net"] - (0.05 - RT_HAND - 0.004)) < 1e-12
    # funding that does not cover the window: NOT_IN_DATA, zero, no imputation
    f2 = core.Funding([e_ms + 8 * 3600000], [0.01])
    r2 = core.simulate_leg(c, 5, 0.10, f2)
    assert r2["funding_rule"] == "NOT_IN_DATA" and r2["funding"] == 0.0
    r3 = core.simulate_leg(c, 5, 0.10, None)
    assert r3["funding_rule"] == "NOT_IN_DATA"
    # stop exit charges funding only to the end of the stop day
    c2 = flat_coin(over={7: (100.0, 101.0, 90.0, 95.0), 14: (100.0, 101.0, 99.0, 100.0)})
    ts = [e_ms - 3600000, e_ms + 8 * 3600000, int(c2.ms[7]) + DAY - 8 * 3600000, int(c2.ms[9]), int(c2.ms[14]) + DAY]
    f3 = core.Funding(ts, [0.7, 0.001, 0.002, 0.5, 0.0])
    r4 = core.simulate_leg(c2, 5, 0.08, f3)
    assert r4["exit_reason"] == "STOP" and abs(r4["funding"] - 0.003) < 1e-12


def test_window_incomplete_ended_and_holes():
    c = flat_coin(n=12)                                          # entry at bar 5 needs bar 14: incomplete, still trading
    assert core.simulate_leg(c, 5, 0.08) is None
    c = flat_coin(n=12, ended=True)
    r = core.simulate_leg(c, 5, 0.08)
    assert r["exit_reason"] == "ENDED-EXIT" and r["days_held"] == 7 and r["ended"]
    # LUNA hole: a leg overlapping 2022-05-13..31 is dropped, a coin with another name is not
    start = eday(2022, 5, 1)
    closes = [100.0] * 60
    assert core.simulate_leg(mk(closes, start=start, name="LUNA", r=0.0), 5, 0.08) is None
    assert core.simulate_leg(mk(closes, start=start, name="ABC", r=0.0), 5, 0.08) is not None
    ft = core.HOLES["FTT"]
    assert ft == (eday(2022, 11, 15), eday(2023, 9, 22))


def test_stop_distance_floor_and_atr():
    mkt, funds = synth_market(seed=6, crash_days=CRASHES)
    d = core.find_events(mkt.breadth)[1]
    for s in core.leg_signals(mkt, d):
        assert s["pct"] >= 0.08 - 1e-12                          # floor 8%, hence fee in R <= 0.015
        c = mkt.coins[s["ci"]]
        t_loc = mkt.dmin + d - c.day0
        assert abs(s["dist"] - max(2.5 * c.atr[t_loc], 0.08 * s["entry"])) < 1e-9


def test_placebo_path_is_same_code_as_real_leg():
    c = flat_coin(over={8: (100.0, 111.0, 91.0, 110.0)})
    P = core.path_arrays(c, [5, 6], None)
    o = core.outcome_vec(P, 0.08)
    r = core.simulate_leg(c, 5, 0.08)
    assert abs(o["net_R"][0] - r["net_R"]) < 1e-12 and o["k_exit"][0] == r["days_held"] - 1


# ------------------------------------------------------------------ statistics
def test_bootstrap_planted_and_null():
    rs = np.random.RandomState(1)
    planted = list(rs.normal(1.0, 0.5, 15))
    b = st.boot(planted)
    assert b["ci_low"] > 0 and b["p_le0"] < 0.01
    null = list(rs.normal(0.0, 0.5, 15))
    b0 = st.boot(null)
    assert b0["ci_low"] < 0 < b0["ci_high"] and abs(b0["mean"]) < 0.4


def test_holm_and_dose_and_strata():
    h = st.holm({"a": 0.01, "b": 0.04})
    assert abs(h["a"] - 0.02) < 1e-12 and abs(h["b"] - 0.04) < 1e-12
    legs = []
    for i, (b, v) in enumerate([(0.2, -1.0), (0.4, 0.0), (0.6, 1.0)]):
        legs.append(dict(sig_day=eday(2024, 3, 1) + 30 * i, B=b, net_R=v, ep=i, above=float(i % 2)))
    dr = st.dose_response(legs)
    assert dr["testable"] and dr["monotone"]
    legs[2]["net_R"] = -2.0
    assert not st.dose_response(legs)["monotone"]
    sp = st.strata_prediction([dict(sig_day=1, net_R=0.5, above=1.0, ep=0), dict(sig_day=2, net_R=-0.2, above=0.0, ep=1)])
    assert sp["holds"] and not sp["flipped"]


def test_planted_edge_is_detected_end_to_end():
    legs, S = run_synth(edge=0.02)
    v = S["VAL"]
    assert v["episodes"] >= 8 and v["net_R"] > 0 and v["boot_episode"]["ci_low"] > 0
    pb = S["placebo"]["VAL_pri_window"]
    assert pb["n_legs"] > 0 and pb["real"] > pb["p975"] and pb["excess"] > 0
    assert S["bars"]["2_val_mean_gt0_and_episode_ci_low_gt0"] and S["bars"]["4_placebo_primary_window"]
    assert S["verdict"] != "UNDERPOWERED"


def test_no_edge_reads_about_zero():
    legs, S = run_synth(edge=0.0)
    v = S["VAL"]
    assert v["episodes"] >= 8
    assert abs(v["net_R"]) < 0.6                                 # fee and noise only
    assert v["boot_episode"]["ci_low"] < 0 < v["boot_episode"]["ci_high"] or v["net_R"] <= 0.3
    assert S["verdict"] in ("FAIL", "NOT-A-PASS", "FRAGILE")


def test_underpowered_never_fail():
    legs, S = run_synth(edge=0.0)
    few = [l for l in legs if l["ep"] < 3 or l["split"] == "DEV"]
    # keep only 3 VAL episodes
    val_eps = sorted({l["ep"] for l in legs if l["split"] == "VAL"})[:3]
    few = [l for l in legs if l["split"] == "DEV" or l["ep"] in val_eps]
    mkt, funds = synth_market(seed=3, crash_days=CRASHES, edge=0.0)
    pools = st.pool_entries(mkt, funds, lambda d: "BASE")
    st.assign_episodes(few)
    S2 = st.run_cell(few, pools, nboot=200, ndraw=100)
    assert S2["VAL"]["episodes"] == 3 and S2["verdict"] == "UNDERPOWERED"
    assert not any(S2["kill"].values())


def test_mutation_stop_not_wins_ties_is_detected():
    """Mutation check: a simulator that lets the close rescue a stopped bar must fail the tie test above."""
    c = flat_coin(over={8: (100.0, 111.0, 91.0, 110.0)})
    r = core.simulate_leg(c, 5, 0.08)
    mutated_gross = 110.0 / 100.0 - 1.0                          # the wrong (close-rescues) outcome
    assert abs(r["gross"] - mutated_gross) > 0.1


def test_episode_assignment_and_split_follow_first_event():
    legs = [dict(sig_day=eday(2023, 12, 25), net_R=1.0, iso_week="a", coin="X"),
            dict(sig_day=eday(2024, 1, 5), net_R=3.0, iso_week="b", coin="Y"),
            dict(sig_day=eday(2024, 3, 1), net_R=5.0, iso_week="c", coin="X")]
    st.assign_episodes(legs)
    assert legs[0]["ep"] == legs[1]["ep"] != legs[2]["ep"]
    assert legs[0]["split"] == legs[1]["split"] == "DEV" and legs[2]["split"] == "VAL"
    assert st.ep_means(legs) == {legs[0]["ep"]: 2.0, legs[2]["ep"]: 5.0}
