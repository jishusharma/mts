import sys
sys.dont_write_bytecode = True
"""Tests for maker_model.py. Expected numbers are worked out by hand from the stated rules (module docstring), with
entry 100, stop 99, target 102 (R = 1) unless a case says otherwise; fees: taker 0.0005, maker 0, adverse bp x fill price."""
from array import array
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maker_model as M  # noqa: E402  (also puts the repo root on sys.path)
import tom_bt as T  # noqa: E402

P = M.regime_params()


def mk(bars):
    """bars: list of (o,h,l,c)."""
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for a, b, d, e in bars:
        o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    return T.Bars1m(0, o, h, l, c, v, tbv)


def run(bars, regime, side="long", entry=100.0, stop=99.0, target=102.0, fw=5, hold=3):
    return M.score_trade(mk(bars), 0, side, entry, stop, target, fw, hold, P[regime])


def test_regime_params():
    assert P["A"]["fee_entry"] == 0.0005 and P["A"]["fee_target"] == 0.0005
    assert P["B"]["fee_entry"] == 0.0 and P["B"]["fee_target"] == 0.0
    assert P["B"]["fee_stop"] == 0.0005 and P["B"]["fee_timeout"] == 0.0005
    assert P["C"]["tick"] == 0.5 and P["B"]["tick"] == 0.0
    assert P["D_1bp"]["adv_bp"] == 1.0 and P["D_0.02bp"]["adv_bp"] == 0.02


# touch fill at 100 (low == 100), target 102 touched on bar 1
TOUCH_WIN = [(100.5, 100.8, 100.0, 100.4), (100.4, 102.0, 100.3, 101.9)]


def test_touch_win_b_and_a():
    r = run(TOUCH_WIN, "B")
    assert r["status"] == "filled" and r["reason"] == "target"
    assert r["gross_r"] == pytest.approx(2.0) and r["fee_r"] == pytest.approx(0.0) and r["net_r"] == pytest.approx(2.0)
    a = run(TOUCH_WIN, "A")
    # fee_R = (0.0005*100 + 0.0005*102) / 1 = 0.05 + 0.051
    assert a["fee_r"] == pytest.approx(0.101) and a["net_r"] == pytest.approx(1.899)


def test_touch_win_adverse_cells():
    # adv_R = bp * 1e-4 * (100 + 102) / 1
    d1 = run(TOUCH_WIN, "D_1bp")
    assert d1["adv_r"] == pytest.approx(0.0202) and d1["net_r"] == pytest.approx(1.9798)
    d2 = run(TOUCH_WIN, "D_0.02bp")
    assert d2["adv_r"] == pytest.approx(0.000404) and d2["net_r"] == pytest.approx(1.999596)


def test_through_rule_makes_touch_a_non_fill_and_a_ran_away():
    # C: bar0 low 100.0 only touches (needs <= 99.5); bar1 high 102.0 reaches the target before any fill
    assert run(TOUCH_WIN, "C")["status"] == "ran"


def test_ran_away_before_fill_in_B():
    r = run([(101.0, 102.5, 100.5, 102.0)], "B")   # never trades down to 100, reaches 102
    assert r["status"] == "ran"


def test_gap_stop_fills_at_open():
    bars = [(100.5, 100.8, 99.9, 100.4), (98.0, 98.5, 97.5, 98.2)]
    b = run(bars, "B")
    assert b["reason"] == "stop" and b["gross_r"] == pytest.approx(-2.0)
    assert b["fee_r"] == pytest.approx(0.049) and b["net_r"] == pytest.approx(-2.049)   # 0.0005 * 98
    a = run(bars, "A")
    assert a["fee_r"] == pytest.approx(0.099) and a["net_r"] == pytest.approx(-2.099)    # 0.05 + 0.049


def test_fill_bar_only_checks_stop():
    r = run([(100.2, 100.3, 98.9, 99.5)], "B")   # fills at 100, same bar trades through 99
    assert r["reason"] == "stop" and r["exit_i"] == r["fill_i"] == 0
    assert r["gross_r"] == pytest.approx(-1.0) and r["net_r"] == pytest.approx(-1.0495)  # stop px min(100.2, 99) = 99


def test_stop_first_when_both_in_one_bar():
    r = run([(100.4, 100.6, 99.9, 100.4), (100.4, 102.5, 98.8, 100.0)], "B")
    assert r["reason"] == "stop" and r["gross_r"] == pytest.approx(-1.0)


