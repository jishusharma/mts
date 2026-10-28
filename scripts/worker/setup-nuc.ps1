# FILE: setup-nuc.ps1
# PURPOSE: One-time setup on the NUC for worker version 2.
#          1. Stores the queue share credential for this account (survives reboots).
#          2. Installs the launcher and worker under C:\MTS-Worker.
#          3. Sets Ollama to one request at a time and to keep the model loaded.
#          4. Disables sleep and hibernate on mains power.
#          5. Registers the scheduled task MTS-NUC-Worker: starts at sign-in,
#             hidden, no time limit, one copy only. Then starts it.
#          Safe to run again.
# RUN:     On the NUC, signed in as the account that runs Ollama, in PowerShell
#          opened with Run as administrator (commands printed by setup-desktop.ps1):
#          net use Z: /delete /y
#          net use \\jis-nb\MTS-Queue /user:jis-nb\mtsworker *
#          powershell -ExecutionPolicy Bypass -File \\jis-nb\MTS-Queue\deploy\setup-nuc.ps1
param(
    [string]$DesktopHost = 'jis-nb',
    [string]$ShareName = 'MTS-Queue',
    [string]$WorkerUser = 'mtsworker',
    [string]$LocalRoot = 'C:\MTS-Worker',
    [string]$TaskName = 'MTS-NUC-Worker'
)

$ErrorActionPreference = 'Stop'
$QueueRoot = "\\$DesktopHost\$ShareName"
$Me = "$env:USERDOMAIN\$env:USERNAME"
function Step([string]$Message) { Write-Host "[setup] $Message" }

# 1. Credential, stored in this account's credential manager
# A stale entry for the same host (for example the desktop user's own
# account, saved by an earlier drive mapping) wins over a new one and makes
# every access fail with Access denied. Replace it, then prove it took.
$listed = (& cmdkey "/list:$DesktopHost" | Out-String)
if ($listed -notmatch [regex]::Escape($WorkerUser)) {
    if ($listed -match 'User:') { & cmdkey "/delete:$DesktopHost" | Out-Null; Step "removed an old stored credential for $DesktopHost" }
    $cred = Get-Credential -UserName "$DesktopHost\$WorkerUser" -Message "Password of $WorkerUser on $DesktopHost (chosen in setup-desktop.ps1)"
    $plain = $cred.GetNetworkCredential().Password
    & cmdkey "/add:$DesktopHost" "/user:$DesktopHost\$WorkerUser" "/pass:$plain" | Out-Null
    $plain = $null
    $listed = (& cmdkey "/list:$DesktopHost" | Out-String)
    if ($listed -notmatch [regex]::Escape($WorkerUser)) { throw "Credential for $DesktopHost was not stored. cmdkey /list:$DesktopHost shows:`n$listed" }
    Step "stored the credential for $DesktopHost as $WorkerUser"
} else {
    Step "credential for $DesktopHost already stored as $WorkerUser"
}
foreach ($m in @(Get-SmbMapping -ErrorAction SilentlyContinue | Where-Object { $_.LocalPath -and $_.RemotePath -like "\\$DesktopHost\*" -and $_.RemotePath -notlike "*\$ShareName" })) {
    Remove-SmbMapping -LocalPath $m.LocalPath -Force -UpdateProfile -ErrorAction SilentlyContinue
    Step "removed old drive mapping $($m.LocalPath) -> $($m.RemotePath)"
}
if (-not (Test-Path -LiteralPath (Join-Path $QueueRoot 'incoming'))) {
    throw "Cannot reach $QueueRoot\incoming. Check the desktop is on and setup-desktop.ps1 has run."
}
Step "queue share reachable at $QueueRoot"

# 2. Local install
New-Item -ItemType Directory -Force -Path $LocalRoot, (Join-Path $LocalRoot 'outbox'), (Join-Path $LocalRoot 'logs') | Out-Null
foreach ($f in 'nuc-launcher.ps1', 'nuc-worker.ps1') {
    Copy-Item -LiteralPath (Join-Path $QueueRoot "deploy\$f") -Destination (Join-Path $LocalRoot $f) -Force
}
Step "installed launcher and worker in $LocalRoot"

# 3. Ollama settings for this account (read when Ollama starts; the reboot test applies them)
[Environment]::SetEnvironmentVariable('OLLAMA_NUM_PARALLEL', '1', 'User')
[Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '30m', 'User')
Step 'Ollama: one request at a time, model kept loaded 30 minutes between tasks'

# 4. Always-on power settings
& powercfg /change standby-timeout-ac 0
& powercfg /change hibernate-timeout-ac 0
Step 'power: sleep and hibernate disabled on mains power'

# 5. Scheduled task
$arg = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$LocalRoot\nuc-launcher.ps1`" -QueueRoot `"$QueueRoot`" -LocalRoot `"$LocalRoot`""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $Me
$principal = New-ScheduledTaskPrincipal -UserId $Me -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Step "scheduled task $TaskName registered and started"

Write-Host ''
Write-Host 'Two one-time manual settings make this survive a hard power cut:'
Write-Host '  a) Automatic sign-in: run netplwiz, untick "Users must enter a user name and password".'
Write-Host '     If that box is missing: Settings > Accounts > Sign-in options > turn off'
Write-Host '     "Require Windows Hello sign-in for Microsoft accounts", then reopen netplwiz.'
Write-Host '  b) BIOS: press F2 at power-on > Power > After Power Failure = Power On.'
Write-Host 'Then close any old worker window and restart the NUC once to prove it comes back alone.'
Write-Host "Logs: $LocalRoot\logs\launcher.log and worker.log"
