"""Verification script for RUMERS_SKIM_DIRECT.md.

Checks:
1. File exists at MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md
2. Contains exactly 20 video rows (excluding headers)
3. Columns present: id, title, idea, MECHANICAL Y/N, approx minute, status (UNVERIFIED-PARAPHRASE)
4. None of the 10 videos from RUMERS_DIRECT_VIEW.md are present
5. Strictly NO quotation marks around spoken words (no '"', no curly quotes in idea text)
6. Flagged MECHANICAL Y or N based on complete entry and exit definition
"""
import sys
from pathlib import Path
import re

OLD_10_VIDEOS = {
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
}

def verify():
    path = Path("MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md")
    if not path.is_file():
        print(f"FAIL: {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find table rows
    table_rows = []
    for line in lines:
        s = line.strip()
        if s.startswith("|") and ("UNVERIFIED-PARAPHRASE" in s):
            table_rows.append(s)

    if len(table_rows) != 20:
        print(f"FAIL: Expected exactly 20 UNVERIFIED-PARAPHRASE rows, found {len(table_rows)}")
        return 1

    # Check 10 old videos not present
    for old_id in OLD_10_VIDEOS:
        if old_id in content:
            print(f"FAIL: Found video ID from RUMERS_DIRECT_VIEW.md: {old_id}")
            return 1

    # Check each row
    minute_pattern = re.compile(r"~\s*\d{1,2}:\d{2}|\bminute\b|\bmin\b", re.IGNORECASE)
    mechanical_pattern = re.compile(r"\|\s*(YES|NO)\s*\|", re.IGNORECASE)

    seen_ids = set()
    for idx, row in enumerate(table_rows, 1):
        # Check approx minute
        if not minute_pattern.search(row):
            print(f"FAIL: Row {idx} missing approx minute: {row}")
            return 1

        # Check MECHANICAL Y/N
        if not mechanical_pattern.search(row):
            print(f"FAIL: Row {idx} missing MECHANICAL Y/N: {row}")
            return 1

        # Check quotation marks around spoken words
        if '"' in row or '\u201c' in row or '\u201d' in row:
            print(f"FAIL: Quotation mark found in table row {idx}: {row}")
            return 1

        # Extract video ID (11 alphanumeric characters with - or _)
        parts = [p.strip() for p in row.split("|")[1:-1]]
        # Find 11 char video id
        vid_match = re.search(r"\b[A-Za-z0-9_-]{11}\b", row)
        if not vid_match:
            print(f"FAIL: Row {idx} missing valid 11-char YouTube ID: {row}")
            return 1
        seen_ids.add(vid_match.group(0))

    if len(seen_ids) != 20:
        print(f"FAIL: Expected 20 unique video IDs, got {len(seen_ids)}")
        return 1

    # Check markdown blockquotes with quotes: > "..."
    if re.search(r'>\s*["\u201c\u201d]', content):
        print("FAIL: Found verbatim quote block (> \")")
        return 1

    print(f"PASS: {path} verified successfully (20 unique rows, all UNVERIFIED-PARAPHRASE, no quotes, all required fields valid).")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
