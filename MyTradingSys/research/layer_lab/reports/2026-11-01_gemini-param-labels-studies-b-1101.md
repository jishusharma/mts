# Layer Lab Report: Parameter Labels Audit for Sim Desk Studies Part B

- **Task**: `gemini-param-labels-studies-b-1101`
- **Lane**: `CODEX`
- **Date**: 2026-11-01
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Studies Audited**: `krown.py`, `pitchfork.py`, `wavetrend.py`
- **Primary Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-01/studies_param_labels_b.md`

---

## 1. Executive Summary

A parameter audit was conducted across the three sim desk studies (`research/sim_desk/studies/krown.py`, `pitchfork.py`, `wavetrend.py`) and their underlying layers. Each parameter was cataloged with file:line location, default value, and labeled as either `SOURCED` (with verbatim quote or reference citation) or `OURS` (internal execution or default engineering parameter).

- **Total Parameters Swept**: 64
- **SOURCED Parameters**: 24 (37.5%)
- **OURS Parameters**: 40 (62.5%)
- **Deliverable First Line Verification**: `# SOURCED: 24, OURS: 40`

---

## 2. Parameter Counts by Study

| Study | Source File | Total Params | SOURCED | OURS | Sourced Concepts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `krown` | `research/sim_desk/studies/krown.py` | 21 | 7 | 14 | S5 21/55 EMA cross on 200 SMA side (KR-M01, KR-M02); S8 BBWP basis 7, lookback 100, 50th percentile confirmation (KR-Q01, KR-Q02) |
| `pitchfork` | `research/sim_desk/studies/pitchfork.py` | 23 | 6 | 17 | Andrews 3-pivot median line 80% rule; Modified Schiff 50% shift (Dologa / Schiff); Schiff time/price 50% shift ratios |
| `wavetrend` | `research/sim_desk/studies/wavetrend.py` | 20 | 11 | 9 | LazyBear 10/21/4 EMA/SMA, 0.015 CCI factor, 53/60 overbought/oversold bands, dual long/short sides; TrendCrypto2022 3-bar low stop, 1.5R target |

---

Noticed: Mathematical formulas and indicator core definitions are rigorously sourced from original publications (LazyBear scripts, Andrews/Schiff manuscripts, Krown TA101 rules), while operational desk harnesses (symbol, fees, DEV dates, timeouts, and ZigZag confirmation delays) are cleanly isolated and labeled as OURS.
