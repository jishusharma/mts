"""Unit and integration tests for scripts/dev/trial_ledger.py.

Verifies:
1. Two small temp registries parse correctly with row counts per study.
2. Output sorting is stable and rerun gives byte-identical output.
3. Existing TRIAL_LEDGER.csv is never modified.
4. holdout_reads.csv skeleton exists with expected header.
5. Live repo scan over the 9 TRIAL_REGISTRY*.csv files sums to exactly 1279 rows.
"""
import csv
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

import pytest
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))

import trial_ledger


def hash_file(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def test_temp_registries_and_stable_sort(tmp_path):
    # Setup two mock registries
    reg1 = tmp_path / "study1" / "TRIAL_REGISTRY.csv"
    reg1.parent.mkdir(parents=True)
    with open(reg1, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "date", "variant", "n_trades", "mean_R_net"])
        writer.writerow(["run_b", "2026-10-02", "var_b", "10", "0.15"])
        writer.writerow(["run_a", "2026-10-01", "var_a", "20", "-0.10"])

    reg2 = tmp_path / "study2" / "TRIAL_REGISTRY_SMOKE.csv"
    reg2.parent.mkdir(parents=True)
    with open(reg2, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["study", "variant", "date", "data_window", "verdict"])
        writer.writerow(["study2", "var_z", "2026-10-05", "DEV", "PASS"])

    out_ledger = tmp_path / "TRIAL_LEDGER_BUILT.csv"
    out_holdout = tmp_path / "holdout_reads.csv"

    stats, total = trial_ledger.build_ledger(
        registry_files=[reg1, reg2],
        out_built_path=out_ledger,
        out_holdout_path=out_holdout,
        repo_root=tmp_path,
    )

    assert total == 3
    assert out_ledger.exists()
    assert out_holdout.exists()

    # Verify rows in built ledger
    with open(out_ledger, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3

    # Check headers
    assert list(rows[0].keys()) == ["study", "variant", "date", "split", "verdict"]

    # Check byte-identical on rerun
    hash1 = hash_file(out_ledger)
    trial_ledger.build_ledger(
        registry_files=[reg1, reg2],
        out_built_path=out_ledger,
        out_holdout_path=out_holdout,
        repo_root=tmp_path,
    )
    hash2 = hash_file(out_ledger)
    assert hash1 == hash2


def test_hand_kept_trial_ledger_untouched():
    hand_kept = REPO / "MyTradingSys" / "research" / "TRIAL_LEDGER.csv"
    assert hand_kept.exists()
    orig_hash = hash_file(hand_kept)

    # Run the main runner
    trial_ledger.main()

    new_hash = hash_file(hand_kept)
    assert orig_hash == new_hash, "TRIAL_LEDGER.csv was modified!"


def test_live_repo_trial_ledger_built():
    built_path = REPO / "MyTradingSys" / "research" / "TRIAL_LEDGER_BUILT.csv"
    holdout_path = REPO / "MyTradingSys" / "research" / "holdout_reads.csv"

    assert built_path.exists(), "TRIAL_LEDGER_BUILT.csv must exist after build"
    assert holdout_path.exists(), "holdout_reads.csv must exist after build"

    with open(built_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # The sum of rows across the 9 TRIAL_REGISTRY*.csv files is 1279
    files = trial_ledger.find_registry_files(REPO)
    assert len(files) == 9, f"Expected 9 registry files, found {len(files)}"

    expected_total = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            r = csv.reader(fp)
            next(r, None)
            expected_total += sum(1 for _ in r)

    assert len(rows) == expected_total == 1279, (
        f"Built ledger has {len(rows)} rows, expected {expected_total}"
    )

    # Check holdout reads header
    with open(holdout_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header == ["timestamp_utc", "study", "holdout_window", "accessor", "reason", "verdict"]
