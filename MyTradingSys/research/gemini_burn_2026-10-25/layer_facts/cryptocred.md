# Layer Fact Sheet: cryptocred

> **Claude review 2026-10-26** (`MyTradingSys/research/layer_lab/reports/2026-10-26_gemini-facts-review.md`): content errors below are fixed; about 60 line cites drift from trunk (content true, line off) and are listed in that report, not rewritten here. Treat any line number as approximate (+-15).

Facts compiled from repository files only per ANTIGRAVITY_LAPTOP.md item C (`MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34`).
No verdict on keeping, dropping, demoting, or parking any layer (`MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:16,33`).

---

## 1. ORIGIN

- **Analyst / Trader**: CryptoCred (`MyTradingSys/system/LAYERS.md:106`, `MyTradingSys/research/cross_trader_consolidated.md:925,935`).
- **Primary Source Clusters (`MyTradingSys/research/cross_trader_consolidated.md:255-440`)**:
  - Cluster C08: Market Structure Break (MSB): Definition & Significance (`MyTradingSys/research/cross_trader_consolidated.md:321`, `MyTradingSys/backtest/layers/FORMULAS.md:167-172`).
  - Cluster C07: Retests (`MyTradingSys/research/cross_trader_consolidated.md:255`, `MyTradingSys/backtest/layers/FORMULAS.md:167-172`).
  - Cluster C10: Setup Types: Entry Patterns (`MyTradingSys/research/cross_trader_consolidated.md:401`, `MyTradingSys/backtest/layers/FORMULAS.md:167-172`).
  - Source video inventory (`XeQV2ECtZVQ`, `_ndAoizXy64`, `Yp0k8HD5xro`, `BHwoN7VPrBE`, `inqHN8q57X4`): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:5`).
- **Quoted Sources (file:line)** (`MyTradingSys/research/cross_trader_consolidated.md:263-431`):
  - **MSB Definition (C08-E01 / CT-021)**: "my definition is a shift in the sequence of highs and lows in the opposite direction so for a bullish market structure break it is when a sequence of lower highs is violated by a higher high and of course for bearish market structure break is when a sequence of higher lows is violated by a lower low" (`MyTradingSys/research/cross_trader_consolidated.md:330-331`, citing video `BHwoN7VPrBE` ~22:00).
  - **Swing High/Low Definition (C09-E01 / CT-020)**: "a swing low is a low with a higher low on both sides and a swing high is a high with a lower high on both sides... there's no single formula... recency is important, significance and size of the move following that high or low is important... the basic smell test... what's the most obvious or outstanding high or low you probably can't go wrong with that" (`MyTradingSys/research/cross_trader_consolidated.md:370-372`, citing video `BHwoN7VPrBE` ~08:00; also `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:28-29`).
  - **Retest Optionality (C07-E01 / CT-035)**: "what you'll often see is this blanket statement that the market needs to retest x to confirm it as support resistance just forget it right i don't know i can't call this anything other than the notion because it's complete fiction... the significant event tends to be the break of structure itself it doesn't suddenly become magically valid if price decides to come back to it" (`MyTradingSys/research/cross_trader_consolidated.md:263-265`, citing video `inqHN8q57X4` ~06:15).
  - **Setup 1 - S/R Flip Continuation (C10-E01 / CT-025)**: "the long trade is taken on a pullback to the broken high... the short trade is taken on a pullback to the broken low... broken support turning to resistance on re-test broken resistance turning to support on a re-test" (`MyTradingSys/research/cross_trader_consolidated.md:409-410`, citing video `BHwoN7VPrBE` ~45:00).
  - **Setup 2 - Fib Pullback Continuation (C10-E04 / CT-032)**: "the continuation trade is taken below the breakout point but above the most recent low... i'll map out the low and then the higher high and then as the market starts pulling back it's between these levels that i'll look for structure... personally i look for support resistance structures anywhere between the 618 and 786 retracement... there's no fixed answer really" (`MyTradingSys/research/cross_trader_consolidated.md:428-431`, citing video `BHwoN7VPrBE` ~50:00, ~55:00).
  - **Setup 3 - Counter-trend / Defensive Rules (C10-E02 / CT-028)**: "if you're trading counter trend you're trading against the current so to speak and therefore you have to be more defensive and less liberal with those positions... shorter holding periods... greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5... different sizing is also another consideration... smaller or more conservative" (`MyTradingSys/research/cross_trader_consolidated.md:417-419`, citing video `BHwoN7VPrBE` ~33:00).
  - **Stop Placement / Invalidation Principle**: "stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation" (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:12`, citing video `XeQV2ECtZVQ:L33`).

