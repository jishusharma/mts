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
   e. Tom DSR/PBO (B147 part 4) once the JIS-NB regeneration task (B147_ROW_DROP_EXACT) is done.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## State at handoff
- 2026-10-10 block DONE. Trunk unblocked (9b27da3): test_mainnet_flag_offline failed only when MTS_ACCOUNT is set in the host env; test now hermetic. Quick gate green with and without MTS_ACCOUNT.
- Closed with tests: B145 (filter_range_noise NOT neutral, flag stays off), B146, B150 (gate discovery + extra-tests step 3xt + mainnet refuses testnet calibration), B151 (fib bear zone never fired; rerun: all CC setups FAIL),
  B152, B153 (Py+Java net_rr parity), B155 (prompt contract gate 3pc), B156 (thesis age), T093 (turn-of-candle 4-12 h imbalance on klines 2022-2026: NO REPLICATION; the old handoff called it T085, T085 is the time-exit task).
- IN-FIX: B147 (row drop attributed: 17/19 old SETUP_FORMING used the removed 0.2% fallback stop), B148 (close on first live beat_utc), B136 (buildOiBreakdown UNAVAILABLE, needs JVM restart). BLOCKED: B140 hardware, B142-B144 (D15-D17), B149 (needs a captured 08:00 settlement log).
- JIS-NB desk tasks pending: register CI/CD jobs (`register_cicd_tasks.ps1 -Trigger`), B149 capture, B147/B135 snapshot regeneration, Java mvn tests + restart window. Live mirror install (20261009-202832) still pending.
- CI/CD: auto_deploy.py + daily_hygiene.py + register script shipped; both tasks registered and triggered once on JIS-NUC (auto_deploy = NOT_LIVE there, correct; hygiene ran the gate and reported). green/fast-track advance is the only proof CI is green on both OSes (no gh CLI, repo is private): `git ls-remote origin refs/heads/green/fast-track` vs `origin/fast-track`.
- Java without JDK 17 (this NUC has only JDK 11): compile main + test with `javac --release 11` against the ~/.m2 jars and call the test methods from a small main (worked for MarketDataSnapshotTest 21/21).
- Tool quirk: Bash heredocs with backslash-n or many quotes can be mangled; write scripts with the Write tool. The main NUC clone is shared by several sessions: commit only your files.
- Not shipped, owned by JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Do not edit. Untracked check_handoff.py / skill_src are another session's.
- No git stash in shared clones; do not pass --help to sync.py subcommands.
