"""Hand-built bars for every rule of eh-s2-wick-level-context (T09 long, T10 short).

Scenario S1 (Monday 2024-01-01, flat price 100, volume 10, 15m bars, 96 per day):
  week 1 (Jan 1-7): low 90 on Jan 2 12:00, high 106 on Jan 3 12:00  -> prior-week low 90 / high 106 for week 2
  Jan 9 12:00 high 105                                              -> prior-day high 105 on Jan 10
  sweep bar s = Jan 10 12:00: low 85, close 91, volume 40 (4x the median 10)
  fill bar s+1 (low 89 < 90), +1R bar s+2 (high 96 >= 95), target bar s+3 (high 106 > 105)
  entry 90, stop 85, R = 5, target 105 = 3R -> gross +3.0 R, maker exit, fee 0.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wick_context as wc  # noqa: E402

BAR = 900_000
T0 = int(pd.Timestamp("2024-01-01").timestamp() * 1000)


def flat(days, price=100.0, vol=10.0, t0=T0):
    n = days * 96
    return {"t": t0 + np.arange(n, dtype=np.int64) * BAR, "o": np.full(n, price), "h": np.full(n, price),
            "l": np.full(n, price), "c": np.full(n, price), "v": np.full(n, vol)}


def ix(day, hh=0, mm=0):
    return day * 96 + hh * 4 + mm // 15


def setbar(b, i, o=None, h=None, l=None, c=None, v=None):
    cur = {k: b[k][i] for k in "ohlcv"}
    for k, x in zip("ohlcv", (o, h, l, c, v)):
        if x is not None:
            cur[k] = x
    cur["h"] = max(cur["h"], cur["o"], cur["c"], cur["l"])
    cur["l"] = min(cur["l"], cur["o"], cur["c"], cur["h"])
    for k in "ohlcv":
        b[k][i] = cur[k]


def cut(b, n):
    return {k: v[:n].copy() for k, v in b.items()}


def mirror(b, pivot=200.0):
    return {"t": b["t"].copy(), "o": pivot - b["o"], "h": pivot - b["l"], "l": pivot - b["h"], "c": pivot - b["c"],
            "v": b["v"].copy()}


S = ix(9, 12)  # sweep bar index in S1


def s1(days=16, fill=True):
    b = flat(days)
    setbar(b, ix(1, 12), l=90.0)
    setbar(b, ix(2, 12), h=106.0)
    setbar(b, ix(8, 12), h=105.0)
    setbar(b, S, o=100.0, l=85.0, c=91.0, v=40.0)
    if fill:
        setbar(b, S + 1, o=91.0, h=92.0, l=89.0, c=90.5)
        setbar(b, S + 2, o=90.5, h=96.0, l=90.5, c=95.0)
        setbar(b, S + 3, o=95.0, h=106.0, l=95.0, c=105.0)
    return b


def run(b, sg=1, **kw):
    ev = wc.find_events(b, sg)
    tr, fn = wc.simulate(b, ev, sg, **kw)
    return ev, tr, fn


# ---------------------------------------------------------------- level, sweep, target, payoff
def test_week_level_sweep_fill_target_win():
    ev, tr, fn = run(s1())
    assert len(ev) == 1
    e = ev[0]
    assert e["ltype"] == "week" and e["s"] == S and e["r"] == S and e["price_level"] == 90.0
    assert e["ext_price"] == 85.0 and e["target_price"] == 105.0 and abs(e["target_r"] - 3.0) < 1e-9
    assert len(tr) == 1
    t = tr[0]
    assert t["kind"] == "target" and t["fill_idx"] == S + 1 and t["exit_idx"] == S + 3
    assert abs(t["gross_r"] - 3.0) < 1e-9 and t["fee_r"] == 0.0 and t["fund_r"] == 0.0
    assert abs(t["net_r"] - 3.0) < 1e-9
    assert fn["orders"] == 1 and fn["filled"] == 1


def test_break_even_at_plus_1r_then_stopped_at_entry():
    b = s1()
    setbar(b, S + 3, o=95.0, h=96.0, l=90.0, c=91.0)  # low == entry: break-even stop trades
    _, tr, _ = run(b)
    t = tr[0]
    assert t["kind"] == "be" and t["exit_idx"] == S + 3 and t["gross_r"] == 0.0
    assert abs(t["fee_r"] - 6.0 / (5.0 / 90.0 * 1e4)) < 1e-9


def test_be_trigger_bar_itself_does_not_stop_at_entry():
    b = s1()
    setbar(b, S + 2, o=90.5, h=96.0, l=89.5, c=95.0)  # +1R and back through entry in one bar: BE armed from the next bar
    _, tr, _ = run(b)
    assert tr[0]["kind"] == "target" and tr[0]["exit_idx"] == S + 3


def test_stop_at_sweep_extreme_before_plus_1r():
    b = s1()
    setbar(b, S + 2, o=90.5, h=91.0, l=84.0, c=86.0)
    _, tr, _ = run(b)
    t = tr[0]
    assert t["kind"] == "stop" and t["gross_r"] == -1.0 and t["exit_idx"] == S + 2
    assert abs(t["fee_r"] - 6.0 / (5.0 / 90.0 * 1e4)) < 1e-9
    assert abs(t["net_r"] - (-1.0 - t["fee_r"])) < 1e-9


def test_stop_wins_tie_on_fill_bar():
    b = s1()
    setbar(b, S + 1, o=91.0, h=106.0, l=84.0, c=100.0)  # fills, reaches the stop and the target in one bar
    _, tr, _ = run(b)
    assert tr[0]["kind"] == "stop" and tr[0]["gross_r"] == -1.0 and tr[0]["exit_idx"] == S + 1


def test_stop_wins_tie_with_target_on_later_bar():
    b = s1()
    setbar(b, S + 3, o=95.0, h=106.0, l=85.0, c=100.0)  # target and stop (not yet BE... BE armed) in one bar
    _, tr, _ = run(b)
    assert tr[0]["kind"] == "be" and tr[0]["gross_r"] == 0.0  # the break-even stop beats the target in the same bar


def test_fill_needs_strictly_lower_low():
    b = s1(fill=False)
    setbar(b, S + 1, l=90.0)  # touches, does not trade through
    ev, tr, fn = run(b)
    assert len(ev) == 1 and tr == [] and fn["unfilled"] == 1 and fn["orders"] == 1


def test_order_lives_four_bars():
    b = s1(fill=False)
    setbar(b, S + 4, o=91.0, l=89.0, c=90.5)
    _, tr, fn = run(b)
    assert fn["filled"] == 1 and tr[0]["fill_idx"] == S + 4
    b2 = s1(fill=False)
    setbar(b2, S + 5, o=91.0, l=89.0, c=90.5)
    _, tr2, fn2 = run(b2)
    assert tr2 == [] and fn2["unfilled"] == 1 and fn2["filled"] == 0


def test_time_stop_at_fill_plus_96_closes_at_the_close():
    b = s1(fill=False)
    setbar(b, S + 1, o=91.0, h=92.0, l=89.0, c=90.5)
    for i in range(S + 2, len(b["t"])):
        for k in "ohlc":
            b[k][i] = 92.0
    _, tr, _ = run(b)
    t = tr[0]
    assert t["kind"] == "timeout" and t["exit_idx"] == S + 1 + 96
    assert abs(t["gross_r"] - (92.0 - 90.0) / 5.0) < 1e-9
    assert abs(t["fee_r"] - 6.0 / (5.0 / 90.0 * 1e4)) < 1e-9


def test_open_trade_at_end_of_data_is_dropped_and_counted():
    b = cut(s1(), S + 3)  # last bar is +1R bar; no exit yet
    _, tr, fn = run(b)
    assert tr == [] and fn["unresolved"] == 1


# ---------------------------------------------------------------- first touch, reclaim window
def test_no_reclaim_within_3_bars_kills_the_level_for_good():
    b = s1(fill=False)
    setbar(b, S, c=88.0)
    setbar(b, S + 1, o=88.0, l=87.0, c=88.0)
    setbar(b, S + 2, o=88.0, l=87.0, c=88.0)
    setbar(b, S + 3, o=88.0, l=87.0, c=88.0)  # 4th bar closing back above would be too late
    setbar(b, S + 3, o=88.0, c=95.0)
    assert wc.find_events(b, 1) == []
    setbar(b, S + 10, o=100.0, l=80.0, c=95.0, v=40.0)  # a later "perfect" sweep of the same, already touched level
    assert wc.find_events(b, 1) == []


def test_reclaim_on_third_bar_counts_and_extreme_spans_sweep_bars():
    b = s1(fill=False)
    setbar(b, S, c=88.0)
    setbar(b, S + 1, o=88.0, l=84.0, c=89.0)
    setbar(b, S + 2, o=89.0, l=88.0, c=91.0)
    ev = wc.find_events(b, 1)
    assert len(ev) == 1 and ev[0]["r"] == S + 2 and ev[0]["s"] == S and ev[0]["ext_price"] == 84.0


def test_first_touch_dead_after_an_earlier_pass_below_the_level():
    b = s1(fill=False)
    setbar(b, ix(9, 2), o=100.0, l=89.0, c=95.0)  # earlier bar traded below 90 first (a reclaiming wick, volume 10)
    ev = wc.find_events(b, 1)
    assert len(ev) == 1 and ev[0]["s"] == ix(9, 2)  # the earlier bar IS the first touch; bar S is not an event
    assert all(e["s"] != S for e in ev)


# ---------------------------------------------------------------- effort, knife, target size
def test_volume_gate_is_3x_median_and_can_be_dropped():
    b = s1()
    setbar(b, S, v=25.0)
    ev, tr, fn = run(b)
    assert ev[0]["vol_ok"] is False and abs(ev[0]["vol_ratio"] - 2.5) < 1e-9
    assert tr == [] and fn["vol_fail"] == 1
    _, tr2, _ = run(b, vol_gate=False)
    assert len(tr2) == 1
    setbar(b, S, v=30.0)
    ev3, tr3, _ = run(b)
    assert ev3[0]["vol_ok"] is True and len(tr3) == 1  # exactly 3.0x passes


def test_knife_helper_numbers():
    # straight fall 100 -> 92.8 with no bounce: knife
    hi = [100 - 0.6 * j for j in range(12)]
    lo = [h - 0.6 for h in hi]
    assert wc.is_knife(hi, lo) is True
    # fall of 1 % only: not a knife however clean
    assert wc.is_knife([100, 99.8, 99.6, 99.4], [99.8, 99.6, 99.4, 99.0]) is False
    # 7 % fall with a bounce of 3 (> 25 % of the fall): not a knife
    hi2 = [100, 97, 94, 97, 95, 93]
    lo2 = [98, 95, 93, 94, 93, 92]
    assert wc.is_knife(hi2, lo2) is False
    # H on the last bar: counter-move 0, fall = H - L (the same bar): bar range only
    assert wc.is_knife([100, 100, 100, 103], [100, 100, 100, 100]) is False


def test_knife_veto_end_to_end():
    b = s1()
    for j in range(12):
        o = 100.0 - 0.6 * j
        setbar(b, S - 12 + j, o=o, h=o, l=o - 0.6, c=o - 0.6)
    ev, tr, fn = run(b)
    assert ev[0]["knife"] is True and tr == [] and fn["knife_veto"] == 1


def test_target_under_2_5r_is_skipped_and_counted():
    b = s1()
    setbar(b, ix(8, 12), h=100.0)  # prior-day high 100 = 2R from entry 90 / stop 85
    ev, tr, fn = run(b)
    assert abs(ev[0]["target_r"] - 2.0) < 1e-9
    assert tr == [] and fn["target_lt"] == 1 and fn["orders"] == 0


def test_nearest_above_helper():
    assert wc.nearest_above(90.0, [105.0, 100.0, 80.0, 90.0]) == 100.0
    assert wc.nearest_above(90.0, [80.0, 90.0]) is None
    assert wc.nearest_above(90.0, []) is None


# ---------------------------------------------------------------- mirror, month, pivot
def test_short_mirror_has_the_same_gross_r():
    b = mirror(s1())
    ev, tr, _ = run(b, sg=-1)
    assert len(ev) == 1 and ev[0]["ltype"] == "week" and ev[0]["price_level"] == 110.0 and ev[0]["ext_price"] == 115.0
    assert tr[0]["kind"] == "target" and abs(tr[0]["gross_r"] - 3.0) < 1e-9 and tr[0]["side"] == -1


def test_prior_month_level():
    b = flat(45)
    setbar(b, ix(1, 12), l=90.0)  # January low
    s = ix(40, 12)  # Feb 10
    setbar(b, s, o=100.0, l=85.0, c=91.0, v=40.0)
    ev = wc.find_events(b, 1)
    assert len(ev) == 1 and ev[0]["ltype"] == "month" and ev[0]["price_level"] == 90.0


def test_pivot_low_confirmed_only_after_the_right_side_closes():
    b = flat(20)
    setbar(b, ix(7, 12), l=90.0)  # Jan 8 (Monday): pivot day, 5 flat days each side
    s = ix(13)  # Jan 14 00:00 = first bar after the right side (days 8..12) closed
    setbar(b, s, o=100.0, l=85.0, c=91.0, v=40.0)
    ev = wc.find_events(b, 1)
    pv = [e for e in ev if e["ltype"] == "pivot"]
    assert len(pv) == 1 and pv[0]["price_level"] == 90.0 and pv[0]["s"] == s
    # one bar earlier is still inside the right side: no pivot level exists yet
    b2 = flat(20)
    setbar(b2, ix(7, 12), l=90.0)
    setbar(b2, ix(12, 12), o=100.0, l=85.0, c=91.0, v=40.0)  # day 12 low 85 < 90 -> also not a pivot (not strict)
    assert [e for e in wc.find_events(b2, 1) if e["ltype"] == "pivot"] == []


def test_pivot_tie_is_not_a_pivot():
    b = flat(20)
    setbar(b, ix(7, 12), l=90.0)
    setbar(b, ix(9, 12), l=90.0)
    setbar(b, ix(13), o=100.0, l=85.0, c=91.0, v=40.0)
    assert [e for e in wc.find_events(b, 1) if e["ltype"] == "pivot"] == []


def test_incomplete_first_period_gives_no_level():
    b = flat(16, t0=T0 + 5 * 96 * BAR)  # starts Saturday Jan 6: the first week is partial
    setbar(b, ix(0, 12), l=90.0)
    setbar(b, ix(5, 12), o=100.0, l=85.0, c=91.0, v=40.0)  # Jan 11, in the week after the partial one (Jan 8-14)... prior week partial
    assert wc.find_events(b, 1) == []


# ---------------------------------------------------------------- one position, window start
def test_one_position_at_a_time_and_start_filter():
    b = s1()
    ev = wc.find_events(b, 1)
    dup = dict(ev[0])
    dup["r"] = ev[0]["r"] + 1
    dup["t_r"] = ev[0]["t_r"] + BAR
    tr, fn = wc.simulate(b, ev + [dup], 1)
    assert len(tr) == 1 and fn["busy"] == 1
    tr2, fn2 = wc.simulate(b, ev, 1, start_ms=int(b["t"][S]) + BAR)
    assert tr2 == [] and fn2["orders"] == 0


# ---------------------------------------------------------------- fees, funding, R arithmetic
def test_cost_bps_regimes_and_fee_r():
    assert wc.exit_cost_bps("target", "B") == 0.0
    for k in ("stop", "be", "timeout"):
        assert wc.exit_cost_bps(k, "B") == 6.0  # 5 bps taker (fees.FEES_DERIBIT) + 1 bp slippage
        assert wc.exit_cost_bps(k, "A") == 12.0  # 5 + 5 taker + 2 bps round-trip slippage
    assert wc.exit_cost_bps("target", "A") == 12.0
    assert abs(wc.fee_r(6.0, 90.0, 5.0) - 6.0 / (5.0 / 90.0 * 1e4)) < 1e-12


def test_regime_a_charges_the_target_leg_too():
    _, tr, _ = run(s1(), regime="A")
    assert abs(tr[0]["fee_r"] - 12.0 / (5.0 / 90.0 * 1e4)) < 1e-9


def test_funding_long_pays_short_receives():
    b = s1()
    settle = int(b["t"][S + 2])
    tr, _ = wc.simulate(b, wc.find_events(b, 1), 1, funding=[(settle, 0.0001)])
    assert abs(tr[0]["fund_r"] - 0.0001 / (5.0 / 90.0)) < 1e-9
    assert abs(tr[0]["net_r"] - (3.0 - tr[0]["fund_r"])) < 1e-9
    m = mirror(b)
    tr2, _ = wc.simulate(m, wc.find_events(m, -1), -1, funding=[(settle, 0.0001)])
    assert abs(tr2[0]["fund_r"] + 0.0001 / (5.0 / 110.0)) < 1e-9
    tr3, _ = wc.simulate(b, wc.find_events(b, 1), 1, funding=[(int(b["t"][S + 10]), 0.0001)])
    assert tr3[0]["fund_r"] == 0.0  # settlement after the exit


# ---------------------------------------------------------------- no lookahead, splits, regime tag
@pytest.mark.parametrize("sg", [1, -1])
def test_prefix_no_lookahead_on_noisy_bars(sg):
    rng = np.random.default_rng(7)
    n = 150 * 96
    ret = rng.normal(0, 0.004, n)
    c = 100 * np.exp(np.cumsum(ret))
    o = np.concatenate(([100.0], c[:-1]))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.003, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.003, n)))
    v = np.exp(rng.normal(0, 0.8, n)) * 10
    b = {"t": T0 + np.arange(n, dtype=np.int64) * BAR, "o": o, "h": h, "l": l, "c": c, "v": v}
    full = wc.find_events(b, sg)
    assert len(full) >= 3
    k = 100 * 96

    def key(e):
        return (e["s"], e["r"], round(e["price_level"], 9), e["ltype"], round(e["ext_price"], 9),
                None if e["target_price"] is None else round(e["target_price"], 9), e["vol_ok"], e["knife"])

    part = wc.find_events(cut(b, k), sg)
    a = sorted(key(e) for e in full if e["r"] < k)
    p = sorted(key(e) for e in part if e["r"] < k)
    assert a == p and len(a) >= 1
    # changing the future never changes the past
    b2 = {kk: vv.copy() for kk, vv in b.items()}
    b2["l"][k:] *= 0.5
    b2["h"][k:] *= 1.5
    again = sorted(key(e) for e in wc.find_events(b2, sg) if e["r"] < k)
    assert again == a


def _write_klines(folder, rows):
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "BTCUSDT-15m-x.csv", "w", newline="\n") as f:
        for t, px in rows:
            f.write(f"{t},{px},{px},{px},{px},10,{t + BAR - 1},1,1,5,1,0\n")


def test_loader_refuses_bars_past_the_split_end_and_the_holdout(tmp_path):
    ts = lambda s: int(pd.Timestamp(s).timestamp() * 1000)  # noqa: E731
    rows = [(ts("2024-06-30 23:45"), 1.0), (ts("2024-07-01 00:00"), 2.0), (ts("2025-06-30 23:45"), 3.0),
            (ts("2025-07-01 00:00"), 4.0), (ts("2025-07-02 00:00"), 5.0)]
    _write_klines(tmp_path / "klines", rows)
    dev = wc.load_bars(tmp_path, "DEV")
    assert dev["t"].max() < ts("2024-07-01")
    val = wc.load_bars(tmp_path, "VALIDATION")
    assert val["t"].max() == ts("2025-06-30 23:45") and len(val["t"]) == 3
    with pytest.raises(wc.splits.SplitViolation):
        wc.load_bars(tmp_path, "HOLDOUT")
    with pytest.raises(wc.splits.SplitViolation):
        wc.load_bars(tmp_path, "DEV", end_ms=ts("2025-01-01"))
    with pytest.raises(wc.splits.SplitViolation):
        wc.check_bars_in_split({"t": np.array([ts("2025-07-01")])}, "VALIDATION")
    with pytest.raises(wc.splits.SplitViolation):
        wc.load_funding_split(tmp_path, "HOLDOUT")


def test_regime_tags_of_a_long_uptrend():
    n = 1800
    rng = np.random.default_rng(3)
    c = 100 * np.exp(np.cumsum(rng.normal(0.006, 0.015, n)))
    t_open = int(pd.Timestamp("2018-01-01").timestamp() * 1000) + np.arange(n, dtype=np.int64) * 86_400_000
    weeks = [int(pd.Timestamp("2022-06-06").timestamp() * 1000) + k * 7 * 86_400_000 for k in range(8)]
    tags = wc.regime_tags(t_open, c, weeks)
    assert len(tags) == 8 and all(x in ("bull", "bear", "range", None) for x in tags)
    assert any(x == "bull" for x in tags)
    early = wc.regime_tags(t_open, c, [t_open[10]])
    assert early == [None]  # no 200-day average and no monthly RSI yet: NOT_IN_DATA, never invented
    assert wc.regime_mix_text(["bull", "range", None, "range"]).startswith("4 weeks")


def test_rsi14_wilder_reference_values():
    c = np.array([44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28,
                  46.28, 46.00, 46.03, 46.41, 46.22, 45.64])
    r = wc.rsi14(c)
    assert np.isnan(r[:14]).all()
    assert abs(r[14] - 70.46) < 0.1  # classic Wilder worked example
