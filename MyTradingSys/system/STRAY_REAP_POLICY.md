# Stray-process reap policy

`sync.py ship` and `sync.py health` run `scripts/dev/host_health.py`. It REPORTS a stray CPU hog (a process outside the repo's known
set with 3600+ CPU-seconds) to the operator desk with the exact stop command. It stops one itself only when its command line matches a
line of the allow-list below. Never reaped whatever is listed: .mts_live, live_runner_cli, loop-supervisor, start-trading-day,
claude.exe, the ship/deploy processes.

How the operator pre-approves a pattern: add one line `- allow: <text>` under "Allow-list" (case-insensitive; the text must appear in
the process command line, e.g. `- allow: python vp.py`). Remove the line to withdraw it. Commit it through `sync.py ship`.

## Allow-list
