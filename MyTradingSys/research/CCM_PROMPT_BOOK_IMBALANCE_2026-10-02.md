# CCM PROMPT: promote book_imbalance 0.0 fix (one file, one commit)
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Mode: Claude Code Mode (Win app, local disk).
# Budget: 1 percent weekly left. Lean execution only.

You are a Claude Code Mode session. One file. One commit.
Line 1: session ID MTS-YYYY-MM-DD-HHMMZ-CLI-BLD-bookimbal
Line 2: usage percent, or '1 assumed'.

## BUDGET

1 percent left. No subagents. No file reads outside the list below.
No exploration. Do the steps, commit, stop.

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

8. Commit. Two commands:
   git add MyTradingSys/runtime/math_object_builder.py MyTradingSys/tests/test_book_imbalance_nodata.py
   git commit -m "fix: book_imbalance 0.0 is unknown, not ask-heavy vs LONG" -m "MTS-Session: <your session ID>"
   git push origin main

## STOP

After step 8, print the four-line verify block and stop. Do not touch
any other .new file. Do not finish Wave 2. Do not read the switchability
spec.

## VERIFY BLOCK
TASK: promote book_imbalance 0.0 fix
DONE: <one line>
VERIFIED: mechanical (hashes 2D9F8489 -> 02282C87, fail-first output, Build-Check PASS)
MISSED: <or none>

# END
