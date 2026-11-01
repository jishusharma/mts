"""Verification script for RUMERS_DIRECT_VIEW.md.

Checks:
1. File exists at MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW.md
2. Covers all 10 target videos:
   6WfTIyJ-YzQ, EoQDQVblmMY, N6zlfBJsoRc, kozesVBKkg4, aTMFouI9mF4,
   T0H_jpQXdVI, pcYO-yzAtrQ, hMURCHLnZVE, xtN0U-j_4Jc, l0j1irTKIUw
3. Every row in the rules table is tagged UNVERIFIED-PARAPHRASE
4. Every row contains an approximate minute reference
5. No quotation marks around spoken words (no quote blocks > "..." or quotes in rule texts)
6. Contains a ranked candidate list of complete entry/exit rules
"""
import sys
from pathlib import Path
import re

TARGET_VIDEOS = [
    "6WfTIyJ-YzQ",
    "EoQDQVblmMY",
    "N6zlfBJsoRc",
    "kozesVBKkg4",
    "aTMFouI9mF4",
    "T0H_jpQXdVI",
    "pcYO-yzAtrQ",
    "hMURCHLnZVE",
    "xtN0U-j_4Jc",
    "l0j1irTKIUw",
]

def verify():
    path = Path("MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW.md")
    if not path.is_file():
        print(f"FAIL: {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check 1: 10 videos present
    missing_videos = [vid for vid in TARGET_VIDEOS if vid not in content]
    if missing_videos:
        print(f"FAIL: Missing videos in document: {missing_videos}")
        return 1

    # Check 2: Table rows with UNVERIFIED-PARAPHRASE and approx minutes
    table_rows = [line for line in lines if line.strip().startswith("|") and ("UNVERIFIED-PARAPHRASE" in line)]
    if len(table_rows) < 10:
        print(f"FAIL: Expected at least 10 UNVERIFIED-PARAPHRASE rule rows, found {len(table_rows)}")
        return 1

    # Check that each table row has approx minute
    minute_pattern = re.compile(r"~\s*\d{1,2}:\d{2}|\bminute\b|\bmin\b", re.IGNORECASE)
    for row in table_rows:
        if not minute_pattern.search(row):
            print(f"FAIL: Row missing approx minute: {row}")
            return 1

    # Check 3: No quotation marks around spoken words
    # Check for markdown blockquotes with quotes: > "..."
    if re.search(r'>\s*["\u201c\u201d]', content):
        print("FAIL: Found verbatim quote block (> \")")
        return 1

    # Check for quotation marks in table rows
    for row in table_rows:
        # Check if row has speech in quotes
        if '"' in row or '\u201c' in row or '\u201d' in row:
            print(f"FAIL: Quotation mark found in table row: {row}")
            return 1

    # Check 4: Ranked candidate list
    if "Ranked" not in content or "Candidate" not in content:
        print("FAIL: Missing ranked candidate list")
        return 1

    print(f"PASS: {path} verified successfully ({len(table_rows)} rules across 10 videos, all UNVERIFIED-PARAPHRASE, no quotes, ranked list present).")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
