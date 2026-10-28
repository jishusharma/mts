# DEVICE TASKS

Rule: a chore every device must do (cleanup, guard scripts, installs) is defined ONCE in `MyTradingSys/system/DEVICE_TASKS.json`, with the devices it applies to. No other doc keeps a per-device list for it; they point here.
- Entry: `id`, `what`, `run` (exact command, PowerShell 5 safe, no `&&`), `verify` (exits 0 when done), `applies_to` (device names or `"all"`), `added`, `by_hook`. Devices are the file's `devices` list (old and new host names match, hosts.py).
- Add: `python scripts/dev/device_tasks.py add --id X --what "..." --run "..." --verify "..." --applies all` writes the entry and broadcasts it HIGH (with the run command) to every host; then `sync.py ship`. New device: `device_tasks.py add-device NAME` (tasks marked "all" cover it at once).
- Check this host: `python scripts/dev/device_tasks.py check` (DONE / MISSING / UNKNOWN, exit 1 on MISSING). The daily c_drive_guard SessionStart run does it report-only and posts one signal line, so
- `python scripts/dev/device_tasks.py matrix` shows task x device from the latest reports (UNKNOWN = that device has not reported yet; `-` = not for it).
- Probes for verify commands: `device_tasks.py probe free-gb|behind|env|git-min|no-mts-tasks`. No scheduler is added (SCHEDULING_POLICY.md).
Reports are `ack` records with id `device-tasks` in the signals repo; MISSING stays visible in the matrix until the device's next daily run.
