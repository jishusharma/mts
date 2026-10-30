# Positioning Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-positioning`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/positioning` code, find its source (analyst extract, FORMULAS.md, architecture spec, or none), and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 8
- **SOURCED count**: 3
- **OURS count**: 5
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/positioning/`)

| Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|
| Funding lookback window | `layers/positioning/funding_cvd_fade.py:70` | `lookback: int = 90` | OURS | Undefined in source literature (Memon 2026); grid-searched IS only `{60, 90, 180}` (`MyTradingSys/backtest/layers/FORMULAS.md:369`). |
| CVD divergence lookback | `layers/positioning/funding_cvd_fade.py:70` | `n: int = 20` | OURS | CVD price divergence lookback window; grid `{20, 50}` (`MyTradingSys/backtest/layers/FORMULAS.md:369`). |
| High funding percentile threshold | `layers/positioning/funding_cvd_fade.py:70` | `hi: float = 0.95` | OURS | Undefined in source literature; grid `{0.90, 0.95, 0.99}` (`MyTradingSys/backtest/layers/FORMULAS.md:369`). |
| Low funding percentile threshold | `layers/positioning/funding_cvd_fade.py:71` | `lo: float = 0.05` | OURS | Undefined in source literature; grid `{0.01, 0.05, 0.10}` (`MyTradingSys/backtest/layers/FORMULAS.md:369`). |
| CVD divergence filter toggle | `layers/positioning/funding_cvd_fade.py:71` | `use_divergence: bool = True` | OURS | Supervisor merge decision (2026-09-29) combining funding extreme with CVD divergence fade (`FORMULAS.md:361`). |
| Cumulative CVD bar delta | `layers/positioning/funding_cvd_fade.py:48` | `2 * tbv - v` | SOURCED | Standard taker-buy trade volume delta: $\Delta = \text{TBV} - (\text{V} - \text{TBV}) = 2\text{TBV} - \text{V}$ (`MyTradingSys/backtest/layers/FORMULAS.md:360`). |
| Round-trip taker fee rate | `layers/positioning/trade_costs.py:51` | `fee_rt: float = 0.0010` (10 bps) | SOURCED | Binance USDT-M perpetual contract standard taker fee (`MyTradingSys/backtest/layers/FORMULAS.md:345`). |
| Round-trip slippage allowance | `layers/positioning/trade_costs.py:51` | `slip_rt: float = 0.0002` (2 bps) | OURS | Internal slippage hurdle from T055b "SCALPING FEE FLOOR" (`MyTradingSys/backtest/layers/FORMULAS.md:345-347`). |

---

## 2. Details and Observations

1. **Origins & Provenance**:
   - The candidate C1 layer (`funding_cvd_fade`) was synthesized from academic literature on funding mean reversion (Memon 2026; He/Manela/Ross/von Wachter arXiv 2212.06888) combined with order-flow CVD divergence (`T055a H2`).
   - Ground truth audits (`HOME_FIT_AUDIT_POSITIONING.md:7-11`) confirmed zero mentions of funding or open interest in FlowHorse extracts; the strategy is an independent internal construct, not a trader replication.
2. **Parameters & Grids**:
   - Because academic literature establishes the principle without specifying operational thresholds, the lookback window (`90`), percentile cutoffs (`0.95 / 0.05`), and CVD divergence window (`20`) are grid-searched parameters (`OURS`).
   - Exchange execution fee rates (10 bps RT) and perpetual funding cashflow conventions (long pays positive rate, short receives) reflect venue reality (`SOURCED`), while the 2 bps slippage buffer is an internal floor (`OURS`).
