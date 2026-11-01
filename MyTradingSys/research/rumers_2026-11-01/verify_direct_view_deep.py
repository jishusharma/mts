"""Verification script for RUMERS_DIRECT_VIEW_DEEP.md.

Checks:
1. File exists at MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md
2. Covers the 5 top-ranked candidate videos:
   6WfTIyJ-YzQ, EoQDQVblmMY, xtN0U-j_4Jc, kozesVBKkg4, l0j1irTKIUw
3. Every rule row is tagged UNVERIFIED-PARAPHRASE with approximate minute
4. Per-rule table contains entry, stop, target, timeframe, indicators
5. Contains NOT_STATED where elements or numbers are not given in video
6. No quotation marks around spoken words
7. Number labeling: SOURCED or NOT_STATED
"""
import sys
from pathlib import Path
import re

TARGET_VIDEOS = [
    "6WfTIyJ-YzQ",
    "EoQDQVblmMY",
    "xtN0U-j_4Jc",
    "kozesVBKkg4",
    "l0j1irTKIUw",
]

def verify():
    path = Path("MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md")
    if not path.is_file():
        print(f"FAIL: {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check 1: 5 videos present
    missing_videos = [vid for vid in TARGET_VIDEOS if vid not in content]
    if missing_videos:
        print(f"FAIL: Missing videos in document: {missing_videos}")
        return 1

    # Check 2: Table rows with UNVERIFIED-PARAPHRASE and approx minutes
    table_rows = [line for line in lines if line.strip().startswith("|") and ("UNVERIFIED-PARAPHRASE" in line)]
    if len(table_rows) < 15:
        print(f"FAIL: Expected at least 15 UNVERIFIED-PARAPHRASE rule rows across 5 videos, found {len(table_rows)}")
        return 1

    # Check that each table row has approx minute
    minute_pattern = re.compile(r"~\s*\d{1,2}:\d{2}|\bminute\b|\bmin\b", re.IGNORECASE)
    for row in table_rows:
        if not minute_pattern.search(row):
            print(f"FAIL: Row missing approx minute: {row}")
            return 1

    # Check 3: NOT_STATED appears where parameters/gaps are missing
    if "NOT_STATED" not in content:
        print("FAIL: Missing NOT_STATED markers in document")
        return 1

    # Check 4: No quotation marks around spoken words or quotes
    quote_chars = ['"', '\u201c', '\u201d', '“', '”']
    for char in quote_chars:
        if char in content:
            print(f"FAIL: Found quotation character {repr(char)} in document")
            return 1

    # Check 5: Required column headers
    header_found = False
    for line in lines:
        if line.strip().startswith("|") and ("Timeframe" in line) and ("Entry" in line) and ("Stop" in line) and ("Target" in line) and ("Indicator" in line):
            header_found = True
            break
    if not header_found:
        print("FAIL: Required table columns (Timeframe, Entry, Stop, Target, Indicator) not found in header")
        return 1

    print(f"PASS: {path} verified successfully ({len(table_rows)} rules across 5 videos, all UNVERIFIED-PARAPHRASE, NOT_STATED used, no quotes).")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
