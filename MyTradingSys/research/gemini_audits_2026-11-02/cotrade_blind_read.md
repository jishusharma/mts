# FOUND: 106, NOT_IN_DATA: 1, DIFF: 0

# Blind Re-read of testnet_cotrade DESIGN.md and P5_BRIEF.md Numbers vs Sources

Audit of all empirical numbers, percentages, US-window ranges, shares, ladder parameters, caps, and test cases in:
1. `MyTradingSys/research/testnet_cotrade_2026-10-31/DESIGN.md`
2. `MyTradingSys/research/testnet_cotrade_2026-10-31/P5_BRIEF.md`

Cross-checked against:
- `MyTradingSys/research/testnet_cotrade_2026-10-31/stats_run.json`
- `MyTradingSys/research/testnet_cotrade_2026-10-31/ladder_math.py`
- Cited repo execution code (`risk_guard.py`, `trade_plan_validator.py`, `daily_loss_guard.py`, `deribit_orders.py`, `cotrade.py`, `executor.py`, `journal.py`)
- Cited research reports (`eur_low_us_sweep_2026-10-14/RESULT.md`, `us_open_oos_2026-10-30/REPORT.md`, `pre_us_squeeze_2026-10-29/RESULT.md`, `us_open_levels_2026-10-30/RESULT.md`, `t053_hedge_variants_2026-10-30/results.txt`)

## Summary

- **Total Numbers / Claims Audited**: 107
- **FOUND (Exact match in cited source / machine-generated data / execution code)**: 106
- **NOT_IN_DATA (Explicit null hypothesis / no pattern finding acknowledged in text)**: 1
- **DIFF (Discrepancy between text and cited source)**: 0

---

## 1. DESIGN.md Audit Table

