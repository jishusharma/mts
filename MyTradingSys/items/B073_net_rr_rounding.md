# B073 - NET_RR ROUNDING INCONSISTENCY IN OUTPUT VS SANITY CHECK

Opened: 2026-09-27 by session Claude Sonnet 5 (via NUC worker task 008, reviewed by coordinator).
Severity: LOW (rounding inconsistency; display only, not a defect).
Status: CLOSED.

## DESCRIPTION

net_rr is rounded to 2 dp on output, sanity uses the unrounded value:
72 rows show 2.0 with sanity false. Display only, not a defect.

Per-item doc: research/core_readiness_2026-09-27/CORE_READINESS_PLAN.md
section 2, finding F11.

## BLOCKS

- No direct blocking items.

## UPDATES

2026-09-27: Filed per CORE_READINESS_PLAN.md F11.

B073 closed 2026-10-04 (MTS-2026-10-04-0538Z-CLI-BLD-b072-b073-math-object): round, then sanity; see research/BUGS.md B073.
