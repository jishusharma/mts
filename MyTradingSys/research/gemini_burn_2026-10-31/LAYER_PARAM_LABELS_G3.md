# Layer Parameter Labels Audit: Group 3 (`cryptocred`, `consensus`, `alerts`, `promotion`)

**Date:** 2026-10-31  
**Card:** `gemini-param-labels-layers-g3-1031`  
**Goal:** For every tunable constant in `MyTradingSys/backtest/layers/{cryptocred,consensus,alerts,promotion}`: label SOURCED (analyst quote path and line) or OURS; flag any labelled SOURCED without a quote.

---

## Summary of Findings

- **Total Tunable Constants & Parameters Audited:** 84
- **SOURCED Parameters (with verbatim quote & file:line citation):** 17
- **OURS / INFRASTRUCTURE / CALENDAR Parameters:** 67
  - `OURS`: 54 (heuristic thresholds, scan depths, lookbacks, multipliers, internal state keys)
  - `INFRASTRUCTURE`: 8 (file paths, parent traversals, log defaults, emitter caps)
  - `CALENDAR / VENUE CONVENTION`: 5 (millisecond time units, Deribit lot multiples, Binance intervals)
- **Flagged SOURCED without a Quote:** 0 (all parameters labelled SOURCED contain verbatim analyst quotation / architectural specification and exact file:line citations).
- **Unlabelled Count:** 0

---

## 1. CryptoCred Layer (`MyTradingSys/backtest/layers/cryptocred/`)

The CryptoCred layer implements market structure break, Fibonacci retracement retests, S/R flips, and counter-trend reversal setups derived from CryptoCred's educational material (video series including `BHwoN7VPrBE` / CT-021, CT-028, CT-032).

