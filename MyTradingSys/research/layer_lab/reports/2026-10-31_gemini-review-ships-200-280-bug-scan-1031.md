# Layer Lab Report: Cross-Vendor Bug Scan of Fast-Track Code Commits 200 to 280

Task: gemini-review-ships-200-280-bug-scan-1031
Lane: CODEX
Reviewer: Gemini 3.8 Flash (independent cross-vendor review)
Date: 2026-10-31 (UTC 2026-10-31)

## Summary of Findings

A cross-vendor diff-vs-Result audit was performed on fast-track code commits 200 to 280 touching `.py`, `.java`, or `.js` under `MyTradingSys`.

- Total commits analyzed: 80 (SOURCED: `git log --no-merges --format=%h -- MyTradingSys/**/*.py MyTradingSys/**/*.java MyTradingSys/**/*.js` skip 200 take 80)
- Commits with explicit `Result:` lines matching diff: 76 / 80
- Commits without an explicit `Result:` line: 4 / 80 (Rows 12 `218bb1c2b`, 13 `3d109ca0c`, 14 `18161df7c`, and 76 `c0c5b7ea0` - standard git reverts/re-applies)
- Commits requiring functional code FIX: 0 / 80
- Full evaluation table: `MyTradingSys/research/gemini_burn_2026-10-31\SHIPS_200_280_REVIEW.md` (80 rows).

## Detailed Review Breakdown

