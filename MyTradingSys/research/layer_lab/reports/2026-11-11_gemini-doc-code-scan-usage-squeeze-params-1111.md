CONSISTENT: 4 | CONTRADICTION: 0 | NOT_IN_CODE: 1

# Independent Gemini Scan: `USAGE_squeeze.md` Parameters Against `squeeze.py` Defaults and Logic

- **Card**: `gemini-doc-code-scan-usage-squeeze-params-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on worktree branch `gemini-q/gemini-doc-code-scan-usage-squeeze-params-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/research/tv_favorites_2026-11/USAGE_squeeze.md` (read)
  - `MyTradingSys/backtest/layers/squeeze/squeeze.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-code-scan-usage-squeeze-params-1111.md` (this report)
- **Scope Out Respected**:
  - Read-only audit; zero edits to `USAGE_squeeze.md` or `squeeze.py`.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
- **Done When Criteria**:
  - Line 1 has counts CONSISTENT/CONTRADICTION (sum 5) and one row per clause quoting `file:line`.

---

## 1. Parameter and Logic Comparison Table

| # | Parameter / Logic Clause | Statement in `USAGE_squeeze.md` (`file:line`) | Default / Logic in `squeeze.py` (`file:line`) | Status | Notes |
|---|---|---|---|---|---|
| 1 | Bollinger Bands length 20 and 2.0 sd multiplier | `USAGE_squeeze.md:10`: `"Bollinger Bands (len 20, 2.0 sd)"`; `USAGE_squeeze.md:59-60`: `"- Bollinger Bands length: 20 (SOURCED)"`, `"- Bollinger Bands multiplier: 2.0 (SOURCED)"`; `USAGE_squeeze.md:65-66`: `"- LazyBear code bug: Original Pine script used multKC (1.5) for BB deviation; corrected in MTS formula (FORMULAS.md s31) to BB mult 2.0."` | `squeeze.py:15-16`: `def squeeze_momentum(..., bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.5, ... textbook_bb=False):`; `squeeze.py:4-6`: `"Script quirk (SOURCED): LazyBear's Pine source computes dev = multKC * stdev(source, length), so the Bollinger half-width is kc_mult*stdev (1.5*sd), not 2.0*sd... textbook_bb=True (OURS) restores the textbook half-width bb_mult*stdev (2.0*sd)."` | CONSISTENT | Both document the standard 20 / 2.0 parameters and explicitly document the LazyBear Pine quirk where `multKC` is used by default unless `textbook_bb=True`. Parameter default arguments in code are `bb_len=20`, `bb_mult=2.0`. |
| 2 | Keltner Channels length 20 and 1.5 multiplier | `USAGE_squeeze.md:10`: `"Keltner Channels (len 20, 1.5 ATR/TR)"`; `USAGE_squeeze.md:61-62`: `"- Keltner Channels length: 20 (SOURCED)"`, `"- Keltner Channels multiplier: 1.5 (SOURCED)"` | `squeeze.py:15`: `kc_len=20, kc_mult=1.5`; `squeeze.py:40`: `kc_hw = kc_mult * _sma(tr, i, kc_len)` | CONSISTENT | Function signature sets defaults `kc_len=20` and `kc_mult=1.5`; channel half-width calculation in line 40 directly applies `kc_mult * _sma(tr, i, kc_len)`. |
| 3 | TR vs ATR calculation | `USAGE_squeeze.md:10`: `"Keltner Channels (len 20, 1.5 ATR/TR)"`; `USAGE_squeeze.md:63`: `"- True Range calculation: True (SOURCED)"` | `squeeze.py:25-26`: `tr = [high[i] - low[i] if i == 0 else max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])) for i in range(n)]`; `squeeze.py:40`: `kc_hw = kc_mult * _sma(tr, i, kc_len)` | CONSISTENT | True Range is explicitly calculated per bar (max of high-low, high-prev_close, low-prev_close) and its simple moving average (`_sma(tr, i, kc_len)`) is used for Keltner Channel half-width. |
| 4 | Squeeze-on definition (BB inside KC) | `USAGE_squeeze.md:10`: `"When BB is inside KC, squeeze is ON (black dots on zero line)."` | `squeeze.py:18`: `"squeeze_on: BB inside KC (strict); squeeze_off: BB outside KC (strict); both False when equal/overlapping."`; `squeeze.py:41-42`: `tol = 1e-9 * max(1.0, abs(bb_hw), abs(kc_hw))`, `on[i] = bb_hw < kc_hw - tol` | CONSISTENT | Squeeze-on is defined strictly as Bollinger Band half-width strictly less than Keltner Channel half-width (within relative tie tolerance). |
| 5 | Setup requirement: >= 6 consecutive squeeze dots | `USAGE_squeeze.md:11`: `"- Setup requirement: Carter requires >= 6 consecutive squeeze dots to verify sufficient energy storage before release."`; `USAGE_squeeze.md:31`: `"- Rule: Wait for >= 6 squeeze dots; enter on first fired dot in momentum direction; exit when momentum fades."` | `squeeze.py:1-51`: Module computes per-bar context columns only (`on`, `off`, `mom`); no multi-bar streak counting or 6-dot threshold logic in `squeeze.py` | NOT_IN_CODE | Consistent with `USAGE_squeeze.md:3,70` ("Context column only; no code, no trading rules, no backtest" and "Strictly a context column... Never a trade trigger"); the 6-dot setup count is a downstream trading/setup rule and is not implemented inside `squeeze.py`. |

---

## 2. Summary & Verification

- **Total Clauses Checked**: 5
- **Consistent**: 4
- **Contradictions**: 0
- **Not in Code**: 1
- **All unit tests pass**: `python -m unittest MyTradingSys/backtest/layers/squeeze/test_squeeze.py` runs 4 tests with exit code 0.
