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
$lockFile = Join-Path $R "data\apparatus.lock"
$rootPids = @()
if (Test-Path $lockFile) {
    $parts = (Get-Content $lockFile -Raw).Trim() -split "\s+"
    if ($parts.Length -ge 1) {
        try { $rootPids += [int]$parts[0] } catch {}
    }
    if ($rootPids.Count -gt 0) {
        $existing = Get-Process -Id $rootPids[0] -ErrorAction SilentlyContinue
        if ($existing -and $existing.ProcessName -eq "powershell") {
            Write-Host "APPARATUS ALREADY RUNNING PID=$($rootPids[0])"
            Write-Host "Use .\scripts\core\stop-day.ps1 first, then retry."
            exit 1
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

# fallback: orphan java whose cmdline references this project
Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = $_.CommandLine
    if ($cmd -and ($cmd -match 'BinanceDataFeed' -or $cmd -match 'datafeed\.' -or $cmd -match 'statemachine')) {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 2
$splat = @{ Mode = $M; Popups = $Popups }
if ($Dir) { $splat.Direction = $Dir }
if ($E -gt 0) { $splat.Entry = $E }
if ($S -gt 0) { $splat.Stop = $S }
if ($T -gt 0) { $splat.Target = $T }
& "$R\scripts\core\start-trading-day.ps1" @splat