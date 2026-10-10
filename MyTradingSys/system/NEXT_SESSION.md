<!-- relay: go depth=2 id=ad8843b5 -->
# NEXT SESSION PROMPT (handoff 2026-10-10 ~01:30Z, relay session after B159; Claude Code Win App, either account)

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
   a. B160 engine snapshot at shot time (prompt in research/screenshot_context_2026-10-10/REPORT.md section 7, Sonnet).
   b. B141: write the runner for the 28 pre-registered cells (research/PRE_REG_HTF_REPLACE_2026-10-07.md), run on F:/MTS/data, holdout once.
   c. B149 capture (JIS-NB desk task, live host only): after 08:05 UTC, if a position stayed open across the 08:00 settlement
      (daily_loss_monitor log), run the capture command in the desk task from a worktree with the live data dirs, ship the json, mark done.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## State at handoff (2026-10-10 ~01:30Z, JIS-NB, relay session, depth 1 -> next fires mts-relay-b)
- DONE this session: B159 CLOSED (commit 6b86944): `shot.py read` now stores every claim row `{id, class, claim, evidence}` on the manifest `read` event (folded into shot state as `claim_rows`); counts and `status_line` unchanged; a malformed row (3 cells, empty claim or evidence, class spelled `Match` / `NOT IN DATA`) is refused with its line number and nothing is appended. The real 78f967b4e253 extract yields 9 rows. test_shot 23 pass. Follow-up not done (by design): falsifier/invalidation lines to capture.py as `chart_read` with `level`.
- Quick gate: all steps pass except `tests/docs/test_integrity.py::test_2_no_forbidden_refs`, which flagged the old tool-quirk line of this file (it quoted a forbidden git phrase). Reworded below; the next gate run should be green. If it is still red, fix before new work.
- Hygiene: STATUS.md "Daily Hygiene" has no run on this host yet (task `MTS-DailyHygiene` not registered here); last known GREEN 2026-10-09T22:51Z.
- Desk: DSA queue holds D11, D19, D20, D21, D22 (pending) + daily gate (taken); JIS-NB holds live-mirror install and B149 capture (pending). B147/B135 regen and the Java run desk tasks are done.
- Operator-owned, do not attempt: CI workflow patch `system/ci_concurrency_fix.patch` (needs a workflow-scope token); live-mirror install on JIS-NB (admin shell). `sync.py start` prints "live mirror: REFUSED: no CURRENT pointer" until that install is done: expected.
- Still open: B149 capture (needs 08:00Z settlement with an open position; if none was open, mark waiting and move on).
- Positions open on testnet at last check: L-mkt-1009-2100, S-mkt-1009-1901 (position_manager untouched; do not touch).
- `sync.py where` flags mts-research (13 unshipped commits) and mts-extract (3 untracked): other sessions' worktrees, not this relay's.
- Relay (RELAY.md): chain running, the relay tasks are Claude App scheduled tasks (not Windows tasks: schtasks shows nothing, by design). Stop it with `python scripts/sched/relay.py stop "<why>"`.
- Java: JIS-NB has JDK 17 at C:\tools\jdk-17.0.18 and Maven, `mvn -q -o test` works in a worktree; NUC has JDK 11 (javac --release 11 harness).
- Tool quirks: Bash heredocs with backslash-n are mangled (a heredoc patch script with a relative path also failed): write patch scripts with the Write tool or use Edit. A chained `cd x && git <merge or switch>` is denied: use `git -C <dir> <cmd>` as its own call.
- Not shipped, owned by JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Do not edit.
- No stash in shared clones; do not pass --help to sync.py subcommands.
