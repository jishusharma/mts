<!-- relay: go depth=1 id=b9f05a2c -->
# NEXT SESSION PROMPT (handoff 2026-10-10 ~00:50Z, relay-a after B157; Claude Code Win App, either account)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), then State below. Worktree only, never the live tree.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   Read STATUS.md "Daily Hygiene": a RED there is fixed before new work. One task per session; hand off after the task,
   5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData query decisions + feedback. Apply answered decisions with no `applied`
   (D01-D22 were all applied at 00:30Z 2026-10-10). New unanswered decisions: act on the `recommended` option only when older
   than 24 h; Java changes (D15 on B142, D17 on B144) are staged + tested, the restart goes to a JIS-NB desk task.
2. DSA / JIS-NB results: for every desk task now done, spot-check ONE number against its file, then use it (no redo).
3. TASK (pick first unclaimed, claim it):
   a. B159 claim rows into manifest (Sonnet): prompt in research/screenshot_context_2026-10-10/REPORT.md section 7.
   b. B160 (prompt in the same REPORT section 7).
   c. B141: write the runner for the 28 pre-registered cells (research/PRE_REG_HTF_REPLACE_2026-10-07.md), run on F:/MTS/data, holdout once.
   d. B149 capture (JIS-NB desk task, live host only): after 08:05 UTC, if a position stayed open across the 08:00 settlement
      (daily_loss_monitor log), run the capture command in the desk task from a worktree with the live data dirs, ship the json, mark done.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## State at handoff (2026-10-10 ~00:50Z, JIS-NB, relay-a session)
- DONE this session: B157 CLOSED (commit a081314): `shot.py read` refuses a chart extract without `Prior:` (path or `none`) or with a missing Prior path, prints the prior read's Invalidation/Falsify lines to score HELD/BROKEN/UNTESTED; TEMPLATE.md has "Carried context"; screenshot_intake.md stage 4 updated. Quick gate PASS.
- Old task 3b (D11/D12) is done: D11 is a DSA desk task (pending), D12 recorded in DSA_DELEGATION.md; both marked applied.
- Hygiene GREEN (2026-10-09T22:51Z). Desk: DSA queue holds D11, D19, D20, D21, D22 (pending) + daily gate (taken); JIS-NB holds live-mirror install and B149 capture (pending).
- Still open: B149 capture (needs 08:00Z settlement with an open position), live-mirror install (needs an admin shell on JIS-NB: operator), CI workflow patch system/ci_concurrency_fix.patch (needs a workflow-scope token: operator).
- Positions open on testnet at the previous handoff: L-mkt-1009-2100, S-mkt-1009-1901 (position_manager untouched; do not touch).
- `sync.py where` flags mts-extract (3 untracked) and mts-research (13 unshipped commits): other sessions' worktrees, not this relay's.
- Relay (RELAY.md): chain running; stop it with `python scripts/sched/relay.py stop "<why>"`.
- Java: JIS-NB has JDK 17 at C:\tools\jdk-17.0.18 and Maven, `mvn -q -o test` works in a worktree; NUC has JDK 11 (javac --release 11 harness).
- Tool quirk: Bash heredocs with backslash-n are mangled; write patch scripts with the Write tool. Chained `cd x && git checkout` is denied: use `git -C`.
- Not shipped, owned by JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Do not edit.
- No git stash in shared clones; do not pass --help to sync.py subcommands.
