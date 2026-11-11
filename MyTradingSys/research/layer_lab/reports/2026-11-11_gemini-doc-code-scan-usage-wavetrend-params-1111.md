COUNTS: CONSISTENT=5 CONTRADICTION=0 NOT_IN_DATA=0

# Contradiction Scan Report: `USAGE_wavetrend.md` Parameters vs `wavetrend.py` Code Defaults

- **Task**: `gemini-doc-code-scan-usage-wavetrend-params-1111`
- **Date**: 2026-11-11 UTC
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In**:
  - `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md` (read)
  - `MyTradingSys/backtest/layers/wavetrend/wavetrend.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-code-scan-usage-wavetrend-params-1111.md` (new)
- **Scope Out**: No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.

---

## Executive Summary

An audit of parameter clauses and cross definitions stated in `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md` was performed against the code implementation and constant definitions in `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`.

Across the 5 primary parameter groups defined in the task scope (Channel length, Average length, Overbought levels, Oversold levels, and Cross definition):
- **CONSISTENT**: 5
- **CONTRADICTION**: 0
- **NOT_IN_DATA**: 0

All parameters and cross mechanics documented in `USAGE_wavetrend.md` match the default constants and execution logic in `wavetrend.py` with zero discrepancies.

---

## Detailed Clause Comparison Table

| # | Parameter / Logic Group | `USAGE_wavetrend.md` Citation & Quote | `wavetrend.py` Citation & Quote | Status | Audit Analysis & Verification |
|---|---|---|---|---|---|
| 1 | Channel Length (`n1`) | `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:12`: `"esa = EMA(ap, n1) (default n1 = 10)"` and `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:62`: `"- Channel Length (n1): 10 (SOURCED)"` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16`: `"N1, N2, SMA_N, K = 10, 21, 4, 0.015   # SOURCED: Crosses:14-21"` | `CONSISTENT` | SOURCED (`USAGE_wavetrend.md:12,62`, `wavetrend.py:16`). Both set channel length `n1` / `N1` to 10. |
| 2 | Average Length (`n2`) | `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:15`: `"wt1 = EMA(ci, n2) (default n2 = 21)"` and `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:63`: `"- Average Length (n2): 21 (SOURCED)"` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16`: `"N1, N2, SMA_N, K = 10, 21, 4, 0.015   # SOURCED: Crosses:14-21"` | `CONSISTENT` | SOURCED (`USAGE_wavetrend.md:15,63`, `wavetrend.py:16`). Both set average length `n2` / `N2` to 21. |
| 3 | Overbought Levels (`obLevel1`, `obLevel2`) | `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:17`: `"fixed overbought (OB) bands at +53/+60"` and `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:64-65`: `"- Overbought Level 1 (obLevel1): 60 (SOURCED)"` and `"- Overbought Level 2 (obLevel2): 53 (SOURCED)"` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17`: `"OB1, OB2 = 60.0, 53.0                  # SOURCED: Crosses:9-12 (os = negatives)"` and `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:35-38`: `"if v >= OB1: return \"ob2\" \n if v >= OB2: return \"ob1\""` | `CONSISTENT` | SOURCED (`USAGE_wavetrend.md:17,64-65`, `wavetrend.py:17,35-38`). Both specify +60 (`OB1`) and +53 (`OB2`). |
| 4 | Oversold Levels (`osLevel1`, `osLevel2`) | `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:17`: `"oversold (OS) bands at -53/-60"` and `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:66-67`: `"- Oversold Level 1 (osLevel1): -60 (SOURCED)"` and `"- Oversold Level 2 (osLevel2): -53 (SOURCED)"` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17`: `"OB1, OB2 = 60.0, 53.0                  # SOURCED: Crosses:9-12 (os = negatives)"` and `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:39-42`: `"if v <= -OB1: return \"os2\" \n if v <= -OB2: return \"os1\""` | `CONSISTENT` | SOURCED (`USAGE_wavetrend.md:17,66-67`, `wavetrend.py:17,39-42`). Both specify -60 (`-OB1`) and -53 (`-OB2`). |
| 5 | Cross Definition (`wt1` vs `wt2`) | `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:18`: `"Bullish cross when wt1 crosses above wt2 (green dot); bearish cross when wt1 crosses below wt2 (red dot)."` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:46-48`: `"+1 up-cross, -1 down-cross, 0 none. \"le\": fires at the first bar strictly on the opposite side of the last strict side; a tie bar is skipped; NaN in either series resets the side (no event across a hole)."` and `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:55-58`: `"side = (a > b) - (a < b) \n out.append(side if (side != 0 and last != 0 and side != last) else 0)"` | `CONSISTENT` | SOURCED (`USAGE_wavetrend.md:18`, `wavetrend.py:46-48,55-58`). Both define bullish cross as `wt1 > wt2` (+1) and bearish cross as `wt1 < wt2` (-1). |
