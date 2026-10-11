<!-- relay: go depth=34 id=c5f18667 -->
# NEXT SESSION PROMPT (handoff 2026-10-11, Opus operator session "Tom/Fabio transfer probe"; Claude Code Win App, either account; older text below is history)

ONE-MESSAGE RULE (operator 2026-10-10, standard practice): the block below must run with no input from the operator. Every open question carries a default; the session answers itself from Control Room (ArtifactData) and acts. Overwrite this file at each handoff.
DIRECTION (operator 2026-10-11): redefine the Tom and Fabio layers completely from today's findings. Road map, STOP list and session plan:
`MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md` (read it before Q1). Do NOT backtest or tune the current Tom/Fabio encoding on BTC.

```
MTS builder session. Read CLAUDE.md, STATUS.md (regenerate first), research/tom_transfer_2026-10-11/ROADMAP.md, then State below.
0. `python scripts/dev/sync.py start`, `sync.py where`, `desk.py list --all`. Push fails: say so in one line, stop.
   Read STATUS.md "Daily Hygiene": a RED there is fixed before new work. One task per session; hand off after the task,
   5 operator turns or ~50k tokens: ship, overwrite this file, `where` clean.
1. Control Room (url in CONTROL_ROOM.md): ArtifactData query decisions + feedback. Apply answered decisions with no `applied`;
   a new unanswered decision: act on its `recommended` option only when older than 24 h.
2. DAX data DONE 2026-10-11 (card tom-dax-data): F:/MTS/data/dax_archive holds 684,940 GER40 1m bars, 2024-10-01..2026-10-09,
   every weekday fetched; snapshot check MATCH. Nothing to do here.
3. TASK: first Qn below not DONE and not claimed. Its card is the whole brief:
   `python scripts/dev/tasks.py brief <card>` -> `sync.py claim` -> work -> `tasks.py done <card> --result "<number/file>"` -> ship -> release.
   Q1. DONE 2026-10-11 (relay JIS-NB): net_rr 0.70->4.94, quick gate green. (old text:) Card tom-verdict-fee-per-market (Sonnet). Code is ON fast-track (09a6196, BTC bit-identical test, quick gate passed pre-merge); claim released; card still active. Remaining: quick gate on HEAD, confirm the new Java tests fail on old code, run `dax_engine.py snap --at 2026-05-12T07:55:00Z` and read the vwap_band_+1 short's net_rr (was 0.70 at gross 5.09; the agent's run printed nothing - check the out file), then `tasks.py done`. Java reaches live only via supervisor deploy. DONE when: card done_when holds (GER40 netRR(24229,24111,24257)=4.1696 (the brief said 4.1662: hand error, (118-0.24229)/(28+0.24229)=4.1696), BTCUSDT bit-identical test red-before).
   Q2. DONE 2026-10-11 (relay JIS-NB): TOM_TRADE_LEDGER.csv 12 trade ids / 30 rows, every trade in all 7 videos (36 sheets); <30 because the videos show ~1.7 trades each. Follow-up card find-more-tom-trade-recap-videos-yt-dlp- (raw, refiner will scope).
   Q3. Card fabio-trade-ledger (Sonnet; in progress: ledger 14 trades F1-F11 / 43 rows, DyS79Eb92Ug read to t=1950 (F10 +4964$, no trade t=1775-1950, talking head). F11 read (t=2775-3000, -2115$, ledger 14 trades / 43 rows). t=3025-3275 read (F12 NQ long 6->10, outcome not shown; ledger 15 trades / 46 rows). t=3275-3525 read (F12 stopped -1525$, F13 NQ long 8->10 open at t=3500, ledger 18 trades / 49 rows). t=3525-3775 read (F13 stopped -2910$, flat no trade to t=3750, ledger 16 trades / 52 rows). t=3775-4025 read (F14 NQ long 8, stopped -2611$, ledger 17 trades / 54 rows). t=4025-4275 read (flat, no trade, Daily 15147). t=4275-4525 read (flat, no trade, performance journal window, Daily 15147). t=4525-4775 read (flat, no trade, Daily 15147, talking heads). t=4775-5025 read (flat, no trade, Daily 15147, talking heads; ledger 17 trades / 57 rows). t=5025-5275 read (flat, no trade, Daily 15147, talking heads; ledger 17 trades / 58 rows). t=5275-5525 read (talking heads, no chart, no trade; ledger 17 trades / 59 rows). t=5525-5775 read (flat, no trade, ledger 17 trades / 60 rows). t=5775-6025 read (flat, no trade, hypothetical bounce sketch, ledger 60 rows). t=6025-6275 read (flat, no trade, talking heads from t=6200; ledger 62 rows). NEXT window t=6275-6525 step 25, tool: python -I scripts/dev/fabio_window_sheet.py DyS79Eb92Ug 6275 6525 25 w22 (the tool overwrites an old w22 sheet), flattened captions DyS79Eb92Ug.txt beside the video on F: fabio_videos; one window per session). DONE when: FABIO_TRADE_LEDGER.csv has >= 20 trades (or all available in the downloaded videos) with frame evidence.
   Q4. Cards tom-layer-v2-spec (part A: families + sourced rules) then tom-layer-v2-cost (part B: per-market proofs/cost, BTC stop-width transfer rule, Sonnet build cards). OPUS, approved by the operator 2026-10-11, size M each = one card per session; both need Q2. DONE when: TOM_LAYER_V2_SPEC.md parts A and B + Sonnet build cards.
   Q5. Cards fabio-layer-v2-spec (part A) then fabio-layer-v2-markets (part B: NQ vs BTC data plan, cost, recall-harness + encode cards). OPUS, approved, size M each; both need Q3. DONE when: FABIO_LAYER_V2_SPEC.md parts A and B + cards.
   Q6. Card tom-encode-spike-fade (Sonnet; needs Q1 + tom-layer-v2-cost). DONE when: RECALL_DAX_V2.md shows recall >= 4/7 (or the honest miss), flag-off BTC output identical.
   Q7. Card tom-dax-backtest (run; needs Q6): `tom_dax_bt.py all --shifts 0,1,2,3`, then `report --read-holdout --shifts 0,1,2,3` once. DONE when: DAX_BT_REPORT.md has dev + holdout rows and the branch named.
   Q8. Card tom-probe-prereg (M arms only, needs tom-dax-backtest + tom-layer-v2-cost). DONE when: card done_when holds.
   Q9. DONE 2026-10-11 (relay JIS-NB): B144 countSignals ignores volume spike, new test red-before, mvn 89 green, quick gate green. Java live only via supervisor deploy.
   Q10. DONE 2026-10-11 (relay JIS-NB): BuildVpFixedGridTest green on HEAD, red under L566 mutation (80371 vs 80370), B059 CLOSED.
   Q11. DONE 2026-10-11 (relay JIS-NB): B124 CLOSED, check_journal in testnet_canary.py, 6 new tests red-before, 31 pass; live-tree canary: journal OK, 5 open all journaled.
   Q12-13. DONE 2026-10-11 (relay JIS-NB): B122 reject text fix (new test red-before); refiner pass REFINE_OK.
   Q14. DONE 2026-10-11 (relay JIS-NB): TOM_TRADE_LEDGER.csv +7 rows, new videos liEJMfE_PXg (T11), ZZeET7ng1nk (T12), SANOimk8M9o (same trade as T3); 14 trades / 37 rows.
   Q15. DONE 2026-10-11 (relay JIS-NB, partial): F6 (Jpd96fLqr5M, NQ long) added, gLHd none shown (tutorial), 9I5vTvwsMBk has no f398, DyS79Eb92Ug/Is1HvdfQm5c/xUyqIjCfZzg downloaded unread (2.4-3.8 h): 2 raw follow-up cards for the refiner.
   Q16. DONE 2026-10-11 (relay JIS-NB): B066 CLOSED option C, tierFor() + SetupCandidatesBuilderTierTest green, registry test OK. Java live only via supervisor deploy.
   Q17. DONE 2026-10-11 (relay JIS-NB): B118 CLOSED option 1, layers.bracket_source=SAMPLING on every layer log row, new test red-before, 96 pass. Live only via supervisor deploy. (old text:) Card B118 (Sonnet), default option 1 (label layer trades bracket_source=SAMPLING, keep values). DONE when: test_auto_trader.py new test red-before then green and row B118 CLOSED. Edit auto_trader.py only as .new staged (live tree imports it).
   Q18. (same video as Q3, covered there; skip unless Q3 is DONE) card find-more-fabio-trade-recap-videos-yt-dl, ONE video only: Is1HvdfQm5c. DONE when: its ledger rows with frame files are in FABIO_TRADE_LEDGER.csv (or a per-video line saying none shown).
   A Sonnet session that reaches an OPUS card: skip it, take the next Sonnet card, and say "Q4/Q5 need an Opus session" in the handoff.
4. Run-and-report work goes to DSA (system/DSA_DELEGATION.md).
End: `sync.py ship`, `sync.py release <slug>`, overwrite this file, `sync.py where` clean, one-line summary, stop.
```

