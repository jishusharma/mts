"""
Tests for prob_table.py - Dirichlet-smoothed frequency table.
Hand-derived test values computed manually.
"""

import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prob_table


def test_outcome_above_band():
    """ret_pct > band -> UP"""
    assert prob_table.outcome(0.3, band=0.2) == "UP"
    assert prob_table.outcome(1.5, band=0.2) == "UP"


def test_outcome_below_neg_band():
    """ret_pct < -band -> DOWN"""
    assert prob_table.outcome(-0.3, band=0.2) == "DOWN"
    assert prob_table.outcome(-1.5, band=0.2) == "DOWN"


def test_outcome_in_band():
    """ret_pct in [-band, band] -> FLAT"""
    assert prob_table.outcome(0.0, band=0.2) == "FLAT"
    assert prob_table.outcome(0.15, band=0.2) == "FLAT"
    assert prob_table.outcome(-0.15, band=0.2) == "FLAT"


def test_outcome_at_band_edges():
    """At exact band boundaries (ret_pct == band), should be FLAT (not strictly >)"""
    assert prob_table.outcome(0.2, band=0.2) == "FLAT"  # exactly at band, not > band
    assert prob_table.outcome(-0.2, band=0.2) == "FLAT"  # exactly at -band, not < -band


def test_outcome_just_outside_band():
    """Just outside band boundaries should classify correctly"""
    assert prob_table.outcome(0.20001, band=0.2) == "UP"
    assert prob_table.outcome(-0.20001, band=0.2) == "DOWN"


