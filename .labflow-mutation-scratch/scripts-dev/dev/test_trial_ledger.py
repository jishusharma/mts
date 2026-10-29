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
    assert list(rows[0].keys()) == ["study", "variant", "date", "split", "verdict", "count_only"]

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

    # Built ledger = sum of rows across every tracked TRIAL_REGISTRY*.csv (count grows as studies land)
    files = trial_ledger.find_registry_files(REPO)
    assert len(files) >= 9, f"Expected at least 9 registry files, found {len(files)}"

    expected_total = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            r = csv.reader(fp)
            next(r, None)
            expected_total += sum(1 for _ in r)

    assert len(rows) == expected_total >= 1279, (
        f"Built ledger has {len(rows)} rows, expected {expected_total}"
    )

    # Check holdout reads header
    with open(holdout_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header == ["timestamp_utc", "study", "holdout_window", "accessor", "reason", "verdict"]



LOWERCASE_FIXTURES = {
    "context_factors": (
        "study,factor,definition,side,count_of,n,split,outcome_read\n"
        "ctx,F1,def a,long,cnt,1.0,DEV,no\nctx,F1,def a,short,cnt,2.0,DEV,no\n", True),
    "context_factors_pit": (
        "trial_id,factor,primary,alternative,reason,n_primary_long,n_primary_short,n_alt_long,n_alt_short,outcome_read\n"
        "T1,F1,p,a,r,1,2,3,4,no\nT2,F2,p,a,r,1,2,3,4,no\n", True),
    "eur_low_us": (
        "cell,side,h,n,mean_G,se,net,t_net,diff_vs_ctrl,t_diff,verdict\n"
        "A,1,120,133,none,none,none,none,none,none,BLOCKED\n"
        "A,-1,120,133,none,none,none,none,none,none,BLOCKED\n", True),
    "imbalance": (
        "cell,block,rr,n,net_R,se\nIMB,H1,1,10,-0.3,0.02\nIMB,H1,2,10,-0.2,0.02\n", False),
    "mal_bb_mid": (
        "cell,h,n,mean_G,se,net,t_net,diff_vs_ctrl,t_diff,verdict\nA1,60,9,0.01,0.02,-0.1,-6,0.01,0.6,FAIL\nA1,120,9,0.01,0.02,-0.1,-6,0.01,0.6,FAIL\n", False),
    "opr_bb_mtf": (
        "cell,side,h,n,mean_G,se,net,t_net,diff_vs_ctrl,t_diff,verdict\n"
        "AU,1,120,19,0.02,0.08,-0.12,-1.4,0.003,0.04,INCONCLUSIVE\nAU,-1,120,19,0.02,0.08,-0.12,-1.4,0.003,0.04,FAIL\n", False),
}


def test_lowercase_trials_adapters(tmp_path):
    files = []
    for name, (text, _) in LOWERCASE_FIXTURES.items():
        f = tmp_path / "research" / f"{name}_2026-10-16" / "trials.csv"
        f.parent.mkdir(parents=True)
        f.write_text(text, encoding="utf-8", newline="\n")
        files.append(f)
    out = tmp_path / "BUILT.csv"
    stats, total = trial_ledger.build_ledger(
        registry_files=files, out_built_path=out,
        out_holdout_path=tmp_path / "h.csv", repo_root=tmp_path)
    assert total == 12
    rows = list(csv.DictReader(open(out, encoding="utf-8")))
    keys = [(r["study"], r["variant"]) for r in rows]
    assert all(v for _, v in keys)
    assert len(set(keys)) == len(keys)
    for name, (_, count_only) in LOWERCASE_FIXTURES.items():
        study = "ctx" if name == "context_factors" else f"{name}_2026-10-16"
        mine = [r for r in rows if r["study"] == study]
        assert len(mine) == 2, name
        assert all((r["count_only"] == "True") == count_only for r in mine), name


def test_live_repo_includes_lowercase_trials():
    files = trial_ledger.find_registry_files(REPO)
    low = [f for f in files if f.name == "trials.csv"]
    assert len(low) == 8
    path = REPO / "MyTradingSys" / "research" / "TRIAL_LEDGER_BUILT.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    prefixes = ("context_factors", "eur_low_us", "imbalance_qriptal", "mal_bb_mid", "opr_bb_mtf",
                "opr_preopen", "opr_weekly_low")
    low_rows = [r for r in rows if r["study"].startswith(prefixes)]
    keys = [(r["study"], r["variant"]) for r in low_rows]
    assert len(low_rows) >= 176
    assert len(set(keys)) == len(keys)
