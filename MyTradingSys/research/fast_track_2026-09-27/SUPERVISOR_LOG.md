# Supervisor log (Opus supervisor sessions)

One entry per supervisor session. Next supervisor: read this plus STATUS.md; nothing else from the chat is needed.

## 2026-09-28 - session 1

Landed: 0bbace1 L6 re-arm (T4 safety review: breach check still runs after re-arm, never blocks the
protective stop), 3f98dc8 CryptoCred cc_structure/cc_retest/cc_setups + 19 tests (2 Qwen bugs in
cc_setups caught by plan-derived tests), 01d0eed six Tom extracts (quote-verified), 63383f7 gate step 5b
(layer tests, also under --quick), 65815f9 lesson OUTPUT_TOKENS, 4f74c20 RSI/timeframe design +
operator directive verbatim in PROJECT_VISION, 3569ee3 1m history 2022-01..2025-08 fetched.

Operator decisions: bin NUC 019 (done: .rejected_019 + verdict). Download 1m history to 2022 (done).
RSI 40/60 is private to the MalkanView sub-layer; every other RSI use is standard (14, 70/50/30).
Wants: smoothed RSI MA + support on it per timeframe; tolerance ("slippage") around 40/60 found by
backtest for every edge case; alerts per timeframe incl. 1,2,3,10m and 2d,3d,5d; params tunable on
testnet from operator and trusted-professional input. NUC should do as much backtesting as possible.

Supervisor decisions: RSI_TF_LAYER_DESIGN.md D1-D7 (timeframe layer serves all layers, core later;
RSI split core/ma/events/malkan_40_60; params files with provenance; backtests on desktop now, NUC
"RUN" job type later if sweeps exceed ~30 min and Python is on the NUC).

Caught: test plans must come from definitions, not code - rsi TEST_PLAN C1 had been copied from
bt_rsi.py.new (off vs textbook Wilder: idx5 70.0 vs 77.777778). Fixed; 071 repacked. NUC tasks
070-075 moved to Dumps/workers/NUC-QUEUE/held/ until the formula audit (FORMULAS.md, re-derivation
of all plan numbers, Qwen 076 formula_audit.py) repacks them into incoming/.
Also caught: 031 packed with OUTPUT_TOKENS 3500 and 063/064 with 2500 (both would truncate); raised.

Open: formula audit agent; worker-model research (WORKER_MODEL_RESEARCH.md); NUC 031 was 66+ min
without a heartbeat at 09:10Z (longest earlier task 57 min) - check the NUC if still silent;
L6 part 2 (P/L from transaction log, 095ea22) not built; prob_table.py.new and bt_rsi.py.new
unreviewed (bt_rsi superseded by layers/rsi, do not promote); make_status "Open Findings" stale;
TF-B5 native-1d gate needs a real-data test; Malkan rules have no verbatim extract yet (only
research/malkan_rsi_2026-09-28/WEB_RESEARCH.md; NUC 040 reply PARTIAL) - multi-timeframe 5-star
composition (monthly+weekly gate daily) is a later task.
Next: Qwen self-validation technique -> pick from research, add to spec template and queue_tool.

Worker research (WORKER_MODEL_RESEARCH.md) -> decisions: keep qwen3-coder:30b; pilot one alternative
(glm-4.7-flash class MoE) on 2-3 already-verified specs before any switch; Devstral Small 2 24B (dense)
too slow for this CPU. Worker v3 batch (Sonnet session, T049): (1) EDIT output mode (search/replace
blocks) for changes to existing files - full rewrites only for new files; (2) execution-feedback retry:
verify runs the spec's tests, on failure auto-packs NNNr with the failure log, max 2 repairs; (3) sample-
and-vote (3 candidates) only for execution/risk specs; (4) package options num_thread 6 (physical cores;
research said 8, llama.cpp guidance is physical cores - measure both), keep_alive long. Operator sets
OLLAMA_FLASH_ATTENTION=1 and OLLAMA_KV_CACHE_TYPE=q8_0 on the NUC (server env; not reachable from here).

Operator 2026-09-28: FORMULAS.md must cover EVERY formula MTS uses (core, execution sizing/fees/P&L,
indicators, probability, backtest stats), not only the RSI/backtest layers. Inventory agent running;
money-affecting untested formulas get audited first. NUC heartbeat: nuc-worker.ps1 writes heartbeat only
at task start and calls Ollama with stream=false (timeout 7200 s), so silence during a long task is
normal, not a hang. Worker v3 adds: stream + heartbeat every 60 s with tokens so far. HDMI unplug on the
NUC does not affect CPU inference.

