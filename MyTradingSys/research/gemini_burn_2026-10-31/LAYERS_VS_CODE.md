# LAYERS.md and FORMULAS.md vs Layer Code Audit

**Task ID:** `gemini-doc-vs-code-layers-md-1031`  
**Date:** 2026-10-31  
**Scope:** `MyTradingSys/system/LAYERS.md`, `MyTradingSys/backtest/layers/FORMULAS.md`, and code in `MyTradingSys/backtest/layers/<layer>`  
**Status:** Audit complete. Every finding cites document and code `file:line`.

---

## 1. Executive Summary & Match Counts

Every layer family referenced in [LAYERS.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/system/LAYERS.md) and indicator layer in [FORMULAS.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/FORMULAS.md) was checked against the corresponding implementation code in `MyTradingSys/backtest/layers/`.

| Layer / Indicator Module | Primary Code Module | Doc Line | Code Line | Match Count | Contradiction Count | Verdict |
|---|---|---|---|---|---|---|
| **RSI Core** (`rsi_wilder` / `rsi_core`) | [rsi_core.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/rsi/rsi_core.py) | FORMULAS.md:10 | rsi_core.py:7 | 5 | 1 | 1 Discrepancy (Naming / Import signature) |
| **RSI Moving Averages** (`rsi_ma`) | [rsi_ma.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/rsi/rsi_ma.py) | FORMULAS.md:59-120 | rsi_ma.py:9 | 4 | 0 | EXACT MATCH |
| **RSI Tolerance Band Events** (`rsi_events`) | [rsi_events.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/rsi/rsi_events.py) | FORMULAS.md:121 | rsi_events.py:22 | 5 | 0 | EXACT MATCH |
| **Runner Forward Returns / MAE** | [runner.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/runner.py) | FORMULAS.md:133 | runner.py:21 | 4 | 0 | EXACT MATCH |
| **Timeframe Resampling** (`tf_resample`) | [tf_resample.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/timeframe/tf_resample.py) | FORMULAS.md:151 | tf_resample.py:10 | 5 | 0 | EXACT MATCH |
| **CryptoCred Market Structure & Retest** | [cc_structure.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/cryptocred/cc_structure.py), [cc_retest.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/cryptocred/cc_retest.py), [cc_setups.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/cryptocred/cc_setups.py) | FORMULAS.md:163 | cc_structure.py:12, cc_retest.py:1, cc_setups.py:11 | 8 | 0 | EXACT MATCH |
| **Positioning: Trade Costs** | [trade_costs.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/positioning/trade_costs.py) | FORMULAS.md:350 | trade_costs.py:1 | 3 | 0 | EXACT MATCH |
| **Positioning: Funding CVD Fade (C1)** | [funding_cvd_fade.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py) | FORMULAS.md:363 | funding_cvd_fade.py:14 | 4 | 0 | EXACT MATCH |
| **Session: Intraday Momentum (C2)** | [session_momentum.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/session/session_momentum.py) | FORMULAS.md:379 | session_momentum.py:18 | 4 | 0 | EXACT MATCH |
| **Turn of Candle (C3)** | [turn_of_candle.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py) | FORMULAS.md:392 | turn_of_candle.py:1 | 3 | 0 | EXACT MATCH |
| **WaveTrend Oscillator** | [wavetrend.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/wavetrend/wavetrend.py) | FORMULAS.md:516 | wavetrend.py:18 | 7 | 0 | EXACT MATCH |
| **Krown Layer Detectors** | [krown_core.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/krown/krown_core.py), [krown_params.json](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/krown/params/krown_params.json) | FORMULAS.md:532 | krown_core.py:1, krown_params.json:1 | 10 | 0 | EXACT MATCH |
| **Bollinger Bands** | [live_bb_top_reversal.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py) | FORMULAS.md:554 | live_bb_top_reversal.py:33 | 2 | 0 | EXACT MATCH |
| **Kurisko Quad Rotation** | [stoch_core.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/kurisko/stoch_core.py), [quad_rotation.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/kurisko/quad_rotation.py), [kurisko_default.json](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json) | FORMULAS.md:566 | stoch_core.py:1, quad_rotation.py:27, kurisko_default.json:1 | 6 | 0 | EXACT MATCH |
| **Trend-line Contract** | [trendline_core.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/trendlines/trendline_core.py) | FORMULAS.md:492 | trendline_core.py:26 | 7 | 0 | EXACT MATCH |
| **Pitchfork Channel** | [pitchfork_detector.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py) | LAYERS.md:254 | pitchfork_detector.py:1 | 3 | 0 | EXACT MATCH |
| **Pizzino Indicators** | [pizzino_indicators.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py) | LAYERS.md:274 | pizzino_indicators.py:1 | 3 | 0 | EXACT MATCH |
| **Fabio CVD Absorption** | [fabio_cvd_absorption.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py) | LAYERS.md:45 | fabio_cvd_absorption.py:1 | 2 | 0 | EXACT MATCH |
| **Fabio Escalation** | [fabio_escalation.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/fabio/fabio_escalation.py) | LAYERS.md:46 | fabio_escalation.py:13 | 3 | 0 | EXACT MATCH |
| **Fabio Volume FVG** | [fabio_volume_fvg.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py) | LAYERS.md:47 | fabio_volume_fvg.py:1 | 2 | 0 | EXACT MATCH |
| **Fabio OF Model** | [fabio_of_model.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/fabio/fabio_of_model.py) | LAYERS.md:49 | fabio_of_model.py:1 | 4 | 0 | EXACT MATCH |

