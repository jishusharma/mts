# Session MTS-2026-10-01-1858Z-CLD-BLD-two-cores: TWO CORES READINESS (W1 wiring, W2 test gaps, W3 revalidation)
Base: origin/main a6445e3. Branch alias: claude/cool-gauss-dx5ht5. Budget row: 85 assumed (usage unreadable), so one parent pass, no subagents, no fix pass.
Method: static read of committed files only; no process, gitignored file, LAN or F: data was visible. "unknown" = not decidable from the clone.

## W1. Wiring check (rows of WIRING_MAINTENANCE_AUDIT_2026-10-01.md section 1, at HEAD)
| # | Path | State | Evidence |
|---|---|---|---|
| 1 | Java feed -> math_object_builder -> verdict -> Tom alert, LONG side | BROKEN | runtime/math_object_builder.py:399 defaults book_imbalance to 1.0 only when the key is absent; a present 0.0 (no data) passes :413 (`_book < 0.33`) and adds "ask-heavy vs LONG". Operator-approved fix not in committed code. A staged .new is unknown (gitignored) |
| 2 | live_runner_cli -> alerts -> auto_trader | PARTIAL | code at backtest/layers/alerts/live_runner_cli.py (298 lines; registry ~150-195), emits via live_runner_core.py:149; no launcher: mts.ps1 has no runner verb (grep "runner" empty) and "status" (mts.ps1:113-150) does not report it |
| 3 | auto_trader -> new_plan -> executor -> position_manager -> trade_ledger | OK | mts.ps1:244-246 (auto-trader verb); auto_trader.py:11-19 header; trade_ledger.record_closed called at auto_trader.py:371 |
| 4 | daily_loss_monitor | OK | mts.ps1:238-239; status line mts.ps1:141 |
| 5 | orphan_watchdog_cli | MISSING (launcher) | code execution/orphan_watchdog_cli.py + tests exist; no mts.ps1 reference (grep "orphan" empty) |
| 6 | cryptocred classify_msb (live, jishu_4) | PARTIAL | cc_structure.py:81 now has filter_range_noise=False (default off); callers cc_setups.py:36,67,153 pass `**(msb_kwargs or {})`. Whether live passes the flag is unknown (live_layers.py not traced in this pass) |
| 7 | tick layer | OK (by decision) | no "tick" entry in live_runner_cli.py (grep empty); decision SUPERVISOR_LOG:170 per audit |
| 8 | Fabio v3 | MISSING | only backtest/layers/fabio/pending_test_fabio_v3.py; no v3 module in backtest/layers/fabio/; spec research/fast_track_2026-09-27/FABIO_V3_SPEC.md |
| 9 | queue/consumer.py (CBP) | OK (ack-only, by decision) | queue/consumer.py present; no auto_trader import (grep not run on every file: unknown beyond auto_trader.py) |
| 10 | testnet_status.py | PARTIAL | scripts/dev/testnet_status.py + test; research/testnet_status/TESTNET_STATUS_2026-10-01.md now exists (audit said never run); scheduling unknown |
| 11 | Handoff cloud -> SUP | BROKEN (unverifiable consumption) | SUPERVISOR_INBOX.md 26 lines; SUPERVISOR_LOG.md last "- inbox" line is 2026-09-29 (SUPERVISOR_LOG:203) |
Extra, new at HEAD: no consensus writer exists (grep "consensus" in code: none, only docs); TF maps lack 3m and 1d: scripts/dev/alert_rate_check.py:23 TF_MIN has 1m,5m,15m,1h,4h; execution/auto_trader.py:47 TF_SECONDS has 1m..1d but no 3m. Architecture wants RSI keys 1m,3m,15m,1h,4h,1d (ARCHITECTURE_TWO_CORES_2026-10-01.md:39). Execution/{plans,journal} dirs absent in clone (gate step 3c).

