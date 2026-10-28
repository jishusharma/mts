# B117 - Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING in start-trading-day.ps1

Status: OPEN. Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (b) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING in start-trading-day.ps1.

## Findings

- RA-W4-V02 | audit source MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md:214 | C1 verdict NOT | Bands remain at scripts/core/start-trading-day.ps1:225-230; test_b076 only pins them.

## Evidence

- scripts/core/start-trading-day.ps1:225-230: proof under 3 gives WAIT_PROOF, under 5 gives WATCH, otherwise SETUP_FORMING.
- B076 and T052 touch only SETUP_CONFIRMED. MyTradingSys/tests/test_b076_setup_confirmed_unreachable.py pins the 3/5 thresholds rather than sourcing them.
- REVALIDATION_ACTIONS_2026-10-01.md:214 marks the bands NO-SOURCE.

## Fix shape

Follow-up session: source the bands from the trader's own words or remove them. Update test_b076 together with the code, not before.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

