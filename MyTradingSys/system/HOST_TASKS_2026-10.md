# JIS-NB Windows tasks (MTS-*), 2026-10-15

> **RETIRED 2026-10-17, see SCHEDULING_POLICY.md.** Operator 2026-10-17: every scheduled task on every device is removed; this table is history, the current state is in SCHEDULING_POLICY.md section 5.

`Get-ScheduledTask` 08:33 IST: 21 tasks. Nothing changed; decision q-host-sched-tasks (OPERATOR_DECISIONS.md).

| Task | Runs | Last result | Finding | Action |
|---|---|---|---|---|
| MTS-Scheduler-Tick | scripts/sched/tick.py, 15 min | 0 | legacy Tier-0 clock; only reader is run_worker.py (NUC lane, retired 10-01); 982 tick_*.md in live tree | disable; unregister after 7 quiet days |
| MTS-Live-Health | check_live_health.py in BinanceDataFeed.registry, 5 min | 0 | checkout 1621 commits behind, 1 commit not on trunk (4fc5e6c0); the script equals trunk | point the launcher at the live tree |
| MTS_Monitor_4h | mts/research/rerun_monitor.ps1 | 0x80070420 (09-17) | target gone; one-shot | unregister |
| MTS-Audit-Digest, -Rotation | scripts/worker/audit_*.py, daily | 0, running | built for the NUC Qwen queue (retired 10-01) | confirm no reader, disable |
| MTS-Backup | backup_snapshot.py in mts-push, 15 min | 1 (08:22) | failing; mts-push 1200 behind; :07 slot = time of the 03:07 gc that reset tidy's idle clock (not proven) | read its log, fix |
| Alert-Rate-Check, Audit-Digest, Declutter-Backups, Orphan-Watchdog, Retention | daily 08:35-09:10 | last run 10-11 | registration updated 10-14 (event 140) | check they ran 10-15 |

No daily job points at an archived script; MTS_Monitor_4h is the only task whose target is gone.
Skip on battery: Live-Health, Feed-Watchdog, OI-Recorder, Scheduler-Tick, Supervisor, Wrapper, Retention, testnet status.
OK, no action: testnet canary, testnet status, AutoDeploy, CDriveCare (mts-dsa), DailyHygiene, Feed-Watchdog, LiveMirror,
Make-Status, OI-Recorder, Supervisor and Wrapper (logon start).
