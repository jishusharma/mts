# LIVE HOST MOVE: live testnet loop JIS-NB -> DESKTOP-F7IU69N (staged 2026-10-21, NOT CUT OVER)

Operator 2026-10-21: the live testnet loop moves from JIS-NB (desktop) to DESKTOP-F7IU69N (Lenovo laptop, two batteries, lid close on AC = do nothing, already set).
JIS-NUC (new APC BX600C-IN UPS) becomes the 24/7 backtest and data host. JIS-NB stays the operator's screen and stops hosting the loop.
This file is the plan; nothing in it has run. Builders never deploy, start or stop live processes, touch HALT files or open trades: the cutover (section 4) is ONE owner's
manual restart window, run by the operator or a coordinator the operator names for it. DEVICES.md sections 3/6/7/8 and DEPLOY_RUNBOOK.md point here.

Why the laptop and not the NUC (the 2026-10-06 candidate): the laptop has its own two-battery UPS, no thermal history (the NUC hit 98 C under backtest load, DEVICES s3),
and taking the loop off the NUC lets the NUC run backtests flat out with no "one worker while live" cap. Trade-offs: Wi-Fi only today, a 4-core i7-8550U, one C: drive (no F:).

## 1. Facts captured on DESKTOP-F7IU69N, 2026-10-20 21:34Z = 2026-10-21 03:04 IST (read-only commands)
| Item | Value | Command |
|---|---|---|
| Hostname | DESKTOP-F7IU69N | `$env:COMPUTERNAME` |
| LAN IPv4 | 192.168.29.157 (DHCP, not reserved) | `ipconfig` |
| Active network | Wi-Fi only (Intel AC 8265, 144 Mbps link); no Ethernet adapter up | `Get-NetAdapter` |
| Batteries | 2 | `Get-CimInstance Win32_Battery` |
| Power plan | Balanced | `powercfg /getactivescheme` |
| Windows Update active hours | 22:00-16:00 (local) | HKLM `...\WindowsUpdate\UX\Settings` |
| Last boot | 2026-10-18 18:08 local | `Win32_OperatingSystem.LastBootUpTime` |
| Public API round-trip, Wi-Fi, new TLS connection per call, n=15 each | Binance spot `/api/v3/time` median 205 ms (min 179); Binance futures `/fapi/v1/time` 201 ms (min 176); Deribit testnet `public/get_time` 323 ms (min 303) | probe in section 3 item 9 |
Not captured here: the same probe from JIS-NB (needed for the comparison), charge thresholds, Energy saver state, logged-off startup.

## 2. Roles after the move
| Host | Role | Holds |
|---|---|---|
| DESKTOP-F7IU69N | live testnet loop (feeds, auto_trader, position managers, daily_loss_monitor, live_runner_cli, orderflow_live, htf_context_live, loop-supervisor) + live tree `.mts_live` | runtime state, local only (section 5) |
| JIS-NUC | 24/7 backtests, data recording/refresh, Codex lab, DSA bridge, relay sessions; never the live loop | `F:\MTS\data` (canonical backtest data), owner-marker share, live mirror share |
| JIS-NB | operator screen, Claude sessions, work trees; cold standby for the loop (same one-owner rule) | its old live tree, kept read-only as the rollback copy for 14 days |

