# B153 - net_rr floor stays at NO-SOURCE 1.25 with no owner for the 'restore after P4' note; Python and Java net_rr have no direct cross-language parity test; B136 residual still fail-open

Status: OPEN. Severity: LOW. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

net_rr floor stays at NO-SOURCE 1.25 with no owner for the 'restore after P4' note; Python and Java net_rr have no direct cross-language parity test; B136 residual still fail-open.

## Evidence

- system/net_rr_floor.json still 1.25, note 'lowered for testnet collection; restore after P4'. P4 ended NO REPLICATION at 4h/8h/12h (075e1c5, research/P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md; net -9.6 to -10.2 bp, CIs below zero). P4 is a different study, so its closure does not trigger a restore and nothing tracks one (only SUPERVISOR_LOG.md:260 'edit that one line').
- Worker re-computation: entry 60000, stop 59940, target 60180 gives net_rr 1.0 in Python (mts_math.py:78) and by hand in Java (ExecutionMathConstants.netRR); no discrepancy. No test feeds the same inputs to both; parity is indirect (test_b070_fee_parity.py compares constants; NetRRConstantTest.java:28 and test_mts_math.py:229 assert the same vector).
- B136 residual confirmed: MarketDataSnapshot.java:1498-1541 buildOiBreakdown still writes retail/whale/topAccounts as 0.0 on failure (confidence LOW, no unavailable_fields). No production Python reader of oi_breakdown found, so impact is limited to the snapshot JSON.

## Fix shape

Operator decision with owner and end date: restore 2.0, keep 1.25 with expiry, or pause Tom trading. Add one table-driven Python/Java parity test (expected values from FORMULAS.md section 17). Close B136 by emitting UNAVAILABLE.

## Related

- MyTradingSys/research/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

# END
