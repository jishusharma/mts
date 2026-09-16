# loop-supervisor.ps1
# Watches the loop wrapper. Restarts it if the wrapper dies or hangs.
# Run in its own window: .\scripts\core\loop-supervisor.ps1
# Stop cleanly: create data\supervisor_stop.flag

param(
    [int]$CheckIntervalSec = 30,
    [int]$SnapshotStaleSec = 240,
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
    param([string]$Which)
    Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -match "datafeed\.Main" -and $_.CommandLine -match $Which
        }
}

SupLog "=== SUPERVISOR START mode=$Mode interval=${IntervalMin}m stale=${SnapshotStaleSec}s ==="

while ($true) {
    if (Test-Path $StopFlag) {
        SupLog "stop flag present, exiting"
        exit 0
    }

    $loopAlive = $false
    $loopPid   = 0
    if (Test-Path $LockFile) {
        try {
            $parts = (Get-Content $LockFile -Raw).Trim() -split "\s+"
            if ($parts.Length -ge 1) { $loopPid = [int]$parts[0] }
            if ($loopPid -gt 0) {
                $p = Get-Process -Id $loopPid -ErrorAction SilentlyContinue
                if ($p) { $loopAlive = $true }
            }
        } catch {}
    }

    $latest = Get-ChildItem (Join-Path $R "data\snapshots\BTCUSDT_*.json") -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $snapAge = 99999
    if ($latest) { $snapAge = [int]((Get-Date) - $latest.LastWriteTime).TotalSeconds }

    $hung = ($loopAlive -and $snapAge -gt $SnapshotStaleSec)

    if (-not $loopAlive -or $hung) {
        $reason = if (-not $loopAlive) { "wrapper_dead" } else { "wrapper_hung snapAge=${snapAge}s" }
        SupLog "RESTART reason=$reason oldPid=$loopPid"

        $targets = @()
        $targets += Get-JavaDatafeed -Which "statemachine"
        $targets += Get-JavaDatafeed -Which "snapshot"
        foreach ($t in $targets) {
            SupLog "  killing java PID=$($t.ProcessId)"
            try { Stop-Process -Id $t.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
        }

        if (Test-Path $LockFile) { Remove-Item $LockFile -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2

        $loopArgs = @(
            "-NoProfile","-ExecutionPolicy","Bypass",
            "-File","$R\scripts\core\start-trading-day.ps1",
            "-Mode",$Mode,
            "-IntervalMin",$IntervalMin
        )
        $new = Start-Process powershell.exe -ArgumentList $loopArgs -PassThru -WindowStyle Hidden
        SupLog "  started new wrapper PID=$($new.Id)"
    } else {
        SupLog "ok wrapper=$loopPid snapAge=${snapAge}s"
    }

    Start-Sleep -Seconds $CheckIntervalSec
}
