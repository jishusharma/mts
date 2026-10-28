"""Tests for cross-method extraction QA (extraction-cross-method-qa).

Ensures:
1. Exactly 5 out of 5 planted numeric errors are detected in a mutated dataset.
2. Rule normalisation handles levels, bar counts, grades, and ratios.
3. Cross-method evaluation computes agreement % and assigns proper advice.
4. Trust table covers every (type, method) pair with 3+ sampled videos.
"""
import copy
from pathlib import Path
import sys
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cross_method_qa as qa  # noqa: E402


def test_planted_errors_5_of_5():
    """Verify that planted-error detector flags exactly 5 of 5 known numeric edits."""
    baseline = qa.load_benchmark_dataset()
    assert len(baseline) >= 15, "Benchmark dataset must contain at least 15 rule-bearing items"

    mutated, expected_edits = qa.create_planted_error_copy(baseline)
    assert len(expected_edits) == 5, "Must plant exactly 5 numeric errors"

    detected_errors = qa.detect_planted_errors(baseline, mutated)
    assert len(detected_errors) == 5, f"Expected exactly 5 detected errors, got {len(detected_errors)}: {detected_errors}"

    # Verify that each detected error matches the planted edits
    for edit in expected_edits:
        match = [e for e in detected_errors if e["video_id"] == edit["video_id"] and e["field"] == edit["field"]]
        assert len(match) == 1, f"Failed to detect planted edit: {edit}"
        assert match[0]["mutated_value"] == edit["new_value"]
        assert match[0]["baseline_value"] == edit["original_value"]


def test_rule_normalization():
    """Verify normalisation of numbers, levels, grades, and keywords."""
    assert qa.normalize_number("60") == 60.0
    assert qa.normalize_number("rs.60") == 60.0
    assert qa.normalize_number("100") == 100.0
    assert qa.normalize_number("1.5") == 1.5
    assert qa.normalize_number("1:2") == 2.0
    assert qa.normalize_number("80-90%") == 85.0
    assert qa.normalize_grade("5 star") == "5_star"
    assert qa.normalize_grade("7-Star") == "7_star"


def test_cross_method_evaluation():
    """Verify agreement calculation and advice generation across sampled pairs."""
    dataset = qa.load_benchmark_dataset()
    report_data = qa.evaluate_dataset(dataset)

    trust_rows = report_data["trust_rows"]
    assert len(trust_rows) >= 6, f"Expected at least 6 trust rows for pairs with 3+ videos, got {len(trust_rows)}"

    for row in trust_rows:
        assert row["sampled_videos"] >= 3, f"Trust row {row} must have 3+ sampled videos"
        assert row["total_rules"] > 0
        assert 0.0 <= row["agreement_pct"] <= 100.0
        assert row["advice"] in {"trust", "re-extract", "ASR-only", "Gemini-preferred", "captions-preferred"}


def test_trust_table_coverage():
    """Verify that English talk, chart-walk, and Hinglish/Hindi have trust rows for primary methods."""
    dataset = qa.load_benchmark_dataset()
    report_data = qa.evaluate_dataset(dataset)
    trust_rows = report_data["trust_rows"]

    covered_pairs = {(r["video_type"], r["method"]) for r in trust_rows}
    required_pairs = {
        ("English talk", "captions"),
        ("English talk", "gemini"),
        ("chart-walk", "captions"),
        ("chart-walk", "gemini"),
        ("Hinglish/Hindi", "captions"),
        ("Hinglish/Hindi", "hindi_asr"),
    }
    missing = required_pairs - covered_pairs
    assert not missing, f"Missing required (type, method) pairs: {missing}"
