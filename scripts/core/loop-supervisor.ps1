# loop-supervisor.ps1
# Watches the loop wrapper. Restarts on death. Kills tree on stale.
# Single stop flag: runtime_data\loop_stop.flag, honored by wrapper, supervisor,
# and stop-day.ps1.
# Writes runtime_data\loop_state.json on every decision.
# Stale = snapshot or state_code mtime older than SnapshotStaleSec for
# StaleDebounce consecutive ticks.
# Circuit breaker trips after CircuitBreakerRestarts in
# CircuitBreakerWindowMin, refuses further restarts.

param(
    [int]$CheckIntervalSec        = 30,
    [int]$SnapshotStaleSec        = 300,
    [int]$RestartGraceSec         = 420,
    [int]$StaleDebounce           = 2,
    [int]$CircuitBreakerRestarts  = 5,
    [int]$CircuitBreakerWindowMin = 15,
    [string]$Mode                 = "armed",
    [int]$IntervalMin             = 1
)

$ErrorActionPreference = "Continue"
$R = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location $R

$SupLog        = Join-Path $R "runtime_data\supervisor_log.txt"
$LockFile      = Join-Path $R "runtime_data\apparatus.lock"
$StopFlag      = Join-Path $R "runtime_data\loop_stop.flag"
$StateFile     = Join-Path $R "runtime_data\loop_state.json"
$SupLockFile   = Join-Path $R "runtime_data\supervisor.lock"
$StateCodeFile = Join-Path $R "MyTradingSys\runtime\state_code.json"
$SnapGlob      = Join-Path $R "runtime_data\snapshots\BTCUSDT_*.json"

# Auxiliary processes (added 2026-10-03). Restarted by VBS launcher so they
# escape this supervisor's job object and survive terminal close.
$Aux = @(
    @{ name = "auto_trader";        match = "MyTradingSys\.execution\.auto_trader";               vbs = "launch-auto-trader.vbs" },
    @{ name = "live_runner_cli";    match = "MyTradingSys\.backtest\.layers\.alerts\.live_runner_cli"; vbs = "launch-live-runner.vbs" },
    @{ name = "orderflow_live";     match = "MyTradingSys\.backtest\.layers\.fabio\.orderflow_live";  vbs = "launch-orderflow-live.vbs" },
    @{ name = "daily_loss_monitor"; match = "daily_loss_monitor\.py";                             vbs = "launch-daily-loss.vbs" },
    @{ name = "oi_recorder";        match = "oi_recorder\.py";                                    vbs = "launch-oi-recorder.vbs" },
    @{ name = "htf_context_live";   match = "MyTradingSys\.backtest\.layers\.fabio\.htf_context_live"; vbs = "launch-htf-context.vbs" }
)

function SupLog {
    param([string]$msg)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
    $line = "$stamp | $msg"
    Write-Host $line
    Add-Content -LiteralPath $SupLog -Value $line -Encoding UTF8
}

function WriteState {
    param(
        [string]$Action,
        [string]$Reason,
        [int]$WrapperPid,
        [int]$JavaPid,
        [int]$SnapAge,
        [int]$ScAge,
        [int]$StaleStrikes,
        [int]$RestartCount
    )
    $obj = [ordered]@{
        ts_utc             = (Get-Date).ToUniversalTime().ToString("o")
        action             = $Action
        reason             = $Reason
        wrapper_pid        = $WrapperPid
        java_pid           = $JavaPid
        supervisor_pid     = $PID
        snapshot_age_sec   = $SnapAge
        state_code_age_sec = $ScAge
        stale_strikes      = $StaleStrikes
        restart_count_24h  = $RestartCount
    }
    try {
        $json = $obj | ConvertTo-Json -Compress
        [System.IO.File]::WriteAllText($StateFile, $json, (New-Object System.Text.UTF8Encoding $false))
    } catch { }
}

