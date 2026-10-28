# B065 - STALE SWING FLAG HAS NO CONSUMER

Register row: MyTradingSys/research/BUGS.md B065.
Opened: 2026-09-23 by MTS-2026-09-23-0831Z. Severity MED.

## DEFECT

MarketDataSnapshot.java L719-722 computes structure.{tf}.stale = (swingHigh < currentPrice) || (swingLow > currentPrice). The flag is correctly written and propagated by mts_math.py L321-327 into current_market_state.md as SWING.{tf}_stale.

The code that consumes the swing levels ignores the flag:
- SetupCandidatesBuilder.extractZones reads structure.{1h,15m,5m}.swing_high and swing_low as zone candidates (tfRank 4/3/2). No stale check.
- SetupCandidatesBuilder.getSwingTF pulls stops from structure.1h for weekly zones. No stale check.

Consequence: zones and stops are built from swing levels the snapshot itself has flagged as no longer bracketing price. A correctly-computed invalidation signal has no effect.

## EVIDENCE

T041 worker rounds 1-3 (session MTS-2026-09-23-0831Z).
Coordinator reads: current_market_state.md L55 SWING.1h_stale: true while structured reads continue.

## FIX SHAPE (not applied)

One of:
1. extractZones skips zones whose source tf has stale=true.
2. getSwingTF refuses stale swings as stop-source.
3. Document as intentionally informational; no consumer by design.

## STATUS

OPEN. Design only. Independent of T041 close-out.

# END
