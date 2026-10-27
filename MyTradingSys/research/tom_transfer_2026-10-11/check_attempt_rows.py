"""Test / validation script for card tom-ledger-add-the-losing-first-attempts.
Verifies that rows T1-a0 and T7-a0 exist in TOM_TRADE_LEDGER.csv with exact quotes,
row_kind=ATTEMPT_LOST, family=spike_fade, NOT_IN_DATA for unquoted numeric fields,
and that the quotes are genuine substrings of the canonical transcripts.
"""
import csv
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
REPO = DIR.parents[2]
LEDGER = DIR / "TOM_TRADE_LEDGER.csv"
GROUPS = DIR / "TOM_LEDGER_CANONICAL_GROUPS.csv"
TRANSCRIPTS = REPO / "raw_transcripts_canonical"

Q1 = "I was already a bit too early this morning. Took a stop loss as well."
Q2 = "I had already been stopped out in the pre-session when I was a bit too early, losing one R."

def check():
    if not LEDGER.exists():
        print(f"FAIL: {LEDGER} does not exist")
        return 1
    
    with open(LEDGER, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    
    by_id = {r["id"]: r for r in rows}
    
    # 1. Existence check
    for req in ("T1-a0", "T7-a0"):
        if req not in by_id:
            print(f"FAIL: {req} missing from {LEDGER.name}")
            return 1
    
    # 2. T1-a0 check
    r1 = by_id["T1-a0"]
    assert r1["canonical_id"] == "T1", f"T1-a0 canonical_id != T1: {r1['canonical_id']}"
    assert r1["row_kind"] == "ATTEMPT_LOST", f"T1-a0 row_kind != ATTEMPT_LOST: {r1['row_kind']}"
    assert r1["family"] == "spike_fade", f"T1-a0 family != spike_fade: {r1['family']}"
    assert r1["video"] == "n7ZSkjb7JXs", f"T1-a0 video != n7ZSkjb7JXs: {r1['video']}"
    assert r1["entry"] == "NOT_IN_DATA", f"T1-a0 entry != NOT_IN_DATA: {r1['entry']}"
    assert r1["stop"] == "NOT_IN_DATA", f"T1-a0 stop != NOT_IN_DATA: {r1['stop']}"
    assert r1["target"] == "NOT_IN_DATA", f"T1-a0 target != NOT_IN_DATA: {r1['target']}"
    assert Q1 in r1["note"], f"T1-a0 note missing quote Q1: {r1['note']}"
    
    # 3. T7-a0 check
    r7 = by_id["T7-a0"]
    assert r7["canonical_id"] == "T7", f"T7-a0 canonical_id != T7: {r7['canonical_id']}"
    assert r7["row_kind"] == "ATTEMPT_LOST", f"T7-a0 row_kind != ATTEMPT_LOST: {r7['row_kind']}"
    assert r7["family"] == "spike_fade", f"T7-a0 family != spike_fade: {r7['family']}"
    assert r7["video"] == "l8RZrBfzvp4", f"T7-a0 video != l8RZrBfzvp4: {r7['video']}"
    assert r7["entry"] == "NOT_IN_DATA", f"T7-a0 entry != NOT_IN_DATA: {r7['entry']}"
    assert r7["stop"] == "NOT_IN_DATA", f"T7-a0 stop != NOT_IN_DATA: {r7['stop']}"
    assert r7["target"] == "NOT_IN_DATA", f"T7-a0 target != NOT_IN_DATA: {r7['target']}"
    assert Q2 in r7["note"], f"T7-a0 note missing quote Q2: {r7['note']}"
    
    # 4. Transcripts substring check
    t1_txt = (TRANSCRIPTS / "n7ZSkjb7JXs_raw.txt").read_text(encoding="utf-8")
    assert Q1 in t1_txt, f"Q1 not found in n7ZSkjb7JXs_raw.txt"
    
    t7_txt = (TRANSCRIPTS / "l8RZrBfzvp4_raw.txt").read_text(encoding="utf-8")
    assert Q2 in t7_txt, f"Q2 not found in l8RZrBfzvp4_raw.txt"
    
    # 5. Check GROUPS membership
    if GROUPS.exists():
        with open(GROUPS, encoding="utf-8", newline="") as f:
            g_rows = list(csv.DictReader(f))
        g_by_id = {g["canonical_id"]: g for g in g_rows}
        assert "T1-a0" in g_by_id["T1"]["member_row_ids"].split(";"), "T1-a0 not in T1 member_row_ids"
        assert "T7-a0" in g_by_id["T7"]["member_row_ids"].split(";"), "T7-a0 not in T7 member_row_ids"
    
    print("PASS: check_attempt_rows passed all checks")
    return 0

if __name__ == "__main__":
    sys.exit(check())
