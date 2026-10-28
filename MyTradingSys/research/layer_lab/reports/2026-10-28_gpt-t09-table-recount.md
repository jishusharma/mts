# GPT T09 table recount - 2026-10-28

Verdict: **FIX-FIRST** - the exact-match total is **3,156**, not “3,200+”; the export also undercounts RSI 1h live by one.

## Checked

- Read the scope files: `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T09_live_parity.md`, `MyTradingSys/research/sim_desk/results/t09_live_parity.json`, and `MyTradingSys/research/sim_desk/export_results.py`.
- Followed the cited output sources `scripts/T09/out/parity_result.json` and `scripts/T09/out/exit_result.json` under the audit directory. Checked the exporter’s generated JSON `results/t09_live_parity.json` against the source records.
- Recounted section 4's exact rows: turn_of_candle 2,880 + session_momentum 30 + cvd_absorption (77+22) + sr_flip (102+28) + failed_msb (8+9) = **3,156**. Exported statement is line 169 of `export_results.py`; source statement is T09 line 72.
- Recounted volume_fvg: 15m (15 side + 1 off-by-one + 3 backtest-only = 19), 1h (3 side + 1 off-by-one + 1 backtest-only = 5); combined: **24 backtest signals, 0 same + 18 side + 2 off-by-one + 4 backtest-only**. No live-only rows.
- Export split yields 20 per-key table rows; 18 logical rows in the source table include grouped timeframe entries. No DEV candle bars or new backtest run were needed; this is a count audit of existing outputs, so the PRE_REG_TEMPLATE run-readiness checklist did not apply.

## Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| HIGH | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T09_live_parity.md:72`; `MyTradingSys/research/sim_desk/export_results.py:169` | The exact-match claim “0 differences in 3,200+ signals” overstates the denominator. | The five named families' exact rows sum to 3,156 (2,880+30+99+130+17). The source table and export statement both say 3,200+. | Replace with “0 differences in 3,156 signals” (or correct the source rows if the intended population differs). SONNET follow-up created: `correct-t09-exact-match-count-and-3-200-`. |
| MED | `MyTradingSys/research/sim_desk/export_results.py:123-124`; `MyTradingSys/research/sim_desk/results/t09_live_parity.json` (`examples[0].rows`, `rsi_events 1h`) | The export's RSI 1h Live count is 27, one below the source table's 28. | Source `parity_result.json` has `live_tradable_side=28`, `same=3`, `live_only=24`; exporter computes Live as 3+24=27. The source table T09 section 4 and exported JSON side-category values otherwise show 3 same and 24 live-only. | Export the source's live tradable/accepted count for the Live column, and preserve the category totals separately. |

No new run was performed. No market bars were inspected. The audit is limited to the counts and exporter text named in this card.

Follow-up cards created: `correct-t09-exact-match-count-and-3-200-` (HIGH).
