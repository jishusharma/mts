<!-- relay: go depth=1 id=8a455ad2 -->
# NEXT SESSION PROMPT (handoff 2026-10-10 ~06:50Z, relay session after B160; Claude Code Win App, either account)

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
   0. Pre-check (2 min, not a task): `grep '"kick"\|"idle"' ~/.claude/mts-relay-log.jsonl | tail -3`. An event after 09:40Z
      2026-10-10 from the dispatcher = B164 CLOSED (edit the row); none = list_task_runs mts-dispatcher, read its last run, fix.
      D23 (vision addendum) answered -> apply to PROJECT_VISION.md + CHANGELOG, mark applied; unanswered -> leave (operator's call).
   a. B141 (skip while the NUC claim on it is open: `sync.py start` lists claims): write the runner for the 28 pre-registered cells (research/PRE_REG_HTF_REPLACE_2026-10-07.md), run on F:/MTS/data, holdout once.
   b. B149 capture (JIS-NB desk task, live host only): after 08:05 UTC, if a position stayed open across the 08:00 settlement
      (daily_loss_monitor log), run the capture command in the desk task from a worktree with the live data dirs, ship the json, mark done.
   c. B160 follow-up: once <live>/Dumps/backtest/raw/klines has BTCUSDT-1m-2026-10-09.csv, run `shot.py engine <id>` for the 10-09
      chart shots (78f967b4e253, b5f554a9f68a, 6188a576411b, ...), ship research/screenshots/engine/*.json; re-score NOT_IN_DATA rows only in a new extract.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## Update 2026-10-10 ~09:30Z (relay session A, JIS-NB, commit 0cdb2cb)
- DONE: B164 follow-up: mts-dispatcher's 09:08Z tick failed silently: it ran the LIVE tree's relay.py (3f8a5ef, no `kick`). Its prompt
  (~/.claude/scheduled-tasks/mts-dispatcher/SKILL.md, host-local) now runs origin/fast-track's relay.py copied to %TEMP%; manual run logged IDLE.
  B166 CLOSED (paste 88.9 KB). B165 declutter already live (page built 09:21Z). D23 still unanswered (created today): not applied.
- B168 waits on the operator (reload AIBridge extension on JIS-NB + JIS-NUC). Live tree is behind origin (3f8a5ef + 1 unshipped commit, dirty):
  MTS-AutoDeploy cannot ff it; supervisor's call, builders do not touch it.

## State at handoff (2026-10-10 ~06:50Z, JIS-NB, relay session, depth 2 -> next fires mts-relay-a/b by parity)
- DONE this session: B160 CLOSED (commit cbec6d2): `shot.py engine <id> [--raw DIR] [--plan]` floors the chart's `at` to the minute, compiles src/main + harness SnapAt.java into %TEMP% (src/ and target/ untouched), runs on the 1m archive (default <main>/Dumps/backtest/raw) from an empty cwd, writes research/screenshots/engine/<id>.json. Refuses non-chart, no `at`, non-BTCUSDT, archive missing the shot's day, null snapshot. test_shot 26 pass (3 new, fail-first checked). Real run 65656faa31ba (10-07 09:24:59Z): current_price 83745.4 = 09:23 1m close (MATCH, no look-ahead); live-only fields (net delta, OI breakdown, book, funding rate) are listed as unavailable in data_quality.
- Archive coverage: <live>/Dumps/backtest/raw/klines ends 2026-10-08 (refresh_klines.py tops it up daily); F:/MTS/data/tom_raw ends 2026-09-26. Needs JDK 17: put C:/tools/jdk-17.0.18/bin first on PATH (D: java also works).
- Quick gate: GREEN at cbec6d2 (the test_integrity red of the last handoff is gone).
- Control Room: D01-D22 all applied; no new decisions at 06:45Z.
- Hygiene: STATUS.md "Daily Hygiene" still has no run on this host (MTS-DailyHygiene not registered here).
- Desk: DSA queue holds D11, D19, D20, D21, D22 (pending) + daily gate (taken); JIS-NB holds live-mirror install and B149 capture (pending).
- Operator-owned, do not attempt: CI workflow patch `system/ci_concurrency_fix.patch` (needs a workflow-scope token); live-mirror install on JIS-NB (admin shell). `sync.py start` prints "live mirror: REFUSED: no CURRENT pointer" until then: expected.
- Positions open on testnet at last check (01:30Z): L-mkt-1009-2100, S-mkt-1009-1901 (position_manager untouched; do not touch).
- Relay (RELAY.md): chain running as Claude App scheduled tasks. Stop it with `python scripts/sched/relay.py stop "<why>"`.
- Java: JIS-NB has JDK 17 at C:/tools\jdk-17.0.18 and Maven; NUC has JDK 11.
- Tool quirks: Bash heredocs with backslash-n are mangled: write patch scripts with the Write tool or use Edit. A chained `cd x && git <merge or switch>` is denied: use `git -C <dir> <cmd>` as its own call. ArtifactData out_dir into the scratchpad is refused: read without out_dir.
- Not shipped, owned by JIS-NB live tree: backtest/bigtrade/*, research/bigtrade_2026-10-09/*, pm_heartbeats files. Do not edit.
- No stash in shared clones; do not pass --help to sync.py subcommands.

## Update 2026-10-10 (inbox pass, JIS-NB, session switching fix)
- Why chains stopped (B164): relay.py gate used a 20-minute clock lock (killed the 06:42Z hand-over), the 04:23Z header said stop, depth cap had no reset, nothing started a chain. Fixed: lock keyed by handoff id, chain base, `relay.py kick`, App task `mts-dispatcher` every 30 min (starts mts-relay-a/b when the handoff says go; starts mts-control-room when the Inbox has a `new` item). RELAY.md has the rules.
- Inbox pass: 6 verbatim items recorded; B164-B170 filed (B165 declutter CLOSED, B169 MTS-Backup console hidden CLOSED, B170 CI emails = operator-only). Opus vision review: research/VISION_GAP_2026-10-10.md, draft NOT applied, decision D23 asks the operator.
- AIBridge: content.js stays armed after a block-less DSA answer, faster poll (B168). The extension must be reloaded on JIS-NB and JIS-NUC by the operator.
- NUC session is working D11 and B141: do not duplicate.
