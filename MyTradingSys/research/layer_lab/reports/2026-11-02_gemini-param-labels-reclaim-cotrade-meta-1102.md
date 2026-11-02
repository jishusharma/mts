# Layer Lab Report: Parameter Labels Audit for reclaim.py, ladder_math.py, us_window_stats.py, features.py, analyze.py

- **Task**: `gemini-param-labels-reclaim-cotrade-meta-1102`
- **Lane**: `CODEX`
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (low) worker (Antigravity JIS-NUC)
- **Files Audited**:
  - `MyTradingSys/research/reclaim_close_stop_2026-11/reclaim.py`
  - `MyTradingSys/research/testnet_cotrade_2026-10-31/ladder_math.py`
  - `MyTradingSys/research/testnet_cotrade_2026-10-31/us_window_stats.py`
  - `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/features.py`
  - `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/analyze.py`
- **Primary Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-02/param_labels_reclaim_cotrade_meta.md`

---

## 1. Executive Summary

A line-by-line parameter provenance audit was performed across five research scripts in `reclaim_close_stop_2026-11`, `testnet_cotrade_2026-10-31`, and `meta_label_tom_fabio_2026-10-31`. Each numeric constant, indicator length, filter cut, execution grid, and configuration default was cataloged with file:line location, default value, and labeled as either `SOURCED` (with verbatim quote, exchange/statutory citation, or formula specification) or `OURS` (internal execution or research harness defaults).

- **Total Scripts Audited**: 5
- **Total Parameters Audited**: 68
- **Classification Counts**:
  - `SOURCED`: 21 (30.9%)
  - `OURS`: 47 (69.1%)
- **Deliverable First Line Verification**: `# SOURCED: 21, OURS: 47`

---

## 2. Parameter Distribution by Module

| Module | Scope / Purpose | Total Params | SOURCED | OURS | Key Sourced Concepts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `reclaim.py` | Fractal swing break & reclaim study | 13 | 2 | 11 | Wilder 14 ATR (`FORMULAS.md` s12); Binance taker fee 0.05% (`fees.py:36`) |
| `ladder_math.py` | Co-trade doubling ladder scale-in | 8 | 2 | 6 | Operator order base size ($100 USD); doubling rung sequence |
| `us_window_stats.py` | US cash open window empirical distributions | 10 | 5 | 5 | NYSE open 09:30 ET; 60m pre-open release; 30m IB; EDT -4h offset |
| `features.py` | Layer features at trade entry | 22 | 8 | 14 | BBWP 7/100; Wilder 14 RSI; WaveTrend -2..+2 zones; EU/US cash hours; Malkan 40/60 bands; DEV dates |
| `analyze.py` | Meta-label purged blocked CV & evaluation | 15 | 4 | 11 | BBWP 85 expansion; Malkan 40/60 RSI; PTJ trend sign; WaveTrend ob/os thresholds |

---

Noticed: Mathematical indicators (BBWP, RSI, WaveTrend), institutional market hours (US cash open 09:30, London open 07:00, US EDT -4h offset), and fee limits (Binance taker 0.05%) are strictly verified against source literature and exchange specifications, whereas simulation geometries, solver hyperparameters (IRLS $\lambda=1.0$, 50 iters), and statistical harness seeds are cleanly isolated and labeled as OURS.
