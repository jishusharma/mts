# BUILD PIPELINE
# Session: MTS-2026-10-03-0328Z-DSA-COO
# Written: 2026-10-03
# Reconciled to disk: 2026-10-03T06:00Z by MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd (14 stale rows, WORK_REVIEW_2026-10-03 section 1.2)
# Purpose: single queue for all pending work. One row per item. Every item runs
#          the same T0-T5 contract and the same gate. Waves run in order.

## HOW AN ITEM RUNS

1. Read the row. Read the item doc.
2. Compose a CL or DSA prompt carrying a T0-T5 contract (same shape R4 used):
   T0 questions answered first, T1 file shape, T2 output shape,
   T3 tests (fail-before proof), T4 disk verification, T5 MISSED deviations.
3. Ship the prompt. Wait for reply. Same-turn verify against disk.
4. Gate: T1-T4 PASS, tests pass, Build-Check PASS, commit with session ID trailer.
   Live-path items also restart and verify.
5. Mark LANDED. Move to next row.

An OPEN or IN-FIX id in research/BUGS.md with no row here is still picked: scripts/sched/pick_task.py sweeps it
into one wave after the last wave below (B089). Add a row only to set its order; on close a LANDED row is the record.

## STATUS VALUES

QUEUED / IN-FLIGHT / GATED / LANDED / BLOCKED / PARKED

## WAVE 0 - SCAFFOLD

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 0.1 | - | OPERATOR_DIRECTIVE_2026-10-03-historical-testing.md | LANDED | - | - |
| 0.2 | - | BUILD_PIPELINE.md (this file) | LANDED | - | indexed in 03_FILE_INDEX.md, commit 5a6ec09 |
| 0.3 | - | 03_FILE_INDEX rows for 0.1 + 0.2 | LANDED | - | rows present, commit 5a6ec09 (wave 0.3) |
| 0.4 | B088 | session-id surface code CLI + cooldown source | LANDED | - | BUGS + INDEX CLOSED; direct fix, row for the record; session MTS-2026-10-03-1230Z-CLI-BLD-fix-b088-b089 |
| 0.5 | B089 | pick_task.py sweeps BUGS-only OPEN ids | LANDED | - | BUGS + INDEX CLOSED; direct fix, row for the record; session MTS-2026-10-03-1230Z-CLI-BLD-fix-b088-b089 |

