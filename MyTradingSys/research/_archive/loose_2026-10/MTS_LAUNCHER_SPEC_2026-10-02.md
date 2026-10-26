# MTS LAUNCHER SPEC: `mts runner` and `mts orphans` verbs plus status lines for live_runner_cli and orphan_watchdog_cli
Session: MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int / sonnet-01 (WAVE 1 item 3). SPEC ONLY: no .ps1 was edited, no process was started, nothing under execution/ or layers/alerts/ was touched.
Method: static read of committed files at HEAD 9695b36 (Linux clone; no pwsh on this machine, so nothing below was parse-checked or run). "unknown" = not decidable from the files.
Origin: TWO_CORES_READINESS_2026-10-01.md W1 rows 2 and 5 (lines 9, 12), fix 4 (line 58); WIRING_MAINTENANCE_AUDIT_2026-10-01.md:72 (F4, "small, mts.ps1, desktop builder").

## 0. Path correction
The brief (and CLOUD_PROMPT_TWO_CORES_INTEGRATION_2026-10-02.md:56-57, "Do not edit scripts/mts.ps1") name `scripts/mts.ps1`. That path does not exist: `ls scripts/` shows Build-Check.ps1, Dump_All.ps1, core, dev, live, load.ps1, manager, monitor, operator, qwen_decommission*.py, start-session.ps1, tools, update_prompt.py, worker. The launcher is **`mts.ps1` at the repo root** (git-tracked; read by scripts/dev/check_guide.py:53, `REPO / "mts.ps1"`; MTS_USER_GUIDE.md section 8 last line: `.\mts.ps1 <command>`). All citations below use the root path.

## 1. How the existing launcher launches and reports (mts.ps1)
| Piece | Where | What it does |
|---|---|---|
| Entry | mts.ps1:10-13, :94 | `param($Verb, $Arg)`, one `switch ($Verb.ToLower())`; unknown verb prints help, exit 2 (:268) |
| Verb table | mts.ps1:23-47 (`# VERBS-BEGIN` / `# VERBS-END`) | rows `@("Group", "verb", "text")`; source of truth for `mts help` (:96-104) and for check_guide.py:28-29 |
| Output helpers | mts.ps1:49-52 | `Ok` -> `"  OK    text"` green; `Warn` -> `"  WARN  text"` yellow; `Bad` -> `"  STOP  text"` red; informational lines are written by hand as `"  --    text"` (:142, :146) |
| Python call | mts.ps1:55-56 | `$env:PYTHONUNBUFFERED = "1"`; `function Py { & python @args }`; output goes to the console, verbs end `exit $LASTEXITCODE` (e.g. :158, :199, :251) |
| Own window | mts.ps1:66-69 | `Open-Window title command` = `Start-Process pwsh.exe -NoExit -NoProfile -Command "... Set-Location '$Root'; $command"` (cwd = repo root) |
| Process detection | mts.ps1:71-74 | `Get-Procs pattern [wql-name-filter]` = `Get-CimInstance Win32_Process -Filter <names>` then `Where CommandLine -match pattern`; callers use `.Count` |
| File age | mts.ps1:76-79 | `Age path` = whole seconds since LastWriteTime, `$null` if missing |
| `guard` verb | mts.ps1:237-241 | `Get-Procs "daily_loss_monitor" "Name='python.exe'"` -> if found `Ok "... already running"; break`; else `Open-Window "MTS daily-loss guard" "python '$Exec\daily_loss_monitor.py'"`, then `Ok "... started in its own window - leave it open"` |
| `auto` verb | mts.ps1:243-248 | same pattern with `Get-Procs "auto_trader" "Name='python.exe'"`; shows brakes first; window command `python -m MyTradingSys.execution.auto_trader` |
| `status` verb | mts.ps1:113-148 | cyan section headers "Market loop" (:115), "Brakes" (:139), "Trades" (:143); guard line :141-142 (`Get-Procs "daily_loss_monitor" "Name='python.exe' OR Name='pythonw.exe'"`, `Ok "daily-loss guard running"` else `Say "  --    daily-loss guard not running (optional: mts guard)"`); state_code freshness :122-128 (`Age`, WARN above 150 s) |
Observations (not changed here): `mts status` has no line for the auto-trader (no "auto_trader" in :113-148); no existing verb stops `guard` or `auto` (the only stop verb is `mts stop` = market loop, :111).

