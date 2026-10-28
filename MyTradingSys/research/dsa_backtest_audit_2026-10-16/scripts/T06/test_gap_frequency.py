"""Hand-computed checks for gap_frequency.stats (expected numbers derived on paper, not from the code)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gap_frequency as g

# 15 flat bars (range 1 -> ATR14 = 1, close 100); entry bar i=14; bar 15 opens at gap_open.
FLAT = [(100.0, 100.5, 99.5, 100.0)] * 15
HOLD = 3


def series(gap_open):
    return FLAT + [(gap_open, gap_open, gap_open - 1, gap_open)] + [(gap_open, gap_open, gap_open, gap_open)] * (HOLD + 2)


def test_long_gap_beyond_one_atr_stop():
    r = g.stats(series(98.0), 1, HOLD)[("atr", 1.0)]
    # i=14: stop 99, next open 98 < 99 -> P gap; first low<=99 is bar 15 (low 97), open 98 < 99 -> gapped, overshoot (99-98)/1 = 1.0 R
    assert r["p_gap"] == 1
    assert r["gapped"] == 1 and [round(x, 9) for x in r["over"]] == [1.0]


def test_no_gap_when_open_inside_stop():
    r = g.stats(series(99.5), 1, HOLD)[("atr", 1.0)]
    # stop 99, open 99.5 > stop; low 98.5 <= 99 -> stop-out but NOT gapped
    assert r["stops"] == 1 and r["gapped"] == 0 and r["p_gap"] == 0


def test_short_mirror():
    bars = FLAT + [(102.0, 103.0, 102.0, 102.0)] + [(102.0,) * 4] * 5
    r = g.stats(bars, -1, HOLD)[("atr", 1.0)]
    # short stop 101, open 102 > 101 -> gap, overshoot (102-101)/1 = 1.0
    assert r["p_gap"] == 1 and [round(x, 9) for x in r["over"]] == [1.0]


def test_fill_bar_gap_with_offset():
    # a=0.5: L = 99.5, stop = 98.5 (D=1); a=0: stop 99. open 98.0 beats both
    r = g.stats(series(98.0), 1, HOLD)[("atr", 1.0)]
    assert r["f_gap"][0.5] == 1 and r["f_gap"][0.0] == 1
    # open 98.8: above 98.5 (no gap for a=.5) but below 99 (gap for a=0)
    r2 = g.stats(series(98.8), 1, HOLD)[("atr", 1.0)]
    assert r2["f_gap"][0.5] == 0 and r2["f_gap"][0.0] == 1