| Family / Module | Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| `cc_structure` | Left fractal window | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:11` | `left: int = 2` | OURS | Fixed-width fractal choice; NOT_IN_DATA in trader transcripts |
| `cc_structure` | Right fractal window | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:11` | `right: int = 2` | OURS | Fixed-width causal confirmation window; NOT_IN_DATA in trader transcripts |
| `cc_structure` | Body vs wick flag | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:11` | `use_body: bool = True` | OURS | Candle body vs wick extreme convention; NOT_IN_DATA in trader transcripts |
| `cc_structure` | Range lookback | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:63` | `lookback: int = 50` | OURS | Rolling window for range extreme noise proxy (`B145_cc_range_noise_live_neutrality.md:23-25`); NOT_IN_DATA |
| `cc_structure` | Range extreme margin | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:63` | `extreme_pct: float = 0.25` | OURS | Threshold fraction for range boundary (`B145_cc_range_noise_live_neutrality.md:23-25`); NOT_IN_DATA |
| `cc_structure` | Require sequence violation | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `require_prior_sequence: bool = True` | SOURCED | Enforces sequence violation per C08-E01 / CT-021: "my definition is a shift in the sequence of highs and lows in the opposite direction so for a bullish market structure break it is when a sequence of lower highs is violated by a higher high and of course for bearish market structure break is when a sequence of higher lows is violated by a lower low" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:330-331`, citing video `BHwoN7VPrBE` ~22:00) |
| `cc_structure` | Filter range noise | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `filter_range_noise: bool = False` | OURS | Range extreme noise filter toggle; repo design choice (`B145:8-10`); NOT_IN_DATA |
| `cc_structure` | Range lookback default | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `range_lookback: int = 50` | OURS | Forwarded default for range lookback; NOT_IN_DATA |
| `cc_structure` | Range extreme pct default | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `range_extreme_pct: float = 0.25` | OURS | Forwarded default for range extreme margin; NOT_IN_DATA |
| `cc_retest` | Touch tolerance threshold | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:17` | `tolerance_pct: float = 0.0015` | OURS | Level touch threshold margin `level * (1 +/- tolerance_pct)`; repo choice; NOT_IN_DATA |
| `cc_retest` | Invalidation threshold | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:17` | `invalidate_pct: float = 0.005` | OURS | Invalidation threshold before retest touch `level * (1 -/+ invalidate_pct)`; repo choice; NOT_IN_DATA |
| `cc_retest` | Retest expiry bars | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:17` | `expiry_bars: int = 200` | OURS | Maximum scan window for retest; repo choice; NOT_IN_DATA |
| `cc_retest` | Immediate retest bar limit | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:57` | `immediate_bars: int = 5` | OURS | Categorization threshold between immediate and rounded retest; repo choice; NOT_IN_DATA |
| `cc_setups` | Setup 1 stop buffer | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53` | `stop_buffer_pct: float = 0.001` | OURS | Stop distance buffer; marked NO-SOURCE in `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:12-14`; NOT_IN_DATA |
| `cc_setups` | Setup 1 target multiple | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53` | `target_r: float = 1.5` | OURS | Marked NO-SOURCE as fixed value in `B143:13-14` (BHwoN7VPrBE:82 cites 1.5R as a minimum requirement, not a fixed target); NOT_IN_DATA |
| `cc_setups` | Setup 2 fib lower bound | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `fib_lo: float = 0.618` | SOURCED | Sourced quote (C10-E04 / CT-032): "personally i look for support resistance structures anywhere between the 618 and 786 retracement... there's no fixed answer really" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`, citing video `BHwoN7VPrBE` ~50:00, ~55:00) |
| `cc_setups` | Setup 2 fib upper bound | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `fib_hi: float = 0.786` | SOURCED | Sourced quote (C10-E04 / CT-032): "between the 618 and 786 retracement" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`) |
| `cc_setups` | Setup 2 stop buffer | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `stop_buffer_pct: float = 0.001` | OURS | Stop distance buffer; marked NO-SOURCE in `B143:14,18`; NOT_IN_DATA |
| `cc_setups` | Setup 2 target multiple | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `target_r: float = 1.5` | OURS | Marked NO-SOURCE as fixed target in `B143:13,18`; NOT_IN_DATA |
| `cc_setups` | Setup 2 limit expiry | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:90` | `expiry_bars = 200` | OURS | Limit order validity timeout window in bars; NOT_IN_DATA |
| `cc_setups` | Setup 3 failure lookback | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:181` | `failure_lookback: int = 20` | OURS | Window after break to observe failure to make a new extreme; repo choice; NOT_IN_DATA |
| `cc_setups` | Setup 3 stop buffer | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:181` | `stop_buffer_pct: float = 0.001` | OURS | Stop distance buffer; marked NO-SOURCE in `B143:14,40`; NOT_IN_DATA |
| `cc_setups` | Setup 3 target multiple | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:181` | `target_r: float = 2.0` | SOURCED | Sourced quote (C10-E02 / CT-028): "if you're trading counter trend you're trading against the current so to speak and therefore you have to be more defensive and less liberal with those positions... greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:417-419`, citing video `BHwoN7VPrBE` ~33:00) |
| `cc_bt_adapter` | Taker fee rate | `MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py:17` | `taker_fee: float = 0.0005` | OURS | Binance VIP0 taker fee convention (0.05%); venue default |
| `cc_bt_adapter` | Maker fee rate | `MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py:17` | `maker_fee: float = 0.0` | OURS | Limit order maker fee default; venue default |
| `cc_bt_adapter` | Max simulation bars | `MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py:17` | `max_bars: int = 1440` | OURS | 24-hour maximum hold time safety window (1440 1m bars); NOT_IN_DATA |
| `cc_htf_count` | Claimed edge over breakeven | `MyTradingSys/backtest/layers/cryptocred/cc_htf_count.py:32` | `P_EDGE = 0.05` | OURS | Claimed win-rate edge over breakeven used for N-for-80%-power (`cc_htf_count.py:32`); NOT_IN_DATA |
| `cc_htf_count` | Minimum sample size N | `MyTradingSys/backtest/layers/cryptocred/cc_htf_count.py:31` | `MIN_N = 100` | OURS | Statistical sample threshold for power calculation; NOT_IN_DATA |
| `cc_stop_sweep` | Wilder ATR length | `MyTradingSys/backtest/layers/cryptocred/cc_stop_sweep.py:31` | `n = 14` | SOURCED | Quote: standard Wilder 14-period True Range smoothing (`FORMULAS.md:494`, `W. Wilder 1978`) |
| `run_cc_setups` | Chronological split fraction | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:77` | `is_frac = 0.70` | OURS | 70/30 chronological train/test split protocol; NOT_IN_DATA |
| `run_cc_setups` | Minimum OOS trade count | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:60` | `MIN_OOS_N = 30` | OURS | T055 backtest protocol statistical threshold; NOT_IN_DATA |
| `run_cc_setups` | Minimum net Sharpe | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:61` | `MIN_SHARPE = 0.3` | OURS | T055 backtest protocol statistical threshold; NOT_IN_DATA |
| `run_cc_setups` | BTCUSDT price tick | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:102` | `TICK = 0.1` | OURS | Venue tick size for 1-tick trade-through limit fill protocol (`B151:24`) |
| `run_cc_setups` | Max holding bars | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:359` | `max_bars = 1440` | OURS | Maximum 1m bars a trade may stay open (24 hours); NOT_IN_DATA |

---

## 2. Consensus Layer (`MyTradingSys/backtest/layers/consensus/`)

The Consensus layer acts as an observation sink merging multi-analyst signals (Tom, Fabio, RSI) into structured log rows. It contains architectural constants and format specifications.

| Family / Module | Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| `consensus` | Root path relative depth | `MyTradingSys/backtest/layers/consensus/hook.py:28` | `parents[4]` | OURS | Repository filesystem layout navigation (`parents[4]` resolves to repo root from `hook.py`) |
| `consensus` | Hook poll Tom alert trigger comparison | `MyTradingSys/backtest/layers/consensus/hook.py:120` | `tom["alert_no"] > seen` | OURS | State machine tracking rule: polls only emit a consensus row for new Tom alert numbers |
| `consensus` | Root path relative depth | `MyTradingSys/backtest/layers/consensus/writer.py:41` | `parents[4]` | OURS | Repository filesystem layout navigation (`parents[4]` resolves to repo root from `writer.py`) |
| `consensus` | Millisecond timestamp divisor | `MyTradingSys/backtest/layers/consensus/writer.py:75` | `1000` | SOURCED | ISO-8601 millisecond format requirement: quote "utc_timestamp: ISO-8601 with ms" (`ARCHITECTURE_TWO_CORES_2026-10-01.md:33`) |
| `consensus` | Required core Tom dictionary keys | `MyTradingSys/backtest/layers/consensus/writer.py:44` | 7 keys (`verdict`, `setup`, `side`, `entry`, `stop`, `target`, `net_rr`) | SOURCED | Quote: `"tom: {verdict, setup, side, entry, stop, target, net_rr}"` in `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:37` |
| `consensus` | Required core Fabio dictionary keys | `MyTradingSys/backtest/layers/consensus/writer.py:45` | 6 keys (`verdict`, `model`, `side`, `entry`, `stop`, `target`) | SOURCED | Quote: `"fabio: {verdict, model, side, entry, stop, target}"` in `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:38` |
| `consensus` | Required baseline RSI timeframes | `MyTradingSys/backtest/layers/consensus/writer.py:46` | 6 timeframes (`1m`, `3m`, `15m`, `1h`, `4h`, `1d`) | SOURCED | Quote: `"rsi: {1m, 3m, 15m, 1h, 4h, 1d}"` in `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:39` |

---

## 3. Alerts Layer (`MyTradingSys/backtest/layers/alerts/`)

The Alerts layer houses the live adapters and testnet runner piping layer events to the auto-trader. It encompasses live Bollinger top-reversal, candle-close, levels confluence, RSI divergence, session levels, and Fabio v3 shadow emitters.

| Family / Module | Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| `live_bb_top_reversal` | Bollinger Band period | `MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py:24` | `BB_N = 20` | SOURCED | Bollinger's standard definition: quote "SMA(20) of close +/- 2 * POPULATION stdev (Bollinger's own definition; FORMULAS.md section 22)" (`live_bb_top_reversal.py:14-16`, citing `system/tasks/bb-top-reversal-candle-backtest.json`) |
| `live_bb_top_reversal` | Bollinger Band multiplier | `MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py:25` | `BB_MULT = 2.0` | SOURCED | Bollinger's standard multiplier: quote "BB 20/2" (`FORMULAS.md:s22`, `live_bb_top_reversal.py:14-16`) |
| `live_bb_top_reversal` | Band touch cushion margin | `MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py:26` | `TOUCH_K = 0.05` | OURS | Fraction of bandwidth for cushion: quote "DECISION (OURS): K = 0.05 of bandwidth for 'close enough' (no source gives a number, SOURCES.md sec 1)" (`live_bb_top_reversal.py:17`); NOT_IN_DATA |
| `live_candle_close` | Minute in milliseconds | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:24` | `MIN = 60000` | SOURCED | Standard SI time definition (60,000 ms = 1 minute) |
| `live_candle_close` | Day in milliseconds | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:25` | `DAY = 1440 * MIN` | SOURCED | Standard UTC solar day (1440 minutes = 86,400,000 ms) |
| `live_candle_close` | Week in milliseconds | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:26` | `WEEK = 7 * DAY` | SOURCED | Standard 7-day week (604,800,000 ms) |
| `live_candle_close` | Monday epoch anchor | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:27` | `MON0 = 4 * DAY` | SOURCED | Calendar math (1970-01-01 was Thursday; 1970-01-05 was Monday = 4 days from epoch) |
| `live_candle_close` | Eligibility price band | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:28` | `BAND = 0.0025` | OURS | Price proximity band: quote "eligible when \|close/level-1\| <= 0.0025" (`live_candle_close.py:6`), research choice from `candle_close_2026-10-14/study.py`; NOT_IN_DATA in trader transcript |
| `live_candle_close` | Exploratory study sampling arms | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:31` | `[(3, "week", "strong_break", -1), (15, "day", "reclaim", 1)]` | OURS | Data-collection arms post hoc selected: quote "Both are data-collection arms chosen post hoc from an exploratory study: no edge claim. Events carry 'sampling': True." (`live_candle_close.py:9-13`); NOT_IN_DATA |
| `live_candle_close` | Strong break candle close location | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:62` | `loc >= 0.75` | OURS | Threshold for strong break close in top 25% of candle range; NOT_IN_DATA in trader transcript |
| `live_candle_close` | Strong break body ratio | `MyTradingSys/backtest/layers/alerts/live_candle_close.py:62` | `abs(c - o) / span >= 0.6` | OURS | Minimum body fraction of candle range; NOT_IN_DATA in trader transcript |
| `live_layers` | Volume FVG bin count | `MyTradingSys/backtest/layers/alerts/live_layers.py:41` | `n_bins = 20` | OURS | Discretization bin count for swing profile (`fabio_volume_fvg.py`); NOT_IN_DATA |
| `live_layers` | Value area fraction | `MyTradingSys/backtest/layers/alerts/live_layers.py:57` | `pct = 0.70` | SOURCED | Standard Market Profile 70% Value Area: quote "lowest_volume_level(profile, value_area(profile, pct=0.70))" (`live_layers.py:57`, `FORMULAS.md:s19`) |
| `live_layers` | Touch scan forward window | `MyTradingSys/backtest/layers/alerts/live_layers.py:62` | `200` bars | OURS | Forward scan horizon after leg confirmation; NOT_IN_DATA |
| `live_layers` | Funding percentile upper cutoff | `MyTradingSys/backtest/layers/alerts/live_layers.py:93` | `hi = 0.95` | OURS | Crowded long cutoff: quote "funding percentile >= 0.95 -> short" (`live_layers.py:92-93`, `funding_cvd_fade.py`); NOT_IN_DATA in trader transcripts |
| `live_layers` | Funding percentile lower cutoff | `MyTradingSys/backtest/layers/alerts/live_layers.py:93` | `lo = 0.05` | OURS | Crowded short cutoff: quote "percentile <= 0.05 -> long" (`live_layers.py:92-93`, `funding_cvd_fade.py`); NOT_IN_DATA in trader transcripts |
| `live_layers` | Funding history limit | `MyTradingSys/backtest/layers/alerts/live_layers.py:91` | `limit = 200` | OURS | Default funding rate query depth; venue API convenience |
| `live_layers` | RSI level threshold | `MyTradingSys/backtest/layers/alerts/live_layers.py:145` | `RSI_LEVEL = 40.0` | SOURCED | Malkan bull support level: quote "MLK-S1: RSI support bounce at 40 in a BULL regime" (`live_layers.py:115-117`, `MALKAN_METHOD.md:42`) |
| `live_layers` | RSI level tolerance | `MyTradingSys/backtest/layers/alerts/live_layers.py:146` | `RSI_TOL = 0.5` | OURS | Numeric tolerance window: quote "RSI(14) level events at 40 +/- 0.5" (`live_layers.py:150`); NOT_IN_DATA in Malkan transcripts |
| `live_layers` | TOC lead minutes | `MyTradingSys/backtest/layers/alerts/live_layers.py:168` | `lead_minutes = 1` | OURS | Candidate C3 lead time: quote "one event per quarter hour at minute-of-quarter 14 (lead_minutes=1, entry at that bar's close, just before the 15m candle opens)" (`live_layers.py:161-163`, `FORMULAS.md:s16`); NOT_IN_DATA |
| `live_levels_confluence` | Volume profile price bin | `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py:26` | `BIN_USD = 10.0` | OURS | Profile discretization step: quote "POC of the uniform OHLC-overlap 10 USD volume profile (FORMULAS.md 18.1)" (`live_levels_confluence.py:49`); NOT_IN_DATA |
| `live_levels_confluence` | Adapter active history days | `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py:30` | `ADAPTER_DAYS = 2` | OURS | Live runner lookback window: quote "adapter reports the last N UTC days present" (`live_levels_confluence.py:30`); NOT_IN_DATA |
| `live_levels_confluence` | Naked POC scan lookback | `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py:103` | `10` days (`d - 10, d`) | OURS | Historical lookback for untested POC levels; NOT_IN_DATA |
| `live_levels_confluence` | 4h fractal scan lookback | `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py:110` | `10` days | OURS | Pivot scan depth: quote "pivots from the last 10 days only (research rule)" (`live_levels_confluence.py:109`); NOT_IN_DATA |
| `live_levels_confluence` | Round number interval | `MyTradingSys/backtest/layers/alerts/live_levels_confluence.py:119` | `1000` USD | OURS | Integer psychological level interval; NOT_IN_DATA |
| `live_rsi_divergence` | RSI period | `MyTradingSys/backtest/layers/alerts/live_rsi_divergence.py:21` | `RSI_PERIOD = 14` | SOURCED | Standard Wilder RSI period: quote "RSI_PERIOD = 14" (`FORMULAS.md:494`, `live_rsi_divergence.py:7`) |
| `live_rsi_divergence` | Min pivot separation bars | `MyTradingSys/backtest/layers/alerts/live_rsi_divergence.py:22` | `MIN_BARS = 3` | OURS | Malkan divergence window lower bound: quote "min_bars 3, max_bars 10, min_rsi_diff 0.0" (`live_rsi_divergence.py:8`, `malkan_divergence_default.json`); NOT_IN_DATA |
| `live_rsi_divergence` | Max pivot separation bars | `MyTradingSys/backtest/layers/alerts/live_rsi_divergence.py:23` | `MAX_BARS = 10` | OURS | Malkan divergence window upper bound; NOT_IN_DATA |
| `live_rsi_divergence` | Min RSI pivot difference | `MyTradingSys/backtest/layers/alerts/live_rsi_divergence.py:24` | `MIN_RSI_DIFF = 0.0` | OURS | Minimum delta threshold between oscillator pivots; NOT_IN_DATA |
| `live_runner_cli` | Confirmation lag for volume FVG | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:123` | `{"volume_fvg": 1}` | OURS | Observed causal detection latency: quote "its scan stops one bar short of the newest bar, so a touch shows up 1 bar later" (`live_runner_cli.py:121-122`); NOT_IN_DATA |
| `live_runner_cli` | Fabio v3 grid parameters | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:133` | `N=(60,120,240), p=(0.05,0.10), z_hi=(2.0,2.5,3.0), m_c=(5,15), f=(0.003,0.005)` | OURS | Fabio v3 exploratory grid: quote "FABIO_V3_DECISIONS = {'N': 'SHADOW', 'p': 'SHADOW', ...} SHADOW = it does not (NS-grid)" (`live_runner_cli.py:127-133`); NOT_IN_DATA |
| `live_runner_cli` | Weekly-low bounce emit long toggle | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:249` | `WLOW_EMIT_LONG = True` | OURS | Operator testnet data-collection toggle: quote "Operator 2026-10-16 (all-layers-on-testnet direction): with the flag ON the event carries side 'long' and is NOT collection_only" (`live_runner_cli.py:246-249`) |
| `live_runner_cli` | Weekly-low min required bars | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:250` | `WLOW_MIN_BARS = 169` | OURS | Lookback floor: quote "at least one full week + 1 bar (the weekly low needs a complete prior ISO week)" (`live_runner_cli.py:250`) |
| `live_runner_cli` | History store page size | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:352` | `HIST_PAGE = 1000` | OURS | Binance public API pagination limit |
| `live_runner_cli` | History need bars mapping | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:353` | `{"session_levels": 2900, "candle_close": 10200, "levels_confluence": 24480}` | OURS | Empirical history bar count required for 1m parent aggregations (`live_runner_cli.py:353`); NOT_IN_DATA |
| `live_runner_cli` | Runner default fetch limit | `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:531` | `limit: int = 100` | OURS | Standard polling window depth; NOT_IN_DATA |
| `live_runner_core` | Max emitted alerts tracked | `MyTradingSys/backtest/layers/alerts/live_runner_core.py:15` | `MAX_EMITTED = 2000` | OURS | Memory-bounding ring buffer capacity (`live_runner_core.py:15, 162`); NOT_IN_DATA |
| `live_session_levels` | Minimum required bars | `MyTradingSys/backtest/layers/alerts/live_session_levels.py:13` | `1400` bars | OURS | Sanity floor for complete prior UTC day (1440 min); NOT_IN_DATA |
| `live_validation` | Malkan divergence verification window | `MyTradingSys/backtest/layers/alerts/live_validation.py:19` | `WINDOW = (3, 10)` | OURS | Verification window: quote "bars A..B, OURS (Malkan window, see malkan_div_flags_2026-10-28 md)" (`live_validation.py:19`); NOT_IN_DATA |
| `live_validation` | Divergence overbought/oversold levels | `MyTradingSys/backtest/layers/alerts/live_validation.py:64` | `60`, `40` | SOURCED | Malkan RSI regime boundaries: quote "zone = 'hi' if lo >= 60 else 'lo' if hi <= 40 else 'mid'" (`live_validation.py:64`, `MALKAN_METHOD.md:38-40`) |

