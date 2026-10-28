# Testnet status 2026-10-05

- Window: 2026-10-04T02:30:02Z to 2026-10-05T02:30:02Z (24 h). Generated 2026-10-05T02:30:02Z by scripts/dev/testnet_status.py on the desktop.
- Sanitized: no order/plan/client ids, keys or balances; P/L is per-trade net USD only.

## Sources
- auto_trades.jsonl: found, 814 rows, 0 unparseable line(s)
- trade_ledger.jsonl: found, 191 rows, 0 unparseable line(s), 0 non-trade row(s) ignored
- auto_trader_config.json: found, 5 routing prefixes

## Per family x account (24 h)

| Family | Account | Alerts | Entered | Closed | Wins | Net USD | Busy | AutoPause | Unmapped | Rejected | Halt | Failed | Unresolved |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cryptocred | jishu_4 | 2 | 2 | 3 | 0 | -0.0606 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabio | jishu_3 | 3 | 2 | 2 | 0 | -0.0209 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_2 | 0 | 0 | 1 | 0 | -0.0631 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_3 | 5 | 1 | 2 | 1 | -0.0537 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| session | jishu_4 | 1 | 1 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| tom | main | 28 | 2 | 3 | 0 | -0.1417 | 0 | 0 | 0 | 22 | 0 | 4 | 0 |
| turn_of_candle | jishu_1 | 69 | 66 | 67 | 9 | -0.5739 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |

Alerts = signals the trader logged a decision for (rejected, skipped, attempted). Entered = trade_attempt outcome entered. Closed/Wins/Net = resolved ledger rows stamped in the window (win = net > 0). Failed = attempt that did not enter. Unresolved = ledger row without an outcome.

## Zero-trade flags
- FLAG 0 trades in 24 h: rsi / jishu_2

## Open positions (last logged, not live)

Entered in auto_trades.jsonl with no later trade_closed (whole log). Not an exchange reading.

| Account | Open (last logged) |
|---|---:|
| jishu_1 | 0 |
| jishu_2 | 0 |
| jishu_3 | 0 |
| jishu_4 | 1 |
| main | 0 |

## HALT / brake events

- Brake files at run time: none present (existence only; checked when this script ran)
- skipped_halt decisions in window: 0
- auto_trader starts with a brake set in window: 0
- halt_history/: found, 0 archived in window, 3 older

## OPERATOR_ALERTS.log

- OPERATOR_ALERTS.log: not found
