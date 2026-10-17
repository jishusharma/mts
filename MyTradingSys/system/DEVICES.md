# DEVICES

> Scheduled tasks: none are allowed on any device (RETIRED 2026-10-17, see SCHEDULING_POLICY.md); mentions below of MTS-* tasks, dispatcher, AutoDeploy, Supervisor are the old design.

Reference for every machine this project runs on: hostnames, addresses, disks, shares, and the rules that touch them. Read it before touching network
paths, shares, scheduled tasks or the live loop. What each machine and login does, and what it may touch: HOW_MTS_RUNS.md (the one table).
No fabricated values: an unconfirmed field says NOT CAPTURED; fill it from the command shown, then update this file.
The 2026-10-06 device plan's proposals, the Ollama/Qwen worker notes, the router block and the 2026-10-08 Windows-update log were moved out on 2026-10-15:
`MyTradingSys/archive/devices_2026-10-15/DEVICES_2026-10-14_full.md` (the whole file as it was). Open questions: B137, B138.

## 0. Which machine am I on? (every session checks this first)

Check the HOSTNAME, never the username: the desktop and the laptop both run as `e-ngineers`, and the Claude app runs under three logins across them (CLOUD_ACCOUNTS.md).

| Hostname | Machine | PowerShell | Python |
|---|---|---|---|
| JIS-NB | Desktop (tower, the operator's main screen) | `$env:COMPUTERNAME` | `socket.gethostname()` |
| JIS-NUC | NUC (mostly headless, reached by Remote Desktop) | same | same |
| DESKTOP-F7IU69N | Laptop (travel + infrastructure; the name is misleading) | same | same |

Inside a Remote Desktop window the hostname is the REMOTE machine: a session started in an RDP window on the laptop that shows JIS-NB is a desktop session.
`F:\MTS` exists on both JIS-NB and JIS-NUC and they are different disks.

## 1. What lives where

| Device | Role | Runs |
|---|---|---|
| JIS-NB (192.168.29.188) | Operator workstation + live testnet system + repo source of truth | auto_trader, position_manager, daily_loss_monitor, live_runner_cli, orderflow_live, htf_context_live, 2 Maven feeds, scheduled checks, alert popups, Claude sessions |
| JIS-NUC (192.168.29.110) | Claude relay sessions + Codex lab + DSA bridge + backtests; no live loop (Qwen lane ended 2026-10-01); a candidate future home of the live loop (section 3) | Python 3.14.6; work tree `C:\Users\E-ngineers\IdeaProjects\mts-dsa`; data `F:\MTS\data`; jobs as one-shot scheduled tasks |
| DESKTOP-F7IU69N | Full working machine when travelling; infrastructure at home | Remote Desktop into JIS-NB and JIS-NUC; Claude app; own repo clone for reading and cloud work |

Datasets: the 1m klines (Dumps/backtest/raw_1m_2022, ~2.5M BTCUSDT bars, needed by run_cc_setups and the fabio/rsi runners) exist on JIS-NB and, since 2026-10-12, on JIS-NUC
(fetched from data.binance.vision by backtest/fetch_binance_archive.py, 2022-01..2026-10-11, 2,512,800 bars, 0 gaps; the first copy was deleted with its worktree by `tidy` 2026-10-12
and re-fetched to the PRIMARY tree `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest\raw_1m_2022\klines`, which tidy never touches; from another worktree pass it as --data-root / the klines_dir argument);
JIS-NUC otherwise has raw_1h / raw_1d / funding (B151). OI / long-short metrics are not fetched on the NUC.

Rule: the live testnet system moves between machines only in a restart window the operator chooses (section 3).

## 2. The operator's screen rule (2026-10-06)

The desktop is where the operator types, chats and trades. Nothing in the background may open, flash or take focus of a window on it. Alerts are the
exception: they appear and stay on screen until dismissed.
- Background processes (live loop, feeds, scheduled checks, Claude helper shells) run with no window: `pythonw.exe` or `Start-Process -WindowStyle Hidden`, output to log files
  under `Dumps\` (C: tree, see B138), visible via `mts status` / `mts watch`. Scheduled tasks run hidden ("Run whether user is logged on or not", or a hidden launcher), never a console window.
- `mts.ps1` `Open-Window` (mts.ps1:69-71) still starts guard, runner, orderflow, auto-trader and position managers each in a visible pwsh window; making them hidden is owned by the thread "Fix desktop Claude app and flashing shells".
- Alert popups stay in the operator's own sign-in session (the only session that can draw on his screen). Operator 2026-10-06: a second Windows account is fine if it helps, but he is never asked to switch profiles.

## 3. Where the live loop runs (operator decision 2026-10-06) - OWNER GUARD DECIDED, MOVE OPEN

The live loop moves to JIS-NUC IF performance does not degrade, and it must start by itself when the NUC is switched on. Until both conditions are proven it stays on JIS-NB, hidden (section 2).
The move itself is a restart window the operator chooses (B137 Q5); nothing moves from this document. Not yet proven: execution speed on the NUC (Deribit order round-trip, Binance feed delay,
bar-close-to-alert delay, same hour and code as the desktop); load (the NUC hit 98 C under continuous load, so backtests there are paused or capped to one worker while the loop is live, enforced in code);
unattended start (a startup task that does not depend on the lock screen, see section 7). Feeds, auto_trader, position managers, loss monitor and runners talk through local files, so they move as one set.
The loop can be started or stopped from the desktop, the laptop (RDP or the ssh gate) or the NUC, but it runs on exactly ONE machine at a time: two copies would place duplicate orders on the same testnet accounts.
DECIDED (OURS, card live-loop-one-owner-guard): `scripts/dev/live_owner.py` keeps one marker `live_owner.json` (host + utc heartbeat) in the directory named by env MTS_LIVE_OWNER_DIR (a share both hosts can read; default `runtime_data/` = single-host mode, so set it on BOTH hosts before the NUC is ever started). `mts start` and the loop-supervisor call `check` before any live process starts: a different host with a heartbeat younger than 180 s, an unreachable owner dir or an unreadable/corrupt marker refuses (fail closed); same host or a stale peer is allowed. The supervisor refreshes the heartbeat every 30 s tick. Not wired: a release on `mts stop` (the 180 s stale limit covers it). The NUC stays a cold standby; moving the loop is still a separate restart window.

## 4. Remote access

- At home: Windows Remote Desktop (mstsc) from the laptop to JIS-NB and JIS-NUC. The operator already uses RDP to the NUC. Desktop RDP host: NOT SET UP as of 2026-09-26; needs Windows Pro on JIS-NB (edition NOT CAPTURED: `winver`),
  a password on the signed-in account (the auto sign-in account has none) and Settings > System > Remote Desktop on.
- Away from home: do NOT forward port 3389 on the router. Tailscale (free tier, private network) was OK'd by the operator 2026-10-06 and is NOT set up yet; machine names/addresses are NOT CAPTURED until then.
- RDP into the desktop takes over the same signed-in session, so the loop and popups keep running. Always close with Disconnect (the X), never Sign out: signing out ends the session and every process started in it, including the live loop.
- Both machines must be left on for travel access; the operator switches them off/on by hand today (B137 Q8).

## 5. Code sync (operator 2026-10-07, replaces the desktop-only push rule)

GitHub jishusharma/mts `fast-track` is the hub. Any work tree on any machine (NUC, laptop, an App worktree on the desktop, cloud) ships with `scripts/dev/sync.py ship`; see system/PARALLEL.md.
Only the live tree on JIS-NB (marked `.mts_live`) never ships; it changes only by manual or coordinator-run deploy (DEPLOY_RUNBOOK.md; MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md).
Backtest data (F:\MTS\data on the NUC) is not in git; it is copied after new recordings, and parity is re-checked with `tom_bt_run.py rows` (section 7).

## 6. JIS-NB (desktop) - primary, source of truth for the repository

- Hardware: i7-4770K, 32 GB RAM; domain eng.e-ngineers.com. Windows account (interactive, own login): E-ngineers.
  Windows account (queue-only, no admin rights): mtsworker, hidden from the sign-in screen; password known to the operator, not written here.
- Repo root: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed (branch fast-track). LAN IPv4: 192.168.29.188.
- Share: \\JIS-NB\MTS-Queue -> Dumps\workers\NUC-QUEUE (C: tree), change access for mtsworker only. The old whole-repo share (MTS-Repo, Everyone/Full) was removed 2026-09-25.
  Read-only live mirror share MTS-Mirror (F:\MTS\Mirror): LIVE_MIRROR.md.
- Also on F: of this machine: F:\MTS\dsa (DSA worker), F:\MTS\Dumps (copy, B138), F:\AIBridge.
- Dumps (B138): C:\...\Dumps is canonical. F:\MTS\Dumps is a stale copy: do not write to it. Operator 2026-10-06: do the C: to F: move; script ready: scripts\dev\move_dumps_to_F.ps1
  (dry run by default, -Apply moves; renames the old folder, never deletes; the junction keeps the share path working). Held until the flashing fix is confirmed; never while a writer holds Dumps\workers\NUC-QUEUE.
- Claude vm_bundles (11.6 GB on C:): the Claude app's workspace image; left alone (the thread "Fix desktop Claude app and flashing shells" owns it). Revisit if C: runs short.
- Remote Desktop host: NOT SET UP (section 4).

## 7. JIS-NUC (NUC) - Claude relay, Codex lab, DSA bridge, backtests

- Role: no live loop. Work tree `C:\Users\E-ngineers\IdeaProjects\mts-dsa` (a worktree of the NUC's `...\IdeaProjects\BinanceDataFeed\.git`; `F:\MTS\repo` is NOT a git repo, DEPLOY_RUNBOOK.md NUC notes), data `F:\MTS\data`. Ships with `sync.py ship` like any work tree.
- Hardware: Intel NUC, i7-10710U, 32 GB RAM, Windows 10 Pro 22H2 (the operator set policy values 2026-10-08 to stay on 22H2; effect NOT VERIFIED; no ESU: accepted for a worker with no live path; undo = delete those four values, listed in the archived full file), CPU-only. LAN IPv4: 192.168.29.110.
- Python: 3.14.6, per-user, E-ngineers: %LOCALAPPDATA%\Programs\Python\Python314\python.exe (not on PATH of the gate's SSH session; call it by full path). Backtests need only the standard library plus tzdata.
  Disk 2026-10-06: C: 132 GB free, F: 200 GB free; 12 threads.
- Parity check 2026-10-06: `tom_bt_run.py rows` recomputed on the NUC and on the desktop into fresh work dirs; all 57 monthly rows.jsonl files byte-identical (sha256). Re-run `rows` before trusting the older F:\MTS\data\tom_bt cache (09-30).
- NUC-eligible jobs: any backtest that reads only committed code plus F:\MTS\data (tom_bt rows/fabio/report, bt/ ladder, layers/run_t055). Desktop-only: anything that reads live runtime state, Maven feeds or testnet.
- ssh gate (v3, key `~/.ssh/nuc_gate`): `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 status|logs N|sysinfo|models|disk-top|ps (script on stdin)|ps-bg <name>|job-log <name>`.
  The operator does NUC-side key and gate changes; never touch keys or `.secrets`.
- How to run a job by hand: SSH sessions have no share credentials, so wrap the job in a one-shot scheduled task for E-ngineers (principal LogonType Interactive; the auto sign-in session holds the share credential),
  write a transcript to F:\MTS\_in\*.log, poll it, delete the task after. Pattern: F:\MTS\_in\bt.ps1. Paths with backslashes get mangled in transit: build them with [char]92.
- Qwen lane ended 2026-10-01; both Ollama models were removed 2026-10-06 (Ollama stays installed). Leftovers: `C:\MTS-Worker\` and task MTS-NUC-Worker (unregistered 2026-10-17, SCHEDULING_POLICY.md); read items/T049_nuc_worker_v2.md before changing either.
- Stored credential: cmdkey entry for JIS-NB, user JIS-NB\mtsworker (fixed 2026-09-25). Automatic sign-in: ON (2026-09-26) but the operator reports (2026-10-06) a lock screen needing one click after power-on, so that line is NOT VERIFIED.
  Anything that must run unattended after power-on (the live loop, section 3) cannot assume a signed-in desktop; a startup task that runs whether or not a user is logged on needs a password on the account (the operator sets it once, never written here). Do not change this until the operator approves.
  BIOS power-on-after-power-failure is deliberately NOT set (operator switches both machines off/on manually).
- The desktop firewall blocks inbound HTTP from the NUC; use the MTS-Queue share. Remote Desktop: the operator already connects to it; account and settings NOT CAPTURED.

## 8. DESKTOP-F7IU69N (laptop) - travel and infrastructure

- Role (operator 2026-10-06): when travelling, everything is done from the laptop by Remote Desktop into JIS-NB and JIS-NUC (section 4). At home it is used for infrastructure work. It may start the live loop only under the one-owner rule (section 3), never as a second copy.
- Hardware: Lenovo 20L90025RT, i7-8550U, 32 GB RAM, 477 GB SSD (single drive C:), Windows 11 Pro 25H2, no GPU. Account e-ngineers. Tools: Java 21, Maven 3.9.11, Python 3.14.7, Git 2.24.1 (update before cloning).
- Repo copy: C:\Users\e-ngineers\IdeaProjects\BinanceDataFeed is on master (0cca386, tracks the removed share; stale): re-clone per section 5. LAN IPv4: NOT CAPTURED (`ipconfig | findstr /C:"IPv4"`).

## 9. Router and home network

Router model, firmware and admin address: NOT CAPTURED (admin address is usually the default gateway: `ipconfig | findstr /C:"Default Gateway"`). The router admin login stays with the operator; it is never written to this repo, a chat or a session record.
A cloud session cannot reach the router. DHCP reservations for the three machines and a copy of the router's device list are proposed (operator 2026-10-06: put the router under MTS), not done.

## 10. Open items

- mtsworker must NOT be a member of the local Administrators group on jis-nb. NOT VERIFIED as of 2026-10-06. Check: net localgroup Administrators
- B137 Q9: System Restore / shadow storage on desktop C: unverified (admin: vssadmin list shadowstorage).

## How to update this file
Run the ipconfig command on each machine and replace the matching NOT CAPTURED line. Add a new machine as its own section the moment it is connected. When the operator answers an open decision, replace it with the decision and date.
