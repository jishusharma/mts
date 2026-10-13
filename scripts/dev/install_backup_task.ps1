# Registers the Windows task MTS-Backup: every 15 min, snapshot every worktree to origin/backup/<host>/<worktree>.
# Offset: BACKUP_OFFSET_MIN=7 past the quarter hour, so it never shares a minute with MTS-AutoDeploy (:00/:15/:30/:45; B178).
# Per-user task, no admin, no secrets; run again to update. Remove with: schtasks /Delete /TN MTS-Backup /F
param([string]$Repo = (Resolve-Path "$PSScriptRoot\..\..").Path)
$py = (Get-Command python -ErrorAction Stop).Source
$pyw = Join-Path (Split-Path $py) 'pythonw.exe'   # no console window flashing every tick (B173)
if (Test-Path $pyw) { $py = $pyw }
$action = New-ScheduledTaskAction -Execute $py -Argument "scripts\dev\backup_snapshot.py --repo `"$Repo`"" -WorkingDirectory $Repo
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(7) -RepetitionInterval (New-TimeSpan -Minutes 15)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "MTS-Backup" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Get-ScheduledTask -TaskName "MTS-Backup" | Select-Object TaskName, State
