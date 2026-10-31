# Parameter Labels Audit Report: Cryptocred, Consensus, Alerts, Promotion (G3)

**Card:** `gemini-param-labels-layers-g3-1031`  
**Date:** 2026-10-31 (UTC)  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/LAYER_PARAM_LABELS_G3.md`  
**Scope:** `MyTradingSys/backtest/layers/{cryptocred,consensus,alerts,promotion}`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  

---

## 1. Summary of Findings

Across the 4 target layer modules (`cryptocred`, `consensus`, `alerts`, `promotion`):
- Total tunable parameters and structural constants audited: **84** [OURS]
- **SOURCED:** **17** (all verified with specific file:line citations and verbatim source quotes / architectural specifications)
- **OURS:** **67** (including 54 engineering discretizations, scan depths, lookback windows, heuristics, tolerances; 8 infrastructure paths/buffers; 5 venue/calendar conventions)
- **Flagged SOURCED without a quote:** **0**
- **Unlabelled constants:** **0**

---

## 2. Findings by Module

1. **CryptoCred** (`MyTradingSys/backtest/layers/cryptocred/`):
   - 34 parameters swept (5 SOURCED, 29 OURS).
   - Core structural rules (sequence violation for MSB, 0.618-0.786 Fibonacci retracement bounds, 2.0R target multiple for counter-trend reversals, and Wilder 14 ATR smoothing) are SOURCED (`cross_trader_consolidated.md:330-331, 417-431`, `BHwoN7VPrBE`, `FORMULAS.md:494`).
   - Discretizations (fractal widths `left=2, right=2`, range-noise filter `50 bars, 0.25`, retest tolerances `0.0015, 0.005`, 200-bar retest expiry, 0.1% stop buffer, and 70/30 chronological split protocol) are OURS (`B143`, `B145`).
2. **Consensus** (`MyTradingSys/backtest/layers/consensus/`):
   - 7 parameters swept (4 SOURCED, 3 OURS).
   - Required dictionary keys for Tom (`verdict`, `setup`, `side`, `entry`, `stop`, `target`, `net_rr`), Fabio (`verdict`, `model`, `side`, `entry`, `stop`, `target`), RSI timeframes (`1m`, `3m`, `15m`, `1h`, `4h`, `1d`), and millisecond timestamps are SOURCED verbatim from architecture spec (`ARCHITECTURE_TWO_CORES_2026-10-01.md:33-39`).
   - Relative filesystem navigation depths (`parents[4]`) and alert deduplication state comparisons are OURS.
3. **Alerts** (`MyTradingSys/backtest/layers/alerts/`):
   - 30 parameters swept (5 SOURCED, 25 OURS).
   - Standard Bollinger 20 / 2.0 (`live_bb_top_reversal.py:24-25`, `FORMULAS.md:s22`), standard SI millisecond conversions, standard 70% Value Area (`live_layers.py:57`, `FORMULAS.md:s19`), Malkan bull support 40 (`live_layers.py:145`), and Wilder RSI 14 are SOURCED.
   - Cushion margin `TOUCH_K=0.05` (`live_bb_top_reversal.py:26`), candle-close proximity band `BAND=0.0025`, 200-bar touch scan window, 95/5 funding crowd cutoffs, 10 USD profile bins, 10-day naked POC lookback, 169-bar weekly low lookback, and `MAX_EMITTED=2000` memory ring buffer are OURS.
4. **Promotion** (`MyTradingSys/backtest/layers/promotion/`):
   - 13 parameters swept (3 SOURCED, 10 OURS).
   - Deribit contract lot size (10 USD contracts) and standard normal distribution 95% CI multipliers ($3.92 = 2 \times 1.96$ and $[0.025, 0.975]$ bootstrap percentiles) are SOURCED (`registry.py:96`, `promote.py:64, 72`).
   - Statistical sanity sample floor `MIN_TRADES=30`, `POWER_Z=0.84`, `MDE_SAFETY=4`, bootstrap parameters (`BOOT_SEED=20261016`, `BOOT_DRAWS=2000`), error margins `TOL_R=0.01`, `TOL_N=0.05`, Holm-Bonferroni critical threshold `alpha=0.025`, and position ceiling $10,000 USD are OURS (`promote.py:40-47`).

---

## 3. Verification

Executed full test suite across the target layers:
```bash
python -m pytest MyTradingSys/backtest/layers/alerts/test_alert_emitter.py MyTradingSys/backtest/layers/alerts/test_live_bb_top_reversal.py MyTradingSys/backtest/layers/alerts/test_live_candle_close.py MyTradingSys/backtest/layers/alerts/test_live_rsi_divergence.py MyTradingSys/backtest/layers/alerts/test_live_runner_core.py MyTradingSys/backtest/layers/cryptocred/test_cc_bt_adapter.py MyTradingSys/backtest/layers/cryptocred/test_cc_htf_count.py MyTradingSys/backtest/layers/consensus/test_hook.py MyTradingSys/backtest/layers/consensus/test_writer.py MyTradingSys/backtest/layers/promotion/test_registry_gate.py
# 129 passed in 3.99s
```

Primary deliverable created:
- `MyTradingSys/research/gemini_burn_2026-10-31/LAYER_PARAM_LABELS_G3.md`
