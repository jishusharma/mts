"""Trade-through checks for Tom's limit entry and target legs."""
from types import SimpleNamespace

from MyTradingSys.backtest.tom_bt import sim_limit_trade


def bars(rows):
    return SimpleNamespace(
        n=len(rows),
        o=[r[0] for r in rows], h=[r[1] for r in rows],
        l=[r[2] for r in rows], c=[r[3] for r in rows],
    )


def trade(data, side, entry, stop, target, through_ticks=0):
    return sim_limit_trade(data, 0, side, entry, stop, target, 1, 1,
                           fees={"entry": 0, "target": 0, "stop": 0, "timeout": 0},
                           through_ticks=through_ticks)


def test_long_entry_touch_needs_one_tick_of_trade_through():
    touch = bars([(101, 102, 100, 101)])
    through = bars([(101, 102, 99, 100)])
    assert trade(touch, "long", 100, 95, 110)["filled"]
    assert not trade(touch, "long", 100, 95, 110, 1)["filled"]
    assert trade(through, "long", 100, 95, 110)["filled"]
    assert trade(through, "long", 100, 95, 110, 1)["filled"]


def test_short_entry_touch_needs_one_tick_of_trade_through():
    touch = bars([(99, 100, 98, 99)])
    through = bars([(99, 101, 98, 100)])
    assert trade(touch, "short", 100, 105, 90)["filled"]
    assert not trade(touch, "short", 100, 105, 90, 1)["filled"]
    assert trade(through, "short", 100, 105, 90)["filled"]
    assert trade(through, "short", 100, 105, 90, 1)["filled"]


def test_long_target_requires_trade_through_but_default_remains_touch():
    data = bars([(100, 101, 99, 100), (105, 110, 100, 108)])
    args = (data, "long", 100, 90, 110)
    assert trade(*args)["reason"] == "target"
    assert trade(*args, through_ticks=1)["reason"] == "timeout"


def test_short_target_requires_trade_through_but_default_remains_touch():
    data = bars([(100, 101, 99, 100), (90, 100, 90, 92)])
    args = (data, "short", 100, 110, 90)
    assert trade(*args)["reason"] == "target"
    assert trade(*args, through_ticks=1)["reason"] == "timeout"


def test_target_touch_before_entry_only_cancels_after_trade_through_threshold():
    long_data = bars([(105, 110, 101, 105)])  # no entry touch; target touched, not through by one
    short_data = bars([(95, 99, 90, 95)])
    assert trade(long_data, "long", 100, 90, 110)["reason"] == "ran"
    assert trade(long_data, "long", 100, 90, 110, 1)["reason"] == "no_fill"
    assert trade(short_data, "short", 100, 110, 90)["reason"] == "ran"
    assert trade(short_data, "short", 100, 110, 90, 1)["reason"] == "no_fill"


def test_zero_through_ticks_is_output_identical_to_default():
    data = bars([(100, 101, 99, 100), (100, 111, 99, 110)])
    args = (data, 0, "long", 100, 90, 110, 1, 1)
    assert sim_limit_trade(*args) == sim_limit_trade(*args, through_ticks=0)
