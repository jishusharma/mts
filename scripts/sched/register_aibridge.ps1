<#
register_aibridge.ps1 - registers the DSA AI Bridge agent (F:\AIBridge\src\agent.ps1, 127.0.0.1:7181) with Task Scheduler.

  AIBridge-Agent   at logon + every 5 min   hidden (conhost --headless), output appended to F:\AIBridge\src\run\agent.log
                   MultipleInstances=IgnoreNew, so the 5-min trigger is a watchdog: it only starts the agent when it is not running.
                   Also restarts up to 3x (1 min apart) if the agent exits with an error.

Usage (as the logged-in user):  powershell -File scripts\sched\register_aibridge.ps1 [-Root F:\AIBridge] [-Remove]
Idempotent (-Force). Check: python scripts\dev\aibridge_health.py   (or  Get-ScheduledTaskInfo AIBridge-Agent)
Why: 2026-10-12 the task was logon-only with a visible window; a logoff/Ctrl-C (0xC000013A) left the bridge down with no restart.
#>
param([string]$Root = 'F:\AIBridge', [switch]$Remove)
$ErrorActionPreference = 'Stop'
$name = 'AIBridge-Agent'
if ($Remove) {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
    Write-Output "removed $name"
    exit 0
}
$agent = Join-Path $Root 'src\agent.ps1'
if (-not (Test-Path $agent)) { throw "no agent at $agent" }
$logDir = Join-Path $Root 'src\run'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir 'agent.log'
$cmd = "if ((Test-Path '$log') -and ((Get-Item '$log').Length -gt 5MB)) { Move-Item -Force '$log' '$log.old' }; " +
       "Add-Content '$log' ('--- start ' + (Get-Date -Format o)); & '$agent' *>> '$log'"
$conhost = Join-Path $env:SystemRoot 'System32\conhost.exe'
$arg = "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -Command `"$cmd`""
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$act = New-ScheduledTaskAction -Execute $conhost -Argument $arg -WorkingDirectory (Join-Path $Root 'src')
$t1 = New-ScheduledTaskTrigger -AtLogOn -User $user
$t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 5)
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$pri = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $act -Trigger @($t1, $t2) -Settings $set -Principal $pri -Force | Out-Null
Write-Output "registered $name -> $agent (logon + every 5 min watchdog, hidden, log $log)"
