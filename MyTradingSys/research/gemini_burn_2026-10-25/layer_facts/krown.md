# Layer Fact Sheet: krown

Family: `krown` (Krown: TA 101: zones, volume, candles, averages, ranges)  
Source files: `MyTradingSys/system/LAYERS.md`, `MyTradingSys/system/layer_index.json`, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md`, `MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md`, `MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md`, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md`, `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md`.  
Status note: Repo files record that detectors are not built and no strategy backtest has been run (`MyTradingSys/system/LAYERS.md:222`, `MyTradingSys/system/layer_index.json:426`).

---

## 1. ORIGIN

- **Analyst / Indicator**: Eric Krown (@ECKrown / "Crown", Krown Trading) (`MyTradingSys/options/research/KROWN_FREE_VS_PAID.md:1`).
- **Core Teaching / Scope**: Swing and context method for the daily and weekly chart on BTC/crypto (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:8-12`).
- **Source Corpus**: Spec v0.2 and 120-rule ledger from 15 of 19 reachable TA 101 YouTube videos (14 TA + 1 fees) (`MyTradingSys/system/LAYERS.md:222`, `MyTradingSys/system/layer_index.json:426`).
- **Quoted Origin Concepts**:
  - Timeframe / Market: SOURCED: "daily is the gold standard for most cryptos" (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:31`, citing `extract__t_XIBrcjRk.md:115-122`).
  - Bar Close: SOURCED: "00:00 UTC" (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:31,41`, citing `KR-T04`).
  - Core Principle on Breaks: SOURCED: "Only a close beyond the zone breaks a level. No close outside. We don't call it broken. Period." (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:1034-1036`, citing `qEfES84jwwo | END | t=00:30:46`).
  - Zone Definition: SOURCED: zone = [close, wick extreme] of a pivot bar ("wick-to-close", KR-Z01) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`).
  - Range Noise: SOURCED: "The middle, that's your no man's land. No memory, no zone, no edge." (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:1017-1019`, citing `6aA-P4Gvhrc | BEGIN | t=00:06:08`).
  - Confluence: SOURCED: "when you align these things they become infinitely more powerful" (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:1042-1044`, citing `8MvxK_nxO-0 | END | t=00:29:10`).

---

## 2. PARAMETERS

Parameters compiled per component from `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:39-52`:

- `tf` module:
  - Bar close timestamp: `00:00 UTC` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:41`, citing rule `T04`).
  - Target timeframes: `1w, 1d, 6h, 4h` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:31,41`, citing rule `KR-T08`).
  - Week start convention: `Monday 00:00 UTC` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:41`).

- `swings` module:
  - Swing definitions: dominant-low and dominant-lower-high definitions; reversal = trade and close beyond the dominant level; one-bar peaks ignored; confirm on the next reversal close (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:42`, citing rules `L10, L01, Z05`).
  - Swing lookback parameter: `k bars each side {2,3,5}` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:42`).
  - Filtering parameters: size of a "one-bar peak", swings on closes vs highs/lows, "about the same" range tolerance (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:42`).

- `zones` module:
  - Zone boundaries: `wick-to-close` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z01`).
  - Turn threshold: `>= 2 turns` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z02`).
  - Maximum active zones: `max 5` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z03`).
  - Maturity threshold: `> 3 tests mature` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z13`).
  - Heavy-volume anchor flag: `2x volume` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z04`).
  - Trend direction: `levels work with the trend` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z17`).
  - Reaction size threshold: reaction size to count a turn, grid in ATR units (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`).
  - Ranking & recency: ranking weights, "recent" for touches (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:43`, citing rule `Z18`).

- `volume` module:
  - Baseline MA period: `SMA 20` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`, citing rule `V01`) or `30-day` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`, citing rule `TOP-05`).
  - Expansion multiplier: `2x` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`, citing rule `V02`).
  - Low volume observation: `0.5 observation` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`, citing rule `V10`).
  - Same-slot baseline: same-slot baseline as second arm (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`).
  - Breakout threshold grid: `grid {1.0, 1.25, 1.5}x` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`).
  - Baseline comparison window: `20 vs 30 vs 60` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:44`, citing conflict `C10`).

- `vol_regime` (BBWP) module:
  - Basis length: `7` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing rule `Q01`).
  - Lookback: `100` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing rule `Q01`).
  - Source series: `close` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing rule `Q01`).
  - Expansion / High threshold: `high >= 85` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing rule `Q02`).
  - Compression / Low threshold: `low <= 25-35` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing rule `Q02`).
  - Rebound / Confirmation threshold: `confirm > 50` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing rule `Q02`).
  - Bollinger Band multiplier: `band multiplier 2` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`).
  - Percentile formula & threshold grid: exact percentile formula, grid `{80, 85, 90} x {25, 30, 35}` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:45`, citing conflict `C13`).

