# WORKSTATION MODES (authority for operator_reminders.md section 0) - 2026-09-29

| Machine | Roles | Allowed | Never |
|---|---|---|---|
| Desktop JIS-NB | Tom loop (armed), auto_trader, live_runner_cli, daily_loss_monitor, testnet suites, polling station (inbox_poller), supervisor session + hourly check, git commits | everything in CLAUDE.md | mainnet without the S5 gates |
| NUC JIS-NUC | Qwen worker (nuc-worker.ps1, qwen3-coder:30b primary, qwen3.6 think-on retry) | queue tasks, ssh gate verbs | commits, trading |
| Laptop DESKTOP-F7IU69N (i7-8550U, 31.8 GB, no GPU) | 1 DSA browser worker (scripts/worker/dsa_worker.py, lane incoming_dsa via \JIS-NB\MTS-Queue), 2 read-only monitors (queue status, HALT files, auto_trades, ledger), 3 Claude CLI for questions / polling-station asks | read, ask, run the DSA worker | loop control, trading processes, commits to the desktop repo, testnet suites |

Laptop setup order: Chrome -> `pip install playwright` -> copy scripts/worker/dsa_*.py + dsa_selectors.json + start-dsa-chrome.ps1 ->
point the worker's queue root at \JIS-NB\MTS-Queue -> log in to DSA in the dedicated Chrome -> `--calibrate` -> `--once` -> loop.
Git 2.24.1 on the laptop is old; update before any clone. No Ollama on the laptop: CPU-only 14B runs ~2 tok/s, slower than the NUC queue.
