# Layer Fact Sheet: wavetrend

> **Claude review 2026-10-26** (`MyTradingSys/research/layer_lab/reports/2026-10-26_gemini-facts-review.md`): content errors below are fixed; about 8; NUC-local file:/// links rewritten to repo-root links. Final recorded labels: W01-W03, W09 FAIL; W04-W08 INCONCLUSIVE (`MyTradingSys/research/VERDICTS.csv:56-64`); W07/W08 also detector-invalid; sim-desk n=369 is the default config only (1h, band 53, both sides, 1.5R) line cites drift from trunk (content true, line off) and are listed in that report, not rewritten here. Treat any line number as approximate (+-15).

Scope: Layer family `wavetrend` fact sheet, compiled strictly from repository files with file:line citations or `NOT_IN_DATA`. Contains no verdict on keeping, dropping, demoting, or parking a layer.

---

## 1. ORIGIN

- **Origin Analyst / Author:** LazyBear (PineScript author).
  - Quoted source: `"@author LazyBear ... If you use this code in its original/modified form, do drop me a note."` ([PARITY_CONTRACT.md:13](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L13); [FORMULAS.md:511](/MyTradingSys/backtest/layers/FORMULAS.md#L511); [wavetrend.py:5](/MyTradingSys/backtest/layers/wavetrend/wavetrend.py#L5)).
  - Source publication / pin: TradingView script titled `"WaveTrend with Crosses [LazyBear]"` by user lonestar108 (`https://www.tradingview.com/v/jFQn4jYZ/`, script id 2295, created 2016-02-20) saved at `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt` ([PARITY_CONTRACT.md:7-12](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L7-L12)).
  - Identical oscillator mathematics confirmed in marketcalls gist mirror `LB_WaveTrend_marketcalls_gist.pine.txt` ([PARITY_CONTRACT.md:10-12](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L10-L12)).
- **Underlying Concept / Port:** LazyBear's 2014 publication calls WaveTrend a port of an earlier TS/MT indicator ([EXTERNAL_SETUPS.md:13](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L13)).
- **Core Signal Concept:** The author proposes a sell when the oscillator crosses down through its signal line above an overbought band, and a buy when it crosses up below an oversold band ([EXTERNAL_SETUPS.md:13](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L13); [studies/wavetrend.py:1-7](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L1-L7)).

---

## 2. PARAMETERS

- **Formula & Indicator Parameters (SOURCED):**
  - Source citation: `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:9-23` and `gist:14-21` cited in [PARITY_CONTRACT.md:17-18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L17-L18), [PRE_REG.md:17](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L17), [FORMULAS.md:511-513](/MyTradingSys/backtest/layers/FORMULAS.md#L511-L513).
  - Price source: `ap = (h + l + c) / 3` (HLC3) [SOURCED: [PARITY_CONTRACT.md:18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L18); [FORMULAS.md:513](/MyTradingSys/backtest/layers/FORMULAS.md#L513)].
  - Channel length: `n1 = 10` for `esa = EMA(ap, 10)` and `d = EMA(|ap - esa|, 10)` [SOURCED: [PARITY_CONTRACT.md:18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L18); [FORMULAS.md:513](/MyTradingSys/backtest/layers/FORMULAS.md#L513)].
  - CI divisor factor: `0.015` in `ci = (ap - esa) / (0.015 * d)` [SOURCED: [PARITY_CONTRACT.md:15-18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L15-L18); [FORMULAS.md:513](/MyTradingSys/backtest/layers/FORMULAS.md#L513)].
  - Average length: `n2 = 21` for `wt1 = EMA(ci, 21)` [SOURCED: [PARITY_CONTRACT.md:18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L18); [FORMULAS.md:513](/MyTradingSys/backtest/layers/FORMULAS.md#L513)].
  - Signal smoothing: `SMA(wt1, 4)` for `wt2` [SOURCED: [PARITY_CONTRACT.md:18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L18); [FORMULAS.md:513](/MyTradingSys/backtest/layers/FORMULAS.md#L513)].
  - Threshold bands: `+53 / +60` (overbought) and `-53 / -60` (oversold), centre `0` [SOURCED: [PARITY_CONTRACT.md:18](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L18); [PRE_REG.md:17](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L17); [FORMULAS.md:511](/MyTradingSys/backtest/layers/FORMULAS.md#L511)].
  - Long on up-cross below oversold band, short on down-cross above overbought band [SOURCED: [EXTERNAL_SETUPS.md:23](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L23); [studies/wavetrend.py:5-7](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L5-L7)].
  - Long-only stop at preceding three-bar low, target 1.5x risk (TrendCrypto2022) [SOURCED: [EXTERNAL_SETUPS.md:24](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L24); [studies/wavetrend.py:6-7](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L6-L7)].

- **Conventions & Study Setup Parameters (OURS):**
  - Warmup period: `WARMUP = 200` bars from series start, after gap, or after NaN [OURS: [PARITY_CONTRACT.md:23](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L23); [FORMULAS.md:515](/MyTradingSys/backtest/layers/FORMULAS.md#L515)].
  - Flat window zero-division protection: `d <= 1e-9 * abs(ap)` yields `ci = NaN` [OURS: [PARITY_CONTRACT.md:24](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L24); [FORMULAS.md:515](/MyTradingSys/backtest/layers/FORMULAS.md#L515)].
  - Cross convention: "le" where event fires at first bar strictly on opposite side of last strict side; tie bar skipped; above-tie-above not a cross [OURS: [PARITY_CONTRACT.md:26](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L26); [FORMULAS.md:515](/MyTradingSys/backtest/layers/FORMULAS.md#L515)].
  - Closed bars only: `available_at = bar_open_time + timeframe`; earliest executable price = next bar open [OURS: [PARITY_CONTRACT.md:29](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L29); [FORMULAS.md:515](/MyTradingSys/backtest/layers/FORMULAS.md#L515)].
  - HTF value alignment: value of the last HTF bar whose close time <= t [OURS: [PARITY_CONTRACT.md:30](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L30); [FORMULAS.md:515](/MyTradingSys/backtest/layers/FORMULAS.md#L515)].
  - Atlas study statistical floor: `FLOOR = 153` distinct UTC event-days (Holm over 12 cells, alpha 0.05/12 two-sided, power 80%, MDE <= 0.30 SD) [OURS: [PRE_REG.md:20](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L20)]. Later re-gated to 200 days [OURS: [DISPOSITION_2026-10-19.md:13](/MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md#L13); [STATUS_2026-10-19.md:9](/MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md#L9)].
  - Event parameter `R_out = 3` (bars outside zone before arrival counts) [OURS: [PRE_REG.md:21](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L21)].
  - Event parameter `c = 5` (B2 centre-test half-width, WT points) [OURS: [PRE_REG.md:22](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L22)].
  - Event parameters `k = 2` (pivot right-hand bars) and `G = 20` (max bars between pivots) [OURS: [PRE_REG.md:23](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L23)].
  - Context bin cutoffs (volatility terciles, EMA(200) trend state with 10-bar slope, HTF zone, volume participation 20-day trailing terciles, UTC 8-hour windows) [OURS: [PRE_REG.md:25-38](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L25-L38)].
  - Primary outcome horizon: `H = 12` bars (descriptive H = 4, 48) [OURS: [PRE_REG.md:80](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L80)].
  - Sim-desk trading rules: entry at next bar open, both lines beyond band, max hold 100 bars, timeframes {1h, 4h, 15m} [OURS: [studies/wavetrend.py:8-10, 21-23](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L8-L10)].

---

## 3. BACKTESTS

Every backtest / empirical run recorded in the repository:

### 1. WaveTrend DEV Behaviour Atlas (Card `wavetrend-dev-atlas`)
- **Report Path:** `MyTradingSys/research/wavetrend_2026-10-17/RESULT.md` ([RESULT.md:1-135](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L1-L135); machine output at `MyTradingSys/research/wavetrend_2026-10-17/atlas_out/atlas_results.json` cited in [AUDIT_2026-10-18.md:33](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L33)).
- **Ledger Entries:** `MyTradingSys/research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv:7` ([EXPOSURE_LEDGER.csv:7](/MyTradingSys/research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv#L7)); `MyTradingSys/research/TRIAL_LEDGER.csv:10-18` (trials `WT-A01_W01` through `WT-A09_W09`) ([TRIAL_LEDGER.csv:10-18](/MyTradingSys/research/TRIAL_LEDGER.csv#L10-L18)); `MyTradingSys/research/VERDICTS.csv:56-64` ([VERDICTS.csv:56-64](/MyTradingSys/research/VERDICTS.csv#L56-L64)).
- **Sample Split:** DEV only (Binance USDT-M BTCUSDT 1m klines, 2022-01-01 through 2024-06-30, 912 days) ([PRE_REG.md:9](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L9); [RESULT.md:5](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L5)). In-sample / Out-of-sample: DEV in-sample; VALIDATION reads = 0; HOLDOUT reads = 0 ([RESULT.md:5](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L5); [DISPOSITION_2026-10-19.md:3](/MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md#L3)).
- **Fee Net Status:** Not fee-net; gross only (no fees, no funding, no strategy stops/targets) ([PRE_REG.md:84](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L84); [RESULT.md:5](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L5); [AUDIT_2026-10-18.md:28](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L28)).
- **Number of Observations / Trades (n):**
  - Primary cells (events / event-days / conjunction mean return %):
    - W01 (5m A1_L53 trend:with): `n = 3893` events (910 days), mean = -0.0143% (-1.43 bps), SE = 0.0108% ([RESULT.md:15, 29](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L15); [VERDICTS.csv:56](/MyTradingSys/research/VERDICTS.csv#L56)).
    - W02 (5m A1_L53 htf:mid): `n = 4196` events (908 days), mean = -0.0078% (-0.78 bps), SE = 0.0096% ([RESULT.md:16, 33](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L16); [VERDICTS.csv:57](/MyTradingSys/research/VERDICTS.csv#L57)).
    - W03 (5m A2_L53 trend:with): `n = 3509` events (904 days), mean = -0.0043% (-0.43 bps), SE = 0.0110% ([RESULT.md:17, 37](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L17); [VERDICTS.csv:58](/MyTradingSys/research/VERDICTS.csv#L58)).
    - W04 (15m A2_L53 trend:with): `n = 1154` events (716 days), mean = -0.0209% (-2.09 bps), SE = 0.0325% ([RESULT.md:18, 41](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L18); [VERDICTS.csv:59](/MyTradingSys/research/VERDICTS.csv#L59)).
    - W05 (15m B2 htf:mid): `n = 788` events (511 days), mean = -0.0578% (-5.78 bps), SE = 0.0329% ([RESULT.md:19, 45](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L19); [VERDICTS.csv:60](/MyTradingSys/research/VERDICTS.csv#L60)).
    - W06 (15m B2 trend:with): `n = 538` events (390 days), mean = -0.0422% (-4.22 bps), SE = 0.0402% ([RESULT.md:20, 49](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L20); [VERDICTS.csv:61](/MyTradingSys/research/VERDICTS.csv#L61)).
    - W07 (1h C1 trend:with): `n = 298` events (251 days), mean = -0.0295% (-2.95 bps), SE = 0.1457% ([RESULT.md:21, 53](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L21); [VERDICTS.csv:62](/MyTradingSys/research/VERDICTS.csv#L62)).
    - W08 (1h C1 htf:mid): `n = 271` events (239 days), mean = 0.0897% (+8.97 bps), SE = 0.1228% ([RESULT.md:22, 57](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L22); [VERDICTS.csv:63](/MyTradingSys/research/VERDICTS.csv#L63)).
    - W09 (1h B1 htf:mid): `n = 947` events (562 days), mean = 0.0241% (+2.41 bps), SE = 0.0418% ([RESULT.md:23, 61](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L23); [VERDICTS.csv:64](/MyTradingSys/research/VERDICTS.csv#L64)).
  - Total primary cell event count sum: `15,594` events across W01–W09 (cells overlap; not a distinct-event total) ([RESULT.md:15-23](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L15-L23)).
  - Additional control runs reported: A3_L53, A1_L60, A3_L60 across 5m, 15m, 1h (n between 291 and 6,373) ([RESULT.md:101-110](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L101-L110)).
  - Descriptive runs reported: 4h unconditioned events (n between 22 and 244) and C2 on 5m (n = 1,207) and 15m (n = 402) ([RESULT.md:114-123](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L114-L123)).

### 2. Sim-Desk Simulator Study (`studies/wavetrend.py`)
- **Report Path / Code:** `MyTradingSys/research/sim_desk/studies/wavetrend.py` ([studies/wavetrend.py:1-122](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L1-L122)); logged in `MyTradingSys/research/layer_lab/TRIALS.md:273` ([TRIALS.md:273](/MyTradingSys/research/layer_lab/TRIALS.md#L273)) and `MyTradingSys/system/NEXT_SESSION.md:68` ([NEXT_SESSION.md:68](/MyTradingSys/system/NEXT_SESSION.md#L68)).
- **Sample Split:** DEV 2022-04-01 through 2024-06-30; VALIDATION/HOLDOUT never offered ([TRIALS.md:273](/MyTradingSys/research/layer_lab/TRIALS.md#L273); [studies/wavetrend.py:28](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L28)).
- **Fee Net Status:** Fee-net: maker 0.02%, taker 0.05%, plus slippage ([TRIALS.md:273](/MyTradingSys/research/layer_lab/TRIALS.md#L273); [studies/wavetrend.py:69-79](/MyTradingSys/research/sim_desk/studies/wavetrend.py#L69-L79); [NEXT_SESSION.md:68](/MyTradingSys/system/NEXT_SESSION.md#L68)).
- **Number of Observations / Trades (n):**
  - Trades filled: `n = 369` trades (0 never filled) ([TRIALS.md:273](/MyTradingSys/research/layer_lab/TRIALS.md#L273); [test_reference.py:60](/MyTradingSys/research/sim_desk/test_reference.py#L60); [NEXT_SESSION.md:68](/MyTradingSys/system/NEXT_SESSION.md#L68)).
  - Outcome metric: mean net R = -0.158 R (95% CI [-0.288, -0.023]), worst losing streak 8 ([TRIALS.md:273](/MyTradingSys/research/layer_lab/TRIALS.md#L273); [NEXT_SESSION.md:68](/MyTradingSys/system/NEXT_SESSION.md#L68)).

---

## 4. KNOWN BUGS, FABRICATIONS, ASSUMPTIONS & AUDIT RULINGS

- **Formal `lab_query.py rulings wavetrend` Output:**
  - `{"family": "wavetrend", "rulings": []}` (`NOT_IN_DATA`: no bug rows name wavetrend in `MyTradingSys/research/BUGS.md`) ([lab_query.py output](/scripts/dev/lab_query.py)).
- **Documented Audit Findings & Issues in Repo Files:**
  1. **C1 Divergence Definition/Implementation Mismatch (HIGH):**
     - Description: `ATLAS_STUDY_SPEC.md` §2 defines C1 as a confirmed price pivot with the WT pivot making a lower/higher extreme. In `MyTradingSys/research/wavetrend_2026-10-17/count_events.py:181-192`, C1 confirmed two price pivots and evaluated `wt1[p]` at those price-pivot bar indices without verifying that either WT value was a confirmed WT pivot ([AUDIT_2026-10-18.md:7](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L7); [STATUS_2026-10-19.md:13](/MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md#L13); [DISPOSITION_2026-10-19.md:7](/MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md#L7)).
     - Reproduction: `repro_c1_spec_mismatch.py` confirmed `C1 events: [(22, 1)]` where price pivots are 10 and 20 while WT pivots are 12 and 18 ([AUDIT_2026-10-18.md:9](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L9)).
     - Consequence: Cells W07 and W08 are invalid under the intended event definition and do not measure confirmed WT-pivot divergence ([AUDIT_2026-10-18.md:11](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L11); [DISPOSITION_2026-10-19.md:9](/MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md#L9); [LAYERS.md:244](/MyTradingSys/system/LAYERS.md#L244)).
  2. **Control-Arm Uncertainty Inferential Basis Discrepancy (MEDIUM):**
     - Description: Primary event arm uses day-clustered SE (`MyTradingSys/research/wavetrend_2026-10-17/atlas.py:132-143`), while random-clock and context-only arms report the standard deviation of 200 sampled draw means (`MyTradingSys/research/wavetrend_2026-10-17/atlas.py:229-233`); `diff_test` combines them assuming independence ([AUDIT_2026-10-18.md:13-17](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L13-L17); [RESULT.md:132](/MyTradingSys/research/wavetrend_2026-10-17/RESULT.md#L132); [STATUS_2026-10-19.md:15](/MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md#L15)).
     - Consequence: Does not preserve shared market-time dependence; limits inferential strength of p-values ([AUDIT_2026-10-18.md:17](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L17); [DISPOSITION_2026-10-19.md:15](/MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md#L15)).
  3. **Input Manifest Content Pinning Deficiency (MEDIUM):**
     - Description: Exposure ledger entries in `EXPOSURE_LEDGER.csv` recorded directory path and script SHA, but did not record file manifests/digests or duplicate/missing bar checks ([AUDIT_2026-10-18.md:19-23](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L19-L23); [STATUS_2026-10-19.md:17](/MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md#L17)). Addressed subsequently by task card `wavetrend-data-inference` ([wavetrend-data-inference.json:15](/MyTradingSys/system/tasks/wavetrend-data-inference.json#L15)).
  4. **Parity Scope Limitation:**
     - Description: Parity is formula/spreadsheet parity against `make_golden.py` and research reference `wt_parity_ref.py`, NOT TradingView / Pine runtime parity (no TradingView export was available) ([PARITY_CONTRACT.md:32](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L32); [FORMULAS.md:523](/MyTradingSys/backtest/layers/FORMULAS.md#L523); [AUDIT_2026-10-18.md:27](/MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md#L27)).

---

## 5. CONFLUENCE

Intended companion layers, confirming indicators, and confluence structures documented in repo files:

- **Confirmed/Companion Indicators in Study Design:**
  - **Trend State:** EMA(200) trend filter (price position relative to EMA(200) and EMA(200) 10-bar slope direction) ([ATLAS_STUDY_SPEC.md:21](/MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md#L21); [PRE_REG.md:26](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L26)).
  - **Higher Timeframe (HTF) Zone:** WaveTrend state of the next-higher timeframe (5m->15m, 15m->1h, 1h->4h, 4h->1d) at its last closed bar ([ATLAS_STUDY_SPEC.md:21](/MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md#L21); [PRE_REG.md:27](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L27)).
  - **Participation / Volume:** Bar volume relative to trailing 20-day mean of the same UTC time slot ([ATLAS_STUDY_SPEC.md:21](/MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md#L21); [PRE_REG.md:28](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L28)).
  - **Volatility Regime:** Trailing realized volatility terciles (std of 100 log returns) ([ATLAS_STUDY_SPEC.md:21](/MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md#L21); [PRE_REG.md:25](/MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md#L25)).
- **External Literature Confluence Models Surveyed:**
  - Squeeze Momentum context ([EXTERNAL_SETUPS.md:29](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L29)).
  - Supertrend / MTF agreement ([EXTERNAL_SETUPS.md:30](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L30)).
  - Volume-weighted moving average (VWMA) overlay ([EXTERNAL_SETUPS.md:28](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L28)).
  - Market Cipher composites (combining WaveTrend waves with Money Flow, Stoch RSI, regular RSI) ([EXTERNAL_SETUPS.md:31](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L31)).
  - Support/Resistance price levels and pivots ([EXTERNAL_SETUPS.md:27](/MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md#L27)).
- **System Confluence & Gating Status:**
  - Standalone observation module with no live callers, no side, and explicitly NO Tom or Fabio gating: `"OBSERVATION ONLY: no side, no routing, no Tom/Fabio gate"` ([wavetrend.py:1](/MyTradingSys/backtest/layers/wavetrend/wavetrend.py#L1); [PARITY_CONTRACT.md:35, 38](/MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md#L35); [PROJECT_MAP.md:89](/MyTradingSys/system/PROJECT_MAP.md#L89)).
  - Presence in Layer Index / System Registry: `layer_index.json` has `wavetrend` registered in family array (`MyTradingSys/system/layer_index.json:716`; [STATUS_2026-10-19.md:26](/MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md#L21); [LAYERS.md:8, 243-255](/MyTradingSys/system/LAYERS.md#L8)).
  - Strategy layer map: `NOT_IN_DATA` (no row in `MyTradingSys/system/layer_map.json` for wavetrend) ([DISPOSITION_2026-10-19.md:21](/MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md#L21); [STATUS_2026-10-19.md:26](/MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md#L26)).
