"""Spec-derived tests for scripts/dev/run_argon_pipeline.py pure helpers.

Covers:
  - flash_counts:
    * empty list and items without flash_parsed returning zeroed counts
    * accurate scoring of matches, mismatches, and field mapping
    * accurate classification of invented numbers and correct nulls
  - trials_headline:
    * exact formatting of summary fields and Flash comparison
    * dynamically reflecting counts dictionary values
  - generate_report:
    * creating output parent directories and writing full Markdown report
    * inclusion of headline descriptive counts in Section 1
    * inclusion of comparison table rows in Section 3
    * inclusion of enlarged crop transcriptions in Section 4
    * inclusion of findings and follow-up cards in Sections 5 & 6
"""
from pathlib import Path
import pytest

import run_argon_pipeline as rap


@pytest.fixture
def sample_pipeline_data():
    return {
        "metadata": {
            "card": "argon-blind-read-7-frames",
            "model": "gemini-4-argon-low",
            "effort": "low",
        },
        "descriptive_counts_7_frames": {
            "total_fields": 28,
            "matches": 22,
            "mismatches": 2,
            "correct_nulls": 2,
            "missed_nulls": 1,
            "invented_numbers": 1,
            "unverified": 0,
        },
        "flash_descriptive_counts_7_frames": {
            "total_fields": 28,
            "matches": 20,
            "mismatches": 3,
            "correct_nulls": 2,
            "missed_nulls": 2,
            "invented_numbers": 1,
            "unverified": 0,
        },
        "descriptive_counts_all_panels": {
            "total_fields": 32,
            "matches": 24,
            "mismatches": 3,
            "correct_nulls": 3,
            "missed_nulls": 1,
            "invented_numbers": 1,
            "unverified": 0,
        },
        "evaluations": [
            {
                "id": "frame_1",
                "frame": "frame_001.png",
                "truth": {"pos": 1, "entry": 25000, "sl": 24900, "tp": 25300},
                "truth_source": "PILOT_AUDIT_UNCHECKED",
                "argon_parsed": {"position": 1, "entry": 25000, "stop": 24900, "target": 25300},
                "argon_scores": {"position": "MATCH", "entry": "MATCH", "stop": "MATCH", "target": "MATCH"},
                "flash_parsed": {"position": 1, "entry": 25000, "stop": 24900, "target": 25250},
            },
            {
                "id": "frame_2",
                "frame": "frame_002.png",
                "truth": {"pos": -1, "entry": 24500, "sl": None, "tp": 24000},
                "truth_source": "PILOT_AUDIT_UNCHECKED",
                "argon_parsed": {"position": -1, "entry": 24500, "stop": None, "target": 24000},
                "argon_scores": {"position": "MATCH", "entry": "MATCH", "stop": "CORRECT_NULL", "target": "MATCH"},
                "flash_parsed": {"position": -1, "entry": 24500, "stop": 24600, "target": 24000},
            },
        ],
        "crops": [
            {
                "id": "crop_k0zm_target",
                "descriptive_response": "Crop analysis: readable blue tag 25206 clearly visible above 25200.",
            },
            {
                "id": "crop_0550_stop",
                "descriptive_response": "Stop Loss Label: None visible in this crop (obscured by entry tag).",
            },
        ],
    }


def test_flash_counts_empty_and_no_flash():
    assert rap.flash_counts([])["matches"] == 0
    items = [{"truth": {"pos": 1}, "flash_parsed": None}]
    assert rap.flash_counts(items)["matches"] == 0


def test_flash_counts_scoring_accurately():
    items = [
        {
            "truth": {"pos": 2, "entry": 100, "sl": 90, "tp": 120},
            "flash_parsed": {"position": 2, "entry": 100, "stop": 95, "target": 120},
        }
    ]
    counts = rap.flash_counts(items)
    assert counts["matches"] == 3  # pos, entry, target match
    assert counts["mismatches"] == 1  # stop mismatch (95 vs 90)


def test_flash_counts_invented_and_correct_null():
    items = [
        {
            "truth": {"pos": 1, "entry": 100, "sl": None, "tp": None},
            "flash_parsed": {"position": 1, "entry": 100, "stop": 90, "target": None},
        }
    ]
    counts = rap.flash_counts(items)
    assert counts["matches"] == 2  # pos, entry
    assert counts["invented_numbers"] == 1  # stop is invented
    assert counts["correct_nulls"] == 1  # target is correct null


def test_trials_headline_format(sample_pipeline_data):
    headline = rap.trials_headline(sample_pipeline_data)
    assert "Argon low, 7 frames, 28 fields" in headline
    assert "matches 22" in headline
    assert "mismatch 2" in headline
    assert "correct null 2" in headline
    assert "missed null 1" in headline
    assert "invented 1 (Flash 1)" in headline
    assert "results in research/layer_lab/argon_blind_read/results_argon-low.json" in headline


def test_trials_headline_dynamic_counts(sample_pipeline_data):
    sample_pipeline_data["descriptive_counts_7_frames"]["matches"] = 25
    sample_pipeline_data["flash_descriptive_counts_7_frames"]["invented_numbers"] = 4
    headline = rap.trials_headline(sample_pipeline_data)
    assert "matches 25" in headline
    assert "invented 1 (Flash 4)" in headline


def test_generate_report_creates_file_and_headers(sample_pipeline_data, tmp_path):
    report_file = tmp_path / "sub" / "report.md"
    rap.generate_report(sample_pipeline_data, report_file)
    assert report_file.exists()

    content = report_file.read_text(encoding="utf-8")
    assert content.startswith("# Layer Lab Report: argon-blind-read-7-frames")
    assert "## 1. Headline Numbers and Verdict" in content
    assert "Matches to known numeric truth: **22**" in content
    assert "## 2. What was Run" in content
    assert "## 3. Comparison Table (Argon low vs Flash low vs Pilot Reference)" in content
    assert "## 4. Enlarged Crop Transcriptions" in content
    assert "## 5. Findings & Defect Ledger" in content
    assert "## 6. Follow-up Cards" in content


def test_generate_report_includes_crop_descriptions(sample_pipeline_data, tmp_path):
    report_file = tmp_path / "report_crops.md"
    rap.generate_report(sample_pipeline_data, report_file)
    content = report_file.read_text(encoding="utf-8")

    assert "readable blue tag 25206 clearly visible above 25200" in content
    assert "Stop Loss Label: None visible in this crop" in content


def test_generate_report_table_content(sample_pipeline_data, tmp_path):
    report_file = tmp_path / "report_table.md"
    rap.generate_report(sample_pipeline_data, report_file)
    content = report_file.read_text(encoding="utf-8")

    assert "| frame_001.png | position | 1 | 1 | 1 | MATCH |  |" in content
    assert "| frame_002.png | stop | None | None | 24600 | CORRECT_NULL | Honest null |" in content
