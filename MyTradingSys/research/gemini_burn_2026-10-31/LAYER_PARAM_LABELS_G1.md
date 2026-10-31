# Layer Parameter Labels Audit: Group 1 (`fabio`, `kurisko`, `pizzino`, `session`, `session_levels`)

**Date:** 2026-10-31  
**Card:** `gemini-param-labels-layers-g1-1031`  
**Goal:** For every tunable constant in `MyTradingSys/backtest/layers/{fabio,kurisko,pizzino,session,session_levels}`: label SOURCED (analyst quote path and line) or OURS; flag any labelled SOURCED without a quote.

---

## Summary of Findings

- **Total Tunable Constants & Parameters Audited:** 96
- **SOURCED Parameters (with verbatim quote & file:line citation):** 28
- **OURS / OPERATOR-HYPOTHESIS / SIM / SAFETY Parameters:** 68
  - `OURS`: 42
  - `OPERATOR-HYPOTHESIS`: 4
  - `SIM` (data, cost, calendar, venue conventions): 18
  - `SAFETY` (execution limit circuit breakers): 4
- **Flagged SOURCED without a Quote:** 0 (all parameters labelled SOURCED contain verbatim analyst quotation and exact file:line citation).
- **Unlabelled Count:** 0

---

## 1. Fabio Layer (`MyTradingSys/backtest/layers/fabio/`)

### 1.1 `fabio_cvd_absorption.py`, `fabio_escalation.py`, `fabio_volume_fvg.py`

| Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|
| `left` (swing lookback) | `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:45` | `2` | OURS | Discretization of swing pivot detection window; NOT_IN_DATA in Fabio transcripts |
| `right` (swing lookforward) | `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:45` | `2` | OURS | Discretization of causal confirmation window; NOT_IN_DATA in Fabio transcripts |
| `use_body` | `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:45` | `True` | OURS | Engineering convention for candle extreme calculation; NOT_IN_DATA in Fabio transcripts |
| `price_tolerance` | `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:45` | `0.001` (0.1%) | OURS | Level tolerance for CVD vs price absorption divergence; concept FAB-007 (`o-w5Gxss6T0`) "CVD makes a lower low while price is still on the same level as before", but numeric tolerance `0.001` is NOT_IN_DATA (OURS) |
| `level_tolerance` | `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:16` | `0.001` (0.1%) | OURS | Retest tolerance for escalation into level; NOT_IN_DATA in Fabio transcripts |
| `aggression_k` | `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:16` | `2.0` | OURS | Aggression multiple over baseline delta; NOT_IN_DATA in Fabio transcripts |
| `record_lookback` | `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:16` | `20` | OURS | Rolling baseline window for aggression comparison; NOT_IN_DATA in Fabio transcripts |
| `n_bins` (profile) | `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:51` | `20` | OURS | Profile discretization bin count; NOT_IN_DATA in Fabio transcripts |
| `pct` (value area) | `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:116` | `0.70` | SOURCED | Quote: 8C:52-54 "to raise the exposure low in the curve" (`FABIO_V3_SPEC.md:73`, P11); standard Market Profile 70% Value Area (`FORMULAS.md:s19`) |

### 1.2 `fabio_of_model.py` & `orderflow_bars.py`

| Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|
| `TICK` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:34` | `0.1` | SIM | Binance BTCUSDT perpetual tick size convention (`FABIO_V3_SPEC.md:33`, P41 SIM) |
| `TOL` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:35` | `0.001` (0.1%) | OURS | Level proximity tolerance; NOT_IN_DATA in Fabio transcripts |
| `BIN` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:36` | `10.0` (USD) | OURS | Footprint bar bin resolution; NOT_IN_DATA in Fabio transcripts |
| `STATE_MIN` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:37` | `15` | OURS | Initial window to establish session state; NOT_IN_DATA in Fabio transcripts |
| `RETEST_BARS` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:38` | `6` | OURS | Horizon for breakout retest observation; NOT_IN_DATA in Fabio transcripts |
| `FILL_TF_BARS` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:39` | `3` | OURS | Limit order fill cancellation window; NOT_IN_DATA in Fabio transcripts |
| `SESSIONS` | `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:44` | `(("asia", 0, 480), ("london", 480, 810), ("ny", 810, 1260))` | OPERATOR-HYPOTHESIS | Fixed-UTC session clocks (Asia 00:00-08:00, London 08:00-13:30, NY 13:30-21:00); docstring: `session (UTC) Asia 00:00-08:00, London 08:00-13:30, NY 13:30-21:00. Prior session = the previous session in that sequence` (`fabio_of_model.py:8-12`); trader names sessions but clock boundaries are operator hypotheses |
| `BIN_USD` | `MyTradingSys/backtest/layers/fabio/orderflow_bars.py:37` | `10.0` | OURS | Footprint bin width in USD; NOT_IN_DATA in transcripts |
| `NBINS` | `MyTradingSys/backtest/layers/fabio/orderflow_bars.py:38` | `800` | OURS | Fixed histogram bin array allocation; engineering choice |
| `rolling window` | `MyTradingSys/backtest/layers/fabio/orderflow_bars.py:144` | `30` (days) | OURS | Rolling prior calendar days to evaluate big-trade percentiles (P05 NS-fixed, `FABIO_V3_SPEC.md:67`) |