def test_timeout_is_taker_at_last_close():
    bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 101.0, 100.2, 100.9), (100.9, 101.5, 100.5, 101.0)]
    b = run(bars, "B", hold=2)
    assert b["reason"] == "timeout" and b["gross_r"] == pytest.approx(1.0)
    assert b["fee_r"] == pytest.approx(0.0505) and b["net_r"] == pytest.approx(0.9495)   # 0.0005 * 101
    a = run(bars, "A", hold=2)
    assert a["fee_r"] == pytest.approx(0.1005) and a["net_r"] == pytest.approx(0.8995)


def test_through_rule_on_target_touch_does_not_fill():
    bars = [(100.2, 100.4, 99.5, 100.3), (100.3, 102.0, 100.2, 101.0), (101.0, 101.4, 100.8, 101.2)]
    b = run(bars, "B", hold=2)   # fills at 100 (low 99.5 <= 100); bar1 high 102.0 touches the target -> win
    assert b["reason"] == "target" and b["net_r"] == pytest.approx(2.0)
    c = run(bars, "C", hold=2)   # low 99.5 <= 100 - 0.5 fills; high 102.0 < 102.5 so the target is not filled; timeout at 101.2
    assert c["reason"] == "timeout" and c["gross_r"] == pytest.approx(1.2)
    assert c["fee_r"] == pytest.approx(0.0506) and c["net_r"] == pytest.approx(1.1494)  # 0.0005 * 101.2


def test_no_fill_inside_window():
    bars = [(101.0, 101.2, 100.6, 101.0)] * 3
    assert run(bars, "B", fw=3)["status"] == "no_fill"
    assert run(bars, "C", fw=3)["status"] == "no_fill"


def test_short_mirror():
    bars = [(99.5, 100.0, 99.4, 99.6), (99.6, 99.7, 98.0, 98.2)]   # high 100 touches the sell limit, low 98 touches target
    b = run(bars, "B", side="short", stop=101.0, target=98.0)
    assert b["reason"] == "target" and b["net_r"] == pytest.approx(2.0)
    a = run(bars, "A", side="short", stop=101.0, target=98.0)
    assert a["fee_r"] == pytest.approx(0.099) and a["net_r"] == pytest.approx(1.901)     # 0.05 + 0.049
    # C: high 100 < 100.5, no fill; bar1 low 98 reaches the target first
    assert run(bars, "C", side="short", stop=101.0, target=98.0)["status"] == "ran"


def test_bad_geometry():
    assert run(TOUCH_WIN, "B", stop=101.0)["status"] == "bad_geometry"


def test_agrees_with_tom_bt_for_touch_regimes():
    cases = [(TOUCH_WIN, 3), ([(100.5, 100.8, 99.9, 100.4), (98.0, 98.5, 97.5, 98.2)], 3),
             ([(100.2, 100.5, 99.9, 100.3), (100.3, 101.0, 100.2, 100.9), (100.9, 101.5, 100.5, 101.0)], 2)]
    from MyTradingSys.backtest.fees import FEES_ALL_TAKER, FEES_DERIBIT
    for bars, hold in cases:
        for reg, fees in (("A", FEES_ALL_TAKER), ("B", FEES_DERIBIT)):
            ref = T.sim_limit_trade(mk(bars), 0, "long", 100.0, 99.0, 102.0, 5, hold, fees)
            mine = run(bars, reg, hold=hold)
            assert mine["net_r"] == pytest.approx(ref["net_r"]) and mine["fee_r"] == pytest.approx(ref["fee_r"])


def test_summarize_counts():
    res = [dict(status="filled", reason="target", gross_r=2.0, fee_r=0.0, adv_r=0.0, net_r=2.0),
           dict(status="filled", reason="stop", gross_r=-1.0, fee_r=0.0495, adv_r=0.0, net_r=-1.0495),
           dict(status="ran"), dict(status="no_fill")]
    s = M.summarize(res, lambda x: (min(x), max(x)))
    assert (s["n_signals"], s["n_filled"]) == (4, 2)
    assert s["fill_rate"] == pytest.approx(0.5) and s["ran_rate"] == pytest.approx(0.25)
    assert s["gross"] == pytest.approx(0.5) and s["fee"] == pytest.approx(0.02475)
    assert s["net"] == pytest.approx(0.47525) and s["net_per_signal"] == pytest.approx(0.237625)
    assert s["target"] == pytest.approx(0.5) and s["net_ci"] == (-1.0495, 2.0)
    assert s["net_per_signal_ci"] == (-1.0495, 2.0)   # zeros for the two unfilled: min -1.0495, max 2.0
