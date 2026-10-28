# B171 - Snapshot OI field is a quantized gauge; the full-precision OI series is unread

Status: OPEN. Severity: MED. Opened 2026-10-10.
Source: DSA session MTS-2026-10-10-1608Z-DSA-COO, OI divergence research pass.

## What it is

The live snapshot carries only three OI fields: open_interest.direction, open_interest.change_1h_pct,
and open_interest.delta_state. change_1h_pct has two-decimal resolution. Measured over the 28-day
snapshot window: min -2.34, max 2.21, mean -0.0208. Small OI moves round to zero, so 7584 of 21379
rows (about 35 percent) fall into a flat bucket. The signal is quantized away before any layer sees it.

## What exists on disk but is unread

- Dumps/backtest/raw/metrics: 391 daily CSVs, 5-minute cadence, column sum_open_interest, full
  precision. Window 2025-09-01 to 2026-09-26. 112608 records.
- MyTradingSys/runtime/oi_live/oi_1m.csv: 1-minute cadence, column openInterest, from 2026-10-05.
- MyTradingSys/runtime/oi_live/oi_5m_30d.csv: 5-minute, 30-day window.

No layer reads any of these. mts_math.py lists open_interest fields as contextual only.
quad_classify.py reads change_1h_pct for a regime label.
## Evidence from the research pass

Three OI divergence tests ran 2026-10-10. The last is pre-registered, cost-aware, regime-stratified,
walk-forward: research/_archive/loose_2026-10/PRE_REG_OI_DIVERGENCE_2026-10-10.md, result appended. 2350 events, 24 cells,
Bonferroni divisor 24. Every cell negative after fees, slippage and funding; magnitude at the cost
floor. VERDICT: NO REPLICATION for OI divergence as a directional signal on 15-minute bars.

That verdict does not settle this bug. The bug is about the field: the snapshot value cannot support
any precision-sensitive test, and the usable series sits idle.

## What Claude decides

1. Does any layer consume the full-precision OI series? If yes: which file (metrics archive for
   research, oi_live for live) and at what cadence.
2. If no layer will: mark OI display-only and record the reason, so this does not reopen.

## Detail files

- research/_archive/loose_2026-10/PRE_REG_OI_DIVERGENCE_2026-10-10.md
- research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md
- research/_archive/loose_2026-10/OI_DIVERGENCE_2026-10-10.md, research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md
- research/loose_code/oi_divergence_v2_2026-10-10.py (reusable: 15m bars, cost wiring, regime labels)