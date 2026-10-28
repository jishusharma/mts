# B086 - dispatcher demo launched a second CL writer

Status: CLOSED. Severity: HIGH. Opened 2026-10-03.

## Defect

The queue-dispatcher build session ran mts go as a smoke test.
That launched a real second claude session against the same tree.
The second session edited three files before it was killed.

One-writer-per-file-set rule violated. Two writers on one tree.

## Evidence

Session MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher, own words:
  My own mts go check launched a real claude session on the R4-T2
  prompt. It edited htf_context_live.py, test_htf_context_live.py
  and BUILD_PIPELINE.md (row 2.2 now LANDED) before I killed it.
  I left those changes uncommitted and did not revert them. That
  session wrote no record.

Files touched by the second session (uncommitted at HEAD):
  MyTradingSys/backtest/layers/fabio/htf_context_live.py
  MyTradingSys/backtest/layers/fabio/test_htf_context_live.py
  MyTradingSys/runtime/BUILD_PIPELINE.md (row 2.2 to LANDED)

## Fix (Claude decides mechanism)

The dispatcher must not launch a live writer as part of its own
session. Candidate shapes:
  - mts go defaults to dry-run (prints the composed prompt).
  - a separate flag or keystroke is required to launch live.
  - the dispatcher checks a lock file before launching.
  - the pick_task.py smoke test uses a temp tree or a mock.

Claude to choose the simplest one that holds the one-writer rule.

## Receipt

scripts/sched/go.py:64 dry run when env CLAUDECODE is set or --dry given (a Claude Code session never starts a second writer); operator terminal has no CLAUDECODE so mts go launches live (go.py:70-76); mts.ps1:274-278 go verb delegates to go.py, adds -Dry switch (:13). Tests: MyTradingSys/tests/test_go.py test_1_inside_claude_code_is_dry_no_launch, test_2_operator_terminal_launches_live, test_3_dry_flag_forces_no_launch, test_7_mts_go_verb_delegates_to_go_py.

# END
