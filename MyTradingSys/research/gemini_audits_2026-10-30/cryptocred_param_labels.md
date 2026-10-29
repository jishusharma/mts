# CryptoCred Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-cryptocred`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/cryptocred` code, find its source (analyst extract, FORMULAS.md, architecture spec, or none), and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 28
- **SOURCED count**: 4
- **OURS count**: 24
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/cryptocred/`)

| Family / Module | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `cc_structure` | Left fractal window | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:11` | `left: int = 2` | OURS | Fixed-width fractal choice; repo-chosen default. |
| `cc_structure` | Right fractal window | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:11` | `right: int = 2` | OURS | Fixed-width fractal choice; repo-chosen default. |
| `cc_structure` | Body vs wick flag | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:11` | `use_body: bool = True` | OURS | Compares candle bodies `max(o, c)` / `min(o, c)` instead of wicks; repo choice. |
| `cc_structure` | Range lookback | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:63` | `lookback: int = 50` | OURS | Window for range extreme noise proxy (`B145_cc_range_noise_live_neutrality.md:23-25`). |
| `cc_structure` | Range extreme margin | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:63` | `extreme_pct: float = 0.25` | OURS | Threshold fraction for range boundary (`B145_cc_range_noise_live_neutrality.md:23-25`). |
| `cc_structure` | Require sequence violation | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `require_prior_sequence: bool = True` | SOURCED | Enforces sequence violation per C08-E01 / CT-021: "my definition is a shift in the sequence of highs and lows in the opposite direction so for a bullish market structure break it is when a sequence of lower highs is violated by a higher high and of course for bearish market structure break is when a sequence of higher lows is violated by a lower low" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:330-331`, citing video `BHwoN7VPrBE` ~22:00). |
| `cc_structure` | Filter range noise | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `filter_range_noise: bool = False` | OURS | Range extreme noise filter toggle; repo design choice (`B145:8-10`). |
| `cc_structure` | Range lookback default | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `range_lookback: int = 50` | OURS | Forwarded default for range lookback. |
| `cc_structure` | Range extreme pct default | `MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81` | `range_extreme_pct: float = 0.25` | OURS | Forwarded default for range extreme margin. |
| `cc_retest` | Touch tolerance threshold | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:17` | `tolerance_pct: float = 0.0015` | OURS | Level touch threshold margin `level * (1 +/- tolerance_pct)`; repo choice. |
| `cc_retest` | Invalidation threshold | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:17` | `invalidate_pct: float = 0.005` | OURS | Invalidation threshold before retest touch `level * (1 -/+ invalidate_pct)`; repo choice. |
| `cc_retest` | Retest expiry bars | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:17` | `expiry_bars: int = 200` | OURS | Maximum scan window for retest; repo choice. |
| `cc_retest` | Immediate retest bar limit | `MyTradingSys/backtest/layers/cryptocred/cc_retest.py:57` | `immediate_bars: int = 5` | OURS | Categorization threshold between immediate and rounded retest; repo choice. |
| `cc_setups` | Setup 1 stop buffer | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53` | `stop_buffer_pct: float = 0.001` | OURS | Stop distance buffer; marked NO-SOURCE in `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:12-14`. |
| `cc_setups` | Setup 1 target multiple | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53` | `target_r: float = 1.5` | OURS | Marked NO-SOURCE as fixed value in `B143:13-14` (BHwoN7VPrBE:82 cites 1.5R as a minimum requirement, not a fixed target). |
| `cc_setups` | Setup 2 fib lower bound | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `fib_lo: float = 0.618` | SOURCED | Sourced quote (C10-E04 / CT-032): "personally i look for support resistance structures anywhere between the 618 and 786 retracement... there's no fixed answer really" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`, citing video `BHwoN7VPrBE` ~50:00, ~55:00). |
| `cc_setups` | Setup 2 fib upper bound | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `fib_hi: float = 0.786` | SOURCED | Sourced quote (C10-E04 / CT-032): "between the 618 and 786 retracement" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`). |
| `cc_setups` | Setup 2 stop buffer | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `stop_buffer_pct: float = 0.001` | OURS | Stop distance buffer; marked NO-SOURCE in `B143:14,18`. |
| `cc_setups` | Setup 2 target multiple | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89` | `target_r: float = 1.5` | OURS | Marked NO-SOURCE as fixed target in `B143:13,18`. |
| `cc_setups` | Setup 2 limit expiry | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:90` | `expiry_bars = 200` | OURS | Limit order validity timeout window in bars. |
| `cc_setups` | Setup 3 failure lookback | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:181` | `failure_lookback: int = 20` | OURS | Window after break to observe failure to make a new extreme; repo choice. |
| `cc_setups` | Setup 3 stop buffer | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:181` | `stop_buffer_pct: float = 0.001` | OURS | Stop distance buffer; marked NO-SOURCE in `B143:14,40`. |
| `cc_setups` | Setup 3 target multiple | `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:181` | `target_r: float = 2.0` | SOURCED | Sourced quote (C10-E02 / CT-028): "if you're trading counter trend you're trading against the current so to speak and therefore you have to be more defensive and less liberal with those positions... greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:417-419`, citing video `BHwoN7VPrBE` ~33:00). |
| `run_cc_setups` | Chronological split fraction | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:77` | `is_frac = 0.70` | OURS | 70/30 chronological train/test split protocol. |
| `run_cc_setups` | Minimum OOS trade count | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:60` | `MIN_OOS_N = 30` | OURS | T055 backtest protocol statistical threshold. |
| `run_cc_setups` | Minimum net Sharpe | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:61` | `MIN_SHARPE = 0.3` | OURS | T055 backtest protocol statistical threshold. |
| `run_cc_setups` | BTCUSDT price tick | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:102` | `TICK = 0.1` | OURS | Venue tick size for 1-tick trade-through limit fill protocol (`B151:24`). |
| `run_cc_setups` | Max holding bars | `MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:359` | `max_bars = 1440` | OURS | Maximum 1m bars a trade may stay open (24 hours). |

---

## 2. Details and Observations

1. **Trader Sourced vs Repo Engineering**:
   - CryptoCred's methodology defines the structural logic: sequence-violation market structure break (`C08-E01`), 0.618-0.786 Fibonacci retracement boundaries (`C10-E04`), and a higher 2.0R target multiple for counter-trend reversal setups (`C10-E02`).
   - Mechanical discretizations—such as fractal swing width (`left=2, right=2`), range-noise filters (`50 bars, 25%`), retest touch and invalidation thresholds (`0.15%`, `0.5%`), and the 0.1% stop buffer (`B143`)—are repo-engineered defaults (`OURS`).
2. **Backtest Protocol & Infrastructure**:
   - The 70/30 split, `TICK=0.1` trade-through limit fill convention, and T055 verdict gating thresholds (`MIN_OOS_N=30`, `MIN_SHARPE=0.3`) originate entirely from internal backtest standards (`OURS`).