- `candles` module:
  - Strict engulfing definition: engulfing definition (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:46`, citing rule `C06`).
  - Confirmation condition: confirm = close beyond pattern wick (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:46`, citing rule `C08`).
  - Pattern horizon: `3-5 bars` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:46`, citing rule `C03`).
  - Three black crows count: `three down bars from the high` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:46`, citing rule `C11`).
  - Candle shape thresholds: wick-to-range ratio for "big wick", body ratio for doji, "exact low" lookback (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:46`).

- `mas` (Moving Averages) module:
  - Moving average periods: `EMA 5, 21, 55, 377` and `SMA 50, 200` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:47`, citing rules `M01, M09, M07`).
  - Weekly trend bias: weekly 55 EMA bias (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:47`, citing rule `M10`).
  - Touch & slope parameters: "long time away" N days, slope thresholds, touch tolerance (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:47`).

- `rsi` module:
  - Overbought level: `70` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:48`, citing rule `S02`).
  - RSI regime zones: `zones 40/60 and 40-80/20-60` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:48`, citing rule `S03`).
  - Divergence definitions: regular and hidden divergence definitions (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:48`, citing rule `S05`).
  - RSI calculation period: `period 14` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:48`).
  - Thresholds & lookback: oversold level, divergence lookback and spacing (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:48`).
  - MACD parameters: `(12, 26, 9)` (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:48`).

- `range` module:
  - Range bounds: edges only (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:49`, citing rule `R01`).
  - Breakout rule: close breaks (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:49`, citing rule `Z07`).
  - Measured target: range height projection (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:49,58`, citing rule `R07`).
  - Range tightness: compression/tightness score thresholds, flat-MA slope threshold (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:49`).

- `topdown` module:
  - Hierarchy roles: `1w tide, 1d decide, 4h/6h timing` (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:50`, citing rule `T03`).
  - Trend state definition: state from dominant levels (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:50`, citing rule `KR-L10`).
  - Extra parameters: none beyond L10's (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:50`).

- `tops` module:
  - Four-signal combination: `3 of 4` within "a few bars" on weekly/monthly (reversal candle, extreme volume 2x 30-day average, BBWP > 85, RSI divergence or MACD cross) (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:51`, citing rules `P01, V02, Q02`).
  - Top cluster window: `"a few bars" {2,3,4}` and selection of which 3 of 4 (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:51`).

- Setup-specific Stop & Target parameters:
  - Structural stop (Vol-compression breakout S8): far side of compression zone, a close beyond it (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:16,64`, citing rule `Q05`); distance beyond it (OURS, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:64`).
  - Sourced exit (Vol-compression breakout S8): take profit as volatility peaks (BBWP in 90s, reversal candle on high volatility, volatility losing its average) (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:64`, citing rule `Q06`).
  - Scale-out at tops (S9): 20-85% scale-out (SOURCED, `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:17,65`, citing rule `P02`).
  - General stop distance & risk per trade: NOT_IN_DATA (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:18,69-70`: "A stop DISTANCE for any setup, risk per trade, hold time...").

---

## 3. BACKTESTS

- **Formal Layer Backtest Status**:
  - `MyTradingSys/system/LAYERS.md:222`: "Detectors not built, not backtested."
  - `MyTradingSys/system/layer_index.json:426`: "Detectors not built, not backtested."
  - `MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:4-5`: "Detectors and the recall check (items 3) are allowed before this is complete; no P&L backtest is."
  - Number of backtest trades on Krown strategy: `0` / NOT_IN_DATA (`MyTradingSys/system/LAYERS.md:222`).

