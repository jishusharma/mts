# CL PROMPT: Fabio v3 core, engine.py only
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Mode: CL (Claude Local, Win app Code mode, local disk).
# Account: B (jishu.awgp). Weekly pool ~1 percent. Use the remainder now.
# Scope: one file (engine.py.new). No subagents. Commit as you go.

You are a CL session. One file. One task: engine.py.
Line 1: session ID MTS-YYYY-MM-DD-HHMMZ-CLI-BLD-fabio-engine
Line 2: usage percent, or '1 assumed'.

## BUDGET AND SAVE-WORK DISCIPLINE

1 percent weekly left. Every token counts. Rules, in order:

1. No subagents. No exploration. No file reads outside FILES.
2. One file to write: engine.py.new. Nothing else.
3. Do not run pytest. Do not run Build-Check. Do not import the
   module. The 1 percent does not cover a test run. Gate work happens
   after weekly reset.
4. Save-work checkpoints. Commit and push at these points:
   a. Immediately after engine.py.new is on disk (complete or partial).
   b. Immediately after each successful edit to engine.py.new.
   c. Before any read over 200 lines if there is unsaved work.
5. If a tool call times out or is denied twice in a row: push what is
   on disk with a WIP tag, print the verify block, stop.
6. Never refuse work for budget. Never amend a WIP commit.

## FILES (only these)

READ:
- MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md
  (sections 3, 4, 5, 7.1, 10, 11 only; do not read the rest)
- MyTradingSys/backtest/layers/fabio/v3/signals.py.new
- MyTradingSys/backtest/layers/fabio/v3/models.py.new
- MyTradingSys/backtest/layers/fabio/v3/fill.py.new
- MyTradingSys/backtest/layers/fabio/v3/manage.py.new
- MyTradingSys/backtest/layers/fabio/v3/costs.py.new
- MyTradingSys/backtest/layers/fabio/v3/day_gates.py.new
- MyTradingSys/backtest/layers/fabio/v3/__init__.py.new

WRITE:
- MyTradingSys/backtest/layers/fabio/v3/engine.py.new

Do NOT read pending_test_fabio_v3.py. Do NOT read any other file.

## THE FILE

Public API:

  run(bars, config) -> {
      verdict, model, side, entry, stop, target,
      management, diagnostics
  }

Spec rules:
- verdict vocabulary mirrors FABIO_V3_SPEC section 4 state names.
- Section 4 defines models A, B, C, D. The engine runs them
  independently per window and reports the first that fires.
- Config keys come from section 7.1. Grid params (NS-grid) are
  REQUIRED config, no defaults.
- Imports: stdlib + v3 siblings + orderflow_bars + fees (B081).
  No imports from execution/ or layers/alerts/.

Every decision cites a spec section as a comment at the line. Write
"unknown: <what>" where the spec is silent, then continue.

## COMMIT-AS-YOU-GO (exact commands)

After engine.py.new is on disk (complete or partial):

  git add -f MyTradingSys/backtest/layers/fabio/v3/engine.py.new
  git commit -m "fabio v3: engine.py (WIP, unverified)" -m "MTS-Session: <your session ID>"
  git push origin main

If you edit engine.py.new again, repeat the three commands with an
updated WIP message. Never batch at the end.

After the file is final, one more commit for the bookkeeping:

  MyTradingSys/system/sessions/<session ID>.md  (14 fields, model=see-chat)
  MyTradingSys/system/03_FILE_INDEX.md          (one row for engine.py.new)
  MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md (one entry)

## STOP EARLY IF

Stop and print the verify block if any of these:

- Any tool call is denied or times out twice in a row.
- Chat header shows 0 percent remaining.
- You are about to read more than 3 files to write engine.py.
- Spec is silent on a needed decision and no sibling module already
  answers it. Write "unknown: <what>" at that line and continue.

## STOP

After the final commit, print the four-line verify block and stop.
Do not run tests. Do not write README. Do not review the other
modules. That is a future session after weekly reset.

## VERIFY BLOCK
TASK: write fabio/v3/engine.py
DONE: <one line>
VERIFIED: <mechanical | routed | unverifiable-on-this-surface; name it>
MISSED: <anything dropped, or none>

# END