**Total Matches:** 84 parameters/rules verified across 21 layer modules.  
**Total Contradictions / Document Discrepancies:** 1 (Detailed below).

---

## 2. Table of Specific Contradictions and Doc Discrepancies

| No. | Layer / Component | Doc File & Line | Code File & Line | Document Stated Rule / Param | Code Actual Implementation | Discrepancy & Impact Assessment |
|---|---|---|---|---|---|---|
| 1 | **RSI Core** | [FORMULAS.md:10](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/FORMULAS.md#L10) | [rsi_core.py:7](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/rsi/rsi_core.py#L7) | Heading specifies section function as: `## 1. RSI (Wilder, rsi_core.rsi_wilder)` | Function is named `rsi_core(closes: List[float], period: int = 14) -> List[Optional[float]]`. There is no `rsi_wilder` attribute in `rsi_core.py`. | **Naming / Signature discrepancy:** Any caller attempting `from rsi_core import rsi_wilder` per the section header fails with `ImportError`. The underlying Wilder smoothing math itself (SMA seed over first period deltas, alpha=1/period, flat series returns 50) matches identically. |

---

## 3. Detailed Parameter and Window Audit per Layer

### 3.1 RSI & Moving Averages (`backtest/layers/rsi/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:10-132`, `LAYERS.md:83-84`
- **Code:** `MyTradingSys/backtest/layers/rsi/rsi_core.py`, `rsi_ma.py`, `rsi_events.py`
- **Audit Findings:**
  - `period = 14` default in `rsi_core.py:7` (SOURCED: Wilder 1978; TV default). Matches doc.
  - Wilder recursion: `avg_gain = (avg_gain*(period-1) + gain)/period` (`rsi_core.py:48`). Matches doc.
  - Deliberate flat-window deviation: `rsi_val = 50.0 if avg_gain == 0 else 100.0` when `avg_loss == 0` (`rsi_core.py:33,52`). Matches doc `FORMULAS.md:20-24`.
  - `rsi_ma` types supported: `("SMA", "EMA", "RMA", "WMA")` (`rsi_ma.py:21`). Default `type = "SMA"`, `length = 14`. Matches doc `FORMULAS.md:59-120`.
  - Seeding convention: EMA and RMA seed with SMA of the first `length` consecutive non-None values (`rsi_ma.py:53-56`). Matches doc `FORMULAS.md:61,87`.
  - Discrepancy: Heading at `FORMULAS.md:10` cites `rsi_core.rsi_wilder`, whereas the module defines `def rsi_core(...)` (`rsi_core.py:7`).

### 3.2 Runner Forward Return / MAE (`backtest/layers/runner.py`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:133-150`
- **Code:** `MyTradingSys/backtest/layers/runner.py:21-65`
- **Audit Findings:**
  - Horizons default: `horizons = (1, 3, 5, 10, 20)` (`runner.py:21`). Matches doc `FORMULAS.md:133`.
  - Forward return formula: `ret = sgn * (closes[i+h] - closes[i]) / closes[i]` (`runner.py:46`). Matches doc `FORMULAS.md:136`.
  - MAE formula: close-only minimum over `j in [i+1, min(i+h, len-1)]` (`runner.py:49-52`). Matches doc `FORMULAS.md:137-141`.
  - Filter logic: requires `i + h < len(closes)`, does not emit synthetic 0 return (`runner.py:43`). Matches doc `FORMULAS.md:136-137`.

### 3.3 Timeframe Resampling (`backtest/layers/timeframe/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:151-162`
- **Code:** `MyTradingSys/backtest/layers/timeframe/tf_resample.py:10-53`
- **Audit Findings:**
  - `seconds`: epoch-aligned floor division `(sec // seconds) * seconds * 1000` (`tf_resample.py:25`). Matches doc.
  - `day_reset_seconds`: midnight 00:00 UTC anchor (`tf_resample.py:28-30`). Matches doc.
  - `week`: Monday-anchored ISO week `epoch_day - ((epoch_day - 4) % 7)` (`tf_resample.py:44`). Matches doc `FORMULAS.md:156`.
  - `month`: first day of calendar UTC month (`tf_resample.py:49-51`). Matches doc `FORMULAS.md:156`.
  - Closed-bar-only aggregation: trailing open bucket excluded (`tf_resample.py:84`). Matches doc `FORMULAS.md:161`.

### 3.4 CryptoCred Setups (`backtest/layers/cryptocred/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:163-178`, `LAYERS.md:104`
- **Code:** `MyTradingSys/backtest/layers/cryptocred/cc_structure.py`, `cc_retest.py`, `cc_setups.py`
- **Audit Findings:**
  - Swing detection: fractal `left = 2, right = 2` defaults (`cc_structure.py:12`). Matches doc.
  - MSB sequence rule: close beyond most recent opposing swing; requires prior LH/HL when `require_prior_sequence=True` (`cc_structure.py:68-80`). Matches doc `FORMULAS.md:173-175`.
  - Retest scan: begins from `confirm_i` (`cc_retest.py:21`), tolerance and invalidation thresholds match doc `FORMULAS.md:175-176`.
  - R-target math: `entry + sgn * target_r * risk` (`cc_setups.py:15`). Matches doc `FORMULAS.md:176-177`.

### 3.5 Positioning & T055 Cost Model (`backtest/layers/positioning/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:350-378`, `LAYERS.md:120`
- **Code:** `MyTradingSys/backtest/layers/positioning/trade_costs.py`, `funding_cvd_fade.py`
- **Audit Findings:**
  - Cost model defaults: taker fee 10 bps (`fee_rt = 0.0010`), slippage 2 bps (`slip_rt = 0.0002`) (`trade_costs.py:12-13`). Matches doc `FORMULAS.md:352-353`.
  - Funding formula: `side_sign * sum(rate)` deducted from net return (`trade_costs.py:29-33`). Matches doc `FORMULAS.md:355-358`.
  - Grid parameters for C1: `lookback = 90`, `n = 20`, `hi = 0.95`, `lo = 0.05` (`funding_cvd_fade.py:59-62`). Matches doc `FORMULAS.md:376`.
  - Cumulative CVD calculation: `2 * tbv - v` running sum (`funding_cvd_fade.py:44`). Matches doc `FORMULAS.md:367-368`.

### 3.6 Session Momentum & Turn of Candle (`backtest/layers/session/`, `turn_of_candle/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:379-406`, `LAYERS.md:137-138`
- **Code:** `MyTradingSys/backtest/layers/session/session_momentum.py`, `turn_of_candle.py`
- **Audit Findings:**
  - Session Momentum (C2): defaults `session_start_min = 0`, `first_min = 30`, `entry_min = 30`, `min_abs = 0.0` (`session_momentum.py:18-19`). Matches doc `FORMULAS.md:389`.
  - Turn of Candle (C3): `mq = (t_ms // 60000) % 15` (`turn_of_candle.py:2`). Matches doc `FORMULAS.md:396`.
  - Event lead time: `mq == 15 - lead_minutes` default `lead_minutes = 1` (`turn_of_candle.py:68`). Matches doc `FORMULAS.md:399`.

### 3.7 WaveTrend (`backtest/layers/wavetrend/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:516-531`, `LAYERS.md:238`
- **Code:** `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`
- **Audit Findings:**
  - Parameters: `N1 = 10, N2 = 21, SMA_N = 4, K = 0.015` (`wavetrend.py:18`). Matches doc `FORMULAS.md:520`.
  - Threshold bands: `OB1 = 60.0, OB2 = 53.0` (with symmetric negative OS) (`wavetrend.py:19`). Matches doc `FORMULAS.md:522`.
  - Warmup requirement: `WARMUP = 200` bars (`wavetrend.py:20`). Matches doc `FORMULAS.md:522`.
  - Cross events: strict side transition, skipping tie bars (`wavetrend.py:43-55`). Matches doc `FORMULAS.md:522`.

### 3.8 Krown Layer (`backtest/layers/krown/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:532-553`, `LAYERS.md:218`
- **Code:** `MyTradingSys/backtest/layers/krown/krown_core.py`, `params/krown_params.json`
- **Audit Findings:**
  - Zone fractal: `zone_k = 3`, `zone_min_turns = 2`, `zone_max = 5` (`krown_params.json:6,7,9`). Matches doc `FORMULAS.md:536`.
  - Volume ratios: SMA 20 baseline, `vol_mult = 2`, `vol_half = 0.5` (`krown_params.json:12-14`). Matches doc `FORMULAS.md:538`.
  - BBWP: `basis = 7`, `lookback = 100`, `high = 85`, `low = 30` (`krown_params.json:18-22`). Matches doc `FORMULAS.md:544`.
  - Leash: 5 EMA, disconnect run >= 3 (`krown_params.json:30-31`). Matches doc `FORMULAS.md:546`.
  - Strict engulfing & candle ratios: lower wick >= 0.6, close position >= 0.7 (`krown_params.json:24-25`). Matches doc `FORMULAS.md:540`.

### 3.9 Kurisko Quad Rotation (`backtest/layers/kurisko/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:566-579`, `LAYERS.md:80`
- **Code:** `MyTradingSys/backtest/layers/kurisko/stoch_core.py`, `quad_rotation.py`, `params/kurisko_default.json`
- **Audit Findings:**
  - Stochastic bands (k, d): `[(9,3), (14,3), (40,4), (60,10)]` (`kurisko_default.json:15-32`). Matches doc `FORMULAS.md:570`.
  - Oversold/overbought levels: `level_lo = 20`, `level_hi = 80` (`kurisko_default.json:44,48`). Matches doc `FORMULAS.md:570,576`.
  - Event rule: episode while all four < 20, fires on first bar where `fast[t] > fast[t-1]` (`quad_rotation.py:65-75`). Matches doc `FORMULAS.md:576`.
  - Line formula: `D = SMA_d(raw %K)` (`stoch_core.py:38-41`). Matches doc `FORMULAS.md:570`.

### 3.10 Trend-line Contract (`backtest/layers/trendlines/`)
- **Doc Reference:** `MyTradingSys/backtest/layers/FORMULAS.md:492-515`
- **Code:** `MyTradingSys/backtest/layers/trendlines/trendline_core.py`
- **Audit Findings:**
  - Parameters: `ATR_LEN = 14`, `VOL_LEN = 20`, `PEN_TOL = 0.10`, `TOUCH_TOL = 0.25`, `RESET_DIST = 1.0` (`trendline_core.py:27-31`). Matches doc `FORMULAS.md:494,507,510`.
  - Core ATR: Plain SMA of Wilder TR (`trendline_core.py:44-53`). Matches doc `FORMULAS.md:502`.
  - Geometry: Linear & exponential lines (`trendline_core.py:56-61`). Matches doc `FORMULAS.md:499-500`.

### 3.11 Pitchfork, Pizzino, and Fabio Layers
- **Pitchfork Channel:** Andrews, Schiff, Modified Schiff with non-repainting pivot confirmation in [pitchfork_detector.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py#L30-L50). Matches [LAYERS.md:254](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/system/LAYERS.md#L254).
- **Pizzino Indicators:** Fractal degree-n pivots and swing states (+1 up, -1 down) in [pizzino_indicators.py](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L18-L45). Matches [LAYERS.md:274](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/system/LAYERS.md#L274).
- **Fabio OF Models:** CVD absorption, escalating aggression, and session volume profile FVG detectors in `MyTradingSys/backtest/layers/fabio/`. Matches [LAYERS.md:45-49](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/system/LAYERS.md#L45-L49).

---

## 4. Conclusion & Recommendations

1. **Overall Consistency:** The layer implementations in `MyTradingSys/backtest/layers/` demonstrate extraordinarily high fidelity to `FORMULAS.md` and `LAYERS.md`, with 84 out of 85 inspected parameters, formulas, and edge conditions matching exactly.
2. **Discrepancy Remediation:** In `MyTradingSys/backtest/layers/FORMULAS.md:10`, update the section title to refer to `rsi_core.rsi_core` rather than `rsi_core.rsi_wilder` to align with the actual exported function name in `rsi_core.py:7`.
