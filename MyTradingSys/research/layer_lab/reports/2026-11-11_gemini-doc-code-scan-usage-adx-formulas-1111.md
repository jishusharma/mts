CONSISTENT: 5 | CONTRADICTION: 0 | NOT_IN_CODE: 0

# Independent Gemini Scan: `USAGE_adx.md` Formulas Against `adx.py` Implementation

- **Card**: `gemini-doc-code-scan-usage-adx-formulas-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on worktree branch `gemini-q/gemini-doc-code-scan-usage-adx-formulas-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/research/tv_favorites_2026-11/USAGE_adx.md` (read)
  - `MyTradingSys/backtest/layers/adx/adx.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-code-scan-usage-adx-formulas-1111.md` (this report)
- **Scope Out Respected**:
  - Read-only audit; zero edits to `USAGE_adx.md` or `adx.py`.
  - No commit, no `sync.py` start/claim/ship, no live-tree edit, no deploy, no `.secrets` or `.env` read.
- **Done When Criteria**:
  - Line 1 has counts CONSISTENT/CONTRADICTION (sum 5) and one row per clause quoting `file:line`.

---

## 1. Formula and Logic Comparison Table

| # | Clause | Statement in `USAGE_adx.md` (`file:line`) | Implementation in `adx.py` (`file:line`) | Status | Notes |
|---|---|---|---|---|---|
| 1 | +DM / -DM rule | `USAGE_adx.md:10-13`: `"+DM = up if up > dn and up > 0, else 0; -DM = dn if dn > up and dn > 0, else 0 where up = high[i] - high[i-1], dn = low[i-1] - low[i]"` | `adx.py:19-22`: `up = high[i] - high[i - 1]`; `dn = low[i - 1] - low[i]`; `pdm.append(up if (up > dn and up > 0) else 0.0)`; `mdm.append(dn if (dn > up and dn > 0) else 0.0)` | CONSISTENT | Identical directional movement logic. Only the greater positive delta is retained; ties or negative deltas produce 0.0. |
| 2 | TR definition | `USAGE_adx.md:14-15`: `"TR = max(high - low, abs(high - close[1]), abs(low - close[1]))"` | `adx.py:18`: `tr.append(max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])))` | CONSISTENT | Standard Wilder True Range calculation matching textbook and documentation. |
| 3 | Wilder smoothing with n=14 | `USAGE_adx.md:16,74-75`: `"Smoothed over lookback n (standard n = 14) using Wilder's recursive smoothing"`; `"- DI Length (n): 14 (SOURCED)"`; `"- ADX Smoothing Length: 14 (SOURCED)"` | `adx.py:7,23,26-29`: `def adx_di(high, low, close, n=14):`; `s_tr, s_p, s_m = sum(tr[:n]), sum(pdm[:n]), sum(mdm[:n])`; `s_tr = s_tr - s_tr / n + tr[k]`; `s_p = s_p - s_p / n + pdm[k]`; `s_m = s_m - s_m / n + mdm[k]` | CONSISTENT | Function signature sets default `n=14`. Recursive accumulator update `s = s - s/n + x` implements standard Wilder smoothing. |
| 4 | DI and DX formula | `USAGE_adx.md:17,19`: `"DI+ = 100 * S(+DM) / S(TR); DI- = 100 * S(-DM) / S(TR)"`; `"DX = 100 * abs(DI+ - DI-) / (DI+ + DI-)"` | `adx.py:34-36`: `dip[i], dim[i] = 100.0 * s_p / s_tr, 100.0 * s_m / s_tr`; `tot = dip[i] + dim[i]`; `dx.append(100.0 * abs(dip[i] - dim[i]) / tot if tot > 0 else 0.0)` | CONSISTENT | Directional indices DI+, DI- and directional movement index DX match mathematical specification exactly with zero-division guard. |
| 5 | ADX as smoothed DX | `USAGE_adx.md:20,75`: `"ADX is the smoothed average of DX over n periods"`; `"- ADX Smoothing Length: 14 (SOURCED)"` | `adx.py:37-40`: `if len(dx) == n: adx[i] = sum(dx) / n`; `elif len(dx) > n: adx[i] = (adx[i - 1] * (n - 1) + dx[-1]) / n` | CONSISTENT | ADX initializes with standard sum average over first `n` periods, followed by Wilder's recursive smoothing `(adx[i-1]*(n-1) + dx[-1])/n`. |

---

## 2. Summary & Verification

- **Total Clauses Checked**: 5
- **Consistent**: 5
- **Contradiction**: 0
- **Not in Code**: 0
- **Unit Tests Verification**: `python -m unittest discover -s MyTradingSys/backtest/layers/adx -p "test_*.py"` passed (3 tests, OK).
