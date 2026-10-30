"""Spec-derived tests for the Tom noise-unit helpers; fixtures stay in pytest temp dirs."""
import importlib.util
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("TOM_NOISE_UNITS_SOURCE", ROOT / "scripts/dev/tom_noise_units.py"))
SPEC = importlib.util.spec_from_file_location("tom_noise_units_under_test", SOURCE)
tnu = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tnu)


def test_true_range_formula_and_empty_input():
    # Prior close 10; max(2, 3, 1)/11 = 3/11.
    assert tnu.true_ranges([(12, 9, 10), (12, 10, 11)]) == pytest.approx([2 / 11])
    assert tnu.true_ranges([]) == []
    assert tnu.true_ranges([(12, 9, 10)]) == []


def test_aggregate_keeps_only_full_bucket_and_uses_extrema_and_last_close():
    rows = {i * 60_000: (1, h, l, c) for i, (h, l, c) in enumerate(
        [(11, 9, 10), (13, 8, 12), (12, 7, 11), (14, 9, 13), (15, 10, 14),
         (20, 18, 19), (21, 17, 20), (22, 16, 21), (23, 15, 22), (24, 14, 23),
         (30, 28, 29)])}
    assert tnu.aggregate(rows, 5) == [(0, 15, 7, 14), (300_000, 24, 14, 23)]


def test_tr_fracs_requires_adjacent_bucket_and_keep_predicate():
    bars = [(0, 12, 9, 10), (300_000, 13, 9, 12), (900_000, 14, 11, 13)]
    assert tnu.tr_fracs(bars, 5, lambda b: True) == pytest.approx([4 / 12])
    assert tnu.tr_fracs(bars, 5, lambda b: b == 900_000) == []


def test_n5_direct_bars_median_and_empty_result():
    # TR fractions are 2/10 and 4/20; median is their arithmetic midpoint.
    assert tnu.n5([(11, 9, 10), (11, 10, 10), (14, 10, 20)]) == pytest.approx(0.15)
    assert tnu.n5([(1, 0, 1)]) == 0.0


def test_n5_five_minute_boundaries_complete_buckets_and_median():
    rows = {}
    # Three complete buckets with close 10, 10, 20 and true ranges 1, 4.
    for b, (hi, lo, close) in enumerate([(11, 9, 10), (11, 10, 10), (14, 10, 20)]):
        for minute in range(5):
            rows[(b * 5 + minute) * 60_000] = (close, hi, lo, close)
    # A fourth, incomplete bucket must not enter the calculation.
    rows[900_000] = (1, 100, 0, 1)
    assert tnu.n5(rows) == pytest.approx(0.15)


def test_n5_timestamp_cutoff_is_inclusive_of_completed_bar_close():
    rows = {}
    for minute in range(15):
        bucket = minute // 5
        close = (10, 10, 20)[bucket]
        hi, lo = ((11, 9), (11, 10), (14, 10))[bucket]
        rows[minute * 60_000] = (close, hi, lo, close)
    midnight = datetime(1970, 1, 1, 0, 15, tzinfo=timezone.utc)
    assert tnu.n5(rows, asof=midnight) == pytest.approx(0.15)
    assert tnu.n5(rows, asof=900_000) == pytest.approx(0.15)


def test_n5_rejects_naive_datetime_and_direct_list_asof():
    with pytest.raises(ValueError, match="explicit timezone"):
        tnu.n5({}, asof=datetime(2024, 1, 1))
    with pytest.raises(ValueError, match="timestamped bars"):
        tnu.n5([(1, 0, 1)], asof="2024-01-01")


def test_min_stop_width_uses_larger_noise_or_fee_gate():
    assert tnu.min_stop_width(100, 0.01, 0.001) == pytest.approx(0.88)
    assert tnu.min_stop_width(100, 0.001, {"entry": 0.002, "stop": 0.003}) == pytest.approx(2.0)


def test_min_stop_width_at_and_around_noise_fee_crossover():
    fee_width = 1.0  # (0.0025 / 0.25) * entry 100
    at_limit = fee_width / (0.88 * 100)
    assert tnu.min_stop_width(100, at_limit, 0.0025) == pytest.approx(fee_width)
    assert tnu.min_stop_width(100, at_limit * 0.999, 0.0025) == pytest.approx(fee_width)
    assert tnu.min_stop_width(100, at_limit * 1.001, 0.0025) == pytest.approx(0.88 * at_limit * 1.001 * 100)


def test_load_skips_header_bad_rows_outside_window_and_dropped_day(tmp_path):
    month = tmp_path / "X-1m-2024-01.csv"
    outside_month = tmp_path / "X-1m-2023-12.csv"
    jan1 = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    jan2 = jan1 + 86_400_000
    month.write_text("open,open,high,low,close\nnot-a-ts,1,2,0,1\n" +
                     f"{jan1},1,2,0,1\n{jan2},1,3,0,2\n", encoding="utf-8")
    outside_month.write_text(f"{jan1 - 60_000},1,2,0,1\n", encoding="utf-8")
    assert tnu.load(tmp_path, date(2024, 1, 1), date(2024, 1, 2), {"2024-01-02"}) == {
        jan1: (1.0, 2.0, 0.0, 1.0)
    }


def test_cli_empty_input_and_malformed_split_take_error_paths(tmp_path):
    split = tmp_path / "split.json"
    split.write_text(json.dumps({"dev_window": ["2024-01-01", "2024-01-01"],
                                 "dev_dropped_days": [], "holdout_window": ["2024-01-02", "2024-01-03"]}),
                     encoding="utf-8")
    empty = tmp_path / "empty"
    empty.mkdir()
    no_rows = subprocess.run([sys.executable, str(SOURCE), "--dax", str(empty), "--btc", str(empty),
                              "--split", str(split)], capture_output=True, text=True)
    assert no_rows.returncode != 0
    assert "StatisticsError" in no_rows.stderr
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    bad = subprocess.run([sys.executable, str(SOURCE), "--dax", str(empty), "--btc", str(empty),
                          "--split", str(malformed)], capture_output=True, text=True)
    assert bad.returncode != 0


def test_cli_rejects_dev_window_that_reaches_holdout(tmp_path):
    split = tmp_path / "split.json"
    split.write_text(json.dumps({"dev_window": ["2024-01-01", "2024-01-03"],
                                 "dev_dropped_days": [], "holdout_window": ["2024-01-03", "2024-01-04"]}),
                     encoding="utf-8")
    empty = tmp_path / "empty"
    empty.mkdir()
    run = subprocess.run([sys.executable, str(SOURCE), "--dax", str(empty), "--btc", str(empty),
                          "--split", str(split)], capture_output=True, text=True)
    assert run.returncode != 0
    assert "AssertionError" in run.stderr
