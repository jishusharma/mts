# Gemini Review Report: Cross-Vendor Review of 4 GPT Formula Audits (2026-10-30)

- Task: `gemini-review-gpt-formula-audits-1030`
- Producer: GPT (`research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-<layer>-layer.md`)
- Reviewer: Gemini (Antigravity)
- Date: 2026-10-30 (UTC)
- Primary deliverable: `research/gemini_audits_2026-10-30/review_gpt_formula_audits.md`

## Summary of Findings

A blind second-read recomputation was performed on all 4 GPT formula audit reports delivered on 2026-10-30:
1. `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-pizzino-layer.md`
2. `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-pitchfork-layer.md`
3. `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-kurisko-layer.md`
4. `MyTradingSys/research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-krown-layer.md`

Every re-derived number was recomputed independently by hand from `FORMULAS.md` (or layer `SPEC.md` where `FORMULAS.md` is `NOT_IN_DATA`) and compared against the layer implementation code.

### Detailed Layer Comparisons

1. **Pizzino** (`MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py:18-127`):
   - Scope in `MyTradingSys/backtest/layers/FORMULAS.md:3-8` does not contain Pizzino formulas (`NOT_IN_DATA`).
   - Ground truth specification: `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md:15-88`.
   - Degree-1 fractal pivots on 10-bar toy series:
     - Hand: `[(2, 14, 3, 'H'), (5, 7, 6, 'L'), (8, 16, 9, 'H')]`
     - Code: `pizzino_indicators.find_pivots(H, L, 1)` -> `[(2, 14, 3, 'H'), (5, 7, 6, 'L'), (8, 16, 9, 'H')]`
     - Status: SAME (Delta: 0).
   - Consecutive extension count from low (t=5, 'L'):
     - Hand: `[0, 1, 2, 3, 3]`
     - Code: `pizzino_indicators.bar_count_from(H, L, 5, 'L')` -> `[0, 1, 2, 3, 3]`
     - Status: SAME (Delta: 0).
   - 50% Midpoint and Half State at bar 9 (ph=16, pl=7, C[9]=12):
     - Hand: Midpoint `11.5`, state `strong`
     - Code: `pizzino_indicators.mid_line(16, 7)` -> `11.5`, `half_state(12, 11.5, 'weak')` -> `'strong'`
     - Status: SAME (Delta: 0).

2. **Pitchfork** (`MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:66-149`):
   - `MyTradingSys/backtest/layers/FORMULAS.md:492-514` (§19) defines 2-anchor linear/log trend lines, but does not specify 3-anchor median-line pitchfork geometry (`NOT_IN_DATA`).
   - Toy anchors: P0=(0, 100), P1=(4, 140), P2=(8, 120), evaluation at t=9:
     - Midpoint M = (6, 130), slope = (130-100)/(6-0) = 5.0. Hand: `5.0`. Code: `f.slope` -> `5.0`. (SAME, Delta: 0).
     - ML(9) = 100 + 5.0 * 9 = 145.0. Hand: `145.0`. Code: `f.get_ml(9)` -> `145.0`. (SAME, Delta: 0).
     - UML(9): ML(4) = 120.0, offset = +20.0, UML(9) = 145.0 + 20.0 = 165.0. Hand: `165.0`. Code: `f.get_uml(9)` -> `165.0`. (SAME, Delta: 0).
     - LML(9): ML(8) = 140.0, offset = -20.0, LML(9) = 145.0 - 20.0 = 125.0. Hand: `125.0`. Code: `f.get_lml(9)` -> `125.0`. (SAME, Delta: 0).
     - UW(9): channel width = 20.0, warning line offset = +40.0, UW(9) = 185.0. Hand: `185.0`. Code: `f.get_upper_warning_line(9)` -> `185.0`. (SAME, Delta: 0).
     - LQ(9): lower quarter line offset = -10.0, LQ(9) = 135.0. Hand: `135.0`. Code: `f.get_lower_quarter_line(9)` -> `135.0`. (SAME, Delta: 0).

3. **Kurisko** (`MyTradingSys/backtest/layers/kurisko/stoch_core.py:23-41`, `quad_rotation.py:33-112`):
   - Defined in `MyTradingSys/backtest/layers/FORMULAS.md:566-578` (§24).
   - Bar 6 stochastic outputs:
     - Raw %K (k=2): HH=97, LL=94.5, C=96.5 -> 100 * 2.0 / 2.5 = 80.0. Hand: `80.0`. Code: `80.0`. (SAME, Delta: 0).
     - D line (k=3, d=1): HH=97, LL=94.5, C=96.5 -> 100 * 2.0 / 2.5 = 80.0. Hand: `80.0`. Code: `80.0`. (SAME, Delta: 0).
     - D line (k=4, d=1): HH=98, LL=94.5, C=96.5 -> 100 * 2.0 / 3.5 = 57.142857143. Hand: `57.142857143`. Code: `57.142857142857146`. (SAME, Delta: 0).
     - D line (k=5, d=1): HH=99, LL=94.5, C=96.5 -> 100 * 2.0 / 4.5 = 44.444444444. Hand: `44.444444444`. Code: `44.44444444444444`. (SAME, Delta: 0).
     - Long rotation event at bar 6: Hand: `side='long'`, `episode_start_t=18000000`. Code: `side='long'`, `episode_start_t=18000000`. (SAME, Delta: 0).

4. **Krown** (`MyTradingSys/backtest/layers/krown/krown_core.py:84-310`):
   - Defined in `MyTradingSys/backtest/layers/FORMULAS.md:538-548` (§21).
   - Volume ratio at t=3 (n=3): mean(100, 120, 80) = 100, V=200 -> 200/100 = 2.0. Hand: `2.0`. Code: `kc.vol_ratio(v, 3)[3]` -> `2.0`. (SAME, Delta: 0).
   - Strict engulfing at t=1: prior (10.5, 9.5), current (h=11.5, l=9.0, c=11.0). Low 9.0 < 9.5 and close 11.0 > 10.5 -> bull. Hand: `bull`. Code: `kc.engulfing(h, l, c, 1)` -> `bull`. (SAME, Delta: 0).
   - Wilder RSI at t=9 (period=2): Hand: `66.796875`. Code: `kc.rsi(c, 2)[9]` -> `66.796875`. (SAME, Delta: 0).

## Match Table Summary
Total audited outputs across the 4 GPT reports: 17.
- SAME: 17
- DIFF: 0
