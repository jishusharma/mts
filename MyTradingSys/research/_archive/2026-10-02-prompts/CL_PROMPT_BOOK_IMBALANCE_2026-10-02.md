# CL PROMPT: promote book_imbalance 0.0 fix (one file, one commit)
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Mode: Claude Code Mode (Win app, local disk).
# Budget: 1 percent weekly left. Lean execution only.

You are a Claude Code Mode session. One file. One commit.
Line 1: session ID MTS-YYYY-MM-DD-HHMMZ-CLI-BLD-bookimbal
Line 2: usage percent, or '1 assumed'.

## BUDGET

1 percent left. No subagents. No file reads outside the list below.
No exploration. Do the steps, commit, stop.

Commit-as-you-go. Only 1 percent of the weekly budget remains. If the
session is cut off mid-task, whatever is uncommitted is lost. So:
- After each numbered step that writes a file, commit that file
  immediately with a WIP message tagged "partial, unverified". Do not
  wait for the final step to batch.
- If the session ends early, the last pushed commit is a valid resume
  point.
- Do not amend or squash WIP commits. Leave the trail.
- If a step cannot be started because credits run out, stop cleanly and
  push whatever is on disk.

## BRANCH (operator directive)
CLAUDE.md says branch fast-track. Operator directive overrides for this
session: commit to main and push origin main. Reason: this is a single
small fix, gated by Build-Check, and every session today is on main.
No fast-track branch.

## OWNERSHIP
No SUPERVISOR_LOG claim needed. math_object_builder.py is under runtime/,
not execution/ or layers/alerts/. The runtime loop is down tonight
(java absent, static mode), so no live process imports it right now.

## FILES (only these)

- MyTradingSys/runtime/math_object_builder.py (target)
- MyTradingSys/runtime/math_object_builder.py.new (staged fix)
- MyTradingSys/tests/test_book_imbalance_nodata.py.new (test)

## THE CHANGE (already staged, already verified by DSA)

Line 415 of the .new adds a '_book != 0.0' condition to the ask-heavy
vs LONG guard. 0.0 means no order-book data, not ask-heavy. Comment
cites SetupCandidatesBuilder.java:581 and MarketDataSnapshot.java:213-214.
Two lines added, nothing else changed.

## STEPS

1. Fail-first. Copy the test to MyTradingSys/tests/test_book_imbalance_nodata.py
   Run: python -m pytest MyTradingSys/tests/test_book_imbalance_nodata.py -v
   It MUST fail against the old math_object_builder.py. Capture the
   failing assertion line. If it passes, STOP and report.

2. Hash before.
   Get-FileHash MyTradingSys/runtime/math_object_builder.py -Algorithm SHA256
   Expect prefix 2D9F8489.

3. Backup.
   Copy-Item MyTradingSys/runtime/math_object_builder.py MyTradingSys/runtime/math_object_builder.py.pre_bookimbal

4. Promote.
   Move-Item MyTradingSys/runtime/math_object_builder.py.new MyTradingSys/runtime/math_object_builder.py

5. Hash after + diff.
   Get-FileHash MyTradingSys/runtime/math_object_builder.py -Algorithm SHA256
   Expect prefix 02282C87. If different, STOP.
   git diff --no-index MyTradingSys/runtime/math_object_builder.py.pre_bookimbal MyTradingSys/runtime/math_object_builder.py
   Expected: one line changed (the guard) plus two comment lines.

6. Re-run the test now. It MUST pass.
   python -m pytest MyTradingSys/tests/test_book_imbalance_nodata.py -v

7. Gate.
   .\scripts\Build-Check.ps1
   STATUS must be PASS. If FAIL, STOP and report.

8. Session record. Create MyTradingSys/system/sessions/<your session ID>.md
   using the 14-field template from MyTradingSys/system/sessions/README.md.
   Fields: surface CLI, host JIS-NB, account A, model as reported,
   role BLD, branch main, branch_alias none, predecessor none,
   lanes none, started <now UTC>, ended <now UTC>, status closed,
   commits <short hash>, handoff none. One short file.

9. Index row. Append one row to MyTradingSys/system/03_FILE_INDEX.md:
   | MyTradingSys/tests/test_book_imbalance_nodata.py | test | Fail-first
   for the book_imbalance 0.0 guard. | <your session ID> | <date> |
   Then update the # SIZE: ~NKB header at the top to match the new
   byte count (round to 1 decimal).

10. Commit. All files in one commit:
    git add MyTradingSys/runtime/math_object_builder.py MyTradingSys/tests/test_book_imbalance_nodata.py MyTradingSys/system/sessions/<your session ID>.md MyTradingSys/system/03_FILE_INDEX.md
    git commit -m "fix: book_imbalance 0.0 is unknown, not ask-heavy vs LONG" -m "MTS-Session: <your session ID>"
    git push origin main

## STOP

After step 10, print the four-line verify block and stop. Do not touch
any other .new file. Do not finish Wave 2. Do not read the switchability
spec.

## VERIFY BLOCK
TASK: promote book_imbalance 0.0 fix
DONE: <one line>
VERIFIED: mechanical (hashes 2D9F8489 -> 02282C87, fail-first output, Build-Check PASS)
MISSED: <or none>

# END
