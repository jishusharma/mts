# Pre-registration: Positioning C1 (NO-SOURCE Research Test, PRE_REG_TEMPLATE.md)

Date: 2026-10-18. Card: `positioning-c1-prereg-no-source`. Checklist: `research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md` section 6 (template: `backtest/PRE_REG_TEMPLATE.md`).
No P&L backtest run; no tuning; edits to live-path code out of scope.
Provenance rule: Every parameter and number is explicitly labelled SOURCED (quote + file:line) or OURS (engineering / design choice). All C1 parameters and empirical DEV numbers are OURS.

---

## 0. Pre-build gate (items 0a-0f; decision q13, 2026-10-14: adopted, "be flexible")

- 0a Cost: Smallest stop or target this idea uses? On BTC fees stay under 0.25 R only with a stop of at least 0.40 % (taker legs) or 0.20 % (maker entry) [SOURCED PRE_REG_TEMPLATE.md:12]. C1 is a pure time-exit strategy holding 48 15m bars (12.0 hours) [OURS, COUNT_POWER.md:88-94], with no fixed stop-loss order in the market. Taker cost model is Binance USDT-M taker fee 10 bps RT + 2 bps slippage = 12 bps (0.12 %) round trip [SOURCED run_t055.py:9; FORMULAS.md:364]. Per-trade noise standard deviation on BTC 15m is 1.31 % [SOURCED HOME_FIT_AUDIT_POSITIONING.md:85; COUNT_POWER.md:19]. In noise units, round-trip transaction cost is 0.12 % / 1.31 % = 0.0916 R [OURS, COUNT_POWER.md:24]. At 48 bars, empirical mean gross moves across the 6 passing cells range from +0.253 % to +0.341 % [OURS, COUNT_POWER.md:88-94], which represent 2.1x to 2.8x round-trip cost (12 bps). If an operational disaster stop is placed at 1.5x ATR (~1.96 % at 1.31 % sd) [OURS], fee share of R is 0.12 % / 1.96 % = 0.061 R (6.1 % of R < 0.25 R) [OURS]. Gate 0a passes.
- 0b Gross: Does a cheap fixed-horizon check on existing data show a raw move of at least 2x the round-trip cost? Yes. 2x round-trip cost on BTC is 24 bps (0.240 %) [SOURCED PRE_REG_TEMPLATE.md:13; COUNT_POWER.md:15]. On the 30-month DEV window (2022-01-01 to 2024-06-30, 87,552 15m bars), a count-only check on the 36 grid cells of `run_t055.c1_grid()` established that 6 cells with `use_divergence: True` at horizon 48 bars (12 hours) exceed the +0.240 % threshold [OURS, COUNT_POWER.md:56-70, 88-94]: (1) lookback 180, n 50, hi/lo 99/1: gross 48b = +0.341 % (N = 352) [OURS]; (2) lookback 180, n 20, hi/lo 95/5: gross 48b = +0.308 % (N = 1163) [OURS]; (3) lookback 90, n 50, hi/lo 95/5: gross 48b = +0.273 % (N = 682) [OURS]; (4) lookback 90, n 50, hi/lo 99/1: gross 48b = +0.271 % (N = 425) [OURS]; (5) lookback 180, n 20, hi/lo 99/1: gross 48b = +0.255 % (N = 677) [OURS]; (6) lookback 180, n 50, hi/lo 95/5: gross 48b = +0.253 % (N = 600) [OURS]. At 4 bars (1h) and 16 bars (4h), 0 of 36 cells pass [OURS, COUNT_POWER.md:97-98]. Gate 0b passes at 48 bars for these 6 pre-registered candidate cells.
- 0c Record: Does the source have dated calls or trades we can score on BTC data? No dated trader calls or trades exist in repo data or literature [SOURCED HOME_FIT_AUDIT_POSITIONING.md:32-34; LEDGER_FEASIBILITY.md:1-25]. C1 is NOT a trader-sourced layer; it is an engineering encoding of a literature hypothesis (Memon 2026 funding reversion + CVD divergence) with zero trader trades [SOURCED HOME_FIT_AUDIT_POSITIONING.md:9-15]. Per Gate 0c and PROJECT_VISION.md exception 2 [SOURCED PROJECT_VISION.md:238-242], C1 is classified as a NO-SOURCE research test (hypothesis-only), NEVER a core layer. It may run strictly as a labelled research backtest, never as a live layer. Gate 0c is satisfied via exception 2.
- 0d Data: Does BTC history hold every input the source reads? Yes. C1 reads 15m OHLCV bars with taker-buy volume (aggressor proxy, CVD = 2*tbv - v) and 8-hour funding rates [SOURCED FORMULAS.md:364; funding_cvd_fade.py:48; HOME_FIT_AUDIT_POSITIONING.md:46-48]. DEV window data (2022-01-01 00:00:00 UTC to 2024-06-30 23:59:59 UTC, 30 months, 87,552 15m bars resampled from 1,313,280 1m klines across 30 monthly CSV files in `raw_1m_2022`) is complete with zero missing bars, verified against `DATA_MANIFEST.csv:1-31` [SOURCED DATA_MANIFEST.csv:1-31; COUNT_POWER.md:5,21]. Historical 8-hour funding records from `raw_fund` cover 2020-01-01 to 2024-06-30 (4,929 records, zero gaps) with defect B103 verified fixed [SOURCED COUNT_POWER.md:5; T055_BT_RERUN_FULLFUNDING_2026-10-07.md:7,36]. Unused trader inputs (live liquidation history, tick/L2 depth, whale wallet cohorts) are NOT_IN_DATA [SOURCED HOME_FIT_AUDIT_POSITIONING.md:47-48]. Gate 0d passes.
- 0e Power: Trades in the dev window and the detectable edge; if larger than the claimed edge, write INCONCLUSIVE in advance or do not run (backtest/power_mde.py). Across the 30-month DEV window, all 36 grid cells have N >= 352 trades (range: 352 to 2,055 trades), well above the N >= 100 power floor [SOURCED PRE_REG_TEMPLATE.md:16; COUNT_POWER.md:78]. Zero cells are inconclusive on DEV [OURS, COUNT_POWER.md:79]. For the 6 candidate cells passing Gate 0b at 48 bars, MDE % (at 1.31 % noise and cost_r = 0.0916 R) spans 0.102 % to 0.195 % [OURS, COUNT_POWER.md:34-71, 79], well below the 0.240 % (2x cost) threshold and below the observed gross moves (+0.253 % to +0.341 %). Gate 0e passes.
- 0f Kill: Which result ends this source for good, and how many redesigns are allowed before it? The Positioning C1 NO-SOURCE idea (`funding_cvd_fade`) is permanently KILLED (source retired, closed, no further cards or variants permitted) if: (1) On DEV backtest: none of the 6 pre-registered candidate cells achieves mean net return > 0.0 % after fees (12 bps RT + funding) AND exceeds the 95th percentile of the matched random-entry null distribution; OR (2) On VALIDATION (2024-07-01 to 2025-06-30, read ONCE): the frozen top candidate from DEV fails to achieve mean net return > 0.0 % after fees; OR (3) On sealed HOLDOUT: the frozen configuration fails to achieve mean net return > 0.0 % after fees, OR fails to beat the 95th percentile matched null benchmark. Redesign budget: Exactly ZERO (0) redesigns allowed [OURS]. This pre-registration and its subsequent single backtest card represent the FINAL opportunity for this NO-SOURCE literature concept. If it fails DEV, VALIDATION, or HOLDOUT, the concept is permanently closed. Gate 0f is strictly specified.

