Verdict: SOUND (The 13 executed trials in edge_hunt_2026-11-09 match their source reports, code, and CSV data; no look-ahead bias is present in feature evaluation or trade simulation; fee models rigorously account for venue taker/maker structures, 2 bps slippage, and funding rates; and the universal conclusion that zero trials passed the DEV screen is fully reproduced).

# Blind Review of Edge Hunt Study (edge_hunt_2026-11-09)

## 1. Headline Numbers Recount and Claim Verification

Every headline number in `MyTradingSys/research/edge_hunt_2026-11-09/EDGE_TABLE.md:9-23` was recounted against each worker's `RESULT.md` and associated CSV files.

| Id | Hypothesis | Claimed n | Recounted n | Claimed Mean Net R | Recounted Mean Net R | Claimed SE | Recounted SE | Claimed 95% CI | Recounted 95% CI | Claimed Verdict | Recounted Verdict | Match Status | Source Citation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T01 | 7-star spinning top, BTC+ETH 4h/1d | 108 | 108 | -0.217 | -0.217 | 0.150 | 0.150 | -0.511..+0.077 | -0.511..+0.077 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h1-spinning-top-7star/RESULT.md:1` |
| T02 | 7-star MTF long | 7 | 7 | +1.058 | +1.058 | 1.012 | 1.012 | -0.93..+3.04 | -0.93..+3.04 | INCONCLUSIVE | INCONCLUSIVE | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/RESULT.md:1` |
| T03 | 5-star MTF long | 8 | 8 | +0.072 | 0.072 | 0.509 | 0.509 | -0.92..+1.07 | -0.92..+1.07 | INCONCLUSIVE | INCONCLUSIVE | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/RESULT.md:1` |
| T04 | first-touch sweep-reclaim fade PDH/PDL/PWH/PWL | 1150 | 1150 | -0.221 | -0.2209 | 0.043 | 0.0432 | -0.305..-0.136 | -0.3055..-0.1363 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/RESULT.md:1` |
| T05 | fast-in short-time level fade, BTC 15m | 300 | 300 | -0.086 | -0.0858 | 0.081 | 0.0815 | -0.245..+0.074 | -0.245..+0.074 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/RESULT.md:1` |
| T06 | RSI14 cross of its SMA14, 4h BTC+ETH | 1322 | 1322 | +0.048 | +0.0484 | 0.040 | 0.0397 | -0.029..+0.126 | -0.0294..+0.1261 | INCONCLUSIVE | INCONCLUSIVE | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/RESULT.md:1` |
| T07 | Malkan 5-layer level short, BTC+ETH 4h | - | - | - | - | - | - | - | - | NOT RUN | NOT RUN | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/EDGE_TABLE.md:22` |
| T08 | T07 mirrored as a long | - | - | - | - | - | - | - | - | NOT RUN | NOT RUN | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/EDGE_TABLE.md:23` |
| T09 | HTF support wick long, BTC 15m | 41 | 41 | -0.581 | -0.5810 | 0.235 | 0.2351 | -1.042..-0.120 | -1.0417..-0.1202 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/RESULT.md:1` |
| T10 | HTF resistance wick short, BTC 15m | 47 | 47 | -0.804 | -0.8041 | 0.215 | 0.2151 | -1.226..-0.382 | -1.2257..-0.3825 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/RESULT.md:1` |
| T11 | RSI 40/60 bounce with MTF confluence | 1588 | 1588 | -0.146 | -0.1462 | 0.042 | 0.0417 | -0.228..-0.064 | -0.2280..-0.0644 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/RESULT.md:1` |
| T12 | T11 against HTF bias | 1477 | 1477 | -0.133 | -0.1331 | 0.044 | 0.0439 | -0.219..-0.047 | -0.2192..-0.0470 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/RESULT.md:1` |
| T13 | confluence score 0-5 slope (score>=3 n=410 -0.163) | 13851 | 13851 | - | - | - | - | slope +1.04, CI -0.91..+2.99 | slope +1.04, CI -0.91..+2.99 | INCONCLUSIVE | INCONCLUSIVE | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o1-confluence-dose-response/RESULT.md:1` |
| T14 | 1h level fade, balance phase | 358 | 358 | -0.232 | -0.2324 | 0.071 | 0.071 | -0.371..-0.094 | -0.371..-0.094 | FAIL | FAIL | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/RESULT.md:1` |
| T15 | MLK-S1 4h RSI-40 long, accumulation/bull | 51 | 51 | +0.016 | +0.0164 | 0.247 | 0.247 | -0.467..+0.500 | -0.467..+0.500 | INCONCLUSIVE | INCONCLUSIVE | MATCH | `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/RESULT.md:1` |