## 3. Laptop 24/7 readiness checklist (operator does the settings; a session only reads and records them)
Tick each with the date in DEVICES.md section 8. All must be ticked before section 4 runs.
1. Charge threshold 60-80 % on BOTH batteries: Lenovo Vantage > Power > Battery Charge Threshold, custom start 60 % / stop 80 %, applied to each battery. Check: Vantage shows it; the battery stays at <= 80 % after a night on AC. (OURS: long life at constant AC; the UPS reserve is 60 % of two packs.)
2. Energy saver off: Settings > System > Power & battery > Energy saver = never automatically (both "on battery" thresholds off), so a power cut does not throttle the CPU while the loop runs on battery.
3. Power mode on AC: Best performance; Screen off on AC 5 min is fine; Sleep on AC = Never; Hibernate on AC = Never (`powercfg /change standby-timeout-ac 0`, `powercfg /change hibernate-timeout-ac 0`). Lid close on AC = Do nothing (already set: verify `powercfg /q SCHEME_CURRENT SUB_BUTTONS LIDACTION`). Lid close on battery: Do nothing too, or a power cut with the lid shut sleeps the loop.
4. USB / Wi-Fi power saving off: Device Manager > network adapter > Power Management: untick "Allow the computer to turn off this device"; same for the Ethernet adapter once fitted.
5. Windows Update restarts: active hours 22:00-16:00 already cover 18 h; set Settings > Windows Update > Advanced > "Get me up to date" OFF and "Notify me when a restart is required" ON; pause updates for 1 week around the cutover. Restarts happen only in a window the operator chooses (the loop is restarted by hand after, item 7). Never let Update restart it unannounced: that is a silent loop stop.
6. Ethernet: plug the laptop into the router by cable (USB-C/USB 3 gigabit dongle if it has no RJ45) and re-run the probe (item 9). Wi-Fi stays as the fallback. DHCP reservation for the laptop on the router (DEVICES s9) so the LAN address does not move.
7. Logged-off startup: SCHEDULING_POLICY.md allows no standing scheduled task, and `loop-supervisor` / `mts start` today run in the signed-in session. Default (no operator answer needed): no auto-start; after any reboot the owner signs in and runs `mts start` (section 4 step 9), and the coordinator checks `mts status` on every wake. An unattended start after a power cut or Update restart needs an operator exception to SCHEDULING_POLICY (decision `q-live-autostart`, default NO) plus a password on the account and a "run whether user is logged on or not" task; it is not staged here. Auto sign-in alone is not enough (the NUC showed a lock screen after power-on, DEVICES s7).
8. Alert popups: `show-alert.ps1` draws on the signed-in session of the host that runs the loop, i.e. the laptop, not the operator's desktop screen. Before cutover decide where alerts surface (default: keep popups on the laptop and read alerts on JIS-NB through `live_mirror.py brief`; a desktop popup relay is a separate card).
9. Latency vs JIS-NB: run the probe below on JIS-NB and on the laptop (cable, then Wi-Fi) inside the same 15 minutes, plus `mts status` bar-close-to-alert delay over one hour on each host if both are logged in. Pass (OURS): laptop median <= JIS-NB median + 20 ms and min <= JIS-NB min + 20 ms for each endpoint. Fail = stay on JIS-NB, record the numbers here.
   ```python
   # save as a scratch file (not in the repo); public endpoints only
   import time, urllib.request, statistics, socket
   U = {"binance_time": "https://api.binance.com/api/v3/time", "binance_fapi_time": "https://fapi.binance.com/fapi/v1/time",
        "deribit_test_get_time": "https://test.deribit.com/api/v2/public/get_time"}
   print(socket.gethostname())
   for k, u in U.items():
       xs = []
       for _ in range(15):
           t = time.perf_counter(); urllib.request.urlopen(u, timeout=10).read(); xs.append((time.perf_counter() - t) * 1000); time.sleep(0.3)
       xs.sort(); print(k, "median %.0f ms" % statistics.median(xs), "min %.0f" % xs[0])
   ```
10. Tools: Java 21 + Maven 3.9.11 (feeds), Python 3.14.7, Git updated to 2.40+ (LENOVO_SETUP.md step 1), `gh` installed and logged in (missing on this machine 2026-10-21: STATUS cannot read CI). `mvn -q compile` passes in the live tree.
11. Disk: C: free >= 100 GB (`Get-PSDrive C`); runtime logs rotate (RETENTION_POLICY.md) because there is no F: drive.
12. Testnet keys: the operator places the testnet key files in the laptop live tree the same way as on JIS-NB. Sessions never read, copy or move them.

