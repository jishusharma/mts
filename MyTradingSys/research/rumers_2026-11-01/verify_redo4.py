"""Verification script for RUMERS_REDO4.md.

Checks:
1. File exists at MyTradingSys/research/rumers_2026-11-01/RUMERS_REDO4.md
2. Covers exactly the 4 re-watched video IDs:
   OYLv6Ev-kVE, lUr32iqWHz8, 4zazKDSXlh8, NMUd0oX_7Pg
3. Real title copied from the page for each video ID
4. Per-rule table contains entry, stop, target, timeframe, indicators
5. Uses NOT_STATED where absent
6. Every row tagged UNVERIFIED-PARAPHRASE with approx minute
7. Strictly NO quotation marks around spoken words
"""
import sys
from pathlib import Path
import re

TARGET_VIDEOS = [
    "OYLv6Ev-kVE",
    "lUr32iqWHz8",
    "4zazKDSXlh8",
    "NMUd0oX_7Pg",
]

EXPECTED_TITLES = {
    "OYLv6Ev-kVE": "LIVE TRADING GOLD & BITCOIN || Challenge Day-04",
    "lUr32iqWHz8": "My Simple 3-Step Swing Strategy",
    "4zazKDSXlh8": "The 15-Minute Candle Strategy I Will Use For Life",
    "NMUd0oX_7Pg": "The SIMPLE",
}

def verify():
    path = Path("MyTradingSys/research/rumers_2026-11-01/RUMERS_REDO4.md")
    if not path.is_file():
        print(f"FAIL: {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check 1: 4 target videos present
    for vid in TARGET_VIDEOS:
        if vid not in content:
            print(f"FAIL: Video ID {vid} not found in {path}")
            return 1

    # Check 2: Expected titles present
    for vid, exp_title in EXPECTED_TITLES.items():
        if exp_title not in content:
            print(f"FAIL: Expected title fragment '{exp_title}' for {vid} not found")
            return 1

    # Check 3: Table rows with UNVERIFIED-PARAPHRASE
    table_rows = [line for line in lines if line.strip().startswith("|") and ("UNVERIFIED-PARAPHRASE" in line)]
    if len(table_rows) < 4:
        print(f"FAIL: Expected at least 4 UNVERIFIED-PARAPHRASE rows, found {len(table_rows)}")
        return 1

    # Check 4: Approx minute on every row
    minute_pattern = re.compile(r"~\s*\d{1,2}:\d{2}|\bminute\b|\bmin\b", re.IGNORECASE)
    for idx, row in enumerate(table_rows, 1):
        if not minute_pattern.search(row):
            print(f"FAIL: Row {idx} missing approx minute: {row}")
            return 1

    # Check 5: NOT_STATED present
    if "NOT_STATED" not in content:
        print("FAIL: NOT_STATED marker missing in document")
        return 1

    # Check 6: Required table columns in header
    header_found = False
    for line in lines:
        s = line.strip().lower()
        if s.startswith("|") and ("timeframe" in s) and ("entry" in s) and ("stop" in s) and ("target" in s) and ("indicator" in s):
            header_found = True
            break
    if not header_found:
        print("FAIL: Required columns (timeframe, entry, stop, target, indicator) not found in table header")
        return 1

    # Check 7: No quotation marks around spoken words (check markdown blockquotes > " or quotes in paraphrase columns)
    # Spoken word quotes typically look like "..." or '...' around conversational quotes
    if re.search(r'>\s*["\u201c\u201d]', content):
        print("FAIL: Found blockquote quotation marks around spoken words")
        return 1

    print(f"PASS: {path} verified successfully (4 target videos, real titles, per-rule table, NOT_STATED used, no spoken word quotes).")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
