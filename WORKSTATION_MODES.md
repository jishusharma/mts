# WORKSTATION MODES (authority for operator_reminders.md section 0) - 2026-09-29

| Machine | Roles | Allowed | Never |
|---|---|---|---|
| Desktop JIS-NB | DSA browser worker (operator 2026-09-29: login/captcha where the operator is; Chrome profile, downloads, logs on F:\MTS\dsa; queue = local Dumps\workers\NUC-QUEUE, lane incoming_dsa, no share), Tom loop (armed), auto_trader, live_runner_cli, daily_loss_monitor, testnet suites, polling station (inbox_poller), supervisor session + hourly check, git commits | everything in CLAUDE.md | mainnet without the S5 gates |
| NUC JIS-NUC | Qwen worker (nuc-worker.ps1, qwen3-coder:30b primary, qwen3.6 think-on retry) | queue tasks, ssh gate verbs | commits, trading |
| Laptop DESKTOP-F7IU69N (i7-8550U, 31.8 GB, no GPU) | 1 read-only monitors (queue status, HALT files, auto_trades, ledger via \\JIS-NB\MTS-Queue), 2 Claude CLI for questions / polling-station asks | read, ask | loop control, trading processes, DSA worker, commits to the desktop repo, testnet suites |

DSA worker setup (desktop): `python -m pip install playwright` -> scripts\worker\start-dsa-chrome.ps1 (profile F:\MTS\dsa\chrome-profile) ->
log in to DSA -> fill scripts\worker\dsa_selectors.json -> start-dsa-worker.ps1 -Calibrate -> -Once -> start-dsa-worker.ps1 (loop, logs F:\MTS\dsa\logs).
Laptop: no Ollama (CPU-only 14B ~2 tok/s); update Git 2.24.1 before any clone.
