"""Wiring tests for wt_extreme_cross_2026-11 (hand arithmetic, never read back from study.py):
extreme-cross detection at -50 / +40, DEV guard (a post-DEV bar raises SplitViolation), bounce/drop excursion math,
fee-net, day-type tags (ex-post same day vs as-of prior day), and as-of causality of the cross."""
import importlib.util
import random
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from MyTradingSys.backtest import splits  # noqa: E402

_spec = importlib.util.spec_from_file_location("wt_extreme_cross_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

DAY = 86400000
MIN = 60000


def test_cross_events_and_dev_guard():
    # wt1 below wt2 on bars 0,1; bar 2 wt1 = -52 > wt2 = -55: up-cross at -52 <= -50 -> buy at i=2
    assert study.extreme_crosses([-70, -60, -52, -40], [-55, -55, -55, -55]) == [(2, 1)]
    # up-cross at -48 is outside the -50 zone: no event
    assert study.extreme_crosses([-70, -60, -48, -40], [-50, -50, -50, -50]) == []
    # down-cross at +41 >= 40 -> sell; at +39 no event (asymmetric zones, card thresholds)
    assert study.extreme_crosses([60, 50, 41, 30], [45, 45, 45, 45]) == [(2, -1)]
    assert study.extreme_crosses([60, 50, 39, 30], [42, 42, 42, 42]) == []
    # bible variant -60: the -52 cross no longer counts
    assert study.extreme_crosses([-70, -60, -52, -40], [-55, -55, -55, -55], buy_lvl=-60.0) == []
    # DEV guard: last bar before DEV_END passes, a bar at DEV_END (VALIDATION) raises
    end = study.ms(splits.DEV_END)
    study.dev_guard([{"t": study.ms(splits.DEV_START)}, {"t": end - MIN}])
    with pytest.raises(splits.SplitViolation):
        study.dev_guard([{"t": study.ms(splits.DEV_START)}, {"t": end}])
    with pytest.raises(splits.SplitViolation):
        study.dev_guard([{"t": study.ms(splits.DEV_START) - MIN}, {"t": end - MIN}])


def test_outcome_excursion_and_fee_net():
    bars = [{"t": k * MIN, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for k in range(30)]
    bars[3].update(h=106.0, l=97.0)       # within bars 1..4 after entry bar 0: best high 106, worst low 97
    bars[4].update(c=103.0)
    o = study.outcome(bars, 0, 1, k=4)
    assert abs(o["mfe"] - 6.0) < 1e-9 and abs(o["mae"] - 3.0) < 1e-9 and abs(o["ret"] - 3.0) < 1e-9
    assert abs(o["pts"] - 6.0) < 1e-9
    assert abs(o["net"] - (3.0 - study.COST)) < 1e-9
    s = study.outcome(bars, 0, -1, k=4)    # short from 100: drop to 97 = +3 %, adverse 106 = 6 %, close 103 = -3 %
    assert abs(s["mfe"] - 3.0) < 1e-9 and abs(s["mae"] - 6.0) < 1e-9 and abs(s["ret"] + 3.0) < 1e-9
    assert study.outcome(bars, 27, 1, k=4) is None     # no full window after the entry: dropped, not padded


def test_day_type_ex_post_and_prior_day_as_of():
    # day 0: open 100, close 107, range 110-100 = 10 -> |7|/10 = 0.7 >= 0.6 trend; day 1: open 107 close 106, range 4 -> range
    bars = []
    for k in range(1440):
        bars.append({"t": k * MIN, "o": 100.0 + 7 * k / 1439, "h": 100.0 + 7 * k / 1439, "l": 100.0 + 7 * k / 1439,
                     "c": 100.0 + 7 * k / 1439})
    bars[500].update(h=110.0)
    for k in range(1440):
        bars.append({"t": DAY + k * MIN, "o": 107.0, "h": 107.0, "l": 107.0, "c": 107.0})
    bars[1440 + 10].update(h=109.0, l=105.0)
    bars[-1].update(c=106.0)
    types = study.day_types(bars)
    assert types == {0: "trend", 1: "range"}
    # as-of tag of an event on day 1 = day 0's type; on day 0 there is no prior day
    assert study.prior_day_type(types, DAY + 5 * MIN) == "trend"
    assert study.prior_day_type(types, 5 * MIN) is None
    assert study.same_day_type(types, DAY + 5 * MIN) == "range"


def _bars(n, shock=None):
    rnd = random.Random(7)
    out, c = [], 100.0
    for k in range(n):
        c = c * (1 + rnd.gauss(0, 0.004))
        out.append({"t": k * MIN, "o": c, "h": c * 1.001, "l": c * 0.999, "c": c})
    if shock is not None:
        out.append({"t": n * MIN, "o": shock, "h": shock, "l": shock, "c": shock})
    return out


def test_events_ignore_future_bars():
    base = study.events_for(_bars(3000), "1m")
    more = study.events_for(_bars(3000, shock=1.0), "1m")
    assert len(base) >= 5
    assert [e for e in more if e["i"] < 3000] == base
    assert all(e["t_close"] == e["i"] * MIN + MIN for e in base)
