# MTS-2026-10-02-2135Z-CLI-BLD-scheduler-stack
status: closed
started: 2026-10-02T21:35:00+00:00
ended: 2026-10-02T21:50:00+00:00
type: build
model: Sonnet 5.5
task: scheduler stack T0-T9 (detectors, tick, worker prefix, run_worker, prefix test, Task Scheduler entry)
owner: CLI-BLD

## T0 facts
- claude.exe: C:\Users\E-ngineers\.local\bin\claude.exe (exists)
- claude --help: --max-budget-usd present; --max-turns NOT listed. run_worker probes help and omits it (budget + wall TTL bound the run).
- python 3.14.6
- scripts/sched, system/sched, runtime/sched, research/sched_reports: all False before build.

## Deviations
- --max-turns unsupported in this CLI build: not passed.
- Build-Check and run_all_tests --quick not wired into tick (plan s9: verify runtime/exit mapping first); canary wired.
- Orphan sweep of claude.exe by dead wrapper PID not built (Job Object kill-on-close + TTL + pid_gone ledger field are).
- Prefix is 2.6 KB, below any model cache minimum: cache reads will not apply until the prefix grows with real content.
- Task MTS-Scheduler-Tick registered then Disabled (its trigger would start in 1 min). Enable when ready.
- tests/test_worker_prefix_hash.py not added to run_all_tests (existing file); run: python -m unittest tests.test_worker_prefix_hash
- .gitignore: scheduler runtime state and tick/worker reports ignored.
