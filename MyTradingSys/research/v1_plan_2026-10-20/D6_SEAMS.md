# D6. Seams for future modules (options, other markets): where they plug in, nothing built now

Rule: v1 leaves a named seam and a one-line test that the seam exists. No option code, no second venue, no DAX, until v2.
The options work in MyTradingSys/options/OPTIONS_PLAN.md stays independent (its P0-P5) and does not touch core until an
operator-approved spec, as that plan already says.

| Seam | v1 shape | What a module adds later |
|---|---|---|
| Signal.instrument | a string today (BTCUSDT); v1 schema makes it an object {venue, symbol, kind} with kind fixed to "perp" | kind "option" with strike, expiry, right; or a new venue/symbol for another market |
| Exposure ledger | one table keyed by instrument, holding net size and risk in R; the daily-loss monitor and HALT read exposure here, not the perp position directly | options report delta-equivalent exposure into the same table; the loss cap does not change |
| Data adapter | one interface: subscribe(instrument) -> candles and trades; Binance perp is the only implementation | a Deribit options feed or an equities feed implements the same interface |
| Fee model | per venue and instrument, from backtest/layers/FORMULAS.md section 17; the backtester takes it as a parameter | an options fee and slippage model drops in without touching the backtester |
| Promotion registry | promoted_setups.json rows carry instrument | an options setup is just another row |
| Timeframe map | the one TF map card (one-timeframe-map-for-the-whole-toolchain) is the seam for daily/weekly markets | DWM equities (Malkan cards) plug into the same map |

Not a seam (deliberately): no abstract "strategy" base class, no plugin loader, no event bus. Modules are folders that write
Signal rows. The core reads rows. That is enough for v1 and v2, and it keeps the LLM-built code flat.

Test that the seam exists (S1): one pytest that builds a Signal with kind "option" and asserts the core rejects it with
"kind not enabled", not with a crash. That proves the field is there and the gate is closed.
