# Stray-process reap policy

`sync.py ship` and `sync.py health` run `scripts/dev/host_health.py`. It REPORTS a stray CPU hog (a process outside the repo's known
set with 3600+ CPU-seconds) to the operator desk with the exact stop command. It stops one itself only when its command line matches a
line of the allow-list below. Never reaped whatever is listed: .mts_live, live_runner_cli, loop-supervisor, start-trading-day,
claude.exe, the ship/deploy processes.

How the operator pre-approves a pattern: add one line `- allow: <text>` under "Allow-list" (case-insensitive; the text must appear in
the process command line, e.g. `- allow: python vp.py`). Remove the line to withdraw it. Commit it through `sync.py ship`.

## Allow-list

## Procs step (scripts/dev/c_drive_guard.py procs): report daily, kill only by PID with `procs --apply`

The daily c_drive_guard run logs a count of stray shells and runtimes (python, pythonw, node, pwsh, powershell, cmd, bash, conhost) older
than 24 h. It kills nothing. `python scripts/dev/c_drive_guard.py procs --apply` kills the KILL rows by PID only, each re-checked in a
fresh process snapshot (same PID, same start time). Never by image name, never a process tree.

Safe patterns (the code constant PROC_SAFE in c_drive_guard.py is what the killer reads; OPERATOR EDIT NEEDED: confirm or strike them,
then the code changes through `sync.py ship`): desk.py, sim_desk, layers.fabio, scripts/dev/, mytradingsys/.

Never, whatever matches: .mts_live, live_runner, loop-supervisor, start-trading-day, oi_recorder, orderflow_live, htf_context_live,
deploy, auto_deploy, wait_then_ship, cicd_run, `sync.py` with `ship`, every java process, any process with a claude.exe ancestor, and any
ancestor whose command line holds one of the words above.
