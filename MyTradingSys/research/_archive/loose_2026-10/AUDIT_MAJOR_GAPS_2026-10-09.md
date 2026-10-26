# AUDIT: MAJOR GAPS IN MTS (2026-10-09)

Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Surface: App, read-only audit plus filing. HEAD at audit time 5122e8a.
Method: first pass by the session, then a revalidation by four independent read-only workers (live path, backtest/edge claims,
safety tests and duplicated math, recent runtime/Java commits). One concrete claim per worker report was spot-checked by the
session against the repo (0c34a2d diff and tom_bt.py:177; deribit_orders.py:168/:273-281 and daily_loss_monitor.py:362-377;
run_all_tests.py gate list; run_cc_setups.py:102-118 and retention.py:61 with audit_digest.py:12; test_fix3_offline.py:40).
Limits: live tree on JIS-NB and the running processes were not inspected; Maven and the 5 backtest/bt tests were not run;
the Oct-7 rerun data is not reachable here (numbers quoted from the report); Deribit token lifetime and fee schedule unverified.

## 1. Verdict

The fail-closed plumbing around orders is strong. The trading logic has no demonstrated edge, and the evidence for and against
it is itself unreliable. What the audit would stop for: B148 (a subaccount's loss can go unseen by the daily-loss monitor) and
B146/B147 (tiny stops that fees dominate; a live rule with no valid backtest).

## 2. Corrections to the first draft of this audit (revalidation, workers + spot checks)

| Earlier claim | Revalidated |
|---|---|
| Fees give net R -2.8 to -2.9 because Tom stops are ES/DAX-scale | Sign confirmed; the -2.76 R magnitude is an artefact of tiny stops (median 0.082 %) created when 0c34a2d removed the floor. Reframed as B146. |
| Live rule has no history because book/funding/OI are missing | CONTRADICTED by the older run on the same history (19 signals). Reframed as B147. |
| Layer trading is a deny-list that fails open | Blocklist was parked on purpose by the operator on 2026-10-08 (testnet calibration, mainnet independently guarded). Downgraded; the real gap is the gate (B150). |
| Kill-switch mutation survivors K1/K2/K4/M1 | REFUTED at HEAD. test_fix3_mutants_offline.py kills all four and is gated by star-import. The mutation report is stale. Dropped. |
| L6 PnL source is open | Implemented (1542151, 924d7a0) but with a settlement gap; tracker stale. B149. |
| Trial registry has 21 vs 36 rows | 20 data rows on HEAD; the 16 others are on an unmerged branch; no correction applied. In B147. |
| Python and Java net_rr may differ | No discrepancy found; only the cross-test is missing. Low. B153. |

## 3. Findings (ranked) with proof

Each is tracked in research/BUGS.md and items/<file>. Proof lines are in the item docs; summary here.

### B146 (HIGH): No minimum stop width exists since 0c34a2d removed the NO-SOURCE 0.1 % floor and nothing replaced it: Tom backtest median stop 0.082 %, planned gross R:R 79, fees dominate

Item: MyTradingSys/items/B146_no_min_stop_after_floor_removal.md

- 0c34a2d (2026-10-06) deleted MIN_STOP_PCT 0.001 and the 0.2 % fallback in SetupCandidatesBuilder.java (T3 ruling, correct on provenance). Grep of Python, Java and PowerShell finds no other gate that rejects a stop that is too tight relative to fees; SetupCandidatesBuilderStopT3Test.tightSwingStopIsNotWidened pins a 0.05 % stop as KEPT.
- research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md:109: median stop 0.082 % of price, mean fee 2.76 R, mean planned gross R:R 79.46; line 6: sensitivity n=2880 net R -2.91 [-4.35, -1.89], holdout n=181 net -2.80. Before the floor was removed (TOM_CORE_BT_RERUN_2026-10-06.md:19) median stop was 0.200 %, net -0.30, fee about 0.23 R.
- backtest/tom_bt.py:177 fee_r = (entry_fee*entry + exit_fee*px)/risk, i.e. fee divided by stop distance. The -2.76 R magnitude is dominated by tiny stops (mean of 1/stop); the NEGATIVE SIGN is robust: gross R is -0.15 [-0.29, 0.04] before any fee, and random-entry null gross is +0.223 (report line 121). backtest/fees.py:22-23 DERIBIT_MAKER is 0.0 (the 0.0002 maker rate is the Binance profile, fees.py:27): confirm the Deribit maker assumption against the live schedule.
- The only remaining guards are the net_rr fee term and floor 1.25 (a 79:1 planned R:R passes easily) and the per-plan max-loss caps. A far target next to a tiny stop is exactly what looks best to the net_rr test and worst after fees.

Fix shape: Do NOT re-add 0.1 % (NO-SOURCE). Measure instead, pre-registered: net R by stop-width bucket (<0.1, 0.1-0.2, 0.2-0.4, >0.4 %), maker vs taker legs, holdout read once. Derive a fee-based admission rule (reject when round-trip fee > an agreed fraction of the stop distance) from that measurement and flag any constant NO-SOURCE. Also check the Deribit maker fee assumption. Live path: stage, test, supervisor deploys.

### B147 (HIGH): Tom live-rule evidence is unreliable: rerun shows 0 SETUP_FORMING signals but the older run on the same history had 19 (all short); the 'history lacks data' explanation is contradicted; holdout read twice; the Oct-7 run is not on HEAD

Item: MyTradingSys/items/B147_tom_live_rule_evidence_unreliable.md

- Worker recomputation from F:\MTS\data\tom_bt\*.rows.jsonl (120,892 rows): 320 rows at proof 5 and 19 SETUP_FORMING, all short. The rerun (TOM_CORE_BT_RERUN_2026-10-06_full.md:12-14) has rows 90,699 and proof histogram {3: 13,666; 4: 331; 5: none}. The report blames missing book/funding/OI, but the old run had the same history and produced 19 signals and 17 fills. AUDIT_CLOSEOUT_2026-10-07.md:66 says the row drop is 'not yet attributed'.
- H1 (all-short) is not resolved: B131 is CLOSED on a code change plus unit tests only; B135 (post-fix parity re-run of the diag) is OPEN. No post-fix long/short measurement of the LIVE rule exists; only proof>=3 sensitivity variants show parity.
- bt_runs/tom_core_20260929/FROZEN.md (added by f2e7229) says holdout 'run once, this run', and the Oct-7 report reads the same 2026-06-26.. holdout again: used twice. The Oct-7 run directory bt_runs/tom_core_20261007 exists only on origin/research/agenda-2026-10-06 (7aa01cd), not on HEAD, yet the report cites its FROZEN.md. F:\MTS has no tom_bt_2026-10-07 data, so the rerun numbers cannot be recomputed here.
- TRIAL_REGISTRY.csv at HEAD has 20 data rows, not the 36 the report cites (the other 16 are on the unmerged branch). tom_bt_report.py:197 n_trials = lines-1; lines 329-330 only print that DSR 'would need >= 100 trades'; no DSR or multiple-testing correction is computed for Tom (Bonferroni only for 8 Fabio-tag comparisons, none survive). Registry rows count variants of one run, not independent hypotheses.
- Fabio v3 P2: A/B/D have 0 OOS trades (not evaluable), C negative (-0.1038 over 79 days, recomputed from F:\MTS\data\fabio_v3_bt\dayR.json). research/_archive/loose_2026-10/P2_FABIO_V3_HOLDOUT_STATUS.md wrongly says the 2026-06-26.. holdout was read once on 2026-10-04; PRE_REG_FABIO_V3.md:28 says it was not read. SUPERVISOR_LOG.md:269 still says 'P4 8h window PASS', void since the corrected run (075e1c5).

Fix shape: (1) Attribute the row drop 120,892 -> 90,699 and the loss of proof-5 rows (diff the two snapshot generators); until done the live rule has NO valid backtest, say 'insufficient N'. (2) Close B135: re-run the allshorts diag after B131 and report long vs short counts for the live rule. (3) Merge or archive the research/agenda branch so the Oct-7 run is on HEAD; state in FROZEN.md that the holdout has been read twice and treat it as burned for Tom. (4) Count trials honestly and apply DSR/PBO for Tom as for Fabio v3. (5) Correct P2_FABIO_V3_HOLDOUT_STATUS.md and the SUPERVISOR_LOG P4 PASS line.

### B148 (HIGH): Daily-loss monitor re-authenticates as the MAIN account when a named subaccount token expires; it also silently drops accounts on a config read error; orphan sweep can miss orphans and never reports a halt

Item: MyTradingSys/items/B148_dlm_reauth_main_account_and_account_drops.md

- execution/daily_loss_monitor.py:362-377 refresh_named_accounts authenticates each label with MTS_ACCOUNT set, then RESTORES the env. execution/deribit_orders.py:273-281 _call re-authenticates on codes 13009/13010/13011 via authenticate(), which reads MTS_ACCOUNT at call time (:168). After restore it is unset, so the re-auth logs in as MAIN. Worker repro with fakes: get_account_summary returned account_of_token 'tok_MAIN', auth calls ['jishu_7','MAIN']. I re-read both code paths and confirm the mechanism; the real Deribit token lifetime is unverified.
- Effect: a subaccount's PnL is replaced by main's (main counted twice, the loser invisible); on a breach kill_all flattens main again and leaves the subaccount open. Nothing raises, so the failure path never runs.
- daily_loss_monitor.py:357 named_account_labels returns [] on any config read/parse error and is re-read every loop (:405), while auto_trader loads its config once (auto_trader.py:745) and keeps trading those accounts. orphan_watchdog_cli.py:40 falls back to ['fabio'], so no jishu_N account is swept.
- Orphan watchdog: orphan_watchdog_cli.py:99 always calls run_once(..., None, ...), so the log only gets orphan_seen/ok; mts.ps1:198-205 reports only ok and orphan_halt, so a confirmed orphan halt prints nothing. live_accounts decides liveness by pid only; pm_heartbeat.pid_alive treats 'unknown' as alive (:148-180), so a hard-killed position_manager plus Windows pid reuse hides an orphan. The sweep runs once a day (launch-orphan-sweep.vbs, 09:10, 7 x 120 s).
- auto_trader.py:440-445: when a named account's secret file is missing account_for returns None = main slot, so a layer trade goes to the main account at the override size (up to 1000 USD on jishu_14); the only signal is one _account_missing log line.

Fix shape: Failing-first tests, then fixes: (1) make re-auth account-explicit (pass the label into authenticate / keep the label on the client) so a token for jishu_N can only be refreshed as jishu_N, and fail closed (raise, counted by the failure path) if it cannot; (2) config read error must keep the last good account list, not return []; (3) a missing named-account secret must REJECT the layer trade, not fall to main; (4) log orphan_halt from the CLI path and make mts status show it; (5) liveness uses heartbeat age. Safety diff: Opus review. Live path: stage, supervisor deploys.

### B149 (MED): L6 part 2 (daily-loss PnL source) is implemented but the tracker still says OPEN/DEFERRED, and the built source excludes settlement/funding and loses unrealised loss across the 08:00 settlement

Item: MyTradingSys/items/B149_l6_pnl_source_tracker_stale_settlement_gap.md

- Commits 1542151 and 924d7a0 switched the PnL source to the transaction log plus session UPL (mainnet_pnl.py). research/fast_track_2026-09-27/OPEN_FINDINGS.md:31 still says OPEN / DEFERRED.
- mainnet_pnl.py allows only 'trade' entries, so settlement and funding are excluded, while the FIX4_DESIGN decision said to include them. The log window starts 00:00 UTC but futures_session_upl resets at the 08:00 UTC settlement, so an unrealised loss on a position held across 08:00 moves into an excluded settlement entry and drops out of the day total. Layer holds up to 8 bars (8 h at 1h) make this reachable. The --pnl-source help text (daily_loss_monitor.py:388) says 'equity on testnet', contradicting default_pnl_source (:235-242). Real Deribit semantics unverified (worker could not check live data).

Fix shape: Verify against a captured testnet response across an 08:00 settlement; include settlement/funding as decided or record why not; fix the help text; update OPEN_FINDINGS L6. Must be closed before any mainnet use.

### B150 (MED): The test gate is a hand-maintained allow-list: new live-path safety tests (dlm_failure_cap, auto_trader_blocklist, auto_trader_sizes) are not in it; the calibration test pins an empty blocklist; nothing in code enforces restoring the parked blocklist

Item: MyTradingSys/items/B150_gate_is_hand_maintained_allowlist.md

- scripts/dev/run_all_tests.py:91-97 lists execution test modules by name. Worker count: 173 tracked test_*.py, 154 run by the full gate, 19 not run, of which 14 are live code tests, incl. execution/test_dlm_failure_cap.py, test_auto_trader_blocklist.py, test_auto_trader_sizes.py, test_auto_trader_confirm.py (all pass when run by hand, 38 tests). I re-checked that run_all_tests.py names test_dlm_aggregate and test_orphan_sweep_loop but not these. A regression in the DLM failure cap would not fail the gate.
- Three ungated tests FAIL at HEAD (test_audit_t0_checks::test_find_leftover_names_matches_rejected_and_raw, two in tests/test_worker_prefix_hash.py): look Windows-specific, undiagnosed.
- auto_trader_config.json (2026-10-08, '_calibration') parked trade_blocklist; routes ~21 prefixes to jishu_1..jishu_21 with size_overrides 20-1000 USD. Nothing in code reads trade_blocklist_parked or _calibration. test_auto_trader_blocklist.py:96 test_shipped_calibration_config_blocks_no_layer ASSERTS an empty blocklist, so restoring the list (as _calibration instructs) will fail the gate. Mainnet itself stays protected independently (executor called without --mainnet, typed confirmation at deribit_orders.py:177-199, named accounts refused on mainnet :153-155, 50 USD cap).

Fix shape: Make the gate discover tests (glob test_*.py, with an explicit skip-list that needs a reason) or add a check that fails when a tracked execution/ test is neither listed nor skip-listed. Diagnose the 3 failing ungated tests. Replace the empty-blocklist assertion with a check that either the blocklist is present or a calibration flag explicitly allows empty, and add a mainnet-path guard that refuses non-empty-size_overrides/empty-blocklist config.

### B151 (MED): CryptoCred limit-fill backtest fills on touch and drops signals by a future event, so its PASS numbers are upper bounds; maker-entry fee refund applied on touch fills with a 0.1 % stop

Item: MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md

- backtest/layers/cryptocred/run_cc_setups.py:102-118 find_limit_fill fills when low <= level (long) / high >= level (short): TOUCH, though the docstring and commit 37e34ba say 'trades through'. BACKTEST_PROTOCOL.md:51 requires trade-through by 1 tick, and fabio_of_model.py follows it. bt_engine.py targets also fill on touch.
- setup2_fib_pullback (cc_setups.py ~L115-175) emits a signal only if a bar's low lands inside the fib zone, so a bar that blows straight through the zone, fills the limit and hits the stop produces no signal and is never counted. Trades still open at the end of data are dropped (open_at_end -> None).
- Already acknowledged direction: CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:9-13 shows the earlier PASS (sr_flip hit 0.84, fib OOS +0.1687 %) was a fill-bias artefact; with touched limit all three setups FAIL. Worker found no layer with a passing pre-registered result (T055 C1/C2/C3 FAIL, BACKTEST_L1 only the 1h/40 cell clears PBO at +0.043 % OOS, below the 14 bp cost). Headline PASS numbers elsewhere (e.g. AUDIT_RERUNS_2026-10-06.md:12) should be read as upper bounds.

Fix shape: Change the fill rule to trade-through by 1 tick; count a signal as unfilled/lost when its zone is traversed without a fill; report open-at-end trades; re-run the CC setups and update the rerun report. Keep every layer alert-only until a pre-registered, trade-through backtest passes (the parked blocklist is the opposite of that rule).

### B152 (MED): retention.py deletes/trims files that other tools read (audit digest, supervisor canary), irreversibly; deploy of af91b21 will trip on orderflow _state.json

Item: MyTradingSys/items/B152_retention_deletes_read_data_and_deploy_trap.md

- scripts/dev/retention.py:61 deletes Dumps/workers/NUC-QUEUE/done entries older than 14 days, but scripts/worker/audit_digest.py:12,22-39 reads *.task.json/.verdict.txt/.reply.json there, so AUDIT_DIGEST silently loses older findings. It tail-trims runtime_data/supervisor_log.txt to 2000 lines (gitignored, irreversible) although scripts/dev/testnet_canary.py:217 reads its mtime (a daily rewrite makes the canary read 'fresh' once a day) and LOG_GAP_2026-10-02.md cites line 16365 of it as outage evidence. The Dumps.pre_B138 'strict subset' check compares sizes only (retention.py:33-38). Scope is otherwise narrow: it cannot reach ledgers, journals, auto_trades.jsonl, HALT history, transcripts or orderflow/OI data. Dry run is the default; launch-retention.vbs passes --apply.
- af91b21 untracked the orderflow recorder _state.json: on the live tree git merge --ff-only will abort (file modified by the recorder) or delete it; without it orderflow_live.py:187-190 restarts at the current minute and the minutes since the last write are never fetched. The supervisor must copy the file before deploying (mechanism only, live tree not inspected).

Fix shape: Exclude audit-read paths from retention or change audit_digest to read an archive; keep a dated copy before trimming logs; make the subset check content-based. Add the _state.json copy-and-restore step to the deploy runbook.

### B153 (LOW): net_rr floor stays at NO-SOURCE 1.25 with no owner for the 'restore after P4' note; Python and Java net_rr have no direct cross-language parity test; B136 residual still fail-open

Item: MyTradingSys/items/B153_netrr_floor_ownerless_and_cross_language_parity.md

- system/net_rr_floor.json still 1.25, note 'lowered for testnet collection; restore after P4'. P4 ended NO REPLICATION at 4h/8h/12h (075e1c5, research/_archive/loose_2026-10/P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md; net -9.6 to -10.2 bp, CIs below zero). P4 is a different study, so its closure does not trigger a restore and nothing tracks one (only SUPERVISOR_LOG.md:260 'edit that one line').
- Worker re-computation: entry 60000, stop 59940, target 60180 gives net_rr 1.0 in Python (mts_math.py:78) and by hand in Java (ExecutionMathConstants.netRR); no discrepancy. No test feeds the same inputs to both; parity is indirect (test_b070_fee_parity.py compares constants; NetRRConstantTest.java:28 and test_mts_math.py:229 assert the same vector).
- B136 residual confirmed: MarketDataSnapshot.java:1498-1541 buildOiBreakdown still writes retail/whale/topAccounts as 0.0 on failure (confidence LOW, no unavailable_fields). No production Python reader of oi_breakdown found, so impact is limited to the snapshot JSON.

Fix shape: Operator decision with owner and end date: restore 2.0, keep 1.25 with expiry, or pause Tom trading. Add one table-driven Python/Java parity test (expected values from FORMULAS.md section 17). Close B136 by emitting UNAVAILABLE.

## 4. Overdone (opinion, for the operator)

- 284 research .md files (about 413k words) against 321 Python files in MyTradingSys; the Direction Review (2026-10-02) found
  zero Tom or Fabio testnet trades in 72 h of document and audit output. Fabio v3 has 93 unit tests, shadow-only alerts and a
  failed pre-registered OOS (0 trades for A/B/D). 21 testnet accounts now route layers whose backtests failed or never ran.
- Suggested rule: no new audit document and no new layer until B146, B147 and B148 report.

## 5. Not verified (open questions)

Whether the running JVM/runner restarted onto the 2026-10-08 code; real Deribit token lifetime and 08:00 settlement behaviour;
Deribit maker fee schedule; why 3 ungated tests fail; the Oct-7 Tom run data; Maven tests for ArchiveHistoricalSource.

Also noted by workers, lower priority: ArchiveHistoricalSource drops the Sunday 23:00 bar (167 vs 168 bars, archive/live VPOC
parity, MarketDataSnapshot.java:1077-1092); fetch_binance_archive.py:67 skips a half-extracted day permanently;
refresh_klines.py grows the backtest input in place (pin date ranges); consensus rows are write-only (nothing reads
Dumps/consensus); hook.py:86-96 takes the newest snapshot with no age check; 652ebfb made book_imbalance 0.0 fail-open by
operator approval and the harness no longer guards that case.

## 6. Actions requested of coming sessions

See SUPERVISOR_INBOX.md entry of 2026-10-09. Order: B148, B146, B147 (first), then B150, B149, B151, B152, B153.
