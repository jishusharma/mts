CONSISTENT: 5 | CONTRADICTION: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `malkan_40_60.py` Regime Classifier against Docstring and Cited Rules

- **Card**: `gemini-blind-read-malkan-40-60-regime-1111`
- **Worker / Model**: Gemini (`gemini-3.8-flash-low` worker on throwaway worktree branch `gemini-q/gemini-blind-read-malkan-40-60-regime-1111`)
- **Date**: 2026-11-11 (UTC)
- **Scope In (Read)**:
  - `MyTradingSys/backtest/layers/rsi/malkan_40_60.py` (implementation, docstrings, function signatures)
  - `MyTradingSys/backtest/layers/rsi/test_malkan_40_60.py` (unit tests covering regime classification, defaults, setups)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-malkan-40-60-regime-1111.md` (this report)
- **Scope Out Respected**:
  - Read-only audit; zero edits to `malkan_40_60.py` and `test_malkan_40_60.py`.
  - No live-tree edit, no deploy, no `.secrets` or `.env` read.
- **Verdict**: All 5 required clauses are CONSISTENT (5 CONSISTENT, 0 CONTRADICTION, 0 NOT_IN_DATA).

---

## 1. Clause Verification Table (5 Clauses)

| # | Clause Description | Docstring Ref (`malkan_40_60.py`) | Implementation Ref (`malkan_40_60.py`) | Test Evidence (`test_malkan_40_60.py`) | Status |
|---|---|---|---|---|---|
| 1 | Output length equals input length | L26: `"Identical algorithm to the scoped `rsi_regime`: returns a list the same length as `rsi`."` | L41, L61: `result = [None] * len(rsi)` ... `return result` | L21-24: `rsi = [None, None, 65, 62, 58, 42, 38, 45, 55, 63]`; `got = malkan_regime(...)`; `self.assertEqual(got, expected)` where `len(rsi) == len(expected) == 10` | CONSISTENT |
| 2 | Lookback window needs consecutive non-None run | L27-29: `"A value at index `i` requires exactly `lookback` consecutive non-`None` `rsi` values ending at `i` (walking backward from `i`, collecting non-`None` values until `lookback` are found or the start of the series is reached without enough — if not enough, output `None` at `i`)."` | L43-50, L59: `for i in range(len(rsi)): window = []; j = i; while len(window) < lookback and j >= 0: if rsi[j] is not None: window.append(rsi[j]); j -= 1; if len(window) == lookback: ... # else: leave as None` | L21-24: `test_d1_regime_lo40_hi60_lookback3` tests `[None, None, 65, 62, 58, ...]` returning `None` for indices 0..3 until lookback=3 non-None values are accumulated | CONSISTENT |
| 3 | Defaults 40/60/20 live only here | L10-11, L24: `"D2 rule: the 40/60 numbers are private to malkan_40_60. No other module imports them. This file is the one place those numbers may live as defaults."`; `def malkan_regime(rsi: list, lo: float = 40.0, hi: float = 60.0, lookback: int = 20) -> list:` | L24: `lo: float = 40.0, hi: float = 60.0, lookback: int = 20` | L90-109: `TestMalkanIsolation` (`test_d7_malkan_default_has_40_and_60`, `test_c4_cross_reference_other_params_file_has_no_40_60`) verifying 40/60 isolation | CONSISTENT |
| 4 | Bull setup at 40 and bear setup at 60 | L7-8, L64-83, L107-117: `MLK-S1` ("Bullish candlestick forms at 40 RSI level on daily chart = buy signal"); `MLK-S2` ("Bearish candlestick forms at 60 RSI level on daily chart = short signal") | L64, L87-104: `malkan_setup_bull(..., level: float = 40.0, ...)` emits `side="long"`, `rule_id="MLK-S1"`, `event="support"`; L107, L121-138: `malkan_setup_bear(..., level: float = 60.0, ...)` emits `side="short"`, `rule_id="MLK-S2"`, `event="rejection"` | L43-54 (`test_d3_bull_setup_fires`), L77-88 (`test_d6_bear_setup_fires`) | CONSISTENT |
| 5 | Single timeframe only | L13-17: `"MLK-GAP1: The real Malkan 5-star setup gates a Daily entry on Monthly AND Weekly RSI regime (a 3-timeframe composition). This module implements the single-timeframe mechanics only: regime + 40/60 bounce/reject + entry-candle color. A caller must run it once per timeframe (via the timeframe layer, D1) and combine results itself to reconstruct the full multi-timeframe setup."` | L24, L64, L107: `malkan_regime`, `malkan_setup_bull`, `malkan_setup_bear` operate strictly on a single 1D series of bars/rsi/regime without any cross-timeframe or multi-timeframe aggregation code | L17-89: all unit tests execute on single timeframe synthetic test series | CONSISTENT |

---

## 2. Test Execution Verification

- **Command**:
  ```bash
  python -m unittest MyTradingSys/backtest/layers/rsi/test_malkan_40_60.py
  ```
- **Output**:
  ```
  ........
  ----------------------------------------------------------------------
  Ran 8 tests in 0.000s

  OK
  ```
  (SOURCED: test output, 8 passed).