## WAVE 1 - UNBLOCK

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 1.1 | B080 | dsa_worker hourly-cap misfires on stale pace entries | LANDED | - | BUGS + INDEX CLOSED; commits f97a441, 17d74f7 |
| 1.2 | B075 | historical mode unfit for backtesting | QUEUED | - | partial at 86313de (no live calls, flow fields null + UNAVAILABLE, session attached). Residual: candidates still emit book_imbalance 0.0 and read net_delta via asDouble (SetupCandidatesBuilder.java:552,635,822). Registry stays OPEN |
| 1.3 | TF1 | gate: Fabio v3 + orderflow_live + htf_context tests into run_all_tests | LANDED | - | add MyTradingSys/backtest/layers/fabio/v3/tests, test_orderflow_live.py, test_htf_context_live.py to scripts/dev/run_all_tests.py (119 pass today, 0 gated); MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md E7 ; CLOSED: PYTEST_LAYER_PATHS in step 4 (119 pytest now gated), step 3g guard test, fail-before shown; session MTS-2026-10-03-1059Z-CLI-BLD-tf1-gate-fabio-v3 |
| 1.4 | TF2 | per-source live funnel report (alert to exit) | LANDED | - | CLOSED: scripts/dev/funnel_report.py + test_funnel_report.py (5 tests, fail-before = module missing), gate step 3f, --quick PASS; session MTS-2026-10-03-1314Z-CLI-BLD-tf2-per-source-live; spec was: new read-only scripts/dev/funnel_report.py over execution/auto_trades.jsonl, execution/trade_ledger.jsonl, runtime/alerts; daily table per source; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 2 L4 |
| 1.5 | TF3 | Fabio v3 live silence: diagnose + OF backfill | LANDED | - | CLOSED: cause = 2026-10-03 is a Saturday, ny_open_utc() is None so the v3 layer is silent by design (day_gates ny_open_utc; live_runner_cli.py fabio_v3_flow_window); volume_tier is NOT the cause (live passes no prior_vols, engine.py _tier returns "99", signals.py:277-284 never reached). Friday 10-02 had no OF bars (writer started 10-03 03:01Z): backfilled 09-29..10-02 (4x1440 bars, thr_days 30) via backtest/layers/fabio/of_backfill.py, state untouched; v3 engine on the 10-02 15:00Z window returns a verdict (91-bar window). 10-03 00:00-03:01Z not backfilled (live owns the day). Next live v3 window: Mon 2026-10-05 13:30Z. test_of_backfill.py 4 tests, fail-before = module missing + ownership-guard mutation; gate step added; session MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live |
| 1.6 | TF4 | execution provenance audit Tom + Fabio (read-only) | LANDED | - | CLOSED: MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md, 24 rows (E1-E9 Tom + Fabio, E10 per v2 extract); quote gate PASS (52 in the audit, 59 anchors in the 5 v2 extracts); parameter rows 1 SOURCED (Tom limit order type) / 6 CONCEPT-ONLY / 12 NO-SOURCE; findings: Tom limits 7 of 9 no_fill (zone price carries no Deribit basis, alert fires after the touch), time exit 40 min to 32 h by zone name, size 10 makes the 50/50 split impossible, 8 of 9 plans carry the NO-SOURCE 0.2 % stop, entry-before-proof 1 of 7 Tom entries (chain kept); TF5 order E1, E3, E2 (size 20 authority is Ruling 2, not Ruling 1); session MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven; spec was: Opus. Rows: entry order type, time exit, size, 50/50 runner, runner min distance, max_age_bars, BE rule, stop placement; quote + file:line or NO-SOURCE, testnet default FLAG per row; check entry-before-proof (EXTRACTION_ROUND2 A1) across the 5 Tom v2 extracts; output MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md E1-E5 |
| 1.7 | TF5 | Tom execution fixes from TF4 (fills, time exit, runner size) | QUEUED | 1.6 | staged .new in execution/ only, live-path tests (restart/reset, API error, fail closed), never restart or touch HALT/trades; supervisor promotes; testnet size 20 FLAG (Ruling 1); MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md E1-E3 |
| 1.8 | TF6 | Tom golden-scenario translation tests (L2) | QUEUED | 1.6 | new MyTradingSys/tests/test_tom_golden.py from 4MoNjEQ2Dd8 v2 + ANGLE_TRADE_CATALOG.md setups; failing scenarios listed in the report, not fixed here; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 2 L2 |
| 1.9 | TF7 | Fabio golden-scenario translation tests (L2) on v3 | QUEUED | 1.3 | new v3/tests/test_fabio_golden.py from FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md, FABIO_TRADE_MODEL.md (0jM5Y31YJak, 8CWKfoSJu3c); MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 2 L2 |
| 1.10 | TF8 | Fabio v3 historical backtest, pre-registered (L3) | QUEUED | 1.3 | write PRE_REG_FABIO_V3.md first (metric, threshold, stop rule, N = grid cells for DSR), then run v3 over F:/MTS/data/orderflow_1m walk-forward with backtest/fees.py; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 2 L3 |

