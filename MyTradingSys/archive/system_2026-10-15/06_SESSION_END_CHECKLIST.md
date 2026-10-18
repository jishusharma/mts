# SUPERSEDED 2026-10-07

The live close procedure lives in DSA_SESSION_PROMPT.md section 12 (SESSION END)
and section 13b (SESSION HANDOFF NOTE). This file is kept as a historical
reference. Sessions close by the handoff and the section 11 refresh, not by
this checklist.

---

# SESSION-END VALIDATION PROTOCOL
# File: system/06_SESSION_END_CHECKLIST.md
# Purpose: Run this checklist BEFORE closing any session. Catches the errors 
#          that occurred in the 2026-08-29 cross-trader session.
# Rule: NO SESSION CLOSES until this checklist is completed and signed off.
# ---

## SECTION 1: FILE SYSTEM CLAIMS

For EVERY directory or file you claimed to create/modify:

```
[ ] Run: find <claimed_path> -type f | wc -l
[ ] Run: find <claimed_path> -type d
[ ] Verify output matches your claims
```

**What caught:** cryptocred/ and crypnuevo/ dirs claimed but not created.

---

## SECTION 2: SCHEMA COMPLIANCE (For DSA-dependent rules)

For EVERY rule you marked "READY" or "NO DSA CHANGES NEEDED":

```
[ ] Read data_schema_v1.0.md
[ ] List the EXACT field names your rule needs
[ ] Confirm each field exists in the schema
[ ] If ANY field missing → re-tag as BLOCKED, list missing fields
```

**What caught:** A.1 needed `hours_in_structure` (missing), A.2 needed 
`volume_relative` (missing). Both were falsely marked "READY".

---

## SECTION 3: SNAPSHOT VALIDATION (Rule 35)

For EVERY rule you claim "validated against N snapshots":

```
[ ] List the exact file paths of all N snapshots
[ ] Show the verdict for each snapshot
[ ] Show how the rule changes the verdict on at least 1 snapshot
[ ] Screenshots/charts alone do NOT count as snapshots
```

**What caught:** "3 snapshots" = 1 JSON + 3 screenshots. Screenshots are 
visual context, not verdict-generating snapshots.

---

## SECTION 4: DECISIONS LOG

For ANY architectural decision, phase change, or significant finding:

```
[ ] Read 02b_DECISIONS_LOG.md
[ ] Confirm your decision is the TOP entry
[ ] If missing → append before closing session
```

**What caught:** Cross-trader phase launch was not logged.

---

## SECTION 5: TASK NUMBER INTEGRITY

For ANY DSA_TASK_XXX or SYS_AI_TASK_XXX you reference:

```
[ ] Run: ls C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\market_data/dsa_task_* 
          (or relevant task directory)
[ ] Confirm the file exists
[ ] If it doesn't exist → either create it or remove the reference
```

**What caught:** DSA_TASK_011 was referenced but no file existed.

**Updated 2026-09-03:** Full DSA task audit revealed 10 of 11 task numbers have no file. See `runtime_data/DSA_TASK_INDEX.md`. Rule strengthened: no new DSA_TASK_XXX without adding to index FIRST. Also: `03_FILE_INDEX.md` falsely claimed 3 DSA task files were archived — they never existed. Always verify archive claims against actual directory contents.

---

## SECTION 6: SELF-CONSISTENCY

```
[ ] Read your session's main output file (consolidation, report, etc.)
[ ] Check for contradictions:
    - "NO INTEGRATION" policy vs "READY" tags
    - "Zero contradictions" claim vs actual contradictions found
    - "All done" vs incomplete items
[ ] If contradictions found → fix before closing
```

**What caught:** "NO INTEGRATION until all 7 extracted" but 2 rules 
marked "READY" (implies integration-ready now).

---

## SECTION 7: TAG INTEGRITY

For EVERY rule tagged CONFIRM/CLARIFY/GAP/REJECT:

```
[ ] Re-read the original transcript segment
[ ] Verify the quote is VERBATIM (not paraphrased)
[ ] Verify the tag is correct (not upgraded to sound more important)
[ ] Verify the Source GPS (Video ID + timestamp) is accurate
```

**What caught:** None in this session, but this is the #1 source of 
contamination in prior sessions.

---

## SIGN-OFF BLOCK

Copy this block and fill it in at session end:

```
SESSION SIGN-OFF — 2026-XX-XX
Validator: sys_AI

[ ] Section 1 (File claims) — PASSED / FAILED: ___
[ ] Section 2 (Schema compliance) — PASSED / FAILED: ___
[ ] Section 3 (Snapshot validation) — PASSED / FAILED: ___
[ ] Section 4 (Decisions Log) — PASSED / FAILED: ___
[ ] Section 5 (Task numbers) — PASSED / FAILED: ___
[ ] Section 6 (Self-consistency) — PASSED / FAILED: ___
[ ] Section 7 (Tag integrity) — PASSED / FAILED: ___

FAILURES FOUND: ___
CORRECTIONS MADE: ___
SESSION STATUS: CLEAR TO CLOSE / NEEDS FIXES
```

---

## AUTOMATED VALIDATION (Where Possible)

Some checks can be scripted. Run this Python block at session end:

```python
import os, json

errors = []

# Check 1: Dirs claimed in session exist
claimed_dirs = [
    "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys/extracts/cryptocred/raw",
    "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys/extracts/cryptocred/extracted",
    "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys/extracts/crypnuevo/raw",
    "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys/extracts/crypnuevo/extracted",
]
for d in claimed_dirs:
    if not os.path.isdir(d):
        errors.append(f"MISSING DIR: {d}")

# Check 2: DSA task files referenced exist
task_refs = []  # Fill in any DSA_TASK_XXX you referenced
task_dir = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\market_data"
for task in task_refs:
    if not os.path.exists(os.path.join(task_dir, task)):
        errors.append(f"MISSING TASK FILE: {task}")

# Check 3: Decisions log has today's entry
log_path = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\system/02b_DECISIONS_LOG.md"
with open(log_path) as f:
    content = f.read()
today = "2026-08-29"  # Update date
if today not in content[:500]:  # Check top of file
    errors.append(f"MISSING DECISIONS LOG ENTRY for {today}")

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(f"  - {e}")
else:
    print("VALIDATION PASSED — all checks clear")
```

---

## SESSION SIGN-OFF — 2026-08-31
Validator: sys_AI

[x] Section 1 (File claims) — PASSED: math_object_builder.py, test_math_object_builder.py, mts_math.py, test_mts_math.py all exist at claimed paths
[x] Section 2 (Schema compliance) — PASSED: No DSA schema changes needed (math layer uses existing fields)
[x] Section 3 (Snapshot validation) — PASSED: 98/98 tests pass, determinism verified
[x] Section 4 (Decisions Log) — PASSED: No new architectural decisions (implementation of existing plan)
[x] Section 5 (Task numbers) — PASSED: No new task numbers referenced
[x] Section 6 (Self-consistency) — PASSED: "AI never recomputes math" rule consistent across all files
[x] Section 7 (Tag integrity) — PASSED: No new extractions tagged

FAILURES FOUND: None
CORRECTIONS MADE: None
SESSION STATUS: CLEAR TO CLOSE

---
# END

---

---

## SESSION SIGN-OFF TEMPLATE (CURRENT)

Use this template for the current session. Historical sign-offs are preserved above.



---
# END