## 2. The two targets (real CLIs)
### 2.1 live_runner_cli (MyTradingSys/backtest/layers/alerts/live_runner_cli.py)
- Must run as a module from the repo root: `python -m MyTradingSys.backtest.layers.alerts.live_runner_cli --poll-seconds 60` (fast_track_2026-09-27/NEXT_SESSION_PLAN.md:16-18: "`python .../live_runner_cli.py` fails with ModuleNotFoundError").
- Alert-only: "no orders, no execution imports, no keys, no mainnet (public market-data endpoint only)" (live_runner_cli.py:3-6). Fetches Binance public klines (default_fetch_klines, :79).
- argparse (main at :241; args :245-252): `--symbol` default BTCUSDT; `--tfs` default `"1h,15m,5m,1m"` (:247); `--state-path` default `MyTradingSys/runtime/live_alert_state.json` (:248, cwd-relative); `--alerts-dir` default `MyTradingSys/runtime/alerts` (:249, cwd-relative); `--limit` int default 100; `--poll-seconds` int default 60; `--once` flag (one poll then exit 0, :284-286).
- Per poll (loop_body :259-282): writes `<alerts-dir>/<tf>.jsonl` for tfs that produced alerts (:272-273), saves the state file every poll (`save_state`, :275), prints one flushed line (:278) of the form `poll <UTC yyyy-MM-ddTHH:mm:ssZ> alerts=<n> errors=<n> <layer|sub|tf>=<count> ...` (format_poll_line :227-238), prints each fetch/layer error as JSON on stderr (:281-282). Loop sleeps `--poll-seconds` (:291); Ctrl+C prints "stopped", exit 0 (:292-294).
- Console/hidden logging today: hand-started hidden with logs `Dumps/alerts/runner_logs/live_runner_2026-09-29.{out,err}` (NEXT_SESSION_PLAN.md:17, :159). Log name format is not uniform (`auto_trader_20260929_1955.{out,err}`, SUPERVISOR_LOG.md:182): no convention is established.
### 2.2 orphan_watchdog_cli (MyTradingSys/execution/orphan_watchdog_cli.py)
- Run-once testnet check, "NOT scheduled" (orphan_watchdog_cli.py:1; orphan_watchdog.py:6; MAINNET_READINESS_CHECKLIST.md:74). It is a script, not a module entry: it does `sys.path.insert(0, HERE)` and imports its siblings (:13-16), so `python MyTradingSys\execution\orphan_watchdog_cli.py` works like the other execution scripts that `Py` runs.
- argparse (:57-60): `--once` (store_true, default True, i.e. always true), `--interval` float default 0.0 (0 = single pass; >0 repeats every N seconds and stops on exit code 3, :86-94), `--currency` default `BTC`. `--mainnet` is deliberately not defined (:62: argparse rejects it, exit 2).
- Exit codes (docstring :1, expression :82): 0 ok, 1 account read errors, 3 orphan HALT written; 2 = argparse error.
- Side effects: authenticates per account label through `deribit_orders.authenticate()` with `MTS_ACCOUNT` set per label (:36-50; labels = "default" + the values of `accounts` in auto_trader_config.json, :24-33); read-only towards the exchange (orphan_watchdog.py:2-4); **appends a line to MyTradingSys/execution/HALT when an orphan is found** (orphan_watchdog.py:49-61, :83-84; HALT_PATH :20); appends one JSON row per run to `MyTradingSys/execution/orphan_watchdog.jsonl` (LOG_PATH :21; row `{ts, event: "ok"|"orphan_halt", orphans: [{account, position, open_orders}], errors: {label: repr}, live: [labels]}`, orphan_watchdog.py:86-97; `ts` is `datetime.now(timezone.utc).isoformat()`, :66, :88). Heartbeat input: `MyTradingSys/execution/pm_heartbeats/` (pm_heartbeat.py:20).
- Known precedent for a false HALT: first live run 2026-09-29 read the wrong heartbeat folder and wrote a false HALT (fixed a9629e8; MAINNET_READINESS_CHECKLIST.md:74).
- Printed output: only when something is wrong (`Orphan accounts found: ...` :79, `Errors occurred: N` :81); a clean run prints nothing.

