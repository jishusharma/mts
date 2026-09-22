# T034 - POSITIONING STATES

Register row: MyTradingSys/mts/research/BUGS.md T034.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

No verbatim ask on record (opened 2026-09-19). Row title and source transcribed below from BUGS.md.

Title: Add Net Longs / Net Shorts / (New) positioning states from OI + CVD cross.

Source: MarketDataSnapshot.java new positioning block; INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 3.

## STATE

2026-09-22 OPEN.
Definition locked 2026-09-22: net_longs (standing, OI), net_longs_new (entering, CVD), net_shorts (standing, OI), net_shorts_new (entering, CVD).
Pending operator decision: output type (boolean / strength / both, backtest both).

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Item doc created during T039 functionality-doc sweep.