---

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Answer: Framing finding: The tested layer is NOT a FlowHorse layer and NOT a whale layer [SOURCED HOME_FIT_AUDIT_POSITIONING.md:7-16]. FlowHorse extracts contain zero mentions of funding, open interest, or liquidation (0/0/0 grep count), and 0 of 32 FlowHorse rules are built in the rulebook [SOURCED CROSS_TRADER_RULEBOOK.md:121; HOME_FIT_AUDIT_POSITIONING.md:11]. In raw transcripts FlowHorse explicitly states he is not focused on funding [SOURCED extract_izZyd-HrTSE_the_flow_horse.txt:230]. Whale signals were rejected before testing as coincident/lagged [SOURCED whale_positioning_evidence_2026-09-12.md:19,46]. C1 is an engineering encoding of Memon 2026 (funding-extreme reversion) combined with CVD divergence [SOURCED FORMULAS.md:356-370].
- Home market: Crypto perpetuals (Binance USDT-M BTCUSDT) [SOURCED run_t055.py:9].
- Timeframe: 15-minute bars resampled from 1m klines, with 8-hour funding rates [SOURCED FORMULAS.md:364; run_t055.py:65].
- Session: 24/7 continuous crypto market (no intraday session filtering, though session strata are evaluated per B154) [SOURCED HOME_FIT_AUDIT_POSITIONING.md:26].
- Holding period: 48 bars of 15m (12.0 hours) [OURS, COUNT_POWER.md:88-94], chosen based on DEV power and Gate 0b pass from the 4b/16b/48b grid. All horizons are OURS.
Evidence (file:line):
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:7-16` "Finding that frames everything: the tested layer is not a FlowHorse layer"
- `extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:230` FlowHorse: not focused on funding
- `research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:121` FlowHorse built rows: 0 of 32
- `research/whale_positioning_evidence_2026-09-12.md:19,46` "Whale signals are coincident or lagged, not leading; DO NOT add whale-tracking DSA field"
- `MyTradingSys/backtest/layers/FORMULAS.md:356-370` C1 specification and formula definition
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:88-100` DEV horizon dynamics and Gate 0b results

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Answer: NOT_IN_DATA. As a NO-SOURCE research test under VISION exception 2 [SOURCED PROJECT_VISION.md:238-242], no human trader exists behind this layer, and no trade ledger or dated call list exists [SOURCED HOME_FIT_AUDIT_POSITIONING.md:32-34]. The feasibility audit of FlowHorse sources confirmed 0 scoreable BTC events [SOURCED LEDGER_FEASIBILITY.md:1-25]. Per Gate 0c, this missing input is recorded honestly; the layer remains an unverified hypothesis. Ground truth for C1 detection logic is verified through deterministic unit tests in `test_funding_cvd_fade.py:27-90` on synthetic fixture bars and known funding percentiles.
Evidence (file:line):
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:32-35` "NOT_IN_DATA. There is no FlowHorse trade ledger and no dated call list... For C1 no trader exists"
- `MyTradingSys/research/positioning_flowhorse_2026-10/LEDGER_FEASIBILITY.md:1-25` 0 scoreable BTC events in FlowHorse sources, verdict HYPOTHESIS
- `MyTradingSys/backtest/layers/positioning/test_funding_cvd_fade.py:27-90` Unit tests pinning funding percentiles, CVD divergence, and event generation
- `MyTradingSys/system/PROJECT_VISION.md:238-242` VISION exception 2 for NO-SOURCE research tests

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Answer: Recall is NOT_IN_DATA due to lack of a trader ledger (item 2). Fire rate on DEV (30 calendar months, 2022-01-01 to 2024-06-30, 87,552 15m bars) from `COUNT_POWER.md:34-71`: Across the 6 candidate cells passing Gate 0b at 48 bars, fire rate spans 11.7 to 42.8 events per month (4.02 to 14.68 events per 1,000 bars) [OURS, COUNT_POWER.md:34-71]:
- Cell 1 (lookback 180, n 50, hi/lo 99/1, div yes): N = 352 (11.7/mo, 4.02/1000b; 2022: 167, 2023: 172, 2024: 13) [OURS, COUNT_POWER.md:70].
- Cell 2 (lookback 180, n 20, hi/lo 95/5, div yes): N = 1163 (38.8/mo, 13.28/1000b; 2022: 469, 2023: 592, 2024: 102) [OURS, COUNT_POWER.md:62].
- Cell 3 (lookback 90, n 50, hi/lo 95/5, div yes): N = 682 (22.7/mo, 7.79/1000b; 2022: 236, 2023: 291, 2024: 155) [OURS, COUNT_POWER.md:56].
- Cell 4 (lookback 90, n 50, hi/lo 99/1, div yes): N = 425 (14.2/mo, 4.85/1000b; 2022: 193, 2023: 165, 2024: 67) [OURS, COUNT_POWER.md:58].
- Cell 5 (lookback 180, n 20, hi/lo 99/1, div yes): N = 677 (22.6/mo, 7.73/1000b; 2022: 364, 2023: 297, 2024: 16) [OURS, COUNT_POWER.md:64].
- Cell 6 (lookback 180, n 50, hi/lo 95/5, div yes): N = 600 (20.0/mo, 6.85/1000b; 2022: 223, 2023: 308, 2024: 69) [OURS, COUNT_POWER.md:68].
The encoding fires selectively (1 event every 68 to 249 bars) and does not fire everywhere.
Evidence (file:line):
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:34-71` Complete 36-cell DEV count, fire rate, and annual breakdown table
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:77-80` Power and sample size findings
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:40-42` Prior fire rate audit

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Answer: Inputs required by C1: 15m OHLCV bars, taker-buy volume (aggressor proxy, CVD = 2*tbv - v) and 8-hour funding rates [SOURCED FORMULAS.md:364; funding_cvd_fade.py:48].
Data verification for DEV window (2022-01-01 00:00:00 UTC to 2024-06-30 23:59:59 UTC, 30 months, 87,552 15m bars resampled from 1,313,280 1m klines):
- 30 monthly Binance BTCUSDT 1m kline files verified with exact SHA-256 checksums from `MyTradingSys/research/gross_effect_screen_2026-10-15/DATA_MANIFEST.csv:1-31` [SOURCED DATA_MANIFEST.csv:1-31]. Zero gaps in DEV klines.
- 8-hour funding rate history from `raw_fund` covering 2020-01-01 to 2024-06-30 (4,929 records, zero gaps). Defect B103 (silent zero funding) is verified fixed; every trade is funded [SOURCED T055_BT_RERUN_FULLFUNDING_2026-10-07.md:7,36].
- FlowHorse / whale inputs (historical liquidation orders, tick/L2 book depth, whale entity cohorts) are NOT_IN_DATA [SOURCED HOME_FIT_AUDIT_POSITIONING.md:47-48].
Evidence (file:line):
- `MyTradingSys/research/gross_effect_screen_2026-10-15/DATA_MANIFEST.csv:1-31` 30 monthly Binance BTCUSDT 1m files and SHA-256 checksums
- `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:48` CVD calculation from taker buy volume
- `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:7,36` 4,929 funding records, all trades funded
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:46-49` Data audit verdict FAIR for C1 inputs

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Answer: Drawn levels: NOT_IN_DATA (no trader levels exist). Parity is established via raw-bar checks and deterministic test cases in `test_funding_cvd_fade.py:27-90`:
- Hand-computed funding percentile logic verified (including current record) [SOURCED FORMULAS.md:364; test_funding_cvd_fade.py:27-32].
- CVD divergence strictly requires price lower-low with CVD higher-low (bullish fade) or price higher-high with CVD lower-low (bearish fade) over `n` bars [SOURCED FORMULAS.md:365-368; test_funding_cvd_fade.py:50-56].
- Funding lookback is defined in 8-hour funding records (e.g. lookback 90 = 30 calendar days, lookback 180 = 60 calendar days) [SOURCED FORMULAS.md:363; test_funding_cvd_fade.py:66-90].
Evidence (file:line):
- `MyTradingSys/backtest/layers/positioning/test_funding_cvd_fade.py:27-32,50-56,66-90` Deterministic parity tests
- `MyTradingSys/backtest/layers/FORMULAS.md:362-368` Formula definitions for funding percentiles and CVD divergence
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:52-54` Parity audit verdict FAIR

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Answer: Cost model: Binance USDT-M BTCUSDT taker fee 10 bps round trip + 2 bps slippage = 12 bps (0.12 %) round trip [SOURCED run_t055.py:9; FORMULAS.md:364]. Actual 8-hour funding rates paid/received over the hold are charged explicitly [SOURCED run_t055.py:111-113].
- Stop width in noise units: C1 uses fixed time-horizon exits (48 bars = 12.0 hours) [OURS]. In noise units, BTC 15m per-trade standard deviation is 1.31 % [SOURCED HOME_FIT_AUDIT_POSITIONING.md:85; COUNT_POWER.md:19].
- Transaction cost in noise units: 0.12 % / 1.31 % = 0.0916 R [OURS, COUNT_POWER.md:24].
- If an operational disaster stop is placed at 1.5x ATR (~1.96 % at 1.31 % sd) [OURS], fee share of R is 0.12 % / 1.96 % = 0.061 R (6.1 % of R), which is strictly < 0.25 R [OURS].
- At 48 bars, empirical mean gross moves across the 6 passing cells range from +0.253 % to +0.341 % [OURS, COUNT_POWER.md:88-94], satisfying Gate 0b (gross >= 2x cost = 0.240 %).
Evidence (file:line):
- `MyTradingSys/backtest/layers/run_t055.py:9,111-113` Taker fee 10 bps, slippage 2 bps, funding charging
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:58-61` Cost audit verdict FAIR
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:14,24` Cost R and noise unit derivation

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Answer: Fill model: Immediate market taker execution at the close of the event bar [SOURCED run_t055.py:10-12]. Exit is an immediate market taker execution at the close of bar i+h [SOURCED run_t055.py:111-113].
- Resting limit orders are not used; therefore touch-fill optimism, selection bias, and trade-through fill defect classes (B151) do not occur [SOURCED items/B151_backtest_fill_optimism_and_selection.md:1; HOME_FIT_AUDIT_POSITIONING.md:64-66].
- Full round-trip taker fee (10 bps) and flat slippage (2 bps) are charged on every simulated trade.
Evidence (file:line):
- `MyTradingSys/backtest/layers/run_t055.py:10-12,111-113` Market entry and exit execution
- `MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:1` Touch-fill defect class description
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:64-66` Fills audit verdict FAIR

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Answer: Mismatch is explicitly stated [SOURCED HOME_FIT_AUDIT_POSITIONING.md:70-73]: C1 uses a fixed time-based exit at 48 15m bars (12.0 hours) [OURS, COUNT_POWER.md:88-94]. No stop-loss, profit target, or trailing exit management is simulated.
- Sourced rationale: For a mean-reversion phenomenon, a fixed time exit represents a conservative lower bound on performance relative to dynamic management. For FlowHorse, who uses 1.5-2.0 ATR stops and point-of-origin targets [SOURCED extract_UrnES-HzQ6w_the_flow_horse.txt:283,579-583], this is an explicit mismatch. Because C1 is evaluated strictly as a NO-SOURCE research test (VISION exception 2), the fixed time exit is retained as the registered lower-bound benchmark.
Evidence (file:line):
- `MyTradingSys/backtest/layers/run_t055.py:87,111-113` Fixed horizon exits at 4, 16, 48 bars
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:70-74` Exits audit verdict UNFAIR, mismatch stated
- `extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:283,579-583` FlowHorse management rules

