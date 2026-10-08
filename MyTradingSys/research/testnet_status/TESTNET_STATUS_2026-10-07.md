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
