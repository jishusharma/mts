"""Fabio v3 costs (spec 5.3) and fills (spec 5.1). Expected numbers hand-derived from the spec, T-ids in comments."""
import pytest

from MyTradingSys.backtest.layers.fabio.v3 import (FEE_MAKER, FEE_TAKER, TICK, fee_rate, find_fill, fills_in_bar,
                                                   funding_r, leg_r, missed_winner, taker_fill)


def bar(o, h, l, c):
    return {"o": o, "h": h, "l": l, "c": c}


def test_fee_constants_spec_53():                       # spec 5.3: FEE_MAKER 0.0, FEE_TAKER 0.0005
    assert FEE_MAKER == 0.0 and FEE_TAKER == 0.0005 and TICK == 0.1


def test_fee_rate_rejects_unknown_kind():
    with pytest.raises(ValueError):
        fee_rate("limit")


def test_t29_short_maker_entry_taker_stop():            # T29: net -1.16667
    r = leg_r(-1, 1.0, 100000.0, 100300.0, "maker", "taker", 300.0)
    assert r["gross_r"] == pytest.approx(-1.0)
    assert r["fee_r"] == pytest.approx(0.0005 * 100000 / 300)
    assert r["net_r"] == pytest.approx(-1.16667, abs=1e-5)


def test_t29_taker_entry_both_legs():                   # T29: taker entry -> net -1.33333
    r = leg_r(-1, 1.0, 100000.0, 100300.0, "taker", "taker", 300.0)
    assert r["net_r"] == pytest.approx(-1.33333, abs=1e-5)


def test_t29_slippage_two_bps_per_taker_leg():          # T29: 0.06667 per taker leg
    one = leg_r(-1, 1.0, 100000.0, 100300.0, "maker", "taker", 300.0, slip_bps=2.0)
    two = leg_r(-1, 1.0, 100000.0, 100300.0, "taker", "taker", 300.0, slip_bps=2.0)
    assert one["slip_r"] == pytest.approx(0.06667, abs=1e-5)
    assert two["slip_r"] == pytest.approx(0.13333, abs=1e-5)


def test_t30_maker_target_exit_has_no_exit_fee():       # T30
    r = leg_r(1, 1.0, 100.0, 101.0, "maker", "maker", 1.0)
    assert r["fee_r"] == 0.0 and r["net_r"] == pytest.approx(1.0)


def test_leg_r_rejects_zero_risk_unit():
    with pytest.raises(ValueError):
        leg_r(1, 1.0, 100.0, 101.0, "maker", "maker", 0.0)


def test_funding_counts_records_in_open_closed_interval():   # spec 5.3 / FORMULAS 13: (t_in, t_out]
    recs = [(1000, 0.0001), (2000, 0.0001), (3000, 0.0001)]
    assert funding_r(1, 1.0, 100.0, 1000, 3000, recs, 1.0) == pytest.approx(0.02)   # 2000 and 3000 only
    assert funding_r(-1, 1.0, 100.0, 1000, 3000, recs, 1.0) == pytest.approx(-0.02)  # short receives
    assert funding_r(1, 1.0, 100.0, 1000, 3000, recs, 1.0, mult=2.0) == pytest.approx(0.04)   # 2x stress


# ---- fills
def test_t27_sell_fill_through():                       # T27: sell 100: h 100.1 fills; 100.05 and 100.0 do not
    assert fills_in_bar(bar(99, 100.1, 98, 99), -1, 100.0)
    assert not fills_in_bar(bar(99, 100.05, 98, 99), -1, 100.0)
    assert not fills_in_bar(bar(99, 100.0, 98, 99), -1, 100.0)


def test_t27_buy_fill_through():                        # T27: buy 104: l 103.9 fills; 103.95 does not
    assert fills_in_bar(bar(105, 106, 103.9, 105), 1, 104.0)
    assert not fills_in_bar(bar(105, 106, 103.95, 105), 1, 104.0)


def test_t28_arming_bar_never_fills():                  # T28
    bars = [bar(100, 101, 99, 100), bar(100, 101, 99, 100)]
    assert find_fill(bars, 0, 1, 99.5) == (1, 99.5)     # fills in bar 1, not bar 0 although l[0] qualifies
    assert find_fill(bars[:1], 0, 1, 99.5) is None


def test_find_fill_respects_end_idx():
    bars = [bar(100, 101, 99, 100)] * 2 + [bar(100, 101, 95, 96)]
    assert find_fill(bars, 0, 1, 98.0, end_idx=1) is None
    assert find_fill(bars, 0, 1, 98.0) == (2, 98.0)


def test_taker_fill_is_open_of_fill_bar():              # spec 5.1: taker fill at o[j], j is the fill bar
    assert taker_fill([bar(1, 2, 0, 1), bar(5, 6, 4, 5)], 1) == (1, 5)


def test_missed_winner_reaches_p_plus_2d():             # spec 5.1: P + s*2D; long P 100, D 5 -> 110
    bars = [bar(100, 101, 99, 100), bar(100, 110.0, 99, 109)]
    assert missed_winner(bars, 1, 100.0, 5.0, 1)
    assert not missed_winner([bars[0], bar(100, 109.9, 99, 109)], 1, 100.0, 5.0, 1)
    assert missed_winner([bars[0], bar(100, 101, 90.0, 91)], -1, 100.0, 5.0, 1)   # short mirror