---

## 2. PARAMETERS

### Swing Detection & Market Structure (`cc_structure.py`)
- `left: int = 2`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:12`). Fixed-width fractal choice; repo-chosen default.
- `right: int = 2`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:12`). Fixed-width fractal choice; repo-chosen default.
- `use_body: bool = True`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:12`). Compares candle bodies `max(o, c)` / `min(o, c)` instead of wicks.
- `require_prior_sequence: bool = True`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:68`, `MyTradingSys/research/cross_trader_consolidated.md:330-331`). Enforces sequence violation (lower-high broken by higher-high for bull MSB; higher-low broken by lower-low for bear MSB) per C08-E01.
- `filter_range_noise: bool = False`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:68`, `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:8-10`).
- `range_lookback: int = 50`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:47,68`, `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:23-25`).
- `range_extreme_pct: float = 0.25`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:47,68`, `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:23-25`). Proxies C08-E03 ("not noise" boundary); value is unsourced.

### Retest Classification (`cc_retest.py`)
- `tolerance_pct: float = 0.0015`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:18`). Price touch threshold `level * (1 +/- tolerance_pct)`.
- `invalidate_pct: float = 0.005`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:18`). Invalidation threshold before retest touch `level * (1 -/+ invalidate_pct)`.
- `expiry_bars: int = 200`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:18`). Maximum scan window for retest.
- `immediate_bars: int = 5`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:57`). Categorization threshold between immediate and rounded retest.

### Trade Setups (`cc_setups.py`)
- **Setup 1 (`setup1_sr_flip`)** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53-78`):
  - `stop_buffer_pct: float = 0.001`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:12-14`). Marked NO-SOURCE.
  - `target_r: float = 1.5`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:13-14`). Marked NO-SOURCE as fixed value (BHwoN7VPrBE:82 cites 1.5R as a minimum requirement, not a fixed target).
- **Setup 2 (`setup2_fib_pullback`)** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89-172`):
  - `fib_lo: float = 0.618`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/research/cross_trader_consolidated.md:428-431`). C08/C10-E04 quote: "structures anywhere between the 618 and 786 retracement".
  - `fib_hi: float = 0.786`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/research/cross_trader_consolidated.md:428-431`). C10-E04.
  - `stop_buffer_pct: float = 0.001`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:14,18`). Marked NO-SOURCE.
  - `target_r: float = 1.5`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:13,18`). Marked NO-SOURCE.
  - `expiry_bars: int = 200`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:90`). Limit validity timeout.
- **Setup 3 (`setup3_failed_msb_reversal`)** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178-220`):
  - `failure_lookback: int = 20`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178`). Window after break to observe failure to make a new extreme.
  - `stop_buffer_pct: float = 0.001`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:14,40`). Marked NO-SOURCE.
  - `target_r: float = 2.0`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178`, `MyTradingSys/research/cross_trader_consolidated.md:417-419`). C10-E02: counter-trend minimum R requirement "two reward for one risk instead of 1.5".

### Runner & Simulation Parameters (`run_cc_setups.py`)
- `tf: str = "1h"`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:353`). Trader quote on timeframes (CT-048): "I'll be trading high timeframe from the daily and weekly but a lot of my entries and management will be on the hourly timeframe" (`MyTradingSys/research/cross_trader_consolidated.md:515`).
- `is_frac: float = 0.70`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:73`). 70/30 chronological train/test split.
- `max_bars: int = 1440`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:356`). Max 1m bars a trade can stay open.
- `tick: float = 0.1`: **OURS (protocol)** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:102`, `MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:24`). BTCUSDT tick; the 1-tick trade-through rule is BACKTEST_PROTOCOL, not the trader.

---

## 3. BACKTESTS

### Run 1: L1-D3 075 CryptoCred Adapter Baseline (`2026-09-27`)
- **Report path**: `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37-64`
- **Fee-net or not**: Gross 5-bar forward return stats, plus simulated trades with default taker/maker fees without funding (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37-43,92-95`).
- **In-sample or out-of-sample**: NOT_IN_DATA for the CC adapter (the 70/30 split is stated only for the D3 RSI study, `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:7`); CC adapter on 1h bars (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37`).
- **n trades & results** (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`):
  - `setup1_sr_flip`: 2,517 signals, 500 sim trades (capped), h5 mean return +0.021%, hit rate 46.3%, sim win rate 51.2% (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`).
  - `setup2_fib_pullback`: 839 signals, 500 sim trades (capped), h5 mean return +0.006%, hit rate 52.1%, sim win rate 61.4% (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`).
  - `setup3_failed_msb_reversal`: 290 signals, 290 sim trades, h5 mean return +0.036%, hit rate 47.6%, sim win rate 33.4% (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`).

