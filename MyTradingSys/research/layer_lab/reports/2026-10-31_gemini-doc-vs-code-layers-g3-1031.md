# Layer Lab Report: `gemini-doc-vs-code-layers-g3-1031`

**Task ID:** `gemini-doc-vs-code-layers-g3-1031`  
**Date:** 2026-10-31  
**Worker:** Gemini Flash  
**Card Goal:** For each of the layers cryptocred consensus alerts promotion compare the LAYERS.md row and its research notes with the code in backtest/layers/<layer>; list each contradiction with both file:line.

---

## 1. Summary of Execution & Findings

- Reviewed documentation across [LAYERS.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g3-1031/MyTradingSys/system/LAYERS.md), [FORMULAS.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g3-1031/MyTradingSys/backtest/layers/FORMULAS.md), [PROMOTION_PIPELINE.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g3-1031/MyTradingSys/system/PROMOTION_PIPELINE.md), and layer-specific READMEs/handoff documents.
- Audited implementation code across `MyTradingSys/backtest/layers/cryptocred/`, `MyTradingSys/backtest/layers/consensus/`, `MyTradingSys/backtest/layers/alerts/`, and `MyTradingSys/backtest/layers/promotion/`.
- Executed unit and regression test suites across all 4 module suites (103 tests ran green in 24.5s via `python -m unittest MyTradingSys.backtest.layers.cryptocred.test_cc_structure MyTradingSys.backtest.layers.consensus.test_writer MyTradingSys.backtest.layers.promotion.test_promote`).

### Match Summary by Layer Module

1. **cryptocred** (`MyTradingSys/backtest/layers/cryptocred/`):
   - 14 rules and parameters verified (fractal swing `left=2, right=2, use_body=True`, MSB sequence violation, `filter_range_noise=False`, retest tolerance `0.15%`, invalidation `0.5%`, setup 1 & 2 targets `1.5R`, setup 2 fib `0.618-0.786`, setup 3 target `2.0R`, lookback `20`).
   - Contradictions: **0**.
2. **consensus** (`MyTradingSys/backtest/layers/consensus/`):
   - 8 structural constants and rules verified (7 `TOM_KEYS`, 6 `FABIO_KEYS`, 6 `RSI_TFS`, ISO-8601 ms timestamps, snapshot ID fallback, non-blocking observation guarantee).
   - Contradictions: **0**.
3. **alerts** (`MyTradingSys/backtest/layers/alerts/`):
   - 10 parameters and integration rules verified (Bollinger Bands `n=20`, `mult=2.0`, population standard deviation, short-side reversal emission, live runner CLI defaults `--tfs 1h,15m,5m,1m`, `--poll-seconds 60`, post-poll consensus observer hook).
   - Contradictions: **0**.
4. **promotion** (`MyTradingSys/backtest/layers/promotion/`):
   - 12 rules and parameters verified (`MIN_TRADES = 30`, `net_r > 0`, `ci_low > 0`, bounds check, PRE_REG pre-dating screen verdict, `PASS` verdict check, `BT-TUNED` label check, trial ledger variant count parity, single-read checks, default-deny shadow gating, fail-closed handling).
   - Contradictions: **0**.

- **Total Parameter & Rule Matches Verified**: 44 [OURS]
- **Total Contradictions Found**: 0 [OURS]

---

## 2. Deliverables Created

- Comparison Table Artifact: [LAYERS_VS_CODE_G3.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g3-1031/MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE_G3.md)
- Lab Report: [2026-10-31_gemini-doc-vs-code-layers-g3-1031.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g3-1031/MyTradingSys/research/layer_lab/reports/2026-10-31_gemini-doc-vs-code-layers-g3-1031.md)

Noticed: `alerts/live_runner_cli.py` and `promotion/registry.py` both implement fail-closed behavior on missing or unreadable registry files by falling back to collection-only rather than dropping alerts completely or crashing the runner.
