# PROMPT CONFORMANCE CHECKLIST
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Applies to DSA sessions only. Rule: before DSA hands any Claude prompt
# to the operator, print the table below with evidence per row. Do not
# deliver the prompt until every row is PASS. Evidence = the exact
# command run and its output, not a claim.

## PROMPT TYPES

CC - Claude Cloud Repo. Win Claude App, Cloud Mode.
  Sees: pushed git refs only. No disk. No LAN. No F:\\\\.
  Branch: harness-assigned claude/<name>. Record as branch_alias.
  Commits: to its own branch. Operator cherry-picks.
  Read-only means: no writes to main, no Maven, no gitignored paths.
    It does NOT mean no file output. Every analysis session names its
    deliverable path and commits it to the branch.

CL - Claude Code Mode. Win Claude App, Code Mode.
  Sees: local disk.
  Branch: fast-track per CLAUDE.md; never master.
  Can run Maven locally (D:\\tools\\apache-maven-3.9.14).
  Writes: <file>.new for staged work; commit after promotion.

Both conform to CLAUDE_MANAGER_SPEC routing and SURFACE_POLICY s2-s4.

## BEFORE DELIVERING ANY PROMPT

| # | Check | Evidence |
|---|---|---|
| 1 | Every file path in the prompt exists on disk | Test-Path per path |
| 2 | Every script path exists | Test-Path |
| 3 | Save-work clause: never refuse work for budget; at 95 percent or above, commit-then-continue | quote |
| 4 | Model matches CLAUDE_MANAGER_SPEC routing table | quote |
| 5 | CLAUDE.md gates carried: run_all_tests --quick; new tests fail first; no in-place executor/live_runner edits; .new staging; no mainnet; no keys | quote |
| 6 | Ownership-claim line for any execution/ or layers/alerts/ .new staging | quote |
| 7 | Session record uses the 14-field template (sessions/README.md) | quote |
| 8 | Verify block names TASK / DONE / VERIFIED / MISSED | quote |
| 9 | 03_FILE_INDEX row requirement stated for every new file | quote |
| 10 | LF-only, no BOM; no Dumps/ path (Dumps/ is gitignored; CC cannot read it) | quote |

## CC-ONLY

- Deliverable path named. A no-writes prompt wastes the cloud budget.
  Cost 2026-10-01:  lost to a no-writes chart read.
- Checkpoint commits, not one at the end. Protects against container
  reclaim. Cost 2026-10-01: 1800Z chart-read lost 75 lines.
- No Maven, no LAN, no F:\\\\, no .secrets/, no .env.
- Branch created by harness, recorded as branch_alias. Do not create
  cloud/work.

## CL-ONLY

- Branch fast-track. Never master. Never push, merge, rebase, reset.
- Live-path files (auto_trader, position_manager, daily_loss_monitor,
  live_runner_cli) are never edited in place. Stage .new. Supervisor
  restarts.
- HALT files and open trades off limits to builders.

## PROMPT SHAPE

- Line 1: session ID with -CLD- for CC or -CLI- for CL.
- Line 2: usage percent, or '85 assumed' if unreadable.
- Budget gate first (SURFACE_POLICY s3).
- Boot section: files, by line range.
- One task per prompt. One wave of children. Cap 3.
- Hard rules carried verbatim from CLAUDE.md.
- Every claim in the prompt carries file:line or a proof path.
- End with the four-line verify block template.

# END