### Run 2: CC Setups Touch-Fill Model Rerun (`2026-10-07`)
- **Report path**: `MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:1-125`
- **Fee-net or not**: Net of fees, both with funding (7,305 records) and without funding (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:27-29`). Fee variants: `all_taker` and `maker_entry`.
- **In-sample or out-of-sample**: 70/30 chronological split (IS: 29,063 bars, OOS: 12,457 bars; 41,520 total 1h bars) (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:27`).
- **n trades & results** (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:33-140`):
  - `setup1_sr_flip`: 1,527 signals, 1,477 trades (50 unfilled limits); IS n=1,056, OOS n=421 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:33,52`).
    - `all_taker`: IS mean net R -1.0668 (-0.1067%), OOS mean net R -1.0683 (-0.1068%), Sharpe -0.883 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:37-38`).
    - `maker_entry`: IS mean net R -0.3802 (-0.0380%), OOS mean net R -0.3819 (-0.0382%), Sharpe -0.263 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:56-57`).
  - `setup2_fib_pullback`: 508 signals, 508 trades (0 unfilled limits); IS n=372, OOS n=136 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:71,90`).
    - `all_taker`: IS mean net R -0.3363 (-0.0659%), OOS mean net R -1.8558 (-0.0383%), Sharpe -0.112 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:75-76`).
    - `maker_entry`: IS mean net R 0.0167 (+0.0049%), OOS mean net R -0.7079 (+0.0331%), Sharpe 0.091 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:94-95`).
  - `setup3_failed_msb_reversal`: 167 signals, 167 trades (0 unfilled limits); IS n=119, OOS n=48 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:109,128`).
    - `all_taker`: IS mean net R -0.0431 (+0.1595%), OOS mean net R -0.2514 (-0.2976%), Sharpe -0.193 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:113-114`).
    - `maker_entry`: IS mean net R 0.0431 (+0.2201%), OOS mean net R -0.1745 (-0.2403%), Sharpe -0.155 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:132-133`).

### Run 3: CC Setups Trade-Through by 1 Tick Rerun (`2026-10-09`)
- **Report path**: `MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:144-245`
- **Fee-net or not**: Net of fees, funding included (7,305 records); both `maker_entry` and `all_taker` (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:146,168`).
- **In-sample or out-of-sample**: 70/30 chronological split (IS: 29,248 bars, OOS: 12,536 bars; 41,784 total 1h bars) (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:148,168`).
- **n trades & results** (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:154-245`):
  - `setup1_sr_flip`: 1,536 signals, 1,486 trades (50 unfilled limits); IS n=1,063, OOS n=423 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:158,172,190`).
    - `maker_entry`: OOS net -0.0380%, Sharpe -0.262, 0 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:154,195`).
    - `all_taker`: OOS net -0.1067%, Sharpe -0.881, 0 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:155,177`).
  - `setup2_fib_pullback`: 516 signals, 516 trades (0 unfilled limits); IS n=373, OOS n=143 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:159,209`).
    - `maker_entry`: OOS net +0.0416%, Sharpe 0.106, 1 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:156`).
    - `all_taker`: OOS net -0.0298%, Sharpe -0.080, 1 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:157,213`).
  - `setup3_failed_msb_reversal`: 167 signals, 167 trades; IS n=119, OOS n=48 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:160,225-245`).
    - `maker_entry`: OOS net -0.2403%, Sharpe -0.155, 1 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:160`).
    - `all_taker`: OOS net -0.2976%, Sharpe -0.193, 0 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:161`).

