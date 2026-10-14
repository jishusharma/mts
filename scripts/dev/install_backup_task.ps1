# Registers the Windows task MTS-Backup: every 15 min, snapshot every worktree to refs/heads/backup/<host>/<worktree> on the LOCAL bare repo (git remote "backup").
# The GitHub repo (origin) is PUBLIC since 2026-10-11 and a snapshot carries uncommitted + untracked files, so the task passes --remote backup
# (F:\MTS_backup.git on JIS-NB) and this script refuses a repo that has no "backup" remote. backup_snapshot.py also refuses origin without --allow-origin.
# Offset: BACKUP_OFFSET_MIN=7 past the quarter hour, so it never shares a minute with MTS-AutoDeploy (:00/:15/:30/:45; B178).
# Per-user task, no admin, no secrets; run again to update. Remove with: schtasks /Delete /TN MTS-Backup /F
# The live task today runs runtime_data\launch-backup.vbs (wscript, no console window, same arguments); re-running this replaces that
# action with pythonw.exe directly (also windowless), the exit code still lands in the task's LastTaskResult.
param([string]$Repo = (Resolve-Path "$PSScriptRoot\..\..").Path)
$remotes = @(& git -C $Repo remote)
if ($remotes -notcontains 'backup') {
    throw "REFUSED: $Repo has no git remote named 'backup' (git -C $Repo remote add backup F:/MTS_backup.git). Not falling back to origin: it is the public repo."
}
$py = (Get-Command python -ErrorAction Stop).Source
$pyw = Join-Path (Split-Path $py) 'pythonw.exe'   # no console window flashing every tick (B173)
if (Test-Path $pyw) { $py = $pyw }
$action = New-ScheduledTaskAction -Execute $py -Argument "scripts\dev\backup_snapshot.py --repo `"$Repo`" --remote backup" -WorkingDirectory $Repo
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(7) -RepetitionInterval (New-TimeSpan -Minutes 15)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "MTS-Backup" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Get-ScheduledTask -TaskName "MTS-Backup" | Select-Object TaskName, State
