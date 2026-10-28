# DEVICES

Reference for every machine this project runs on. Read by any session or
person working across the desktop, the NUC or the laptop before touching
network paths, shares, scheduled tasks or the live loop. No fabricated values:
an unconfirmed field says NOT CAPTURED instead of a guess; fill it from the
command shown, then update this file.

Device plan 2026-10-06 (operator requirements, thread "Plan what runs on each
device"). Lines marked PROPOSED are recommendations pending the operator's
answer; everything else is current fact. Open questions: B137, B138.

## 0. Which machine am I on? (every session checks this first)

Check the HOSTNAME, never the username: the desktop and the laptop both run as
`e-ngineers`, and the Claude app runs under two Google accounts on all three.

| Hostname | Machine | PowerShell | Python |
|---|---|---|---|
| JIS-NB | Desktop (tower, the operator's main screen) | `$env:COMPUTERNAME` | `socket.gethostname()` |
| JIS-NUC | NUC (mostly headless, reached by Remote Desktop) | same | same |
| DESKTOP-F7IU69N | Laptop (travel + infrastructure; the name is misleading) | same | same |

A session records the hostname in its session record. Inside a Remote Desktop
window the hostname is the REMOTE machine: a session started in an RDP window on
the laptop that shows JIS-NB is a desktop session. Note that `F:\MTS` exists on
both JIS-NB and JIS-NUC and they are different disks.

## 1. What lives where

| Device | Role | Runs |
|---|---|---|
| JIS-NB (192.168.29.188) | Operator workstation + live testnet system + repo source of truth | auto_trader, position_manager, daily_loss_monitor, live_runner_cli, orderflow_live, htf_context_live, 2 Maven feeds, scheduled checks, alert popups, Claude sessions |
| JIS-NUC (192.168.29.110) | Backtest and heavy-research worker (Qwen lane ended 2026-10-01); PROPOSED future home of the live loop (section 3) | Python 3.14.6, repo copy F:\MTS\repo, data F:\MTS\data; jobs as one-shot scheduled tasks |
| DESKTOP-F7IU69N | Full working machine when travelling; infrastructure at home | Remote Desktop into JIS-NB and JIS-NUC; Claude app; own repo clone for reading and cloud work |

Datasets: the 1m klines (Dumps/backtest/raw_1m_2022, ~2.5M BTCUSDT bars, needed by run_cc_setups and the fabio/rsi runners) exist on JIS-NB and, since 2026-10-12, on JIS-NUC (fetched from data.binance.vision by backtest/fetch_binance_archive.py, 2022-01..2026-10-11, 2,512,800 bars, 0 gaps; the first copy was deleted with its worktree by `tidy` 2026-10-12 and re-fetched 2026-10-12 to the PRIMARY tree C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest\raw_1m_2022\klines, which tidy never touches; from another worktree pass it as --data-root / the klines_dir argument); JIS-NUC otherwise has raw_1h / raw_1d / funding (B151). OI / long-short metrics are not fetched on the NUC.

Rule: the live testnet system moves between machines only in a supervisor restart window (section 3).

## 2. The operator's screen rule (2026-10-06)

The desktop is where the operator types, chats and trades. Nothing in the
background may open, flash or take focus of a window on it. Alerts are the
exception: they appear and stay on screen until dismissed.

- Background processes (live loop, feeds, scheduled checks, Claude helper
  shells) run with no window: `pythonw.exe` or `Start-Process -WindowStyle
  Hidden`, output to log files under `Dumps\` (C: tree, see B138), visible via
  `mts status` / `mts watch`. Scheduled tasks run hidden ("Run whether user is
  logged on or not", or a hidden launcher), never a console window.
- Today `mts.ps1` `Open-Window` (mts.ps1:69-71) starts guard, runner, orderflow,
  auto-trader and position managers each in a visible pwsh window. Making
  these hidden is owned by the thread "Fix desktop Claude app and flashing
  shells"; this file only records the rule.
- Alert popups stay in the operator's own sign-in session (that is the only
  session that can draw on his screen). Operator 2026-10-06: a second account
  is fine if it helps, but he is never asked to switch profiles (it would be a
  background-only identity nobody signs in to; none created yet). PROPOSED
  (B137-A): on JIS-NB no second Windows account for the loop. A loop under another account or in Session 0 could not
  show popups at all; it would need a separate alert viewer. Hidden launchers in
  the operator's own session give the same "nothing flashes" result with no
  new moving parts.

## 3. Where the live loop runs (operator decision 2026-10-06)

Decision: the live loop moves to JIS-NUC IF performance does not degrade, and
it must start by itself when the NUC is switched on. Until both conditions are
proven it stays on JIS-NB, hidden (section 2). The move itself is a
supervisor-owned restart window (B137 Q5); nothing moves from this document.

Conditions to prove before the move (PROPOSED test plan):
- Speed: orders go to Deribit testnet (execution/deribit_client.py
  TESTNET_BASE) and market data comes from Binance feeds. Measure on the NUC
  against the desktop, same hour, same code: Deribit order round-trip, Binance
  feed delay, and bar-close-to-alert delay. Execution speed is the network path
  to the exchanges, so the NUC passes if its numbers are no worse.
- Load: the NUC also runs backtests (B137 Q6). It hit 98 C under continuous
  load (LESSONS_LEARNED F). Backtests on the NUC are paused or capped to one
  worker while the loop is live, enforced in code, not in instructions.
- Whole loop together: feeds, auto_trader, position managers, loss monitor and
  runners talk through local files (state, heartbeats, HALT, journal), so they
  all move as one set and only alerts come back to the operator's screen.
- Unattended start: see the NUC login note in section 7. The loop must start
  from a startup task that does not depend on anyone clicking the lock screen.

Start from any device (operator requirement 2026-10-06): the loop can be
started or stopped from the desktop, the laptop (RDP or the ssh gate) or the
NUC itself, but it runs on exactly ONE machine at a time. Two copies would
place duplicate orders on the same testnet accounts. PROPOSED: the start verb
first checks a single owner marker (owner host + heartbeat time) and refuses
if another machine's heartbeat is fresh; an unreadable marker fails closed
(no start). The marker lives where both machines can read it; where is open.

## 4. Remote access (Tailscale OK'd by the operator 2026-10-06; not set up yet)

Tailscale = a free private network app. Installed on each machine and signed in
to one account, it gives every machine a stable name that works from anywhere,
encrypted, without opening any router port and without caring that the home
internet address changes. Setup: the operator signs in once per machine (browser
login); sessions then record each machine's Tailscale name and address in this file
(NOT CAPTURED until then). No gateway or port debugging is needed on his side.

- At home: Windows Remote Desktop (mstsc) from the laptop to JIS-NB and JIS-NUC.
  The operator already uses RDP to the NUC. Desktop RDP host: NOT SET UP as of
  2026-09-26; needs Windows Pro on JIS-NB (edition NOT CAPTURED: `winver`),
  a password on the signed-in account (the auto sign-in account has none) and
  Settings > System > Remote Desktop on.
- Away from home: do NOT forward port 3389 on the router. Use a private
  overlay network (Tailscale, free tier) on all three machines and RDP to the
  Tailscale name. Needs: operator installs it and signs in on each machine.
- RDP into the desktop takes over the same signed-in session, so the loop and
  popups keep running and appear in the RDP window. Always close with
  Disconnect (the X), never Sign out: signing out ends the session and every
  process started in it, including the live loop.
- Both machines must be left on for travel access; the operator switches them
  off/on by hand today (B137 Q8).

## 5. Code sync (operator 2026-10-07, replaces the desktop-only push rule)

GitHub jishusharma/mts `fast-track` is the hub. Any work tree on any machine (NUC, laptop, an App
worktree on the desktop, cloud) ships with `scripts/dev/sync.py ship`; see system/PARALLEL.md. Only the
live tree on JIS-NB (marked `.mts_live`) never ships; it changes only by the supervisor's deploy.
Backtest data (F:\MTS\data on the NUC) is not in git; it is copied after new recordings, and parity is
re-checked with `tom_bt_run.py rows` (section 7).

## 6. jis-nb (desktop) - primary, source of truth for the repository

- Role: repository lives here. Coordinator sessions run here (Cowork,
  linked via the desktop app's device bridge).
- Hardware: i7-4770K, 32 GB RAM; domain eng.e-ngineers.com.
- Windows account (interactive, own login): E-ngineers.
- Windows account (queue-only, no admin rights): mtsworker. Hidden from
  the sign-in screen. Password known to the operator; not written here.
- Repo root: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed (branch fast-track)
- Share: \\JIS-NB\MTS-Queue -> Dumps\workers\NUC-QUEUE (C: tree), change access for
  mtsworker only. The old whole-repo share (MTS-Repo, Everyone/Full) was
  removed 2026-09-25; ACL backup in backup_session\acl-before-worker-v2-*.txt.
- LAN IPv4: 192.168.29.188 (arp from the NUC, 2026-10-06).
- Also on F: of this machine: F:\MTS\dsa (DSA worker), F:\MTS\Dumps (copy, B138), F:\AIBridge.
- Dumps (B138): C:\...\Dumps is canonical. F:\MTS\Dumps is a stale copy: do not
  write to it. Operator 2026-10-06: do it. Script ready: scripts\dev\move_dumps_to_F.ps1
  (dry run by default, -Apply moves; renames the old folder, never deletes; the junction
  keeps the share path working, so no repoint). Held until the flashing fix is confirmed.
  Original proposal: finish the C: to F: swap (junction plus share repoint) in
  the same supervisor restart window as any working-tree move, never while a
  writer holds Dumps\workers\NUC-QUEUE.
- Claude vm_bundles (11.6 GB on C:): the Claude app's workspace image. Operator 2026-10-06:
  does not need it. Left alone for now because the Claude app's own workspace may depend
  on it; the thread "Fix desktop Claude app and flashing shells" owns that. PROPOSED
  (B137 Q10): keep; deleting it only forces a re-download. Revisit if C: runs short.
- Remote Desktop host: NOT SET UP (section 4).

## 7. JIS-NUC (NUC) - backtest and research worker

- Role (2026-10-06): backtests and heavy research. Holds a COPY of the repo
  (F:\MTS\repo, from git archive HEAD, tracked files only, no secrets) and the
  backtest data (F:\MTS\data); the desktop repo stays canonical. Results are
  copied back by hand until section 5 is decided.
- Hardware: Intel NUC, i7-10710U, 32 GB RAM, Windows 10 Pro, CPU-only.
- Python: 3.14.6, per-user, E-ngineers: %LOCALAPPDATA%\Programs\Python\Python314\python.exe
  (not on PATH of the gate's SSH session; call it by full path). Backtests need only the
  standard library. Disk 2026-10-06: C: 132 GB free, F: 200 GB free; 12 threads.
- Parity check 2026-10-06: `tom_bt_run.py rows` (HEAD e9bd822) recomputed on the NUC and on the
  desktop into fresh work dirs; all 57 monthly rows.jsonl files are byte-identical (sha256). Desktop
  took 142 s on 1 worker. The older F:\MTS\data\tom_bt cache (09-30) differs because the verdict
  code changed since; re-run `rows` before trusting that cache.
- NUC-eligible jobs (PROPOSED, B137 Q6): any backtest that reads only committed
  code plus F:\MTS\data (tom_bt rows/fabio/report, bt/ ladder, layers/run_t055).
  Desktop-only: anything that reads live runtime state, Maven feeds or testnet.
- How to run a job: SSH sessions have no share credentials, so wrap the job in a
  one-shot scheduled task for E-ngineers (principal LogonType Interactive; the
  auto sign-in session holds the share credential), write a transcript to
  F:\MTS\_in\*.log, poll it, delete the task after. Pattern: F:\MTS\_in\bt.ps1.
  Paths with backslashes get mangled in transit: build them with [char]92.
- Ollama: 0.34.4 and ~38 GB of models in F:\ollama (qwen3.6:35b, qwen3-coder:30b),
  idle since the Qwen lane was decommissioned 2026-10-01. DELETED 2026-10-06 on the
  operator's word (ollama rm of both models over the ssh gate; checked afterwards on JIS-NUC by hostname, ollama list empty; Ollama itself stays
  installed; free space on F: after is NOT CAPTURED). Original proposal (B137 Q7):
  delete the models; F: has room so this is housekeeping, and they can be
  re-pulled if a local model is ever wanted again.
- Old Qwen worker files: C:\MTS-Worker\ (nuc-worker.ps1, nuc-launcher.ps1, logs\,
  outbox\); scheduled task MTS-NUC-Worker (at sign-in). See
  MyTradingSys/items/T049_nuc_worker_v2.md before changing either.
- Stored credential: cmdkey entry for JIS-NB, user JIS-NB\mtsworker (fixed
  2026-09-25; a stale entry for the desktop's own account caused Access
  denied until corrected - see T049 doc).
- Automatic sign-in: ON (set 2026-09-26). BIOS power-on-after-power-failure:
  deliberately NOT set (operator switches both machines off/on manually;
  see T049 doc "operator requirement 2026-09-25").
- LAN IPv4: 192.168.29.110 (arp, 2026-10-06). The desktop firewall blocks
  inbound HTTP from the NUC; use the MTS-Queue share.
- Remote Desktop: the operator already connects to it (2026-10-06); account and
  settings NOT CAPTURED.
- Start-up behaviour (operator, 2026-10-06): after power-on the NUC does not go
  straight to the desktop; it shows the login/unlock screen and the operator
  must click once (no password needed) before the desktop appears. This
  conflicts with "Automatic sign-in: ON" above, so that line is NOT VERIFIED.
  Anything that must run unattended after power-on (the live loop, section 3)
  cannot assume a signed-in desktop. PROPOSED: a scheduled task with trigger
  "At startup", run whether or not a user is logged on, with stored
  credentials, hidden; plus fixing auto sign-in so the click is not needed.
  A startup task that runs whether or not a user is logged on needs a password on
  the account (Windows refuses it for blank-password accounts); the operator sets it
  once, and it is never written here. Do not change any of this until the operator approves.

## 8. DESKTOP-F7IU69N (laptop) - travel and infrastructure

- Role (operator 2026-10-06): when travelling, everything is done from the
  laptop, by Remote Desktop into JIS-NB and JIS-NUC (section 4). At home it is
  used for infrastructure work. The live loop runs on one machine (section 3);
  the laptop controls it through the RDP window or the ssh gate, and may start
  it only under the one-owner rule (section 3), never as a second copy.
- Hardware: Lenovo 20L90025RT, i7-8550U, 32 GB RAM, 477 GB SSD (single drive C:),
  Windows 11 Pro 25H2, no GPU. Account e-ngineers.
- Tools: Java 21, Maven 3.9.11, Python 3.14.7, Git 2.24.1 (update before cloning).
- Repo copy: C:\Users\e-ngineers\IdeaProjects\BinanceDataFeed on master
  (0cca386, tracks the removed share; stale). Re-clone per section 5.
- Folder layout for MTS and CBP: owned by the thread "Laptop folder cleanup and setup".
- LAN IPv4: NOT CAPTURED. Run on the laptop: ipconfig | findstr /C:"IPv4"

## 9. Router and home network (operator 2026-10-06: put the router under MTS)

- Router model, firmware and admin address: NOT CAPTURED. The admin address is
  usually the default gateway: on any machine run  ipconfig | findstr /C:"Default Gateway"
- The router admin login stays with the operator. It is never written to this repo,
  a chat or a session record. A cloud session cannot reach the router; changes are
  made by the operator at the router page (or in a session he is watching) and
  logged here with the date.
- PROPOSED: DHCP reservations for JIS-NB (192.168.29.188), JIS-NUC (192.168.29.110)
  and DESKTOP-F7IU69N so their addresses never change; no port forwarding (remote
  access is Tailscale, section 4); keep a copy of the router's device list here.
- To capture: model, admin address, DHCP range, current reservations, any existing
  port forwards (to be removed), Wi-Fi/guest settings, firmware date.

## 10. Open items

- mtsworker must NOT be a member of the local Administrators group on jis-nb.
  NOT VERIFIED as of 2026-10-06. Check: net localgroup Administrators
- B137 Q9: System Restore / shadow storage on desktop C: unverified (admin:
  vssadmin list shadowstorage).
- B137 Q2 (third-device "NUC project" session): the third device is the laptop
  (it joined this project 2026-10-06 06:02Z); proposed to close.

## How to update this file

Run the ipconfig command on each machine and replace the matching
NOT CAPTURED line. Add a new machine as its own section in the same
format the moment it's connected, even before you know its final role.
When the operator answers a PROPOSED line, replace it with the decision and date.

- Status 2026-10-08 (operator-reported, NUC UNBLOCKED): the Windows 11 25H2 upgrade failed on
  Windows Update (0x80242016, then 0x8007001F) after a component-store corruption (KB5066791 had
  failed 2026-09-26 with 0x80073712). Operator ran `DISM /Online /Cleanup-Image /RestoreHealth`
  (ok) and `sfc /scannow` (corrupt files repaired). Decision: stay on Windows 10 22H2. Operator
  set policy values under HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate:
  TargetReleaseVersion=1, ProductVersion="Windows 10", TargetReleaseVersionInfo="22H2", and
  AU\NoAutoRebootWithLoggedOnUsers=1 (stops the 25H2 offer and surprise restarts). Windows 10 is
  out of support (no ESU): NO-SECURITY-PATCHES risk accepted for a worker with no live path.
  New HDMI cable: Acer ACR06F8 detected, 1920x1080. Not verified: that the policy took effect
  after `gpupdate`/restart, and that KB5066791 now installs. Undo = delete those four values.
