# Parity Audit: Code Rules & Parameters vs Sourced Quotes

- **Auditor:** Gemini (Antigravity / JIS-NUC)
- **Role:** Codebase Parity & Traceability Auditor
- **Date:** 2026-10-30
- **Scope:** Inverse trace from `MyTradingSys/backtest/layers/` back to trader quotes (`WIRING_MALKAN_KROWN.csv`, `WIRING_TOM_FABIO_HABIB.csv`).

---

## 1. Overview & Methodology

This audit inspects every active layer directory in `MyTradingSys/backtest/layers/` (`rsi`, `krown`, `fabio`, `kurisko`, `pizzino`, `wavetrend`, `pitchfork`, `trendlines`, `alerts`) and verifies whether implemented rules, constants, and parameters trace back to verified trader quotes (`SOURCED`) or whether they represent engineer judgements (`OURS`), operator hypotheses, or unsourced additions.

---

## 2. Per-Layer Parity Summary

| Layer Folder | Primary Trader / Source | Sourced Rules Traced | Unsourced / Engineering Rules | Parity Status | Recommendation |
|---|---|:---:|:---:|:---:|---|
| `rsi` | Malkan (MalkanView) | PRD, NRD, 40/60 regimes, 3-10 candle window, decimal diff | Generic hidden divergence (`krown_hidden_divergence.py`) | **MISPLACED** | Move generic hidden divergence out of Malkan layer to Krown confluence |
| `krown` | Eric Krown | BBWP 85/30/50, 21/55 EMA, 200 SMA, 5 EMA leash, 3-crows, Vol 2x | Zone lookback 250, swing tol 0.01, doji 0.1, hammer 0.6 | **SOUND** | SOURCED and OURS explicitly segregated in `krown_params.json` |
| `fabio` | Fabio Valentini | CVD absorption, value area, balance, curve, exhaustion | Session gate fallback constants | **SOUND** | Code rules trace to `WIRING_TOM_FABIO_HABIB.csv` |
| `kurisko` | John Kurisko | (9,3),(14,3),(40,4),(60,10) stochastics, %D line, oversold 20 | Short side mirror (>80), 4-RSI band option | **LABELLED** | Label short side `OURS` and 4-RSI `OPERATOR-HYPOTHESIS` |
| `pizzino` | Michael & Jason Pizzino | 3-bar length, HH+HL test, 50% line, next-pivot target | Fractal rule, state formula, W, L, N, tol, R, RRmin, 2R | **LABELLED** | SOURCED vs OURS explicitly tagged in module header |
| `wavetrend` | LazyBear (lonestar108) | N1=10, N2=21, SMA=4, K=0.015, OB1=60, OB2=53 | WARMUP=200, D_TOL=1e-9 | **SOUND** | Observation-only; parameter constants strictly cited |
| `pitchfork` | Andrews, Schiff, Morge | Andrews, Schiff, Modified Schiff geometry, Hagopian | N/A (Textbook public source) | **LABELLED** | Label `EXTERNAL_PUBLIC` (not trader-specific) |
| `trendlines` | Technical Analysis Standard | Swing pivot connections, ATR touch | k=3, spacing 10..200, age cap 500, ATR tolerances | **LABELLED** | Explicitly documented as `OURS` (contract) |
| `alerts` | MTS Core Infrastructure | None (Sink infrastructure only) | Formatter, JSONL appender, runner harnesses | **NOT COVERED** | Infrastructure only; does not enforce trader rules |

---

## 3. Key Findings & Actions

1. **RSI Layer Isolation (Operator 2026-10-28 Rule):**
   - Malkan's layer strictly specifies Positive Reversal (PRD) and Negative Reversal (NRD) divergence with trend conditions.
   - `krown_hidden_divergence.py` implements textbook hidden divergence with **no trend condition**.
   - It is correctly labeled in code comments as `KROWN-CONFLUENCE`, but sits inside `backtest/layers/rsi/`. Recommendation: isolate in a shared confluence module or move under `backtest/layers/krown/`.
2. **Kurisko Short Arm:**
   - Kurisko only explicitly traded the long turn-up from $< 20$.
   - The short arm ($> 80$) is an MTS synthetic mirror. It is properly marked `OURS` in `kurisko_default.json`.
3. **Alerts & Runner Harnesses:**
   - `backtest/layers/alerts/` is marked `NOT COVERED` as it is purely testnet event routing infrastructure without trading logic.
