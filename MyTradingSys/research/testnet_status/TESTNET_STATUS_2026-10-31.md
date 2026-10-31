# Testnet status 2026-10-31

- Window: 2026-10-30T05:35:32Z to 2026-10-31T05:35:32Z (24 h). Generated 2026-10-31T05:35:32Z by scripts/dev/testnet_status.py on the desktop.
- Sanitized: no order/plan/client ids, keys or balances; P/L is per-trade net USD only.

- Owner host: DESKTOP-F7IU69N (Lenovo) per live_owner.py check (fresh heartbeat, 2026-10-31); JIS-NB holds the .mts_live-marked checkout but its runtime files are stale (auto_trades.jsonl last written 2026-10-20), so this page reads a stale JIS-NB copy, not the live loop
- Engine state: last log row 2026-10-20T17:45:42Z (251.8 h before window end): STALE (over 6 h; this copy is not a live reading)
- Calibration rows (pre_pipeline_sources) never count toward the GO_LIVE_BAR.

## Sources
- auto_trades.jsonl: found, 5802 rows, 0 unparseable line(s)
- trade_ledger.jsonl: found, 813 rows, 0 unparseable line(s), 0 non-trade row(s) ignored
- auto_trader_config.json: found, 19 routing prefixes
- promoted_setups.json: found, 0 promoted source(s)
- pre_pipeline_sources: 27 calibration prefix(es)

## Per family x account (24 h)

| Family | Account | Label | Alerts | Entered | Closed | Wins | Net USD | Busy | AutoPause | Unmapped | Rejected | Halt | Failed | Unresolved |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cryptocred | jishu_16 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cryptocred | jishu_17 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cryptocred | jishu_18 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cryptocred | jishu_19 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cryptocred | jishu_20 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabio | jishu_11 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabio | jishu_12 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabio | jishu_13 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabio | jishu_14 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fabio | jishu_15 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| positioning | jishu_10 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_2 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_3 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_4 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_7 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rsi | jishu_8 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| session | jishu_9 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| tom | main | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| turn_of_candle | jishu_1 | calibration | 0 | 0 | 0 | 0 | +0.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

STALE: the newest auto_trades.jsonl row predates this window, so the zeros above mean no data in the window, not no trading. Read the live owner's files for a live number.

Alerts = signals the trader logged a decision for (rejected, skipped, attempted). Entered = trade_attempt outcome entered. Closed/Wins/Net = resolved ledger rows stamped in the window (win = net > 0). Failed = attempt that did not enter. Unresolved = ledger row without an outcome.

## Zero-trade flags
- FLAG 0 trades in 24 h: cryptocred / jishu_16
- FLAG 0 trades in 24 h: cryptocred / jishu_17
- FLAG 0 trades in 24 h: cryptocred / jishu_18
- FLAG 0 trades in 24 h: cryptocred / jishu_19
- FLAG 0 trades in 24 h: cryptocred / jishu_20
- FLAG 0 trades in 24 h: fabio / jishu_11
- FLAG 0 trades in 24 h: fabio / jishu_12
- FLAG 0 trades in 24 h: fabio / jishu_13
- FLAG 0 trades in 24 h: fabio / jishu_14
- FLAG 0 trades in 24 h: fabio / jishu_15
- FLAG 0 trades in 24 h: positioning / jishu_10
- FLAG 0 trades in 24 h: rsi / jishu_2
- FLAG 0 trades in 24 h: rsi / jishu_3
- FLAG 0 trades in 24 h: rsi / jishu_4
- FLAG 0 trades in 24 h: rsi / jishu_7
- FLAG 0 trades in 24 h: rsi / jishu_8
- FLAG 0 trades in 24 h: session / jishu_9
- FLAG 0 trades in 24 h: tom / main
- FLAG 0 trades in 24 h: turn_of_candle / jishu_1

## Open positions (last logged, not live)

Entered in auto_trades.jsonl with no later trade_closed (whole log). Not an exchange reading.

| Account | Open (last logged) |
|---|---:|
| jishu_1 | 0 |
| jishu_10 | 0 |
| jishu_11 | 0 |
| jishu_12 | 0 |
| jishu_13 | 0 |
| jishu_14 | 0 |
| jishu_15 | 0 |
| jishu_16 | 0 |
| jishu_17 | 0 |
| jishu_18 | 0 |
| jishu_19 | 0 |
| jishu_2 | 0 |
| jishu_20 | 0 |
| jishu_21 | 0 |
| jishu_3 | 0 |
| jishu_4 | 0 |
| jishu_7 | 0 |
| jishu_8 | 0 |
| jishu_9 | 0 |
| main | 0 |

## HALT / brake events

- Brake files at run time: HALT, AUTO_PAUSE (existence only; checked when this script ran)
- HALT: present
- HALT_DAILY_LOSS: absent
- AUTO_PAUSE: present
- skipped_halt decisions in window: 0
- auto_trader starts with a brake set in window: 0
- halt_history/: found, 0 archived in window, 7 older

## OPERATOR_ALERTS.log

- OPERATOR_ALERTS.log: not found

## Funnel (scripts/dev/funnel_report.py --days 1, read from the JIS-NB checkout)

- TOTAL for 2026-10-31 UTC: alerts 0, rejected 0, skipped 0, attempts 0, filled 0, nofill 0, closed 0, wins 0. Zeros of a stale copy (see Engine state), not a live reading.

## Owner evidence

- live_owner.py check (owner marker): live loop owned by DESKTOP-F7IU69N, heartbeat under 10 s old.
- live_mirror.py brief: LIVE OWNER desktop-f7iu69n; the JIS-NB copy is refused as not the owner's.
- The JIS-NB checkout is marked by .mts_live but its auto_trades.jsonl was last written 2026-10-20 and trade_ledger.jsonl 2026-10-15: it is not running the loop.
- system/live_host.txt still says JIS-NB (stale). DECISION (OURS): left unchanged here because two tests in scripts/dev/test_live_mirror.py (test_hostname_case_does_not_matter, test_worktree_on_jis_nb_reads_local_folder) read the real file and fail when it names DESKTOP-F7IU69N; the file is to be corrected together with those tests. The owner marker already overrides the file (LIVE_MIRROR.md).
- NOT_RUN: the owner host own files are not readable from this host; a live readout needs this script run on DESKTOP-F7IU69N.
