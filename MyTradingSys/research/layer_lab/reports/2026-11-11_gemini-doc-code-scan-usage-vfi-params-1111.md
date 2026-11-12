CONSISTENT: 5 | CONTRADICTION: 0

# Independent Gemini Scan: `USAGE_vfi.md` Parameters Against `vfi.py` Defaults and Logic

- **Card**: `gemini-doc-code-scan-usage-vfi-params-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on worktree branch `gemini-q/gemini-doc-code-scan-usage-vfi-params-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/research/tv_favorites_2026-11/USAGE_vfi.md` (read)
  - `MyTradingSys/backtest/layers/vfi/vfi.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-code-scan-usage-vfi-params-1111.md` (this report)
- **Scope Out Respected**:
  - Read-only audit; zero edits to `USAGE_vfi.md` or `vfi.py`.
  - No commit, no claim, no ship, no sync operations.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
- **Done When Criteria**:
  - Line 1 has counts CONSISTENT/CONTRADICTION (sum 5) and one row per clause quoting `file:line`.

---

## 1. Parameter and Logic Comparison Table

| # | Parameter / Logic Clause | Statement in `USAGE_vfi.md` (`file:line`) | Default / Logic in `vfi.py` (`file:line`) | Status | Notes |
|---|---|---|---|---|---|
| 1 | Length (`130`) | `USAGE_vfi.md:13`: `"Sums signed capped volume over a finite rolling lookback (default 130 bars)"`; `USAGE_vfi.md:20`: `"daily (130-bar rolling window, 50-day average volume baseline)"`; `USAGE_vfi.md:29`: `"length 130, coef 0.2, vcoef (max volume cutoff) 2.5"`; `USAGE_vfi.md:59`: `"- Length: 130 (SOURCED)"` | `vfi.py:8`: `def vfi(..., length=130, ...):`; `vfi.py:10`: `"raw = SUM(vcp, length) / vave, first defined at bar max(stdev_len, length) + length - 1."`; `vfi.py:27,34-35`: `vave = sum(volume[i - length:i]) / length`, `raw[i] = sum(vcp[i - length + 1:i + 1]) / vave if vave else None` | CONSISTENT | Both document and implement default rolling lookback window `length = 130`. |
| 2 | Cutoff Coefficient `coef` (`0.2`) | `USAGE_vfi.md:11`: `"cutoff = coef * stdev(log_change, 30) * close (default coef = 0.2)"`; `USAGE_vfi.md:29`: `"length 130, coef 0.2, vcoef (max volume cutoff) 2.5"`; `USAGE_vfi.md:30`: `"coefficient 0.2 for daily and 0.1 for intraday"`; `USAGE_vfi.md:60`: `"- Coef (cutoff coefficient): 0.2 for daily, 0.1 for intraday (SOURCED, Katsanos)"` | `vfi.py:8`: `def vfi(..., coef=0.2, ...):`; `vfi.py:26`: `cutoff = coef * vinter * close[i]`; `vfi.py:30`: `vcp[i] = vc if mf > cutoff else (-vc if mf < -cutoff else 0.0)` | CONSISTENT | Both specify default `coef = 0.2` for volatility cutoff threshold filtering. |
| 3 | Max Volume Cutoff Multiplier `vcoef` (`2.5`) | `USAGE_vfi.md:12`: `"Caps extreme individual bar volume at 2.5 * SMA(volume, 50) to prevent single-day outlier spikes"`; `USAGE_vfi.md:29`: `"vcoef (max volume cutoff) 2.5"`; `USAGE_vfi.md:61`: `"- Vcoef (max volume cutoff multiplier): 2.5 (SOURCED)"` | `vfi.py:8`: `def vfi(..., vcoef=2.5, ...):`; `vfi.py:28`: `vc = min(volume[i], vcoef * vave)` | CONSISTENT | Both specify default volume capping multiplier `vcoef = 2.5` applied to rolling average volume. |
| 4 | Smoothing Window & Kind `smooth` / `smooth_kind` (`3` / `sma`) | `USAGE_vfi.md:63`: `"- Smooth VFI: False (SOURCED, 3-bar SMA when true)"`; `USAGE_vfi.md:70`: `"- Outputs: Both raw VFI and 3-bar smoothed VFI exposed for research."` | `vfi.py:8`: `def vfi(..., smooth=3, ..., smooth_kind="sma"):`; `vfi.py:11`: `"smoothed = SMA(raw, smooth) (or EMA, SMA-seeded, with smooth_kind="ema"); smooth <= 1 returns raw."`; `vfi.py:45-48`: `if smooth_kind == "sma" or prev is None: prev_sma = sum(w) / smooth; sm[i] = prev_sma; prev = prev_sma` | CONSISTENT | Code defaults to `smooth=3` and `smooth_kind="sma"`, matching the 3-bar SMA smoothing documented in USAGE notes. |
| 5 | Inter-Period Stdev Window `stdev_len` (`30`) | `USAGE_vfi.md:11`: `"cutoff = coef * stdev(log_change, 30) * close"`; `USAGE_vfi.md:64`: `"- Inter-period stdev window: 30 (SOURCED)"` | `vfi.py:8`: `def vfi(..., stdev_len=30, ...):`; `vfi.py:22-25`: `for i in range(max(stdev_len, length), n): w = inter[i - stdev_len + 1:i + 1]; m = sum(w) / stdev_len; vinter = math.sqrt(sum((x - m) ** 2 for x in w) / stdev_len)` | CONSISTENT | Both define the log typical price change standard deviation lookback window as 30 bars. |

---

## 2. Summary & Verification

- **Total Clauses Checked**: 5
- **Consistent**: 5
- **Contradictions**: 0
- **Not in Code**: 0
- **Unit Tests Verification**: `python -m unittest discover -s MyTradingSys/backtest/layers/vfi` passes with 5 tests OK (exit code 0).
