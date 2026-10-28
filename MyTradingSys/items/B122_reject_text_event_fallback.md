# B122 - auto_trader.py reject text uses alert.get('event') instead of the fallback key

Status: OPEN. Severity: COSMETIC. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (c) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

auto_trader.py reject text uses alert.get('event') instead of the fallback key.

## Findings

- M29-17 | audit source MyTradingSys/research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-29.md:79 | C1 verdict NOT | Predates 10-01. auto_trader.py:313 reject text still uses alert.get('event') not the fallback.

## Evidence

- MyTradingSys/execution/auto_trader.py:313 reject text still uses alert.get('event') rather than the fallback.

## Fix shape

One-line follow-up. LIVE PATH file: stage as .new, supervisor restarts.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

