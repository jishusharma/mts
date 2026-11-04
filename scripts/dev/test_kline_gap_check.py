"""Tests for kline_gap_check: missing 1m bars are flagged, sealed months are counted by rows only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import kline_gap_check as k

MIN = 60_000
T0 = 1_640_995_200_000  # 2022-01-01 00:00 UTC


def test_gap_check_flags_missing_minutes():
    ts = [T0 + i * MIN for i in range(10) if i != 4]
    assert k.missing_minutes(ts, T0, T0 + 9 * MIN) == [T0 + 4 * MIN]


def test_gap_check_clean_series_has_no_gaps():
    ts = [T0 + i * MIN for i in range(10)]
    assert k.missing_minutes(ts, T0, T0 + 9 * MIN) == []


def test_expected_rows_for_month():
    assert k.expected_rows('2022-02') == 28 * 1440
    assert k.expected_rows('2024-02') == 29 * 1440


def test_sealed_month_checked_by_row_count_only(tmp_path):
    p = tmp_path / 'ETHUSDT-1m-2025-07.csv'
    p.write_text('x\n' * (31 * 1440 - 1), encoding='utf-8')
    r = k.check_month(p, '2025-07', sealed=True)
    assert r == {'month': '2025-07', 'missing': 1, 'mode': 'rows'}
