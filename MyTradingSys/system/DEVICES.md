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
| JIS-NB (192.168.29.188) | Operator workstation + live testnet system (until the cutover in LIVE_HOST_MOVE.md, then cold standby) + repo source of truth | auto_trader, position_manager, daily_loss_monitor, live_runner_cli, orderflow_live, htf_context_live, 2 Maven feeds, scheduled checks, alert popups, Claude sessions |
| JIS-NUC (192.168.29.110) | 24/7 backtest and data host on the APC BX600C-IN UPS (2026-10-21) + Claude relay sessions + Codex lab + DSA bridge; never the live loop (Qwen lane ended 2026-10-01) | Python 3.14.6; work tree `C:\Users\E-ngineers\IdeaProjects\mts-dsa`; data `F:\MTS\data`; jobs as one-shot scheduled tasks |
| DESKTOP-F7IU69N (192.168.29.157, DHCP) | Next live testnet host (operator 2026-10-21, staged, NOT cut over: LIVE_HOST_MOVE.md); full working machine when travelling | Remote Desktop into JIS-NB and JIS-NUC; Claude app; own repo clone for reading and cloud work |

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

## 3. Where the live loop runs - TARGET DESKTOP-F7IU69N (operator 2026-10-21), STAGED, still on JIS-NB

Operator 2026-10-21 replaces the 2026-10-06 NUC plan: the live loop moves to DESKTOP-F7IU69N (laptop, two batteries = its own UPS, lid close on AC = do nothing);
JIS-NUC becomes the 24/7 backtest/data host and never runs the loop. Until the cutover runs, the loop stays on JIS-NB, hidden (section 2). Plan, readiness checklist,
one-owner cutover checklist, data plan and code prerequisites: LIVE_HOST_MOVE.md. The move is a restart window the operator chooses (B137 Q5); nothing moves from this document.
Not yet proven on the laptop: latency vs JIS-NB (same-hour probe, LIVE_HOST_MOVE s3 item 9; laptop Wi-Fi baseline 2026-10-20 21:34Z: Binance ~200 ms, Deribit testnet ~320 ms median per new HTTPS call);
Ethernet; unattended start after a reboot (not allowed by SCHEDULING_POLICY; default manual `mts start`, decision q-live-autostart). Feeds, auto_trader, position managers, loss monitor and runners talk through local files, so they move as one set.
The loop can be started or stopped from the desktop, the laptop (RDP or the ssh gate) or the NUC, but it runs on exactly ONE machine at a time: two copies would place duplicate orders on the same testnet accounts.
DECIDED (OURS, card live-loop-one-owner-guard): `scripts/dev/live_owner.py` keeps one marker `live_owner.json` (host + utc heartbeat) in the directory named by env MTS_LIVE_OWNER_DIR (a share both hosts can read; default `runtime_data/` = single-host mode, so set it on BOTH hosts before the laptop is ever started; target `\\JIS-NUC\MTS-Live`, LIVE_HOST_MOVE s5). `mts start` and the loop-supervisor call `check` before any live process starts: a different host with a heartbeat younger than 180 s, an unreachable owner dir or an unreadable/corrupt marker refuses (fail closed); same host or a stale peer is allowed. The supervisor refreshes the heartbeat every 30 s tick. Not wired: a release on `mts stop` (the 180 s stale limit covers it). After the cutover JIS-NB is the cold standby (its tree kept 14 days for rollback); the NUC is never a standby.

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

- Live loop: runs here until the cutover in LIVE_HOST_MOVE.md section 4; after it this tree's `.mts_live` is renamed `.mts_live.retired-<date>`, the tree is kept unchanged 14 days as the rollback copy, and JIS-NB is the operator screen + cold standby only (one-owner rule, section 3).

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
- After the cutover the mirror share and the backup bare repo (F:\MTS\Mirror, F:\MTS_backup.git) move to the NUC (LIVE_HOST_MOVE s5); until then they stay here.

## 7. JIS-NUC (NUC) - 24/7 backtest and data host, Claude relay, Codex lab, DSA bridge

