# B074 - RULE-ORDER DEPENDENCE IN COMPUTE-VERDICT AFFECTS SNAPSHOT OUTCOME

Opened: 2026-09-27 by session Claude Sonnet 5 (via NUC worker task 008, reviewed by coordinator).
Severity: LOW (contradiction cap runs before broken-value override; non-actionable).
Status: FIXED (2026-10-04).

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
2026-10-04: FIXED in start-trading-day.ps1 (broken-value override now runs before the proof_dir caps); pinned by MyTradingSys/tests/test_b074_rule_order.py (fails on pre-change file, passes after); residual: WATCH-tier snapshots still differ in reason text by proofDir. Session MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper.
