# Live check of the W3 layers (2026-10-16, JIS-NUC, read-only on the live tree)

mirror@2026-10-16 13:51Z (JIS-NB, git fc9794f4, flags: HALT). fc9794f4 contains W3 (f036d72d, 2026-10-16 10:58Z) and 28ca4005 (ancestor check: yes).

## Verdict: NOT RUNNING when checked. The runner process predates W3. Cause found and fixed (below).

Evidence (parsed all 3000 lines of the mirrored `runtime_data/live_runner.log`, 2978 `poll` lines, 2026-10-14 07:58Z .. 2026-10-16 13:50Z, 0 Traceback/Exception lines):
- The poll key set changed only twice: 21 keys at 2026-10-14 07:58Z, 22 keys at 2026-10-16 04:49Z (wlow_bounce|bbrsi60|1h added). No key of rsi_divergence, bb_top_reversal, session_levels, candle_close or levels|confluence ever appears.
- Last runner restart: supervisor_log.txt 2026-10-16 10:21Z (`RESTART reason=stale`, wrapper 4248), 37 min before W3 was committed (10:58Z); none since (wrapper 4248 `ok` at 13:51Z).
- Cause: `scripts/dev/auto_deploy.py` RESTART_MAP named the process `live_runner_cli.py`, but the runner runs as `python -m MyTradingSys.backtest.layers.alerts.live_runner_cli` (mts.ps1:318, loop-supervisor.ps1:38) - no `.py` in the command line - so `kill_process` matched 0 processes after every deploy touching alerts/. The orderflow recorder had the same trap and was already fixed by name.

## Fix (this ship)
`RUNNER_PROC = "layers.alerts.live_runner_cli"` in auto_deploy.py; test `test_restart_only_the_processes_whose_files_changed` fails on the old code (97 pass after). DEPLOY_RUNBOOK.md updated. The next AutoDeploy that touches alerts/ or layer packages, or the next stale-restart by loop-supervisor, loads W3 (loop-supervisor relaunches the runner within about a minute after a kill). I did not restart anything (rule). Until then the W3 layers are idle.

## Per layer
| layer | registered in code | live runner state | evaluated bars, errors | gate via `auto_trader.layer_signal` (offline, real config) |
|---|---|---|---|---|
| rsi_divergence (1h) | live_runner_cli.py:515 | NOT loaded (stale process) | 0 polls with key, 0 errors | long/short: no reject, plan built (size 20 / loss 2, config :104) |
| bb_top_reversal (15m) | :516 | NOT loaded | same | same (:112) |
| session_levels (1m) | :517 | NOT loaded | same | same (:108) |
| candle_close (1m) | :518 | NOT loaded | same | same (:116) |
| levels / confluence (1m) | :519 | NOT loaded | same | same (:120) |
| wlow_bounce (1h, bbrsi60) | :505 | LOADED since 04:49Z; 724 polls on the 16th, key present in all | 0 errors (the 533 grep hits were `errors=0` in poll text) | long and short: no reject (:124); alerts need `side`, else `unmapped` |

Decisions in the mirror (`auto_trades.jsonl`, 500 rows): turn_of_candle skipped_halt 112, rsi_events skipped_halt 21+3; rsi:cross unmapped rejects 36 are pre-existing `rsi_events` (not W3). No W3 source appears yet, as expected from the above. Nothing is rejected for promotion_reject in the sample. HALT stays the only expected block.

## Flashing windows (7ffb330a, on fast-track; not yet in this branch)
`git show 7ffb330a:scripts/dev/mts_signal.py`: spawn_send flags = `0x08000000` (CREATE_NO_WINDOW) only, line 173; the git helper run at :67-69 also CREATE_NO_WINDOW. No DETACHED_PROCESS left. Matches the headless-conhost pattern. (The old combination was the bug: CREATE_NO_WINDOW is ignored with DETACHED_PROCESS, so each git child opened a console.)

## Follow-up for whoever reads the next mirror
After the next runner restart, expect 28 poll keys (22 + 5 + ... check `rsi_divergence|rsi_divergence|1h` etc. in the `poll` line) and `HIST_NEED_BARS` history fetches without `fetch:` errors.
