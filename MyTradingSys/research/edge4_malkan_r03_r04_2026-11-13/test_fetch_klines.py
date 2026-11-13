import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_klines as fk

H = 3600000


def bar(t, c=1.0):
    return [t, c, c, c, c, 1.0]


def test_no_gap_or_duplicate_bars():
    # duplicates (same open time, from overlapping pages) collapse to one; output ascending; a missing bar is reported as a gap
    rows = [bar(5 * H), bar(0), bar(H), bar(H, 2.0), bar(2 * H), bar(4 * H)]
    out = fk.clean_bars(rows, H, now_ms=100 * H)
    ts = [r[0] for r in out]
    assert ts == sorted(set(ts)) == [0, H, 2 * H, 4 * H, 5 * H]
    assert fk.find_gaps(out, H) == [(2 * H, 4 * H)]  # (last bar before gap, next bar after gap)
    assert fk.find_gaps([bar(0), bar(H), bar(2 * H)], H) == []


def test_only_closed_bars_kept():
    # a bar is closed only when open + interval <= now; the forming bar is dropped
    rows = [bar(0), bar(H), bar(2 * H)]
    assert [r[0] for r in fk.clean_bars(rows, H, now_ms=2 * H)] == [0, H]   # H-bar closes exactly at 2H: kept
    assert [r[0] for r in fk.clean_bars(rows, H, now_ms=2 * H - 1)] == [0]  # one ms earlier it is still forming
    assert [r[0] for r in fk.clean_bars(rows, H, now_ms=2 * H + 1)] == [0, H]  # bar 2H is forming: dropped
    assert fk.clean_bars(rows, H, now_ms=0) == []
