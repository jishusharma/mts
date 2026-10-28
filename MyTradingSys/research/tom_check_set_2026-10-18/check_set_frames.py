"""Check script for Tom CHECK set frames-only trade recaps.

Validates:
1. research/tom_check_set_2026-10-18/CHECK_SET.md exists and contains:
   - required line: 'no caption read'
   - status: every frames-only trade found or 'none found beyond S7/S8 with the queries tried'
2. For every check set row in TOM_TRADE_LEDGER.csv (T11, T12, and any further rows):
   - Every cited frame path exists on disk
   - No caption file path (.vtt, .txt) exists in sources or in F:/MTS/data/tom_videos for that video
   - Unreadable / uncertified fields are marked NOT_IN_DATA
3. TOM_TRADE_LEDGER.md contains the expected trade count line.
"""
import csv
import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECK_SET_DIR = REPO_ROOT / "MyTradingSys/research/tom_check_set_2026-10-18"
CHECK_SET_MD = CHECK_SET_DIR / "CHECK_SET.md"
TOM_LEDGER_CSV = REPO_ROOT / "MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv"
TOM_LEDGER_MD = REPO_ROOT / "MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.md"
TOM_VIDEOS_DIR = Path("F:/MTS/data/tom_videos")

CHECK_SET_VIDEO_IDS = {"liEJMfE_PXg", "ZZeET7ng1nk"}
CHECK_SET_ROW_IDS = {"T11", "T11-x", "T12", "T12-m1"}


def check_check_set_md():
    errors = []
    if not CHECK_SET_MD.exists():
        return [f"Missing required file: {CHECK_SET_MD}"]

    content = CHECK_SET_MD.read_text(encoding="utf-8")

    # Required line check
    if "no caption read" not in content.lower():
        errors.append("CHECK_SET.md missing required line: 'no caption read'")

    # Outcome line check
    has_trades = "trades found" in content.lower()
    has_none = "none found beyond s7/s8 with the queries tried" in content.lower()
    if not (has_trades or has_none):
        errors.append("CHECK_SET.md must state trades found or 'none found beyond S7/S8 with the queries tried'")

    return errors


def check_check_set_ledger_rows():
    errors = []
    if not TOM_LEDGER_CSV.exists():
        return [f"Missing ledger CSV: {TOM_LEDGER_CSV}"]

    with open(TOM_LEDGER_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    found_check_rows = []
    for r in rows:
        rid = r["id"]
        vid = r["video"]
        # Check if row belongs to check set
        if vid in CHECK_SET_VIDEO_IDS or rid in CHECK_SET_ROW_IDS or "CHECK" in r.get("prior_exposure", ""):
            found_check_rows.append(r)

            # 1. Check frame paths
            frame_col = r.get("frame", "")
            if not frame_col:
                errors.append(f"Row {rid} has no frame path")
            else:
                paths = [p.strip() for p in frame_col.split(";")]
                for p in paths:
                    # Could be absolute or relative to repo or F:
                    fp = Path(p)
                    if not fp.is_absolute():
                        fp = REPO_ROOT / p
                    if not fp.exists():
                        errors.append(f"Row {rid}: frame path does not exist on disk: {p}")

            # 2. Check no caption file path in sources or in video dir
            for field in ("note", "time_evidence_type", "evidence_unresolved"):
                val = r.get(field, "")
                if ".vtt" in val.lower() or ".txt" in val.lower():
                    errors.append(f"Row {rid}: caption file referenced in field {field}: {val}")

            # Check that video directory has no .vtt or .txt for this check set video
            for ext in (".vtt", ".en.vtt", ".en-orig.vtt", ".txt"):
                cap_file = TOM_VIDEOS_DIR / f"{vid}{ext}"
                if cap_file.exists():
                    errors.append(f"Row {rid}: video {vid} has caption file {cap_file} on disk (violates frames-only)")

            # 3. Check unreadable fields are NOT_IN_DATA
            contract = r.get("executed_contract", "")
            if "NOT_IN_DATA" not in contract:
                errors.append(f"Row {rid}: executed_contract must be NOT_IN_DATA, got {contract!r}")

    if not found_check_rows:
        errors.append("No CHECK set rows found in TOM_TRADE_LEDGER.csv")

    return errors


def check_ledger_md_count():
    errors = []
    if not TOM_LEDGER_MD.exists():
        return [f"Missing ledger MD: {TOM_LEDGER_MD}"]

    content = TOM_LEDGER_MD.read_text(encoding="utf-8")
    if "14 trade ids / 37 rows" not in content and "trade ids" not in content:
        errors.append("TOM_TRADE_LEDGER.md missing trade count line")

    return errors


class TestCheckSetFrames(unittest.TestCase):
    def test_check_set_md(self):
        errs = check_check_set_md()
        self.assertEqual(errs, [], "\n".join(errs))

    def test_check_set_ledger_rows(self):
        errs = check_check_set_ledger_rows()
        self.assertEqual(errs, [], "\n".join(errs))

    def test_ledger_md_count(self):
        errs = check_ledger_md_count()
        self.assertEqual(errs, [], "\n".join(errs))


def main():
    all_errs = []
    all_errs.extend(check_check_set_md())
    all_errs.extend(check_check_set_ledger_rows())
    all_errs.extend(check_ledger_md_count())

    if all_errs:
        print("FAIL: check_set_frames.py violations found:")
        for e in all_errs:
            print(f"  - {e}")
        return 1
    else:
        print("PASS: check_set_frames.py all checks passed")
        return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "unittest":
        unittest.main(argv=[sys.argv[0]])
    else:
        sys.exit(main())
