CONSISTENT: 5 | CONTRADICTION: 0

# Independent Gemini Blind Read: `malkan_mtf.py` `state_asof` and Gating against Docstring

- **Card**: `gemini-blind-read-malkan-mtf-asof-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on worktree branch `gemini-q/gemini-blind-read-malkan-mtf-asof-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/backtest/layers/rsi/malkan_mtf.py` (implementation and module/function docstrings)
  - `MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py` (test coverage)
- **Scope Out Respected**:
  - Read-only audit; no edits to source/test files.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
- **Done When Criteria**:
  - Line 1 has counts `CONSISTENT: 5 | CONTRADICTION: 0` (sum 5).
  - One row per clause quoting `file:line`.

---

## 1. Clause-by-Clause Verification Table

| # | Clause Requirement | Docstring Citation (`file:line`) | Implementation Citation (`file:line`) | Status |
|---|---|---|---|---|
| 1 | `state_asof` returns the value of the latest higher-timeframe bar with `time <= t` | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:24`: `"Return the value from the LATEST entry in times whose value is <= t."` and `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:29-33`: `"Return the value from the LATEST entry in times whose value is <= t (the higher-timeframe bar that was already open/closed at or before the daily timestamp t ... Return None if times is empty or every entry in times is > t"` | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:42-50`: `"i = len(times) - 1"`, `"while i >= 0 and times[i] > t: i -= 1"`, `"if i < 0: return None"`, `"return values[i]"`; tested in `MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py:17-20`: `"self.assertEqual(state_asof([0, 10, 20], ["RANGE", "BULL", "BULL"], 13), "BULL")"` | CONSISTENT |
| 2 | Closed-bar only, no leakage (no future bar can gate a daily bar) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:14-16`: `"The 'most recently CLOSED higher-timeframe bar as of the daily timestamp' lookback semantics of state_asof are critical: a daily bar is gated by the most recently CLOSED higher-timeframe bar, never a future one. This prevents information leakage into backtests."` and `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:30-32`: `"...never a future one"` | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:44`: loop stops as soon as `times[i] <= t`, guaranteeing any entry with `times[i] > t` is ignored; tested in `MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py:14-15`: `"self.assertIsNone(state_asof([10, 20], ["BULL", "BEAR"], 5))"` | CONSISTENT |
| 3 | No own RSI or regime computation inside this file | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:10-12`: `"This module performs NO new RSI/regime computation itself: monthly and weekly rsi/malkan_regime values must already have been computed by running rsi_core/malkan_regime once per timeframe (via the D1 timeframe layer) before calling here; this file only aligns and gates."` | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:19`: imports only `"from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_setup_bull, malkan_setup_bear"`; lines 53-125 contain only gating / lookups / labels, importing or executing no RSI math | CONSISTENT |
| 4 | Monthly and Weekly regime gate the Daily setup | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:6-8`: `"Monthly and Weekly malkan_regime states gate a Daily malkan_setup_bull/malkan_setup_bear signal, reconstructing the full Malkan 5-star setup from the single-timeframe pieces malkan_40_60.py already implements per timeframe."` and `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:55-58`: `"Multi-timeframe bull setup (MLK-S1-MTF): Daily regime BULL + rsi_events 'support' @ 40 + bullish entry candle, gated by Weekly and Monthly RSI regimes both being BULL."` | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:64-74`: evaluates `w = state_asof(weekly_times, weekly_regime, signal["t"])` and `m = state_asof(monthly_times, monthly_regime, signal["t"])`, gating with `"if w == 'BULL' and m == 'BULL': ... signals.append(new_signal)"`; tested in `MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py:38-65` | CONSISTENT |
| 5 | Bull and bear both composed | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:6-7`: `"Monthly and Weekly malkan_regime states gate a Daily malkan_setup_bull/malkan_setup_bear signal"` and `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:79-84`: `"Multi-timeframe bear setup (MLK-S2-MTF): Daily regime BEAR + rsi_events 'resistance' @ 60 + bearish entry candle, gated by Weekly and Monthly RSI regimes both being BEAR."` | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:53-76`: implements `malkan_mtf_bull`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:79-102`: implements `malkan_mtf_bear` checking `if w == "BEAR" and m == "BEAR": ... signals.append(new_signal)`; both tested in `MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py:27-103` | CONSISTENT |

---

## 2. Summary & Verification

- **Total Clauses Checked**: 5
- **Consistent**: 5
- **Contradictions**: 0
- **Not in Data**: 0
- **All unit tests pass**: `python -m unittest MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py` runs 11 tests with exit code 0.