### Run 4: BigTrade Exit Policies Backtest (`2026-10-09`)
- **Report path**: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-56`
- **Fee-net or not**: Net of fees and slippage (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:12-14`).
- **In-sample or out-of-sample**: TRAIN (IS) vs VALIDATE (OOS) splits (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:20-56`).
- **Caveats in report** (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-3,7`): CONTAMINATED, DEV read VALIDATION 2024-07..12; TRAIN ran to 2025-01-01; VALIDATE is 2025-01..06 only; HOLDOUT 2025-07.. not read. DEV-only rerun: sr_flip:1h time_96_wide_stop_2atr TRAIN +9.8 bp (n 1024) -> +7.6 bp (n 878).
- **n trades & results** (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-56`):
  - `layer:cryptocred:failed_msb:15m`: TRAIN n=396, VALIDATE n=57 across 6 exit policies; mean returns negative in both splits across all policies (e.g. `live_like_1pct_2pct_8bars`: -8.0 bp TRAIN, -11.2 bp VALIDATE) (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-26`).
  - `layer:cryptocred:failed_msb:1h`: TRAIN n=109, VALIDATE n=17 across 6 exit policies (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:27-32`).
  - `layer:cryptocred:fib_pullback:15m`: TRAIN n=1,149, VALIDATE n=147 across 6 exit policies; all 6 policies negative in both splits (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:33-38`).
  - `layer:cryptocred:fib_pullback:1h`: TRAIN n=278, VALIDATE n=47 across 6 exit policies (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:39-44`).
  - `layer:cryptocred:sr_flip:15m`: TRAIN n=4,035, VALIDATE n=583 across 6 exit policies; all 6 policies negative in both splits (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:45-50`).
  - `layer:cryptocred:sr_flip:1h`: TRAIN n=1,024, VALIDATE n=163 across 6 exit policies; `time_96_wide_stop_2atr` policy recorded +9.8 bp TRAIN / +0.1 bp VALIDATE, while remaining 5 policies were net negative (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:51-56,143`).

### Run 5: BigTrade Fires Parity Check (`2026-10-09`)
- **Report path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16,24`
- **Fee-net or not**: Parity check only (firing agreement between offline detector and live engine alerts; no P&L) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16`).
- **In-sample or out-of-sample**: Last 5 days live comparison (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16`).
- **n trades & results**: Superseded perp run: parity 0-4% for cryptocred and fabio keys (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:15`). Spot rerun 2026-10-09: "All kline keys 92-100 % parity" (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:11`). No P&L.

### Run 6: Stop Placement & Parameter Sweep Study (`2026-10-10`)
- **Report path**: `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47-69`, `MyTradingSys/research/cryptocred_stop_2026-10-10/stop_sweep_result.json`
- **Fee-net or not**: Net R after costs on 1h bars (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47-49`).
- **In-sample or out-of-sample**: DEV / full archive dataset (`raw_1m_2022` 1h bars) (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47`).
- **n trades & sweep results** (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:51-65`):
  - `setup1_sr_flip` (n=1,487): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:52-57`):
    - `pct_0.1` (NO-SOURCE): net R -1.069, hit rate 0.373 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:52`).
    - `pct_0.25` (NO-SOURCE): net R -0.386, hit rate 0.406 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:53`).
    - `pct_0.5` (NO-SOURCE): net R -0.174, hit rate 0.411 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:54`).
    - `atr_1.0` (CC-invalidation): net R -0.162, hit rate 0.411 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:55`).
    - `atr_1.5` (CC-invalidation): net R -0.095, hit rate 0.421 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:56`).
    - `atr_2.0` (CC-invalidation): net R -0.101, hit rate 0.420 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:57`).
  - `setup2_fib_pullback` (n=1,392): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:58-61`):
    - `pct_0.1` (NO-SOURCE): net R -1.307, hit rate 0.306 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:58`).
    - `pct_0.5` (NO-SOURCE): net R -0.209, hit rate 0.367 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:59`).
    - `atr_1.0` (CC-invalidation): net R -0.184, hit rate 0.361 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:60`).
    - `atr_2.0` (CC-invalidation): net R -0.073, hit rate 0.405 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:61`).
  - `setup3_failed_msb_reversal` (n=167): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:62-65`):
    - `pct_0.1` (NO-SOURCE): net R -1.050, hit rate 0.317 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:62`).
    - `pct_0.5` (NO-SOURCE): net R -0.272, hit rate 0.305 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:63`).
    - `atr_1.0` (CC-invalidation): net R -0.217, hit rate 0.329 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:64`).
    - `atr_2.0` (CC-invalidation): net R -0.040, hit rate 0.371 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:65`).

