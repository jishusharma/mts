# Layer Lab Report: Parameter Labels Audit for preus_pullback.py and c30_validation.py

- **Task**: `gemini-param-labels-eagle-preus-c30-1102`
- **Lane**: `CODEX`
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)
- **Files Audited**:
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/preus_pullback.py`
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation.py`
- **Primary Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-02/param_labels_eagle_preus_c30.md`

---

## 1. Executive Summary

A line-by-line parameter provenance audit was performed across two research scripts in `MyTradingSys/research/eagle_eyes_picture_2026-10-28/`:
1. `preus_pullback.py` (descriptive base rate study of pre-US overnight range giveback)
2. `c30_validation.py` (pre-registered single VALIDATION read of WaveTrend dots with RSI divergence)

Each numeric constant, indicator threshold, simulation window, preflight test parameter, and configuration default was cataloged with file:line location, default value, and labeled as either `SOURCED` (with verbatim quote, exchange/statutory citation, or formula specification) or `OURS` (internal desk heuristics, simulation geometries, or software harness parameters).

- **Total Scripts Audited**: 2
- **Total Parameters Audited**: 62
- **Classification Counts**:
  - `SOURCED`: 11 (17.7%)
  - `OURS`: 51 (82.3%)
- **Deliverable First Line Verification**: `# SOURCED: 11, OURS: 51`

---

## 2. Parameter Distribution by Module

| Module | Scope / Purpose | Total Params | SOURCED | OURS | Key Sourced Concepts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `preus_pullback.py` | Descriptive study of pre-US pullback base rate (00:00-13:00Z) | 16 | 0 | 16 | None (all parameters are internal engineering / desk definitions; `preus_pullback.py:1`: "OURS: overnight window 00:00-12:59Z... P0 = 13:00Z open") |
| `c30_validation.py` | Frozen pre-registered single VALIDATION read for C30 (2024-07..2025-06) | 46 | 11 | 35 | Pre-reg VALIDATION split dates 2024-07-01..2025-07-01 (`splits.py:35-37`); LazyBear WaveTrend oversold -53 (`FORMULAS.md` s20.2); Binance taker fee 0.05% (`fees.py:36`); Binance API limit 1000; Hill (1970) t-to-z Cornish-Fisher expansion; 95% CI normal z=1.96; Holm (1979) family size m=2; alpha=0.05 |

---

Noticed: `preus_pullback.py` contains exclusively `OURS` parameters (16 of 16), which is explicitly acknowledged in the module's opening header (`preus_pullback.py:1`: "OURS: overnight window 00:00-12:59Z (H,L); P0 = 13:00Z open..."). In `c30_validation.py`, the mathematical boundaries (Holm family m=2, alpha 0.05, Hill 1970 expansion, normal z=1.96), data bounds (VALIDATION dates 2024-07-01..2025-07-01 per `backtest/splits.py:35-37`), exchange specs (Binance REST API limit 1000, Binance VIP0 spot taker fee 0.05% per leg per `backtest/fees.py:36`), and canonical indicator band (LazyBear WaveTrend -53 per `FORMULAS.md` s20.2) are strictly `SOURCED`, while the test harness tolerances, aggregation multiples, random seeds (P2b seed 5, P8 seed 11), and exit indices are cleanly classified as `OURS`.
