# Testnet status 2026-10-07

- Window: 2026-10-06T02:30:02Z to 2026-10-07T02:30:02Z (24 h). Generated 2026-10-07T02:30:02Z by scripts/dev/testnet_status.py on the desktop.
- Sanitized: no order/plan/client ids, keys or balances; P/L is per-trade net USD only.

## Sources
- auto_trades.jsonl: found, 2221 rows, 0 unparseable line(s)
- trade_ledger.jsonl: found, 257 rows, 0 unparseable line(s), 0 non-trade row(s) ignored
- auto_trader_config.json: found, 5 routing prefixes

## Per family x account (24 h)

| Family | Account | Alerts | Entered | Closed | Wins | Net USD | Busy | AutoPause | Unmapped | Rejected | Halt | Failed | Unresolved |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cryptocred | jishu_4 | 6 | 1 | 1 | 1 | +0.0006 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| fabio | jishu_3 | 3 | 1 | 1 | 0 | -0.0013 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| rsi | jishu_2 | 4 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| rsi | jishu_3 | 30 | 3 | 3 | 1 | +0.0886 | 9 | 0 | 0 | 0 | 18 | 0 | 0 |
| tom | main | 19 | 1 | 1 | 1 | +0.0018 | 0 | 0 | 0 | 17 | 0 | 1 | 0 |
| turn_of_candle | jishu_1 | 934 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 934 | 0 | 0 |

Alerts = signals the trader logged a decision for (rejected, skipped, attempted). Entered = trade_attempt outcome entered. Closed/Wins/Net = resolved ledger rows stamped in the window (win = net > 0). Failed = attempt that did not enter. Unresolved = ledger row without an outcome.

## Zero-trade flags
- FLAG 0 trades in 24 h: rsi / jishu_2
- FLAG 0 trades in 24 h: turn_of_candle / jishu_1

## Open positions (last logged, not live)

Entered in auto_trades.jsonl with no later trade_closed (whole log). Not an exchange reading.

| Account | Open (last logged) |
|---|---:|
| jishu_1 | 0 |
| jishu_2 | 0 |
| jishu_3 | 0 |
| jishu_4 | 0 |
| main | 0 |

## HALT / brake events

- Brake files at run time: none present (existence only; checked when this script ran)
- skipped_halt decisions in window: 963
- auto_trader starts with a brake set in window: 44
- halt_history/: found, 1 archived in window, 3 older
  - 2026-10-06T14:44:15Z HALT_DAILY_LOSS_2026-10-06_deribit502

## OPERATOR_ALERTS.log

- OPERATOR_ALERTS.log: not found

## Recount (haiku-recount-testnet-readout)

Method: day-file table re-summed from its own rows (Entered 6 = Closed 6, Wins 3, Net +0.0897, Halt 963 = skipped_halt 963, zero-trade flags match). Cross-check: `funnel_report.py --day` against the live-tree execution/ inputs (read-only). Keys differ: funnel is per layer:sub:tf and per UTC day, not per family x account and 24 h from 02:30Z; funnel has no account key; funnel alerts are runtime/alerts rows, day-file alerts are auto_trader decisions. The day file was generated at window end (02:30Z), so the later UTC-day funnel run can see rows it could not.
- cryptocred / jishu_4: SAME. Day file alerts 6, entered 1, closed 1, wins 1, net +0.0006; funnel 2026-10-06 cryptocred (fib_pullback 2 + sr_flip 4 alerts; sr_flip 1 filled/1 closed/1 win/+0.0006).
- fabio / jishu_3: SAME. Day file alerts 3, entered 1, closed 1, wins 0, net -0.0013; funnel 2026-10-06 fabio (cvd_absorption 2 + volume_fvg 1 alerts; 1/1/0/-0.0013).
- rsi / jishu_2: DIFF. Day file alerts 4, entered 0 (zero-trade flag). Funnel has no account key; family-level rsi 2026-10-06 + 2026-10-07 shows entries, so the per-account count cannot be confirmed from the funnel.
- rsi / jishu_3: DIFF. Day file alerts 30, entered 3, closed 3, wins 1, net +0.0886; funnel rsi 2026-10-06 entered 1, net -0.0158 (alerts 39 across rsi layers, no account key). Window and key mismatch, not reconciled.
- tom / main: DIFF. Day file alerts 19, rejected 17, entered 1, net +0.0018; funnel tom 2026-10-06 rejected 12, entered 0; 2026-10-07 rejected 13, entered 1, net +0.0018. Rejected count is 17 in the day file vs 25 across the two UTC days; not reconciled.
- turn_of_candle / jishu_1: DIFF. Day file alerts 934 (all skipped_halt), entered 0; funnel turn_of_candle alerts 99 (2026-10-06) + 93 (2026-10-07), 6 filled and net -0.0921 on 2026-10-07 (after the day file was generated). Halt-skip vs alert definition differs.
Overall: DIFF. Table re-sum is internally consistent (SAME on the table itself); cross-source agreement holds only for cryptocred and fabio, the other four rows do not reconcile on the same window and key.