All headline numbers across T01-T15 in `EDGE_TABLE.md` match the underlying result logs and CSV files exactly.

---

## 2. Look-Ahead Hunt

We examined feature construction, multi-timeframe aggregation, signal detection, and entry execution across all trial code.

### Findings by Feature / Study:
1. **T01 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h1-spinning-top-7star/spinning_top.py:186-218`)**:
   - The spinning top candle is evaluated at bar `i` close using highs, lows, opens, and closes up to bar `i`. Volume is compared against the median of bars `i-20..i-1`.
   - Entry orders (buy/sell stop) are placed for execution on bars `i+1..i+3` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h1-spinning-top-7star/spinning_top.py:218`).
   - No bar after the decision bar is used in feature calculation.

2. **T02 & T03 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/star_grades.py:112-140`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/star_grades.py:236-285`)**:
   - Higher timeframe RSI metrics (monthly, weekly) are aggregated strictly using historical bars closed prior to signal timestamp `t` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/star_grades.py:84-110`).
   - Signal is formed at the close of daily bar `i`. Trade execution takes place on the next day open `i+1` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/star_grades.py:270-280`).
   - No look-ahead detected.

3. **T04 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/first_touch.py:100-145`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/first_touch.py:175-205`)**:
   - Prior day / prior week highs and lows (PDH/PDL/PWH/PWL) are calculated strictly on completed calendar periods.
   - Touch and reclaim sequence requires breach at bar `t`, reclaim close at bar `r` (`t <= r <= t+3`), with entry at the close of bar `r`.
   - Trade simulation executes across subsequent bars `r+1..r+96` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/first_touch.py:210-235`). No future bars are read during signal detection.

4. **T05 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:220-250`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:287-318`)**:
   - Speed is computed using bars `t-12..t` prior to the level touch at bar `t`.
   - `time_trade` evaluates time at level between touch `t` and reclaim bar `r` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:296`).
   - Note on descriptive exploratory feature: `time_desc` evaluates `t..t+7` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:297`) which uses bars after entry. However, the author explicitly quarantined this to exploratory analysis and used strictly `time_trade <= 2` for frozen trial T05 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:314-318`). The frozen trial has zero look-ahead.

5. **T06 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/rsi_ma_cross.py:75-130`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/rsi_ma_cross.py:133-188`)**:
   - RSI14 and SMA14 are computed strictly up to signal bar `i`.
   - Trade entry occurs at bar `i+1` upon confirming price action (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/rsi_ma_cross.py:150-165`).
   - No look-ahead detected.

6. **T09 & T10 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/wick_context.py:180-245`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/wick_context.py:280-360`)**:
   - Swing extremes and HTF levels are established on completed bars. Volume median uses preceding 20 bars.
   - Limit order is placed at the level at the reclaim bar close, active for bars `r+1..r+4` with strict fill condition (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/wick_context.py:320-335`).
   - No look-ahead detected.