- Role (operator 2026-10-21): 24/7 backtests and data, never the live loop (so no one-worker cap once the loop runs on the laptop). On an APC BX600C-IN UPS (2026-10-21; USB shutdown link and runtime at NUC load NOT CAPTURED). Planned shares (LIVE_HOST_MOVE s5, NOT CREATED): `MTS-Data` = F:\MTS\data READ-only for the laptop and JIS-NB accounts (NUC sole writer); `MTS-Live` = F:\MTS\live_owner CHANGE for the laptop and JIS-NB (one-owner marker); `MTS-Mirror` = F:\MTS\Mirror (laptop CHANGE, readers Read); `MTS-Backup` bare repo for the laptop live tree.
- Earlier role text: no live loop. Work tree `C:\Users\E-ngineers\IdeaProjects\mts-dsa` (a worktree of the NUC's `...\IdeaProjects\BinanceDataFeed\.git`; `F:\MTS\repo` is NOT a git repo, DEPLOY_RUNBOOK.md NUC notes), data `F:\MTS\data`. Ships with `sync.py ship` like any work tree.
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

## 8. DESKTOP-F7IU69N (laptop) - next live testnet host (staged), travel

- Role (operator 2026-10-21): the live testnet loop moves here (LIVE_HOST_MOVE.md); STAGED, NOT CUT OVER. Until the cutover it must not run the loop; after it, it is the only host that does (section 3).
  When travelling the laptop leaves home with the operator, and the loop with it: a trip needs a cutover back to JIS-NB first or the loop running on the road (decide per trip; default: cut back to JIS-NB).
- 24/7 readiness (LIVE_HOST_MOVE s3; tick with date). Captured 2026-10-20 21:34Z: 2 batteries; power plan Balanced; Wi-Fi only (Intel AC 8265), built-in Ethernet I219-V not connected, LTE modem without SIM; Windows Update active hours 22:00-16:00; lid close AC = do nothing, battery = SLEEP; Energy saver at 50 %; sleep on battery 30 min.
  `scripts/dev/laptop_live_ready.ps1` (dry run by default; elevated `-Apply`) sets the scriptable items.
  Done 2026-10-21 (operator ran `laptop_live_ready.ps1 -Apply`, verified by dry run): sleep/hibernate never on AC and battery [x]; lid close do nothing on AC and battery [x]; Energy saver off (threshold 0) [x]; Wi-Fi adapter max performance on battery [x]; Update NoAutoRebootWithLoggedOnUsers + restart notifications [x]; Git 2.55.0 [x]; gh 2.102.0 installed [x]; NIC "allow turn off" Disabled on Wi-Fi and Ethernet (re-run `-Apply -SkipTools`, dry run read back Disabled) [x]; `gh auth login` (jishusharma) [x].
  Open: charge threshold 60-80 % both batteries [ ]; power mode Best performance [ ]; Update pause around cutover [ ]; Ethernet + DHCP reservation [ ]; logged-off start (default manual) [ ]; latency vs JIS-NB [ ]; testnet keys placed by the operator [ ].
- Earlier role (operator 2026-10-06): when travelling, everything is done from the laptop by Remote Desktop into JIS-NB and JIS-NUC (section 4). At home it is used for infrastructure work.
- Hardware: Lenovo 20L90025RT, i7-8550U, 32 GB RAM, 477 GB SSD (single drive C:), Windows 11 Pro 25H2, no GPU. Account e-ngineers. Tools: Java 21, Maven 3.9.11, Python 3.14.7, Git 2.24.1 (update before cloning).
- Repo copy: C:\Users\e-ngineers\IdeaProjects\BinanceDataFeed is on master (0cca386, tracks the removed share; stale): re-clone per section 5; the live tree will be a fresh clone `C:\MTS\mts-live` (LIVE_HOST_MOVE s4 step 3). LAN IPv4: 192.168.29.157 (Wi-Fi, DHCP, 2026-10-20; reserve it on the router). No F: drive: runtime state stays on C:, backtest data is read from the NUC share.
- Git author email: `e-ngineers@DESKTOP-F7IU69N` (traffic.py attribution; card tc6-lenovo-git-email).

## 8b. Worktree maintenance, every device (operator 2026-10-21; the one allowed standing task, SCHEDULING_POLICY.md s4)

One script, identical on JIS-NB, JIS-NUC and the Lenovo laptop (DESKTOP-F7IU69N): `scripts/dev/wt_maint.py`. Daily 07:15 local, headless (`conhost --headless`), task `MTS-WorktreeMaint-<device>`, device read from the hostname, paths from the checkout.
Each run: fetch; retire finished worktrees (sync.py tidy's rules incl. hand-named trees; ignored data first moved to the primary tree's `Dumps/wt_rescue/`); `git worktree prune`; delete local branches fully merged into origin/fast-track; write trees holding unshipped/uncommitted work to `Dumps/worktree_report.txt` (gitignored) and one line to the SUPERVISOR_LOG.
Never touched: primary, live tree (`.mts_live`), lane trees, Codex trees, any tree changed in the last 30 min or idle under 24 h, any tree with uncommitted files or commits not on origin/fast-track. No stash/reset/force-push; a second run changes nothing.

```
python scripts/dev/wt_maint.py install      # once per device, from the primary checkout (after pulling origin/fast-track)
python scripts/dev/wt_maint.py status       # device, task state, last run, last report
python scripts/dev/wt_maint.py              # dry run (default); --apply does it by hand
python scripts/dev/wt_maint.py uninstall
```

Operator line for the Lenovo session: `You are Builder. Install the worktree maintenance job on this device: pull origin/fast-track, run python scripts/dev/wt_maint.py install, run python scripts/dev/wt_maint.py status, ship.`

## 9. Router and home network

Router model, firmware and admin address: NOT CAPTURED (admin address is usually the default gateway: `ipconfig | findstr /C:"Default Gateway"`). The router admin login stays with the operator; it is never written to this repo, a chat or a session record.
A cloud session cannot reach the router. DHCP reservations for the three machines and a copy of the router's device list are proposed (operator 2026-10-06: put the router under MTS), not done.
Power: the router and the fibre ONT have no backup power; with the loop on the laptop a power cut keeps the laptop up but drops the internet. Fit a DC mini-UPS (outputs matching the adapter labels) or put both on the NUC's BX600C-IN (LIVE_HOST_MOVE s7). NOT DONE.

## 10. Open items

- mtsworker must NOT be a member of the local Administrators group on jis-nb. NOT VERIFIED as of 2026-10-06. Check: net localgroup Administrators
- B137 Q9: System Restore / shadow storage on desktop C: unverified (admin: vssadmin list shadowstorage).

## How to update this file
Run the ipconfig command on each machine and replace the matching NOT CAPTURED line. Add a new machine as its own section the moment it is connected. When the operator answers an open decision, replace it with the decision and date.
