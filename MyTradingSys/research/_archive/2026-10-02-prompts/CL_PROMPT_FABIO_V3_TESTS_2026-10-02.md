# CL PROMPT: Fabio v3 tests, one file at a time
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Mode: CL (Win app, Code mode, local disk).
# Account: B (jishu.awgp). Weekly pool small. One file per prompt.
# Scope: this prompt writes ONE test file, then stops. Repeat per file.

You are a CL session. One test file. Then stop.
Line 1: session ID MTS-YYYY-MM-DD-HHMMZ-CLI-BLD-fabio-tests
Line 2: usage percent, or 'unknown'.

## BUDGET AND SAVE-WORK DISCIPLINE

Weekly pool is nearly spent. Rules in order:

1. No subagents. No exploration. No file reads outside FILES.
2. Exactly one test file this prompt. Do not open a second.
3. One pytest run only, after the file is written. Fail-first proof
   for this file.
4. Do NOT run git add, git commit, or git push. The classifier blocks
   them. DSA commits from the desktop.
5. If a tool call is denied twice in a row, or chat shows 0 percent:
   stop and print the verify block. Whatever is on disk survives.
6. Never refuse work for budget.

## FILES (only these)

READ:
- MyTradingSys/backtest/layers/fabio/v3/signals.py.new (the module under test)
- MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md section 3 only (S1-S9 definitions)
- MyTradingSys/backtest/layers/FORMULAS.md (only the sections signals.py references)

WRITE:
- MyTradingSys/backtest/layers/fabio/v3/tests/test_signals.py.new

## THE FILE

One pytest file for signals.py. Requirements:

- Hand-built bars, no external data.
- Every test name states the spec rule: "test_S5_breakout_requires_pressure_direction" etc.
- One test per signal S1..S9 where signals.py exposes it.
- One test that fails on a broken copy of signals.py: flip the S5
  direction check inside a copy. Show the failing run.
- No mocks. No imports outside stdlib, pytest, and the module under test.

Do not touch any other file. Do not create __init__.py. Do not edit
signals.py.new.

## RUN ONCE

After writing the file, run exactly:

  python -m pytest MyTradingSys/backtest/layers/fabio/v3/tests/test_signals.py.new -v

If pytest cannot collect a .new file (likely: pytest collects .py),
then:
  - Copy the test to MyTradingSys/backtest/layers/fabio/v3/tests/test_signals.py
  - Run pytest against that path
  - Delete the .py copy after. Keep only the .new on disk.

Report the pass/fail counts.

## STOP EARLY IF

- Any tool call denied twice.
- Chat header shows 0 percent.
- You find yourself about to read a 4th file.

## STOP

After the run, reply with:
- full path of test_signals.py.new
- line count
- pass/fail counts
- the failing run output for the broken-copy case (or "cannot show, one run only")
Then stop.

DSA commits from the desktop and writes the next-file prompt.

## VERIFY BLOCK
TASK: write fabio/v3/tests/test_signals.py.new
DONE: <one line>
VERIFIED: <mechanical | routed | unverifiable-on-this-surface; name it>
MISSED: <anything dropped, or none>

# END