## WAVE 2 - R4 FINISH

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 2.1 | R4-T1 | provenance read: K_BAL 0.8 / BAL_POC_BAND 0.25 / B_PROF 50 | LANDED | - | answered in FABIO_PROVENANCE_AUDIT_2026-10-01.md:59 (P02 k_bal 0.8 + POC band 0.25 = NS-fixed, CONCEPT-ONLY) and :98 (P41 B_prof bundle = SIM, DATA-PLUMBING); feeds R4-D |
| 2.2 | R4-T2 | false-vs-null collapse in failed_breakout | LANDED | - | failed_breakout returns None when no previous 4H balance (htf_context_live.py:87-90, :105); False kept for computed negative; 2 new tests + 1 updated in test_htf_context_live.py, all fail on pre-change code; session MTS-2026-10-03-1009Z-CL-BLD-r4t2-false-vs-null |
| 2.3 | R4-T3 | historical backtest of balance() parameters, OPERATOR-EXPERIMENT sweep | QUEUED | 1.2 | sweep ranges from operator |
| 2.4 | R4-D | parameter decision (accept / remove / replace-via-backtest) | BLOCKED | 2.1, 2.3 | operator |

## WAVE 3 - R5 / R6

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 3.1 | R5 | Model B failed-breakout shadow on 15m/4H | BLOCKED | 2.4 | shadow until n>=30 |
| 3.2 | R6 | canary as Windows scheduled task | LANDED | - | tasks 'MTS testnet canary' + 'MTS testnet status' Ready; scripts/dev/testnet_canary.py exists |

## WAVE 4 - ENGINE DEFECTS

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 4.1 | B070 | demote UTC 00:00 anchor + 0.75 slippage from gating | QUEUED | - | audit + demote |
| 4.2 | B076 | SETUP_CONFIRMED unreachable | QUEUED | - | trace verdict path |
| 4.3 | T052 | Tom-cited SETUP_CONFIRMED trigger | QUEUED | 4.2 | cite or reject |
| 4.4 | B059 | pf_vp bin-edge drift live verify | QUEUED | - | live tape confirm |
| 4.5 | T042 | OI/CVD peak reference still not emitted | QUEUED | - | add producer |
| 4.6 | B072 | L2 input validation for current_price | QUEUED | - | guard in build_math_object |
| 4.7 | B073 | net_rr rounding inconsistency | QUEUED | - | round-then-sanity |
| 4.8 | B074 | rule-order: contradiction cap before broken-value | QUEUED | - | reorder |
| 4.9 | B066 | rank-1 shown at trigger_ready 150 pts away | PARKED | premise gone | SetupCandidatesBuilder.java:75,:209 gate trigger_ready at distance_pct <= 0.1; BUGS close with receipt pending |
| 4.10 | B063 | divergence: restore in schema or deprecate | QUEUED | - | decide |
| 4.11 | T034 | positioning states (Net Longs/Shorts) | QUEUED | Rule 33 readers | design |
| 4.12 | T037 | test coverage gap 8 engine files | QUEUED | - | Build-Check Java step from -DskipTests compile to mvn -q test; promote 3 staged tests; no pom edit (junit-jupiter 5.10.2 and surefire 3.2.5 already declared) |
| 4.13 | T040 | tick-based delta layer | QUEUED | research gate | threshold source |
| 4.14 | T044 | hybrid REST/WS divergence alert | PARKED | premise gone | no hybrid run mode in Main or scripts; WONTFIX citing B045 pending |
| 4.15 | T046 | stage 3 pending decisions bundle | QUEUED | - | resolve 5 items |
| 4.16 | B069 | STATE_UPDATE_WARN exit=1 under wrapper | QUEUED | - | wrapper exit handling |

## WAVE 5 - EXECUTION

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 5.1 | T050 | Deribit execution layer, phases 3+ | QUEUED | - | order placement testnet |
| 5.2 | B077 | stop order wrong type | LANDED | - | BUGS CLOSED, 5e387a1; deribit_orders.py stop_market, executor.py places the stop through it |
| 5.3 | B078 | cancel_all_by_label overscope | LANDED | - | BUGS CLOSED, 5e387a1; cancel_by_label is label-scoped server-side |
| 5.4 | B079 | caps_check not enforced | LANDED | - | BUGS CLOSED, 5e387a1 + b05c1cf; executor.py refuses on within_max_loss False and above max_notional |
| 5.5 | T048 | satellite framework | BLOCKED | T050 ph4 | design doc |
| 5.6 | T051 | backtest MTS raw verdict | BLOCKED | T050 ph4 | parked |

