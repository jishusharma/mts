<!-- relay: go depth=0 id=0ae95ec9 -->
# NEXT SESSION PROMPT (handoff 2026-10-10, after the unblock-trunk / bug-closing / CI-CD block; Claude Code Win App, either account)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), then State below. Worktree only, never the live tree.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   Read STATUS.md "Daily Hygiene": a RED there is fixed before new work. One task per session; hand off after the task,
   5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData list decisions + feedback. Apply answered decisions with no `applied`.
   Unanswered defaults: D14 keep net_rr 1.25 to 2026-11-10; D15 disable ExtraSetupBuilder candidates; D16 CC alert-only;
   D17 exhaustion screener-only; D18 hardware (nothing a session can do); D13 no change. Act on a default only when the
   decision is older than 24 h; D15/D17 are Java: stage, test with the javac-11 harness below, hand the restart to the JIS-NB desk task.
2. DSA / JIS-NB results: for every desk task now done, spot-check ONE number against its file, then use it (no redo).
3. TASK (pick first unclaimed, claim it):
   a. B157 carried context in screenshot reads (Sonnet): prompt in research/screenshot_context_2026-10-10/REPORT.md section 7.
   b. D11 answered "Yes, download" (2026-10-09 19:43Z): ~9 Malkan public captions with yt-dlp (no video), plus Hindi ones per the
      note; mark D11 applied. D12 answered "Yes, once a day": record it in system/DSA_DELEGATION.md, mark D12 applied.
   c. B159, B160 (prompts in the T092 REPORT section 7), then B158 after D13.
   d. B141: write the runner for the 28 pre-registered cells (research/PRE_REG_HTF_REPLACE_2026-10-07.md), run on F:/MTS/data, holdout once.
   e. B149 capture (JIS-NB desk task, live host only): after 08:05 UTC, if a position stayed open across the 08:00 settlement
      (daily_loss_monitor log), run the capture command in the desk task from a worktree with the live data dirs, ship the json, mark done.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## State at handoff (2026-10-10 ~06:30 IST, JIS-NB, after the Java restart + B147/B135 regeneration)
- DONE this block: live tree is at trunk (auto_deploy keeps it there); Java compiled in the live tree and the state-machine JVM restarted 23:25Z by loop-supervisor (2.5 min feed gap, snapshot + state_code fresh, oi_breakdown real). B136 CLOSED.
  B147 + B135 CLOSED with numbers: research/B147_ROW_DROP_EXACT_2026-10-10.md (HEAD Java regen: kept 90,295; 93.6 pct of lost snapshots were fallback-stop; proof>=5 rows 0; SETUP_FORMING 0). Tom live rule = insufficient N; DSR/PBO moot at N=0.
  Desk tasks done: Java tests + restart, B147/B135 regeneration, CI/CD job registration.
- Still open: B149 capture (needs 08:00Z settlement with an open position), live-mirror install (needs an admin shell on JIS-NB: operator), CI workflow patch system/ci_concurrency_fix.patch (needs a workflow-scope token: operator), DSA queue D11, D19-D22.
- Positions open on testnet: L-mkt-1009-2100, S-mkt-1009-1901 (position_manager untouched; do not touch).
- Relay (RELAY.md): chain started by the JIS-NB session at this handoff; stop it with `python scripts/sched/relay.py stop "<why>"`.
- Java without JDK 17 (NUC has JDK 11): javac --release 11 harness (see git history of this file); JIS-NB has JDK 17 at C:	ools\jdk-17.0.18 and Maven, `mvn -q -o test` works in a worktree.
- Tool quirk: Bash heredocs with backslash-n or many quotes can be mangled; write scripts with the Write tool. The sleep-chain is blocked: wait with an until-loop in a background shell.
- Not shipped, owned by JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Do not edit. Untracked check_handoff.py / skill_src are another session's.
- No git stash in shared clones; do not pass --help to sync.py subcommands. Worktree for this block: ../mts-task (jis-nb/task-2026-10-10).
