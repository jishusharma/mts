# Layer Lab Report: Audit of LAYERS.md & Research Notes vs Layer Code (Group 2)

**Task ID:** `gemini-doc-vs-code-layers-g2-1031`  
**Lane:** CODEX  
**Reviewer:** Gemini 3.8 Flash (independent code-vs-doc audit)  
**Date:** 2026-10-31 (UTC 2026-10-31)  
**Target Layers (Group 2):** `pitchfork`, `trendlines`, `timeframe`, `tick`, `wlow_bounce`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE_G2.md`  

---

## 1. Scope & Objective

Audit every stated parameter, window, formula, and rule documented across:
- `MyTradingSys/system/LAYERS.md`
- `MyTradingSys/backtest/layers/FORMULAS.md`
- Research specifications and contracts: `RESEARCH_PITCHFORK_LAYER.md`, `TRENDLINE_CONTRACT.md`, `TEST_PLAN.md`, `LAYER_PROVENANCE_AUDIT.md`, `PRE_REG.md`

against the actual implementation code under:
- `MyTradingSys/backtest/layers/pitchfork/`
- `MyTradingSys/backtest/layers/trendlines/`
- `MyTradingSys/backtest/layers/timeframe/`
- `MyTradingSys/backtest/layers/tick/`
- `MyTradingSys/backtest/layers/wlow_bounce/`

---

## 2. Key Audit Findings & Match Counts

1. **Total Layers Audited:** 5 layer modules (`pitchfork`, `trendlines`, `timeframe`, `tick`, `wlow_bounce`).
2. **Parameters & Mathematical Rules Verified:** 54 discrete items.
   - Exact Matches: 53 / 54 (SOURCED: see comparison table in [LAYERS_VS_CODE_G2.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g2-1031/MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE_G2.md)).
   - Discrepancies / Contradictions: 1 / 54 (SOURCED: `RESEARCH_PITCHFORK_LAYER.md:24` vs `pitchfork_detector.py:338, 395`).
3. **Identified Discrepancy:**
   - **Pitchfork Pivot Filter:** `RESEARCH_PITCHFORK_LAYER.md:24` specifies that swing pivots $P_0, P_1, P_2$ must have clearance $N \ge 3$ bars and amplitude exceeding $k \ge 2.5 \times \text{ATR}_{14}$. In `pitchfork_detector.py:334-399`, the ZigZag pivot detector uses percentage-based reversal gating (`min_change_pct = 0.02` for 1D, `0.03` for 4H) without an ATR filter.
4. **Subsystem Agreement:**
   - **Pitchfork Channel Math:** Exact match on Standard, Schiff (50% price & time shift), Modified Schiff (50% price shift), warning lines, quartile lines, 80% ML reach rule, 15% Hagopian failure approach gate, and anchored Volume Profile VA confluence (`pitchfork_detector.py:51-305, 468-482`).
   - **Trendlines:** Exact match on v1.1 contract rules including ATR 14 SMA, tolerances (0.10 poke, 0.25 touch, 1.0 reset distance), $k=3$ strict fractal anchors, spacing [10, 200], max age 500 bars, and volume anchor 2.0x surge test (`trendline_core.py:26-135`).
   - **Timeframe Resampling:** Exact match on seconds floor bucketing, midnight 00:00 UTC day-reset (7h), ISO Monday-anchored weeks, calendar month boundaries, and closed-bar emission rule (`tf_resample.py:9-106`).
   - **Tick Extremes & Flagger:** Exact match on timeframes (1, 2, 3, 5, 10, 15m), 5 channels (`net_delta`, `cvd_change`, `volume`, `price_change_pct`, `oi_delta`), $1.5\times$ median gap tiering, top 20 cutoff, and 30m flagger cooldown (`tick_extremes.py:80-214`, `tick_flagger.py:14-142`).
   - **Weekly-Low Bounce:** Exact match on Bollinger (20, 2.0), RSI (14, hi 60.0, lo 52.0), slope cap 3.0, upper band $0.5\%$ proximity, hold window $K=4$, bounce window $B=6$, ISO 168-hour completed week reference, and 169 minimum bars requirement (`detector.py:13-108`, `live_runner_cli.py:250`).

---

## 3. Unit Test Verification

All unit tests for the 5 audited layers pass:
```
python -m pytest MyTradingSys/backtest/layers/pitchfork MyTradingSys/backtest/layers/trendlines MyTradingSys/backtest/layers/timeframe MyTradingSys/backtest/layers/tick MyTradingSys/backtest/layers/wlow_bounce -q
130 passed in 1.34s
```

---
Noticed: Rule P-01 in `RESEARCH_PITCHFORK_LAYER.md:24` specifies an ATR-scaled amplitude filter ($k \ge 2.5 \times \text{ATR}_{14}$) for pivot qualification, whereas `pitchfork_detector.py` implements a percentage change filter (`min_change_pct = 0.02` / `0.03`).
