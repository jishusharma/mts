# loop-supervisor.ps1
# Watches the loop wrapper. Restarts on hang or death without orphaning java.
# Run in its own window: .\scripts\core\loop-supervisor.ps1
# Stop cleanly: create data\supervisor_stop.flag

param(
    [int]$CheckIntervalSec = 30,
    [int]$SnapshotStaleSec = 240,
    [int]$RestartGraceSec  = 180,
    [string]$Mode = "armed",
    [int]$IntervalMin = 1
)

$ErrorActionPreference = "Continue"
$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Set-Location $R

$SupLog   = Join-Path $R "data\supervisor_log.txt"
$LockFile = Join-Path $R "data\apparatus.lock"
$StopFlag = Join-Path $R "data\supervisor_stop.flag"

function SupLog {
    param([string]$msg)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
    $line = "$stamp | $msg"
    Write-Host $line
    Add-Content -LiteralPath $SupLog -Value $line -Encoding UTF8
}

function Get-JavaDatafeed {
    Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match "datafeed\.Main" }
}

function Get-AllWrappers {
    # Any powershell running start-trading-day.ps1. Defense in depth against duplicates.
    Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match "start-trading-day\.ps1" }
}

function Stop-Hard {
    param([int]$Pid)
    if ($Pid -le 0) { return }
    $p = Get-Process -Id $Pid -ErrorAction SilentlyContinue
    if (-not $p) { return }
    try { Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue } catch {}
    # Poll up to 5s, then taskkill tree.
    for ($i = 0; $i -lt 10; $i++) {
        Start-Sleep -Milliseconds 500
        if (-not (Get-Process -Id $Pid -ErrorAction SilentlyContinue)) { return }
    }
    try { & taskkill.exe /T /F /PID $Pid 2>&1 | Out-Null } catch {}
}

function Stop-WrapperAndChildren {
    # Kill every wrapper, not just the lock PID. Then all java datafeed.Main.
    foreach ($w in (Get-AllWrappers)) {
        SupLog "  killing wrapper PID=$($w.ProcessId)"
        Stop-Hard -Pid $w.ProcessId
    }
    foreach ($j in (Get-JavaDatafeed)) {
        SupLog "  killing java PID=$($j.ProcessId)"
        Stop-Hard -Pid $j.ProcessId
    }
}

SupLog "=== SUPERVISOR START mode=$Mode interval=${IntervalMin}m stale=${SnapshotStaleSec}s grace=${RestartGraceSec}s ==="

# Startup: only enter grace if a live wrapper is present. Otherwise ready now.
$lastRestartUtc = [DateTime]::UtcNow.AddSeconds(-$RestartGraceSec - 1)
if (Test-Path $LockFile) {
    try {
        $parts = (Get-Content $LockFile -Raw).Trim() -split "\s+"
        $p0 = [int]$parts[0]
        if ($p0 -gt 0 -and (Get-Process -Id $p0 -ErrorAction SilentlyContinue)) {
            $lastRestartUtc = [DateTime]::UtcNow
            SupLog "startup: existing wrapper PID=$p0, grace clock starting"
        } else {
            SupLog "startup: lock present but PID=$p0 not alive, ready now"
        }
    } catch {
        SupLog "startup: lock unreadable, ready now"
    }
} else {
    SupLog "startup: no lock file, ready now"
}

while ($true) {
    if (Test-Path $StopFlag) {
        SupLog "stop flag present, exiting"
        exit 0
    }

    $loopPid = 0
    $loopAlive = $false
    if (Test-Path $LockFile) {
        try {
            $parts = (Get-Content $LockFile -Raw).Trim() -split "\s+"
            if ($parts.Length -ge 1) { $loopPid = [int]$parts[0] }
            if ($loopPid -gt 0 -and (Get-Process -Id $loopPid -ErrorAction SilentlyContinue)) {
                $loopAlive = $true
            }
        } catch {}
    }

    $latest = Get-ChildItem (Join-Path $R "data\snapshots\BTCUSDT_*.json") -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $snapAge = 99999
    if ($latest) { $snapAge = [int]((Get-Date) - $latest.LastWriteTime).TotalSeconds }

    $sinceRestart = ([DateTime]::UtcNow - $lastRestartUtc).TotalSeconds
    $inGrace = $sinceRestart -lt $RestartGraceSec

    # Extra wrappers beyond the lock holder = duplicate condition, always restart.
    $wrapperCount = @(Get-AllWrappers).Count
    $dupWrappers = $wrapperCount -gt 1

    $needRestart = $false
    $reason = "ok"
    if ($dupWrappers) {
        $needRestart = $true
        $reason = "duplicate_wrappers count=$wrapperCount"
    } elseif (-not $loopAlive) {
        if ($inGrace) {
            SupLog ("grace wrapper_pid=$loopPid missing, ${sinceRestart}s < ${RestartGraceSec}s, waiting")
        } else {
            $needRestart = $true
            $reason = "wrapper_dead oldPid=$loopPid"
        }
    } elseif (-not $inGrace -and $snapAge -gt $SnapshotStaleSec) {
        $needRestart = $true
        $reason = "wrapper_hung snapAge=${snapAge}s oldPid=$loopPid"
    } else {
        SupLog "ok wrapper=$loopPid snapAge=${snapAge}s grace=$inGrace"
    }

    if ($needRestart) {
        SupLog "RESTART reason=$reason"
        Stop-WrapperAndChildren
        Remove-Item $LockFile -ErrorAction SilentlyContinue
        # Small wait so the OS releases file handles and the lock is truly gone
        # before the new wrapper checks it.
        Start-Sleep -Seconds 3

        $loopArgs = @(
            "-NoProfile","-ExecutionPolicy","Bypass",
            "-File","$R\scripts\core\start-trading-day.ps1",
            "-Mode",$Mode,
            "-IntervalMin",$IntervalMin
        )
        $new = Start-Process powershell.exe -ArgumentList $loopArgs -PassThru -WindowStyle Hidden
        SupLog "  started new wrapper PID=$($new.Id)"
        $lastRestartUtc = [DateTime]::UtcNow
    }

    Start-Sleep -Seconds $CheckIntervalSec
}