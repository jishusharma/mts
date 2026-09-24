param(

    [ValidateSet("prep","armed","live")]
    [string]$M = "prep",
    [ValidateSet("short","long","")]
    [string]$Dir = "",
    [double]$E = 0,
    [double]$S = 0,
    [double]$T = 0,
    [ValidateSet("on","off")]
    [string]$Popups = "on"
)

# Pull in shared functions, including Get-Descendants.
. "$PSScriptRoot\shared-functions.ps1"

$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Set-Location $R

# read lock; clear if stale
$lockFile = Join-Path $R "runtime_data\apparatus.lock"
$rootPids = @()
if (Test-Path $lockFile) {
    $parts = (Get-Content $lockFile -Raw).Trim() -split "\s+"
    if ($parts.Length -ge 1) {
        try { $rootPids += [int]$parts[0] } catch {}
    }
    if ($rootPids.Count -gt 0) {
        $existing = Get-Process -Id $rootPids[0] -ErrorAction SilentlyContinue
        if ($existing -and ($existing.ProcessName -eq "powershell" -or $existing.ProcessName -eq "pwsh")) {
            # Gap 6: validate lock content, not just PID liveness. Confirms the
            # process is a loop wrapper and the lock epoch matches its start
            # time, guarding against PID reuse.
            $ci = Get-CimInstance Win32_Process -Filter "ProcessId=$($rootPids[0])" -ErrorAction SilentlyContinue
            $cmdOk = $false
            if ($ci -and $ci.CommandLine) {
                $cmdOk = ($ci.CommandLine -match 'start-trading-day\.ps1') -or ($ci.CommandLine -match 'mode\.ps1')
            }
            $epochOk = $false
            if ($parts.Length -ge 2) {
                try {
                    $epoch = [long]$parts[1]
                    $startUnix = [long]([DateTimeOffset]$existing.StartTime.ToUniversalTime()).ToUnixTimeSeconds()
                    $epochOk = ($startUnix -ge ($epoch - 10)) -and ($startUnix -le ($epoch + 120))
                } catch {}
            }
            if ($cmdOk -and $epochOk) {
                Write-Host "APPARATUS ALREADY RUNNING PID=$($rootPids[0])"
                Write-Host "Use .\scripts\core\stop-day.ps1 first, then retry."
                exit 1
            } else {
                Write-Host "lock PID=$($rootPids[0]) alive but not this loop (cmdOk=$cmdOk epochOk=$epochOk); clearing stale lock"
            }
        }
    }
    Write-Host "stale lock - clearing"
    Remove-Item $lockFile -ErrorAction SilentlyContinue
}

# scoped kill: only lock-PID descendants + orphan datafeed java


foreach ($rp in $rootPids) {
    $desc = Get-Descendants $rp
    foreach ($p in $desc) {
        $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
        if ($proc) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    }
    $proc = Get-Process -Id $rp -ErrorAction SilentlyContinue
    if ($proc) { Stop-Process -Id $rp -Force -ErrorAction SilentlyContinue }
}

# fallback: orphan processes matching this project's loop, even if the lock
# PID was dead and descendants could not be walked. Excludes this process.
$selfId = $PID
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.ProcessId -eq $selfId) { return }
    $cmd = $_.CommandLine
    if (-not $cmd) { return }
    $isLoop = ($cmd -match 'start-trading-day\.ps1') -or ($cmd -match 'datafeed\.Main') -or ($cmd -match 'statemachine') -or ($cmd -match 'mvn\.cmd.*exec:java')
    if ($isLoop -and ($cmd -match 'BinanceDataFeed|datafeed\.|statemachine')) {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 2

# Ensure supervisor is running (guarded). Mirrors mts-up in load.ps1.
# Reads supervisor.lock, launches detached only if no live supervisor.
$supLock = Join-Path $R "runtime_data\supervisor.lock"
$supRunning = $false
if (Test-Path $supLock) {
    try {
        $sp = [int]((Get-Content $supLock -Raw).Trim() -split "\s+")[0]
        if ($sp -gt 0 -and (Get-Process -Id $sp -ErrorAction SilentlyContinue)) { $supRunning = $true }
    } catch {}
}
if (-not $supRunning) {
    Start-Process pwsh.exe -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$R\scripts\core\loop-supervisor.ps1","-Mode",$M,"-IntervalMin","1","-RestartGraceSec","180") -WindowStyle Hidden
    Start-Sleep -Seconds 1
    Write-Host "supervisor launched"
} else {
    Write-Host "supervisor already running PID=$sp"
}

$splat = @{ Mode = $M; Popups = $Popups }
if ($Dir) { $splat.Direction = $Dir }
if ($E -gt 0) { $splat.Entry = $E }
if ($S -gt 0) { $splat.Stop = $S }
if ($T -gt 0) { $splat.Target = $T }
& "$R\scripts\core\start-trading-day.ps1" @splat