function Watch-Aux {
    param([bool]$InGrace)
    if ($InGrace) { return }
    foreach ($a in $Aux) {
        $alive = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
                   Where-Object { $_.CommandLine -match $a.match })
        if ($alive.Count -gt 0) { continue }
        $vbs = Join-Path $R ("runtime_data\" + $a.vbs)
        if (-not (Test-Path $vbs)) {
            SupLog "AUX missing launcher $($a.vbs) for $($a.name)"
            continue
        }
        SupLog "AUX restart $($a.name) via $($a.vbs)"
        Start-Process wscript.exe -ArgumentList "//nologo `"$vbs`"" -WindowStyle Hidden
    }
}

# single-instance supervisor lock
# One-owner guard (DEVICES.md section 3): refuse to start a second live owner; fail closed.
& python (Join-Path $R "scripts\dev\live_owner.py") check
if ($LASTEXITCODE -ne 0) { Write-Host "live loop owner guard refused start, exiting"; exit 1 }
. (Join-Path $PSScriptRoot "suplock.ps1")
try {
    $fs = [System.IO.File]::Open($SupLockFile, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    $sw = New-Object System.IO.StreamWriter($fs)
    $sw.WriteLine("$PID " + [DateTime]::UtcNow.ToString("o"))
    $sw.Flush(); $sw.Close(); $fs.Close()
} catch [System.IO.IOException] {
    $ex = Get-Content $SupLockFile -Raw -ErrorAction SilentlyContinue
    $ep = Get-SupLockLivePid $ex
    if ($ep -gt 0) {
        Write-Host "supervisor already running PID=$ep, exiting"
        exit 0
    }
    [System.IO.File]::WriteAllText($SupLockFile, "$PID " + [DateTime]::UtcNow.ToString("o"))
}

SupLog "=== SUPERVISOR START mode=$Mode interval=${IntervalMin}m stale=${SnapshotStaleSec}s grace=${RestartGraceSec}s debounce=${StaleDebounce}x breaker=${CircuitBreakerRestarts}/${CircuitBreakerWindowMin}m ==="

# Startup grace: always wait RestartGraceSec before any restart.
# Prevents race when mode.ps1 or mts-up launches supervisor and wrapper together.
$lastRestartUtc = [DateTime]::UtcNow
SupLog "startup: grace clock set, ${RestartGraceSec}s grace before any restart"

$restartTimes = New-Object System.Collections.Generic.List[datetime]
$staleStrikes = 0
$startedPid = 0

while ($true) {
    if (Test-Path $StopFlag) {
        SupLog "loop_stop flag present, exiting"
        WriteState -Action "stop" -Reason "flag_present" -WrapperPid 0 -JavaPid 0 -SnapAge 0 -ScAge 0 -StaleStrikes 0 -RestartCount $restartTimes.Count
        Remove-Item $SupLockFile -ErrorAction SilentlyContinue
        exit 0
    }

    $loopPid = 0
    $loopAlive = $false
    if (Test-Path $LockFile) {
        try {
            $parts = (Get-Content $LockFile -Raw).Trim() -split "\s+"
            if ($parts.Length -ge 1) { $loopPid = [int]$parts[0] }
            if ($loopPid -gt 0 -and (Get-Process -Id $loopPid -ErrorAction SilentlyContinue)) { $loopAlive = $true }
        } catch { }
    }

    $smPid = 0
    $jp = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'statemachine' } | Select-Object -First 1
    if ($jp) { $smPid = $jp.ProcessId }
    $javaPid = $smPid

    $latest = Get-ChildItem $SnapGlob -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $snapAge = 99999
    if ($latest) { $snapAge = [int]((Get-Date) - $latest.LastWriteTime).TotalSeconds }

    $scAge = 99999
    if (Test-Path $StateCodeFile) { $scAge = [int]((Get-Date) - (Get-Item $StateCodeFile).LastWriteTime).TotalSeconds }

    $sinceRestart = ([DateTime]::UtcNow - $lastRestartUtc).TotalSeconds
    $inGrace = $sinceRestart -lt $RestartGraceSec

    $cutoff = [DateTime]::UtcNow.AddMinutes(-$CircuitBreakerWindowMin)
    for ($i = $restartTimes.Count - 1; $i -ge 0; $i--) {
        if ($restartTimes[$i] -lt $cutoff) { $restartTimes.RemoveAt($i) }
    }
    $rc = $restartTimes.Count
    $breakerTripped = ($rc -ge $CircuitBreakerRestarts)

    $action = "ok"
    $reason = "ok"
    $needKill = $false
    $needRestart = $false

    # A just-started wrapper holds no lock until pwsh start, warmup (up to ~2 min) and lock create finish;
    # on a loaded host that took minutes and the old 180 s grace restarted it over and over (restart storm,
    # 8-14 per hour on 2026-10-15). While the PID we started is alive and young, it is starting, not dead.
    $starting = ($startedPid -gt 0 -and $sinceRestart -lt ($RestartGraceSec * 2) -and (Get-Process -Id $startedPid -ErrorAction SilentlyContinue))
    if (-not $loopAlive) {
        if ($inGrace -or $starting) {
            $action = "grace"
            $reason = "wrapper_dead_in_grace oldPid=$loopPid"
            SupLog "$reason ${sinceRestart}s/${RestartGraceSec}s"
        } elseif ($breakerTripped) {
            $action = "breaker"
            $reason = "wrapper_dead_breaker_open count=$rc"
            SupLog "CIRCUIT BREAKER: $reason"
        } else {
            $action = "restart"
            $reason = "wrapper_dead oldPid=$loopPid"
            $needRestart = $true
        }
    } else {
        if ($smPid -eq 0) {
            if ($inGrace) {
                $action = "grace"
                $reason = "sm_dead_in_grace wrapper=$loopPid"
                SupLog "$reason ${sinceRestart}s/${RestartGraceSec}s"
            } elseif ($breakerTripped) {
                $action = "breaker"
                $reason = "sm_dead_breaker_open wrapper=$loopPid"
                SupLog "CIRCUIT BREAKER: $reason"
            } else {
                $action = "kill_restart"
                $reason = "sm_dead wrapper=$loopPid"
                SupLog "state-machine java missing; killing wrapper tree and restarting"
                $needKill = $true
                $needRestart = $true
            }
        } else {
        $snapStale = $snapAge -gt $SnapshotStaleSec
        $scStale = $scAge -gt $SnapshotStaleSec
        if ($inGrace) {
            if ($staleStrikes -gt 0) { SupLog "in grace, strikes reset" }
            $staleStrikes = 0
            $reason = "ok_in_grace wrapper=$loopPid sm=$smPid java=$javaPid snapAge=${snapAge}s scAge=${scAge}s grace=$inGrace"
            SupLog $reason
        } elseif ($snapStale -or $scStale) {
            $staleStrikes++
            SupLog "stale strike $staleStrikes/$StaleDebounce snapAge=${snapAge}s scAge=${scAge}s"
            if ($staleStrikes -ge $StaleDebounce) {
                if ($breakerTripped) {
                    $action = "breaker"
                    $reason = "stale_breaker_open snapAge=${snapAge}s scAge=${scAge}s"
                    SupLog "CIRCUIT BREAKER: $reason"
                    $staleStrikes = 0
                } else {
                    $action = "kill_restart"
                    $reason = "stale snapAge=${snapAge}s scAge=${scAge}s wrapper=$loopPid"
                    $needKill = $true
                    $needRestart = $true
                }
            } else {
                $action = "stale_pending"
                $reason = "strike=$staleStrikes snapAge=${snapAge}s scAge=${scAge}s"
            }
        } else {
            if ($staleStrikes -gt 0) { SupLog "stale recovered, strikes reset" }
            $staleStrikes = 0
            $reason = "ok wrapper=$loopPid sm=$smPid java=$javaPid snapAge=${snapAge}s scAge=${scAge}s grace=$inGrace"
            SupLog $reason
        }
        }
    }

    WriteState -Action $action -Reason $reason -WrapperPid $loopPid -JavaPid $javaPid -SnapAge $snapAge -ScAge $scAge -StaleStrikes $staleStrikes -RestartCount $restartTimes.Count

    if ($needKill -and $loopPid -gt 0) {
        SupLog "KILL tree root=$loopPid"
        $tk = Join-Path $env:SystemRoot "System32\taskkill.exe"
        if (Test-Path $tk) {
            & $tk /F /T /PID $loopPid 2>&1 | ForEach-Object { SupLog "  taskkill: $_" }
        } else {
            SupLog "  taskkill not found at $tk"
        }
        Remove-Item $LockFile -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }

    if ($needRestart) {
        SupLog "RESTART reason=$reason"
        if (-not $needKill) {
            Remove-Item $LockFile -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 3
        }
        $loopArgs = @(
            "-NoProfile","-ExecutionPolicy","Bypass",
            "-File","$R\scripts\core\start-trading-day.ps1",
            "-Mode",$Mode,
            "-IntervalMin",$IntervalMin
        )
        $new = Start-Process pwsh.exe -ArgumentList $loopArgs -PassThru -WindowStyle Hidden
        $nid = $new.Id
        $startedPid = $nid
        SupLog "  started new wrapper PID=$nid"
        $lastRestartUtc = [DateTime]::UtcNow
        $restartTimes.Add([DateTime]::UtcNow) | Out-Null
        $staleStrikes = 0
    }

    & python (Join-Path $R "scripts\dev\live_owner.py") claim | ForEach-Object { SupLog "  owner: $_" }

    Watch-Aux -InGrace:$inGrace

    Start-Sleep -Seconds $CheckIntervalSec
}