## 3. Proposed verbs (add to the verb table, mts.ps1:24-46)
```
@("Auto",   "runner",  "Start the alert runner (indicator layers) in its own window"),
@("Safety", "orphans", "Check every testnet account for a position no manager owns (may set HALT)"),
```
Names match check_guide's regex `@\("[^"]+",\s*"([a-z-]+)"` (check_guide.py:29).
### 3.1 `mts runner` (modelled on `auto`, mts.ps1:243-248)
1. If a process matches the anchored pattern (section 5) -> `Ok "alert runner already running"; break`. Never kills, never restarts.
2. `Open-Window "MTS alert runner" "python -m MyTradingSys.backtest.layers.alerts.live_runner_cli --poll-seconds 60"` (Open-Window already sets the cwd to `$Root`, mts.ps1:67, which the cwd-relative defaults :248-249 need).
3. `Ok "alert runner started in its own window - it only writes alerts (no orders); leave it open"`.
No brake check: the runner cannot trade (section 2.1); the auto-trader applies HALT itself. No `$Arg` use in v1 (adding 3m/4h/1d to `--tfs` also needs registry entries; out of scope, see TWO_CORES_FIX_PASS_2026-10-02.md item 2).
Optional log variant (not required for v1): append `2>&1 | Tee-Object -Append -FilePath 'Dumps\alerts\runner_logs\live_runner_<yyyy-MM-dd>.out'` so status can read the last `poll ...` line (section 4, variant B). Dumps/ is gitignored except BUILD_REPORT.md (.gitignore), so the folder must be created at start.
### 3.2 `mts orphans` (modelled on `plan`/`account`: `Py script; exit $LASTEXITCODE`)
```
Py (Join-Path $Exec "orphan_watchdog_cli.py")        # no args: --once, --interval 0, --currency BTC
switch ($LASTEXITCODE) {
  0 { Ok   "no orphan accounts" }
  1 { Warn "some accounts could not be read (not counted as orphans) - see MyTradingSys\execution\orphan_watchdog.jsonl" }
  3 { Bad  "ORPHAN found - HALT written. Check: mts account. When it is flat or owned again: mts resume" }
  default { Bad "orphan watchdog failed (exit $LASTEXITCODE)" }
}
exit $LASTEXITCODE
```
(illustrative; exit-code meanings from orphan_watchdog_cli.py:1, :82). v1 is run-once only. A looping mode (`--interval N`, stops itself on exit 3) is an operator/supervisor decision because the tool is "NOT scheduled" and wrote a false HALT once (section 2.2): unknown / not specified here.

## 4. Status lines (new block at the end of the `status` verb, after "Trades", mts.ps1:143-147)
Header: `Say ""; Say "Layers and watchdogs" Cyan`. Line text (prefix by the existing helpers, so columns match mts.ps1:49-52):

Alert runner (liveness = process + age of the state file the runner rewrites every poll, live_runner_cli.py:275):
| Case | Exact line |
|---|---|
| process found, state age <= LIMIT | `  OK    alert runner running (pid 7920), state updated 34s ago` |
| process found, state age > LIMIT | `  WARN  alert runner running (pid 7920) but state updated 412s ago - STALE (limit 180s)` |
| process found, state file missing | `  --    alert runner running (pid 7920), waiting for its first poll` |
| no process, state file fresh | `  WARN  alert runner: no process found but state updated 40s ago - started elsewhere, or its command line is not visible` |
| no process | `  WARN  alert runner not running - start it with: mts runner` |
LIMIT = 180 s = 3 x the default poll (live_runner_cli.py:251). **NO-SOURCE**: a proposal mirroring the 150 s rule at mts.ps1:127; one constant at the top of the block, operator may change it. WARN (not `--`) for "not running" because the auto-trader's layer signals depend on the runner; whether Tom-only operation should show `--` instead is an operator policy: unknown.

