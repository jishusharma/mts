# P1 COST FLOOR ANALYSIS - CORRECTED (Bug-Fix Trial Row)

Generated: 2026-10-06 13:05 UTC

## Bug Fix Summary

**Previous result (invalid):** 3247 bp mean adverse selection — measured order flow imbalance magnitude (market direction), not execution slippage

**Corrected metric:** Place passive limit orders at offsets 0/2/5 bp below/above prior 1m close. Wait for fill (by touching low/high). Hold 5m or 15m. Exit at market close. Measure: price move against entry = adverse selection (bp).

**Trial row status:** Bug-fix rerun after commit 41fa58f. Pre-registration PRE_REG_P1_COST_FLOOR_2026-10-06.md unchanged. No threshold changes.

## Result

**PASS**

- **Data:** F:/MTS/data/orderflow_1m, 959,021 bars (2024-12-02 to 2026-09-21)
- **Filled passive orders analyzed:** 6,419,364
- **Mean adverse selection:** 0.02 bp
- **Std dev:** 21.94 bp
- **Fee threshold (maker-taker round-trip):** 10.00 bp

## Conclusion

**Decision: PASS** — Passive limit order execution is worth modelling.

Mean adverse selection (0.02 bp) is negligible compared to the 10 bp maker-taker fee saving threshold. This confirms that passive execution costs are low relative to the fee benefits, supporting the P1 cost floor hypothesis that passive limit orders can be profitably used when the fee savings exceed the execution slippage.

### Interpretation

The near-zero mean adverse selection suggests:
1. Passive limit orders filled on thinly-traded 1m bars face minimal slippage
2. The hold-period exits (5m, 15m market close) capture sufficient liquidity without additional cost
3. Adverse selection is dominated by micro-structure noise rather than adverse price movement

This validates passive execution as a candidate strategy component.
