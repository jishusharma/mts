# restart-with-b034.ps1
# Clean restart to load B034 fix. Stops supervisor, kills loop+java, starts fresh, restarts supervisor.
# One-shot utility. Delete after use if desired.

$ErrorActionPreference = 'Stop'
$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Set-Location $R

function Log { param($m) $t = [DateTime]::UtcNow.ToString("HH:mm:ss"); Write-Host "[$t] $m" }

# 1. Stop supervisor
Log "step 1: stop supervisor"
$flag = Join-Path $R "data\supervisor_stop.flag"
New-Item -Path $flag -ItemType File -Force | Out-Null
$supWait = 0
while ($supWait -lt 45) {
    Start-Sleep -Seconds 3
    $supWait += 3
    $sup = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'loop-supervisor' }
    if (-not $sup) { break }
}
if ($sup) { Log "WARN supervisor still alive after 45s: PID $($sup.ProcessId)" }
else      { Log "supervisor exited" }
Remove-Item $flag -ErrorAction SilentlyContinue

# 2. Kill loop + java cleanly
Log "step 2: stop-day.ps1"
& "$R\scripts\core\stop-day.ps1"

Start-Sleep -Seconds 3
$java = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'datafeed\.Main' }
if ($java) { Log "WARN java still alive: $($java.ProcessId)"; throw "java did not die" }
else       { Log "no datafeed java running" }

$wrap = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'start-trading-day\.ps1' }
if ($wrap) { Log "WARN wrapper still alive: $($wrap.ProcessId)"; throw "wrapper did not die" }
else       { Log "no wrapper running" }

# 3. Start fresh
Log "step 3: mode.ps1 -M armed"
Start-Process powershell.exe -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$R\scripts\core\mode.ps1","-M","armed") -WindowStyle Hidden

Start-Sleep -Seconds 5
$newWrap = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'start-trading-day\.ps1' }
$newJava = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'datafeed\.Main' }
if ($newWrap) { Log "wrapper up: PID $($newWrap.ProcessId)" }
if ($newJava) { Log "java up: PID $($newJava.ProcessId)" }
if (-not $newWrap) { throw "wrapper did not start" }

# 4. Restart supervisor
Log "step 4: restart supervisor"
$supArgs = @(
    "-NoProfile","-ExecutionPolicy","Bypass",
    "-File","$R\scripts\core\loop-supervisor.ps1",
    "-Mode","armed","-IntervalMin","1","-RestartGraceSec","90"
)
$newSup = Start-Process powershell.exe -ArgumentList $supArgs -PassThru -WindowStyle Hidden
Log "supervisor started: PID $($newSup.Id)"

# 5. Verify
Start-Sleep -Seconds 5
Log "step 5: verify"
$lock = Join-Path $R "data\apparatus.lock"
if (Test-Path $lock) { Log "lock: $(Get-Content $lock -Raw)" } else { Log "WARN no lock" }
$sc = Get-Item "$R\MyTradingSys\mts\runtime\state_code.json" -ErrorAction SilentlyContinue
if ($sc) {
    $age = [int]((Get-Date) - $sc.LastWriteTime).TotalSeconds
    Log "state_code.json age: ${age}s"
}
Log "done"