## W2. Test gap inventory (BUGS.md:123, T037, 8 engine files)
| File | Tests that exist | Missing |
|---|---|---|
| src/main/java/datafeed/MarketDataSnapshot.java | none in src/test; only Python references backtest/tom_bt_report.py, l1_patch_mds.py (not tests) | snapshot field contract, OI delta state (T033 sites) |
| SetupCandidatesBuilder.java | src/test/java/datafeed/SetupCandidatesBuilderHvnTargetTest.java, NetRRConstantTest.java, CountSignalsD4Test.java, ExtraSetupBuilderFvgTest.java (references it) | entry/stop construction, proof-count paths (unknown if covered by CountSignalsD4) |
| StateCodeEmitter.java | none (grep src/test empty) | state letters, bull/bear counts |
| ExtraSetupBuilder.java | ExtraSetupBuilderFvgTest.java | non-FVG setups |
| SetupScreener.java | none | gate/screen logic |
| runtime/update_market_state.py | none (no test_ file imports it) | all |
| runtime/quad_classify.py | none | four quadrant truth table (price x CVD x OI) |
| runtime/regime_classifier.py | none | all |
Note: BUGS.md:123 predates 4 Java test files; its "ZERO coverage" is stale for SetupCandidatesBuilder and ExtraSetupBuilder. Java tests not run (no Maven in this task).

## W3. Revalidation table (W1-W8 of REVALIDATION_ACTIONS_2026-10-01.md)
| Item | Status | Evidence |
|---|---|---|
| W1 citations | PARTIAL | REVALIDATION_ACTIONS:72-120: 0 of 9 papers opened (egress); 4 packages opened on PyPI |
| W2 DSR trial count | DONE | :122-159, N=3 lower bound, 16 upper readable; true N unknown |
| W3 kappa | NOT-STARTED (blind packet only) | :161-182; W3_BLIND_PACKET_2026-10-01.md, scripts/dev/kappa_check.py; needs clean reader |
| W4 NO-SOURCE re-search | DONE | :184-216 (A08, A11 reclassify candidates) |
| W5 section 10 fields | DONE | :218-231 |
| W6 Fabio provenance | DONE (single reader) | :233-241; FABIO_PROVENANCE_AUDIT_2026-10-01.md |
| W7 backtest fix order | PARTIAL | :243-246: plan only, no fix applied |
| W8 pre-register T2 | PARTIAL | :248-250: PRE_REG_T2.md written; T2 not run, needs F: data |

## Merged priority list (ranked; fixes NOT applied, wave 2 skipped by budget gate)
1. book_imbalance 0.0 treated as ask-heavy vs LONG (W1 row 1): live-safety, blocks Tom LONG. math_object_builder.py:399-413.
2. Fabio core missing as a compiled peer (row 8): blocks the two-core doctrine.
3. No consensus writer; 3m/1d absent from TF maps (extra): blocks acceptance tests of ARCHITECTURE_TWO_CORES.
4. live_runner_cli and orphan_watchdog_cli have no launcher/status (rows 2, 5): mts.ps1.
5. Untested engine files: StateCodeEmitter, SetupScreener, update_market_state, quad_classify, regime_classifier, MarketDataSnapshot (W2).
Then: classify_msb live flag (row 6), SUP inbox consumption (row 11), W3 clean reader, W1 desktop verification.

## Top-5 fix descriptions and acceptance checks (proposals only; not staged)
1. In math_object_builder.py treat book_imbalance of 0.0/None as no data (skip the contradiction). Test: proof book_imbalance=0.0 with LONG yields no "ask-heavy" contradiction; must FAIL on current code. Acceptance: that test passes; test_math_object_builder.py, test_proof_direction.py unchanged.
2. Fabio core module (per scaffold section 2). Acceptance: disable Tom, Fabio verdicts unchanged and vice versa.
3. Consensus writer (scaffold section 3) + add 3m/1d to TF maps. Acceptance: fire N alerts, count N rows, six TF keys present.
4. Add mts verbs for runner and orphan watchdog and report them in status. Acceptance: mts status prints both lines.
5. Add pure-function tests for quad_classify and regime_classifier first (smallest). Acceptance: new tests fail on a deliberately broken copy once.
Each live-path item touches execution/ or layers/alerts/: ownership claim in SUPERVISOR_LOG required before staging .new; no builder restarts live processes.

## Gates
Docs-only commits; run_all_tests.py --quick not run (no code file changed). 
