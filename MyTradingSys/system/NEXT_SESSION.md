<!-- relay: go depth=0 id=180825b1 -->
<!-- relay: go depth=0 id=seed2610a1 -->
# NEXT SESSION PROMPT (handoff 2026-10-10 ~13:30Z, dispatcher-run relay closed B149 code; before: ~13:00Z applied D23; was ~12:40Z relay B closed B149 capture + B164; text below is history) (was 06:50Z, relay session after B160; Claude Code Win App, either account)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), then State below. Worktree only, never the live tree.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   Read STATUS.md "Daily Hygiene": a RED there is fixed before new work. One task per session; hand off after the task,
   5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData query decisions + feedback. Apply answered decisions with no `applied`
   (D01-D23 all applied; D23 at 13:00Z 2026-10-10). New unanswered decisions: act on the `recommended` option only when older
   than 24 h; Java changes (D15 on B142, D17 on B144) are staged + tested, the restart goes to a JIS-NB desk task.
2. DSA / JIS-NB results: for every desk task now done, spot-check ONE number against its file, then use it (no redo).
3. TASK (queue seeded by operator 2026-10-10; pick the first item not done, claim it, ONE per session; mark it DONE in "Queue status" below when shipped):
   Q1. Read the overdue screenshots: `shot.py status`, take the OVERDUE classified charts oldest first (0e9036ae547d, 65656faa31ba, 29ff2b488f13, ...),
       up to 5 per session; for each `shot.py read` with MATCH / MISMATCH / NOT_IN_DATA claims against files you read, then `shot.py done`. Ship the outputs.
   Q2. B171 imbalance indicator end to end: read MyTradingSys/items/B171_imbalance_indicator_end_to_end.md, build the next unfinished step with a
       fail-first test. Design rule from the Grok sweeps: control for price; NO REPLICATION in public evidence, so label it a hypothesis, no tuning.
   Q3. Big-trade backtest follow-ups: research/bigtrade_2026-10-09/PLAN.md and FINDINGS.md, take the next open item (EXIT_POLICIES_REPORT.md lists the
       state). Files under backtest/bigtrade/* stay in the live tree uncommitted: ask JIS-NB desk to commit them, do not copy.
   Q4. Post a desk task to JIS-NB to run scripts/dev/refresh_klines.py for 2026-10-09 (unblocks old 3c: `shot.py engine <id>` on the 10-09 chart shots).
   Empty list: reread Control Room decisions/feedback, then `desk.py list --all`; only then write stop.
4. Route run-and-report work to DSA (system/DSA_DELEGATION.md); post what the DSA queue lacks before ending.
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## Queue status
(none done yet; seeded 2026-10-10 ~18:00Z by operator request, the old "queue empty" stop was wrong: the real backlog was not listed)

## Update 2026-10-10 ~14:35Z (relay run by cron mts-dispatcher, JIS-NB)
- No task done: 3a/3b closed or staged, 3c blocked (klines archive ends 2026-10-08, no 10-09 file). Remaining desk items are DSA/JIS-NB/operator-owned. Queue empty -> stop.
- Reminder: position_manager and runtime/regime_classifier.py were not seen back after the 13:14Z python kill; supervisor to check.

## Update 2026-10-10 ~14:45Z (relay run by cron mts-dispatcher, JIS-NB)
- DONE: B141 writer staged (.new force-added, *.new is gitignored), 15 staged tests OK / 4 fail on live code, quick gate GREEN, SUPERVISOR_LOG entry, B141 item progress. Not promoted.
- Next: 3c only if klines 10-09 exist; else pick from desk/Control Room (nothing else unclaimed in this file).

## Update 2026-10-10 ~14:10Z (relay run by cron mts-dispatcher, JIS-NB)
- DONE: B141 Stage 2 (research/b141_htf_stage2.py + 10 tests, mutation-checked, b141_stage2_result.json, PRE_REG section 9, item progress, wiring_registry REPRO, run_extra_tests). 0 of 16 cells pass; 4H ER cells opposite sign. Holdout not read (no candidate). Quick gate GREEN.
- Next: 3b writer .new (section 7 consequence), or 3c if klines 10-09 exist.

## Update 2026-10-10 ~13:45Z (relay run by cron mts-dispatcher, JIS-NB)
- DONE: B141 Stage 1 coverage (research/b141_htf_stage1.py + 7 tests + b141_stage1_result.json). Incumbent 3.3%/3.0% coverage; 16 of 28 cells kept. 3c still blocked: klines archive ends 10-08 (no BTCUSDT-1m-2026-10-09.csv).
- Next: Stage 2 of B141.

## Update 2026-10-10 ~13:30Z (relay run by cron mts-dispatcher, JIS-NB)
- DONE: B149 code: ALLOWED_TX_TYPES = {trade, settlement}, settlement adds `change` only; 2 new tests fail on old code; BUGS/INDEX/item CLOSED.
- INCIDENT (mine): a stray `python -` in a Bash call hung on a REPL; I ran `taskkill /F /IM python.exe`, which killed ALL host Python processes.
  Supervisor respawned auto_trader, live_runner_cli, orderflow_live, daily_loss_monitor at ~13:14Z (restarted, positions unaffected by the kill itself).
  NOT seen back at 13:15Z: position_manager and runtime/regime_classifier.py. Supervisor/operator: check and restart them (builders may not). Never kill python by image name.
- Next: 3b (B141) or 3c.

## Update 2026-10-10 ~13:00Z (relay run by cron mts-dispatcher, JIS-NB, commit ee3d37e)
- DONE: D23 applied: VISION_GAP_2026-10-10.md (c) addendum appended to PROJECT_VISION.md as drafted (DIRECTION UPDATE section),
  changelog row in research/fast_track_2026-09-27/PROJECT_VISION_CHANGELOG.md, Control Room D23 marked applied. Inbox: 0 new.
- Hygiene: still no run on this host (STATUS "Daily Hygiene" empty, not RED). Next: task 3a (B149 code).

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

## Update 2026-10-10 (JIS-NUC session)
- D11 done in part on the NUC: Malkan W1HrDl70Lhk + A-CQiV_UFB4 captions are in raw_transcripts_canonical (hi original + en machine translation, no extracts yet). N7r3v7plqZM private, dXxQOnK2jhQ members-only. Five ids hit YouTube HTTP 429 from the NUC IP: follow-up desk task d11b (DSA) retries after a cooldown. yt-dlp is now installed on the NUC (pip --user).
- Task 3b is therefore finished except d11b; D11/D12 already carry `applied` in Control Room.
- JIS-NB (session "Inbox items") reports: CI/CD jobs registered; NOT done: live-mirror install (no \JIS-NB\MTS-Mirror share, so `live_mirror.py pull` fails on the NUC), B149 capture, JVM restart. Those are JIS-NB-only.
- NUC-suited next: B141 28-cell runner (3d) on F:\MTS\data (daily/1h/1d only; 1m klines exist only on JIS-NB, so D22 Beta and anything on 1m/5m stays on JIS-NB).
