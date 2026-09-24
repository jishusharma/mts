# B062 - ALERT DIRECTION NOT ALIGNED TO POSITION

Register row: MyTradingSys/research/BUGS.md B062.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

[DC] 2026-09-20 operator request. Verbatim ask not preserved in BUGS.md row; row content transcribed below.

Title: Alert direction not aligned to operator position; engine fires shorts and longs equally while a position is open.

Operator observation: while long, operator received equal short and long popups. Loop has no position awareness.

## STATE

2026-09-22 OPEN. Blocked on spec.
Fix shape: loop reads position.json; suppress WATCH and same-direction SETUP_FORMING when position exists; elevate opposing SETUP_FORMING.
Rule 32 observation carried: B062 suppression needs live SETUP_FORMING matching open position.json direction.

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Item doc created during T039 functionality-doc sweep.
