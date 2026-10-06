# MTS-2026-10-04-1105Z-APP-BLD-b129-harness

Surface: Claude Code Win App (Code mode)
Role: BLD
Host: JIS-NB
Started: 2026-10-04T11:05Z
Ended:   2026-10-04T11:20Z
Status:  CLOSED

## Task

B129. Rework MyTradingSys/tests/test_b074_rule_order.py so the fail-before
proof fires on the assertion, not on a ParserError.

## Change

Held a parsed PowerShell AST. The test now extracts code via
[System.Management.Automation.Language.Parser]::ParseFile, so it no longer
depends on line layout.
- B074: takes the Compute-Verdict function by name.
- B069: takes the statements from the $umsCmd assignment through the $s assignment.
- Optional env var B074_PS1 points the test at another copy of the script
  (used to run against 8604bc0).

## Two-run proof

- Run 1, current HEAD: 2 passed.
- Run 2, 8604bc0 start-trading-day.ps1: 2 failed by assertion, no ParserError.
  B074: old file gives WAIT_PROOF|flow contradiction; test expects
  WAIT_RR|broken below_val + CVD falling vs LONG.
  B069: old log line is state_updated with no exit=0.

## Files

- MyTradingSys/tests/test_b074_rule_order.py (4469 bytes, 96 lines, SHA256 2ae78b81fe69ebba)
- MyTradingSys/items/B129_b074_test_harness_fragility.md (1700 bytes, 38 lines, SHA256 68e8a661c8b9b105)

Both LF, no BOM, 0 non-ASCII.

## Commit

18ed141 on fast-track.

## Not run

Full run_all_tests gate.