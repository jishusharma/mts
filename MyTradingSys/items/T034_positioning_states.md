# T034 - POSITIONING STATES

Register row: MyTradingSys/research/BUGS.md T034.
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

### 2026-09-23T15:30Z - coordinator, session MTS-2026-09-23-1445Z

Source fold. Added from T039 sweep source 5 (INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 3, anchor L217).

Verbatim (L217-221):
> ### Phase 3 - Add positioning states
> 1. Derive Net Longs / Net Shorts from OI + CVD cross.
> 2. Emit four flags: net_longs, net_longs_new, net_shorts,
>    net_shorts_new.
> 3. Each is boolean or a strength value.

Coupling note (adjacent CONSTRAINTS block, L227-233): Rule 33 requires every field requested to be read by a rule. Emitting four new flags requires four matching rule-reads; verify before implementation. Rule 32 (3-snapshot proof for verdict-changing wiring) applies to any downstream wiring.

This fold is documentation only. No implementation this cycle.
