<#
register_dispatch_gate.ps1 - registers MTS-DispatchGate with Windows Task Scheduler (operator 2026-10-15).

  MTS-DispatchGate  every 10 minutes   python scripts\sched\dispatch_gate.py --root <live tree>
  Runs relay.py tick with no model: NOOP costs nothing, KICK starts ONE headless Haiku relay session. The `mts-dispatcher` App routine
  stays as the hourly fallback (cron 7 * * * *) for refine + housekeep. Log: ~\.claude\mts-dispatch-gate.log

Usage (as the logged-in user):  powershell -File scripts\sched\register_dispatch_gate.ps1 [-Trigger] [-Repo <live tree>] [-PeerQuietMin 90]
Idempotent (-Force replaces the same-named task). JIS-NB peer-quiet 90, JIS-NUC 0.
#>
param([switch]$Trigger, [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path, [int]$PeerQuietMin = 90)
$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path -LiteralPath $Repo).Path
if (-not (Test-Path -LiteralPath (Join-Path $Repo 'scripts\sched\dispatch_gate.py'))) { throw "REFUSED: $Repo has no dispatch_gate.py (ship it first)" }
$py = (Get-Command python -ErrorAction Stop).Source
$conhost = Join-Path $env:SystemRoot 'System32\conhost.exe'   # pythonw alone still flashes a window for every git child; conhost --headless shows none
$action = New-ScheduledTaskAction -Execute $conhost -Argument ('--headless "{2}" "{0}\scripts\sched\dispatch_gate.py" --root "{0}" --peer-quiet-min {1}' -f $Repo, $PeerQuietMin, $py) -WorkingDirectory $Repo
$trig = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName 'MTS-DispatchGate' -Action $action -Trigger $trig -Settings $settings -Force | Out-Null
Write-Output 'registered MTS-DispatchGate (every 10 min)'
if ($Trigger) { Start-ScheduledTask -TaskName 'MTS-DispatchGate'; Start-Sleep 5; Get-ScheduledTaskInfo -TaskName 'MTS-DispatchGate' | Select-Object LastRunTime, LastTaskResult }