## 9. Null like-for-like: same session window, same order type, same fill rules.

Answer: Matched Random-Entry Null Specification copied directly from `COUNT_POWER.md:113-132`:
To test whether C1's gross edge reflects genuine timing alpha rather than drift or funding baseline:
1) Sampling Frame: 15m bars inside the exact DEV window (2022-01-01 00:00:00 UTC to 2024-06-30 23:59:59 UTC) [OURS].
2) Exact Side Mix Matching: Match the exact long/short proportion of the real candidate cell (e.g. 89.3 % short, 10.7 % long for lookback 90, n 50, 95/5; 79.9 % short, 20.1 % long for lookback 180, n 20, 95/5; 97.4 % short, 2.6 % long for lookback 180, n 50, 99/1) [OURS, COUNT_POWER.md:103-106, 117-118].
3) Regime and Calendar Density Matching: Condition random entry selection on the same funding percentile regime: short random entries drawn only during bars where funding percentile >= hi; long random entries drawn only during bars where funding percentile <= lo. Stratified by calendar year/quarter to match temporal clustering of extreme funding events [OURS, COUNT_POWER.md:119-123].
4) Execution and Cost Parity: Identical entry price at event bar close; identical holding period (exit at bar i+48 close); identical cost model (12 bps RT taker fee + actual historical funding paid/received) [OURS, COUNT_POWER.md:124-127].
5) Monte Carlo Resampling: 1,000 independent bootstrap draws of sample size N. Real strategy mean net return must exceed the 95th percentile of the matched null distribution AND satisfy two-sided 95 % CI lower bound > 0 [OURS, COUNT_POWER.md:128-132].
Evidence (file:line):
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:113-132` Section 4: Random-Entry Null Specification
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:77-80` Null audit verdict UNFAIR, requirements for like-for-like null

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Answer: Power and MDE analysis from `COUNT_POWER.md:29-72, 77-80` computed using `backtest/power_mde.py`:
- DEV window (30 months, 2022-01-01 to 2024-06-30): All 36 grid cells have N >= 352 (range: 352 to 2,055 trades) [OURS, COUNT_POWER.md:78]. Zero cells have N < 100; zero cells are inconclusive on DEV [OURS, COUNT_POWER.md:79].
- Prior OOS run (109 days, N = 76) had MDE = 0.420 % per trade (underpowered) [SOURCED HOME_FIT_AUDIT_POSITIONING.md:85].
- For the 6 candidate cells passing Gate 0b at 48 bars, MDE % (at 1.31 % noise and cost_r = 0.0916 R) spans 0.102 % to 0.195 % [OURS, COUNT_POWER.md:34-71, 79]:
  1. lookback 180, n 50, hi/lo 99/1: N = 352, MDE net R = 0.149 R, MDE % = 0.195 %, gross 48b = +0.341 % (PASS) [OURS, COUNT_POWER.md:70].
  2. lookback 180, n 20, hi/lo 95/5: N = 1163, MDE net R = 0.082 R, MDE % = 0.107 %, gross 48b = +0.308 % (PASS) [OURS, COUNT_POWER.md:62].
  3. lookback 90, n 50, hi/lo 95/5: N = 682, MDE net R = 0.107 R, MDE % = 0.140 %, gross 48b = +0.273 % (PASS) [OURS, COUNT_POWER.md:56].
  4. lookback 90, n 50, hi/lo 99/1: N = 425, MDE net R = 0.135 R, MDE % = 0.177 %, gross 48b = +0.271 % (PASS) [OURS, COUNT_POWER.md:58].
  5. lookback 180, n 20, hi/lo 99/1: N = 677, MDE net R = 0.107 R, MDE % = 0.140 %, gross 48b = +0.255 % (PASS) [OURS, COUNT_POWER.md:64].
  6. lookback 180, n 50, hi/lo 95/5: N = 600, MDE net R = 0.114 R, MDE % = 0.149 %, gross 48b = +0.253 % (PASS) [OURS, COUNT_POWER.md:68].
