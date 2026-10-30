SOUND ? three hand-derived RSI outputs match the RSI layer code; the Malkan rolling regime formula is not present in FORMULAS.md.

## What was checked

- Canonical formulas: `MyTradingSys/backtest/layers/FORMULAS.md` sections 1?6 (lines 10, 59, 75, 85, 107, 121): Wilder RSI, RMA, SMA, EMA, WMA, and tolerance-band events.
- Implementation: `MyTradingSys/backtest/layers/rsi/rsi_core.py:7-63`, `rsi_ma.py:8-60`, `rsi_events.py:19-103`, and `malkan_40_60.py:24-58`.
- Ran the code on this synthetic 10-close series (not market data): `[10,12,11,14,13,15,14,16,15,17]`. RSI period=3; RSI smoothing examples use length=2. Command: Python snippet importing `rsi_core`, `rsi_ma`, and `malkan_regime` and printing each result.

## Formula inventory

| Formula used by the RSI family | FORMULAS.md | Code evidence | Check |
|---|---|---|---|
| Wilder RSI: SMA-seeded gains/losses over first `period` changes, then Wilder recursive averages; flat loss case returns neutral 50 | ?1, `FORMULAS.md:10-57` | `rsi_core.py:18-39` seeds and emits first RSI; `:42-63` recursive values | MATCH |
| RMA of an RSI series, SMA-seeded then alpha `1/length` recursion | ?2, `FORMULAS.md:59-73` | `rsi_ma.py:49-59` alpha selection and seed/recursion | MATCH |
| SMA of last consecutive non-None inputs | ?3, `FORMULAS.md:75-83` | `rsi_ma.py:36-43` window checks and mean | MATCH |
| EMA with alpha `2/(length+1)`, SMA seed | ?4, `FORMULAS.md:85-105` | `rsi_ma.py:49-59` | MATCH |
| WMA with ascending oldest-to-newest weights | ?5, `FORMULAS.md:107-119` | `rsi_ma.py:26-28,45-47` | MATCH |
| Tolerance-band level event state machine (touch/support/rejection/failure/cross semantics delegated to TEST_PLAN) | ?6, `FORMULAS.md:121-131` | `rsi_events.py:32-103`; band bounds and side classification at `:42-48`, event branches at `:52-95` | MATCH at definition level; not numerically exercised in the 3-value check |
| Malkan rolling 40/60 regime (`BULL`/`BEAR`/`RANGE`) | No corresponding formula section in FORMULAS.md | `malkan_40_60.py:24-58`, especially thresholds at `:53-58` | NOT_IN_DATA (canonical formula absent) |

## Three hand calculations vs code

1. **Seed RSI at index 3 ? SAME.** First three deltas are `+2,-1,+3`; gains `[2,0,3]` average to `5/3`, losses `[0,1,0]` average to `1/3`. `RS=5`; RSI=`100-100/(1+5)=83.333333`. Code returned `83.33333333333334`. Formula `FORMULAS.md:12-22`; implementation `rsi_core.py:25-39`.
2. **Recursive RSI at index 4 ? SAME.** Delta is `-1`: avg gain=`((5/3)*2+0)/3=10/9`; avg loss=`((1/3)*2+1)/3=5/9`; RS=2, RSI=`100-100/3=66.666667`. Code returned `66.66666666666667`. Formula `FORMULAS.md:20-22`; implementation `rsi_core.py:42-53`.
3. **SMA smoothing at index 4 ? SAME.** Length 2 over RSI indices 3?4: `(83.333333+66.666667)/2=75.0`. Code returned `75.0` from `rsi_ma(rsi, "SMA", 2)`. Formula `FORMULAS.md:75-83`; implementation `rsi_ma.py:36-43`.

## Finding

| Severity | File:line | Finding and evidence | Proposed fix |
|---|---|---|---|
| LOW | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24-58` | `malkan_regime` implements a rolling min/max 40/60 classifier, but FORMULAS.md sections 1?6 contain no definition for it. The layer docstring specifies `BULL` when `min>=lo && max>=hi`, `BEAR` when `max<=hi && min<=lo`, otherwise `RANGE`; that contract is code-side only. Status: NOT_IN_DATA in canonical formula source. | Add a canonical formula section for the Malkan rolling regime in a separate formula-maintenance task. No source files changed in this audit. |

No source changes made. No test suite run; this is a report-only arithmetic audit.
