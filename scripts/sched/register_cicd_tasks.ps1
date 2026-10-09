<#
register_cicd_tasks.ps1 - registers the two scheduled CI/CD jobs with Windows Task Scheduler (no operator step after this one run).

  MTS-DailyHygiene  every day 06:30 local    python scripts\dev\daily_hygiene.py   -> MyTradingSys\runtime\sched\hygiene_latest.md (STATUS.md embeds it)
  MTS-AutoDeploy    every 15 minutes         python scripts\dev\auto_deploy.py     -> MyTradingSys\runtime\sched\auto_deploy_last.json
                    does something only where the file .mts_live exists (the live tree, JIS-NB); anywhere else it reports NOT_LIVE.

Usage (repo root, as the logged-in user):  powershell -File scripts\sched\register_cicd_tasks.ps1 [-Trigger] [-SkipDeploy]
  -Trigger     start each registered task once now and print its last result
  -SkipDeploy  register only the hygiene job (hosts that are not the live tree)
Idempotent: -Force replaces the same-named task. Runs as the current user, hidden, on battery too, catches up a missed run at the next start.
#>
param([switch]$Trigger, [switch]$SkipDeploy)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$py = (Get-Command python -ErrorAction Stop).Source
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

function Register-MtsJob($name, $script, $trigger) {
    $act = New-ScheduledTaskAction -Execute $py -Argument ("`"$repo\$script`"") -WorkingDirectory $repo
    $set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
    $pri = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $name -Action $act -Trigger $trigger -Settings $set -Principal $pri -Force | Out-Null
    Write-Output "registered $name -> $script"
}

Register-MtsJob 'MTS-DailyHygiene' 'scripts\dev\daily_hygiene.py' (New-ScheduledTaskTrigger -Daily -At '06:30')
if (-not $SkipDeploy) {
    $every15 = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 15)
    Register-MtsJob 'MTS-AutoDeploy' 'scripts\dev\auto_deploy.py' $every15
}

if ($Trigger) {
    foreach ($n in @('MTS-DailyHygiene', 'MTS-AutoDeploy')) {
        if ($SkipDeploy -and $n -eq 'MTS-AutoDeploy') { continue }
        Start-ScheduledTask -TaskName $n
        $deadline = (Get-Date).AddMinutes(30)
        do { Start-Sleep -Seconds 3; $state = (Get-ScheduledTask -TaskName $n).State } while ($state -eq 'Running' -and (Get-Date) -lt $deadline)
        $info = Get-ScheduledTaskInfo -TaskName $n
        Write-Output ("{0}: state {1}, last result {2} (0 = ok), last run {3}" -f $n, $state, $info.LastTaskResult, $info.LastRunTime)
    }
}