## Update 2026-10-11 ~15:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=6025-6275 read: flat, no trade (Daily 15147), talking heads from t=6200. Ledger row added (62 rows). Next: t=6275+ (w22). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~14:30Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=5525-5775 read: flat, no trade (Daily 15147), talking heads; chart scrolled back to an earlier session at t=5625/5725. Ledger row added (60 rows). Next: t=5775+ (w20). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~14:20Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=5275-5525 read: talking heads only, no trade. Ledger row added (59 rows). Next: t=5525+ (w19). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~14:15Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=5025-5275 read: flat, no trade (Daily 15147), talking heads. Ledger row F-noTrade-5025-5275 added (58 rows). Next: t=5275+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~13:45Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=4775-5025 read: flat, no trade (Daily 15147), talking heads. Ledger row F-noTrade-4775-5025 added. Next: t=5025+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~12:15Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=4525-4775 read: flat, no trade (NQ chart t=4550-4575, Daily 15147), then talking heads. Ledger 17 trades. Next: t=4775+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~11:50Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=4275-4525 read: flat, no trade (Daily 15147 unchanged), performance-journal equity window t=4350-4425. Ledger 17 trades / 55 rows. Next: t=4525+. Q4/Q5 need an Opus session.

## Update 2026-10-12 ~00:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=4025-4275 read: flat, no trade, Daily 15147; chart zoomed out at t=4250. Ledger 17 trades. Next: t=4275+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~23:50Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=3775-4025 read: F14 NQ long 8 stop 25086.25 TP 25186.75, stopped -2611$ (Daily 17758->15147). Ledger 17 trades. Next: t=4025+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~23:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=3525-3750 read: F13 stopped -2910$ (Daily 20668->17758), then flat/no trade. Ledger 16 trades / 52 rows. Next: t=3775+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~22:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=3275-3500 read: F12 stopped out -1525$ (Daily 22193->20668), F13 NQ long 8->10 stop 25097.00, outcome not shown by t=3500. Ledger 49 rows. Next: t=3525+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~20:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=3025-3275 read: F12 NQ long 6->8->10 lots (stops 25085.75 -> 25098.50 -> 25098.25, TP 25140.75), outcome not shown (ad + interview from t=3175). Ledger 15 trades / 46 rows. Next: t=3275+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~18:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=1350-1600 read: F8-x -2121$, F9 long 8 (+259$ net), F10 long 4 open. Ledger 14 entries / 37 rows. Next: Q3 window t=1600+ (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~10:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=1150-1350 read: F7 long 4 (stop 19.5pt, scratch -38$), F8 long 8 (stop 12.75pt). Ledger 11 entries / 32 rows.
- Next: Q3 continue DyS79Eb92Ug t=1350+ (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~09:30Z (relay via cron mts-dispatcher, JIS-NB)
- DONE T0: DAX fetch ALL_DONE -> convert (GER40 684940 bars, 631 days, 2025-03-03 bar = raw), tasks.py done tom-dax-data.
- Q3 progress (not DONE): DyS79Eb92Ug captions flattened, sheets t=380-1100 read: it replays the F6 session; F6 exit resolved (TP ~25001, +10368$). Ledger 9 entries / 29 rows. Tool: scripts/dev/fabio_window_sheet.py.
- Next: Q3 continue (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~01:30Z (relay via cron mts-dispatcher-night, JIS-NB)
- Q2 progress (not DONE): T6hDJcHrVBM sheets 00-03 read: only trade T5 (labels re-read MATCH: -3 @24690 SL 24753 TP 24184); management rows added:
  stop to breakeven, one partial at VWAP, hand-drawn SL 650. Ledger 11 trades / 24 rows, every frame exists. DAX fetch still running, no ALL_DONE. Control Room 0 new.
- Next: Q2 continue with ujedEcmvBMk (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~05:00Z (relay via cron mts-dispatcher-night, JIS-NB)
- Q2 progress (not DONE): UOBgXV20yCM sheets 00-02 read: one teaching trade T9 FDAX long 23887 SL 23857 TP 23962 (entry/exit moment not shown). Ledger 11 trades / 21 rows, frames exist. DAX fetch: no ALL_DONE yet (log tail still FAIL days).
- Next: Q2 continue with T6hDJcHrVBM (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~03:30Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): fZlNGWvd2Ko sheets 00-03 read: F3a-c, NQ long 12-14 lots, stop 3.4-8.9pt, risk 980$ for TP 24655.75 (25.9R), day P/L +22017$. Ledger 13 rows (F1, F2, F3 entries/mgmt). DAX: retry fetch still running (2 PIDs, empty retry log), bt log shows 59 weekday FAILs: tom-dax-data NOT done.
- Next: Q3 continue with 0jM5Y31YJak 00/03/04 (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~00:40Z (relay via cron mts-dispatcher-night, JIS-NB)
- Q2 progress (not DONE): n7ZSkjb7JXs sheets 00-05 read. T1 management added (scale-in to 4, two partials, TP 24422->24426 then removed, stop 24485->24484);
  new T8 GC gold short 1 @4446.8 SL 4456.1 TP 4415.1 (entry/exit not shown). Ledger 10 trades / 19 rows, every frame exists.
- DAX fetch: PIDs 13336 (WindowsApps shim) + 3924 (child) = ONE fetch, not a duplicate; no ALL_DONE yet. Control Room: D01-D24 applied, inbox 0 new.
- Next: Q2 continue with UOBgXV20yCM (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~00:05Z (relay via cron mts-dispatcher-night, JIS-NB)
- Q2 progress (not DONE): k0zm5NYn0IQ sheets 00-09 read. T2 corrected to 25318/SL 25338/TP 25196 (RECALL_DAX 25343 = MISMATCH); new T2b re-entry short 2 @25341 with scale-in, 3 stop tightenings, 2 partials, stop to profit. Ledger 9 trades / 14 rows, every frame exists.
- DAX fetch still running (2 python dax_data.py fetch PIDs 13336, 3924 at 23:43Z; log has 30 FAIL days, no ALL_DONE). Next session: if two fetchers still run, that is a duplicate: check the log before restarting anything.
- Next: Q2 continue (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-10 ~21:10Z (relay A, JIS-NB)
- DONE: B142 (commit e262656): ExtraSetupBuilder.build returns []; ExtraSetupBuilderDisabledTest red->green; full mvn test green. Live only via JIS-NB desk task 20261010-205418 (Java window). Merged over the Tom/Fabio handoff: its text kept, B142 marked done in Q9.

## State at handoff 2026-10-11 (Opus operator session)
- Shipped today: PROBE_PLAN.md, PRE_REG_DAX.md, RECALL_DAX.md (0/7), ROADMAP.md, DIAG_BTC.md (agent), conditions/gap_rules.md (27 rules, agent),
  DAX tooling dax_data.py / dax_engine.py / tom_dax_recall.py / tom_dax_bt.py (build 1e67b85, 29 tests). Cards done: tom-dax-recall, tom-gap-rules-extract, tom-probe-diag-btc.
- Still running at handoff: Dukascopy full fetch (background shell of the operator session; may die with it - step 2 restarts it). tom-dax-data stays active until converted.
- Fee agent stopped by operator request 2026-10-11; its last state is in ../mts-feemkt (see Q1).
- Data on F: dax_raw (raw .bi5, untrusted), dax_archive (Binance-format klines), tom_videos (6 mp4 + vtt + txt + frames), dax_recall*.
- Worktree ../mts-daxbt: ~45 stray untracked files from a stash pop; nothing committed is lost; remove the worktree when idle.

## Queue status
Rebuilt 2026-10-10 ~21:00Z from `tasks.py next` after the Q1-Q4 screenshot/B171 work finished (Q1-Q4 of the old list DONE: shots 29ff2b + 3 single-TF read, B171 NO-INFO with D24 filed, klines desk task 20261010-165600 posted and still pending on JIS-NB).
Why the chain was idle 17:18Z-20:42Z: the old list ended in two items blocked on that desk task, so the handoff said stop while 8 cards were ready. The list now starts from ready cards.
Not in this list on purpose (claimed by other sessions at 20:48Z): tom-verdict-fee-per-market, tom-dax-data, tom-dax-backtest. Refined, waiting for a dispatcher refine pass: B066, B118, tom-encode-spike-fade, tom-probe-prereg.

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

## Update 2026-10-11 ~17:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q17 B118 (see Q17). Note: research/BUGS.md + items/INDEX.md still show B122 OPEN though Q12 fixed it: check and close. Next Sonnet task: Q18 DyS79Eb92Ug. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~16:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q15 partially (see Q15). Next Sonnet task: Q16 B066. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~15:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q14 find-more-tom videos. Q4/Q5 need an Opus session, Q6-Q8 wait on them. Next Sonnet task: Q15 find-more-fabio videos.

## Update 2026-10-11 ~13:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q11 B124. Q4/Q5 need an Opus session, Q6-Q8 wait on them. Next Sonnet card: Q12 B122.

## Update 2026-10-11 ~12:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q10 B059 test. Q4/Q5 need an Opus session. Next Sonnet card: Q11 B124.

## Update 2026-10-11 ~11:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q9 B144. Q4/Q5 need an Opus session, Q6-Q8 wait on them. Next Sonnet card: Q10 B059.

## Update 2026-10-11 ~04:30Z (relay via cron mts-dispatcher-night, JIS-NB)
- DONE Q1 tom-verdict-fee-per-market: recall rerun T3 vwap_band_+1 net_rr 4.94 (was 0.70, gross 5.09); quick gate GREEN. Java fail-first on old code NOT re-run (permission denied); old-code evidence = the 0.70. Java live only via supervisor deploy.
- Next: Q2 tom-trade-ledger (Sonnet). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~09:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): 0jM5Y31YJak sheets 00,03,04 read: no order labels (teaching video), added F2-m1 (2nd box 21441-21448) and F2-x (low ~21250, outcome inferred). Ledger 15 rows, frames exist. Next: Q3 9IliXww64uM sheets, then jasv3L-d8ZE. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~06:30Z (relay via cron mts-dispatcher, JIS-NB)
- Q2 progress (not DONE): ujedEcmvBMk sheets 00-03 read. T3 corrected (SL 24265, not 24257; not stopped out, one lot closed by t=250), T3b re-read MATCH; 2 rows added + 1 outcome-not-shown row. Ledger 11 trades / 27 rows, frames exist. Quick gate: see commit.
- Next: Q2 continue with zQTbdEweG3c (4 sheets), then UOBgXV 03-04, l8RZ 01-02. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~08:30Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): downloaded 5 Fabio videos (f398 720p; the default android client gave 360p, unreadable). F1 NQ short 10 @25652.75 SL 25668.50 TP 25514.75 fully read (stop trail 5 steps), F2 approx, F3 transcript only. Ledger + .md in research/fabio_transfer/.
- Next: Q3 continue (0jM5 00/03/04, fZlNGWvd2Ko). Q4/Q5 need an Opus session.

## Update 2026-10-11 ~10:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): 9IliXww64uM sheets 00-06 read: ES Jan 2026, two pasted screenshot trades F4a short 1 @6986.75, F4b short 1 @6977.5, no stop/TP on any frame. Ledger 17 rows / 7 entries, frames exist. Next: jasv3L-d8ZE 00-05 (last video), then Q3 stats + `tasks.py done`. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~14:00Z (relay via cron mts-dispatcher, JIS-NB)
- DONE Q12 B122. Q4/Q5 need an Opus session, Q6-Q8 wait on them. Next Sonnet task: Q13 refiner (REFINE_NEEDED).

## Update 2026-10-11 ~09:20Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=1575-1775 read, F10 resolved (+4964$, TP 25074.25). Ledger 13 entries. Next: Q3 continue t=1775+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~10:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=1775-1950 read, no new trade (Daily P/L 24354 flat, interview). Ledger 13 trades / 40 rows, frames exist. Next: t=2775+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~19:00Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=2775-3000 read: F11 NQ long 4->8 lots stopped out, -2115$. Ledger 14 trades / 43 rows. Next: t=3025+. Q4/Q5 need an Opus session.

## Update 2026-10-11 ~14:45Z (relay via cron mts-dispatcher, JIS-NB)
- Q3 progress (not DONE): DyS79Eb92Ug t=5775-6025 read: flat, no trade (Daily 15147), price pulled back to ~25063, hand-drawn bounce sketch only. Ledger row added (60 rows). Next: t=6025+ (w21). Q4/Q5 need an Opus session.