| Row | Commit | Subject | Verdict | Key File:Line Cited |
|---|---|---|---|---|
| 1 | `cd5cca601` | live read: 2H footprint read, watcher triggers at 79,923 and 79,836, rows to 21:4xZ | OK | `MyTradingSys/research/live_reads/2026-10-26_cross_market_tools/watch.py:55` |
| 2 | `11ddfd25a` | sim desk: refuse bar/result/fetch timestamps at or after the sealed cut (L1-L7) | OK | `MyTradingSys/research/sim_desk/desk.py:245` |
| 3 | `451af24c3` | levels: raw DEV fill ledger for E1 S2 K5 X0_2R (255 filled + 517 unfilled) | OK | `MyTradingSys/research/design_cards_2026-10-26/levels_raw_ledger/export_ledger.py:1` |
| 4 | `f04a3cbad` | T09-F3: live RSI trades only support@40 long; cross, failure, rejection are alert-only | OK | `MyTradingSys/backtest/layers/alerts/live_layers.py:147` |
| 5 | `597f67416` | lease: cards/docs-only ship passes with a foreign Pipeliner lease | OK | `MyTradingSys/tests/test_lease.py:300` |
| 6 | `92233077c` | pipeliner: station watch 10-26 - monitor fix + 2 mechanism cards + lesson seed | OK | `MyTradingSys/research/pipeliner/station_watcher_monitor.py:30` |
| 7 | `db9207a2d` | live read 10-26: US session record, divergence events, MTF bias ladder, 3 cards | OK | `MyTradingSys/research/live_reads/2026-10-26_cross_market_tools/mtf_bias.py:1` |
| 8 | `4271cb142` | DSA bridge everywhere: aibridge_install --fresh, aibridge_verify.py, laptop installed, NB/NUC brought to B196 | OK | `MyTradingSys/tests/test_aibridge_install_fresh.py:1` |
| 9 | `4b2e525dd` | Audit five planted CBP rows and preserve three known validation failures | OK | `MyTradingSys/tests/test_cbp_query.py:2` |
| 10 | `1b23396e9` | Repair CBP ingestion and wire twice-daily task | OK | `MyTradingSys/tests/test_cbp_query.py:1` |
| 11 | `74727bd43` | raw_1d vs 1m resample: label 9 loaders T01-F2 (EOF, no line shift), DATA_NOTES entry, label test | OK | `MyTradingSys/backtest/layers/timeframe/tf_realdata_gate.py:215` |
| 12 | `218bb1c2b` | Revert "Confluence S3: standalone context read, D1 FAILS vs naive trend on DEV" | UNVERIFIED | `MyTradingSys/backtest/layers/krown/run_context_read.py:1` |
| 13 | `3d109ca0c` | Revert "run_context_read: name forward outcome variables for the look-ahead lint (no number changes)" | UNVERIFIED | `MyTradingSys/backtest/layers/krown/run_context_read.py:1` |
| 14 | `18161df7c` | Revert "raw_1d vs 1m resample: label 9 loaders T01-F2, DATA_NOTES entry, label test" | UNVERIFIED | `MyTradingSys/backtest/layers/timeframe/tf_realdata_gate.py:1` |
| 15 | `47a8afe2e` | raw_1d vs 1m resample: label 9 loaders T01-F2, DATA_NOTES entry, label test | OK | `MyTradingSys/backtest/layers/timeframe/tf_realdata_gate.py:1` |
| 16 | `ad4e461d6` | mfe_exit: DEV pass filters fires by t_fire_ms < 2024-07-01, not the stale split label | OK | `MyTradingSys/research/mfe_exit_2026-10-13/mfe_exit_study.py:24` |
| 17 | `7219cde80` | run_context_read: name forward outcome variables for the look-ahead lint (no number changes) | OK | `MyTradingSys/backtest/layers/krown/run_context_read.py:1` |
| 18 | `73e488af6` | Confluence S3: standalone context read, D1 FAILS vs naive trend on DEV | OK | `MyTradingSys/backtest/layers/krown/run_context_read.py:1` |
| 19 | `81772ccca` | pipeliner: hand-over NEXT_SESSION.md + station watcher monitor script | OK | `MyTradingSys/research/pipeliner/station_watcher_monitor.py:1` |
| 20 | `163f5c12d` | live read 2026-10-26: BTC vs ES/NQ at US open, watcher tools, 3 cards | OK | `MyTradingSys/research/live_reads/2026-10-26_cross_market_tools/chk1m.py:1` |
| 21 | `59424d8d7` | WORKERS rule 9: Blocked - solve it, then report AND continue | OK | `MyTradingSys/tests/docs/test_integrity.py:203` |
| 22 | `512cb754b` | OPS_CHANGE_CHECK.md: 8-question reach test, cited by Lead and DEBUGGING | OK | `MyTradingSys/tests/docs/test_integrity.py:190` |
| 23 | `a15b35fed` | RV05 H2: adjudicate Fabio ledger entry/stop against full-res position lines | OK | `MyTradingSys/research/fabio_transfer/check_rv05_h2.py:1` |
| 24 | `d6e300a5d` | role_hook_launcher: bare 'login A\|B\|C' loads the Supervisor from trunk even in a checkout whose own loader is stale | OK | `MyTradingSys/tests/test_role_hook_launcher.py:42` |
| 25 | `40b784d59` | role_loader: bare 'login A\|B\|C' starts the Supervisor (one-word start per login) | OK | `MyTradingSys/tests/test_role_loader.py:478` |
| 26 | `9d61cb293` | rsi-deep-prob-tables fix: report non-survival share first, relabel window-selection allowlist rows, add beyond-window test | OK | `MyTradingSys/research/rsi_deep_buy_2026-10-19/prob_tables.py:406` |
| 27 | `e77be3a0d` | T10-F4: DEV stability table per study (per year, long/short, top-5 days removed) | OK | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/stability.py:1` |
| 28 | `7e72e3432` | T10-F2: intrabar stop-first vs target-first bounds for Tom, Fabio v3, bt_engine (DEV/VALIDATION) | OK | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/intrabar_bounds.py:1` |
| 29 | `28565f801` | RSI deep-buy Phase 1D-E: depth/bounce probability tables, DEV then VALIDATION | OK | `MyTradingSys/research/rsi_deep_buy_2026-10-19/prob_tables.py:1` |
| 30 | `58251261a` | oi-pivot-reversal-probability-by-tf: PRE_REG, causal candidates, DEV 30-day pilot table | OK | `MyTradingSys/research/oi_pivot_2026-10-26/candidates.py:1` |
| 31 | `8f8a52814` | bt_data.load_klines: convert microsecond stamps, raise on conflicting duplicates, report dups/gaps/unsorted | OK | `MyTradingSys/backtest/bt/bt_data.py:5` |
| 32 | `06d98b8ae` | T08: orderflow study DEV-only by default, guard_phases for protected phases | OK | `MyTradingSys/research/orderflow_views_2026-10-14/study.py:211` |
| 33 | `3dc47d91d` | Audit cross-station task flow; queue priority Claude review | OK | `MyTradingSys/research/coordination_audit_20261026/reproduce.py:1` |
| 34 | `f8d0799de` | research/ top level: 189 -> 14 files; 176 dated loose files into _archive/loose_2026-10 and loose_code, refs rewritten | OK | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:124` |
| 35 | `fd31f8f6b` | analysts: Roman Trading volume-absorption call ingestion adapter | OK | `MyTradingSys/research/analysts/roman/__init__.py:1` |
| 36 | `1fd982416` | G3 pack: bound anchors to shown bars, daily path from argument, input digests writer | OK | `MyTradingSys/research/trendlines_2026-10-17/g3_pack/g3_pack.py:17` |
| 37 | `79f288d88` | test_lease: fewer git spawns (held-lease template, 1-round push-error test, trunk read from origin) | OK | `MyTradingSys/tests/test_lease.py:56` |
| 38 | `ecaacb117` | Trend-line contract v1.1: close-arm penetration, no pre-availability replay, narrowed E11 (audit gaps 1-3) | OK | `MyTradingSys/backtest/layers/trendlines/test_trendline_core.py:296` |
| 39 | `4f32dd966` | T05 audit recount: fix F1/F2/F3 wording, file the S1 LC1 card | OK | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/build_report.py:30` |
| 40 | `612fc6338` | confluence-s1-f6-direction: exp_dir_4h_ours to F6 (sign since BBWP_4h last <= 50), recount | OK | `MyTradingSys/backtest/layers/krown/krown_context.py:26` |
| 41 | `92bd04e27` | Remove leaked test card shipped.json; keep test_tasks_stop from saving cards | OK | `MyTradingSys/tests/test_tasks_stop.py:24` |
| 42 | `c8aa7d9c8` | tasks.py: next hides, take refuses, brief opens with STOP for SHIPPED/STALE cards | OK | `MyTradingSys/tests/test_tasks_stop.py:1` |
| 43 | `2c9bbaf9c` | Lead role core + 4 mode files, roster 10 to 7 (card lead-role-core-and-modes) | OK | `MyTradingSys/tests/test_role_budget.py:11` |
| 44 | `b68a73130` | mts_run: refresh the runner tree from origin/fast-track before each card pick | OK | `MyTradingSys/tests/test_mts_run.py:3` |
| 45 | `2730ef09b` | sim desk krown test: planted leak without the forward-index pattern the lint flags | OK | `MyTradingSys/research/sim_desk/test_krown.py:49` |
| 46 | `1f6571e6c` | sim desk krown: review fixes (cache hash, honest S8 label, daily warm-up note, trade-construction test) | OK | `MyTradingSys/research/sim_desk/studies/krown.py:5` |
| 47 | `60f53e24c` | sim desk: Krown study (S5/S8/S4), exploratory, DEV only | OK | `MyTradingSys/research/sim_desk/studies/krown.py:1` |
| 48 | `abe586637` | role_loader tests: keep TestModeCommand above the __main__ guard | OK | `MyTradingSys/tests/test_role_loader.py:462` |
| 49 | `99712eb55` | role_loader: mode <name> subcommand serves roles/lead/<name>.md from trunk | OK | `MyTradingSys/tests/test_role_loader.py:464` |
| 50 | `67426492d` | sim desk: breakdown table, folded charts and ledger, catalogue-safe run saving | OK | `MyTradingSys/research/sim_desk/build_catalogue.py:90` |
| 51 | `38ca6ef6b` | research: rename GPT proposed fvg-side test so the extra-tests gate does not run it | OK | `MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/proposed_test_volume_fvg_side.py:1` |
| 52 | `bf1f9c6ed` | T09-F2: label paths relative, cc label split so wiring_scan sees no runtime reference | OK | `MyTradingSys/execution/auto_trader.py:52` |
| 53 | `e587164a8` | T09-F2: per-layer exit table; rsi_events 15m/1h trade the RSI backtest bracket, cc 1h trades the event stop, rest stay SAMPLING | OK | `MyTradingSys/execution/auto_trader.py:72` |
| 54 | `c0133da81` | sim desk: review fixes (runs without a stated window hidden, exact ids, query strings, side-by-side race) | OK | `MyTradingSys/research/sim_desk/desk.py:413` |
| 55 | `80d63bacd` | sim desk: one-command launcher, study chips + DEV banner, saved-runs table and side-by-side | OK | `MyTradingSys/research/sim_desk/desk.py:1` |
| 56 | `8e56554c1` | research: harvest NUC overnight burn (3 Gemini gb2, Fabio retry notes, 6 GPT gx4) + NUC_HARVEST.md | OK | `MyTradingSys/research/gpt_burn_2026-10-24/gx4-statecode-races/StateCodeEmitter.java:1` |
| 57 | `e381a45d8` | gemini_queue: timeout and no credential prompt on every git/sync call | OK | `MyTradingSys/tests/test_gemini_claim_skip.py:24` |
| 58 | `5603ff871` | T09-F1: live volume_fvg takes the backtest bounce side, scan from confirmed_i+1 | OK | `MyTradingSys/backtest/layers/alerts/live_layers.py:40` |
| 59 | `6868a4650` | Context files design: card + fixed-form handover, fold-on-ship hook, measure as gate | OK | `MyTradingSys/research/mts_doctor/context_files/coldstart_baseline.py:1` |
| 60 | `11b8f95c4` | sim-v2: re-land slippage box (0.02 %, ours) with its 3 costs.csv rows | OK | `MyTradingSys/research/sim_desk/studies/_bars.py:20` |
| 61 | `cceaedf7b` | Revert sim-v2 slippage box (1282d9c21): CI red on T06 cost inventory | OK | `MyTradingSys/research/sim_desk/studies/_bars.py:20` |
| 62 | `afd937964` | sim-v2: Monte Carlo reshuffle band on the equity curve and a luck line under the verdict | OK | `MyTradingSys/research/sim_desk/desk.py:91` |
| 63 | `2f2954f6e` | sim-v2: clickable trade list; a row opens that trade's candle chart (/api/trade) | OK | `MyTradingSys/research/sim_desk/desk.py:94` |
| 64 | `b99094841` | sim-v2: equity curve shades the drawdown and shows the worst drawdown beside the scrub readout | OK | `MyTradingSys/research/sim_desk/test_conditions.py:196` |
| 65 | `1282d9c21` | sim-v2: slippage box on every study (default 0.02 %, ours) on market and stop fills | OK | `MyTradingSys/research/sim_desk/studies/_bars.py:20` |
| 66 | `bba212e80` | sim-v2: standard numbers strip (win rate, profit factor, max drawdown, gross/fee/net per trade) | OK | `MyTradingSys/research/sim_desk/desk.py:76` |
| 67 | `3ecd38c21` | sim-v2 (e): every desk Run writes results/desk-<study>-<hash>.json in the standard schema | OK | `MyTradingSys/research/sim_desk/artifact/build_artifact.py:205` |
| 68 | `533eab730` | sim-v2 (d): equity curve in R and $1,000 (scrubbable) plus run A vs run B side by side | OK | `MyTradingSys/research/sim_desk/desk.py:73` |
| 69 | `0337601f0` | sim-v2 (c): Run time reported on every run, cached Run under 10 s (tested) | OK | `MyTradingSys/research/sim_desk/test_conditions.py:163` |
| 70 | `de7acbac6` | sim-v2 (b): shared CONDITIONS panel for any layer (side, UTC hours, EMA trend, ATR percentile, weekday, layer B within N bars) | OK | `MyTradingSys/research/sim_desk/conditions.py:1` |
| 71 | `0fc67ac06` | sim-v2 (a): reference tests per desk study, filled trades only, fee-net | OK | `MyTradingSys/research/sim_desk/test_reference.py:1` |
| 72 | `2bd5dcdf2` | T09-F5: funding_cvd_fade re-tested on 1h bars, DEV only, fee-net | OK | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/f5_funding_cvd_1h.py:1` |
| 73 | `11850c8c7` | test_lease: build repos once per run, trim 4-round push-error test (no sleeps), skip global git config | OK | `MyTradingSys/tests/test_lease.py:1` |
| 74 | `14f1703b9` | lookahead_lint: stop flagging chunk and regex text-window slices | OK | `MyTradingSys/tests/test_lookahead_lint.py:60` |
| 75 | `9be3f415e` | rsi/cc: re-land real-funding DEV rerun with lint-clean forward slice | OK | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:107` |
| 76 | `c0c5b7ea0` | Reapply "rsi/cc: load real funding for DEV rerun" (red trunk: new look-ahead FAIL hit run_rsi_backtest.py:111) | UNVERIFIED | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:247` |
| 77 | `bd11ebf78` | sim-v2: catalogue of every known test, WaveTrend export, kind/parity/ROI fields | OK | `MyTradingSys/research/sim_desk/artifact/build_artifact.py:93` |
| 78 | `13da5c4cc` | sim-v2: one simulator page for every test (levels ladder fixed to filled trades) | OK | `MyTradingSys/research/sim_desk/artifact/build_artifact.py:1` |
| 79 | `c7f5eefb8` | T05 backtest audit: placebo nulls, best-of-N bars, fair LC1 control | OK | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/build_report.py:1` |
| 80 | `c725894db` | T09: chunk indices with array_split (same sums, clears fwd-index lint) | OK | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/exit_analysis.py:21` |
