# T048 - SATELLITE FRAMEWORK + EXCHANGE API LAYER

Register row: MyTradingSys/research/BUGS.md T048.
Opened: 2026-09-25 by session MTS-2026-09-25-0829Z.
Severity: HIGH. Status: OPEN (design).

## OPERATOR STATEMENT (verbatim, 2026-09-25)

"file it! we need it. Our goal is to be API ready for trading with MTS."

## THE ASK

Any open position can spawn small, partial, independently-stopped
counter-positions ("satellites"). Each satellite:
  - triggers on a validated condition (BB extreme, CVD divergence,
    later MA cross, etc.),
  - executes on a separate exchange sub-account for true margin and
    liquidation isolation from the parent position,
  - closes on its own profit condition or its own stop,
  - on closure, re-consults the MTS decision layer about resizing or
    opening new positions, which themselves inherit the same satellite
    capability.

MTS must become exchange-agnostic via a real trading API layer.

## WHY THIS MATTERS

Direction statement from operator: the goal is API-ready trading with
MTS. This is the first item filed under that goal.

## WHAT IT CHANGES

1. Position model. Today the model assumes one position at a time
   (single position.json). Satellites require N concurrent positions
   with parent/child links and independent stops.
2. Execution. Today MTS watches. It does not place orders. A real
   exchange API layer does not exist.
3. Governance. No max concurrent positions, no max total notional, no
   max recursion depth, no per-instrument allocation. All undefined.
4. Wiring. Satellites need the same provider -> reader -> consumed_by
   gate that core rules use, so a satellite cannot gate core behavior
   by accident. PROJECT_VISION doctrine: modules never gate core.

## DEPENDENCIES / PREREQUISITES

- A full audit of the current condition/rule inventory to know what
  can trigger a satellite. Owed.
- Design session for the position data model (multi-position +
  parent/child). Owed.
- Decision on exchange API target and whether sub-accounts are manual
  or automated. Owed.
- Governance limits defined before any live order path exists. Owed.

## ANSWERING THE EXTERNAL NOTE

A 20-question status inquiry (5 sections: loop status, condition
inventory, position data model, execution/API, governance numbers) was
received 2026-09-25. It must be answered against the actual codebase,
not from memory. A batched read is owed before answering.

## LAYER FREEZE NOTE (2026-09-26)

An unmerged 2026-09-25 PROJECT_VISION.md.new draft had proposed pausing this
item behind two conditions (compiled_engine.md CORE/MODULE tagging; T043
closing) that were never actually both met. Operator lifted the freeze for
this item specifically on 2026-09-26; see PROJECT_VISION.md's dated
DIRECTION DECISION entry for the full record. This item proceeds.

## STATUS

OPEN. Design, freeze lifted 2026-09-26, exchange API work starting with
Deribit (operator's exchange). Plan: read-only connectivity first (testnet),
then order placement on testnet only behind explicit governance limits, then
live behind an explicit operator toggle. Satellite/multi-position framework
follows once single-position execution is proven. Next action: file a
dedicated sub-item for the Deribit execution layer; batched read of target
files for the 20-question inquiry still owed.
