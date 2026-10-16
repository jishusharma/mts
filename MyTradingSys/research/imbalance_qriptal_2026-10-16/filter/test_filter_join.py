"""Spec-derived tests for filter_join.py (PRE_REG.md sections 2-4). Expected numbers are worked by hand, not read from the code.

Hand-built level trades and imbalance candles: no market data, no F:/ access (CI runners have none). Run: python -m pytest test_filter_join.py
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filter_join as F  # noqa: E402

HOUR = 3_600_000
DAY = 86_400_000
T0 = 100 * DAY


def tab(rows):
    """Candle table from (start, tf_ms, mid, rv, bf) rows; the join reads only these columns."""
    return pd.DataFrame([{"start": s, "end": s + ms, "mid": m, "rv": rv, "bf": bf} for s, ms, m, rv, bf in rows])


EMPTY = tab([])
TABLES_1H = tab([
    (T0 + 8 * HOUR, HOUR, 100.1, 1.0, 0.20),    # C: normal volume, small body (control shape)
    (T0 + 9 * HOUR, HOUR, 100.0, 3.0, 0.10),    # A: volume anomaly, small body
    (T0 + 10 * HOUR, HOUR, 100.0, 3.0, 0.80),   # B: volume anomaly, large body
])


def tabs(one_h=None, four_h=None):
    return {"1h": TABLES_1H if one_h is None else one_h, "4h": EMPTY if four_h is None else four_h, "12h": EMPTY, "1d": EMPTY}


# ---------------------------------------------------------------- the join (imbalance candle at the level, causal)
def test_join_only_closed_candles_count():
    # touch at 10:30: A (09-10) closed, B (10-11) still forming -> small yes, large no
    f = F.imbalance_flags(tabs(), T0 + 10 * HOUR + 30 * 60_000, 100.0, 2.0)
    assert f["small"] is True and f["large"] is False
    # touch exactly at 11:00: B closed at that instant -> large yes
    f = F.imbalance_flags(tabs(), T0 + 11 * HOUR, 100.0, 2.0)
    assert f["large"] is True
    # touch at 09:30: A is still forming and B not started -> no anomaly candle at all
    f = F.imbalance_flags(tabs(), T0 + 9 * HOUR + 30 * 60_000, 100.0, 2.0)
    assert f["small"] is False and f["large"] is False


def test_join_control_shape_has_normal_volume_only():
    # C (rv 1.0, body .2, mid 100.1) is within 0.25 % of 100.0 -> ctrl yes; A and B never count as ctrl (rv 3)
    f = F.imbalance_flags(tabs(), T0 + 10 * HOUR + 30 * 60_000, 100.0, 2.0)
    assert f["ctrl"] is True
    only_a = tab([(T0 + 9 * HOUR, HOUR, 100.0, 3.0, 0.10)])
    assert F.imbalance_flags(tabs(only_a), T0 + 10 * HOUR + 30 * 60_000, 100.0, 2.0)["ctrl"] is False
    # rv exactly 1.2 is not "normal" (< 1.2 required)
    edge = tab([(T0 + 9 * HOUR, HOUR, 100.0, 1.2, 0.10)])
    assert F.imbalance_flags(tabs(edge), T0 + 10 * HOUR, 100.0, 2.0)["ctrl"] is False


def test_join_level_must_sit_at_candle_midpoint():
    t = T0 + 10 * HOUR + 30 * 60_000
    assert F.imbalance_flags(tabs(), t, 100.2, 2.0)["small"] is True      # |100-100.2|/100.2 = 0.1996 % <= 0.25 %
    assert F.imbalance_flags(tabs(), t, 100.26, 2.0)["small"] is False    # 0.2594 % > 0.25 %
    assert F.imbalance_flags(tabs(), t, 101.0, 2.0)["small"] is False     # 0.99 %


def test_join_volume_and_body_thresholds():
    t = T0 + 12 * HOUR
    for rv, bf, small, large in [(1.99, 0.10, False, False), (2.0, 0.10, True, False),     # k = 2: >= 2.0 flags
                                 (3.0, 0.30, True, False), (3.0, 0.31, False, False),       # body <= 0.30 small
                                 (3.0, 0.69, False, False), (3.0, 0.70, False, True),       # body >= 0.70 large
                                 (float("nan"), 0.10, False, False), (3.0, float("nan"), False, False)]:
        f = F.imbalance_flags(tabs(tab([(T0 + 9 * HOUR, HOUR, 100.0, rv, bf)])), t, 100.0, 2.0)
        assert (f["small"], f["large"]) == (small, large), (rv, bf)
    # k = 3 on rv 2.5
    f = F.imbalance_flags(tabs(tab([(T0 + 9 * HOUR, HOUR, 100.0, 2.5, 0.10)])), t, 100.0, 3.0)
    assert f["small"] is False


def test_join_lookback_window():
    one = tab([(T0, HOUR, 100.0, 3.0, 0.10)])
    assert F.imbalance_flags(tabs(one), T0 + 7 * DAY, 100.0, 2.0)["small"] is True              # opened exactly 7 d before: in
    assert F.imbalance_flags(tabs(one), T0 + 7 * DAY + 60_000, 100.0, 2.0)["small"] is False    # 1 minute older: out


def test_join_union_over_timeframes():
    four = tab([(T0, 4 * HOUR, 200.0, 2.5, 0.25)])
    f = F.imbalance_flags(tabs(four_h=four), T0 + 12 * HOUR, 200.0, 2.0)
    assert f["small"] is True and f["small_tf"] == {"1h": False, "4h": True, "12h": False, "1d": False}
    assert F.imbalance_flags(tabs(four_h=four), T0 + 12 * HOUR, 200.0, 3.0)["small"] is False


def test_attach_flags_on_hand_built_trades():
    trades = pd.DataFrame({"t": [T0 + 10 * HOUR + 30 * 60_000, T0 + 11 * HOUR, T0 + 10 * HOUR + 30 * 60_000],
                           "level": [100.0, 100.0, 101.0]})
    out = F.attach_flags(trades, tabs(), 2.0)
    assert out["small"].tolist() == [True, True, False]
    assert out["large"].tolist() == [False, True, False]
    assert len(out) == 3 and "t" in out and "level" in out


# ---------------------------------------------------------------- layer trade: side, touch, bracket, cost
def test_fade_side_uses_previous_close():
    assert F.fade_side(105.0, 100.0) == 1      # came from above: support, long
    assert F.fade_side(95.0, 100.0) == -1      # came from below: resistance, short
    assert F.fade_side(100.0, 100.0) == 0


def test_width_is_lc1_stop_width():
    assert F.stop_width_for(100_000.0, 99_000.0) == pytest.approx(400.0)     # 0.4 % of the open
    assert F.stop_width_for(10_000.0, 100_000.0) == pytest.approx(100.0)     # 0.1 % of the level wins


def test_day_complete_gate():
    assert F.day_complete(1440, 1440) and not F.day_complete(1399, 1440) and not F.day_complete(1440, 1399)


def test_first_touch_and_side_from_previous_bar():
    t = np.arange(5) * 60_000
    o = np.array([102.0, 101.6, 101.0, 100.2, 99.0])
    h = np.array([102.5, 101.9, 101.2, 100.5, 99.5])
    l = np.array([101.5, 101.0, 100.4, 99.8, 98.5])
    c = np.array([101.6, 101.1, 100.5, 100.0, 99.0])
    ev = F.first_touch(t, o, h, l, c, 100.0, prev_close=102.0)
    assert ev == {"idx": 3, "t": 3 * 60_000, "side": 1}      # bar 3 is the first with low <= 100 <= high; bar 2 close 100.5 is above
    # level exactly at a bar's low counts as a touch
    assert F.first_touch(t, o, h, l, c, 101.0, prev_close=102.0)["idx"] == 1
    # never touched
    assert F.first_touch(t, o, h, l, c, 110.0, prev_close=102.0) is None
    # touch on the first bar of the day: side from the previous day's close
    ev0 = F.first_touch(t, o, h, l, c, 102.2, prev_close=99.0)
    assert ev0["idx"] == 0 and ev0["side"] == -1
    # previous close equal to the level on the touch bar: ambiguous side, no trade
    assert F.first_touch(t, o, h, l, c, 102.2, prev_close=102.2) is None


def test_touch_bar_close_does_not_set_the_side():
    # same bars except the touch bar's close flips from below to above the level: the side must not change
    t = np.arange(3) * 60_000
    o = np.array([101.0, 100.6, 100.0]); h = np.array([101.5, 100.9, 100.4]); l = np.array([100.5, 100.2, 99.0])
    base = F.first_touch(t, o, h, l, np.array([100.8, 100.5, 99.5]), 100.0, prev_close=101.0)
    flip = F.first_touch(t, o, h, l, np.array([100.8, 100.5, 100.3]), 100.0, prev_close=101.0)
    assert base["side"] == flip["side"] == 1 and base["idx"] == flip["idx"] == 2


def bar(o, h, l, c):
    return o, h, l, c


def run_bracket(side, level, width, rr, bars):
    a = np.array(bars, dtype=float)
    return F.bracket(side, level, width, rr, a[:, 0], a[:, 1], a[:, 2], a[:, 3])


def test_bracket_long_target_ignores_touch_bar_move():
    # touch bar reaches 101.2 (>= target 101) but that may precede the fill: not credited; bar 2 hits the target
    bars = [bar(100.5, 101.2, 99.5, 100.8), bar(100.8, 100.9, 100.1, 100.5), bar(100.5, 101.0, 100.4, 100.9)]
    assert run_bracket(1, 100.0, 1.0, 1.0, bars) == (101.0, "target")
    # a target move that exists ONLY in the touch bar earns nothing: the trade runs to the time exit
    bars = [bar(100.5, 101.2, 99.5, 100.8), bar(100.8, 100.9, 100.1, 100.5)]
    assert run_bracket(1, 100.0, 1.0, 1.0, bars) == (100.5, "time")
    bars = [bar(99.5, 100.4, 98.7, 99.2), bar(99.2, 99.6, 99.1, 99.4)]      # short mirror: low 98.7 <= target 99 in the touch bar only
    assert run_bracket(-1, 100.0, 1.0, 1.0, bars) == (99.4, "time")


def test_bracket_stop_first_when_one_bar_holds_both():
    bars = [bar(100.5, 100.8, 99.5, 100.2), bar(100.2, 101.5, 98.9, 100.0)]
    assert run_bracket(1, 100.0, 1.0, 1.0, bars) == (99.0, "stop")


def test_bracket_stop_inside_the_touch_bar():
    assert run_bracket(1, 100.0, 1.0, 1.0, [bar(100.5, 101.2, 98.5, 100.0)]) == (99.0, "stop")


def test_bracket_gap_through_stop_fills_at_open():
    bars = [bar(100.5, 100.8, 99.5, 100.2), bar(98.5, 99.0, 98.0, 98.8)]
    assert run_bracket(1, 100.0, 1.0, 1.0, bars) == (98.5, "stop")


def test_bracket_gap_through_target_fills_at_target():
    bars = [bar(100.5, 100.8, 99.5, 100.2), bar(101.5, 102.0, 101.4, 101.8)]
    assert run_bracket(1, 100.0, 1.0, 1.0, bars) == (101.0, "target")


def test_bracket_time_exit_at_last_close():
    bars = [bar(100.5, 100.8, 99.5, 100.2), bar(100.2, 100.9, 99.6, 100.3)]
    assert run_bracket(1, 100.0, 1.0, 1.0, bars) == (100.3, "time")


def test_bracket_short_mirror_rr2():
    bars = [bar(99.5, 100.2, 99.0, 99.4), bar(99.4, 99.6, 97.9, 98.1)]
    assert run_bracket(-1, 100.0, 1.0, 2.0, bars) == (98.0, "target")        # stop 101, target 98
    bars = [bar(99.5, 100.2, 99.0, 99.4), bar(101.4, 101.6, 101.0, 101.2)]
    assert run_bracket(-1, 100.0, 1.0, 2.0, bars) == (101.4, "stop")         # gap above the stop fills at the open


def test_net_r_by_hand():
    # long, level 100, W = 0.4, exit at the 1R target 100.4: gross 1; taker cost 0.0007 x (100 + 100.4) / 0.4 = 0.3507; net 0.6493
    g, c, n = F.net_r(1, 100.0, 0.4, 100.4)
    assert g == pytest.approx(1.0) and c == pytest.approx(0.3507) and n == pytest.approx(0.6493)
    # maker entry: 0.0002 x 100 + 0.0007 x 100.4 = 0.09028 -> 0.2257 R
    g, c, n = F.net_r(1, 100.0, 0.4, 100.4, maker_in=True)
    assert c == pytest.approx(0.2257) and n == pytest.approx(0.7743)
    # short stopped at 100.4: gross -1, cost 0.3507, net -1.3507
    g, c, n = F.net_r(-1, 100.0, 0.4, 100.4)
    assert g == pytest.approx(-1.0) and n == pytest.approx(-1.3507)


def test_dedup_same_price_is_one_trade():
    rows = [{"family": "prior_day_poc", "price": 100.0}, {"family": "naked_poc", "price": 100.0}, {"family": "round_1000", "price": 101.0}]
    out = F.dedup_levels(rows)
    assert [r["price"] for r in out] == [100.0, 101.0]
    assert out[0]["family"] == "prior_day_poc|naked_poc"


# ---------------------------------------------------------------- candles from 1m, DEV guard
def test_candle_table_from_1m():
    n_h = 60
    t = T0 + np.arange(n_h * 60) * 60_000
    v = np.ones(len(t))
    v[55 * 60:56 * 60] = 3.0                              # hour 55: volume 3 per minute
    o = np.full(len(t), 100.0); h = np.full(len(t), 100.5); l = np.full(len(t), 99.5); c = np.full(len(t), 100.0)
    o[55 * 60] = 100.0; c[56 * 60 - 1] = 100.2; h[55 * 60 + 7] = 105.0; l[55 * 60 + 9] = 95.0
    df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})
    tb = F.candle_table(df, "1h")
    assert len(tb) == 60
    assert tb["rv"].iloc[:50].isna().all()
    r = tb.iloc[55]
    assert r["start"] == T0 + 55 * HOUR and r["end"] == T0 + 56 * HOUR
    assert r["rv"] == pytest.approx(3.0)                  # 180 / median(60 x 50 hours) = 3
    assert r["bf"] == pytest.approx(0.02)                 # |100.2 - 100.0| / (105 - 95)
    assert r["mid"] == pytest.approx(100.0)


def test_dev_guard():
    names = ["BTCUSDT-1m-2022-01.csv", "BTCUSDT-1m-2024-06.csv", "BTCUSDT-1m-2024-07.csv", "BTCUSDT-1m-2026-09.csv", "readme.txt"]
    assert F.dev_month_files(names) == ["BTCUSDT-1m-2022-01.csv", "BTCUSDT-1m-2024-06.csv"]
    F.assert_dev(np.array([F.DEV_END_MS - 60_000]))
    with pytest.raises(ValueError):
        F.assert_dev(np.array([F.DEV_END_MS]))


# ---------------------------------------------------------------- levels in blocks equal a long window, and stay causal
def synth_days(n_days, seed=7):
    rng = np.random.default_rng(seed)
    n = n_days * 1440
    close = 20_000 + np.cumsum(rng.normal(0, 8, n))
    open_ = np.concatenate(([20_000.0], close[:-1]))
    hi = np.maximum(open_, close) + rng.uniform(0, 6, n)
    lo = np.minimum(open_, close) - rng.uniform(0, 6, n)
    vol = rng.uniform(1, 10, n)
    return pd.DataFrame({"t": np.arange(n) * 60_000 + 50 * DAY, "o": open_, "h": hi, "l": lo, "c": close, "v": vol})


def test_level_blocks_equal_one_long_window():
    df = synth_days(30)
    d0 = int(df.t.iloc[0] // DAY)
    first = d0 + 17
    got = F.levels_blocks(df, first, d0 + 29, F.KEEP, block=5)
    full = F.lv.levels_by_day([{"t": int(r.t), "o": r.o, "h": r.h, "l": r.l, "c": r.c, "v": r.v} for r in df.itertuples()])
    for d in range(first, d0 + 30):
        a = sorted((x["family"], x["price"]) for x in full[d] if x["family"] in F.KEEP)
        b = sorted((x["family"], x["price"]) for x in got[d])
        assert a == b and len(a) > 0, d


def test_levels_do_not_read_the_day_itself():
    df = synth_days(30)
    d0 = int(df.t.iloc[0] // DAY)
    d = d0 + 25
    base = F.levels_blocks(df, d, d, F.KEEP, block=1)[d]
    mut = df.copy()
    m = mut.t >= d * DAY
    mut.loc[m, ["o", "h", "l", "c"]] = [50_000.0, 60_000.0, 40_000.0, 55_000.0]
    mut.loc[m, "v"] = 999.0
    assert F.levels_blocks(mut, d, d, F.KEEP, block=1)[d] == base


# ---------------------------------------------------------------- statistics and the pre-registered decisions
def test_stats_day_clustered():
    s = F.stats([1.0, -1.0, 0.5, 0.5], [1, 1, 2, 2])
    # mean .25; day sums of deviations: day1 (0.75 - 1.25) = -0.5, day2 (0.25 + 0.25) = 0.5; se = sqrt(0.25 + 0.25) / 4
    assert s["n"] == 4 and s["days"] == 2
    assert s["mean"] == pytest.approx(0.25) and s["se"] == pytest.approx(math.sqrt(0.5) / 4)
    assert s["t"] == pytest.approx(0.25 / (math.sqrt(0.5) / 4))


def h1(**kw):
    base = dict(n_imb=500, n_noimb=900, days_imb=300, mean_imb=0.05, t_imb=2.5, delta=0.30, p_holm=0.01,
                delta_h1=0.2, delta_h2=0.4, mean_ctrl=-0.10, mde=0.10)
    base.update(kw)
    return F.decide_h1(base)


def test_decide_h1_branches():
    assert h1() == ("PASS", "")
    assert h1(mean_imb=-0.05, t_imb=-1.0) == ("FAIL", "filter lifts")           # lifts, layer still loses to costs
    assert h1(delta=-0.01, p_holm=0.9)[0] == "FAIL" and h1(delta=-0.01, p_holm=0.9)[1] == "no lift"
    assert h1(delta_h2=-0.1) == ("FAIL", "no lift")                              # not stable across halves
    assert h1(mean_ctrl=0.20) == ("FAIL", "no lift")                              # shape-only control does as well: (e) fails; label per PRE_REG: lifts needs (b) to fail
    assert h1(mean_ctrl=float("nan"))[0] == "FAIL"
    assert h1(n_imb=199)[0] == "INCONCLUSIVE"                                    # n gate
    assert h1(days_imb=99)[0] == "INCONCLUSIVE"
    assert h1(delta=-0.01, p_holm=0.9, mde=0.20)[0] == "INCONCLUSIVE"            # a FAIL below the power bar reads INCONCLUSIVE
    assert h1(t_imb=1.99)[0] == "FAIL"


def h2(**kw):
    base = dict(n_large=400, delta=-0.30, p_holm=0.01, delta_h1=-0.2, delta_h2=-0.4, mde=0.10)
    base.update(kw)
    return F.decide_h2(base)


def test_decide_h2_branches():
    assert h2() == ("PASS", "")
    assert h2(delta=0.05, p_holm=0.8)[0] == "FAIL"
    assert h2(delta_h1=0.01)[0] == "FAIL"
    assert h2(n_large=199)[0] == "INCONCLUSIVE"
    assert h2(delta=0.05, p_holm=0.8, mde=0.2)[0] == "INCONCLUSIVE"


def test_holm_over_m16():
    p = F.holm_p([0.001, 0.02], m=16)
    assert p[0] == pytest.approx(0.016) and p[1] == pytest.approx(0.30)         # 16 x .001, then max(.016, 15 x .02)


# ---------------------------------------------------------------- end to end on a synthetic tape (independent reference simulation)
def ref_trade(side, level, width, rr, o, h, l, c):
    """Slow bar-by-bar reference written from the PRE_REG exit rules, not from filter_join.bracket."""
    stop, target = level - side * width, level + side * rr * width
    for j in range(len(h)):
        hit_stop = (l[j] <= stop) if side > 0 else (h[j] >= stop)
        hit_tgt = j > 0 and ((h[j] >= target) if side > 0 else (l[j] <= target))
        if hit_stop:
            gap = j > 0 and ((o[j] <= stop) if side > 0 else (o[j] >= stop))
            return (o[j] if gap else stop), "stop"
        if hit_tgt:
            return target, "target"
    return c[-1], "time"


def test_build_events_and_simulate_on_synthetic_tape():
    df = synth_days(30)
    d0 = int(df.t.iloc[0] // DAY)
    ev, skips = F.build_events(df, first_day=d0 + 17, last_day=d0 + 29, block=5)
    assert len(ev) > 20 and skips["incomplete_day"] == 0 and skips["touched"] == len(ev)
    assert set(ev["side"]) <= {1, -1} and (ev["width"] > 0).all()
    assert not ev.duplicated(["day", "level"]).any()                       # one trade per level and day
    o, h, l, c, t = (df[x].to_numpy() for x in ("o", "h", "l", "c", "t"))
    for r in ev.itertuples():
        a = int(np.searchsorted(t, r.day * DAY))
        assert l[r.gidx] <= r.level <= h[r.gidx] and t[r.gidx] == r.t
        assert not ((l[a:r.gidx] <= r.level) & (r.level <= h[a:r.gidx])).any()      # first touch of the day
        assert r.side == (1 if c[r.gidx - 1] > r.level else -1)                      # side from the bar before
        assert r.eidx == int(np.searchsorted(t, (r.day + 1) * DAY))
        assert r.width == pytest.approx(max(0.004 * o[a], 0.001 * r.level))
    sim = F.simulate(ev, df, rrs=(1.0, 2.0))
    for rr in (1.0, 2.0):
        for r in sim.itertuples():
            i, e = r.gidx, r.eidx
            px, kind = ref_trade(r.side, r.level, r.width, rr, o[i:e], h[i:e], l[i:e], c[i:e])
            row = sim.loc[r.Index]
            assert row[f"exit_{rr:g}"] == pytest.approx(px) and row[f"kind_{rr:g}"] == kind
            assert row[f"net_{rr:g}"] == pytest.approx(r.side * (px - r.level) / r.width - 0.0007 * (r.level + px) / r.width)
            assert row[f"net_m_{rr:g}"] == pytest.approx(r.side * (px - r.level) / r.width - (0.0002 * r.level + 0.0007 * px) / r.width)
    assert set(sim["kind_1"]) <= {"stop", "target", "time"}


def test_run_filter_smoke_on_synthetic_tape(tmp_path):
    """The two commands run end to end on a synthetic tape: counts has no outcome column, run writes RESULT.md and refuses a second run."""
    import run_filter as R
    df = synth_days(30)
    d0 = int(df.t.iloc[0] // DAY)
    R.counts(df=df, out=tmp_path, first_day=d0 + 17, last_day=d0 + 29, block=5)
    ev = pd.read_csv(tmp_path / "events_dev.csv")
    assert len(ev) > 20 and (tmp_path / "COUNTS.md").exists()
    assert not any(c.startswith(("net", "gross", "exit", "kind", "cost")) for c in ev.columns)
    R.run(df=df, out=tmp_path)
    res = (tmp_path / "RESULT.md").read_text(encoding="utf-8")
    assert res.splitlines()[0] in ("PASS", "FAIL", "INCONCLUSIVE") and "## Verdict arms" in res and "Declared trial count" in res
    assert (tmp_path / "trades_dev.csv").exists() and (tmp_path / "trials.csv").exists()
    with pytest.raises(SystemExit):
        R.run(df=df, out=tmp_path)
