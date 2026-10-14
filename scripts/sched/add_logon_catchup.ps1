<#
add_logon_catchup.ps1 - gives the daily MTS jobs a delayed at-logon trigger so a run missed while the PC was off happens after boot.

Why (2026-10-14, event logs): JIS-NB is powered off ~02:00-10:30 IST, so the 06:30-09:10 daily jobs never run on time. The
StartWhenAvailable catch-up fires ~3 min after boot while no user is logged on, and Task Scheduler drops it (event 332, principal
ENG\jis Interactive/Limited) without a retry. Logon sessions are ready ~2.5 min after logon event 7001, so a logon trigger delayed
10 min starts the job once the session exists. MTS-Retention and 'MTS testnet status' also had StartWhenAvailable off: turned on.

Usage (as the logged-in user):
  powershell -File scripts\sched\add_logon_catchup.ps1           dry run: reads the tasks, prints what would change, writes nothing
  powershell -File scripts\sched\add_logon_catchup.ps1 -Apply    writes (Set-ScheduledTask: triggers and settings only)
Only the tasks listed in $Tasks are read or changed; each keeps its actions, principal and existing triggers. A task that already has
a logon trigger, or is missing on this host, is skipped with a note. Idempotent: a second -Apply finds the logon trigger and skips.
Side effect to know: the job now also starts at every logon (the daily jobs are idempotent; a running instance is never doubled).
#>
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$Delay = 'PT10M'
$Tasks = @(
    'MTS-DailyHygiene', 'MTS-Make-Status', 'MTS-Alert-Rate-Check', 'MTS-Audit-Rotation', 'MTS-Audit-Digest',
    'MTS-Declutter-Backups', 'MTS-Orphan-Watchdog', 'MTS-Retention', 'MTS testnet status', 'MTS-CDriveCare'
)
$user = "$env:USERDOMAIN\$env:USERNAME"

function Get-TriggerKinds($task) {
    (@($task.Triggers | ForEach-Object { $_.CimClass.CimClassName -replace '^MSFT_Task|Trigger$', '' }) -join ',')
}

if ($Apply) { Write-Output "add_logon_catchup: WRITING changes for $user (logon delay $Delay)" }
else { Write-Output "add_logon_catchup: DRY RUN, nothing is written (add -Apply to write); user $user, logon delay $Delay" }
$change = 0; $ok = 0; $missing = 0
foreach ($name in $Tasks) {
    $t = Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    if (-not $t) {
        Write-Output "skip   ${name}: task not found on this host"
        $missing++
        continue
    }
    $kinds = Get-TriggerKinds $t
    $hasLogon = @($t.Triggers | Where-Object { $_.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger' }).Count -gt 0
    if ($hasLogon) {
        Write-Output "skip   ${name}: already has a logon trigger [$kinds]"
        $ok++
        continue
    }
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $user
    $logon.Delay = $Delay
    $verb = if ($Apply) { 'adding' } else { 'would ' }
    Write-Output ("{0} {1}: triggers [{2}] + logon (delay {3}); StartWhenAvailable {4} -> True" -f $verb, $name, $kinds, $logon.Delay, $t.Settings.StartWhenAvailable)
    $change++
    if ($Apply) {
        $t.Settings.StartWhenAvailable = $true
        Set-ScheduledTask -TaskName $name -TaskPath $t.TaskPath -Trigger (@($t.Triggers) + $logon) -Settings $t.Settings | Out-Null
        $after = Get-ScheduledTask -TaskName $name -TaskPath $t.TaskPath
        Write-Output ("APPLIED {0}: triggers now [{1}], StartWhenAvailable {2}" -f $name, (Get-TriggerKinds $after), $after.Settings.StartWhenAvailable)
    }
}
Write-Output ("add_logon_catchup: {0} to change, {1} already have a logon trigger, {2} not found{3}" -f $change, $ok, $missing, $(if ($Apply) { ' (applied)' } else { ' (dry run)' }))
