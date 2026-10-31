# LAYERS.md Rows and Research Notes vs Code Audit: Group 2

**Task ID:** `gemini-doc-vs-code-layers-g2-1031`  
**Date:** 2026-10-31  
**Lane:** CODEX  
**Reviewer:** Gemini 3.8 Flash (Code vs Documentation Auditor)  
**Target Layers (Group 2):** `pitchfork`, `trendlines`, `timeframe`, `tick`, `wlow_bounce`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE_G2.md`  

---

## 1. Executive Summary & Verification Summary

For each of the target layers (`pitchfork`, `trendlines`, `timeframe`, `tick`, `wlow_bounce`), the specifications, parameters, windows, formulas, and rules stated in `MyTradingSys/system/LAYERS.md`, `MyTradingSys/backtest/layers/FORMULAS.md`, and the primary research notes/contracts were systematically compared against the implementation code under `MyTradingSys/backtest/layers/<layer>/`.

| Layer Family / Module | Primary Code Module | Specification / Research Reference | Stated Parameters & Rules Audited | Match Count | Contradiction / Discrepancy Count | Status Verdict |
|---|---|---|---|---|---|---|
| **pitchfork** (`pitchfork_swing`) | [pitchfork_detector.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py#L1) | [LAYERS.md:253-263](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/system/LAYERS.md#L253-L263), [RESEARCH_PITCHFORK_LAYER.md:18-80](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md#L18-L80), [PHASE2_4H_POC_STUDY.md:26-30](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md#L26-L30) | 12 | 11 | 1 | 1 Discrepancy (Anchor confirmation parameter: ATR filter in Rule P-01 not in ZigZag detector) |
| **trendlines** (`trendline_core`) | [trendline_core.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/trendlines/trendline_core.py#L26) | [FORMULAS.md:492-515](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/FORMULAS.md#L492-L515), [TRENDLINE_CONTRACT.md:12-50](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md#L12-L50), [LAYERS.md:238](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/system/LAYERS.md#L238) | 11 | 11 | 0 | EXACT MATCH |
| **timeframe** (`tf_resample`) | [tf_resample.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/timeframe/tf_resample.py#L9), [registry.json:1](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/timeframe/registry.json#L1) | [FORMULAS.md:151-162](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/FORMULAS.md#L151-L162), [TEST_PLAN.md:1-50](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/timeframe/TEST_PLAN.md#L1-L50), [LAYERS.md:86](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/system/LAYERS.md#L86) | 9 | 9 | 0 | EXACT MATCH |
| **tick** (`tick_extremes`, `tick_flagger`) | [tick_extremes.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/tick/tick_extremes.py#L3), [tick_flagger.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/tick/tick_flagger.py#L14) | [LAYER_PROVENANCE_AUDIT.md:158-179](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md#L158-L179), [T040_tick_delta_layer.md:35-51](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/items/T040_tick_delta_layer.md#L35-L51) | 10 | 10 | 0 | EXACT MATCH |
| **wlow_bounce** (`detector`) | [detector.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/wlow_bounce/detector.py#L13) | [PRE_REG.md:10-50](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md#L10-L50), [live_runner_cli.py:238-270](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/alerts/live_runner_cli.py#L238-L270) | 12 | 12 | 0 | EXACT MATCH |

- **Total Stated Parameters & Mathematical Rules Audited:** 54 items across 5 layer modules.  
- **Exact Matches:** 53 items.  
- **Contradictions / Discrepancies:** 1 item (detailed below).

---

## 2. Table of Contradictions and Documented Discrepancies

| No. | Layer / Component | Doc File & Line | Code File & Line | Document Stated Rule / Param | Code Actual Implementation | Discrepancy & Impact Assessment |
|---|---|---|---|---|---|---|
| 1 | **Pitchfork Pivot Filter** (`pitchfork`) | [RESEARCH_PITCHFORK_LAYER.md:24](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md#L24) | [pitchfork_detector.py:334-383](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py#L334-L383) | **Rule P-01: Anchor Confirmation**: Sourced rule states pivots $P_0, P_1, P_2$ must have minimum clearance $N \ge 3$ bars and swing amplitude exceeding $k \ge 2.5 \times \text{ATR}_{14}$. | `find_pivots_zigzag(highs, lows, lookback=3, min_change_pct=0.02)` uses a percentage threshold (`min_change_pct=0.02`) and no ATR filter. In `scan_pitchfork_signals` (`pitchfork_detector.py:394-395`), `lookback=4` and `min_change_pct=0.03` are used. | **Discrepancy:** The specification in `RESEARCH_PITCHFORK_LAYER.md:24` cites an ATR-scaled amplitude condition ($k \ge 2.5 \times \text{ATR}_{14}$), whereas the Python implementation exclusively uses percentage reversal gating (`min_change_pct`). The lookback $N \ge 3$ is satisfied (`lookback=3` or `lookback=4`). |

---

## 3. Detailed Parameter and Window Audit per Layer

### 3.1 Pitchfork (`backtest/layers/pitchfork/`)
- **Doc References:** `MyTradingSys/system/LAYERS.md:253-263`, `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:18-80`, `PHASE1_EVENT_STUDY.md`, `PHASE2_4H_POC_STUDY.md`.
- **Code:** `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py`.
- **Audit Findings:**
  1. `variant`: `STANDARD`, `SCHIFF`, `MODIFIED_SCHIFF` supported (`pitchfork_detector.py:23-27`). SOURCED: Andrews 1960, Schiff, Dologa. Matches doc.
  2. Schiff Origin formula: $t_{0} = t_0 + 0.5(t_1 - t_0)$, $p_{0} = p_0 + 0.5(p_1 - p_0)$ (`pitchfork_detector.py:72-73`). Matches doc `RESEARCH_PITCHFORK_LAYER.md:29-30`.
  3. Modified Schiff Origin formula: $t_0 = t_0$, $p_0 = p_0 + 0.5(p_1 - p_0)$ (`pitchfork_detector.py:76-77`). Matches doc `RESEARCH_PITCHFORK_LAYER.md:30`.
  4. Median line midpoints: $t_m = (t_1 + t_2)/2$, $p_m = (p_1 + p_2)/2$, slope $m = (p_m - p_0)/(t_m - t_0)$ (`pitchfork_detector.py:82-91`). Matches doc.
  5. Warning lines: $WL_k = UML + k \times \text{half\_width}$ (`pitchfork_detector.py:145`). Matches doc `RESEARCH_PITCHFORK_LAYER.md:56`.
  6. Quartile lines: $ML + 0.5 \times \text{offset}$ (`pitchfork_detector.py:153-157`). Matches Morge 2002 citation.
  7. ML reach rule: `low <= ml <= high` or close beyond ML (`pitchfork_detector.py:171-176`). Matches 80% rule doc `RESEARCH_PITCHFORK_LAYER.md:34-36`.
  8. Hagopian Failure rollover threshold: `max_ml_approach_ratio >= 0.15` (15% distance traveled towards ML before tine failure) (`pitchfork_detector.py:202-205`). Matches doc `RESEARCH_PITCHFORK_LAYER.md:40-42` and `pitchfork_param_labels.md:28`.
  9. Volume Profile filter: `build_profile` over $P_0..P_2$, bin width $10.0$ USD, `VA` filter $VAL \le P_2 \le VAH$, `POC` filter within $1.5\%$ of POC (`pitchfork_detector.py:469-482`). Matches `LAYERS.md:258` and `PHASE2_4H_POC_STUDY.md:26`.
  10. Stop offset: `stop_offset_pct = 0.015` (1.5% stop beyond tine/extreme) (`pitchfork_detector.py:396, 504, 527`). Matches `LAYERS.md:258` (`stop=1.5%`).
  11. Evaluation window: `max_eval_bars = 60` bars (`pitchfork_detector.py:397, 486`). Matches study params.

### 3.2 Trendlines (`backtest/layers/trendlines/`)
- **Doc References:** `MyTradingSys/backtest/layers/FORMULAS.md:492-515`, `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md:12-50`, `LAYERS.md:238`.
- **Code:** `MyTradingSys/backtest/layers/trendlines/trendline_core.py`.
- **Audit Findings:**
  1. Contract version: `trendline_contract_v1.1` (`trendline_core.py:26`). Matches `TRENDLINE_CONTRACT.md:1`.
  2. ATR length: `ATR_LEN = 14`, plain SMA of True Range (`trendline_core.py:27, 48-53`). Matches doc `FORMULAS.md:502` and `TRENDLINE_CONTRACT.md:9`.
  3. Volume baseline window: `VOL_LEN = 20` (`trendline_core.py:28`). Matches doc `FORMULAS.md:512`.
  4. Penetration poke tolerance: `PEN_TOL = 0.10` ($0.10 \times \text{ATR}_b$) (`trendline_core.py:29`). Matches doc `FORMULAS.md:507` and `TRENDLINE_CONTRACT.md:47`.
  5. Touch tolerance: `TOUCH_TOL = 0.25` ($0.25 \times \text{ATR}_b$) (`trendline_core.py:30`). Matches doc `FORMULAS.md:507` and `TRENDLINE_CONTRACT.md:48`.
  6. Reset distance: `RESET_DIST = 1.0` ($1.0 \times \text{ATR}_b$) (`trendline_core.py:31`). Matches doc `FORMULAS.md:510` and `TRENDLINE_CONTRACT.md:47`.
  7. Retest window: `RETEST_WINDOW = 20` bars (`trendline_core.py:32`). Matches `TRENDLINE_CONTRACT.md:14`.
  8. Pivot half-width: `k = 3`, strict ties disqualify (`trendline_core.py:77, 98-109`). Matches doc `FORMULAS.md:496-497` and `TRENDLINE_CONTRACT.md:29-30`.
  9. Line age cap: `max_age = 500` bars (`trendline_core.py:77`). Matches doc `TRENDLINE_CONTRACT.md:46`.
  10. Spacing constraints: `min_spacing = 10`, `max_spacing = 200` bars (`trendline_core.py:78`). Matches doc `TRENDLINE_CONTRACT.md:44-45`.
  11. Line geometries: Linear $L(t) = p_a + \frac{p_b-p_a}{i_b-i_a}(t-i_a)$ and Log $L(t) = \exp(\ln p_a + \frac{\ln p_b-\ln p_a}{i_b-i_a}(t-i_a))$ (`trendline_core.py:126-134`). Matches doc `FORMULAS.md:499-500`.

### 3.3 Timeframe Resampling (`backtest/layers/timeframe/`)
- **Doc References:** `MyTradingSys/backtest/layers/FORMULAS.md:151-162`, `MyTradingSys/backtest/layers/timeframe/TEST_PLAN.md:1-50`, `LAYERS.md:86`.
- **Code:** `MyTradingSys/backtest/layers/timeframe/tf_resample.py`, `registry.json`.
- **Audit Findings:**
  1. Seconds-unit regimes: Floor-aligned division `(sec // seconds) * seconds * 1000` (`tf_resample.py:25`). Matches doc `FORMULAS.md:155`.
  2. Day-reset seconds regime (7h): Cut at midnight 00:00 UTC `day_ms + ((t_ms - day_ms) // step) * step` (`tf_resample.py:28-30`, `registry.json:20`). Matches doc `FORMULAS.md:155`.
  3. Days-unit regime: `anchor_date = 1970-01-01` UTC (`tf_resample.py:33-43`, `registry.json:24-27`). Matches doc `FORMULAS.md:155-156`.
  4. Weekly regime: Monday-anchored ISO week using `epoch_day - ((epoch_day - 4) % 7)` (`tf_resample.py:46-49`, `registry.json:28`). Matches doc `FORMULAS.md:155-156`.
  5. Monthly regime: First day of calendar UTC month (`tf_resample.py:51-53`, `registry.json:29`). Matches doc `FORMULAS.md:156`.
  6. Closed-bar enforcement: Trailing partial bucket omitted (`tf_resample.py:84`). Matches doc `FORMULAS.md:160-161`.
  7. OHLCV aggregation: `o` first open, `c` last close, `h` max high, `l` min low, `v` sum volume (`tf_resample.py:90-106`). Matches doc `FORMULAS.md:159-160`.
  8. Missing bucket behavior: Full gaps reported in `gap_count`, never synthesized (`tf_resample.py:87, 107`). Matches doc `FORMULAS.md:154`.
  9. Timeframe set in registry: Supports 1m..12h, 1d..5d, 1w, 1M (`registry.json:6-30`). Matches `LAYERS.md:86` divergence test suite.

### 3.4 Tick Extremes and Flagger (`backtest/layers/tick/`)
- **Doc References:** `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:158-179`, `MyTradingSys/items/T040_tick_delta_layer.md:35-51`.
- **Code:** `MyTradingSys/backtest/layers/tick/tick_extremes.py`, `tick_flagger.py`, `build_tiers.py`.
- **Audit Findings:**
  1. Timeframes supported: `(1, 2, 3, 5, 10, 15)` minutes (`tick_extremes.py:214`). SOURCED: T040:40-41. Matches doc `LAYER_PROVENANCE_AUDIT.md:165`.
  2. Indicator channels: `net_delta`, `cvd_change`, `volume`, `price_change_pct`, `oi_delta` (`tick_extremes.py:162, 214`, `build_tiers.py:29`). SOURCED: T040:35-36. Matches doc `LAYER_PROVENANCE_AUDIT.md:166`.
  3. Gap clustering rule: New tier opened when `gap > factor * median_gap`, where `factor = 1.5` (`tick_extremes.py:108, 143`). SOURCED rule, factor OURS. Matches doc `LAYER_PROVENANCE_AUDIT.md:168-169`.
  4. Extreme cutoff depth: Top 20 ranks kept per side (`top_n = 20`) (`tick_extremes.py:149, 214`). OURS. Matches doc `LAYER_PROVENANCE_AUDIT.md:170`.
  5. Session tagging: Asian (00-08), European (08-13), Overlap (13-16:30), American (16:30-21), Off-session (21-24 UTC) (`tick_extremes.py:80-96`). Matches doc `LAYER_PROVENANCE_AUDIT.md:171`.
  6. Funding window context: $\pm 30$ minutes of 00:00, 08:00, 16:00 UTC resets (`tick_extremes.py:98-106`). Matches doc `LAYER_PROVENANCE_AUDIT.md:172, 179`.
  7. Price change calculation: `pct = 100 * (c - o) / o` over the bucket (`tick_extremes.py:58`). Matches doc `LAYER_PROVENANCE_AUDIT.md:173`.
  8. Flagger cooldown: 30 minutes (`cooldown_ms = 1800000`) (`tick_flagger.py:142`). Matches doc `LAYER_PROVENANCE_AUDIT.md:174`.
  9. Escalation bypass: Escalation to higher severity tier immediately bypasses cooldown (`tick_flagger.py:95-97`). Matches doc `LAYER_PROVENANCE_AUDIT.md:175`.
  10. Tier boundary definition: Boundary equals the least extreme value in a tier; signal emitted when value $\ge$ boundary (`tick_flagger.py:14-46, 62-69`). Matches doc `LAYER_PROVENANCE_AUDIT.md:176`.

### 3.5 Weekly-Low Bounce (`backtest/layers/wlow_bounce/`)
- **Doc References:** `MyTradingSys/research/wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md:10-50`, `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:238-270`, `wlow_bounce_param_labels.md:1-22`.
- **Code:** `MyTradingSys/backtest/layers/wlow_bounce/detector.py`, `status.py`.
- **Audit Findings:**
  1. Bollinger Band parameters: `bb_n = 20`, `bb_k = 2.0` (`detector.py:14`). SOURCED: operator chart. Matches doc `PRE_REG.md:14`.
  2. Upper Bollinger band calculation: SMA(20) $+ 2.0 \times \text{pstdev}(20)$ (`detector.py:28-34`). Matches standard TV formulation.
  3. RSI parameters: `rsi_n = 14`, `rsi_hi = 60.0`, `rsi_lo = 52.0` (`detector.py:15-17`). SOURCED (`rsi_hi=60.0` from operator quote "just under the RSI 60 line"). Matches doc `PRE_REG.md:15-17`.
  4. RSI slope ceiling: `slope_max = 3.0` points over hold window (`detector.py:18`). Matches doc `PRE_REG.md:18`.
  5. Band closeness threshold: `band_x = 0.005` (close $\ge$ upper $\times (1 - 0.5\%)$) (`detector.py:19`). Matches doc `PRE_REG.md:19`.
  6. Window lengths: Hold window `K = 4`, bounce window `B = 6`, max episode `HMAX = 24`, cooldown `COOLDOWN = 24` (`detector.py:20-23`). Matches doc `PRE_REG.md:20-23`.
  7. Week mode options: `iso` (prior completed Monday-anchored ISO week requiring 168 hourly bars) and `roll168` (rolling 168 bars) (`detector.py:24, 49-66`). Matches doc `PRE_REG.md:24`.
  8. Minimum bars requirement: `WLOW_MIN_BARS = 169` bars (at least one full week + 1 bar) (`live_runner_cli.py:250`). Matches doc.
  9. Hold condition logic: Requires $K$ consecutive closed bars where close $\ge$ upper $\times (1 - \text{band\_x})$ and RSI $\in [52, 60)$ and $|\Delta\text{RSI}| \le 3.0$ (`detector.py:69-80`). Matches doc `PRE_REG.md:32`.
  10. Episode lifecycle: States `TRIGGERED`, `NO_BOUNCE`, `EXPIRED`, `BROKEN`, `BOUNCED` (`detector.py:83-108`). Matches doc `PRE_REG.md:35-40`.
  11. Status recency: `active_bars = 6` (`detector.py:111`). Matches doc.
  12. Delta summation: $\sum(2 \times tbv - v)$ over episode window (`detector.py:124-126`). Matches repo standard CVD delta formulation.

---

## 4. Test Verification
All existing test suites for the 5 audited layers were executed under python pytest environment:
`python -m pytest MyTradingSys/backtest/layers/pitchfork MyTradingSys/backtest/layers/trendlines MyTradingSys/backtest/layers/timeframe MyTradingSys/backtest/layers/tick MyTradingSys/backtest/layers/wlow_bounce -q`
**Result:** 130 passed in 1.34s (100% pass).

---
Noticed: Rule P-01 in `RESEARCH_PITCHFORK_LAYER.md:24` specifies an ATR-scaled amplitude filter ($k \ge 2.5 \times \text{ATR}_{14}$) for pivot qualification, whereas `pitchfork_detector.py` implements a percentage change filter (`min_change_pct = 0.02` / `0.03`).
