# MTS-2026-10-04-1120Z-APP-BLD-b104-prompt-gate

Surface: Claude Code Win App (Code mode)
Role: BLD
Host: JIS-NB
Started: 2026-10-04T11:20Z
Ended:   2026-10-04T11:35Z
Status:  PARTIAL

## Task

B104. Make scripts/dev/prompt_check.ps1 blocking; add checks 6-10.

## Change

prompt_check.ps1 exits 1 on any failed check or on no input; exits 0 only when
all pass. PASS/FAIL table unchanged. Last line names failing checks.
New checks:
- 6 session ID: timestamp within 30 minutes of disk UTC (-NowUtc, -MaxSkewMinutes).
- 7 mode line: requires Mode: live or Mode: static.
- 8 placeholder: fails on any angle-bracket token like <HHMM>.
- 9 restriction words: flags do not, don't, must not, never, forbidden,
  prohibited, off-limits, keep separate, not allowed. A line passes if tagged
  OPERATOR-SET, is a quoted operator line, or appears in -OperatorWords.
- 10 signature: requires a line "P.S : All Access".

## Tests

scripts/dev/test_prompt_check.ps1 extended to 10 fixtures. Fail-before run
against pre-change HEAD: 8 of 10 fail.

## Files

- scripts/dev/prompt_check.ps1  16881 bytes, 317 lines, SHA 0d92a4faf7e1c8ad
- scripts/dev/test_prompt_check.ps1  9072 bytes, 128 lines, SHA 6f38a6892b0b96ae
- MyTradingSys/items/B104_rules_vs_gates.md  2720 bytes, 39 lines, SHA 326109e775d06cdd

All LF, no BOM, 0 non-ASCII.

## Commit

60f3250 on fast-track.

## Open

Item (C) write-time line-ending gate still open. B104 stays OPEN.

## Not run

Full run_all_tests.py gate.