7. **T11 & T12 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/line_confluence.py:120-185`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/line_confluence.py:270-325`)**:
   - Multi-timeframe RSI lines {1h, 4h, 12h, 1d} are sampled using only completed candles at or before the 1h/4h bounce candle close (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/line_confluence.py:140-160`).
   - Entry occurs at the close of the bounce confirmation bar.
   - No look-ahead detected.

8. **T13 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o1-confluence-dose-response/confluence_score.py:150-250`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o1-confluence-dose-response/confluence_score.py:300-360`)**:
   - Confluence layers (0-5) evaluate level presence, RSI-MA trigger, wick divergence, HTF RSI, and volume at the decision bar.
   - Entries and exits execute strictly forward in time.
   - No look-ahead detected.

9. **T14 & T15 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_trials.py:144-220`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_label.py:45-120`)**:
   - `PhaseLabeler` consumes closed daily bars up to timestamp `t` (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_label.py:140-180`).
   - T14 level sweeps evaluate PDH/PDL from the completed prior day; entry is at reclaim close, exit simulated on subsequent bars (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_trials.py:160-180`).
   - T15 evaluates MLK-S1 RSI-40 bounce on 4h bars; entry simulated at next bar open (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_trials.py:280-315`).
   - No look-ahead detected.

---

## 3. Fee and Slippage Hunt

We audited fee models, trading regimes, order sides, and round-trip cost calculations across all study code.

### Fee Regimes:
1. **Regime A (Market / Taker Entry and Exit)**:
   - Base fee: `fees.DERIBIT_TAKER = 0.0005` (5 bps per side, 10 bps round-trip).
   - Slippage: `fees.SLIPPAGE_RT_S13 = 0.0002` (2 bps round-trip).
   - Total base cost: 12 bps round-trip (`FEE_RT_BPS = 12.0`).
   - Expressed in R-multiples: `fee_r = (0.0012) / stop_fraction`.
   - Used in: T01, T02, T03, T04, T05, T06, T11, T12, T13, T14, T15.
   - Verified code citations: `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h1-spinning-top-7star/spinning_top.py:35-37,162-164`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/star_grades.py:42-44,132-134`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/first_touch.py:73-74`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:144-145`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/rsi_ma_cross.py:25-28`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/line_confluence.py:257-263`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o1-confluence-dose-response/confluence_score.py:35-40`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_trials.py:36-38`.

2. **Regime B (Maker Limit Entry and Target, Taker Stop)**:
   - Maker entry / target fee: 0 bps (`fees.FEES_DERIBIT['target'] = 0.0`).
   - Taker stop / timeout fee: 5 bps (`fees.FEES_DERIBIT['stop'] = 0.0005`) plus 1 bp taker slippage (`SLIP_TAKER_BPS = 1.0`).
   - Exit cost: 0 bps if target reached; 6 bps if stopped out.
   - Used in: T09, T10 (`MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/wick_context.py:127-139`).

3. **Funding Cost Accounting**:
   - All perp studies (T04, T05, T09, T10, T14, and futures portions of pooled studies) sum historical 8-hour funding rates over the exact holding window `t_entry < t <= t_exit`.
   - Longs pay positive funding; shorts receive positive funding.
   - Sign convention verified: `funding_r = side * sum(funding_rates) / stop_fraction`.
   - Verified in: `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/first_touch.py:237-241`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/speed_time.py:190-195`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-s2-wick-level-context/wick_context.py:370-376`, `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-o2-phase-lens/phase_trials.py:80-95`.

4. **Audit for Errors**:
   - Double counting: None detected.
   - Missing fees: Spot history before 2019-09 correctly omits perp funding where contracts did not exist, but charges full spot trading fees.
   - Wrong side: Stop losses correctly pay taker fees across all regimes; limit orders strictly enforce the through-tick rule for fills.

---

## 4. Final Review Verdict

**Verdict: SOUND**

The research in `MyTradingSys/research/edge_hunt_2026-11-09` is technically rigorous, reproducible, free of look-ahead artifacts in its frozen trials, and handles transaction costs accurately. The headline conclusion that zero tested hypotheses demonstrated a positive trading edge on the DEV split is completely verified.
