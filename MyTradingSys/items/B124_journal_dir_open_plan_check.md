# B124 - No check that execution/journal holds a file for each open plan; testnet_canary has no journal check

Status: CLOSED 2026-10-11. Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (c) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

No check that execution/journal holds a file for each open plan; testnet_canary has no journal check.

## Findings

- M30-12 | audit source MyTradingSys/research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-30.md:55-59,76 | C1 verdict NOT | Predates 10-01, open. No check that execution/journal/ holds each open plan; testnet_canary has no journal check.

## Evidence

- MAINTAINER_REPORT_2026-09-30.md:55-59,76: journal-dir loss, cause unknown, recorded in LESSONS_LEARNED G only.
- C1: no check that execution/journal/ holds each open plan; testnet_canary has none.

## Fix shape

Follow-up adds a fail-closed journal check to the canary or the position manager. LIVE PATH rules apply (stage .new, restart/reset-state and API-error tests).

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

2026-10-11: scripts/dev/testnet_canary.py check_journal (open-plan rule mirrors auto_trader.open_plans_from_log). New tests in scripts/dev/test_testnet_canary.py, red before: test_journal_missing_for_open_plan_is_red, test_journal_present_is_ok, test_closed_plan_without_journal_is_ok, test_no_open_plans_ok, test_trades_log_missing_is_warn, test_journal_output_has_no_plan_id. 31 pass. Read-only canary run on the live tree: journal OK, 5 open all journaled.
