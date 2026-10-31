# Layer Lab Report: Audit of LAYERS.md & FORMULAS.md vs Layer Code

**Task ID:** `gemini-doc-vs-code-layers-md-1031`  
**Lane:** CODEX  
**Reviewer:** Gemini 3.8 Flash (independent code-vs-doc audit)  
**Date:** 2026-10-31 (UTC 2026-10-31)  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE.md`

---

## 1. Scope & Objective

Audit every stated parameter, window, formula, and rule documented across:
- `MyTradingSys/system/LAYERS.md`
- `MyTradingSys/backtest/layers/FORMULAS.md`

against the actual implementation code under `MyTradingSys/backtest/layers/<layer>/`.

---

## 2. Key Audit Findings & Match Counts

1. **Total Layers & Indicator Modules Audited:** 21 modules.
2. **Parameters & Mathematical Rules Verified:** 85 discrete items.
   - Exact Matches: 84 / 85 (SOURCED: see table in `LAYERS_VS_CODE.md:14-36`).
   - Contradictions / Doc Discrepancies: 1 / 85 (SOURCED: `FORMULAS.md:10` vs `rsi_core.py:7`).
3. **Identified Discrepancy:**
   - **RSI Core function reference:** In `MyTradingSys/backtest/layers/FORMULAS.md:10`, the section header cites `## 1. RSI (Wilder, rsi_core.rsi_wilder)`. However, in `MyTradingSys/backtest/layers/rsi/rsi_core.py:7`, the function is defined as `def rsi_core(closes: List[float], period: int = 14) -> List[Optional[float]]`. No function `rsi_wilder` exists in that module.
4. **Subsystem Agreement:**
   - **RSI / MA / Events:** Exact match on Wilder smoothing, SMA/EMA/WMA/RMA seeding, and flat-series neutral 50.0 value (`rsi_core.py:33`, `rsi_ma.py:21`, `rsi_events.py:22`).
   - **Timeframe Resampling:** Exact match on seconds, day_reset_seconds, Monday-anchored ISO weeks, and month boundaries (`tf_resample.py:10-53`).
   - **CryptoCred:** Exact match on fractal swings, MSB break of last opposing swing, retest invalidation, and R-target math (`cc_structure.py:12`, `cc_retest.py:21`, `cc_setups.py:15`).
   - **Positioning & Cost Model:** Exact match on taker fee (10 bps), slippage (2 bps), funding sign convention, and CVD divergence (`trade_costs.py:12-13`, `funding_cvd_fade.py:44,59`).
   - **Timing (C2/C3):** Exact match on session momentum windows (`session_momentum.py:18`) and minute-of-quarter candle turn (`turn_of_candle.py:2,68`).
   - **WaveTrend:** Exact match on (10, 21, 4, 0.015), 60/53 thresholds, and WARMUP=200 (`wavetrend.py:18-20`).
   - **Krown:** Exact match on all 47 parameters in `krown_params.json` vs `FORMULAS.md` section 21.
   - **Kurisko Quad Rotation:** Exact match on stochastic bands [(9,3), (14,3), (40,4), (60,10)], 20/80 levels, and episode start/turn rule (`stoch_core.py:38`, `quad_rotation.py:65`).
   - **Trendlines:** Exact match on contract v1.1 tolerances (0.10/0.25/1.0 x ATR_b) and plain SMA ATR (`trendline_core.py:27-53`).
   - **Fabio OF Models:** Exact match on CVD absorption, escalation, and volume profile FVG definitions (`fabio_cvd_absorption.py:1`, `fabio_escalation.py:13`, `fabio_volume_fvg.py:1`).

---

## 3. Deliverables Status

- Full comparison table generated: [LAYERS_VS_CODE.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE.md)
- Report generated: [2026-10-31_gemini-doc-vs-code-layers-md-1031.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-md-1031/MyTradingSys/research/layer_lab/reports/2026-10-31_gemini-doc-vs-code-layers-md-1031.md)
- Zero layer or engine code touched (pure research / audit).