Orphan watchdog (run-once tool: no process to find; read the last row of `MyTradingSys\execution\orphan_watchdog.jsonl`, parse `ts` with `[datetimeoffset]::Parse` like mts.ps1:166, `Get-Content -Encoding UTF8`, wrapped in try/catch):
| Case | Exact line |
|---|---|
| no log or empty | `  --    orphan watchdog never run - run it with: mts orphans` |
| last row `ok`, no errors | `  OK    orphan watchdog last run 12 min ago: no orphans (live managers: jishu_2)` (empty `live` -> `(no live managers)`) |
| last row `ok`, `errors` non-empty | `  WARN  orphan watchdog last run 2 h ago: 1 account(s) unreadable (not counted as orphans)` |
| last row `orphan_halt` and `MyTradingSys\execution\HALT` exists | `  STOP  orphan watchdog last run 3 min ago: ORPHAN jishu_2 position=0.5 open_orders=0 - HALT is set; mts account, then mts resume` |
| last row `orphan_halt`, HALT no longer exists | `  WARN  orphan watchdog last run 3 min ago found an orphan (HALT since cleared) - re-check with: mts orphans` |
| unreadable last line | `  WARN  orphan watchdog log unreadable: MyTradingSys\execution\orphan_watchdog.jsonl` |
Age is always printed; **no staleness threshold** is proposed, because the tool is not scheduled (NO-SOURCE for any N); a threshold belongs to whoever schedules it.
Variant B (richer runner line, needs the optional log in 3.1): add `, last poll 34s ago, alerts=0 errors=0` from the newest `poll ...` line (format at live_runner_cli.py:238); WARN when `errors` > 0. Variant A (above) has a blind spot: when every kline fetch fails (network down) the loop still saves the state file (:275), so the line stays OK. Choice A vs B: operator/supervisor: unknown.

## 5. Process detection (copied from the existing pattern, with anchors)
- Runner: `Get-Procs '-m\s+MyTradingSys\.backtest\.layers\.alerts\.live_runner_cli(\s|$)' "Name='python.exe' OR Name='pythonw.exe'"` (names as in the guard check, mts.ps1:141). The only valid launch form is the module form (section 2.1), so anchoring on `-m <module>` avoids matching `python -m pytest ...test_live_runner_cli.py`, which a bare `live_runner_cli` pattern (the style of mts.ps1:244) would match.
- Orphan watchdog: not needed in v1 (run-once). If a looping mode is ever used: `Get-Procs '(^|[\\/\s])orphan_watchdog_cli\.py' "Name='python.exe'"`.
- Read-only: status touches only the state file mtime, one jsonl file and the HALT file's existence; it reads nothing under `.secrets/` and no key file.
- Unknown: whether the desktop python is a venv launcher that shows two processes with one command line (the existing verbs only test `.Count` for truthiness; so should these).

## 6. Paths used
| What | Path (relative to repo root) | Source |
|---|---|---|
| runner state (heartbeat) | `MyTradingSys\runtime\live_alert_state.json` | live_runner_cli.py:248, :275 |
| runner alert files | `MyTradingSys\runtime\alerts\<tf>.jsonl` | live_runner_cli.py:249, :273 |
| runner console / optional log | window; optional `Dumps\alerts\runner_logs\live_runner_<yyyy-MM-dd>.out` | NEXT_SESSION_PLAN.md:17; naming is a proposal |
| orphan log | `MyTradingSys\execution\orphan_watchdog.jsonl` | orphan_watchdog_cli.py:21 |
| HALT | `MyTradingSys\execution\HALT` (mts.ps1:19) | orphan_watchdog_cli.py:20 |

## 7. Restart-safety
- Builders never launch, stop or restart the runner or the watchdog and never touch HALT (CLAUDE.md Hard rules): neither verb is run by a builder; `mts orphans` would write HALT on a real orphan and `mts runner` starts a live process. Only the operator or the supervisor runs them, after the fix is committed and gated.
- `mts runner` is idempotent and contains no `Stop-Process`/`Remove-Item`/`Move-Item`: it cannot restart anything. A runner restart after promoting a registry or layer change is supervisor-owned (CLOUD_PROMPT_TWO_CORES_INTEGRATION_2026-10-02.md step 5; SUPERVISOR_LOG.md:172 "Live runner restarted (old pids killed)"), so v1 has no `restart` or `stop` verb (consistent with `guard`/`auto`).
- `mts orphans` never clears HALT; clearing stays with `mts resume` (mts.ps1:208-219, typed word). Status never removes or writes HALT.
- It never calls mode.ps1 (section 11).