Every candidate cell is fully powered on DEV to detect any true edge >= 0.240 % (2x round-trip cost).
Evidence (file:line):
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:29-72` DEV Count and Power Table (36 Grid Cells)
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:77-80` Section 3.1: Power and Sample Size analysis
- `MyTradingSys/backtest/power_mde.py:1-52` Power and minimum detectable effect formulas
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:84-87` Power audit verdict UNFAIR on prior n=76 run

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Answer: Data partitioning and contamination accounting [SOURCED HOME_FIT_AUDIT_POSITIONING.md:91-94]:
- DEV window: 2022-01-01 00:00:00 UTC to 2024-06-30 23:59:59 UTC (30 calendar months, 87,552 15m bars) [OURS] — clean data, never read by prior C1 backtest runs.
- VALIDATION window: 2024-07-01 00:00:00 UTC to 2025-06-30 23:59:59 UTC (12 calendar months) [OURS] — to be read ONCE after DEV freeze.
- BURNED / CONTAMINATED data: 2025-07-01 to 2026-08-31 (previously read 3 times in T055 OOS runs) is strictly BURNED for C1 and will NEVER be used as holdout [SOURCED HOME_FIT_AUDIT_POSITIONING.md:92-94].
- Sealed HOLDOUT window: 2026-09-01 forward [OURS] — strictly sealed and untouched by developers.
Trial Ledger Accounting:
- Prior trials: Exactly 108 variants (36 parameter cells x 3 holding horizons: 4, 16, 48 bars) from prior T055 runs [SOURCED HOME_FIT_AUDIT_POSITIONING.md:15; run_t055.py:65-68,87].
- Pre-registered redesign trials: Exactly 6 candidate cells at horizon 48 bars pre-registered for DEV backtest evaluation [OURS, COUNT_POWER.md:88-94].
- Cumulative trials = 114 variants.
Evidence (file:line):
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:91-95` Holdout audit verdict UNFAIR, contamination history, and clean DEV split
- `MyTradingSys/backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md:13` Repo split alignment
- `MyTradingSys/backtest/layers/run_t055.py:65-68,87` 36 parameter cells x 3 horizons = 108 prior variants
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:88-94` 6 pre-registered candidate cells

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Answer: Regime and session stratification proposal copied from `COUNT_POWER.md:135-155` per defect B154 [SOURCED items/B154_regime_and_session_stratified_backtest.md:1-14]:
1) Funding Extremity Regime:
   - Extreme High Funding: funding rate >= 95th percentile (short signals) [OURS].
   - Extreme Low / Negative Funding: funding rate <= 5th percentile (long signals) [OURS].
   - Neutral / Mild Funding: 10th to 90th percentile (control baseline) [OURS].
2) Macro Market Trend (Calendar Regimes):
   - 2022 Bear / Deleveraging: persistent downtrend, credit contractions (Terra/Luna, FTX) [OURS, COUNT_POWER.md:144-146].
   - 2023 Consolidation / Recovery: low-volatility range-bound regime, choppy mean reversion [OURS, COUNT_POWER.md:146].
   - 2024 Bull Expansion: pre-halving momentum, persistent positive funding [OURS, COUNT_POWER.md:147].
3) Intraday Session Window:
   - Asia Session: 00:00 to 08:00 UTC [OURS, COUNT_POWER.md:150].
   - European / London Session: 08:00 to 14:00 UTC [OURS, COUNT_POWER.md:151].
   - US Session: 14:00 to 21:00 UTC (US cash open, major volatility concentration) [OURS, COUNT_POWER.md:152].
Every stratum will report N, fire rate, gross mean return at 48 bars, net mean return, and Gate 0b pass rate side-by-side with the pooled metric in any future backtest report.
Evidence (file:line):
- `MyTradingSys/research/positioning_c1_2026-10/COUNT_POWER.md:135-155` Section 5: Regime Strata Proposal for B154
- `MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:1-14` Defect B154 description
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:98-102` Strata audit verdict UNFAIR
