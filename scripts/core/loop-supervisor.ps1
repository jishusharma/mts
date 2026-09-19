# loop-supervisor.ps1
# Watches the loop wrapper. Restarts on death only. Never kills.
# See LOOP_LIFECYCLE_DESIGN_2026-09-19.md stage 1.
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
$LoopStopFlag = Join-Path $R "data\loop_stop.flag"

function SupLog {
    param([string]$msg)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
    $line = "$stamp | $msg"
    Write-Host $line
    Add-Content -LiteralPath $SupLog -Value $line -Encoding UTF8
}


$SupLockFile = Join-Path $R "data\supervisor.lock"
try {
    $fs = [System.IO.File]::Open($SupLockFile, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    $sw = New-Object System.IO.StreamWriter($fs)
    $sw.WriteLine("$PID " + [DateTime]::UtcNow.ToString("o"))
    $sw.Flush(); $sw.Close(); $fs.Close()
} catch [System.IO.IOException] {
    $ex = Get-Content $SupLockFile -Raw -ErrorAction SilentlyContinue
    $ep = 0
    if ($ex) { $ep = [int](($ex.Trim() -split "\s+")[0]) }
    if ($ep -gt 0 -and (Get-Process -Id $ep -ErrorAction SilentlyContinue)) {
        Write-Host "supervisor already running PID=$ep, exiting"
        exit 0
    }
    [System.IO.File]::WriteAllText($SupLockFile, "$PID " + [DateTime]::UtcNow.ToString("o"))
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
        Remove-Item $SupLockFile -ErrorAction SilentlyContinue
        exit 0
    }

    if (Test-Path $LoopStopFlag) {
        SupLog "loop_stop flag present, holding restart"
        Start-Sleep -Seconds $CheckIntervalSec
        continue
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

    $needRestart = $false
    $reason = "ok"
    if (-not $loopAlive) {
        if ($inGrace) {
            SupLog ("grace wrapper_pid=$loopPid missing, ${sinceRestart}s < ${RestartGraceSec}s, waiting")
        } else {
            $needRestart = $true
            $reason = "wrapper_dead oldPid=$loopPid"
        }
    } else {
        SupLog "ok wrapper=$loopPid snapAge=${snapAge}s grace=$inGrace"
    }

    if ($needRestart) {
        SupLog "RESTART reason=$reason"
        SupLog "  reader-only restart: prior wrapper PID=$loopPid not killed"
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