## 8. Failure modes
| # | Failure | Effect | Where it shows |
|---|---|---|---|
| 1 | `pwsh`/`python` not on PATH | the new window errors; like `auto`/`guard` the verb still prints OK | next `mts status`: "alert runner not running" |
| 2 | runner started from another cwd | relative state/alerts paths (live_runner_cli.py:248-249) point elsewhere | status: process found but state STALE or missing |
| 3 | network down | per-tf fetch errors go to stderr, loop continues, state still saved | variant A: still OK (blind spot); variant B: errors > 0 |
| 4 | duplicate runner (Get-CimInstance returns no CommandLine for elevated or other-user processes, so the check misses it) | two writers on one state file and one alerts dir; effect on duplicate auto-trades: unknown | not detected in v1 |
| 5 | orphan CLI false HALT (precedent 2026-09-29, a9629e8) | HALT written, all trading stops | STOP line; operator uses `mts account` then `mts resume` |
| 6 | account label has no key file | that account is a logged read error, not an orphan (orphan_watchdog.py:76-78, :39-40); exit 1 | WARN "unreadable" line |
| 7 | HALT cleared by `mts resume` but the last log row still says `orphan_halt` | permanent STOP would be a false alarm | handled by the HALT-exists test in the table (section 4) |
| 8 | last log line half-written or not JSON | status must not crash | try/catch, WARN "log unreadable" |
| 9 | CIM query cost: one more `Get-CimInstance` per `status` call | slower status; size unknown | optional: reuse one python.exe query for guard, manager and runner |