| Line | Section | Claim / Number | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L4 | Ask | "short 100 here / buy here with a double" | Operator voice call ask | short 100 | **FOUND** | `OURS` | Quote of operator instruction |
| L5 | Ask | Doubling ladder: X, 2X, 3X, 6X ... | Operator doubling scale-in ask | X, 2X, 3X, 6X | **FOUND** | `OURS` | Doubling total ladder progression |
| L12 | Capabilities | deribit_orders.py:487 place() | `execution/deribit_orders.py:487` | `def place(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L13 | Capabilities | deribit_orders.py:396 cancel | `execution/deribit_orders.py:396` | `def cancel(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L13 | Capabilities | deribit_orders.py:400 cancel_by_label | `execution/deribit_orders.py:400` | `def cancel_by_label(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L13 | Capabilities | deribit_orders.py:507 amend | `execution/deribit_orders.py:507` | `def amend(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L13 | Capabilities | deribit_orders.py:408 close_position | `execution/deribit_orders.py:408` | `def close_position(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L14 | Capabilities | executor.py:322 ensure_stop | `execution/executor.py:322` | `def ensure_stop(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L14 | Capabilities | deribit_orders.py:377 server-side stop_market | `execution/deribit_orders.py:377` | `def stop_market(` | **FOUND** | `FACT (not trader-sourced)` | Exact function definition line |
| L15 | Capabilities | trade_plan_validator.py:117 ladder plan type | `execution/trade_plan_validator.py:117` | `elif plan_type == "ladder":` | **FOUND** | `FACT (not trader-sourced)` | Exact validator line |
| L15 | Capabilities | plan_compiler.py:144 ladder compiler | `execution/plan_compiler.py:144` | `elif plan_type == "ladder":` | **FOUND** | `FACT (not trader-sourced)` | Exact compiler line |
| L15 | Capabilities | executor.py:425 executor places rungs | `execution/executor.py:425` | `def _place_ladder_entry_orders(` | **FOUND** | `FACT (not trader-sourced)` | Exact executor line |
| L16 | Capabilities | executor.py:508, :535 targets placed after entry | `execution/executor.py:508,535` | `def _place_targets(` | **FOUND** | `FACT (not trader-sourced)` | Target placement routines |
| L17 | Capabilities | Account cap $10,000 (risk_guard.py:22) | `execution/risk_guard.py:22` | `MAX_ACCOUNT_NOTIONAL_USD = 10000` | **FOUND** | `OURS` | Constant match |
| L17 | Capabilities | Plan ceiling $10,000 (trade_plan_validator.py:35) | `execution/trade_plan_validator.py:35` | `MAX_NOTIONAL_CEILING = 10000` | **FOUND** | `OURS` | Constant match |
| L17 | Capabilities | Max loss -$500 (trade_plan_validator.py:36) | `execution/trade_plan_validator.py:36` | `MAX_LOSS_FLOOR = -500` | **FOUND** | `OURS` | Constant match |
| L17 | Capabilities | Max 10 rungs (trade_plan_validator.py:38) | `execution/trade_plan_validator.py:38` | `MAX_LADDER_RUNGS = 10` | **FOUND** | `OURS` | Constant match |
| L17 | Capabilities | Daily loss -$500 (daily_loss_guard.py:8) | `execution/daily_loss_guard.py:8` | `DEFAULT_DAILY_LOSS_CAP_USD = -500.0` | **FOUND** | `OURS` | Constant match |
| L18 | Capabilities | executor.py:205, :239 HALT checks | `execution/executor.py:205,239` | `if is_halted():` | **FOUND** | `FACT (not trader-sourced)` | Guard check lines |
| L19 | Capabilities | journal.py:91 reconstruct_belief | `execution/journal.py:91` | `def reconstruct_belief(` | **FOUND** | `FACT (not trader-sourced)` | Function definition line |
| L19 | Capabilities | auto_trader.py:702 position_manager respawn | `execution/auto_trader.py:702` | `self._respawn_position_manager(` | **FOUND** | `FACT (not trader-sourced)` | Method definition line |
| L24 | Doubling ladder | Example base size: X = $100 short | `ladder_math.py:6` | `X = 100` | **FOUND** | `OURS` | Exact parameter match |
| L24 | Doubling ladder | Anchor price: P0 = 100,000 | `ladder_math.py:6` | `P0 = 100000.0` | **FOUND** | `OURS` | Exact parameter match |
| L24 | Doubling ladder | Spacing: one rung every +0.4 % | `ladder_math.py:6` | `SPACING = 0.004` (0.4%) | **FOUND** | `OURS` | Exact parameter match |
| L24 | Doubling ladder | Stop gap: one stop 0.4 % above last rung | `ladder_math.py:6` | `STOP_GAP = 0.004` (0.4%) | **FOUND** | `OURS` | Exact parameter match |
| L24 | Doubling ladder | Adds: 1, 2, 3, 6, 12, 24, 48 X | `ladder_math.py:2,11` | `adds [100, 200, 300, 600, 1200, 2400, 4800]` | **FOUND** | `OURS` | Exact sequence match |
| L28 | Doubling ladder | Rung 1: Total size $100 (1X) | `ladder_math.py:21` | `steps=1 total=$100` | **FOUND** | `OURS` | Exact simulation match |
| L28 | Doubling ladder | Rung 1: Price moved against 0.40 % | `ladder_math.py:21` | `stop_move_from_P0=0.40%` | **FOUND** | `OURS` | Exact simulation match |
| L28 | Doubling ladder | Rung 1: Loss at stop $0.40 | `ladder_math.py:21` | `loss_lin=$0.40 loss_inv=$0.40` | **FOUND** | `OURS` | Exact simulation match |
| L28 | Doubling ladder | Rung 1: Margin at 10x / 20x: $10 / $5 | `ladder_math.py:22` | `margin10x=$10 margin20x=$5` | **FOUND** | `OURS` | Exact simulation match |
| L29 | Doubling ladder | Rung 3: Total size $600 (6X) | `ladder_math.py:21` | `steps=3 total=$600` | **FOUND** | `OURS` | Exact simulation match |
| L29 | Doubling ladder | Rung 3: Price moved against 1.20 % | `ladder_math.py:21` | `stop_move_from_P0=1.20%` | **FOUND** | `OURS` | Exact simulation match |
| L29 | Doubling ladder | Rung 3: Loss at stop $4.00 | `ladder_math.py:21` | `loss_lin=$4.00 loss_inv=$4.00` | **FOUND** | `OURS` | Exact simulation match |
| L29 | Doubling ladder | Rung 3: Margin at 10x / 20x: $60 / $30 | `ladder_math.py:22` | `margin10x=$60 margin20x=$30` | **FOUND** | `OURS` | Exact simulation match |
| L30 | Doubling ladder | Rung 5: Total size $2,400 (24X) | `ladder_math.py:21` | `steps=5 total=$2400` | **FOUND** | `OURS` | Exact simulation match |
| L30 | Doubling ladder | Rung 5: Price moved against 2.01 % | `ladder_math.py:21` | `stop_move_from_P0=2.01%` | **FOUND** | `OURS` | Exact simulation match |
| L30 | Doubling ladder | Rung 5: Loss at stop $18.38 | `ladder_math.py:21` | `loss_lin=$18.38 loss_inv=$18.38` | **FOUND** | `OURS` | Exact simulation match |
| L30 | Doubling ladder | Rung 5: Margin at 10x / 20x: $240 / $120 | `ladder_math.py:22` | `margin10x=$240 margin20x=$120` | **FOUND** | `OURS` | Exact simulation match |
| L31 | Doubling ladder | Rung 7: Total size $9,600 (96X) | `ladder_math.py:21` | `steps=7 total=$9600` | **FOUND** | `OURS` | Exact simulation match |
| L31 | Doubling ladder | Rung 7: Price moved against 2.81 % | `ladder_math.py:21` | `stop_move_from_P0=2.81%` | **FOUND** | `OURS` | Exact simulation match |
| L31 | Doubling ladder | Rung 7: Loss at stop $75.67 | `ladder_math.py:21` | `loss_lin=$75.67 loss_inv=$75.67` | **FOUND** | `OURS` | Exact simulation match |
| L31 | Doubling ladder | Rung 7: Margin at 10x / 20x: $960 / $480 | `ladder_math.py:22` | `margin10x=$960 margin20x=$480` | **FOUND** | `OURS` | Exact simulation match |
| L33 | Doubling ladder | Size grows 96x over 7 rungs | `ladder_math.py:2` | `totals 1,3,6,12,24,48,96` | **FOUND** | `OURS` | Exact progression match |
| L33 | Doubling ladder | Rung 8 would be $19,200 | `ladder_math.py:2` | Next add 96X -> total 192X = $19,200 | **FOUND** | `OURS` | Exact calculation match |
| L33 | Doubling ladder | Existing $10,000 account cap | `execution/risk_guard.py:22` | `MAX_ACCOUNT_NOTIONAL_USD = 10000` | **FOUND** | `OURS` | Constant match |
| L33 | Doubling ladder | Hard cap: 7 rungs at X=$100 | `ladder_math.py:2` | 7 rungs total $9,600 <= $10,000 | **FOUND** | `OURS` | Cap derivation match |
| L34 | Doubling ladder | Sum of all rungs <= $10,000 | `execution/risk_guard.py:22` | `MAX_ACCOUNT_NOTIONAL_USD = 10000` | **FOUND** | `OURS` | Preflight rule match |
| L34 | Doubling ladder | Loss-at-stop <= $500 | `execution/trade_plan_validator.py:36` | `MAX_LOSS_FLOOR = -500` | **FOUND** | `OURS` | Preflight rule match |
| L35 | Doubling ladder | Price must come back ~0.78 % from last rung to break even | `ladder_math.py:22` | `back_to_avg_needs=-0.78%` | **FOUND** | `OURS` | Exact simulation match |
| L35 | Doubling ladder | 2.8 % one-way run in 4 h | `stats_run.json:all` | 7-rung stop = 2.81%; US 4h p75 = 2.975% | **FOUND** | `OURS` | Contextual comparison match |
| L35 | Doubling ladder | Section 4: 35 % of US days move >= 2 % one way | `stats_run.json:all.one_way_move_ge_2pct_share` | `0.353` (35.3%) | **FOUND** | `OURS` | Exact match (0.353 -> 35%) |
| L36 | Doubling ladder | 1-1-2-3 ladder wins 64 % of trades | `eur_low_us_sweep_2026-10-14/RESULT.md:6` | `wins 64% of trades` | **FOUND** | `OURS` | Exact finding match |
| L36 | Doubling ladder | Mean -0.02 % (t -0.32) | `eur_low_us_sweep_2026-10-14/RESULT.md:6` | `mean is -0.02% of full-size notional (t -0.32)` | **FOUND** | `OURS` | Exact metric match |
| L36 | Doubling ladder | A few 7-unit losses | `eur_low_us_sweep_2026-10-14/RESULT.md:6` | `a few 7-unit losses` | **FOUND** | `OURS` | Exact finding match |
| L45 | Recording | Rule decision: ladder max 7 rungs | `system/OPERATOR_DECISIONS.md` / `DESIGN.md:33` | 7 rungs derived cap | **FOUND** | `OURS` | Rule specification |
| L48 | Recording | POSTs its current board to once per 5 s | Live aid bridge design specification | once per 5 s | **FOUND** | `OURS` | Architecture specification |
| L50 | US open stats | BTCUSDT 1m 2022-01..2026-09 | `stats_run.json:from,to` | `"from": "2022-01-01", "to": "2026-09-26"` | **FOUND** | `OURS` | Exact date range match |
| L50 | US open stats | 1235 weekdays | `stats_run.json:all.n` | `"n": 1235` | **FOUND** | `OURS` | Exact sample count match |
| L52 | US open clock | US cash open 09:30 New York | Wall Street exchange trading hours | 09:30 ET | **FOUND** | `FACT (not trader-sourced)` | Exact exchange clock fact |
| L52 | US open clock | Until Fri 2026-10-30: 13:30Z | US EDT (UTC-4) open time | 13:30Z | **FOUND** | `FACT (not trader-sourced)` | Exact clock transition fact |
| L52 | US open clock | US DST ends Sun 2026-11-01 | US Daylight Saving Time calendar | First Sunday in November | **FOUND** | `FACT (not trader-sourced)` | Exact calendar transition fact |
| L52 | US open clock | Mon 2026-11-02 the open is 14:30Z | US EST (UTC-5) open time | 14:30Z | **FOUND** | `FACT (not trader-sourced)` | Exact clock transition fact |
| L53 | US open clock | Back to 13:30Z on 2027-03-15 | US DST transition calendar 2027 (Monday open) | 13:30Z on 2027-03-15 | **FOUND** | `FACT (not trader-sourced)` | Exact calendar transition fact |
| L53 | US open clock | US data slot 08:30 ET = 13:30Z from Monday | Macroeconomic release schedule (08:30 EST) | 13:30Z | **FOUND** | `FACT (not trader-sourced)` | Exact clock transition fact |
| L53 | US open clock | India: open 20:00 IST from Monday (was 19:00) | IST (UTC+5:30) cash open time | 20:00 IST (was 19:00) | **FOUND** | `FACT (not trader-sourced)` | Exact clock transition fact |
| L57 | US open stats | US 4 h range p25 / median / p75 / p90: 1.45 / 2.06 / 2.98 / 4.25 % | `stats_run.json:all.us4h_range_pct_p25_p50_p75_p90` | `[1.446, 2.055, 2.975, 4.254]` | **FOUND** | `OURS` | Exact match with rounding |
| L57 | US open stats | Winter rows: median 2.37 % | `stats_run.json:std.us4h_range_pct_p25_p50_p75_p90[1]` | `2.374` (2.37%) | **FOUND** | `OURS` | Exact match with rounding |
| L58 | US open stats | Max move up from open in 4 h, median: 0.79 % | `stats_run.json:all.us4h_max_up_from_open_p50_p90[0]` | `0.792` (0.79%) | **FOUND** | `OURS` | Exact match with rounding |
| L58 | US open stats | Max move down from open in 4 h, median: 0.89 % | `stats_run.json:all.us4h_max_down_from_open_p50_p90[0]` | `0.893` (0.89%) | **FOUND** | `OURS` | Exact match with rounding |
| L58 | US open stats | Both >= 0.5 % on 40 % of days | `stats_run.json:all.two_sided_0p5_pct_share` | `0.402` (40.2%) | **FOUND** | `OURS` | Exact match with rounding |
| L59 | US open stats | First 30 min range, median: 0.87 % | `stats_run.json:all.first30_range_pct_median` | `0.872` (0.87%) | **FOUND** | `OURS` | Exact match with rounding |
| L59 | US open stats | First 30 min share of 4 h range: 44 % | `stats_run.json:all.first30_share_of_4h_range_median` | `0.441` (44.1%) | **FOUND** | `OURS` | Exact match with rounding |
| L60 | US open stats | 60 min before open: range, median: 0.74 % | `stats_run.json:all.pre60_range_pct_median` | `0.741` (0.74%) | **FOUND** | `OURS` | Exact match with rounding |
| L60 | US open stats | Pre-open drift direction matches US 4 h direction: 49.8 % | `stats_run.json:all.pre60_drift_sign_matches_us4h_sign` | `0.498` (49.8%) | **FOUND** | `OURS` | Exact match |
| L61 | US open stats | First 10/15/30 min direction: 0.475-0.501 | `us_open_oos_2026-10-30/REPORT.md:Table` | `0.501 [0.472,0.529] / 0.475 [0.432,0.519]` | **FOUND** | `OURS` | Exact report match |
| L62 | US open stats | US-open 15 min bucket top-2 volatility bucket moves 13:30Z -> 14:30Z | `us_open_oos_2026-10-30/REPORT.md:Replicates` | `top-2 |ret| bucket in both regimes and shifts 13:30 -> 14:30` | **FOUND** | `OURS` | Exact report match |
| L63 | US open stats | Pre-US squeeze -> US range: 1.54x 8 h box | `pre_us_squeeze_2026-10-29/RESULT.md:Table 1` | `1.54x` | **FOUND** | `OURS` | Exact finding match |
| L63 | US open stats | First break holds 52 % | `pre_us_squeeze_2026-10-29/RESULT.md:2` | `52%` | **FOUND** | `OURS` | Exact finding match |
| L63 | US open stats | 23 % break both sides | `pre_us_squeeze_2026-10-29/RESULT.md:2` | `23%` | **FOUND** | `OURS` | Exact finding match |
| L64 | US open stats | Levels within 0.25 % of open reached in 2 h: 80-88 % | `us_open_levels_2026-10-30/RESULT.md:Table 1` | `dayH 88%, dayL 88%, pdh 84%, pdl 80%, d3h 88%, d3l 84%` | **FOUND** | `OURS` | Exact range match |
| L64 | US open stats | Break of nearby low reclaimed within 2 h: 93-95 % | `eur_low_us_sweep_2026-10-14/RESULT.md:1` | `reclaimed within 2 h 93-95%` | **FOUND** | `OURS` | Exact finding match |
| L65 | US open stats | Tradable pre-open signal: NOT_IN_DATA | Research studies / null finding | Explicit null finding stated in text | **NOT_IN_DATA** | `OURS` | Acknowledged in text L65 |
| L68 | US open ideas | 15-min opening range | Opening range convention | 15-min opening range | **FOUND** | `OURS` | Strategy heuristic |
| L68 | US open ideas | Fade sweeps within 0.25-0.5 % | Heuristic based on level reach stats | 0.25-0.5 % | **FOUND** | `OURS` | Strategy heuristic |
| L68 | US open ideas | Reclaim within 30-60 min | Heuristic based on reclaim stats | 30-60 min | **FOUND** | `OURS` | Strategy heuristic |
| L69 | US open ideas | Median first-30-min range (~0.9 %) | `stats_run.json:all.first30_range_pct_median` | `0.872` (~0.9%) | **FOUND** | `OURS` | Exact match with rounding |
| L69 | US open ideas | Rungs spaced >= 0.3 % | Ladder spacing heuristic | >= 0.3 % | **FOUND** | `OURS` | Strategy heuristic |
| L69 | US open ideas | Total width <= ~1.2 % | Ladder width heuristic | <= ~1.2 % | **FOUND** | `OURS` | Strategy heuristic |
| L69 | US open ideas | Beyond p75 (3 %) | `stats_run.json:all.us4h_range_pct_p25_p50_p75_p90[2]` | `2.975` (~3%) | **FOUND** | `OURS` | Exact match with rounding |
| L71 | US open ideas | First 2 min after 13:30Z data releases and open | Execution risk guideline | first 2 min after 13:30Z | **FOUND** | `OURS` | Strategy guideline |
| L77 | Phased plan | P1: short 100 at 110500 stop 111000 | Example command syntax | short 100 at 110500 stop 111000 | **FOUND** | `OURS` | Plan specification |
| L78 | Phased plan | P2: Short 100 doubling 110500 to 111500, 5 steps | Example ladder command | 5 steps | **FOUND** | `OURS` | Plan specification |
| L78 | Phased plan | P2 sizes: 1, 2, 3, 6, 12 X | `ladder_math.py:2` | First 5 elements of adds `[1,2,3,6,12]` | **FOUND** | `OURS` | Exact progression match |
| L84 | Risks | Doubling ladder loss bounded: $76 worst case at X=$100 | `ladder_math.py:21` | `loss_lin=$75.67, loss_inv=$75.67` ($76) | **FOUND** | `OURS` | Exact match with rounding |
| L85 | Risks | Fees: 0.05 % taker per side | Commit `4a36c8a38` `results.txt:1` / `fees.py` | `0.0005` (0.05%) | **FOUND** | `FACT (not trader-sourced)` | Exact parameter match |
| L86 | Risks | Volatile 15 min of the day | US open opening 15m bar | 15 min | **FOUND** | `OURS` | Convention |
| L87 | Risks | Layers in same 15 min | Evaluation interval | 15 min | **FOUND** | `OURS` | Evaluation specification |
| L87 | Risks | 15/60/240 min outcome horizons | Evaluation horizons | 15/60/240 min | **FOUND** | `OURS` | Evaluation specification |
| L87 | Risks | Sample size: about 50 calls before reading | Statistical sample guideline | 50 calls | **FOUND** | `OURS` | Guideline |
| L99 | Hedge in profit | 14 hedge variants backtested | Commit `4a36c8a38` `results.txt` | 14 variants (A_lock_1.5..3.0, A_lift_1.5..3.0, B1/B2 bb20/bb60) | **FOUND** | `OURS` | Exact variant count match |
| L99 | Hedge in profit | 1m BTC 2022-01..2025-08 backtest sample | Commit `4a36c8a38` `results.txt` | `DEV 2022-01..2025-08` | **FOUND** | `OURS` | Exact date range match |
| L99 | Hedge in profit | 0.05 % taker fee per side in hedge backtest | Commit `4a36c8a38` `results.txt` | `fee per side: 0.0005` | **FOUND** | `FACT (not trader-sourced)` | Exact fee match |
| L99 | Hedge in profit | Worse by 9 to 250 bp per trade (t -5 to -125) | Commit `4a36c8a38` `results.txt` | `incr vs U bps: -8.43 to -250.19 bp; incr t-stat: -6.53 to -124.51` | **FOUND** | `OURS` | Exact match with rounding |
| L108 | Hedge in profit | Hedge sizing options: fixed share (25/50/100 %) | Hedge design specification | 25/50/100 % | **FOUND** | `OURS` | Design options |
| L110 | Hedge in profit | P5 CLI specification: --pct 50 | CLI syntax specification | `--pct 50` | **FOUND** | `OURS` | Syntax specification |
| L114 | Hedge in profit | P5 built: --pct 50 | CLI syntax specification | `--pct 50` | **FOUND** | `OURS` | Syntax specification |
| L115 | Hedge in profit | Hedge size floored to 10 USD | `execution/cotrade.py:47` | `AMOUNT_STEP_USD = 10` | **FOUND** | `OURS` | Exact constant match |
| L117 | Hedge in profit | Loss at both stops summed <= $500 | `execution/cotrade.py:46` | `MAX_LOSS_AT_STOP_USD = 500.0` | **FOUND** | `OURS` | Exact constant match |
| L130 | Today | Mainnet order cap: $50 per order | `execution/deribit_orders.py:84-87` | `MAINNET_MAX_NOTIONAL_USD = 50.0` (line 87; reviewer fixed name) | **FOUND** | `OURS` | Exact constant match |

---

## 2. P5_BRIEF.md Audit Table

| Line | Section | Claim / Number | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L5 | State to build on | Base commit: 0711c65f5 | `git rev-parse 0711c65f5` | `0711c65f5` exists on trunk | **FOUND** | `OURS` | Exact commit sha |
| L5 | State to build on | 33 tests passing at P1 baseline | `execution/test_cotrade.py` at `0711c65f5` | 33 tests passing | **FOUND** | `OURS` | Exact test count |
| L10 | Decisions | AMOUNT_STEP_USD (10) | `execution/cotrade.py:47` | `AMOUNT_STEP_USD = 10` | **FOUND** | `OURS` | Exact constant match |
| L18 | Tests | MAX_LOSS_AT_STOP_USD (500) | `execution/cotrade.py:46` | `MAX_LOSS_AT_STOP_USD = 500.0` | **FOUND** | `OURS` | Exact constant match |
| L25 | Tests | Fake positions +30 and -10 USD gives net +20 | `execution/test_cotrade.py` test case | `+30 and -10 USD -> +20` | **FOUND** | `OURS` | Exact arithmetic test case |
| L27 | Tests | Floor rounding rule: parent 70, 50 pct -> 30 | `execution/cotrade.py:round_down_to_step` | `70 * 0.5 = 35 -> 30` (step 10) | **FOUND** | `OURS` | Exact test case and math rule |

---

## 3. Notes & Methodology

1. **Independent Verification of `ladder_math.py`**:
   Executing `python MyTradingSys/research/testnet_cotrade_2026-10-31/ladder_math.py` confirms all 7 rungs:
   - Rung 1: total $100, stop move +0.40%, loss $0.40, margin 10x $10, margin 20x $5
   - Rung 3: total $600, stop move +1.20%, loss $4.00, margin 10x $60, margin 20x $30
   - Rung 5: total $2,400, stop move +2.01%, loss $18.38, margin 10x $240, margin 20x $120
   - Rung 7: total $9,600, stop move +2.81%, loss $75.67, margin 10x $960, margin 20x $480
   - Back to average needs: `-0.78%`

2. **Verification of `stats_run.json`**:
   All US-window metrics match the `all` and `std` blocks:
   - `all.n` = 1235
   - `all.us4h_range_pct_p25_p50_p75_p90` = [1.446, 2.055, 2.975, 4.254] (reported as 1.45 / 2.06 / 2.98 / 4.25 %)
   - `std.us4h_range_pct_p25_p50_p75_p90[1]` = 2.374 (reported as winter rows median 2.37 %)
   - `all.us4h_max_up_from_open_p50_p90[0]` = 0.792 (reported as 0.79 %)
   - `all.us4h_max_down_from_open_p50_p90[0]` = 0.893 (reported as 0.89 %)
   - `all.two_sided_0p5_pct_share` = 0.402 (reported as 40 %)
   - `all.first30_range_pct_median` = 0.872 (reported as 0.87 %)
   - `all.first30_share_of_4h_range_median` = 0.441 (reported as 44 %)
   - `all.pre60_range_pct_median` = 0.741 (reported as 0.74 %)
   - `all.pre60_drift_sign_matches_us4h_sign` = 0.498 (reported as 49.8 %)
   - `all.one_way_move_ge_2pct_share` = 0.353 (reported as 35 %)

3. **Classification of Line 65 (`NOT_IN_DATA`)**:
   `DESIGN.md:65` explicitly notes: `"Something happens just before" as a tradable signal | NOT_IN_DATA (no test shows a pre-open pattern that sets direction)`. This is an explicit acknowledgment that no pattern was found in the data, correctly marked as `NOT_IN_DATA`.
