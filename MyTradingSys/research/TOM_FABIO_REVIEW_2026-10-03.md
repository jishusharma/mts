# TOM + FABIO: 7-DAY REVIEW, TEST PLAN, LAYER PLAN, CI/CD ROWS - 2026-10-03

Session: MTS-2026-10-03-1035Z-CL-SUP-tf-review (CL desktop, Opus 5.5, branch fast-track). Read-only on code; writes this
file, BUILD_PIPELINE.md rows (wave 1 TF*, wave 8 LY*), 03_FILE_INDEX row, session record.
Window: 2026-09-26 .. 2026-10-03 (387 commits). Every number below was read from disk this session; source in brackets.

## 0. ONE-PARAGRAPH ANSWER

The extraction side is done enough: two extraction methods (v1, v2 line-by-line), two provenance audits and a kappa
check all say the same thing: Tom and Fabio give concepts, almost never numbers (Tom 2 of 74 engine parameters
SOURCED; Fabio v3 0 of 8 numeric parameters SOURCED). More re-extraction will not find numbers that are not in the
transcripts. The translation into trades is NOT done: since the R1/R2 fixes (2026-10-02 20:04Z) Tom produced 25 alerts,
6 trade attempts, 5 limit orders that never filled and 1 fill that a time exit closed after 40 minutes; Fabio v3 has
produced 0 live rows. Trades now die in the execution translation (entry type, time exit, contract size), which no
audit covered. Next: stop re-extracting; test the translation directly (golden scenarios from the line-by-line
extracts), fix the execution defects on testnet, run pre-registered historical tests, and let the CI/CD queue carry it.

## 1. WHERE WE STAND - THE 7 DAYS

| Date | What happened | Result |
|---|---|---|
| 09-28..09-29 | Fabio extracts (10 videos), kline-proxy detectors (escalation, cvd_absorption, volume_fvg) | FABIO_L1: no edge [backtest/layers/fabio/FABIO_L1_REPORT.md] |
| 09-30 | Fabio order-flow model on 120 d aggTrades; Tom core historical BT; line-by-line method v2 (Opus) on 4MoNjEQ2Dd8 + fZlNGWvd2Ko; trade catalog | OF model 0/64 variants net-positive OOS, median gross +0.13R, fee drag 0.66R [SUPERVISOR_LOG 09-30 03:30]. Tom BT 19 SETUP_FORMING in 57 months, all short. Catalog: Tom 21 / Fabio 9 trades taken, 0 on BTC, no dates [ANGLE_TRADE_CATALOG.md s1] |
| 09-30 | Provenance hard rule (operator); Tom provenance audit | 74 rows: 2 SOURCED, 33 CONCEPT-ONLY, 36 NO-SOURCE, 3 PLUMBING [PROVENANCE_AUDIT_TOM.md] |
| 10-01 | Revalidation W1-W8, extraction round 2 (5 Tom v2 extracts), Fabio provenance audit, second-reader kappa | Kappa 0.446 (< 0.6): the NO-SOURCE count is reader-dependent; both readers agree on 22 NO-SOURCE rows [W3_KAPPA_REPORT s3]. Fabio 41 rows: SOURCED 14 (labels) / 7 (strict), NO-SOURCE 7 [FABIO_PROVENANCE_AUDIT] |
| 10-02 | Fabio v3 engine promoted (shadow); v3 sourcing; Tom all-shorts diagnosis; direction review | v3 numeric params 0/8 SOURCE, 8/8 SHADOW [FABIO_V3_SOURCING]. 214 of 301 Tom BT losses = `net_rr < 2.0` [TOM_BT_SHORT_DIAGNOSIS s2]. Stack had been down 09-29..10-02 |
| 10-03 | Rulings 1-2 (rip out 2.0 floor, apply defaults); R1 target rule, R2 runner exit, R3 live OF bars, R4 HTF context; CI/CD pipeline + dispatcher | Floor now 1.25 (testnet); target = nearest POC/HVN [WHY_ENGINE_SILENT s3]; queue live |

### 1.1 Live testnet since R1/R2 (2026-10-02 20:04Z .. 2026-10-03 10:56Z) [execution/auto_trades.jsonl, trade_ledger.jsonl]