Formula audit (layers) done 248ab9d: FORMULAS.md s1-10, every plan number re-derived, only C1 was wrong.
RSI flat-series = 50 (TradingView gives 100) kept as a documented deviation. NUC 070-076 released.
Whole-MTS inventory: FORMULA_INVENTORY.md (priority list at bottom). Pending operator decision: core ATR
is SMA of TR, not Wilder - keep (Tom's numbers) or switch?

NEXT SESSION BRIEFS (Sonnet, one each):
A. "Execution formula tests": FORMULA_INVENTORY priority 1+2. Add FORMULAS.md sections for execution
   math; tests for plan_compiler/executor/risk_guard from definitions (fail on a mutated copy); Java net R:R
   shared constant + JUnit. Stage as .new; Opus supervisor T4-reviews before promotion.
B. "Worker v3" (T049): EDIT output mode, test-failure retry (max 2), sample-and-vote for execution specs,
   streaming + heartbeat every 60 s with tokens so far, options num_thread 6 / keep_alive. Pilot
   glm-4.7-flash-class model on 2-3 verified specs.
C. "NUC replies": verify 031/063/064/070-076 as they land; write tests for 070-075 from the committed
   plans; run formula_audit.py once 070-073 are promoted; then first backtests (RSI tolerance sweep,
   CryptoCred setups) per RSI_TF_LAYER_DESIGN D3/D5.
D. Later: Java indicator JUnit tests (priority 3), L6 part 2, make_status stale findings, TF-B5 real-data gate.

NUC remote access (2026-09-28, verified): desktop key ~/.ssh/nuc_gate, forced command
C:\MTS-Worker
uc-gate.ps1 (source: Dumps/workers/NUC-QUEUE/setup-ssh/). `ssh -i ~/.ssh/nuc_gate
e-ngineers@192.168.29.110 status|logs N|ollama-ps|env|restart-worker confirm`; anything else refused
(tested: echo refused). Firewall: port 22 from 192.168.29.188 only; password auth off. restart-ollama needs
task MTS-Ollama (not created). OLLAMA_FLASH_ATTENTION / KV_CACHE_TYPE still unset (operator via RDP);
user env has NUM_PARALLEL=1, KEEP_ALIVE=30m. At 11:20Z NUC on 076 (last queued) - queue about to go idle.

Session 1 closed ~11:30Z. Handoff + next-session waves: NEXT_SESSION_PLAN.md.

## 2026-09-28 - session 2 (Opus supervisor, auto mode)
Operator decisions (asked once at start):
- "Live testing" = BOTH: testnet order runs with Tom core signals + indicator-layer ALERTS (alert-only).
- Core ATR: KEEP plain average of True Range; document it in FORMULAS.md (no Wilder switch).
- R4: L6 part 2 DEFERRED for testnet (L6 re-arm suffices); must be built before any mainnet use.
~13:05Z: queue shows 076 running with a 105-minute-old heartbeat; the SSH gate shows Ollama active (qwen3-coder:30b
loaded, ctx 22528) but TWO worker processes (pid 4084, 10368) - check for a duplicate worker.
Wave 1 launched in background: W1 layers (Sonnet), W2 execution math (Sonnet, staged only), W3 replies
(Haiku), W5 NUC specs 077-081 (Sonnet).

Session 2, ~14:00Z:
- R1 DONE: 08f5ea0 + 61e55f3 (T4 reviewed; operator approved "fix all, then promote"). T4 rejected tick/size
  rounding copied from Python round() and replaced it with side-aware floor/ceil and reject <10 USD. Spot-check
  caught: the new tests were NOT in the run_all_tests step 1 list, and test_risk_guard.py.new would have dropped 9
  tests. LESSON: "gate green" only counts if the new test module is in the gate's list - ask for per-module counts.
- R2 DONE: full run_all_tests.py (Maven + backtest) ALL PASS; NetRRConstantTest 6/6 in surefire.
- R5: layers 070-075 + 077 promoted (tf_realdata_gate: OHLC exact, volume-only diffs, 2023-11-10 at 12%).
  076 formula-audit TIMED OUT (15k prompt tokens, 7200 s limit) -> re-split as 082/083 (<=7k tokens).
  Layer boundary test + OPEN_FINDINGS.md (84de108); only L6 part 2 is open (deferred).
- R6 DONE: BACKTEST_L1_REPORT.md (3e99093). Only 1h RSI-40 support tol 0.5 has PBO<0.05, and its edge is below fees.
  The cc_setups setup2 bars-index vs swings-list-index bug is being fixed.
- The run_all_tests.py working tree holds uncommitted Step 3b/3c guide-checker lines from another session (check_guide.py
  is untracked) - deliberately left out of the commits.
- Next: operator R3 testnet re-run.

Session 2, ~14:30Z (closing - operator conserving tokens):
- 078-081 promoted (13558c0, ae30eda, 4f7204e, 8ea2f68; 081 had 2 fixes). 082 running on the NUC; 083 spec written, not packed.
- Fabio: operator asked "is core MTS + Fabio producing quality setups? identify what Fabio asks in o-w5Gxss6T0 and
  backtest it". Extract exists (FAB-001..009). Backtest agent launched, then STOPPED for tokens before writing files.
  Full brief = NEXT_SESSION_PLAN.md 3.W4. Fabio stays a separate layer; the Tom comparison is descriptive only (override
  ruling still pending with the operator).
- Session 2's W5 auto-pack poller for 083 was stopped with its agent; pack 083 by hand after verifying 082.
- Handoff: NEXT_SESSION_PLAN.md rewritten for session 3.

Session 2, ~15:10Z: R3 DONE (operator approved the supervisor running it). run_testnet_suite_ft2.py after R1 (08f5ea0):
base 6/6, G1/G2 4/4, FT-2 4/4 (T-c breach True at -0.01). Side-aware rounding visible live: C2 short stop
84470.28 -> 84470.0 (floor, toward entry). No HALT files left behind. Readiness gate R1-R4, R6 green; R5 = formula
audit 082 (output hit the 6144 cap - check for truncation) / 083 pending. Tom testnet order runs: READY.
Also committed: operator tooling 309d115 (mts.ps1, guide, new_plan.py), research extracts ba4a396.

## 2026-09-29 supervisor (Opus)
- Filed T058 (broken lows/highs by TF: continuation vs sweep; satellite hedge hook). Sonnet research worker -> T058_BROKEN_EXTREMES.md.
- Sonnet gate worker on 085/086/092-096 -> GATE_REPORT_2026-09-29.md.
- Hourly scheduled task mts-hourly-builder-check (:42) gates new Qwen replies via Sonnet, logs HOURLY_CHECK_LOG.md; lock file prevents overlap.
- 0817968: 085/086 alert runner promoted (nonlocal fix), live smoke --once: 13 alerts, 0 errors. Operator chose A (promotion allowed). Hourly check now Haiku gate-runner; guest-speaker tag for WQ_OAdz-PJ8/zAwEX_tRUfE. T058 decisions (history fetch, hedge timing) still open.
- run_t055.py.new driver staged (22 stub tests pass). Decisions: runbook path fixed to layers/run_t055.py; C2 session=UTC day (1440m) OK; (params,horizon)=grid variant in PBO OK; Sharpe per-trade OK. OPEN: C2/C3 net excludes funding (holds can cross 00/08/16 UTC) - add funding where data exists (2025-09+) before any pass is accepted.

## 2026-09-29 ~03:40-04:40 IST - supervisor session 3 (Opus, bypass mode)
- Operator: "launch as many testnet tests as we can", "assign DSA pending extractions", "new builds -> commit, test, edge cases", handoff.
- Testnet chain 14/14 PASS (testnet_runs/ft2_run_2026-09-29_a.log); account flat; no HALT. Alert runner started continuous (PID 7920).
- 0988 C3 repacked as 0989 (qwen3-coder, OUTPUT_TOKENS 6144). Tom 112-120 withdrawn (duplicates of committed 01d0eed; -a chunks were header-only).
- DSA pack Dumps/workers/DSA_PACK_2026-09-29 (Fabio 0Ky, 0jM, WQ_OAdz-PJ8, zAwEX_tRUfE) + canonical transcripts for the 4.
- verify_extract_quotes.py: [m:ss] markers broke verbatim matching (103/105 false "bad quotes"); fixed + test (fails 2/5 on old code).
- Hourly check SKILL.md: + a2 edge tests, + a3 testnet/alert re-runs; extraction list = fabio 099-111.
- FORMULAS.md s13-16 (T055 cost model, C1-C3) committed (were uncommitted though 0985-0987 were built from them).
- Handoff: NEXT_SESSION_PLAN.md rewritten (asks table for the last 24 h in section 8).

## 2026-09-29 ~04:40 IST - supervisor session 4 (Opus, auto)
- Operator offline; goal = ready for a Deribit MAINNET smoke test (operator-typed, <=50 USD). DSA_OPERATOR_ROADMAP.md tracks A-E for DSA + Jishu (laptop as 2nd Ollama worker; subaccount/key setup; go/no-go; smoke trade).
- Sonnet builder: S5 mainnet flag + mainnet cap + L6 part 2 + guard re-audit + MAINNET_READINESS_CHECKLIST.md. Haiku: Fabio 103/104/105 + R5 repack 082r/083/084. Session cron: supervisor wake every 3 h (:17).
- Mainnet-ready code PROMOTED but UNCOMMITTED (deribit_orders/executor/position_manager/kill_switch/daily_loss_monitor + tests, 33 pass; backups .pre_mainnet). Commit waits on testnet chain, which needs a flat account (smoke trade L-mkt-0928-2240-2 open). Next wake: if flat and no HALT -> run run_testnet_suite_ft2 -> commit "Mainnet-ready gates:" on 6/6+4/4+4/4 (Step 5b turn_of_candle failure is pre-existing, 0989 gate). G-d manager-liveness sweep still PARTIAL.
- Haiku: 103 committed 10759e8; 105 HOLD (quote not in transcript); 082 repacked as 085-formula-audit-a (OUTPUT 15000); 104 + 083/084 still to pack.
- (session 3, ~05:00 IST) Testnet auto-trading live (d77d67c); 9 more layers wired into live runner (4d1bc36); Fabio L1 = NO EDGE
  anywhere (efa1863; only escalation 1h +0.113% OOS net n=182 but PBO 0.756 -> hypothesis). Auto-trader keeps sampling all
  layers on testnet (operator: test every layer); Q3 in NEXT_SESSION_PLAN s9 asks whether to disable no-edge layers.
  COORDINATION with session 4: added execution/AUTO_PAUSE (728f9e1) - pauses only new auto-trades, no HALT - so the
  testnet chain can run on a flat account; message sent to session 4. Note: session 4's uncommitted execution changes are
  used by the auto-trader's subprocess calls (working tree).
- Peer (session 3) note: before the testnet chain create MyTradingSys/execution/AUTO_PAUSE (blocks new auto-trades, no HALT), wait for open trades to close, run chain, delete AUTO_PAUSE. Auto-trader already uses the promoted mainnet-ready working tree.
- DSA_BROWSER_WORKER_PLAN.md: DSA as a paced, human-in-the-loop browser queue worker on the desktop (incoming_dsa lane). Sonnet builds steps 1-2.
- Session 3 stood down (operator). Session 4 = sole supervisor. Its T055 C1/C2 Sonnet agent still running -> will commit "T055 C1/C2 backtest: ..."; pick up verdicts, no duplicate. Watch auto_trader 20676, live_runner 18908, loss monitor 7312, smoke manager 22584.
- T055 C1/C2 (3672305): no pass. C1 15m no edge (n151, -0.40%, PBO .22); C1 1h insufficient (n43, +0.50%, PBO .46); C2 no edge (n519, -0.30%). Funding negligible. Decision (operator order "trade testnet, gather data"): keep C1/C2 sampling on testnet (Q3 default), never a Tom filter; revisit at >=60 events.
- 06:50 IST wake: smoke plan stopped out but manager false-HALTED (stop query order_not_found after trigger -> "unexplained flat"). Real bug, mainnet-relevant. Account flat, no HALT file. AUTO_PAUSE set; Sonnet fixing reconciliation + running FT-2 chain + committing mainnet-ready build, then removes AUTO_PAUSE.
- Queue: 900-902 audits (backfill) running; Fabio 108-111 held (Qwen format: no FILE block / out-of-scope) -> candidates for the DSA lane once calibrated. C3 promoted 5392309.
- Auto-trades so far: 1 smoke entry, 1 entry_failed (slot held by smoke), 27 stale/WAIT_RR rejects. Unmapped rsi:failure side seen x2.
- 2b8b19a committed: mainnet-ready gates + triggered-stop reconciliation (fills via get_user_trades_by_instrument_and_time). Chain 6/6+4/4+4/4 (ft2_run_2026-09-29_b.log). AUTO_PAUSE removed; auto-trading resumed.
- 09:47 IST wake: all runners up, no HALT. 1 real auto-trade since resume (rsi 15m long L-mkt-0929-0200, 02:00Z, managed); 3 skipped_busy behind it (one-slot limit = main data bottleneck -> operator Q2 sub-accounts). rsi:failure left unmapped on purpose (event has no direction; failure of a support vs resistance level is ambiguous - needs a side field from rsi_events).
- Queue idle except hourly audit backfill (906-911 PASS/running; 910 needs operator OVERRIDE for PROJECT_VISION). No new builds. Tokens conserved: no agent this wake.
- 12:47 IST wake: runners up, no HALT. L-mkt-0929-0200 (rsi 15m long @83070.5) open 5h, +1.1%, stop 82240 + target 84731.5 live - healthy; "--hours" is the entry window, not a time exit, so one wide bracket holds the only slot for hours (data bottleneck; consider a layer time-exit or sub-accounts - operator Q1/Q2).
- Other work landed since last wake (d115b0d, 924d7a0, a4d82d6: journal env stamping, mainnet_pnl allow-listed tx types, orphan watchdog not scheduled, model bake-off) - not from this session; queue 3 waiting. No agent this wake.
- 2026-09-29 xferfix: cause = testnet daily P/L used equity delta (default_pnl_source), so a 4x10 BTC subaccount transfer read as -40 BTC and tripped HALT_DAILY_LOSS + kill switch; PM then halted on the cancelled stop.
- Fix commit 1542151: testnet uses the transaction-log P/L (trade-type only) whenever client has get_transaction_log; test_xferfix.py (fails pre-change). Not changed: position_manager treating kill-switch flatten as normal close (note only).
- Halts cleared: HALT + HALT_DAILY_LOSS moved to execution/halt_history/*_2026-09-29_xferfix after verifying main flat, 0 orders (equity 59.9999); monitor baseline reset to 59.99988427.
- 15:47 IST wake: runners up (auto_trader restarted by hourly check, pid 23168), no HALT. rsi 15m trade L-mkt-0929-0200 closed; 2 skipped_busy (malkan_bear, cc fib) while it ran. Another session is active: subaccount transfer false-halt fixed (1542151, testnet P/L from tx log), worker THINK flag, bake-off verdict qwen3-coder primary (26d154f).
- Queue: 946 running, 1 waiting (hourly backfill). 150-152 BLOCKED/153 PARTIAL are bake-off runs, not promotions. No agent this wake.
- L-mkt-0929-0200 closed via manager flatten+halt (stop unreadable 9.2s > 4s) at 08:55Z = 14:25 IST, same minute as the subaccount-transfer false HALT_DAILY_LOSS (halt_history *_xferfix; fixed 1542151) whose kill switch cancelled the stop. Manager reacted correctly (G-d bound works live). No new bug.
- 18:47 IST wake: runners up, no HALT. No auto-trade since 10:49Z (tom WAIT_RR; layers quiet). NUC busy on 121-paste-size-guard (qwen3-coder loaded, CPU 67%; heartbeat stale only mid-generation), 2 waiting. Other session landed time-exit max_hold_minutes (e8fec95), per-layer confirmation lag (c3683bf), operator polling station (8043475). No agent this wake.

## 2026-09-29 (T3 builder) live alert runner: wiring + observability
- Wired turn_of_candle (C3, 1m tf, event toc_m14, NO side: direction of effect not established; ~96 alerts/day, alert-only) into build_default_registry; runner default --tfs now 1h,15m,1m. Tick layer NOT wired: needs tiers.json (absent) and tick net_delta/cvd, not klines.
- RSI "failure" events now carry side (live_layers.rsi_level_layer): resolved below the level -> short, above -> long (entry side is the opposite of the resolving side, read from the RSI value at the event bar). support/rejection/cross stay side-less. auto_trader will now see failure alerts with a side.
- Runner prints a flushed per-poll line with per-layer counts; scripts/dev/alert_rate_check.py (DEAD/QUIET/OK). Live runner restarted (old pids 1892/6632 killed) - see runner_logs.

## 2026-09-29 (T3 builder) operator decisions: outcome ledger, Tom time exit, kill word
- Outcome ledger: execution/trade_ledger.py (+test_trade_ledger.py) writes one row per closed auto-trade to execution/trade_ledger.jsonl (gitignored runtime data); auto_trader.record_ledger hooks trade_closed (never raises; running auto_trader keeps the old code until restarted). `python -m MyTradingSys.execution.trade_ledger --backfill|--summary`, `mts ledger`. Backfill: 2 rows (smoke stop -0.40 USD net; rsi 15m +0.84 net). NOTE the rsi row shows exit_reason "manual": its plan journal dir no longer exists and the exit fill is unlabelled, so a kill-switch flatten (the xferfix false halt) cannot be told apart from a manual close.
- Tom time exit: tom.max_hold_bars=8 of the alert ZONE timeframe (5m->40, 15m->120, 1h->480 min; 15m if unknown). tom.max_hold_minutes still overrides. Zones in the alert history are 5m/15m/1h.
- Kill word: `mts kill-mainnet` / `kill_switch.py --mainnet` now need only the typed word `kill` (deribit_orders.select_environment(True, kill_only=True), used only by kill_switch); --confirm KILL optional on mainnet, required on testnet as before. All other mainnet paths keep the 4 gates + full sentence. MAINNET_READINESS_CHECKLIST.md updated.
- Gates: run_all_tests --quick green; AUTO_PAUSE set, all 5 accounts flat, ft2 suite 6/6 + 4/4 + 4/4, AUTO_PAUSE removed. Backups: *.pre_ledger, *.pre_killword.

## 2026-09-29 (T3 builder) COLLECTION WINDOW START 2026-09-29T14:25Z (19:55 IST)
- Config applied to execution/auto_trader_config.json (accounts block kept): tom size 10 / max_loss 5 / min_net_rr 1.25 / verdicts incl. WAIT_RR / hours 1.0; layers size 10 / max_loss 2 / max_age_bars 2.0 / hours 1.0 (Tom 8-bar and layer 8-bar time exits still on). Verified offline: new_plan + executor dry-run accept a 10 USD market plan with 1% stop (10 USD = Deribit BTC-PERPETUAL minimum contract, so no smaller size exists).
- auto_trader restarted (old pids 23156/16024 stopped, no positions/managers open): new pid 20708, logs Dumps/alerts/runner_logs/auto_trader_20260929_1955.{out,err}, one new "start" event at 14:25:05Z. It now writes the outcome ledger (`mts ledger`).
- RESTORE: copy MyTradingSys/execution/auto_trader_config.json.pre_collect over auto_trader_config.json, then restart auto_trader (stop the python -m MyTradingSys.execution.auto_trader process, start it again hidden with python -u).
- ~20:10 IST: collection window LIVE since 14:25Z (a9cd853 ledger+Tom 8-bar exit+kill word; config .pre_collect; restore cmd above). Runner adc75b3: rsi failure side, turn_of_candle 1m (no side, alert-only), flushed logs, alert_rate_check (expected ~10 tradeable alerts/day total). Audit 910 packed with OVERRIDE-CRITICAL (093889c).
- DATA LOSS (cause unknown): execution/journal/ (L-mkt-* plan journals + auto_manager_logs) was deleted between 15:47 and ~19:30 IST; plans/*.json survived. Not maintainer 972b8b7 (only gitignored). Ledger row is written at trade_closed, so future rows survive; wakes must check the journal dir still holds L-mkt files. Step 3c guide check points at execution/journal/.
- Next wake: if no dispatch after >=1 h of fresh signals -> tom.min_net_rr 1.0 (operator rule). Q1 bracket research job queued (not started).
- 21:47 IST wake: runners up, no HALT. FIRST SUBACCOUNT TRADE: S-mkt-0929-1501 rsi 15m short on jishu_2, entered 15:01Z, closed 15:55Z (routing proven). Its ledger_row had null P/L and no row was written -> Sonnet fixing (plan account for fill reads; always write a row). min_net_rr stays 1.25 (dispatch happened).
- turn_of_candle 1m alerts rejected 7x as unmapped (expected: no side, alert-only). NUC idle (hourly backfills audits a7). Journal dir now holds S-mkt-0929-1501.jsonl; earlier L-mkt loss still unexplained.
