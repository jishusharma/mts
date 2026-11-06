"""Tests for cc_s3_10sym_run.py and the ten-symbol count. Expected numbers computed by hand."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cc_s3_10sym_run as T  # noqa: E402
import cc_s3_pooled_count as P  # noqa: E402

DEV_END_MS = 1719792000000


def _bar(t):
    return {"t": t, "o": 1.0, "h": 1.0, "l": 1.0, "c": 1.0, "v": 1.0}


def test_ten_symbols_have_tick_and_dataset():
    assert len(P.DATASETS) == 10 and set(P.TICKS) == set(P.DATASETS)
    assert P.DATASETS["SOLUSDT"] == "klines_sol" and P.TICKS["DOGEUSDT"] == 0.00001


def test_loader_refuses_validation_dated_bar():
    bars = [_bar(DEV_END_MS - 60000), _bar(DEV_END_MS + 60000)]
    with pytest.raises(Exception):
        P.count_fills(bars, bars, 1.0, 0.01)


def test_dev_bars_with_gap_keep_only_present_bars():
    t0 = 1640995200000
    bars = [_bar(t0), _bar(t0 + 60000), _bar(t0 + 7200 * 60000)]   # 7199-bar hole is not filled
    assert [b["t"] for b in P.dev_bars(bars)] == [b["t"] for b in bars]


def test_holm_single_is_m_times_p_capped():
    assert T.holm_single(0.0001) == pytest.approx(0.0221)   # 221 * 0.0001 by hand
    assert T.holm_single(0.5) == 1.0


def test_verdict_rule():
    assert T.verdict(1000, 0.2, 0.1, 0.01, 8, 10) == "PASS"
    assert T.verdict(1000, 0.2, 0.1, 0.01, 6, 10) == "UNDERPOWERED"   # pooled passes but only 6 of 10 symbols agree
    assert T.verdict(1000, 0.2, -0.1, 0.4, 9, 10) == "UNDERPOWERED"
    assert T.verdict(1000, -0.05, -0.1, 1.0, 2, 10) == "FAIL"
    assert T.verdict(50, 0.3, 0.1, 0.0, 10, 10) == "UNDERPOWERED"
