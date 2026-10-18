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

# Resolve pwsh.exe: prefer MSI, fall back to per-user Store AppExecLink.
$pwshCandidates = @(
    "$env:ProgramFiles\PowerShell\7\pwsh.exe",
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\pwsh.exe"
)
$pwshExe = $pwshCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $pwshExe) { $pwshExe = (Get-Command pwsh.exe).Source }

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

# fallback: orphan processes matching this project loop, excludes this process.
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

# Ensure supervisor is running. Launch via VBS + scheduled task.
# VBS hides the console; scheduled task escapes the IDE terminal job.
$supLock = Join-Path $R "runtime_data\supervisor.lock"
$supRunning = $false
if (Test-Path $supLock) {
    try {
        $sp = [int]((Get-Content $supLock -Raw).Trim() -split "\s+")[0]
        if ($sp -gt 0 -and (Get-Process -Id $sp -ErrorAction SilentlyContinue)) { $supRunning = $true }
    } catch {}
}
if (-not $supRunning) {
    $vbsPath   = Join-Path $R "runtime_data\launch-supervisor.vbs"
    $supScript = Join-Path $R "scripts\core\loop-supervisor.ps1"
    $supCmd    = '"{0}" -NoProfile -ExecutionPolicy Bypass -File "{1}" -Mode {2} -IntervalMin 1' -f $pwshExe, $supScript, $M
    $supCmdVbs = $supCmd -replace '"', '""'
    $vbs = @(
        'Set sh = CreateObject("WScript.Shell")'
        ('sh.CurrentDirectory = "{0}"' -f $R)
        ('sh.Run "{0}", 0, False' -f $supCmdVbs)
    ) -join "`n"
    $enc = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($vbsPath, ($vbs + "`n"), $enc)
    $act = New-ScheduledTaskAction -Execute "$env:windir\System32\wscript.exe" -Argument "//nologo ""$vbsPath""" -WorkingDirectory $R
    # Two triggers: the far-future one only makes the task startable by hand (Start-ScheduledTask); the logon one (delay 90 s) is the stack's
    # only boot recovery: without it the supervisor stays down after every reboot until someone runs mode.ps1.
    $trg = New-ScheduledTaskTrigger -Once -At (Get-Date).AddYears(10)
    $trgLogon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
    $trgLogon.Delay = 'PT1M30S'
    # No time limit (the default 72 h would kill a long-lived supervisor); battery never stops or blocks it; never two copies.
    $supSet = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)
    Register-ScheduledTask -TaskName 'MTS-Supervisor' -Action $act -Trigger @($trg, $trgLogon) -Settings $supSet -Force | Out-Null
    Start-ScheduledTask -TaskName 'MTS-Supervisor'
    Start-Sleep -Seconds 1
    Write-Host 'supervisor launched (hidden via VBS + scheduled task)'
} else {
    Write-Host "supervisor already running PID=$sp"
}

$splat = @{ Mode = $M; Popups = $Popups }
if ($Dir) { $splat.Direction = $Dir }
if ($E -gt 0) { $splat.Entry = $E }
if ($S -gt 0) { $splat.Stop = $S }
if ($T -gt 0) { $splat.Target = $T }

# Launch wrapper via VBS + scheduled task.
$wrapVbs    = Join-Path $R "runtime_data\launch-wrapper.vbs"
$wrapScript = Join-Path $R "scripts\core\start-trading-day.ps1"
$wrapArgs = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -Mode {1} -Popups {2}' -f $wrapScript, $splat.Mode, $splat.Popups
if ($splat.ContainsKey("Direction")) { $wrapArgs += ' -Direction ' + $splat.Direction }
if ($splat.ContainsKey("Entry"))     { $wrapArgs += ' -Entry '     + $splat.Entry }
if ($splat.ContainsKey("Stop"))      { $wrapArgs += ' -Stop '      + $splat.Stop }
if ($splat.ContainsKey("Target"))    { $wrapArgs += ' -Target '    + $splat.Target }
$wrapCmd    = '"{0}" {1}' -f $pwshExe, $wrapArgs
$wrapCmdVbs = $wrapCmd -replace '"', '""'
$wvbs = @(
    'Set sh = CreateObject("WScript.Shell")'
    ('sh.CurrentDirectory = "{0}"' -f $R)
    ('sh.Run "{0}", 0, False' -f $wrapCmdVbs)
) -join "`n"
[System.IO.File]::WriteAllText($wrapVbs, ($wvbs + "`n"), $enc)
$wact = New-ScheduledTaskAction -Execute "$env:windir\System32\wscript.exe" -Argument "//nologo ""$wrapVbs""" -WorkingDirectory $R
$wtrg = New-ScheduledTaskTrigger -Once -At (Get-Date).AddYears(10)
Register-ScheduledTask -TaskName 'MTS-Wrapper' -Action $wact -Trigger $wtrg -Force | Out-Null
Start-ScheduledTask -TaskName 'MTS-Wrapper'
Write-Host 'wrapper launched (hidden via VBS + scheduled task)'
Write-Host 'mode.ps1 returning; loop runs detached'