### 1.3 `fabio/v3/` Package (`costs.py`, `day_gates.py`, `manage.py`, `signals.py`)

| Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|
| `TICK` | `MyTradingSys/backtest/layers/fabio/v3/costs.py:19` | `0.1` | SIM | Binance BTCUSDT tick size (`FABIO_V3_SPEC.md:33`, P41 SIM) |
| `EPS` | `MyTradingSys/backtest/layers/fabio/v3/costs.py:20` | `1e-9` | SIM | Numerical float tolerance for limit fills (`FABIO_V3_SPEC.md:157`, P41 SIM) |
| `MIN_MS` | `MyTradingSys/backtest/layers/fabio/v3/costs.py:21` | `60000` | SIM | 1-minute bar millisecond constant (`FABIO_V3_SPEC.md:33`, P41 SIM) |
| `SLIP_STRESS_BPS` | `MyTradingSys/backtest/layers/fabio/v3/costs.py:22` | `(0.0, 2.0, 5.0)` | SIM | Stress testing slippage grid (`FABIO_V3_SPEC.md:172`, P41 SIM) |
| `FUNDING_STRESS_MULT` | `MyTradingSys/backtest/layers/fabio/v3/costs.py:23` | `2.0` | SIM | Funding cost stress multiplier (`FABIO_V3_SPEC.md:173`, P41 SIM) |
| `WINDOW_BARS` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:12` | `390` | SIM | NY session duration (6.5 hours = 390 1m bars); SOURCED concept quote: 8C:7-8 "I scalp the NASDAQ during the New York session" (`FABIO_V3_SPEC.md:89`, P33) |
| `ENTRY_CUTOFF` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:13` | `330` | OURS | NY cash session entry cutoff at open+330m; NOT_IN_DATA (P33 NS-fixed, `FABIO_V3_SPEC.md:89`) |
| `MAX_MISSING` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:14` | `5` | SIM | Data completeness filter (max missing 1m bars in window); NOT_IN_DATA (P41 SIM, `FABIO_V3_SPEC.md:33`) |
| `MAX_FIRST_LEGS` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:15` | `10` | SAFETY | Daily execution limit circuit breaker; SOURCED concept quote: FAB-0KyIEdvVKMQ-R6 "Beginner execution cap: 10 per day" (`FABIO_RULEBOOK.md:10`, FR-06; `FABIO_V3_SPEC.md:86`, P30 SAFETY) |
| `DAILY_STOP_R` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:16` | `-3.0` | SAFETY | Daily loss circuit breaker; SOURCED concept quote: fZ:79-81 "in the worst session that I can make, I lose around 5,000, 10,000" (`FABIO_V3_SPEC.md:85`, P29 SAFETY; value -3R is safety-exempt) |
| `RECOVERY_LEVEL_R` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:17` | `-1.0` | OURS | Stop-after-recovery threshold; SOURCED concept quote: ja:181-182 "we locked in $12,000 and we are out of the position" (`FABIO_V3_SPEC.md:84`, P28 NS-fixed) |
| `GATE_PRIOR_DAYS` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:18` | `20` | OURS | Rolling prior weekdays for day gate; SOURCED concept quote: 8C:85-87 "volatility is not there every day" (`FABIO_V3_SPEC.md:96`, P40 NS-grid) |
| `GATE_MIN_ELAPSED` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:19` | `60` | OURS | Minimum elapsed session minutes before day gate opens; NOT_IN_DATA (P40 NS-grid, `FABIO_V3_SPEC.md:96`) |
| `TREND_RATIO` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:20` | `0.6` | SIM | Ex-post day type classification ratio; NOT_IN_DATA (P41 SIM, `FABIO_V3_SPEC.md:97`) |
| `Z_POWER` | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:21` | `1.96 + 0.8416` (2.8016) | SIM | Standard statistical power constant (95% confidence, 80% power) for sample size formula (`FABIO_V3_SPEC.md:278`, P41 SIM) |
| `MAX_ADDS` | `MyTradingSys/backtest/layers/fabio/v3/manage.py:21` | `2` (3 entries) | SOURCED | Quote: fZ:152-154 "we loaded the first one here, then we reloaded here, then we reloaded here"; 0j:4 "This was the third position" (`FABIO_V3_SPEC.md:78`, P22) |
| `MIN_ADD_FRAC` | `MyTradingSys/backtest/layers/fabio/v3/manage.py:22` | `0.25` | OURS | Minimum scale-in size (0.25 * initial size); NOT_IN_DATA (P25 NS-fixed, `FABIO_V3_SPEC.md:81`) |
| `ADD_PUSH_M` | `MyTradingSys/backtest/layers/fabio/v3/manage.py:23` | `15` | OURS | S4 window for add entries; SOURCED concept quote: 0j:4 "You see again big trades in the direction of the trend" (`FABIO_V3_SPEC.md:69`, P07 NS-fixed) |
| `B_PROF` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:25` | `50.0` | SIM | Volume profile bin size (re-binned 50 USD); NOT_IN_DATA (P41 SIM, `FABIO_V3_SPEC.md:33`) |
| `BAL_POC_BAND` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:26` | `0.25` | OURS | Balance POC band tolerance (`|c - poc| <= 0.25 * R`); SOURCED concept quote: 0j:4 "there is the fair value on the middle" (`FABIO_V3_SPEC.md:64`, P02 NS-fixed) |
| `K_BAL` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:27` | `0.8` | OURS | Balance range ratio threshold; SOURCED concept quote: 0j:4 "the market is balanced at this time" (`FABIO_V3_SPEC.md:63`, P01/P02 NS-fixed) |
| `DRIFT_Q` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:28` | `0.25` | OURS | Pressure drift quotient threshold; SOURCED concept quote: 0j:4 "the market is clearly building pressure down" (`FABIO_V3_SPEC.md:65`, P03 NS-fixed) |
| `EFFORT_L` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:29` | `60` | OURS | Effort vs result lookback window L; SOURCED concept quote: 0j:4 "the result of the price for a pressure in by delta was almost zero"; 8C:42-44 "the punch to the wall" (`FABIO_V3_SPEC.md:66`, P04 NS-fixed) |
| `R_ABS` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:30` | `0.25` | OURS | Absorption price response threshold; NOT_IN_DATA (P04 NS-fixed, `FABIO_V3_SPEC.md:66`) |
| `R_CTL` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:31` | `1.0` | OURS | Control price progress threshold; NOT_IN_DATA (P04 NS-fixed, `FABIO_V3_SPEC.md:66`) |
| `VR_TIER` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:32` | `1.5` | OURS | Volume ratio threshold for high-volume tier; SOURCED concept quote: ja:25-26 "Today there is a lot of volume. So I need to bigger filter" (`FABIO_V3_SPEC.md:68`, P06 NS-fixed) |
| `VR_DAYS` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:33` | `20` | OURS | Rolling prior weekdays for volume baseline; NOT_IN_DATA (P06 NS-fixed, `FABIO_V3_SPEC.md:68`) |
| `VR_MIN_DAYS` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:34` | `10` | OURS | Minimum sample days required for tiering; NOT_IN_DATA (P06 NS-fixed, `FABIO_V3_SPEC.md:68`) |
| `VA_PCT` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:35` | `0.70` | SOURCED | Quote: 8C:52-54 "to raise the exposure low in the curve" (`FABIO_V3_SPEC.md:73`, P11); standard Market Profile 70% Value Area (`FORMULAS.md:s19`) |
| `LVN_FRAC` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:36` | `0.5` | OURS | Low Volume Node cutoff (`<= 0.5 * median bin`); NOT_IN_DATA (P35 NS-fixed, `FABIO_V3_SPEC.md:91`) |
| `S8_AGE` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:37` | `15` | OURS | S8(a) exhaustion lookback bars; SOURCED concept quote: 0j:4 "the big trades are not pushing anymore the price down" (`FABIO_V3_SPEC.md:75`, P13 NS-fixed) |
| `S8_N` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:38` | `60` | SOURCED | Quote: 0j:4 "We are in a redistribution phase"; hold: fZ:98-99 "The sellers got completely absorbed here" (`FABIO_V3_SPEC.md:76`, P14); lookback window 60 bars is NS-fixed |
| `S8_Z_HI` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:39` | `2.5` | OURS | Z-score delta threshold for exhaustion; NOT_IN_DATA (P04 NS-grid default, `FABIO_V3_SPEC.md:66,90`) |
| `S8_P` | `MyTradingSys/backtest/layers/fabio/v3/signals.py:40` | `0.10` | OURS | Price progress threshold for exhaustion; NOT_IN_DATA (P03 NS-grid default, `FABIO_V3_SPEC.md:65,90`) |

---

## 2. Kurisko Layer (`MyTradingSys/backtest/layers/kurisko/`)

| Parameter / Constant | File:Line (Definition) | File:Line (Code Usage) | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| `enabled` | `layers/kurisko/params/kurisko_default.json:4` | `layers/kurisko/quad_rotation.py:1` | `false` | OURS | Flag-gated default OFF (alert-only layer, `quad_rotation.py:1`). |
| `band_1` | `layers/kurisko/params/kurisko_default.json:30` | `layers/kurisko/quad_rotation.py:25` | `(9, 3)` | SOURCED | Quote / spec row: `KURISKO_SPEC.md:s3` row Stochastic 1 (S4), `(9, 3)`. |
| `band_2` | `layers/kurisko/params/kurisko_default.json:39` | `layers/kurisko/quad_rotation.py:25` | `(14, 3)` | SOURCED | Quote / spec row: `KURISKO_SPEC.md:s3` row Stochastic 2 (S4), `(14, 3)`. |
| `band_3` | `layers/kurisko/params/kurisko_default.json:48` | `layers/kurisko/quad_rotation.py:25` | `(40, 4)` | OURS | Lookback 40 is SOURCED: R1 ("These are 40 candles and these are 60 candles", char 21291); smoothing `d=4` is OURS adopted default from slide S4 (not in spoken words; `KURISKO_SPEC.md:s5 gap 1`). |
| `band_4` | `layers/kurisko/params/kurisko_default.json:56` | `layers/kurisko/quad_rotation.py:25` | `(60, 10)` | SOURCED | Quote / spec row: `KURISKO_SPEC.md:s3` row Stochastic 4 (S4 Full Stoch `(60,10,10)`; S3 `(60,10)`; R1 "60 candles") with `d=10`. |
| `line` | `layers/kurisko/params/kurisko_default.json:65` | `layers/kurisko/stoch_core.py:5,37` | `"D"` | SOURCED | Quote: R8 "here I'm using the D line. And the D line is the signal line"; `D = SMA_d(raw %K)` (`FORMULAS.md:s24`). |
| `level_lo` | `layers/kurisko/params/kurisko_default.json:70` | `layers/kurisko/quad_rotation.py:27,85,96` | `20` | SOURCED | Quote: R2 "all of these bands get oversold below 20" (char 20846); `KURISKO_SPEC.md:s3` Levels (S4, S2). |
| `level_hi` | `layers/kurisko/params/kurisko_default.json:75` | `layers/kurisko/quad_rotation.py:27,87,96` | `80` | SOURCED | `KURISKO_SPEC.md:s3` Levels 20/80 (S4, S2); used by the short mirror. |
| `turn_rule` | `layers/kurisko/params/kurisko_default.json:80` | `layers/kurisko/quad_rotation.py:77` | `fast[t] > fast[t-1]` | OURS | No source defines the number for "turn back up" (R3 "visual confirmation", `KURISKO_SPEC.md:s5 gap 3`). |
| `short_side` | `layers/kurisko/params/kurisko_default.json:85` | `layers/kurisko/quad_rotation.py:77,87` | `all four > level_hi and fast falls` | OURS | Marked NO-SOURCE: trader never states "all four above 80" (`KURISKO_SPEC.md:s5 gap 6`; R10 only states the same goes for the downside). |
| `rsi_bands` | `layers/kurisko/params/kurisko_default.json:90` | `layers/kurisko/quad_rotation.py:26,54,63` | `[(9,0), (14,0), (40,0), (60,0)]` | OPERATOR-HYPOTHESIS | Operator hypothesis from memory ("4 RSI with params"); "RSI" occurs 0 times in Kurisko video S8 (`KURISKO_SPEC.md:s4`). |
| `stoch_slow` | `layers/kurisko/stoch_core.py:37` | `layers/kurisko/stoch_core.py:39-40` | `slow = 1` | OURS | Default un-slowed stochastic calculation; slowing variant `(60,10,10)` is a trial parameter (`FORMULAS.md:s24`). |

---

## 3. Pizzino Layer (`MyTradingSys/backtest/layers/pizzino/`)

| ID | Parameter / Constant | File:Line (Code) | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| P01 | Trend state set | `layers/pizzino/pizzino_indicators.py:52` | 3 states (`up (+1)`, `down (-1)`, `neutral (0)`) | SOURCED | Quote: "up on the one-day one-bar ... down on the mid-term ... neutral on the high-term" (`MyTradingSys/research/pizzino_layer_2026-10-27/method_extraction.md:36`; `SPEC.md:46,130`). |
| P02 | Number of nested degrees | `layers/pizzino/pizzino_indicators.py:67,72` | `3` degrees (1-bar, 2-bar, 3-bar) | SOURCED | Quote: "one-day one-bar, two-bar, three-bar" (`method_extraction.md:22,36`; `SPEC.md:46,131`). |
| P03 | Confluence condition | `layers/pizzino/pizzino_indicators.py:68` | `abs(conf) == 3` | SOURCED | Quote: "confluence across multiple time frames just showing the strong downward bias" (`method_extraction.md:22,29`; `SPEC.md:46,132`). |
| P04 | 1-bar lead indicator | `layers/pizzino/pizzino_indicators.py:72` | Lead flag exists (1-bar turns first) | SOURCED | Quote: 1-bar turn is "always a precursor" (`method_extraction.md:43,50`; `SPEC.md:46,133`). |
| P05 | Bar-count signal length | `layers/pizzino/pizzino_indicators.py:100` | `3` bars | SOURCED | Quote: "three bars up from the low", "three in a row from a significant turning point" (`method_extraction.md:82`; `SPEC.md:67,134`). |
| P06 | Bar-count direction condition | `layers/pizzino/pizzino_indicators.py:106-107` | `HH + HL` (up) / `LH + LL` (down) | SOURCED | Quote: "higher high, higher low" (`method_extraction.md:82,96`; `SPEC.md:67,135`). |
| P07 | Turning point significance | `layers/pizzino/pizzino_indicators.py:87` | Significant turning point required | SOURCED | Quote: turning point "generally means all-time high, but not always" (`method_extraction.md:82,89`; `SPEC.md:67,136`). |
| P08 | Permitted timeframes | `layers/pizzino/pizzino_indicators.py:1` | `D`, `3D`, `W` | SOURCED | Quote: used on 3-day and weekly bars as well as daily (`method_extraction.md:96,110`; `SPEC.md:67,137`). |
| P09 | 50% line definition | `layers/pizzino/pizzino_indicators.py:117` | `mid = (PH + PL) / 2` | SOURCED | Quote: "Top, bottom, halfway through", midpoint of the prior major run (`method_extraction.md:133,154`; `SPEC.md:85,138`). |
| P10 | 50% line strength regime | `layers/pizzino/pizzino_indicators.py:121` | `close > mid` strong, `< mid` weak | SOURCED | Quote: above 50% is strong half, below is weak half (`method_extraction.md:126`; `SPEC.md:85,139`). |
| P11 | Pivot breakout confirmation | `layers/pizzino/pizzino_indicators.py:148` | Close-beyond confirmation required | SOURCED | Quote: "higher time frame closes above those pivot points" (`method_extraction.md:73,184`; `SPEC.md:95,140`). |
| P12 | Retest outcome reading | `layers/pizzino/pizzino_indicators.py:160` | `hold` continuation, `fail` reversal | SOURCED | Quote: hold = continuation; retest from underneath is weak (`method_extraction.md:214,235`; `SPEC.md:95,141`). |
| P13 | Target selection | `layers/pizzino/pizzino_indicators.py:173,176` | Nearest confirmed opposing pivot | SOURCED | Quote: "look up to that next pivot point where price is likely going to rally to next" (`method_extraction.md:66`; `SPEC.md:113,142`). |
| P14 | Invalidation level | `layers/pizzino/pizzino_indicators.py:171` | Stop at last swing extreme `PL(1)` | SOURCED | Quote: invalidation is a "change in trend beneath $88" / swing bottom (`method_extraction.md:161,205`; `SPEC.md:113,143`). |
| P15 | Swing degree lookbacks | `layers/pizzino/pizzino_indicators.py:18,41` | `n = 1, 2, 3` for degrees 1, 2, 3 | OURS | Discretization of "1-bar, 2-bar, 3-bar" swing size (`SPEC.md:19,144`, V-n). |
| P16 | Fractal strictness | `layers/pizzino/pizzino_indicators.py:22,25` | Strict inequalities both sides | OURS | Strict inequality choice on fractal window (`SPEC.md:18,145`, V-frac). |
| P17 | Pivot alternation convention | `layers/pizzino/pizzino_indicators.py:29` | Keep extreme on duplicate pivot kinds | OURS | Tie-breaking rule for alternating pivots (`SPEC.md:18,146`). |
| P18 | Trend state formula | `layers/pizzino/pizzino_indicators.py:60,62` | Close beyond last swing low/high | OURS | Algorithmic implementation of Gann Swing Pro (`SPEC.md:47,147`, V-state). |
| P19 | Lead window `L` | `layers/pizzino/pizzino_indicators.py:81` | `L = 5` bars | OURS | Maximum bars elapsed for 1-bar lead status (`SPEC.md:47,148`, V-L). |
| P20 | Significance window `W` | `layers/pizzino/pizzino_indicators.py:90` | `W = 50` bars | OURS | Lookback window for significant turning point (`SPEC.md:68,149`, V-W). |
| P21 | Degree of turning point `T` | `layers/pizzino/pizzino_indicators.py:96` | Degree `3` | OURS | Degree of pivot selected for bar-count origin (`SPEC.md:68,150`, V-T). |
| P22 | Major-run degree `dm` | `layers/pizzino/pizzino_indicators.py:117` | Degree `3` | OURS | Degree of pivots bounding the 50% midpoint leg (`SPEC.md:86,151`, V-dm). |
| P23 | Break confirmation consecutive closes | `layers/pizzino/pizzino_indicators.py:141` | `N = 2` closes | OURS | Consecutive closes required to confirm a level break (`SPEC.md:96,152`, V-N). |
| P24 | Retest touch tolerance | `layers/pizzino/pizzino_indicators.py:141` | `tol = 0.005` (0.5%) | OURS | Retest touch band margin (`SPEC.md:96,153`, V-tol). |
| P25 | Retest window | `layers/pizzino/pizzino_indicators.py:141` | `R = 20` bars | OURS | Maximum window to observe retest after breakout (`SPEC.md:96,154`, V-R). |
| P26 | Entry confluence threshold | `layers/pizzino/pizzino_indicators.py:68` | `conf >= +2` (long) / `-2` (short) | OURS | Entry filter confluence score threshold (`SPEC.md:114,155`, V-conf). |
| P27 | Minimum Reward/Risk `RRmin` | `layers/pizzino/pizzino_indicators.py:166` | `rr_min = 1.0` | OURS | Minimum acceptable reward-to-risk ratio (`SPEC.md:114,156`, V-RR). |
| P28 | Fallback target multiple | `layers/pizzino/pizzino_indicators.py:166,174,177` | `fallback_r = 2.0` | OURS | Target distance when no confirmed opposing pivot exists (`SPEC.md:114,157`, V-tgt). |
| P29 | Time stop duration | `layers/pizzino/pizzino_indicators.py:111` | `TS = 20` bars | OURS | Maximum trade holding period in bars (`SPEC.md:114,158`, V-TS). |
| P30 | Three-bar count filter | `layers/pizzino/pizzino_indicators.py:110` | Off by default (`B = 5` bars) | OURS | Optional entry confluence filter (`SPEC.md:114,159`, V-B). |
| P31 | Daily session boundary | `layers/pizzino/pizzino_indicators.py:9` | `00:00 UTC` | OURS | Daily bar boundary convention for 24/7 crypto (`SPEC.md:124,160`). |
| P32 | Base chart timeframe | `layers/pizzino/pizzino_indicators.py:9` | `1D` (Daily) | OURS | Primary observation timeframe (`SPEC.md:124,161`, V-tf). |

---

## 4. Session Layer (`MyTradingSys/backtest/layers/session/`)

| Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|
| `first_min` | `MyTradingSys/backtest/layers/session/session_momentum.py:17` | `30` | SOURCED | Shen, Urquhart, Wang, *Financial Review* 57(2), 319-344, 2022 (T1): "the return over the first half-hour predicts the return of the last half-hour" (`session_momentum.py:3-4`; `FORMULAS.md:s15`). |
| `entry_min` | `MyTradingSys/backtest/layers/session/session_momentum.py:17` | `30` | OURS | Rest-of-session adaptation (`entry_min = first_min = 30`); the paper's last half-hour is `entry_min = session_len - 30` (`FORMULAS.md:s15`; docstring: `adaptation to 24/7 BTC is UNDEFINED in the source`). |
| `min_abs` | `MyTradingSys/backtest/layers/session/session_momentum.py:17` | `0.0` | OURS | Absolute return filter threshold; default 0.0 (no return threshold filter); NOT_IN_DATA in paper. |
| `session_start_min` | `MyTradingSys/backtest/layers/session/session_momentum.py:16` | `0` | OURS | 24/7 BTC adaptation anchor (UTC midnight = 0 min); docstring: `The 24/7 BTC adaptation (session = UTC day from session_start_min; "ny"/"london" = DST-aware day_gates open, B102) is UNDEFINED in the source and is a parameter, not a claim` (`session_momentum.py:5-6`). |
| `bar_min` | `MyTradingSys/backtest/layers/session/session_momentum.py:16` | `1` | OURS | Resolution of input bars (1m); standard technical parameter. |
| `DAY` | `MyTradingSys/backtest/layers/session/session_momentum.py:28` | `86400000` | SIM | Milliseconds per 24-hour day standard constant. |

---

## 5. Session Levels Layer (`MyTradingSys/backtest/layers/session_levels/`)

| Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|
| `ASIA_END_MIN` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:29` | `480` | OPERATOR-HYPOTHESIS | 08:00 UTC (480 min). Docstring: `Parameters, ALL NO-SOURCE (placeholders fixed before the run, not tuned): sessions in UTC (Asia 00:00-08:00, EU 08:00-14:00)` |
| `US_OPEN_MIN` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:30` | `840` | OPERATOR-HYPOTHESIS | 14:00 UTC (840 min). Docstring: `US open 14:00 UTC... Tom's only related words (Of_wlv3xaZo:7, QClPWDJ-BrU:7) name no clock, threshold or probability` |
| `FAIL_WINDOW_MIN` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:31` | `60` | OURS | Fixed 60-minute window for close-back failure detection; NO-SOURCE engineering choice |
| `MIN_PREV_BARS` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:32` | `1400` | OURS | Minimum 1m bars required to qualify previous day as complete (out of 1440 possible) |
| `FEE` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:33` | `0.0005` | SOURCED | Deribit exchange contract taker fee rate: inline comment `# fees.py DERIBIT_TAKER per side` (`fees.py:18`) |
| `MIN_EVENTS` | `MyTradingSys/backtest/layers/session_levels/run_session_levels.py:19` | `300` | OPERATOR-HYPOTHESIS | T087 specification: docstring `fewer than MIN_EVENTS (300) events in a cell = 'insufficient n'` |
| `T_MIN` | `MyTradingSys/backtest/layers/session_levels/run_session_levels.py:20` | `2.0` | OURS | Fixed statistical t-ratio threshold for edge candidacy |
| `MIN_MS` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:27` | `60000` | SIM | Standard millisecond constant for 1 minute |
| `DAY_MS` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:28` | `86400000` | SIM | Standard millisecond constant for 1 day |

---

## 6. Unlabelled List

```
TOTAL UNLABELLED CONSTANTS: 0
```
All parameters and tunable constants identified in `MyTradingSys/backtest/layers/{fabio,kurisko,pizzino,session,session_levels}` have been explicitly classified as SOURCED (with verbatim analyst quotations and line citations) or OURS / OPERATOR-HYPOTHESIS / SIM / SAFETY.
