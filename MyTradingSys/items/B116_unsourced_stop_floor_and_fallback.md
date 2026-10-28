# B116 - Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in SetupCandidatesBuilder

Status: CLOSED 2026-10-06 (receipt in BUGS.md, MTS-2026-10-06-2122Z-APP-COO-registry-fix). Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (b) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in SetupCandidatesBuilder.

## Findings

- RA-W4-A03 | audit source MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md:209-210 | C1 verdict NOT | Floor still live at SetupCandidatesBuilder.java:48,126-128; unsourced value not removed or tested.
- RA-W4-A04-M11 | audit source MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md:212 | C1 verdict NOT | Fallback stop still present at SetupCandidatesBuilder.java:129; not removed.

## Evidence

- src/main/java/datafeed/SetupCandidatesBuilder.java:48 MIN_STOP_PCT = 0.001 (comment: v1.3.3 floor, 0.1 percent from zone).
- SetupCandidatesBuilder.java:126-129: stop closer than MIN_STOP_PCT is replaced by zonePrice * 1.002 (short) or * 0.998 (long), a 0.2 percent fallback.
- Rule 32 evidence cited in the code comment is a candidate-count observation (100 of 750 under 0.05 percent), not a trader quote.
- Neither value has a test and neither is in a provenance row as SOURCED.

## Fix shape

Follow-up session: decide per CLAUDE.md provenance rule. Remove both values, or replace them with a trader-sourced rule (transcript quote plus file:line). Never tune. SetupCandidatesBuilder is Java under the live tree, so stage and re-gate before promotion.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