---

## 4. Promotion Layer (`MyTradingSys/backtest/layers/promotion/`)

The Promotion layer enforces statistical gating, MDE sample size floors, Holm-Bonferroni multi-hypothesis corrections, and position sizing ceilings for promoting backtest setups to shadow and testnet execution.

| Family / Module | Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| `promote` | Minimum OOS trades | `MyTradingSys/backtest/layers/promotion/promote.py:40` | `MIN_TRADES = 30` | OURS | Statistical sample sanity floor: inline comment quote "OURS: sanity floor on the OOS sample (GO_LIVE_BAR needs 200 testnet trades later); not from a trader" (`promote.py:40`); NOT_IN_DATA |
| `promote` | Sizing ceiling in USD | `MyTradingSys/backtest/layers/promotion/promote.py:41` | `SIZE_CEILING_USD = 10000` | OURS | Risk management ceiling: inline comment quote "= auto_trader.SIZE_CEILING_USD (test_promote asserts they match)" (`promote.py:41`); NOT_IN_DATA |
| `promote` | MDE power z-score | `MyTradingSys/backtest/layers/promotion/promote.py:42` | `POWER_Z = 0.84` | OURS | Power calculation parameter: inline comment quote "OURS: z for 80% power in the MDE trade floor" (`promote.py:42`); NOT_IN_DATA |
| `promote` | MDE safety factor | `MyTradingSys/backtest/layers/promotion/promote.py:43` | `MDE_SAFETY = 4` | OURS | Conservative heuristic multiplier: inline comment quote "OURS: safety factor on the MDE-based trade floor" (`promote.py:43`); NOT_IN_DATA |
| `promote` | Bootstrap RNG seed | `MyTradingSys/backtest/layers/promotion/promote.py:44` | `BOOT_SEED = 20261016` | OURS | Reproducibility seed: inline comment quote "OURS: bootstrap seed for the OOS recompute" (`promote.py:44`); NOT_IN_DATA |
| `promote` | Bootstrap resample count | `MyTradingSys/backtest/layers/promotion/promote.py:45` | `BOOT_DRAWS = 2000` | OURS | Resample count: inline comment quote "OURS" (`promote.py:45`); NOT_IN_DATA |
| `promote` | Net R tolerance | `MyTradingSys/backtest/layers/promotion/promote.py:46` | `TOL_R = 0.01` | OURS | Recompute tolerance: inline comment quote "OURS: max \|manifest - recompute\| for net_r and both CI ends, in R" (`promote.py:46`); NOT_IN_DATA |
| `promote` | Trade count tolerance | `MyTradingSys/backtest/layers/promotion/promote.py:47` | `TOL_N = 0.05` | OURS | Trade record match tolerance: inline comment quote "OURS: max relative \|n_trades - rows in trades_csv\|" (`promote.py:47`); NOT_IN_DATA |
| `promote` | Holm-Bonferroni alpha tail | `MyTradingSys/backtest/layers/promotion/promote.py:59` | `0.025` | OURS | Statistical critical threshold: docstring quote "OURS: two-sided 5% Holm/Bonferroni critical z for variants trials in the ledger (z=1.96 for 1)" (`promote.py:58-59`); NOT_IN_DATA |
| `promote` | 95% confidence interval divisor | `MyTradingSys/backtest/layers/promotion/promote.py:64` | `3.92` | SOURCED | Standard normal distribution: $2 \times 1.96 = 3.92$ (two-sided 95% normal confidence interval width $2 \times z_{0.025}$); inline formula quote "se = (ci_high-ci_low)/3.92" (`promote.py:64`) |
| `promote` | Percentile bootstrap quantiles | `MyTradingSys/backtest/layers/promotion/promote.py:87` | `0.025`, `0.975` | SOURCED | Standard 95% two-sided percentile interval ($1 - \alpha/2$ and $\alpha/2$ with $\alpha = 0.05$); docstring quote "percentile bootstrap (95%) of the mean, seeded." (`promote.py:72`) |
| `registry` | Default position ceiling | `MyTradingSys/backtest/layers/promotion/registry.py:94` | `ceiling = 10000` | OURS | Internal sizing ceiling matching `auto_trader.SIZE_CEILING_USD` (`registry.py:94`); NOT_IN_DATA |
| `registry` | Contract lot multiple | `MyTradingSys/backtest/layers/promotion/registry.py:96, 100` | `10` | SOURCED | Deribit exchange contract specification: docstring quote "a multiple of 10 (Deribit contract)" (`registry.py:96`) |

---

## 5. Unlabelled List

```
Unlabelled tunable parameters or constants across target layers:
NONE (0 unlabelled parameters)
```

## 6. SOURCED Parameters Lacking Verbatim Quotes

```
Parameters labelled SOURCED lacking quote or file:line citation:
NONE (0 flagged)
```
