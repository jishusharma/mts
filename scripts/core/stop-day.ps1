# stop_day.ps1 - kill MTS apparatus processes (scoped)

# Pull in shared functions, including Get-Descendants.
. "$PSScriptRoot\shared-functions.ps1"
$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$killed = 0
$rootPids = @()

# 1. Read lock PID
$lockFile = Join-Path $R "data\apparatus.lock"
if (Test-Path $lockFile) {
    $parts = (Get-Content $lockFile -Raw).Trim() -split "\s+"
    if ($parts.Length -ge 1) {
        try { $rootPids += [int]$parts[0] } catch {}
    }
}

# 2. Descendant walker


# 3. Kill descendants first
$allPids = @()
foreach ($rp in $rootPids) { $allPids += (Get-Descendants $rp) }
$allPids = $allPids | Sort-Object -Unique
foreach ($p in $allPids) {
    $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "  killing descendant $p ($($proc.ProcessName))"
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        $killed++
    }
}

# 4. Kill lock PID itself
foreach ($rp in $rootPids) {
    $proc = Get-Process -Id $rp -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "  killing lock PID $rp ($($proc.ProcessName))"
        Stop-Process -Id $rp -Force -ErrorAction SilentlyContinue
        $killed++
    }
}

# 5. Fallback: orphan java with datafeed cmdline
Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = $_.CommandLine
    if ($cmd -and ($cmd -match 'BinanceDataFeed' -or $cmd -match 'datafeed\.' -or $cmd -match 'statemachine')) {
        Write-Host "  killing orphan java $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        $killed++
    }
}

# 6. Remove lock
if (Test-Path $lockFile) {
    Remove-Item $lockFile -ErrorAction SilentlyContinue
}

Write-Host "stopped $killed process(es)"
