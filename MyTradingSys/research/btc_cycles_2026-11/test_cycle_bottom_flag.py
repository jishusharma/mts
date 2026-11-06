"""Spec tests for cycle_bottom_flag.py on fixed synthetic fixtures (expected values worked out by hand from RULE.md)."""
import os
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts", "dev"))
import cycle_bottom_flag as f  # noqa: E402

START = date(2026, 9, 1)
EPOCH = date(1970, 1, 1)


def fixture(over=None, end=date(2026, 11, 20), base=70_000.0):
    """Flat daily bars at `base` (low/high +-1 %), with over[date] = (low, close) replacing single days."""
    over, rows, d = over or {}, [], START
    while d <= end:
        lo, c = over.get(d, (base * 0.99, base))
        rows.append(dict(d=d, h=max(c, lo) * 1.01, l=lo, c=c))
        d += timedelta(days=1)
    return rows


def block_end(after):
    d = after
    while (d - EPOCH).days % 5 != 4:
        d += timedelta(days=1)
    return d


B = block_end(date(2026, 10, 12))          # a 5-day block end inside the window
ABOVE = {B - timedelta(days=i): (84_000.0, 85_000.0) for i in range(7)}  # 7 days at 85k: covers a Sunday and the block end


def test_constants_match_analyst_rows():
    import analyst_levels
    assert RECLAIM_IN_ROW(f.RECLAIM_5D)
    assert RECLAIM_IN_ROW(f.WEEKLY_FLOOR)
    assert analyst_levels.parse_levels(f.SOURCE_ROWS[f.RECLAIM_5D])[-1] == f.RECLAIM_5D


def RECLAIM_IN_ROW(level):
    import analyst_levels
    return level in analyst_levels.parse_levels(f.SOURCE_ROWS[level])


def test_window_is_cycles_md_clock():
    assert f.WINDOW == (date(2026, 10, 4), date(2026, 11, 16))
    assert f.PEAK_DATE == date(2025, 10, 6)


def test_flat_market_waits():
    s = f.state(fixture(), date(2026, 11, 7))
    assert s["state"] == "WAIT" and s["confirmed_on"] is None
    assert "WAIT" in f.flag_line(fixture(), date(2026, 11, 7))


def test_confirmed_after_5d_close_above_reclaim():
    rows = fixture(ABOVE)
    s = f.state(rows, B + timedelta(days=1))
    assert s["state"] == "CONFIRMED" and s["confirmed_on"] == B
    line = f.flag_line(rows, B + timedelta(days=1))
    assert "CONFIRMED" in line and "BUY ZONE 80,450-82,059" in line and "lev 2x" in line


def test_today_bar_is_not_counted():
    # asof == B: the block's last day is not yet complete, so no confirmation yet
    assert f.state(fixture(ABOVE), B)["state"] == "WAIT"


def test_weekly_floor_gate():
    # 5-day close above reclaim, but the last completed weekly close is 60k (under 75,000): no confirmation
    assert B.weekday() != 6
    rows = fixture({B: (84_000.0, 85_000.0)}, base=60_000.0)
    assert f.block_closes(rows, B + timedelta(days=1))[B] == 85_000.0
    assert f.state(rows, B + timedelta(days=1))["state"] == "WAIT"
    assert "wk>=75,000 n" in f.flag_line(rows, B + timedelta(days=1))


def test_retest_entry_and_stop():
    over = dict(ABOVE)
    over[B + timedelta(days=1)] = (79_500.0, 80_000.0)   # touches zone, closes under reclaim 80,450: no entry
    over[B + timedelta(days=2)] = (81_000.0, 82_000.0)   # touches zone, daily close holds: entry
    rows = fixture(over)
    assert f.state(rows, B + timedelta(days=2))["state"] == "CONFIRMED"   # day B+2 not complete yet
    s = f.state(rows, B + timedelta(days=3))
    assert s["state"] == "IN" and s["entry_day"] == B + timedelta(days=2)
    assert s["entry"] == 82_000.0
    assert s["stop"] == 78_705.0        # 79,500 swing low (two-day touch streak) * 0.99
    assert "ENTRY OK" in f.flag_line(rows, B + timedelta(days=3))


def test_weekly_close_below_reclaim_exits():
    over = dict(ABOVE)
    over[B + timedelta(days=1)] = (81_000.0, 82_000.0)
    d = B + timedelta(days=2)
    while d.weekday() != 6:
        d += timedelta(days=1)
    for i in range(2, (d - B).days + 1):
        over[B + timedelta(days=i)] = (78_000.0, 79_000.0)   # drifts under the reclaimed level through the Sunday
    rows = fixture(over)
    s = f.state(rows, d + timedelta(days=1))
    assert s["state"] == "WAIT" and s["exit_day"] == d and s["entry"] is None
    assert "last trade exited" in f.flag_line(rows, d + timedelta(days=1))


def test_out_of_window_is_labelled():
    assert " OUT" in f.flag_line(fixture(), date(2026, 11, 20))
    assert " OUT" not in f.flag_line(fixture(), date(2026, 11, 7))


def test_real_csv_today_line():
    rows = f.load()
    line = f.flag_line(rows, date(2026, 11, 7))
    assert line.startswith("CYCLE4 d397 [363-406]") and "dd-40.0%" in line
