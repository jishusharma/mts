<#
register_c_drive_care.ps1 - registers MTS-CDriveCare: every Sunday 04:00 local, runs
  scripts\dev\c_drive_care.ps1 -Apply   (safe deletes only, see that file; skips Chrome cache while Chrome is open)
Log: %LOCALAPPDATA%\MTS-DiskCare\c_drive_latest.md.   Idempotent (-Force replaces).  Run as the logged-in user.
Usage (repo root):  powershell -File scripts\sched\register_c_drive_care.ps1 [-Trigger]
#>
param([switch]$Trigger)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$arg = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}\scripts\dev\c_drive_care.ps1" -Apply' -f $repo
$act = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg -WorkingDirectory $repo
$trg = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '04:00'
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) -MultipleInstances IgnoreNew
$pri = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'MTS-CDriveCare' -Action $act -Trigger $trg -Settings $set -Principal $pri -Force | Out-Null
Write-Output 'registered MTS-CDriveCare (Sunday 04:00)'
if ($Trigger) {
    Start-ScheduledTask -TaskName 'MTS-CDriveCare'
    do { Start-Sleep -Seconds 3 } while ((Get-ScheduledTask -TaskName 'MTS-CDriveCare').State -eq 'Running')
    $i = Get-ScheduledTaskInfo -TaskName 'MTS-CDriveCare'
    Write-Output ("last result {0} (0 = ok)" -f $i.LastTaskResult)
    Get-Content (Join-Path $env:LOCALAPPDATA 'MTS-DiskCare\c_drive_latest.md')
}
