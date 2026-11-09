"""Tests for first_touch.py (T04). Hand-built 15m bars; every PRE_REG rule has a case.

Day index 0 = 1970-01-01 (Thursday). Monday = day 4 (7k-3 for k=1). Bars are 15m, bar i of an array
starting at day 0 has open time i*900000 ms.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import first_touch as ft  # noqa: E402

DAY = ft.DAY
M15 = ft.M15
NB = 96  # bars per day


def build(n, default=(90.0, 95.0, 85.0, 90.0), t0_day=0, overrides=None):
    """n default bars from t0_day, overrides = {bar_index: (o,h,l,c)} (index within this array)."""
    rows = [default] * n
    rows = [list(r) for r in rows]
    for i, v in (overrides or {}).items():
        rows[i] = list(v)
    return ft.arr_from(t0_day * DAY, rows)


def test_daily_level_uses_prior_closed_day_only():
    # day 0 high max = 100 at bar 5; day 1 has a bar at 150 that must NOT leak into day 1's level.
    ov = {5: (90, 100, 80, 90), NB + 3: (90, 150, 80, 90)}
    arr = build(2 * NB + 10, overrides=ov)
    wins = [w for w in ft.windows(arr, "D") if w["fix"] == DAY]
    assert len(wins) == 1
    assert wins[0]["H"] == 100.0
    assert wins[0]["fix"] == DAY and wins[0]["end"] == 2 * DAY


def test_day_window_present_only_with_complete_prior_day():
    arr = build(NB + 5)  # day 0 present but day 1 partial; prior day for day 1 is complete (96), day 2 window partial
    starts = [w["fix"] for w in ft.windows(arr, "D")]
    assert DAY in starts  # day 0 is complete, day 1 window needs prior day 0 = complete
    assert 0 not in starts  # no prior day (day -1) in the data


def test_weekly_level_is_prior_monday_to_sunday_and_fixed_on_monday():
    # week k=0 = days -3..3 ; we build from day -3 so the Monday -3 bar is index 0.
    n = 15 * NB  # days -3 .. 11
    ov = {}
    base = 3 * NB  # index of day 0 is 3*NB (since day -3 starts index 0)
    ov[base + 10] = (90, 200, 80, 90)  # day 0 (Thu, prior week) high 200
    ov[(7 * NB) + 5 * NB] = (90, 300, 80, 90)  # day 5 (in week k=1) high 300 must not be in week k=1 level
    arr = ft.arr_from(-3 * DAY, [list(r) for r in ([(90.0, 95.0, 85.0, 90.0)] * n)])
    for i, v in ov.items():
        arr["h"][i] = v[1]
        arr["l"][i] = v[2]
    wins = [w for w in ft.windows(arr, "W") if w["fix"] == 4 * DAY]
    assert len(wins) == 1, "a Monday (day 4) week window must exist"
    assert wins[0]["H"] == 200.0
    assert wins[0]["end"] == 11 * DAY


def test_first_touch_sweep_and_reclaim_fades_short_and_repeat_is_separate():
    # level PDH = 100 (day 0 bar 5). Day 1 window starts at index 96.
    s = NB + 20  # 116 sweep bar
    ov = {
        s: (95, 105, 95, 105),       # trades beyond 100, closes outside
        s + 1: (105, 105, 95, 99),   # close back inside at s+1 = reclaim r (within 3 bars)
        150: (101, 101, 95, 101),    # second episode (repeat arm) starts
        151: (101, 101, 95, 95),     # reclaim of the repeat
    }
    arr = build(400, overrides=ov)
    # day 0 bar 5 sets the level 100 (make that bar high 100)
    arr["h"][5] = 100.0
    wins = [w for w in ft.windows(arr, "D") if w["fix"] == DAY]
    setups = ft.setups(arr, wins[0])
    first = [x for x in setups if x["arm"] == "first" and x["side"] == "H"]
    rep = [x for x in setups if x["arm"] == "repeat" and x["side"] == "H"]
    assert len(first) == 1 and first[0]["s"] == s and first[0]["r"] == s + 1
    assert first[0]["ext"] == 105.0 and first[0]["entry"] == 99.0
    assert len(rep) == 1 and rep[0]["s"] == 150 and rep[0]["r"] == 151


def test_approach_close_exactly_at_level_is_not_inside():
    s = NB + 20
    ov = {
        s - 12: (100, 100, 95, 100),  # close == level -> not strictly inside -> approach fails
        s: (95, 105, 95, 105),
        s + 1: (105, 105, 95, 99),
    }
    arr = build(400, overrides=ov)
    arr["h"][5] = 100.0
    wins = [w for w in ft.windows(arr, "D") if w["fix"] == DAY]
    first = [x for x in ft.setups(arr, wins[0]) if x["arm"] == "first" and x["side"] == "H"]
    assert first == []


def test_reclaim_after_three_bars_is_no_event():
    s = NB + 20
    ov = {s + k: (95, 105, 95, 105) for k in range(4)}  # closes outside s..s+3
    ov[s + 4] = (105, 105, 95, 99)  # reclaim at s+4 is too late
    arr = build(400, overrides=ov)
    arr["h"][5] = 100.0
    wins = [w for w in ft.windows(arr, "D") if w["fix"] == DAY]
    assert [x for x in ft.setups(arr, wins[0]) if x["arm"] == "first" and x["side"] == "H"] == []


def test_stop_at_sweep_extreme_and_stop_wins_same_bar_tie():
    s = NB + 20
    ov = {s: (95, 105, 95, 105), s + 1: (105, 105, 95, 99), s + 2: (99, 106, 86, 99)}  # bar r+1 hits stop(105) and target(87)
    arr = build(400, overrides=ov)
    arr["h"][5] = 100.0
    wins = [w for w in ft.windows(arr, "D") if w["fix"] == DAY]
    st = [x for x in ft.setups(arr, wins[0]) if x["arm"] == "first" and x["side"] == "H"][0]
    out = ft.outcome(arr, st)
    assert out["exit_kind"] == "stop"
    assert out["gross"] == pytest.approx(-1.0)


def test_target_2R_and_timeout_at_close_of_r_plus_96():
    s = NB + 20
    # target 2R = 99 - 2*6 = 87 : bar hits l=86 -> target
    ov = {s: (95, 105, 95, 105), s + 1: (105, 105, 95, 99), s + 3: (99, 99, 86, 90)}
    arr = build(400, overrides=ov)
    arr["h"][5] = 100.0
    wins = [w for w in ft.windows(arr, "D") if w["fix"] == DAY]
    st = [x for x in ft.setups(arr, wins[0]) if x["arm"] == "first" and x["side"] == "H"][0]
    out = ft.outcome(arr, st)
    assert out["exit_kind"] == "target" and out["gross"] == pytest.approx(2.0)

    # timeout: bars that neither reach stop 105 nor target 87, close at r+96 = 97
    ov2 = {s: (95, 105, 95, 105), s + 1: (105, 105, 95, 99)}
    arr2 = build(400, default=(95, 95, 92, 97), overrides=ov2)
    arr2["h"][5] = 100.0
    st2 = [x for x in ft.setups(arr2, [w for w in ft.windows(arr2, "D") if w["fix"] == DAY][0]) if x["arm"] == "first"][0]
    out2 = ft.outcome(arr2, st2)
    assert out2["exit_kind"] == "time"
    assert out2["gross"] == pytest.approx((99.0 - 97.0) / 6.0)


def test_fee_r_arithmetic_is_12bps_over_stop_fraction():
    assert ft.FEE_RT == pytest.approx(0.0012)
    assert ft.fee_r(0.01) == pytest.approx(0.12)


def test_funding_sign_short_receives_positive_rate():
    s = NB + 20
    ov = {s: (95, 105, 95, 105), s + 1: (105, 105, 95, 99), s + 3: (99, 99, 90, 92)}
    arr = build(400, default=(95, 95, 92, 97), overrides=ov)
    arr["h"][5] = 100.0
    st = [x for x in ft.setups(arr, [w for w in ft.windows(arr, "D") if w["fix"] == DAY][0]) if x["arm"] == "first"][0]
    base = ft.outcome(arr, st)
    # a +0.001 funding record inside the hold: a short receives it -> net R rises by 0.001 / stop_frac
    t_in = int(arr["t"][st["r"] + 10])
    with_f = ft.outcome(arr, st, fund=(np.array([t_in]), np.array([0.001])))
    stop_frac = 6.0 / 99.0
    assert with_f["net"] - base["net"] == pytest.approx(0.001 / stop_frac, rel=1e-9)


def test_knife_flag_fall_without_bounce():
    # 12 bars falling 3 % with no rebound, then a low sweep
    n = 400
    rows = [(100, 100.5, 99.5, 100)] * n
    s = NB + 40
    for k in range(13):
        c = 100 - 3.0 * (k / 12)
        rows[s - 13 + k] = (c, c + 0.2, c - 0.2, c)
    rows[s] = (95, 95.5, 90, 91)
    arr = ft.arr_from(0, [list(r) for r in rows])
    assert ft.knife(arr, s, "L") is True
    # same 3 % fall to 97 but with a 3-point rebound after the low -> counter-move >= 25 % -> not a knife
    path = [100, 99, 98, 97, 98, 99, 100, 99.5, 99, 98.5, 98, 97.5, 97]
    for k in range(13):
        c = float(path[k])
        rows[s - 13 + k] = (c, c + 0.2, c - 0.2, c)
    arr2 = ft.arr_from(0, [list(r) for r in rows])
    assert ft.knife(arr2, s, "L") is False


def test_split_refusal_dev_val_holdout():
    assert ft.SPLIT_END["DEV"] == ft.ms("2024-06-30") + DAY - M15
    with pytest.raises(ft.SplitViolation):
        ft.check_request("DEV", ft.ms("2024-06-01"), ft.ms("2024-07-01"))
    with pytest.raises(ft.SplitViolation):
        ft.check_request("VAL", ft.ms("2024-07-01"), ft.ms("2025-07-01"))
    with pytest.raises(ft.SplitViolation):
        ft.check_request("HOLDOUT", ft.ms("2025-07-01"), ft.ms("2025-08-01"))
    ft.check_request("DEV", ft.ms("2020-01-01"), ft.SPLIT_END["DEV"])  # inside: no raise
