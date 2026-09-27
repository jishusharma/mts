# B074 - RULE-ORDER DEPENDENCE IN COMPUTE-VERDICT AFFECTS SNAPSHOT OUTCOME

Opened: 2026-09-27 by session Claude Sonnet 5 (via NUC worker task 008, reviewed by coordinator).
Severity: LOW (contradiction cap runs before broken-value override; non-actionable).
Status: OPEN.

## DESCRIPTION

Rule-order dependence in Compute-Verdict: contradiction cap runs
before the broken-value override, so the same snapshot ends WAIT_PROOF or
WAIT_RR depending on L2. Both non-actionable; reason text differs.

Per-item doc: research/core_readiness_2026-09-27/CORE_READINESS_PLAN.md
section 2, finding F12.

## BLOCKS

- No direct blocking items.

## UPDATES

2026-09-27: Filed per CORE_READINESS_PLAN.md F12.
