"""
Tests for bt_rsi.py - Wilder RSI and rsi_regime classifier.
Hand-derived test values; all assertions use computed values via manual calculation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_rsi


def test_rsi_wilder_rising_series():
    """closes 1..16: rising series -> RSI should be 100 (all gains, no losses)"""
    closes = list(range(1, 17))  # [1, 2, 3, ..., 16]
    rsi = bt_rsi.rsi_wilder(closes, period=14)
    # Before index 14: None
    assert rsi[0:14] == [None] * 14
    # At index 14: changes are [1, 1, 1, ..., 1] (14 ones)
    # avg_gain = 14/14 = 1.0, avg_loss = 0
    # RSI = 100 (avg_loss == 0 and avg_gain > 0)
    assert rsi[14] == 100.0, f"Expected RSI 100 for rising series, got {rsi[14]}"
    # After index 14, all changes are 1, so avg stays at 1.0, RSI stays 100
    assert rsi[15] == 100.0


def test_rsi_wilder_alternating_series():
    """closes alternating +1/-1 -> RSI should be 50 at the seed (avg_gain == avg_loss)"""
    closes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]  # alternating pattern
    rsi = bt_rsi.rsi_wilder(closes, period=14)
    # Changes: [1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1]
    # gains = [1, 1, 1, 1, 1, 1, 1] = 7 ones
    # losses = [1, 1, 1, 1, 1, 1, 1] = 7 ones
    # avg_gain = 7/7 = 1.0, avg_loss = 7/7 = 1.0
    # RSI = 100 - 100/(1+1) = 100 - 50 = 50.0
    assert rsi[14] == 50.0, f"Expected RSI 50 for alternating series, got {rsi[14]}"


def test_rsi_wilder_none_prefix():
    """Entries before index period should be None"""
    closes = list(range(1, 20))
    rsi = bt_rsi.rsi_wilder(closes, period=14)
    assert len(rsi) == 19
    assert all(x is None for x in rsi[:14])
    assert rsi[14] is not None


def test_rsi_wilder_avg_loss_zero():
    """When avg_loss == 0 and avg_gain > 0, RSI should be 100"""
    # Create a series that only goes up in the seed period
    closes = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]
    rsi = bt_rsi.rsi_wilder(closes, period=14)
    # All changes positive, avg_loss = 0
    assert rsi[14] == 100.0


def test_rsi_wilder_avg_gain_and_loss_zero():
    """When avg_gain == 0 and avg_loss == 0 (flat series), RSI should be 50"""
    closes = [100] * 16  # All the same
    rsi = bt_rsi.rsi_wilder(closes, period=14)
    # All changes are 0
    assert rsi[14] == 50.0


def test_rsi_wilder_value_error_period_lt_1():
    """period < 1 should raise ValueError"""
    try:
        bt_rsi.rsi_wilder([1, 2, 3], period=0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_rsi_wilder_value_error_len_not_gt_period():
    """len(closes) <= period should raise ValueError"""
    try:
        bt_rsi.rsi_wilder([1, 2, 3], period=14)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_rsi_regime_bull():
    """BULL: min(window) >= lo and max(window) >= hi"""
    # Construct window of 20 values, min=50, max=70
    rsi_vals = [50 + (i % 5) * 5 for i in range(21)]  # [50,55,60,65,70,50,55,...] - len 21
    regime = bt_rsi.rsi_regime(rsi_vals, lo=40.0, hi=60.0, lookback=20)
    # At index 20, last 20 values are [60,65,70,50,55,60,65,70,50,55,60,65,70,50,55,60,65,70,50,55]
    # Wait, let me recalculate. With period 21 and lookback 20, we get the last 20 non-None values.
    # Let me verify manually: min of those 20 = 50, max = 70
    # min(50) >= 40 (lo) -> True, max(70) >= 60 (hi) -> True -> BULL
    assert regime[20] == "BULL", f"Expected BULL at index 20, got {regime[20]}"


def test_rsi_regime_bear():
    """BEAR: max(window) <= hi and min(window) <= lo"""
    rsi_vals = [30 + (i % 3) * 5 for i in range(21)]  # [30,35,40,30,35,40,...] - min 30, max 40
    regime = bt_rsi.rsi_regime(rsi_vals, lo=40.0, hi=60.0, lookback=20)
    # At index 20, max = 40, min = 30
    # max(40) <= 60 (hi) -> True, min(30) <= 40 (lo) -> True -> BEAR
    assert regime[20] == "BEAR", f"Expected BEAR at index 20, got {regime[20]}"


def test_rsi_regime_range():
    """RANGE: neither BULL nor BEAR conditions met"""
    rsi_vals = [45 + (i % 2) * 10 for i in range(21)]  # [45,55,45,55,...] - min 45, max 55
    regime = bt_rsi.rsi_regime(rsi_vals, lo=40.0, hi=60.0, lookback=20)
    # At index 20, max = 55, min = 45
    # BULL: min(45) >= 40 -> True, max(55) >= 60 -> False -> Not BULL
    # BEAR: max(55) <= 60 -> True, min(45) <= 40 -> False -> Not BEAR
    # -> RANGE
    assert regime[20] == "RANGE", f"Expected RANGE at index 20, got {regime[20]}"


def test_rsi_regime_none_with_nones():
    """Entries with rsi is None or < lookback non-None values should be None"""
    rsi_vals = [None, None, None, 50, 50, 50]  # Only 3 non-None
    regime = bt_rsi.rsi_regime(rsi_vals, lo=40.0, hi=60.0, lookback=5)
    # At index 5, we have 3 non-None values (< 5), so should be None
    assert regime[5] is None


def test_rsi_regime_value_error_invalid_thresholds():
    """Invalid threshold conditions should raise ValueError"""
    try:
        # lo >= hi
        bt_rsi.rsi_regime([50] * 25, lo=60.0, hi=40.0, lookback=20)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    try:
        # lo <= 0
        bt_rsi.rsi_regime([50] * 25, lo=0.0, hi=60.0, lookback=20)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    try:
        # hi >= 100
        bt_rsi.rsi_regime([50] * 25, lo=40.0, hi=100.0, lookback=20)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_rsi_regime_value_error_lookback_lt_1():
    """lookback < 1 should raise ValueError"""
    try:
        bt_rsi.rsi_regime([50] * 25, lo=40.0, hi=60.0, lookback=0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_rsi_wilder_rising_series()
    test_rsi_wilder_alternating_series()
    test_rsi_wilder_none_prefix()
    test_rsi_wilder_avg_loss_zero()
    test_rsi_wilder_avg_gain_and_loss_zero()
    test_rsi_wilder_value_error_period_lt_1()
    test_rsi_wilder_value_error_len_not_gt_period()
    test_rsi_regime_bull()
    test_rsi_regime_bear()
    test_rsi_regime_range()
    test_rsi_regime_none_with_nones()
    test_rsi_regime_value_error_invalid_thresholds()
    test_rsi_regime_value_error_lookback_lt_1()
    print("All tests passed!")
