# mts.ps1 - the one command for running MTS by hand. See MTS_USER_GUIDE.md.
#
#   mts <verb> [argument]        e.g.  mts status   mts plan   mts trade L-mkt-0928-1430
#
# Every verb wraps an existing script; no trading logic lives here.
# Exchange verbs talk to Deribit TESTNET only (the Python layer hard-codes it).
# The verb table below is the source of truth for "mts help" and for
# scripts/dev/check_guide.py, which fails if the guide misses a verb.

param(
    [Parameter(Position = 0)][string]$Verb = "help",
    [Parameter(Position = 1)][string]$Arg = "",
    [string]$Id = "",
    [switch]$Dry
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Exec = Join-Path $Root "MyTradingSys\execution"
$Plans = Join-Path $Exec "plans"
$Halt = Join-Path $Exec "HALT"
$HaltLoss = Join-Path $Exec "HALT_DAILY_LOSS"
$Guide = Join-Path $Root "MTS_USER_GUIDE.md"

# VERBS-BEGIN  (group | verb | what it does)
$Verbs = @(
    @("Market loop", "start",   "Start the market loop and its watchdog"),
    @("Market loop", "stop",    "Stop the market loop cleanly"),
    @("Market loop", "status",  "One screen: loop, market state, last alert, brakes"),
    @("Market loop", "market",  "Market guide: MA / RSI / candle state + recent layer alerts, with backtest verdict tags (context only)"),
    @("Market loop", "watch",   "Live dashboard (Ctrl+C to leave)"),
    @("Trading",     "plan",    "Build a trade plan by answering questions"),
    @("Trading",     "plans",   "List saved plans"),
    @("Trading",     "check",   "Show the exact orders a plan would place (sends nothing)"),
    @("Trading",     "trade",   "Place a plan on testnet, then open its manager window"),
    @("Trading",     "manage",  "Re-open the manager window for a live plan"),
    @("Trading",     "account", "Testnet balance, positions, open orders (read-only)"),
    @("Safety",      "pause",   "Block all new trades (creates the HALT file)"),
    @("Safety",      "resume",  "Remove the brakes after you have checked the account"),
    @("Safety",      "kill",    "EMERGENCY: cancel every order, close every position, pause"),
    @("Safety",      "kill-mainnet", "EMERGENCY on MAINNET: cancel every order, close every position, pause"),
    @("Safety",      "guard",   "Start the daily-loss guard in its own window"),
    @("Safety",      "orphans", "Check every testnet account for a position no manager owns (may set HALT)"),
    @("Auto",        "auto",    "Start the testnet auto-trader (Tom + layer signals) in its own window"),
    @("Auto",        "runner",  "Start the alert runner (indicator layers) in its own window (only the runner; mts guard starts it too, with the loss monitor and orderflow)"),
    @("Auto",        "autolog", "Last 20 auto-trader decisions (trades, skips, rejects)"),
    @("Auto",        "ledger",  "Closed auto-trades per source: count, win rate, mean and total net P/L"),
    @("Upkeep",      "missed",  "Missed-trade analysis: chart-observed setups vs what MTS did (mts missed [horizon hours])"),
    @("Upkeep",      "soak",    "Testnet soak report from the execution journal (read-only)"),
    @("Upkeep",      "wiring",  "Check that every code file is run by something or declared (the gate runs this too)"),
    @("Upkeep",      "desk",    "Open desktop-reach tasks other sessions wait on (post/take/done: scripts/dev/desk.py)"),
    @("Upkeep",      "go",      "Launch the next queued build task in claude (mts go [slug] [-Id B074] [-Dry])"),
    @("Upkeep",      "test",    "Run the offline test suite (no exchange)"),
    @("Upkeep",      "guide",   "Open the user guide"),
    @("Upkeep",      "help",    "This list")
)
# VERBS-END

function Say([string]$text, [string]$color = "Gray") { Write-Host $text -ForegroundColor $color }
function Ok([string]$text)   { Say "  OK    $text" Green }
function Warn([string]$text) { Say "  WARN  $text" Yellow }
function Bad([string]$text)  { Say "  STOP  $text" Red }

# Python output goes straight to the console (never captured); read $LASTEXITCODE after.
$env:PYTHONUNBUFFERED = "1"
function Py { & python @args }

function Resolve-Plan([string]$name) {
    if (-not $name) { Bad "name a plan, e.g.  mts $Verb L-mkt-0928-1430   (see: mts plans)"; exit 1 }
    foreach ($p in @($name, (Join-Path $Plans $name), (Join-Path $Plans "$name.json"))) {
        if (Test-Path $p -PathType Leaf) { return (Resolve-Path $p).Path }
    }
    Bad "no plan called '$name'  (see: mts plans)"; exit 1
}

function Open-Window([string]$title, [string]$command) {
    $cmd = "`$Host.UI.RawUI.WindowTitle = '$title'; Set-Location '$Root'; $command"
    Start-Process pwsh.exe -ArgumentList @("-NoExit", "-NoProfile", "-Command", $cmd)
}

function Get-Procs([string]$pattern, [string]$names = "Name='pwsh.exe' OR Name='powershell.exe'") {
    @(Get-CimInstance Win32_Process -Filter $names -ErrorAction SilentlyContinue |
      Where-Object { $_.CommandLine -match $pattern })
}

function Age([string]$path) {
    if (-not (Test-Path $path)) { return $null }
    [int]((Get-Date) - (Get-Item $path).LastWriteTime).TotalSeconds
}

function Show-Brakes {
    if (Test-Path $Halt)     { Bad "HALT is set - no new trades. Reason: $((Get-Content $Halt -Raw).Trim())" }
    if (Test-Path $HaltLoss) { Bad "HALT_DAILY_LOSS is set - daily loss limit hit: $((Get-Content $HaltLoss -Raw).Trim())" }
    if (-not (Test-Path $Halt) -and -not (Test-Path $HaltLoss)) { Ok "no brakes set - trading allowed" }
}

function Confirm-Word([string]$word, [string]$question) {
    Say $question Yellow
    $typed = Read-Host "  Type $word to continue (anything else cancels)"
    if ($typed -cne $word) { Say "  cancelled"; return $false }
    return $true
}

switch ($Verb.ToLower()) {

    "help" {
        Say "MTS - type  mts <verb>  (full guide: mts guide)" White
        $group = ""
        foreach ($v in $Verbs) {
            if ($v[0] -ne $group) { $group = $v[0]; Say ""; Say $group Cyan }
            Say ("  mts {0,-13} {1}" -f $v[1], $v[2])
        }
        Say ""
    }

    "start" {
        Py (Join-Path $Root "scripts\dev\live_owner.py") check
        if ($LASTEXITCODE -ne 0) { Bad "live loop owned by another host or owner marker unreadable - not starting (DEVICES.md section 3)"; return }
        $null = . (Join-Path $Root "scripts\load.ps1")
        mts-up
    }

    "market" {
        # Read-only observation digest; also writes MyTradingSys/runtime/market_guide.md
        Py (Join-Path $Root "scripts\dev\market_guide.py")
        Py (Join-Path $Root "scripts\dev\market_guide.py") "--stdout"
    }

    "stop" { & (Join-Path $Root "scripts\core\stop-day.ps1") }

    "status" {
        Say "MTS STATUS   $((Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm')) UTC" White
        Say ""; Say "Market loop" Cyan
        $wrap = Get-Procs "start-trading-day|mode\.ps1"
        $sup  = Get-Procs "loop-supervisor"
        $java = Get-Procs "datafeed\.Main" "Name='java.exe'"
        if ($wrap.Count -and $sup.Count -and $java.Count) { Ok "running (loop, watchdog, data feed)" }
        elseif (-not ($wrap.Count + $sup.Count + $java.Count)) { Warn "not running - start it with: mts start" }
        else { Warn "partly running (loop=$($wrap.Count) watchdog=$($sup.Count) feed=$($java.Count)) - run: mts start" }
        $sc = Join-Path $Root "MyTradingSys\runtime\state_code.json"
        $a = Age $sc
        if ($null -ne $a) {
            $s = Get-Content $sc -Raw | ConvertFrom-Json
            $line = "market state $($s.state)  (bull $($s.bullish_count) / bear $($s.bearish_count))  updated ${a}s ago"
            if ($a -gt 150) { Warn "$line - STALE" } else { Ok $line }
        }
        $log = Join-Path $Root "runtime_data\apparatus_log.txt"
        if (Test-Path $log) {
            $last = Get-Content $log -Tail 30 -Encoding UTF8 | Where-Object { ($_ -split ' \| ').Count -ge 6 } | Select-Object -Last 1
            if ($last) { $f = $last -split ' \| '; Say "  last verdict: $($f[4])   setup: $($f[5])   price $($f[2])" }
        }
        $alert = Join-Path $Root "runtime_data\last_alert.json"
        if (Test-Path $alert) {
            $j = Get-Content $alert -Raw | ConvertFrom-Json
            Say "  last alert:   $($j.title)  ($([int]((Age $alert)/60)) min ago)"
        }
        Say ""; Say "Brakes" Cyan
        Show-Brakes
        $guard = Get-Procs "daily_loss_monitor" "Name='python.exe' OR Name='pythonw.exe'"
        if ($guard.Count) { Ok "daily-loss guard running" } else { Say "  --    daily-loss guard not running (optional: mts guard)" }
        Say ""; Say "Trades" Cyan
        $mgr = Get-Procs "position_manager" "Name='python.exe'"
        if ($mgr.Count) { foreach ($m in $mgr) { Ok "manager running: $(($m.CommandLine -split '\s+')[-1])" } }
        else { Say "  --    no plan being managed" }
        Say ""; Say "Layers and watchdogs" Cyan

        # Alert runner (process + state file age)
        $runner = Get-Procs "-m\s+MyTradingSys\.backtest\.layers\.alerts\.live_runner_cli(\s|$)" "Name='python.exe' OR Name='pythonw.exe'"
        $stateFile = Join-Path $Root "MyTradingSys\runtime\live_alert_state.json"
        $stateAge = Age $stateFile
        $StateFileLimitSeconds = 180
        if ($runner.Count) {
            if ($null -ne $stateAge) {
                if ($stateAge -le $StateFileLimitSeconds) {
                    Ok "alert runner running (pid $($runner[0].ProcessId)), state updated ${stateAge}s ago"
                } else {
                    Warn "alert runner running (pid $($runner[0].ProcessId)) but state updated ${stateAge}s ago - STALE (limit ${StateFileLimitSeconds}s)"
                }
            } else {
                Say "  --    alert runner running (pid $($runner[0].ProcessId)), waiting for its first poll"
            }
        } else {
            if ($null -ne $stateAge) {
                Warn "alert runner: no process found but state updated ${stateAge}s ago - started elsewhere, or its command line is not visible"
            } else {
                Warn "alert runner not running - start it with: mts runner"
            }
        }

        # Orphan watchdog (read last log row)
        $orphanLogFile = Join-Path $Root "MyTradingSys\execution\orphan_watchdog.jsonl"
        try {
            if ((Test-Path $orphanLogFile) -and ((Get-Item $orphanLogFile).Length -gt 0)) {
                $lastLine = Get-Content $orphanLogFile -Encoding UTF8 -Tail 1
                $log = $lastLine | ConvertFrom-Json -ErrorAction Stop
                $logTs = [datetimeoffset]::Parse($log.ts)
                $logAge = [int]((Get-Date).ToUniversalTime() - $logTs.UtcDateTime).TotalSeconds
                $haltExists = Test-Path $Halt

                if ($log.event -eq "ok") {
                    if ($log.errors -and $log.errors.PSObject.Properties.Count -gt 0) {
                        Warn "orphan watchdog last run $logAge s ago: $($log.errors.PSObject.Properties.Count) account(s) unreadable (not counted as orphans)"
                    } else {
                        $managers = if ($log.live -and $log.live.Count -gt 0) { [string]::Join(", ", $log.live) } else { "no live managers" }
                        Ok "orphan watchdog last run $logAge s ago: no orphans ($managers)"
                    }
                } elseif ($log.event -eq "orphan_halt") {
                    if ($haltExists) {
                        $orphanInfo = if ($log.orphans -and $log.orphans.Count -gt 0) {
                            $o = $log.orphans[0]
                            "ORPHAN $($o.account) position=$($o.position) open_orders=$($o.open_orders)"
                        } else {
                            "ORPHAN found"
                        }
                        Bad "orphan watchdog last run $logAge s ago: $orphanInfo - HALT is set; mts account, then mts resume"
                    } else {
                        Warn "orphan watchdog last run $logAge s ago found an orphan (HALT since cleared) - re-check with: mts orphans"
                    }
                }
            } else {
                Say "  --    orphan watchdog never run - run it with: mts orphans"
            }
        } catch {
            Warn "orphan watchdog log unreadable: $orphanLogFile"
        }
        Say ""
    }

    "watch" { & (Join-Path $Root "scripts\live\mts-dashboard.ps1") }

    "plan" { Py (Join-Path $Exec "new_plan.py"); exit $LASTEXITCODE }

    "plans" {
        if (-not (Test-Path $Plans) -or -not (Get-ChildItem $Plans -Filter *.json)) { Say "no saved plans - make one with: mts plan"; break }
        $now = (Get-Date).ToUniversalTime()
        Get-ChildItem $Plans -Filter *.json | Sort-Object LastWriteTime -Descending | ForEach-Object {
            $p = Get-Content $_.FullName -Raw | ConvertFrom-Json
            $e = $p.validity.end   # ConvertFrom-Json may already have turned this into a DateTime
            $end = if ($e -is [datetime]) { $e.ToUniversalTime() } else { [datetimeoffset]::Parse($e).UtcDateTime }
            $state = if ($end -lt $now) { "expired" } else { "valid $([int]($end - $now).TotalMinutes) min" }
            $traded = if (Test-Path (Join-Path $Exec "journal\$($p.plan_id).jsonl")) { "traded" } else { "" }
            Say ("  {0,-20} {1,-5} {2,-6} {3,6} USD  {4,-16} {5}" -f $p.plan_id, $p.side, $p.entry.type, $p.caps.max_notional_usd, $state, $traded)
        }
    }

    "check" {
        $file = Resolve-Plan $Arg
        Py (Join-Path $Exec "plan_compiler.py") $file
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Say "Nothing was sent. To place it:  mts trade $([IO.Path]::GetFileNameWithoutExtension($file))" Green
    }

    "trade" {
        $file = Resolve-Plan $Arg
        $id = (Get-Content $file -Raw | ConvertFrom-Json).plan_id
        if ((Test-Path $Halt) -or (Test-Path $HaltLoss)) { Show-Brakes; Say "Trading is paused. Check the account, then: mts resume" Yellow; exit 1 }
        Py (Join-Path $Exec "plan_compiler.py") $file
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        if (-not (Confirm-Word "GO" "Place plan $id on Deribit TESTNET with the orders above?")) { exit 1 }
        Py (Join-Path $Exec "executor.py") $file "--go"
        if ($LASTEXITCODE -ne 0) { Bad "entry did not complete - read the message above, then: mts account"; exit 1 }
        Open-Window "MTS manage $id" "python '$Exec\position_manager.py' $id"
        Ok "entered. Manager window 'MTS manage $id' is guarding the position - leave it open."
    }

    "manage" {
        if (-not $Arg) { Bad "name a plan id, e.g.  mts manage L-mkt-0928-1430"; exit 1 }
        Open-Window "MTS manage $Arg" "python '$Exec\position_manager.py' $Arg"
        Ok "manager window opened for $Arg"
    }

    "account" { Py (Join-Path $Exec "deribit_read.py"); exit $LASTEXITCODE }

    "pause" {
        if (Test-Path $Halt) { Say "already paused"; Show-Brakes; break }
        $who = "$((Get-Date).ToUniversalTime().ToString('s'))Z manual pause via mts"
        [IO.File]::WriteAllText($Halt, "$who`n")
        Ok "paused - new trades are blocked. Open positions keep their stops. Undo with: mts resume"
    }

    "resume" {
        if (-not (Test-Path $Halt) -and -not (Test-Path $HaltLoss)) { Ok "nothing to resume - no brakes set"; break }
        Show-Brakes
        if (-not (Confirm-Word "RESUME" "Have you checked the account (mts account) and are you sure trading may restart?")) { exit 1 }
        $hist = Join-Path $Exec "halt_history"
        New-Item -ItemType Directory -Force $hist | Out-Null
        $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss')
        foreach ($f in @($Halt, $HaltLoss)) {
            if (Test-Path $f) { Move-Item $f (Join-Path $hist "$(Split-Path $f -Leaf)_$stamp.txt") }
        }
        Ok "brakes removed (kept a copy in execution\halt_history)"
    }

    "kill" {
        Say "KILL SWITCH - cancels EVERY open order and closes EVERY position on the testnet account," Red
        Say "then sets HALT so nothing trades until you run: mts resume" Red
        Say "For the MAINNET account use: mts kill-mainnet" Yellow
        if (-not (Confirm-Word "KILL" "Are you sure?")) { exit 1 }
        Py (Join-Path $Exec "kill_switch.py") "--confirm" "KILL"; exit $LASTEXITCODE
    }

    "kill-mainnet" {
        Say "KILL SWITCH - MAINNET (REAL MONEY) - cancels EVERY open order and closes EVERY position on the LIVE account," Red
        Say "then sets HALT so nothing trades until you run: mts resume" Red
        Say "This acts on the MAINNET account. You will be asked to type: kill  (lowercase; anything else cancels)" Yellow
        Remove-Item Env:MTS_ACCOUNT -ErrorAction SilentlyContinue
        Py (Join-Path $Exec "kill_switch.py") "--mainnet"; exit $LASTEXITCODE
    }

    "guard" {
        if ((Get-Procs "daily_loss_monitor" "Name='python.exe'").Count) { Ok "daily-loss guard already running" }
        else {
            Open-Window "MTS daily-loss guard" "python '$Exec\daily_loss_monitor.py'"
            Ok "daily-loss guard started in its own window - leave it open while trading"
        }
        if ((Get-Procs "-m\s+MyTradingSys\.backtest\.layers\.alerts\.live_runner_cli(\s|$)" "Name='python.exe' OR Name='pythonw.exe'").Count) { Ok "live-runner-cli already running" }
        else {
            Open-Window "MTS live-runner-cli" "python -m MyTradingSys.backtest.layers.alerts.live_runner_cli"
            Ok "live-runner-cli started in its own window - leave it open while trading"
        }
        if ((Get-Procs "orderflow_live" "Name='python.exe'").Count) { Ok "orderflow-live already running" }
        else {
            Open-Window "MTS orderflow-live" "python -m MyTradingSys.backtest.layers.fabio.orderflow_live"
            Ok "orderflow-live started in its own window - leave it open while trading"
        }
    }

    "runner" {
        if ((Get-Procs "-m\s+MyTradingSys\.backtest\.layers\.alerts\.live_runner_cli(\s|$)" "Name='python.exe' OR Name='pythonw.exe'").Count) { Ok "alert runner already running"; break }
        Open-Window "MTS alert runner" "python -m MyTradingSys.backtest.layers.alerts.live_runner_cli --poll-seconds 60"
        Ok "alert runner started in its own window - it only writes alerts (no orders); leave it open"
    }

    "orphans" {
        Py (Join-Path $Exec "orphan_watchdog_cli.py")
        switch ($LASTEXITCODE) {
            0 { Ok "no orphan accounts" }
            1 { Warn "some accounts could not be read (not counted as orphans) - see MyTradingSys\execution\orphan_watchdog.jsonl" }
            3 { Bad "ORPHAN found - HALT written. Check: mts account. When it is flat or owned again: mts resume" }
            default { Bad "orphan watchdog failed (exit $LASTEXITCODE)" }
        }
        exit $LASTEXITCODE
    }

    "auto" {
        if ((Get-Procs "auto_trader" "Name='python.exe'").Count) { Ok "auto-trader already running"; break }
        if ((Test-Path $Halt) -or (Test-Path $HaltLoss)) { Show-Brakes; Say "Brakes are set - the auto-trader logs signals but places nothing until: mts resume" Yellow }
        Open-Window "MTS auto-trader" "& 'C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m MyTradingSys.execution.auto_trader"
        Ok "auto-trader started in its own window - it trades Tom + layer signals on TESTNET; mts pause stops new trades"
    }

    "ledger" {
        Py (Join-Path $Exec "trade_ledger.py") "--summary"; exit $LASTEXITCODE
    }

    "autolog" {
        $log = Join-Path $Exec "auto_trades.jsonl"
        if (-not (Test-Path $log)) { Say "no auto-trader decisions yet" Yellow; break }
        Get-Content $log -Tail 20 | ForEach-Object {
            $e = $_ | ConvertFrom-Json
            $why = if ($e.reason) { $e.reason } elseif ($e.outcome) { "$($e.outcome) $($e.plan_id)" } elseif ($e.busy_with) { "busy with $($e.busy_with)" } else { "" }
            Say ("{0}  {1,-16} {2,-28} {3,-5} {4}" -f $e.ts, $e.event, $e.source, $e.side, $why)
        }
    }

    "missed" {
        # Read-only: scores chart-observed setups (observation store) against auto_trades.jsonl on 1m bars.
        $mArgs = @(); if ($Arg) { $mArgs += @("--horizon-h", $Arg) }
        Py (Join-Path $Root "MyTradingSys\observation\missed.py") @mArgs; exit $LASTEXITCODE
    }

    "soak" {
        Py (Join-Path $Exec "soak_report.py") (Join-Path $Exec "journal"); exit $LASTEXITCODE
    }

    "wiring" {
        Py (Join-Path $Root "scripts\dev\wiring_scan.py") "--check"; exit $LASTEXITCODE
    }

    "desk" {
        # Read-only list of the desk board; agents take/finish tasks with scripts\dev\desk.py.
        Py (Join-Path $Root "scripts\dev\desk.py") "list"; exit $LASTEXITCODE
    }

    "test" { Py (Join-Path $Root "scripts\dev\run_all_tests.py") "--quick"; exit $LASTEXITCODE }

    "go" {
        # Launch logic lives in scripts/sched/go.py: dry inside a Claude Code session (one writer per tree), live here.
        $goArgs = @(); if ($Arg) { $goArgs += $Arg }; if ($Id) { $goArgs += @("--id", $Id) }; if ($Dry) { $goArgs += "--dry" }
        Set-Location $Root
        Py (Join-Path $Root "scripts\sched\go.py") @goArgs; exit $LASTEXITCODE
    }

    "guide" { Invoke-Item $Guide }

    default { Bad "unknown verb '$Verb'"; & $PSCommandPath help; exit 2 }
}
