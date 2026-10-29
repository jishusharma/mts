"""data_check.check() is a pure function over raw open-time rows (read straight off the kline CSVs,
before _bars.load_1m's sort/dedup) -- hand-counted cases for missing minutes, duplicates, out-of-order
rows and the longest gap, plus the look-ahead guard on the sealed 2024-07-01 cut."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data_check  # noqa: E402

MIN_MS = 60000


def test_hole_and_duplicate_hand_counted():
    # 10-minute window [0, 10*MIN). Rows present: 0,1,2,2(dup),3,7,8,9 -> unique minutes {0,1,2,3,7,8,9} = 7.
    # expected=10, present=7, missing=3 (minutes 4,5,6), longest_gap=3, duplicates=1 (the repeated minute 2).
    start_ms, end_ms = 0, 10 * MIN_MS
    rows = [0, 1 * MIN_MS, 2 * MIN_MS, 2 * MIN_MS, 3 * MIN_MS, 7 * MIN_MS, 8 * MIN_MS, 9 * MIN_MS]
    counts = data_check.check(rows, start_ms, end_ms)
    assert counts['expected'] == 10
    assert counts['present'] == 7
    assert counts['missing'] == 3
    assert counts['duplicates'] == 1
    assert counts['longest_gap'] == 3
    assert counts['out_of_order'] == 0


def test_row_at_sealed_cut_raises():
    start_ms, end_ms = 0, 10 * MIN_MS
    rows = [0, 1 * MIN_MS, data_check.CUT_MS]   # exactly at the 2024-07-01 00:00 UTC cut
    with pytest.raises(ValueError):
        data_check.check(rows, start_ms, end_ms)


def test_row_after_sealed_cut_raises():
    start_ms, end_ms = 0, 10 * MIN_MS
    rows = [0, data_check.CUT_MS + MIN_MS]   # one minute past the cut
    with pytest.raises(ValueError):
        data_check.check(rows, start_ms, end_ms)


def test_out_of_order_row_is_counted():
    # rows as read off disk, not pre-sorted: minute 2 arrives before minute 1 -> one out-of-order row.
    start_ms, end_ms = 0, 4 * MIN_MS
    rows = [0, 2 * MIN_MS, 1 * MIN_MS, 3 * MIN_MS]
    counts = data_check.check(rows, start_ms, end_ms)
    assert counts['out_of_order'] == 1
    assert counts['missing'] == 0
    assert counts['duplicates'] == 0
