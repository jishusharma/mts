"""Tests for slippage.py (card gap-g7-stop-slippage). Expected numbers are hand-computed here, not from slippage.py."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import pytest
import slippage as S

T = np.array([0, 100, 200, 400, 1500, 1700], np.int64)


def test_first_trade_beyond_gap_up():
    p = np.array([29990.0, 29995.0, 30005.0, 30001.0, 30010.0, 30020.0])
    assert S.first_trade_beyond(p, 30000.0, +1) == pytest.approx(5.0)    # first trade >= 30000 is 30005: gap 5 USD


def test_first_trade_beyond_exact_hit_zero():
    p = np.array([29990.0, 30000.0, 30003.0])
    assert S.first_trade_beyond(p, 30000.0, +1) == 0.0


def test_first_trade_beyond_down_gap_and_none():
    p = np.array([30010.0, 30003.0, 29994.0, 29990.0])
    assert S.first_trade_beyond(p, 30000.0, -1) == pytest.approx(6.0)    # adverse for a sell stop = level - price
    assert S.first_trade_beyond(np.array([30010.0, 30020.0]), 30000.0, -1) is None
    assert S.first_trade_beyond(np.array([29990.0, 29980.0]), 30000.0, +1) is None


def test_price_after_delta():
    p = np.array([29990.0, 29995.0, 30005.0, 30001.0, 30010.0, 30020.0])
    assert S.price_after(T, p, 200, 0) == 30005.0
    assert S.price_after(T, p, 200, 250) == 30001.0       # last trade <= 450 is t=400
    assert S.price_after(T, p, 200, 1000) == 30001.0      # <= 1200 still t=400
    assert S.price_after(T, p, 200, 1300) == 30010.0      # <= 1500 inclusive
    assert S.price_after(T, p, 200, 5000) is None         # past the last trade: dropped


def test_crossing_events_and_slip():
    p = np.array([29990.0, 29995.0, 30005.0, 30001.0, 29990.0, 29980.0])
    ev = S.crossing_events(T, p)
    # up through 30000 at idx 2 (adverse 5); down through 30000 at idx 4 (30001 > 30000 >= 29990, adverse 10)
    assert [(e["idx"], e["dir"], e["level"]) for e in ev] == [(2, 1, 30000.0), (4, -1, 30000.0)]
    s0 = S.slips_bp(T, p, ev, 0)
    assert s0[0] == pytest.approx(5.0 / 30000.0 * 1e4)
    assert s0[1] == pytest.approx(10.0 / 30000.0 * 1e4)
    s250 = S.slips_bp(T, p, ev, 250)                     # event 0: t=200 -> <=450 -> price 30001 -> adverse 1 USD
    assert s250[0] == pytest.approx(1.0 / 30000.0 * 1e4)


def test_multi_level_jump():
    ev = S.crossing_events(np.array([0, 10], np.int64), np.array([29950.0, 30250.0]))
    assert [e["level"] for e in ev] == [30000.0, 30100.0, 30200.0]
    ev = S.crossing_events(np.array([0, 10], np.int64), np.array([30250.0, 29950.0]))
    assert [e["level"] for e in ev] == [30000.0, 30100.0, 30200.0] and all(e["dir"] == -1 for e in ev)


def test_r_multiple():
    assert S.to_r(8.0, 0.40) == pytest.approx(0.2)        # 8 bp / 40 bp stop


def test_tercile_ties():
    # n=6: q1=sorted[2]=2.0, q2=sorted[4]=4.0; < q1 low, < q2 mid, else high (ties go up)
    assert S.assign_terciles([1.0, 2.0, 2.0, 3.0, 4.0, 5.0]) == ["low", "mid", "mid", "mid", "high", "high"]


def test_pick_days_even_and_extension():
    days = ["d%02d" % i for i in range(20)]
    first = S.pick_days(days, 4, [])
    assert first == ["d02", "d07", "d12", "d17"]          # floor((i+.5)*20/4) = 2,7,12,17
    rem = [d for d in days if d not in first]
    assert S.pick_days(days, 4, first) == [rem[2], rem[6], rem[10], rem[14]]   # 16 left: floor((i+.5)*4) = 2,6,10,14


def test_dev_guard():
    S.assert_dev_day("2024-06-30")
    for d in ("2024-07-01", "2025-01-01"):
        with pytest.raises(ValueError):
            S.assert_dev_day(d)
