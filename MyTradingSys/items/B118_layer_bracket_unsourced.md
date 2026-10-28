# B118 - Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 100 for every layer alert

Status: CLOSED 2026-10-11 (option 1, label only). Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (b) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 100 for every layer alert.

## Findings

- M29-13 | audit source MyTradingSys/research/fast_track_2026-09-27/MAINTAINER_REPORT_2026-09-29.md:74; MAINTAINER_REPORT_2026-09-30.md:51-52 | C1 verdict NOT | Predates 10-01, open. auto_trader.py:69 layer bracket still fixed stop_pct 1.0, targets 2, size 100.

## Evidence

- MyTradingSys/execution/auto_trader.py:69 layers config: size_usd 100, max_loss_usd 10, stop_pct 1.0, targets 2, hours 2.0, max_age_bars 1.2, max_hold_bars 8.
- MAINTAINER_REPORT_2026-09-29.md:74 and 2026-09-30.md:51-52 flagged the brackets; falls under the CLAUDE.md provenance rule.
- Comment at :68 states layers have no stop or target of their own, so every value is ours.

## Fix shape

Follow-up session: source each value or flag it as sampling-only. LIVE PATH: auto_trader.py is imported by the running testnet system. Stage as auto_trader.py.new, never edit in place, builders never restart; only the supervisor restarts after the fix is committed and gated. Needs a restart/reset-state, non-trade-balance and API-error test.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

2026-10-11 (relay JIS-NB, default option 1): auto_trader.DEFAULT_CONFIG layers.bracket_source = "SAMPLING"; layer_signal sets sig["log"]["bracket_source"], so every layer trade_attempt / signal_rejected / skipped row carries it (Tom rows do not). Values unchanged (no tuning). New tests test_auto_trader.py test_layer_trade_log_rows_carry_bracket_source_sampling (red on old code: 2 errors CycleTest+RecoverTest) and test_tom_trade_row_has_no_bracket_source; 96 pass. Edited in the relay worktree only; live tree gets it via supervisor deploy/restart. Option 2 (grid run) not done; bracket stays NO-SOURCE.