| Source | Alerts | Rejected by verdict | Attempts | No fill | Filled | Result |
|---|---|---|---|---|---|---|
| Tom (#84-#108) | 25 (23 consumed) | 16: WAIT_PROOF 9, WAIT_TRIGGER 6, WATCH 1 | 6 | 5 (all `L-lim`/`S-lim` limit entries) | 1: S-lim-1003-0635 short @84650.5 | time_exit after 40.0 min, net -0.0048 USD |
| Fabio v3 (shadow) | 0 rows in runtime/alerts/*.jsonl | - | - | - | - | OF bars ARE written (473 rows on 10-03) |
| Fabio L1 escalation (kline proxy, not v3) | - | - | 1 | 0 | 1 | time_exit 120 min, net -0.0107 USD |

R2 runner never ran: every Tom attempt logged `runner_skipped` = "size 10 too small for a 50/50 split" (3) or "no
RUNNER_TARGET" (2). Size 10 USD is the Deribit minimum contract, so a 50/50 split cannot exist at that size.
Lifetime Tom testnet trades: 1. Lifetime Fabio-model trades: 0.

### 1.2 Why the trades die (ranked)

| # | Defect | Evidence | Audited for provenance? |
|---|---|---|---|
| E1 | Tom entries are limit orders that do not fill | 5 of 6 attempts `no_fill` | No |
| E2 | Time exit (tom.max_hold_bars 8 x zone TF) closes before target | the one fill: 40 min, exit_reason time_exit | No (not in PROVENANCE_AUDIT_TOM) |
| E3 | Runner dead at size 10 | runner_skipped on every attempt | No (50/50 split flagged NO-SOURCE testnet default) |
| E4 | SETUP_CONFIRMED unreachable; most alerts stop at WAIT_PROOF/WAIT_TRIGGER | B076; 15 of 16 rejections | Partly (T052: no Tom-cited trigger) |
| E5 | Order of operations may be reversed: v2 line-by-line of 4MoNjEQ2Dd8 has entry BEFORE the absorption proof; our chain demands proof first | EXTRACTION_ROUND2 s5.1 row A1 | One video only - verify across the other v2 extracts before any code change |
| E6 | Fabio v3 silent live: cause not established. Candidates: volume_tier needs 10 prior days (v3/signals.py:277-284, else "99"); historical OF files end 2026-09-28, live writer started 10-03 | 0 v3 rows | n/a |
| E7 | Fabio v3 tests (119, pass) are not in run_all_tests.py, so the gate does not protect v3 | grep v3 in scripts/dev/run_all_tests.py: 0 hits; pytest run this session 119 passed | n/a |
| E8 | Tom live-path defects still open: B072 fail-open current_price, B073 rounded net_rr gates, B070 0.75 slippage factor (NO-SOURCE) | WORK_REVIEW s1.4 | B070 yes |

The audits covered the engine decision parameters. E1-E3 sit in execution and were never audited; that is where the
signal-to-trade translation fails today.

## 2. TEST PLAN FOR THE FINAL DELIVERABLES (Tom core, Fabio core)

Four levels. Each level answers a different question; none substitutes for another.

| Level | Question | Tom | Fabio | Pass |
|---|---|---|---|---|
| L1 Rule conformance | Does each coded rule do what its quote says? | every TOM-NNN decision point has a test citing the quote (check_rule_ids.py exists) | every P01-P41 row with a quote has a test | 100 % of SOURCED + CONCEPT-ONLY rows have a test; gate runs them |
| L2 Golden scenario (translation test) | Given the situation the trader describes, does the code take HIS trade? | fixtures from 4MoNjEQ2Dd8 v2 + the 4 named setups in ANGLE_TRADE_CATALOG s1(c): B-setup pullback after failed push into no-liquidity high; P-profile exhaustion short; limit sell below last volume step; buying-tail pullback long | fixtures from fZlNGWvd2Ko, 0jM5Y31YJak, 8CWKfoSJu3c line-by-line: balance + hidden CVD pressure -> break with big trades -> BE -> add -> exit on exhaustion | each scenario asserts side, entry timing, stop side of the extreme, target node, management steps. A FAILING scenario is a translation gap, reported, not hidden |
| L3 Historical, pre-registered | Does the translated rule make money on BTC after fees? | R7 on regenerated cache with R1 target rule + E1-E3 fixes | v3 engine over F:\MTS\data\orderflow_1m (2025-01..2026-09-28); grid cells = declared trials | PRE_REG file written before the run (metric, threshold, stop rule); DSR with N = declared cells; walk-forward OOS; maker/taker fees from backtest/fees.py |
| L4 Testnet funnel | Does the live path turn alerts into trades as designed? | alert -> verdict -> attempt -> fill -> exit, per source, daily | same, v3 shadow rows -> (later) orders | funnel report daily; n >= 30 filled per core before any edge claim |

Limits stated up front: (a) no trader BTC trade has a date, so L2 fixtures are our reconstruction of the described
situation, in normalised units; they test translation fidelity, not edge. (b) L3 on BTC tests whether the trader's
idea transfers to BTC; a fail there does not mean the extraction was wrong.

### 2.1 The one operator decision this plan needs

Concept-only parameters (the trader names the idea, never the number) are 33 of 74 Tom rows and 26 of 41 Fabio rows
(strict). Code cannot detect "balance" without a number. The 2026-10-03 directive authorises measuring a value and
OPERATOR-EXPERIMENT values; CLAUDE.md says "never tune" a NO-SOURCE value. Plan default [FLAG]: for CONCEPT-ONLY rows,
the number may come from a pre-registered historical measurement, labelled MEASURED (testnet only, never mainnet);
NO-SOURCE rows (no idea behind them) are removed or shadowed, never measured. Override in OPERATOR_RULINGS Ruling 3.

## 3. CI/CD ROWS ADDED (BUILD_PIPELINE.md, wave 1 = picked before waves 2-7)

| Row | Id | Work | Model | Blocker |
|---|---|---|---|---|
| 1.3 | TF1 | Gate: add Fabio v3 tests, test_orderflow_live, test_htf_context_live to run_all_tests.py (E7) | Sonnet | - |
| 1.4 | TF2 | scripts/dev/funnel_report.py: per-source funnel from auto_trades.jsonl + trade_ledger.jsonl + runtime/alerts (read-only, L4) | Sonnet | - |
| 1.5 | TF3 | Fabio v3 live silence: diagnose E6; backfill OF bars 2026-09-28..live start from Binance aggTrades history (collection-only, writes runtime/orderflow_live only) | Sonnet | - |
| 1.6 | TF4 | Execution provenance audit, Tom + Fabio: entry order type, time exit, size, 50/50 runner, runner min distance 0.25 %, max_age_bars, BE rule, stop placement. Quote + file:line per row; testnet default [FLAG] per row. Also checks E5 across the 5 Tom v2 extracts | Opus | - |
| 1.7 | TF5 | Tom execution fixes from TF4 (E1-E3), staged .new in execution/, live-path tests (restart/reset, API error, fail closed); testnet size 20 so the runner can split [FLAG, Ruling 1]. Supervisor promotes + restarts | Sonnet | 1.6 |
| 1.8 | TF6 | Tom golden-scenario tests (L2), tests/test_tom_golden.py; failing scenarios listed, not fixed in this row | Sonnet (Opus writes the scenario table) | 1.6 |
| 1.9 | TF7 | Fabio golden-scenario tests (L2) on v3 engine with OF-bar fixtures | Sonnet | 1.3 |
| 1.10 | TF8 | PRE_REG_FABIO_V3.md, then v3 historical backtest (L3) | Sonnet | 1.3 |
| 7.1 | R7 | Tom BT re-run (L3), now QUEUED behind B070/B072/B073 instead of "Wave 4" | Sonnet | 4.1, 4.6, 4.7 |

Wave 8 (other layers, section 4) is queued after wave 7.

## 4. ALL OTHER LAYERS - WHAT REMAINS

Layer families on disk: rsi (Malkan), cryptocred, positioning, session, turn_of_candle, tick, consensus, timeframe,
plus T061 WaveTrend (not built). None has a provenance audit like Tom's; every parameter needs its trader's words
(CLAUDE.md Provenance).

| Layer | Live state | Evidence | Remaining |
|---|---|---|---|
| turn_of_candle 1m | trading, jishu_1 | 58 trades: gross +0.017 USD (30 gross winners), net -0.56 USD; C3 backtest already said no edge at 1-5 bars | decide: back to alert-only [FLAG default] - fees eat a gross ~0 effect; n is enough |
| rsi_events 5m/15m/1h (Malkan) | trading | 15m: 4 trades, 3 net winners, +0.90 USD; 5m, 1h: 1 each | provenance audit; historical driver (DSA_BACKLOG malkan_40_60, malkan_mtf, rsi_ma); rsi/observation.py.new staged 26 h |
| cryptocred (failed_msb, fib_pullback, sr_flip) | alerts, 1 skipped_busy | test_cc_retest.py.new + test_cc_structure.py.new staged 123 h | provenance; finish staged tests; classify_msb filter flag (WORK_REVIEW fix-next) |
| positioning funding_cvd_fade | wired 1h | 0 trades seen in window | provenance + historical test |
| session_momentum 15m | trading | 1 trade, net -0.0025 | provenance + historical test |
| fabio L1 (escalation, cvd_absorption, volume_fvg) | trading jishu_3 | kline proxies; FABIO_L1 no edge | retire once v3 emits (v3 is the Fabio model) [FLAG] |
| tick (T040) | not wired by decision | tiers.json 0.11 flags/day | park until R3 OF data is 30 days deep |
| consensus | not built | writer.py.new + test_writer.py.new staged 26 h | finish or archive |
| WaveTrend (T061) | not built | pipeline 6.8 | source (LazyBear script) + layer + test |
| staged .new sweep | 11 files 25-123 h old | STATUS.md In-Flight | promote with gate or archive via declutter_backups.py |

Rows queued (wave 8): LY1 layer provenance audit (all families, one table), LY2 staged .new sweep, LY3 turn_of_candle
decision, LY4 one historical driver for all layers with pre-registration, LY5 rsi observation + consensus finish.

## 5. SESSION PLAN (each line = one `mts go` session; the dispatcher writes the prompt)

| # | Session slug | Rows | Model | Gate |
|---|---|---|---|---|
| 1 | b070-* (already PICKED, held) | 4.1 | Sonnet | --quick |
| 2 | tf1-gate-fabio | 1.3 | Sonnet | --quick |
| 3 | tf2-funnel | 1.4 | Sonnet | --quick |
| 4 | tf3-v3-silence | 1.5 | Sonnet | --quick + v3 rows appear or cause named |
| 5 | tf4-exec-prov | 1.6 | Opus | quotes verified (verify_extract_quotes.py) |
| 6 | tf5-tom-exec | 1.7 | Sonnet + supervisor promote | full gate + live-path tests |
| 7 | tf6-tom-golden / tf7-fabio-golden | 1.8, 1.9 | Sonnet | tests run; failing list in report |
| 8 | tf8-v3-hist | 1.10 | Sonnet | PRE_REG committed before run |
| 9 | b072-b073 bundle, b076 | 4.6, 4.7, 4.2 | Sonnet | full gate |
| 10 | r7-tom-bt | 7.1 | Sonnet | PRE_REG + old vs new R table |
| 11-15 | ly1..ly5 | 8.1-8.5 | Opus (LY1), Sonnet | per row |

## 6. CI/CD: WHAT IS AUTOMATIC TODAY AND WHAT IS NOT

- Automatic: task `MTS-Scheduler-Tick` runs tick.py every 15 min -> pick_task.py writes runtime/queue/next_task.txt.
  Queue head is B070, PICKed at 10:14, 10:29, 10:44Z and HELD (one writer, 6 h cooldown) [runtime/queue/pick_log.jsonl].
- Manual: launch. `mts go` (scripts/sched/go.py) starts an interactive `claude` session; nothing runs it unattended.
  B070 has waited about an hour with no session. Iteration speed today = how often the operator types `mts go`.
- To make it iterate without the operator: a scheduled task that runs go.py headless when a PICK is fresh and no
  session record is open. That is persistent config that spends tokens unattended, so it needs an operator yes; it
  also needs go.py to support a headless mode (claude -p) with a token budget per run. Not done in this session.

# END