## 9. Guide and COMMANDS.md sync (what scripts/dev/check_guide.py enforces)
check_guide.py reads only `mts.ps1` and `MTS_USER_GUIDE.md` (:53-54); it does **not** read COMMANDS.md. Checks: (1) every table verb is in the guide's "All commands" section as `` `mts <verb>` `` and no extra verb is listed (:33-38); (2) every backticked path with a backslash in "Where things are" has an existing folder (file paths: their parent folder) (:40-45); (3) a `Last reviewed: YYYY-MM-DD` line exists (:47).
Required for Step 3c to keep passing on the verb check:
1. MTS_USER_GUIDE.md `## 8. All commands` (line 225): add rows `` | `mts runner` | Start the alert runner (indicator layers) in its own window | `` and `` | `mts orphans` | Check every testnet account for a position no manager owns (may set HALT) | ``.
2. MTS_USER_GUIDE.md line 3: move `Last reviewed:` to the commit date (guide rule "Keeping this guide current", line 278 ff.).
Not enforced but should change in the same commit (guide's own rule): section 3 sample `mts status` output (lines 55-83) gets the two new lines; section 4 "Auto-trading" (from line 160) gets one sentence that layer signals need `mts runner`; section 6 table (line 198) gets a row for an orphan HALT.
"Where things are": add rows only for folders that exist in git. `` `MyTradingSys\execution\orphan_watchdog.jsonl` `` and `` `MyTradingSys\runtime\live_alert_state.json` `` pass (their parent folders exist); `MyTradingSys\runtime\alerts\` and `Dumps\alerts\runner_logs\` would FAIL check (2) in a fresh clone (neither folder exists here).
COMMANDS.md (which says it keeps "older AI-session shortcuts", line 3): no change is required by check_guide; an optional pointer under "START THE SESSION" is a judgement call.
Baseline: Step 3c already FAILS in this clone with three "Where things are" paths absent (execution\plans\, \journal\, \halt_history\; parent baseline run; reproduced with `python scripts/dev/check_guide.py`). So Step 3c cannot prove the sync here: acceptance must look for the absence of any `FAIL: guide 'All commands'` line.
`mts help` is generated from the verb table (mts.ps1:96-104): no separate edit.

## 10. Tests needed
No test harness for mts.ps1 exists (it is not imported by any test; scripts/dev/test_check_guide.py only feeds fixture strings). A PowerShell test precedent exists, run by hand: `pwsh scripts/operator/test_inbox_poller.ps1` (scripts/operator/README.md:32; not in run_all_tests).
1. **Static launcher test** (gate-friendly, new `scripts/dev/test_mts_launcher.py`, unittest, wired as a run_all_tests step next to 3r): reads mts.ps1 as text and asserts (a) `runner` and `orphans` are in the verb table (reuse check_guide's regex); (b) both have a `switch` branch; (c) the runner branch contains the module command exactly as in NEXT_SESSION_PLAN.md:16 (`-m MyTradingSys.backtest.layers.alerts.live_runner_cli`) and no `.py` file path form; (d) neither new branch contains `Stop-Process`, `Remove-Item` or `Move-Item`; (e) the orphans branch maps exit codes 0, 1, 3 (orphan_watchdog_cli.py:1); (f) the status block contains the two line stems `alert runner` and `orphan watchdog`. Fails first on the current mts.ps1 (verbs absent).
2. **Line-format test.** The decision logic in section 4 is not unit-testable while it lives inside the PowerShell switch (mts.ps1 executes on load, so it cannot be dot-sourced). Option P (recommended for testability): a pure Python helper (for example `scripts/dev/status_lines.py`: `runner_line(proc_count, pid, state_age_s)`, `orphan_line(last_row, halt_exists, age_s)`) returning the exact text of section 4, called from mts.ps1 with facts it gathered, and a unit test with one case per table row. Option S (pure PowerShell, matches the existing status block): no unit test, only the manual acceptance below. Choice P vs S: supervisor: unknown.
3. Manual, on the desktop (the only place it can run): `.\mts.ps1 status` before and after `.\mts.ps1 runner`, and after `.\mts.ps1 orphans`; the orphan case with a stub log row instead of a live orphan (never provoke a real orphan).
4. PowerShell parse check: `pwsh -NoProfile -Command "[void][System.Management.Automation.Language.Parser]::ParseFile('mts.ps1',[ref]$null,[ref]$e); $e"` on the desktop; unverifiable on this surface (no pwsh).

## 11. Relationship to scripts/core/mode.ps1
`scripts/core/mode.ps1` exists (git-tracked). `.\scripts\core\mode.ps1 -M armed` (COMMANDS.md:18; CLOUD_PROMPT_TWO_CORES_INTEGRATION_2026-10-02.md:150 "sanctioned launcher") starts the **market loop** only: params `-M prep|armed|live` (:3-4); it kills any previous loop (lock-PID descendants and orphan `start-trading-day`/`datafeed.Main`/`statemachine`/mvn processes, :65-86), then launches the supervisor (loop-supervisor.ps1, :100-120) and the wrapper (start-trading-day.ps1, :128-148) through the scheduled tasks `MTS-Supervisor` and `MTS-Wrapper`. `mts start` reaches it through `mts-up` only when both are dead (scripts/load.ps1:42). It does not start live_runner_cli, auto_trader, daily_loss_monitor or orphan_watchdog_cli (none is referenced in the file). So the runbook's "sanctioned launcher" covers the Tom market loop; the runner and the watchdog have none, which is the gap this spec fills.
Consequences: (a) the new verbs stay independent of mode.ps1 and never call it (rules: "Never run mode.ps1 twice in a row. It kills and restarts", COMMANDS.md hard rules / DSA_SESSION_PROMPT.md:226; "never call mode.ps1 ... with the call operator", methodology/live_session_protocol.md:181); (b) mode.ps1 hard-codes `$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"` (:17) while mts.ps1 uses `$PSScriptRoot` (:16): the new verbs follow mts.ps1; (c) the market loop's `status` check pattern `start-trading-day|mode\.ps1` (mts.ps1:116) is unaffected.

## 12. Acceptance check (one line)
"`.\mts.ps1 status` prints a line starting `alert runner` and a line starting `orphan watchdog`" (both preceded by one of `OK`/`WARN`/`STOP`/`--`), with `python scripts/dev/check_guide.py` showing no `FAIL: guide 'All commands'` line and the static test of section 10.1 passing.

## 13. Unknown (not decidable from the files)
- Whether the runner is currently scheduled or started by hand on the desktop; the two scheduled tasks' state (WIRING_MAINTENANCE_AUDIT_2026-10-01.md:77).
- The actual log file convention for the runner (two different date formats exist).
- Operator policy: WARN vs `--` for a stopped runner; runner variant A vs B; whether the watchdog gets a looping or scheduled mode and with what staleness limit; Option P vs S for testing.
- Whether the desktop python shows one or two processes per runner; whether duplicate runners double-trade.
- Whether `mts status` should also show the auto-trader (it does not today).
