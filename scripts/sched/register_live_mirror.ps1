<#
register_live_mirror.ps1 - registers MTS-LiveMirror: every 5 min, python scripts\dev\live_mirror.py publish  (JIS-NB live tree only).

publish copies the allowlisted live files to the mirror share and moves its CURRENT pointer (LIVE_MIRROR.md); the NUC and laptops read
that mirror with `live_mirror.py pull` / `brief`. live_mirror.py itself refuses to publish anywhere but the folder holding .mts_live,
and this script refuses a -Repo without .mts_live before it builds anything.

Usage (as the logged-in user):
  powershell -File scripts\sched\register_live_mirror.ps1 -Repo C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed           dry run: prints the task, registers nothing
  powershell -File scripts\sched\register_live_mirror.ps1 -Repo C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed -Apply    registers (replaces a same-named task)
Slots: starts at minute 1, so it fires at :01 :06 :11 ... :56, never in a minute used by MTS-AutoDeploy (:00/:15/:30/:45) or
MTS-Backup (:07/:22/:37/:52). Runs as the current user (Interactive, Limited), hidden, one instance at a time, killed after 5 min.
A missed slot is caught up once at the next start; the next publish supersedes it anyway, so nothing replays.
#>
param([Parameter(Mandatory)][string]$Repo, [switch]$Apply)
$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path -LiteralPath $Repo).Path
if (-not (Test-Path -LiteralPath (Join-Path $Repo '.mts_live'))) {
    throw "REFUSED: $Repo has no .mts_live file - the live mirror is published from the live tree only"
}
$mirror = Join-Path $Repo 'scripts\dev\live_mirror.py'
if (-not (Test-Path -LiteralPath $mirror)) { throw "REFUSED: $mirror not found" }

$py = (Get-Command python -ErrorAction Stop).Source
$pyw = Join-Path (Split-Path $py) 'pythonw.exe'   # no console window flashing every 5 min (B173)
if (Test-Path $pyw) { $py = $pyw }
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$act = New-ScheduledTaskAction -Execute $py -Argument 'scripts\dev\live_mirror.py publish' -WorkingDirectory $Repo
$trg = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew
$pri = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

Write-Output ("MTS-LiveMirror: {0} {1}" -f $act.Execute, $act.Arguments)
Write-Output ("  workdir {0}; every 5 min from minute 1; user {1} (Interactive, Limited); hidden; 5 min limit; IgnoreNew; StartWhenAvailable" -f $act.WorkingDirectory, $user)
if ($Apply) {
    Register-ScheduledTask -TaskName 'MTS-LiveMirror' -Action $act -Trigger $trg -Settings $set -Principal $pri -Force | Out-Null
    Write-Output "registered MTS-LiveMirror (every 5 min, :01 :06 :11 ...)"
} else {
    Write-Output "DRY RUN: nothing registered (add -Apply to register)"
}
