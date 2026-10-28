<#
register_cicd_tasks.ps1 - registers the two scheduled CI/CD jobs with Windows Task Scheduler (no operator step after this one run).

  MTS-DailyHygiene  every day 06:30 local    python scripts\dev\daily_hygiene.py   -> MyTradingSys\runtime\sched\hygiene_latest.md (STATUS.md embeds it)
                    + 10 min after every logon: JIS-NB is off ~02:00-10:30, and StartWhenAvailable alone does not catch up
                    (it fires ~3 min after boot with no user session; Task Scheduler drops it, event 332). See add_logon_catchup.ps1.
  MTS-AutoDeploy    every 15 minutes         python scripts\dev\auto_deploy.py     -> MyTradingSys\runtime\sched\auto_deploy_last.json
                    does something only where the file .mts_live exists (the live tree, JIS-NB); anywhere else it reports NOT_LIVE.

Usage (as the logged-in user):  powershell -File scripts\sched\register_cicd_tasks.ps1 [-Trigger] [-SkipDeploy] [-Repo <tree>]
  -Trigger     start each registered task once now and print its last result
  -SkipDeploy  register only the hygiene job (hosts that are not the live tree)
  -Repo        the tree the tasks run from (default: the tree this script sits in). Lets a worktree copy of the script register
               tasks that point at the live tree, e.g. -Repo C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
Idempotent: -Force replaces the same-named task. Runs as the current user, hidden, on battery too, catches up a missed run at the next logon.
#>
param([switch]$Trigger, [switch]$SkipDeploy, [string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path)
$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path -LiteralPath $Repo).Path
foreach ($need in @('scripts\dev\daily_hygiene.py', 'scripts\dev\auto_deploy.py')) {
    if (-not (Test-Path -LiteralPath (Join-Path $Repo $need))) { throw "REFUSED: $Repo has no $need - is -Repo a project tree?" }
}
$py = (Get-Command python -ErrorAction Stop).Source
$pyw = Join-Path (Split-Path $py) 'pythonw.exe'   # no console window flashing every tick (B173)
if (Test-Path $pyw) { $py = $pyw }
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

function New-LogonCatchupTrigger {
    # delayed: the logon session is ready ~2.5 min after logon event 7001 (measured 2026-10-14)
    $t = New-ScheduledTaskTrigger -AtLogOn -User $user
    $t.Delay = 'PT10M'
    $t
}

function Register-MtsJob($name, $script, $trigger) {
    $act = New-ScheduledTaskAction -Execute $py -Argument ("`"$Repo\$script`"") -WorkingDirectory $Repo
    $set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
    $pri = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $name -Action $act -Trigger $trigger -Settings $set -Principal $pri -Force | Out-Null
    Write-Output "registered $name -> $script"
}

Register-MtsJob 'MTS-DailyHygiene' 'scripts\dev\daily_hygiene.py' @((New-ScheduledTaskTrigger -Daily -At '06:30'), (New-LogonCatchupTrigger))
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
