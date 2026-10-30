# Gemini Review of GPT Formula Audits (2026-10-30)

- Producer: GPT (`research/layer_lab/reports/2026-10-30_gpt-audit-formulas-vs-<layer>-layer.md`)
- Reviewer: Gemini (Antigravity)
- Date: 2026-10-30 (UTC)
- Goal: Blind second read of the 4 GPT formula audits delivered 2026-10-30 (Pizzino, Pitchfork, Kurisko, Krown). Recompute each re-derived number from `FORMULAS.md` and layer code; report SAME/DIFF with file:line; facts only, no verdicts.

## Review Table

| Layer | Formula / Output Item | GPT Hand Value | GPT Code Value | Gemini Hand Value | Gemini Code Value | Match (SAME / DIFF) | Delta | Source & Evidence (file:line) | Label |
|---|---|---|---|---|---|---|---|---|---|
| Pizzino | Pivot detection (n=1 fractal, alternating) | `[(2, 14, 3, H), (5, 7, 6, L), (8, 16, 9, H)]` | `[(2, 14, 3, H), (5, 7, 6, L), (8, 16, 9, H)]` | `[(2, 14, 3, 'H'), (5, 7, 6, 'L'), (8, 16, 9, 'H')]` | `[(2, 14, 3, 'H'), (5, 7, 6, 'L'), (8, 16, 9, 'H')]` | SAME | 0 | `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md:15-33`; `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py:18-43` | SOURCED (ME quotes in SPEC: ME:184, ME:154, ME:161; formula OURS in SPEC.md:15-18) |
| Pizzino | Consecutive extension count from low (t=5, 'L') | `[0, 1, 2, 3, 3]` | `[0, 1, 2, 3, 3]` | `[0, 1, 2, 3, 3]` | `[0, 1, 2, 3, 3]` | SAME | 0 | `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md:63-75`; `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py:96-113` | SOURCED (ME:63-75; rule OURS in SPEC.md:63-68) |
| Pizzino | 50% midpoint and half state at bar 9 (ph=16, pl=7, C[9]=12) | Midpoint `11.5`, state `strong` | Midpoint `11.5`, state `strong` | Midpoint `11.5`, state `strong` | Midpoint `11.5`, state `strong` | SAME | 0 | `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md:79-88`; `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py:117-127` | SOURCED (ME:79-88; rule OURS in SPEC.md:79-86) |
| Pitchfork | Median line slope (P0=(0,100), P1=(4,140), P2=(8,120)) | `5.0` | `5.0` | `5.0` | `5.0` | SAME | 0 | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:81-91` | OURS (code implementation; NOT_IN_DATA in FORMULAS.md:492-514) |
| Pitchfork | Median line at t=9: ML(9) | `145.0` | `145.0` | `145.0` | `145.0` | SAME | 0 | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:131-133` | OURS (code implementation; NOT_IN_DATA in FORMULAS.md:492-514) |
| Pitchfork | Upper median line at t=9: UML(9) | `165.0` | `165.0` | `165.0` | `165.0` | SAME | 0 | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:93-118,135-137` | OURS (code implementation; NOT_IN_DATA in FORMULAS.md:492-514) |
| Pitchfork | Lower median line at t=9: LML(9) | `125.0` | `125.0` | `125.0` | `125.0` | SAME | 0 | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:93-121,139-141` | OURS (code implementation; NOT_IN_DATA in FORMULAS.md:492-514) |
| Pitchfork | Upper warning line at t=9: UW(9) | `185.0` | `185.0` | `185.0` | `185.0` | SAME | 0 | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:114-118,143-145` | OURS (code implementation; NOT_IN_DATA in FORMULAS.md:492-514) |
| Pitchfork | Lower quarter line at t=9: LQ(9) | `135.0` | `135.0` | `135.0` | `135.0` | SAME | 0 | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:119-122,147-149` | OURS (code implementation; NOT_IN_DATA in FORMULAS.md:492-514) |
| Kurisko | Raw stochastic %K at bar 6 (k=2) | `80.0` | `80.0` | `80.0` | `80.0` | SAME | 0 | `MyTradingSys/backtest/layers/FORMULAS.md:570,578`; `MyTradingSys/backtest/layers/kurisko/stoch_core.py:23-34` | SOURCED (`FORMULAS.md:570` "raw K = 100*(C[t]-LL)/(HH-LL)") |
| Kurisko | Stochastic line D at bar 6 (k=3, d=1) | `80.0` | `80.0` | `80.0` | `80.0` | SAME | 0 | `MyTradingSys/backtest/layers/FORMULAS.md:570,578`; `MyTradingSys/backtest/layers/kurisko/stoch_core.py:37-41`; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:60-67` | SOURCED (`FORMULAS.md:570` "Plotted line = D = SMA_d(raw %K_k)") |
| Kurisko | Stochastic line D at bar 6 (k=4, d=1) | `57.142857143` | `57.142857143` | `57.142857143` | `57.142857142857146` | SAME | 0 (within float prec `~1.4e-14`) | `MyTradingSys/backtest/layers/FORMULAS.md:570,578`; `MyTradingSys/backtest/layers/kurisko/stoch_core.py:37-41`; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:60-67` | SOURCED (`FORMULAS.md:570,578`) |
| Kurisko | Stochastic line D at bar 6 (k=5, d=1) | `44.444444444` | `44.444444444` | `44.444444444` | `44.44444444444444` | SAME | 0 (within float prec `~1.4e-14`) | `MyTradingSys/backtest/layers/FORMULAS.md:570,578`; `MyTradingSys/backtest/layers/kurisko/stoch_core.py:37-41`; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:60-67` | SOURCED (`FORMULAS.md:570,578`) |
| Kurisko | Long rotation event at bar 6 | `side='long'`, `episode_start_t=18000000` | `side='long'`, `episode_start_t=18000000` | `side='long'`, `episode_start_t=18000000` | `side='long'`, `episode_start_t=18000000` | SAME | 0 | `MyTradingSys/backtest/layers/FORMULAS.md:576,578`; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:71-99,102-112` | SOURCED (`FORMULAS.md:576,578`) |
| Krown | KR-V01/V02 volume ratio at t=3 (n=3) | `2.0` | `2.0` | `2.0` | `2.0` | SAME | 0 | `MyTradingSys/backtest/layers/FORMULAS.md:538`; `MyTradingSys/backtest/layers/krown/krown_core.py:84-90` | SOURCED (`FORMULAS.md:538` "ratio = V / mean of the n=20 PRIOR volumes") |
| Krown | KR-C06 strict engulfing at t=1 | `bull` | `bull` | `bull` | `bull` | SAME | 0 | `MyTradingSys/backtest/layers/FORMULAS.md:540`; `MyTradingSys/backtest/layers/krown/krown_core.py:142-150` | SOURCED (`FORMULAS.md:540` "low < prior low AND close > prior HIGH") |
| Krown | KR-S02 Wilder RSI at t=9 (period=2) | `66.796875` | `66.796875` | `66.796875` | `66.796875` | SAME | 0 | `MyTradingSys/backtest/layers/FORMULAS.md:548`; `MyTradingSys/backtest/layers/krown/krown_core.py:289-310` | SOURCED (`FORMULAS.md:548` Wilder recursion formula) |

## Coverage Summary
- Pizzino: 3 re-derived numbers / outputs audited against `SPEC.md:15-88` and `pizzino_indicators.py:18-127`. Note: `FORMULAS.md:3-8` does not cover Pizzino (NOT_IN_DATA in FORMULAS.md). All 3 match code and SPEC hand calculation.
- Pitchfork: 6 geometric outputs (ML, UML, LML, UW, LQ, slope) audited against `pitchfork_detector.py:66-149`. Section 19 of `FORMULAS.md:492-514` specifies 2-anchor lines, not median line pitchfork geometry (NOT_IN_DATA in FORMULAS.md). All 6 match code and hand calculation.
- Kurisko: 5 outputs (raw %K, 3 D lines, and long rotation event) audited against `FORMULAS.md:566-578` and `quad_rotation.py:33-112`. All 5 match code and FORMULAS.md §24 hand calculation.
- Krown: 3 outputs (volume ratio, strict engulfing, Wilder RSI) audited against `FORMULAS.md:538-548` and `krown_core.py:84-310`. All 3 match code and FORMULAS.md §21 hand calculation.
- Total checked items: 17 outputs across 4 reports.
- Result: 17 SAME, 0 DIFF. All code outputs match hand re-computations exactly.