- **Related Exploratory Study (Candle-Close Screen)**:
  - Report path: `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md` (listed under `results` for krown family in `MyTradingSys/system/layer_index.json:442`).
  - Nature: Exploratory price-return screen on candle-close sequences (borrowing Krown's close-through, reclaim, and retest definitions; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:86`).
  - Fee-net status: Evaluated with a fixed 14 bp round-trip cost screen (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:3,13`).
  - Sample span: DEV sample only: January 2022 – June 2024 (912 days, 1,313,280 Binance BTCUSDT perpetual 1m bars; `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:7`).
  - Out-of-sample: "Validation July 2024 onward and holdout were not opened." (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:8`).
  - Number of observations (n): 105,541 correlated event rows across 126 pooled arms (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:3,8`).
  - Outcome: "0 of 126 pooled arms pass the frozen exploratory screen. No validated tradable edge established." (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:3`).
  - Direct attribution note: "Current source identity is NOT_IN_DATA; Krown sources are relevant definitions only." (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:71`).

---

## 4. KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (RULINGS)

- **Formal lab rulings**:
  - `python scripts/dev/lab_query.py rulings krown` returns `{"family": "krown", "rulings": []}`. No formal rulings logged under `krown`.
- **Repo-documented Assumptions & Gaps**:
  - No resting stop / no stop loss: Krown states "I do not like stop losses" (`MyTradingSys/research/krown_ta101_2026-10-13/reflexivity_log.md:12`, rule `SNR-21`); conflicts with house rule requiring protective stops (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:70-71`, conflict `C3`).
  - Stop distance: No numerical stop distance exists in the corpus (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:18,69-70`; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:27-28`).
  - Analyst statistics as unverified claims: Krown's self-reported numbers (e.g. 90-95% right side of trend, 80-95% for 21/55 cross, 5,284 candles, 82% 5 EMA reconnect, 26 years / 80 touches on 200W SMA) are unverified claims classified as T3 hypotheses to test, not established facts (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:72-74`; `MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md:26`).
  - Volume baseline conflict: Krown states plain 20-period SMA volume 2x spike, whereas repo lessons show plain relative volume acts as a time-of-day clock for BTC; requires testing both SOURCED (plain SMA20) and OURS (same-slot baseline) arms (`MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md:28`, conflict `C5`).
  - Volume venue: Krown specifies reading Coinbase, TradingView index, or CME volume; Binance volume is used in repo data; Coinbase/index volume is NOT_IN_DATA (`MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:32-34`, conflict `C6`).
  - Ground truth trade ledger: TA 101 consists of lecture illustrations rather than a chronological trade ledger; no entry/stop/target triplets stated; ground truth is NOT_ANSWERED (`MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:14-19`).
  - Saturation condition unmet: Only 14 TA videos extracted of 19 reachable (37 total, 18 hidden); the 20-video saturation gate is unmet (`MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md:17`; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:25-26`).

---

## 5. CONFLUENCE (OTHER LAYERS)

Cross-layer confirmation and alignment recorded in repo files:

- **Confirmed by / Confirms (Cross-Trader Overlap)** (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:978-999`):
  - With **Tom** (`tom`):
    - `KR-S1` (Zone test) aligns with `TOM-15` (S/R area first, then candle formation; STRONG overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:980`).
    - `KR-S2` (Break-close) aligns with `TOM-6` (Breakout of balance/zone judged on close with volume; STRONG overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:982`).
    - `KR-S3` (Range-edge) aligns with `TOM-2` (Sell top, buy bottom of balance, middle is noise; STRONG overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:983`).
    - `KR-S3` (Fake-out return) aligns with `TOM-12` (Poke outside balance, fail, return inside; STRONG overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:984`).
    - `KR-S3` (Range scalp) aligns with `TOM-7` (Short top, long bottom of range around flat VWAP; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:986`).
    - `KR-S4, KR-S8` (Compression breakout) aligns with `TOM-15, TOM-6` (Compression before breakout; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:987`).
    - `KR-S5` (MA pullback) aligns with `TOM-4` (Rising average used as pullback line; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:989`).
    - `KR-S9` (Top selling) aligns with `TOM-16` (Extreme volume at high, sellers take over; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:990`).
    - `KR-S13` (Effort vs result) aligns with `TOM-2` (viT trade absorption; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:993`).
    - `KR-S16` (Volatility extreme fade) aligns with `TOM-1` (Fade overextended move; PARTIAL overlap, paraphrase) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:996`).
  - With **Fabio** (`fabio`):
    - `KR-S1` (Zone test) aligns with `FAB-5` (Level defended repeatedly; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:981`).
    - `KR-S3` (Poke and return) aligns with `FAB-4` (Probe out of balance returning inside; STRONG overlap, paraphrase) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:985`).
    - `KR-S4, KR-S8` (Compression breakout) aligns with `FAB-1` (Flat balance followed by volume breakout; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:988`).
    - `KR-S13` (Effort vs result) aligns with `FAB-2, FAB-5` (Volume/delta effort with no price progress = absorption; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:992`).
  - With **Malkan / RSI** (`rsi`):
    - `KR-S9` (Top momentum leg) aligns with `MAL-16` (Bearish RSI divergence; PARTIAL overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:991`).
    - `KR-S14` (Regular divergence) aligns with `MAL-14, MAL-16, MAL-17` (Regular divergence; STRONG overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:994`).
    - `KR-S14` (Hidden divergence) aligns with `MAL-7, MAL-8, MAL-9` (Hidden divergence continuation; STRONG overlap, quoted-both-sides) (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:995`).
    - RSI 40/60 regime (`KR-S03`) matches the `rsi_levels` 40/60 study (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:89`).
  - With **CryptoCred** (`cryptocred`):
    - `KR-Z09, KR-Z10` overlap strongly with CryptoCred S/R flip + retest (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:88`).
  - With **Moving Averages** (`ma_daily`):
    - Krown supplies SOURCED numbers (21/55 EMA, 50/200 SMA, 5 EMA, 377 EMA, 200W SMA; `KR-M01..M10`) replacing unsourced chatbot handoff numbers (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:84`).
  - With **Candle Patterns** (`candle_patterns`):
    - Strict engulfing and "exact low" location provide context for testing candle patterns (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:85`).
  - With **Positioning & Liquidation Cascades** (`positioning`):
    - Sourced concepts `KR-LQC01..LQC04` act as context/regime and execution risk filters: hot funding and high open interest define cascade vulnerability where sizing is throttled and liquidation prices avoid pool clusters (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:93-96`).
- **Setups with No Overlap in Repo**:
  - `KR-S6` (5 EMA leash), `KR-S7` (Capitulation hammer), `KR-S10` (Trendline first return), `KR-S11` (Trendline break & higher low), `KR-S12` (Dominant-level reversal), `KR-S15` (200-week SMA) have no overlap with Tom, Fabio, or Malkan rows (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:998-1000`).

---
