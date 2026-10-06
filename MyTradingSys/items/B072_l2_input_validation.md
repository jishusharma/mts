# B072 - L2 INPUT VALIDATION ABSENT FOR CURRENT_PRICE 'X' OR NONE

Opened: 2026-09-27 by session Claude Sonnet 5 (via NUC worker task 008, reviewed by coordinator).
Severity: LOW (input validation missing; not a defect, but could cause silent errors).
Status: CLOSED.

## DESCRIPTION

L2 input validation absent: build_math_object returns "aligned" for
current_price "x" or None; raises only on cvd null.

Per-item doc: research/core_readiness_2026-09-27/CORE_READINESS_PLAN.md
section 2, finding F10.

## BLOCKS

- No direct blocking items.

## UPDATES

2026-09-27: Filed per CORE_READINESS_PLAN.md F10.

B072 closed 2026-10-04 (MTS-2026-10-04-0538Z-CLI-BLD-b072-b073-math-object): ValueError on bad current_price; see research/BUGS.md B072.
