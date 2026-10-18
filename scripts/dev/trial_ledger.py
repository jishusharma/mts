"""scripts/dev/trial_ledger.py

Builder for research/TRIAL_LEDGER_BUILT.csv and research/holdout_reads.csv.
Scans all TRIAL_REGISTRY*.csv files in the repository and synthesises a clean,
append-friendly built ledger:
  (study, variant, date, split, verdict)

Rules & Invariants:
- The hand-kept MyTradingSys/research/TRIAL_LEDGER.csv is NEVER modified.
- Output sorting is stable; rerunning is byte-identical.
- Per-study counts and total row count are printed to stdout.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def find_registry_files(repo_root: Path = REPO_ROOT):
    """Find all TRIAL_REGISTRY*.csv files tracked by git, or fallback to filesystem glob."""
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "*TRIAL_REGISTRY*.csv"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        files = [repo_root / line for line in lines]
    except Exception:
        files = []

    if not files:
        files = list(repo_root.glob("**/TRIAL_REGISTRY*.csv"))

    # Filter to files under MyTradingSys/research if running in the full repo
    # Keep deterministic sorted order
    files = sorted(set(f for f in files if f.is_file()))
    return files


def derive_study_name(file_path: Path, row: dict, repo_root: Path = REPO_ROOT) -> str:
    """Derive standard study name from row or file path."""
    if row.get("study"):
        return row["study"].strip()

    rel_posix = file_path.resolve().as_posix()
    repo_posix = repo_root.resolve().as_posix()
    if rel_posix.startswith(repo_posix):
        rel = rel_posix[len(repo_posix):].lstrip("/")
    else:
        rel = rel_posix

    # Handle known structures under MyTradingSys/research
    if "fast_track_2026-09-27/bt_runs" in rel:
        if "SMOKE" in file_path.name:
            return "fast_track_smoke_2026-09-27"
        return "fast_track_bt_2026-09-27"
    if "mfe_exit_2026-10-13/rerun_dev" in rel:
        return "mfe_exit_rerun_dev_2026-10-17"

    m = re.search(r"research/(?:layer_lab/)?([^/]+)", rel)
    if m:
        return m.group(1)

    return file_path.parent.name


def extract_variant(row: dict) -> str:
    for key in ("variant", "event", "signature", "run_id"):
        val = row.get(key)
        if val is not None and val.strip():
            return val.strip()
    return ""


def extract_date(row: dict) -> str:
    val = row.get("date")
    if val is not None and val.strip():
        return val.strip()
    return ""


def extract_split(row: dict) -> str:
    for key in ("split", "data_window", "window"):
        val = row.get(key)
        if val is not None and val.strip():
            return val.strip()
    return ""


def extract_verdict(row: dict) -> str:
    for key in ("verdict", "candidate", "note"):
        val = row.get(key)
        if val is not None and val.strip():
            return val.strip()
    return ""


def build_ledger(
    registry_files=None,
    out_built_path: Path = None,
    out_holdout_path: Path = None,
    repo_root: Path = REPO_ROOT,
):
    if registry_files is None:
        registry_files = find_registry_files(repo_root)

    if out_built_path is None:
        out_built_path = repo_root / "MyTradingSys" / "research" / "TRIAL_LEDGER_BUILT.csv"

    if out_holdout_path is None:
        out_holdout_path = repo_root / "MyTradingSys" / "research" / "holdout_reads.csv"

    out_built_path.parent.mkdir(parents=True, exist_ok=True)
    out_holdout_path.parent.mkdir(parents=True, exist_ok=True)

    extracted_rows = []
    study_counts = Counter()

    for fpath in registry_files:
        with open(fpath, "r", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            file_rows = 0
            for r in reader:
                study = derive_study_name(fpath, r, repo_root=repo_root)
                variant = extract_variant(r)
                date = extract_date(r)
                split = extract_split(r)
                verdict = extract_verdict(r)

                extracted_rows.append({
                    "study": study,
                    "variant": variant,
                    "date": date,
                    "split": split,
                    "verdict": verdict,
                    # Internal sort keys
                    "_file": str(fpath),
                    "_idx": file_rows,
                })
                file_rows += 1
                study_counts[study] += 1

    # Deterministic stable ordering:
    # Sort by study, date, variant, _file, _idx
    extracted_rows.sort(key=lambda r: (r["study"], r["date"], r["variant"], r["_file"], r["_idx"]))

    # Write TRIAL_LEDGER_BUILT.csv
    fieldnames = ["study", "variant", "date", "split", "verdict"]
    with open(out_built_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for r in extracted_rows:
            writer.writerow({k: r[k] for k in fieldnames})

    # Write holdout_reads.csv skeleton if not already present
    holdout_fields = ["timestamp_utc", "study", "holdout_window", "accessor", "reason", "verdict"]
    if not out_holdout_path.exists() or out_holdout_path.stat().st_size == 0:
        with open(out_holdout_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp, lineterminator="\n")
            writer.writerow(holdout_fields)

    total_rows = len(extracted_rows)
    return study_counts, total_rows


def main(argv=None):
    if argv is None:
        argv = []
    parser = argparse.ArgumentParser(description="Build TRIAL_LEDGER_BUILT.csv from TRIAL_REGISTRY*.csv files.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Root of repository")
    args = parser.parse_args(argv)

    files = find_registry_files(args.repo_root)
    print(f"Discovered {len(files)} TRIAL_REGISTRY files:")
    for f in files:
        print(f"  - {f.relative_to(args.repo_root) if f.is_relative_to(args.repo_root) else f}")

    counts, total = build_ledger(registry_files=files, repo_root=args.repo_root)
    print("\nPer-study trial counts:")
    for study, cnt in sorted(counts.items()):
        print(f"  {study:35s}: {cnt:4d}")
    print(f"  {'TOTAL':35s}: {total:4d}")


if __name__ == "__main__":
    main(sys.argv[1:])