### Run 7: Live Range Noise Neutrality Archive Replay (`2026-10-10`)
- **Report path**: `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:29-34`
- **Fee-net or not**: Net R after fees (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:14,30`).
- **In-sample or out-of-sample**: Archive replay (`Dumps/backtest/raw_1m_2022 + raw`, 1h) (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:14,30`).
- **n trades & results** (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:30-34`):
  - `setup1_sr_flip`: n=474 with flag vs n=1,477 without; mean net R -1.1351 with flag vs -1.0707 without (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:30-31`).
  - `setup3_failed_msb_reversal`: n=52 with flag vs n=167 without; mean net R -0.1504 with flag vs -0.1029 without (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:31-32`).
  - `setup2_fib_pullback`: passed neutrality check (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:32`).

---

## 4. KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (RULINGS)

- Ruling B143 (BLOCKED / MED) (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:1-8`):
  - Title: CryptoCred 0.1 percent stop buffer and 1.5R target are NO-SOURCE (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:1-8`).
  - Findings: Setup 1, 2, and 3 stops utilize a hardcoded 0.1% buffer (`cc_setups.py:53,89,178`), and setups 1 and 2 utilize a fixed 1.5R target (`cc_setups.py:53,89`), which are repo-invented numbers (NO-SOURCE) (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:12-14,40`).
- Ruling B145 (CLOSED / LOW) (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:1-8`):
  - Title: `classify_msb` `filter_range_noise` is off in the live CryptoCred layer; no evidence it is neutral or better (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:1-8`).
  - Receipt: Tested on archive replay; turning the flag on made net R worse for `setup1_sr_flip` and `setup3_failed_msb_reversal`; flag kept disabled (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:29-34`).
- Ruling B151 (CLOSED / MED) (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:1-8`):
  - Title: CryptoCred limit-fill backtest fills on touch and drops signals by a future event, so its PASS numbers are upper bounds; maker-entry fee refund applied on touch fills with a 0.1% stop (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:1-8`).
  - Receipt: Earlier PASS verdicts were artifacts of filling resting limits on mere touch and post-close bias (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:16-20`, `MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:13-17`). Fixed in runner by requiring trade-through by 1 tick (TICK=0.1) and surfacing `open_at_end` trades; on trade-through rerun, all setups fail net of fees (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:27-39`). Also fixed bear fib zone indexing bug where bear branches built descending zones preventing short signals from ever being emitted (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:37-40`).
- Ruling B154 (OPEN / MED) (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:1-8`):
  - Title: No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate number (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:1-8`).
  - Finding: CryptoCred backtest verdicts are reported as aggregate numbers across the entire dataset; no stratification by market regime (bull, bear, range) or session (e.g. US equity open, 12h boundaries) exists (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:17-21`).
- Historical Module Bug (BACKTEST_L1_REPORT) (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:50-64`):
  - `cc_setups.setup2_fib_pullback` originally indexed `swings[broken_swing_i]`, treating a bar index as a swings-list index, raising `IndexError` on real data (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:50-58`). Fixed in commit `54ad393` (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:60-64`).

---

## 5. CONFLUENCE

- Intended Confirmation Sources (Trader Spec) (`MyTradingSys/research/cross_trader_consolidated.md:280-395`):
  - CryptoCred explicitly specifies that MSB and structure setups require confluence from high-timeframe key levels, horizontal support/resistance, open prices (monthly, weekly, daily opens), funding rates, and open interest (`MyTradingSys/research/cross_trader_consolidated.md:375-385`, citing C09-E02 / CT-024, CT-030).
  - Timeframe confluence: Higher timeframe structure dominates lower timeframe moves; break validity requires close on the structure's anchor timeframe (`MyTradingSys/research/cross_trader_consolidated.md:280-285,389-395`, citing C07-E04 / CT-037, C09-E04 / CT-084).
- Repo Implementation State (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53,89,178`):
  - `cc_structure.py`, `cc_retest.py`, and `cc_setups.py` evaluate setups on isolated single-timeframe price series without multi-timeframe confirmation (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53,89,178`).
  - Confirmation from Tom (order flow / volume profile): NOT_IN_DATA.
  - Confirmation from Fabio (CVD absorption / escalation): NOT_IN_DATA.
  - Confirmation from RSI levels / divergence: NOT_IN_DATA.
  - Multi-layer combination in live alerts: Live alerts wire `cc_sr_flip_layer`, `cc_fib_pullback_layer`, and `cc_failed_msb_layer` as standalone event streams (`MyTradingSys/backtest/layers/alerts/live_layers.py:140-142`); no multi-layer confluence filter is active in code (`MyTradingSys/system/LAYERS.md:106-116`).