## 4. One-owner cutover checklist (one person runs every step, in order, in one restart window)
Owner: the operator, or the coordinator the operator names for this window. Window: flat book preferred (no open testnet position); if a position is open, position_manager keeps running on JIS-NB until it closes (step 6). Write each step's time in SUPERVISOR_LOG.
1. Preconditions: section 3 all ticked; CI green on the target SHA (`origin/green/fast-track`); the code prerequisites in section 6 are on that SHA.
2. Shared owner dir: `MTS_LIVE_OWNER_DIR` set as a user env var on BOTH JIS-NB and the laptop to the NUC share folder (section 5), and on JIS-NB the loop restarted once so its supervisor writes the marker there. Check on each: `python scripts/dev/live_owner.py check` prints the JIS-NB owner from both hosts. Without this the guard is single-host and cannot stop two copies.
3. Laptop live tree: fresh clone `C:\MTS\mts-live` (not the stale master clone), `git checkout --detach <green SHA>`, then create `.mts_live`; copy nothing from git-ignored folders yet. `python scripts/dev/run_all_tests.py --quick` in it: green.
4. Stop new entries on JIS-NB: create the AUTO_PAUSE flag (log owner + expected end in SUPERVISOR_LOG); wait for the current bar to close.
5. Stop the JIS-NB loop: `mts stop` (feeds, runner, auto_trader, daily_loss_monitor, orderflow_live, htf_context_live, loop-supervisor). Wait 180 s (live_owner STALE_SEC) or run `live_owner.py release` on JIS-NB. `mts status` on JIS-NB: not running.
6. Open position: leave its position_manager running on JIS-NB until flat; the laptop starts no position_manager for that id. Note it in SUPERVISOR_LOG.
7. Copy runtime state JIS-NB -> laptop (section 5 "state that moves"), sha256-checked: `robocopy` over the admin share or a USB stick, then compare hashes. Rename JIS-NB's `.mts_live` to `.mts_live.retired-<date>` so no tool treats it as live.
8. Laptop: `python scripts/dev/live_owner.py check` = allowed (stale or released peer).
9. Laptop: `mts start`; `mts status` = running (loop, watchdog, data feed); `live_owner.py check` from JIS-NB now REFUSES (laptop owns).
10. Watch one hour: snapshots fresh, one alert cycle, orderflow `_state.json` advancing with no gap (B152), `check_live_health.py` not RED, Deribit testnet order path answers (no new order needed: the auto_trader's own health line).
11. Clear AUTO_PAUSE (log it). Publish the mirror from the laptop to the new root (section 5); `live_mirror.py brief` on JIS-NB and the NUC shows `mirror@<utc>` < 15 min.
12. Record: DEVICES.md sections 1/3/6/8 and SCHEDULING_POLICY section 5 table updated to "cut over <date>", NEXT_SESSION block replaced, ship.
Rollback (any step 9-10 fails): `mts stop` on the laptop, wait 180 s, rename the laptop `.mts_live` away, rename JIS-NB's back, copy the runtime state back (step 7 reversed), `mts start` on JIS-NB. The JIS-NB tree is kept unchanged for 14 days for this.

## 5. Data plan
- Code: git only. The laptop live tree follows `origin/green/fast-track` by manual or coordinator-run deploy (DEPLOY_RUNBOOK.md); it never ships.
- Runtime state: local on the laptop live tree, never on a share, never in git (repo is public). State that moves at cutover: `runtime_data/` (snapshots, live_runner.log, last_alert.json, live_owner.json if single-host, deploy_backup), `MyTradingSys/runtime/` (orderflow_live `_state.json` + series, oi_live csv, alerts jsonl, sched/*.json, pm_heartbeats, daily-loss state), `MyTradingSys/execution/auto_trades.jsonl` and trader state/plans/journal, `MyTradingSys/research/htf_context/*`, `runtime_data/observations`. The allowlist in `live_mirror.py` is the reference list; anything it names must arrive.
- Backtest data: canonical on the NUC `F:\MTS\data`. Share it READ-ONLY as `\\JIS-NUC\MTS-Data` (Read for the laptop and JIS-NB accounts only; the NUC is the only writer). The live loop reads no backtest data today (only `test_live_levels_confluence.py` names `F:/MTS/data/tom_raw`, a test); a live reader that needs it must take a path from env, never hard-code `F:`.
- Owner marker: `\\JIS-NUC\MTS-Live` (folder `F:\MTS\live_owner`), CHANGE access for the laptop and JIS-NB accounts only, holding `live_owner.json`. On the UPS host, so the marker survives a desktop power-off. Unreachable share = refuse to start (fail closed, by design).
- Live mirror: publish moves to the laptop; root `\\JIS-NUC\MTS-Mirror` (folder `F:\MTS\Mirror` on the NUC; the laptop needs CHANGE there, readers Read). Readers set `MTS_MIRROR_ROOT`; the code default is still `\\JIS-NB\MTS-Mirror` (section 6).
- Backups: `backup_snapshot.py` pushes to remote `backup` = `F:/MTS_backup.git` on JIS-NB; the laptop has no F:. Default: point the laptop live tree's `backup` remote at a bare repo on the NUC share (`\\JIS-NUC\MTS-Backup\MTS_backup.git`), never origin.

## 6. Code prerequisites found while staging (cards, not built here; each needs its own tests; live-path ones need restart/error tests)
| File:line | Ties to JIS-NB | Change |
|---|---|---|
| `scripts/dev/live_mirror.py:32-33,105` | `DEFAULT_ROOT = \\JIS-NB\MTS-Mirror`, local-folder shortcut only when hostname == JIS-NB | root from env/config per host; local shortcut for whichever host holds `.mts_live` |
| `mts.ps1:348` | auto-trader started with an absolute Python path under `C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64` | resolve Python like the other launch lines, or fail closed with a clear message if the path is missing |
| `scripts/dev/backup_snapshot.py:10` | remote `backup` = F:/MTS_backup.git on JIS-NB | doc + per-host remote check only (section 5) |
| `scripts/dev/supervisor.py:513` | NB/NUC host constants for budget and lanes | add the laptop as a live host in the lane rules (no live-tree work from builders) |
| `scripts/dev/auto_deploy.py:4` | docstring says the live tree is JIS-NB | text only (script is retired; manual fallback reads `.mts_live`) |
Grep before the cutover: `grep -rn "JIS-NB" scripts MyTradingSys --include=*.py --include=*.ps1` (41 files on 2026-10-21; most are docs, tests or lane names, not live-path).

## 7. Power and network
- NUC on the APC BX600C-IN (600 VA / 360 W line-interactive). Set up the PowerChute/USB link so the NUC shuts down cleanly on low battery; runtime at NUC load NOT CAPTURED (read it from the UPS display at normal load). BIOS power-on-after-power-failure on the NUC stays the operator's choice (DEVICES s7: NOT set today).
- Laptop: its two batteries are its UPS; at 60-80 % thresholds expect less runtime than full charge: measure once (unplug AC with the loop running, note minutes to 20 %; stop the test there).
- Router and ONT: without power the laptop on battery still loses the internet. Put the router and the fibre ONT on a DC mini-UPS (12 V / 9 V outputs matching their adapters, check the adapter labels; 10,000 mAh class gives a few hours) or on the BX600C-IN if the cables reach (it then shares the NUC's runtime). Until one is fitted, a power cut = feed and order path down even though the laptop stays up; the loop must treat that as API errors (fail closed: no new entries while the exchange is unreachable).

## 8. Open decisions (defaults apply until the operator answers)
- `q-live-autostart`: unattended start after reboot as an exception to SCHEDULING_POLICY. Default NO (manual `mts start`).
- Alert surface (section 3 item 8). Default: popups on the laptop, read on JIS-NB via the mirror.
- Cutover window date. Default: none set; the move does not happen until the operator names it.
</content>
</invoke>
