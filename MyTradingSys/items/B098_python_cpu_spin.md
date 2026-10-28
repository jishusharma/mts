# B098 - Seven Python processes spinning at ~9% CPU each

Status: WONTFIX | Severity: LOW | Opened 2026-10-03

Closed 2026-10-03 17:45Z: process map read in the same session. The 79 percent CPU spike is TF8 backtest worker pool (parent PID 18840 running run_v3_l3, 7 multiprocessing-fork children started 11:40:12 PM, about 160 seconds CPU each in 3 minutes). The aux stack cpu_sec totals seconds, not the cause. No fix owed.

## Observed

Task Manager screenshot, 2026-10-03 ~23:00 IST.

- CPU 79%, Memory 54%
- Seven Python processes, each 8.5-9.1% CPU, 18.6-21.6 MB working set, 0 MB/s disk, 0 Mbps network
- Python (default) group of 5 at 4.9%
- Claude 61 helper processes, 2.6 GB, 1.3% CPU
- Chrome 31 processes, 2.7 GB, 0.6% CPU
- IntelliJ 3 processes, 879 MB, 0.8% CPU

The seven Pythons alone are ~63% of total CPU. Disk and network are at zero.
Each process is CPU-bound with no I/O. That is the signature of a tight loop.

## Suspected set

The live aux stack, launched by Watch-Aux and position managers.

- auto_trader.py (PID 5320 after the TF5 restart)
- position_manager.py x 3 (plans L-lim-1003-1604, L-mkt-1003-1700, L-mkt-1003-1715)
- daily_loss_monitor.py
- live_runner_cli.py
- orderflow_live (orderflow writer)

Count matches seven. Mapping must be confirmed by reading ProcessId -> CommandLine.

## Candidate causes

1. Tight loop with no sleep in any of the aux scripts (most likely).
2. A sleep interval set to 0 (e.g. a poll cadence that was meant to be seconds got passed as milliseconds).
3. A retry loop hammering a failing call at max rate (network is 0 Mbps, so if there is a retry it is on a local resource).
4. Three position managers each polling their own plan file on a sub-second cadence.

## Fix shape (not yet chosen)

Read each aux script and position_manager.py. Find the sleep or poll interval. Identify the file whose loop lacks a sleep or whose interval is wrong. One writer per file set. Staged .new if a live process imports the file.

## Evidence

Screenshot supplied by operator 2026-10-03. Saved by reference; process map captured by this session.