def test_dirichlet_smoothing_counts_only():
    """counts UP2/FLAT0/DOWN0 with alpha=1 -> (2+1)/(3+3) UP, (0+1)/(3+3) FLAT, (0+1)/(3+3) DOWN"""
    # Build manually
    records = [
        {"ts": "2026-01-01T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.5}},  # UP
        {"ts": "2026-01-02T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.3}},  # UP
    ]
    table = prob_table.build_table(records, features=("vp_shape", "price_vs_va", "cvd_slope"),
                                    horizon="60m", band=0.2, alpha=1.0)
    cell = ("V1", "P1", "C1")
    # Raw counts: UP=2, FLAT=0, DOWN=0, n=2
    # Smoothed: UP=(2+1)/(2+3)=3/5, FLAT=(0+1)/(2+3)=1/5, DOWN=(0+1)/(2+3)=1/5
    assert abs(table[cell]["UP"] - 3/5) < 1e-6, f"Expected UP prob 3/5, got {table[cell]['UP']}"
    assert abs(table[cell]["FLAT"] - 1/5) < 1e-6, f"Expected FLAT prob 1/5, got {table[cell]['FLAT']}"
    assert abs(table[cell]["DOWN"] - 1/5) < 1e-6, f"Expected DOWN prob 1/5, got {table[cell]['DOWN']}"


def test_build_table_skip_missing_ts():
    """Records with missing 'ts' or 'fwd_return_pct' should be skipped"""
    records = [
        {"vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.5}},  # Missing ts -> skip
        {"ts": "2026-01-02T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.3}},  # OK
    ]
    table = prob_table.build_table(records, features=("vp_shape", "price_vs_va", "cvd_slope"),
                                    horizon="60m", band=0.2, alpha=1.0)
    # Baseline should have n=1 (only the second record counted)
    assert table["__baseline__"]["n"] == 1


def test_build_table_skip_missing_features():
    """Records with missing feature values should be skipped for that cell"""
    records = [
        {"ts": "2026-01-01T00:00:00Z", "vp_shape": None, "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.5}},  # Missing vp_shape -> skip
        {"ts": "2026-01-02T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.3}},  # OK
    ]
    table = prob_table.build_table(records, features=("vp_shape", "price_vs_va", "cvd_slope"),
                                    horizon="60m", band=0.2, alpha=1.0)
    # Baseline n=1 (only second record used)
    assert table["__baseline__"]["n"] == 1


def test_evaluate_min_n_fallback():
    """Cells with n < min_n in train should fall back to baseline in test"""
    train_records = [
        {"ts": "2026-01-01T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.5}},  # Just 1 record in train -> n=1
    ]
    test_records = [
        {"ts": "2026-02-01T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.3}},  # UP, same cell
    ]
    result = prob_table.evaluate(train_records, test_records, min_n=100, alpha=1.0)
    # Train cell has n=1 < min_n=100, so test should use baseline probs
    # cells_ge_min_n should be 0 (no cell in train has n >= 100)
    assert result["cells_ge_min_n"] == 0


def test_evaluate_chronological_split():
    """Split 70/30 chronologically - never trains on test period"""
    # Create 10 records in chronological order
    records = [
        {"ts": f"2026-01-{i:02d}T00:00:00Z", "vp_shape": f"V{i%2}", "price_vs_va": "P1",
         "cvd_slope": "C1", "fwd_return_pct": {"60m": 0.3 if i % 2 == 0 else -0.3}}
        for i in range(1, 11)
    ]
    # 70/30 split: indices 0-6 train, 7-9 test
    split_idx = int(len(records) * 0.7)
    train = records[:split_idx]
    test = records[split_idx:]

    result = prob_table.evaluate(train, test, min_n=1, alpha=1.0)
    # Just verify n_train and n_test are correct
    assert result["n_train"] == 7
    assert result["n_test"] == 3


def test_evaluate_returns_dict_keys():
    """evaluate() should return dict with required keys"""
    records = [
        {"ts": f"2026-01-{i:02d}T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1",
         "cvd_slope": "C1", "fwd_return_pct": {"60m": 0.3}} for i in range(1, 50)
    ]
    split_idx = int(len(records) * 0.7)
    train = records[:split_idx]
    test = records[split_idx:]

    result = prob_table.evaluate(train, test, min_n=10, alpha=1.0)

    required_keys = {"n_train", "n_test", "cells", "cells_ge_min_n",
                     "logloss_table", "logloss_baseline", "improvement"}
    assert all(k in result for k in required_keys), f"Missing keys in evaluate() result"
    assert result["n_train"] > 0
    assert result["n_test"] > 0


def test_build_table_baseline_entry():
    """__baseline__ entry should exist and have correct structure"""
    records = [
        {"ts": "2026-01-01T00:00:00Z", "vp_shape": "V1", "price_vs_va": "P1", "cvd_slope": "C1",
         "fwd_return_pct": {"60m": 0.5}},  # UP
        {"ts": "2026-01-02T00:00:00Z", "vp_shape": "V2", "price_vs_va": "P2", "cvd_slope": "C2",
         "fwd_return_pct": {"60m": -0.3}},  # DOWN
    ]
    table = prob_table.build_table(records, features=("vp_shape", "price_vs_va", "cvd_slope"),
                                    horizon="60m", band=0.2, alpha=1.0)
    assert "__baseline__" in table
    baseline = table["__baseline__"]
    # Should have UP, FLAT, DOWN, n keys with correct values
    # 2 records: 1 UP, 0 FLAT, 1 DOWN, n=2
    # Smoothed: UP=(1+1)/(2+3)=2/5, FLAT=(0+1)/(2+3)=1/5, DOWN=(1+1)/(2+3)=2/5
    assert abs(baseline["UP"] - 2/5) < 1e-6
    assert abs(baseline["FLAT"] - 1/5) < 1e-6
    assert abs(baseline["DOWN"] - 2/5) < 1e-6
    assert baseline["n"] == 2


if __name__ == "__main__":
    test_outcome_above_band()
    test_outcome_below_neg_band()
    test_outcome_in_band()
    test_outcome_at_band_edges()
    test_outcome_just_outside_band()
    test_dirichlet_smoothing_counts_only()
    test_build_table_skip_missing_ts()
    test_build_table_skip_missing_features()
    test_evaluate_min_n_fallback()
    test_evaluate_chronological_split()
    test_evaluate_returns_dict_keys()
    test_build_table_baseline_entry()
    print("All tests passed!")