## WAVE 6 - RESEARCH / MAINTENANCE

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 6.1 | T053 | two-account hedge / scalping | QUEUED | - | research |
| 6.2 | T054 | US session / pre-market / news | QUEUED | - | research |
| 6.3 | T055 | positioning + proven setups | QUEUED | - | research |
| 6.4 | T056 | audit program (Qwen decommissioned) | PARKED | premise gone | Qwen decommissioned 2026-10-01 (T049, B082 CLOSED on that fact); WONTFIX pending |
| 6.5 | T057 | simplify / declutter | QUEUED | - | DEV_VELOCITY_AUDIT follow-up |
| 6.6 | T058 | broken extremes: sweep vs continuation | QUEUED | - | research |
| 6.7 | T060 | low-volatility anomaly BTC | QUEUED | - | T3 evidence, backtest decides |
| 6.8 | T061 | WaveTrend LazyBear layer | QUEUED | - | integrate as layer |
| 6.9 | T059 | SESSION_PASTE size guard | QUEUED | - | one 150 KB threshold, split at a section boundary (start-session.ps1:314-317 warns at 80 KB only) |
| 6.10 | B083 | prompt_check.ps1 advisory gate | GATED | operator runs test_prompt_check.ps1 | scripts/dev/prompt_check.ps1 + test_prompt_check.ps1 written 2026-10-03; registry stays OPEN until the test run is reported |
| 6.11 | - | cicd_run.py end-to-end CI/CD runner | GATED | operator runs test_cicd_run.py | scripts/dev/cicd_run.py, system/critical_files.json, tests/test_cicd_run.py written 2026-10-03; design in research/CICD_PIPELINE_2026-10-03.md |

## WAVE 7 - TOM ENGINE RE-RUN

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 7.1 | R7 | Tom BT re-run on D1 target rule | QUEUED | 4.1, 4.6, 4.7, 1.7 | write PRE_REG_R7.md first; regenerate the row cache with the R1 target rule and TF5 execution; old-vs-new R distribution; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 2 L3 |

## WAVE 8 - OTHER LAYERS

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 8.1 | LY1 | layer provenance audit, all non-core families (read-only) | QUEUED | - | Opus. rsi, cryptocred, positioning, session, turn_of_candle, tick, consensus: every parameter -> trader quote + file:line or NO-SOURCE; output MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 4 |
| 8.2 | LY2 | staged .new sweep (11 files, 25-123 h) | QUEUED | - | per file: gate and promote, or archive with scripts/dev/declutter_backups.py; list in MyTradingSys/research/STATUS.md In-Flight |
| 8.3 | LY3 | turn_of_candle: trade or alert-only decision | QUEUED | 1.4 | 58 testnet trades gross +0.017 USD net -0.56; default FLAG alert-only via staged execution/auto_trader_config.json.new, supervisor promotes; MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md section 4 |
| 8.4 | LY4 | one pre-registered historical driver for all layers | QUEUED | 8.1 | generalise run_backtest.py pattern; drivers from MyTradingSys/research/fast_track_2026-09-27/DSA_BACKLOG.md (malkan_40_60, malkan_mtf, rsi_ma_events); PRE_REG per layer |
| 8.5 | LY5 | finish rsi observation + consensus writer (staged) | QUEUED | 8.2 | MyTradingSys/backtest/layers/rsi/observation.py.new, MyTradingSys/backtest/layers/consensus/writer.py.new and their tests |


## WAVE 9 - CLOUD CREDIT / APPROVAL

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 9.1 | B090 | cloud credit approval plan (two buckets) | QUEUED | - | Claude approves; operator runs Bucket A today (C1, C8, C4, C7); Bucket B contingent on one desktop step each. See MyTradingSys/items/B090_cloud_credit_approval.md |
# END
