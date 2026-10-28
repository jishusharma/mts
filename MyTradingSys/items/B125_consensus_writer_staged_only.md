# B125 - Consensus writer exists only as staged writer.py.new and test_writer.py.new; not promoted, so not live

Status: OPEN. Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (c) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

Consensus writer exists only as staged writer.py.new and test_writer.py.new; not promoted, so not live.

## Findings

- TC-X1-CONSENSUS | audit source MyTradingSys/research/_archive/loose_2026-10/TWO_CORES_READINESS_2026-10-01.md:19 | C1 verdict NOT | Only staged consensus/writer.py.new and test_writer.py.new; no promoted .py, so not live.

## Evidence

- MyTradingSys/backtest/layers/consensus/writer.py.new and test_writer.py.new are the only files; no promoted .py.
- TWO_CORES_READINESS_2026-10-01.md:19 Top-5 #3 acceptance (fire N alerts, count N rows) is absent.

## Fix shape

Promotion per CLAUDE.md: back up to .pre_<tag>, rename, re-gate, then commit. Test must fail on the pre-change code at least once. Layers/alerts is a one-owner area: claim it in SUPERVISOR_LOG first.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

