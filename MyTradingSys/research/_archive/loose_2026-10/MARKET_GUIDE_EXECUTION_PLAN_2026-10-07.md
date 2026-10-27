# MARKET GUIDE: end-to-end execution plan (2026-10-07)

Status: EXECUTED 2026-10-07 after revalidation (scope cut: no new live layers) - see MARKET_GUIDE_RESULTS_2026-10-07.md. Written from disk state of 2026-10-07 (live_alert_state.json, runtime/alerts/*.jsonl,
AUDIT_CLOSEOUT_2026-10-07.md, candle_patterns_2026-10-04/, BTC_MA_SETUPS_RESEARCH_2026-10-03.md, live_layers.py, live_runner_cli.py).

## 0. Operator requests (verbatim sources)
- 2026-10-07 (this session): "each layer was built to provide trade setups and signals - I need to know if we draw from these signals like a guide on what is
  happening in the market? It could be useful for user like MA cross - rsi set up building - candle stick pattern forming ... are these layers firing? do we have
  any setups or valuable signals we draw?"
- 2026-10-03 (MA): "What trading setups are there for BTC using the moving averages. Maybe secret moving averages that are back-tested and works under certain
  market condition like trending/ranging. There could be other diverse factors and we have to research what they could be!"
- 2026-10-03 (candles): assess "long ... when price goes up past [the previous daily open], exit when current daily breaks previous day close on a closing basis";
  survey which candle signals are worth testing on BTC.
- 2026-10-05 (OPERATOR_ASKS section 0, ask 5): "How can we improve our alerts?" (T067); ask 4 "My charts" (T066); LazyBear/WaveTrend (T061, T065).

## 1. What exists today (verified on disk)
- Firing: ~720 alerts in runtime/alerts/{1m,5m,15m,1h}.jsonl, updated 2026-10-07. By layer: turn_of_candle 408 (timer, sampling only), rsi ~190 (40-level
  cross/support/failure/rejection, Malkan), cryptocred ~20 (sr_flip, fib_pullback), fabio ~25 (cvd_absorption, escalation, volume_fvg; 96 v3_grid shadow rows),
  positioning 3, session 3.
- Gap 1: nothing turns these into a readable "what is happening now" view. Consumers today are auto_trader (needs a side) and raw jsonl.
- Gap 2: RSI emits events at the level, not "setup building" states (approaching 40/60, RSI vs its MA, slope).
- Gap 3: no MA layer (cross, price vs MA, slope/regime). Research stopped at section 4 (feasibility); sections 3/5/6 empty; worker files Q1/Q2/Q3Q4 never written.
- Gap 4: no candle layer. Pilot built and tested (29 tests, 10/10 mutations caught, 40/40 citations) but run_p0 results, run_p1 and the report were never produced.
- Edge evidence: T055 C1 funding_cvd_fade FAIL (OOS -0.0453%), C2 session_momentum FAIL (Sharpe 0.0084), CryptoCred fill-bias reruns all FAIL, Tom rule 19
  signals -> 0 unexplained, toc_m14 no gross edge. RSI and fabio have no verdict found. So current signals are CONTEXT, not proven entries.

## 2. Design principle
Two classes, kept apart so a context view never becomes a hidden trade rule:
- OBSERVATION layers (alert-only, no side, never mapped in auto_trader, never a Tom filter): describe state. Definitions are canonical textbook formulas with a
  FORMULAS.md section (definition + source + worked example), flagged `observation`.
- TRADE layers: need own-words provenance (CLAUDE.md) and pass the BACKTEST_PROTOCOL gate (T055 template: 70/30, PBO < 0.5, n_oos >= 30, Sharpe >= 0.3,
  >= 2 OOS years, net of 14 bps + funding). Until then they stay observation.
Guide output is read-only context; it never changes routing, sizing or HALT.

## 3. Phases

### P0 Preconditions (T0, scripts; no live-tree edit)
1. Claim `layers/alerts/` in SUPERVISOR_LOG (one owner). All edits staged as `<file>.new`; promote only per CLAUDE.md (backup .pre_<tag>, rename, re-gate, commit).
   Builder briefs repeat: never stop/restart auto_trader, position_manager, daily_loss_monitor, live_runner_cli; no HALT files; no trades.
2. Fix B103 (funding_paid silent 0 outside loaded range, fail closed) and fetch fundingRate 2020-01..2026-09 with fetch_binance_archive.py. Blocks any net-of-funding backtest.
3. Operator decisions needed (ask once): (a) pre-2017 BTC data source for 200W/Pi Cycle, or drop those; (b) whose MA/candle methodology counts as "sourced"
   for trade promotion (literature T1/T2 vs a trader's words); (c) the open B128 questions that touch these layers.

### P1 Finish the stalled research (cheapest tier; no new infra)
1. Candles: run `pilot/run_p0.py` (DEV only, minutes), then write `run_p1.py` per PRE_REG section 4 (18 patterns x h in {1,3,5}, block bootstrap, BH). T2 Sonnet
   writes it; tests derived from the pre-reg. Write CANDLE_PATTERNS_RESEARCH_2026-10-04.md. VALIDATION/HOLDOUT stay sealed; VALIDATION is run once per frozen set.
   Output: verdict on the operator daily-open rule (P0a/c/s/e) and a per-pattern table.
2. MAs: re-run the three briefs in btc_ma_2026-10-03/WORKER_BRIEFS.md (T1 Sonnet web workers; playbook Part I; every citation opened; REJECT if unopenable).
   Spot-check one citation per file. Fill sections 3, 5, 6.
3. Add the missing verdicts for existing layers using the same gate: rsi_events (40 level), fabio cvd_absorption/escalation/volume_fvg, cryptocred sr_flip.
   Output: one table "layer | verdict | n_oos | net Sharpe" in STATUS.md. This answers "which signals are valuable" with numbers.
Exit: three research docs committed, each with tagged findings and an explicit REJECT list.

### P2 Build OBSERVATION layers (T2 Sonnet implements; tests from FORMULAS, fail-first)
Each layer: pure function bars -> events (same interface as rsi_level_layer in live_layers.py), tf-agnostic, registered via build_default_registry entries
({layer, sub, tf, fn, params_id}). Add the new layer family to every TF/family map (alert_rate_check, account routing, audits) per CLAUDE.md, with an explicit
"no auto_trader mapping" test.
- ma layer (backtest/layers/ma/): SMA/EMA via existing rsi_ma.py (FORMULAS sec 2-5). Events: price-vs-MA cross, MA-MA cross, MA slope state. Periods taken from P1
  findings only (candidates from feasibility table: 1d SMA20/50 testable, 1h/4h EMA9x21 and close x SMA200 testable; 50x200 and Pi Cycle not testable as events).
  Regime label (efficiency ratio / ADX / Fabio `balance`) computed ex-ante per bar.
- candles layer (backtest/layers/candles/): promote pilot/candles.py patterns that survive P1 triage; plus "forming" state = current open bar partial pattern is NOT
  emitted (closed bars only, matches CONFIRM_LAG logic) so "forming" means setup conditions met on bar i-1.
- rsi_setup layer: reuse rsi_core + rsi_ma. Emits state events: RSI within X of 40/60, RSI vs RSI-MA, Malkan 40/60 regime. Thresholds only from Malkan/
  rsi TEST_PLAN sources (provenance), else NO-SOURCE flagged.
Tests must cover: restart/reset of state, duplicate-emit suppression (emitted keys), API/feed errors fail closed, closed-bar-only.

### P3 Market guide (the user-facing answer)
1. `scripts/dev/market_guide.py` (T0/T2): reads runtime/alerts/*.jsonl + live_alert_state.json + current_market_state.md, outputs a short per-timeframe table:
   RSI state, MA state (price vs MA, cross age), last candle pattern, nearest S/R flip, absorption bias, funding fade, plus age of each signal. toc_m14 excluded.
   Each row shows its P1 verdict tag (EDGE / NO-EDGE / UNTESTED) so context is never confused with a recommendation.
2. Write to runtime/market_guide.md each poll cycle (atomic write) and surface through DSA_SESSION_PROMPT chat surface and the mts launcher status line.
3. Staleness guard: a row older than 2 bars of its tf is greyed; a stopped feed shows FEED STALE (ties to watchdog item G2).

### P4 Validate and promote
1. Offline: `python scripts/dev/run_all_tests.py` (full), plus new-tests-fail-on-old-code evidence.
2. Shadow period on testnet feed: layers run alert-only for >= 7 days; alert_rate_check bounds rate; compare event counts to backtest expectation.
3. Promotion to TRADE layer only per section 2 gate; otherwise stays observation. Supervisor (not builder) restarts runner after fix is committed and gated.

### P5 Related backlog to fold in (do not duplicate)
T067 alert improvements (B136 OI feed fix first; T063 stop-run + OI flush signature), T064 TF confirmation, T061/T065 WaveTrend (LazyBear) as another
observation candidate, T066 My charts (read operator's TradingView ideas via Claude in Chrome) as a human-sourced signal input.

## 4. Routing and cost
T0: fetch, B103 check, market_guide.py reader, tests runner. T1 Haiku: file/stat scans. T2 Sonnet: layer code, run_p1, tests, web workers. T3 Opus: only the
plan review and verdict write-ups. One background shell waits on runs; no polling agents.

## 5. Order and exits
P0 -> P1 (1, 2, 3 in parallel) -> P2 (per surviving signal) -> P3 -> P4. P3 can ship a first version early using only existing layers (RSI, cryptocred, fabio),
which answers the immediate question before MA/candle work lands. Suggested first deliverable: P3 v1 + P1.3 verdict table.

## 6. Risks
- Pattern/MA data snooping: mitigated by pre-reg, block bootstrap, BH, PBO, sealed holdout.
- Literature is mostly negative for candlesticks (DJIA, Tokyo, DAX/Bund no value; BTC only engulfing, in-sample optimised): expect few survivors.
- Few events for long MAs (50x200: 12 events): position-series evaluator needed (layers/ma/position_backtest.py), else UNTESTABLE.
- Live-tree edits break running processes: staged .new only.
- Provenance: any parameter without a transcript/literature source is NO-SOURCE and removed, never tuned.
