# WORKSTATION MODES (authority for operator_reminders.md section 0) - 2026-10-06

Identify the machine by hostname (`$env:COMPUTERNAME`), never by username. Details, remote access
and sync: MyTradingSys/system/DEVICES.md. PROPOSED rows are pending the operator (B137).

| Machine | Roles | Allowed | Never |
|---|---|---|---|
| Desktop JIS-NB | Operator's main screen. DSA browser worker (login/captcha where the operator is; Chrome profile, downloads, logs on F:\MTS\dsa; queue = local Dumps\workers\NUC-QUEUE, lane incoming_dsa, no share), Tom loop (armed), auto_trader, live_runner_cli, daily_loss_monitor, testnet suites, polling station (inbox_poller), supervisor session + hourly check, git commits | everything in CLAUDE.md | mainnet without the S5 gates; any background process that opens, flashes or focuses a window (alerts excepted: they show and stay) |
| NUC JIS-NUC | Backtests and heavy research on F:\MTS\repo + F:\MTS\data (Qwen lane decommissioned 2026-10-01) | NUC-eligible backtests (DEVICES.md section 7), one-shot scheduled-task jobs, ssh gate verbs | commits; trading and the live loop only after the move decision in DEVICES.md section 3 (one owner machine at a time) |
| Laptop DESKTOP-F7IU69N (i7-8550U, 32 GB, no GPU) | Travel: full work through Remote Desktop into JIS-NB / JIS-NUC. Home: infrastructure, Claude app, read-only monitors via \\JIS-NB\MTS-Queue | inside an RDP window: whatever that machine allows. Locally: read, ask, clone/pull, cloud work | running its own live loop or trading processes; commits to the desktop repo from the laptop's own clone |

The live loop may be started from any device but runs on one machine only (DEVICES.md section 3).
Remote Desktop into the desktop: close with Disconnect, never Sign out (sign-out kills the live loop).

DSA worker setup (desktop): `python -m pip install playwright` -> scripts\worker\start-dsa-chrome.ps1 (profile F:\MTS\dsa\chrome-profile) ->
log in to DSA -> fill scripts\worker\dsa_selectors.json -> start-dsa-worker.ps1 -Calibrate -> -Once -> start-dsa-worker.ps1 (loop, logs F:\MTS\dsa\logs).
Laptop: no Ollama (CPU-only 14B ~2 tok/s); update Git 2.24.1 before any clone.
