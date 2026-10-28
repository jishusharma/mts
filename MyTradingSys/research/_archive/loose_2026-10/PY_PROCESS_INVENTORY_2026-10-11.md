# python.exe inventory, JIS-NB, 2026-10-11 ~15:45 local

Read-only. Nothing killed. Re-run: `powershell -File scripts/dev/py_inventory.ps1`.
Count at capture: 20 processes (python.exe + pythonw.exe), not 25+. Several are the WindowsApps launcher shim plus its real child
(2 PIDs per logical process), which inflates the count. Logical processes: 14.

## Expected MTS loop (keep)
| PID | Process | Started | Note |
|---|---|---|---|
| 6924 | auto_trader | 10-10 18:44 | parent PID 24820 gone: normal, supervisor launcher exits after spawn |
| 24128 | live_runner_cli | 10-10 18:44 | parent cmd.exe |
| 3548 | orderflow_live | 10-10 18:44 | parent gone, normal |
| 10356 | daily_loss_monitor | 10-11 14:23 | restarted today (deploy or supervisor) |
| 23972, 22616 | position_manager L-mkt-1011-0955, S-mkt-1011-1000 | 10-11 15:25, 15:30 | OPEN POSITIONS' managers, children of auto_trader. Never kill. |
| 14892 | kline_archiver | 10-11 15:42 | parent cmd.exe |
| 14132 + 11680 | htf_context_live --loop (shim + child) | 10-08 11:17 | one loop (shim parent + child), up 3 days, OK |

## Active sessions (not orphans, finish on their own)
27380 -> 26276 -> 28840 -> 24676 -> 19968 -> 26316: `sync.py ship` -> `run_all_tests.py --quick` -> run_extra_tests -> pytest
test_worker_prefix_hash, started 15:40-15:42, another session's ship. Do NOT stop-day mid-ship; it also runs pytest for
`mts-relay-20261011T1008`.

## Suspect (needs operator OK before any kill)
| PID | Process | Started | Why |
|---|---|---|---|
| 17588 + 9592 | `python -m http.server 8765 --bind 127.0.0.1` | 10-10 22:02 | Parent is a bash.exe (PID 13448) from a Claude session; no MTS script launches this. Likely a leftover preview server from a past session. Idle (CPU 0-1 s). Harmless, 22 MB. Candidate to kill. |

## Orphans from crashed sessions
None found: every non-MTS python has a live parent, and no process has hours of CPU while idle. Parent-dead entries above are
launcher-exit patterns (supervisor starts a process, launcher exits), matching the long-running loop members.

## Notes
- No duplicate loop members (one each of auto_trader, live_runner_cli, orderflow_live, daily_loss_monitor, htf_context_live).
- The ESET/Defender CPU problem (MsMpEng 16-17%) is separate from python; python processes here total ~14 s CPU in the last
  hour except live_runner_cli (117 s since 10-10) and daily_loss_monitor (77 s): normal.
- Stop-day will take the loop down; position managers 23972/22616 guard open positions: operator should confirm those
  positions are closed or accept manager downtime before stop-day.ps1.
