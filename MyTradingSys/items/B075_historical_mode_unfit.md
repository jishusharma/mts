# B075 - HISTORICAL MODE UNFIT FOR BACKTESTING; OMITS KEY DATA FIELDS

Opened: 2026-09-27 by session Claude Sonnet 5 (via NUC worker task 010, reviewed by coordinator).
Severity: MED (impacts backtesting validity).
Status: CLOSED 2026-10-06 (receipt in BUGS.md, MTS-2026-10-06-2122Z-APP-COO-registry-fix).

## DESCRIPTION

"Historical mode (Main 'historical') is unfit for backtesting: zeroes
trade_flow, book_imbalance, funding, OI; omits session and order_flow; and
fetches LIVE spot_perp_basis and oi_breakdown into a past snapshot
(look-ahead). book_imbalance=0.0 turns 100 pct of long rank-1 into L2
'contradiction' (2,233 aligned flipped). Task D1-L0."

Per-item doc: research/core_readiness_2026-09-27/CORE_READINESS_PLAN.md
section 2, finding F7.

## BLOCKS

- Phase D task D1-L0 (L0 historical mode rework).

## UPDATES

2026-09-27: Filed per CORE_READINESS_PLAN.md F7.
