> **REVIEW BANNER:** superseded by `_CORRECTED.md`; the 3,247 bp figure here was a metric bug (order-flow imbalance, not fill slippage).

# P1 COST FLOOR ANALYSIS

Generated: 2026-10-06 18:32 UTC

## Results

**Total bars analyzed:** 959021
**Data source:** F:/MTS/data/orderflow_1m

## Findings

Mean adverse selection (order flow imbalance magnitude): **3247.61 bp**

**Threshold (maker-taker fee saving):** 10 bp
**Decision:** FAIL - Passive execution adverse selection far exceeds fee threshold

### Interpretation

The measured adverse selection (~32.5% typical imbalance) represents order flow directional pressure, not passive-execution slippage. The high values indicate significant order flow asymmetry in the archive, suggesting that passive limit orders would face consistent directional headwind. This is NOT the cost-floor metric from P1_COST_FLOOR research; that requires actual filled passive order tracking against market move. 

**Note:** Full P1 replication requires implementation of p1_cost_floor.py logic from PR #11 with explicit passive limit order fill simulation, not just order flow imbalance magnitude. Current analysis shows order flow characteristics only.

## Month-by-Month

See pre-registration PRE_REG_P1_COST_FLOOR_2026-10-06.md for methodology.

