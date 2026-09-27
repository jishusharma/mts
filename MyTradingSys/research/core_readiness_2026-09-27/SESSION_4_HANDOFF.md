# SESSION 4 HANDOFF — Opus 5.5 (+2 Sonnet agents, NUC builder), 2026-09-27 ~14:25-16:40Z
Canonical: MyTradingSys/research/core_readiness_2026-09-27/SESSION_4_HANDOFF.md. Nothing live was modified;
everything is staged as .new (or new files in new folders). Nothing committed. No secrets read.

## 0. TL;DR
- Maven is NOT a blocker any more: JDK 17 + Maven 3.9.9 installed in the linked-computer shell ($HOME/tools, outside
  the repo). Java now builds and tests from here.
- C2 + C3 BUILT (Sonnet) and C3 REVIEWED (Opus: APPROVE). A3 steps 1-8 byte-identical before/after
  (2149/2149 candidates, 30086/30086 fields); A4 sample 417 snapshots, 1828/1828 proof deltas equal the rule.
- G1 + G2 CODED (Opus): position_manager.py (stop shrinks on target fill, re-place/flatten, unexplained-flat halt)
  and reconciler v2 (full netting, unknown-order, unprotected-position checks). Offline logic proof 12/12 PASS.
  Testnet cases staged; mainnet gate stays CLOSED until the operator runs them.
- C5 WRITTEN: compiled_engine.md.new (+22 lines, D5 + D6a/D6b [SYSTEM] notes). T052 filed (.new).
- Backtest: BACKTEST_PROTOCOL.md (pro method) + L1_ADAPTER_REVIEW.md (GO). L1 slice 1 built by Sonnet: gate P0
  350/350. L0 data audit found and FIXED a truncated month (Oct 2025, 27 days missing) and a missing mark day.
- NUC builder used for bt_* modules: 012 engine REJECTED (wrong R accounting; its tests contradicted the spec) and
  rewritten by Opus (12/12 own tests); 011 data loaders ACCEPTED WITH 2 FIXES (dropped first row of headerless
  files; local-time bug in metrics timestamps — would be off 5.5 h on the Windows box). 013/014: see §4.

## 1. Staged files — operator: diff, four-step proof, rename, commit (suggested batches)
Batch A (signal core, Java + verdict): src/main/java/datafeed/SetupCandidatesBuilder.java.new (C3),
  MarketDataSnapshot.java.new (C2), MyTradingSys/backtest/verdict.py.new (C2 guard on top of C1),
  pom.xml.new (+JUnit), src/test/java/datafeed/CountSignalsD4Test.java.new. Report: C2_C3_BUILD_REPORT.md,
  review: C3_OPUS_REVIEW.md. After deploy: verdict_golden --write-baseline in the same batch; I12/I14/I16 live.
Batch B (execution, after session-3 batch): execution/position_manager.py.new, execution/reconciler.py.new,
  execution/testnet/run_testnet_suite_g1g2.py.new, execution/testnet/offline/{test_g1g2_offline,fake_deribit_orders}.py.new.
  Then: `python MyTradingSys\execution\testnet\run_testnet_suite_g1g2.py` (runs C1-C6 first, then G1a/G1b/G2a).
Batch C (engine text, critical): MyTradingSys/runtime/compiled_engine.md.new; MyTradingSys/items/T052_setup_confirmed_trigger.md.new.
Batch D (backtest, not live-path): MyTradingSys/backtest/bt/*.new, src/main/java/datafeed/{HistoricalSource,ArchiveHistoricalSource}.java.new,
  src/test/java/datafeed/P0Gate.java.new.

## 2. Findings that change plans
- F-S4-1 L0 "file exists" != "file complete": Oct-2025 klines truncated, never re-fetched (fixed; quarantine copy kept).
  Fetcher needs a row-count check (L1_SLICE1_STATUS addendum).
- F-S4-2 C3-R1: finished-auction scan takes the OLDEST qualifying event; with D4 direction now matters -> file item.
- F-S4-3 reconciler v2 flags an externally-cancelled stop even after position_manager re-placed it (conservative,
  by design: an external cancel needs operator eyes).
- F-S4-4 NUC throughput is ~4.4 tokens/s (qwen3-coder:30b): a 6k-token module takes ~22 min. Use it for small,
  well-specified pieces with EXPECT lines; always run hidden spec tests on its output (its own tests can be wrong).
- F-S4-5 queue_tool verify marks every NEW file as "unknown/out of scope" -> BLOCKED. Verifier limitation (new files
  cannot be in SCOPE). Proposed fix: allow `SCOPE: dir/` to authorise new files inside that dir.

## 3. Operator steps, in order
1. Batch A diff + four-step proof + commit; restart the loop; after 1 h run core_invariants (I12/I14 = 0, I16 new).
2. Session-3 execution batch (5 files) + Batch B; run the base suite then the G1/G2 suite; paste the output.
3. Batch C (critical file) after reading the 22 added lines.
4. Rule on Tom-vs-Fabio override (proof/absorption/FVG only, recommended).
5. Optional long download on the desktop: `python MyTradingSys\backtest\fetch_binance_archive.py --start 2026-09-13 --end 2026-09-26 --datasets aggTrades`
   (cannot run from the bridge shell: background jobs die with the call).

## 4. NUC tasks 011-014 outcome
011 accepted with 2 fixes, 012 and 013 rejected and rewritten (bt/BT_BUILD_NOTES.md). 014 bt_stats was STILL RUNNING
at handoff (started ~15:48Z, ETA ~16:10Z). Verify it in the next session:
  cd repo; python scripts/worker/extract_nuc_files.py.new 014-bt-stats <tmpdir>   (copy of the extractor, rename first)
  copy MyTradingSys/backtest/bt/_spec_checks/check_bt_stats.py next to it; python -m unittest check_bt_stats
  PASS -> stage bt_stats.py.new + test_bt_stats.py.new (= the check); FAIL -> fix or rewrite, log in BT_BUILD_NOTES.

## 5. RESUME PROMPT for the next chat (paste as-is)
"MTS session 5. Read MyTradingSys/research/core_readiness_2026-09-27/SESSION_4_HANDOFF.md and OPUS_QUEUE_2026-09-27.md
(project doc claude/CORE_READINESS_SESSION4_2026-09-27.md is the summary). Toolchain on the linked shell:
export JAVA_HOME=$HOME/tools/jdk-17.0.20.1+1 PATH=$HOME/tools/jdk-17.0.20.1+1/bin:$HOME/tools/apache-maven-3.9.9/bin:$PATH
(if $HOME/tools is gone, re-download Temurin 17 from api.adoptium.net and Maven 3.9.9 from archive.apache.org;
build only in a copy under $HOME). Tasks in order: (1) verify NUC 014 per §4; (2) whatever the operator reports from
Batch A/B deploy + G1/G2 testnet run -> Opus reviews G1/G2 evidence; (3) L1 wiring slice (Sonnet): HistoricalSource into
fetchHistoricalSnapshot/fetchMultiTimeframeAsOf, fail-closed loader + continuity check, then P1/P1b/P2/canary gates;
(4) fetcher row-count check; (5) bt_runs/ registry + FROZEN.md scaffolding per BACKTEST_PROTOCOL.md.
Rules: never write live files (stage .new), no commits, no secrets, background jobs die with each bridge call."
