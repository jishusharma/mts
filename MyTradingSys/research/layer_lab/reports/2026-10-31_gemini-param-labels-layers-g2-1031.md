# Parameter Labels Audit Report: Pitchfork, Trendlines, Timeframe, Tick, Wlow_Bounce (G2)

**Card:** `gemini-param-labels-layers-g2-1031`  
**Date:** 2026-10-31 (UTC)  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/LAYER_PARAM_LABELS_G2.md`  
**Scope:** `MyTradingSys/backtest/layers/{pitchfork,trendlines,timeframe,tick,wlow_bounce}`  

---

## 1. Summary of Findings

Across the 5 target layer modules:
- Total tunable parameters and constants swept: **68**
- **SOURCED:** **30** (all verified with specific file:line citations and source quotes/formulas)
- **OURS:** **36** (discretizations, scan depths, tolerances, internal buffers)
- **OPERATOR-HYPOTHESIS / UNVERIFIED:** **2** (`7h` and `7h_epoch` in `timeframe/registry.json:20-21`)
- **Flagged SOURCED without a quote:** **0**
- **Unlabelled constants:** **0**

### Findings by Module
1. **Pitchfork** (`MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py`):
   - 24 constants swept (10 SOURCED, 14 OURS).
   - Core median line geometry, Schiff/Modified Schiff shifts, warning/quartile line formulas, and Mikula 3-bar swing confirmations are SOURCED (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-152`, `RESEARCH_PITCHFORK_LAYER.md:22-30`).
   - Hagopian 15% minimum approach progress threshold (`pitchfork_detector.py:202, 205`), 2% ZigZag reversal filter, and 4H scanner filters are OURS.
2. **Trendlines** (`MyTradingSys/backtest/layers/trendlines/trendline_core.py`):
   - 11 constants swept (2 SOURCED, 9 OURS).
   - Wilder ATR length 14 (`trendline_core.py:27`) and volume surge ratio 2.0x (`trendline_core.py:241`) are SOURCED (`FORMULAS.md:494`, `TRENDLINE_CONTRACT.md:65`).
   - Penetration tolerance 0.10 ATR, touch tolerance 0.25 ATR, reset distance 1.0 ATR, retest window 20, and fractal half-width k=3 are explicitly documented as OURS in the trendline contract (`TRENDLINE_CONTRACT.md:29-84`).
3. **Timeframe** (`MyTradingSys/backtest/layers/timeframe/registry.json`, `tf_resample.py`, `tf_realdata_gate.py`):
   - 17 parameters swept (12 SOURCED, 3 OURS, 2 OPERATOR-HYPOTHESIS).
   - Standard SI timeframes (1m..12h, 1d, 1w, 1M) and calendar constants (1440 min/day, 10080 min/week, Monday epoch day mod 4) are SOURCED.
   - Multi-day anchors (2d, 3d, 5d) and real-data verification tolerance 1e-6 are OURS.
   - `7h` intraday restart stub and `7h_epoch` drift are OPERATOR-HYPOTHESIS (`registry.json:20-21`).
4. **Tick** (`MyTradingSys/backtest/layers/tick/tick_extremes.py`, `tick_oi_extremes.py`, `tick_flagger.py`, `build_tiers.py`):
   - 13 parameters swept (3 SOURCED, 10 OURS).
   - Binance funding resets (00:00, 08:00, 16:00 UTC) and native 5m OI collection interval are SOURCED exchange parameters (`LAYER_PROVENANCE_AUDIT.md:178-179`).
   - Disjoint session boundaries (Asian 0..480m, European 480..780m, Overlap 780..990m, American 990..1260m), 30m funding window, 1.5x gap tier multiplier, top 20 extreme ranking depth, and 30m cooldown are OURS (`LAYER_PROVENANCE_AUDIT.md:170-174`).
5. **Weekly-Low Bounce** (`MyTradingSys/backtest/layers/wlow_bounce/detector.py`, `status.py`):
   - 16 parameters swept (7 SOURCED, 9 OURS).
   - Operator explicit request parameters (BB(20, 2), RSI 14, RSI hi 60, break weekly low, bounce) and 168h week length are SOURCED (`research/wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md:8-26`).
   - Discretizations (RSI floor 52, flat RSI slope max 3.0, BB upper proximity 0.5%, hold K=4, bounce B=6, episode HMAX=24, cooldown 24 bars) are documented as OURS in `PRE_REG.md:21-28`.

Noticed: The trendline contract (`TRENDLINE_CONTRACT.md`) and weekly-low bounce pre-registration (`PRE_REG.md`) are exceptionally thorough examples of distinguishing trader-sourced ideas from algorithmic engineering choices, explicitly cataloging every threshold as SOURCED or OURS before implementation.
