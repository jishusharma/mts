<#
register_codex_lab.ps1 - registers the layer-lab job with Windows Task Scheduler on the host that has the Codex app (JIS-NUC).

  MTS-CodexLab   every 30 minutes   python <lab work tree>\scripts\dev\codex_run.py tick
                 refreshes the lab work tree, then starts Codex on the first ready CODEX card. No card = no Codex call.

Usage (as the logged-in user):  powershell -File scripts\sched\register_codex_lab.ps1 [-LabTree F:\MTS\mts-codex-lab] [-Remove]
Idempotent: -Force replaces the same-named task. Pause without removing: python scripts\dev\codex_run.py stop "<why>".
Spec: MyTradingSys\system\LAYER_LAB.md. Last tick: %CODEX_HOME%\lab_runs\last_tick.txt
#>
param([string]$LabTree = 'F:\MTS\mts-codex-lab', [switch]$Remove)
$ErrorActionPreference = 'Stop'
$name = 'MTS-CodexLab'
if ($Remove) {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
    Write-Output "removed $name"
    exit 0
}
$script = Join-Path $LabTree 'scripts\dev\codex_run.py'
if (-not (Test-Path $script)) { throw "no runner at $script (create the lab work tree first: LAYER_LAB.md)" }
$py = (Get-Command python -ErrorAction Stop).Source
$pyw = Join-Path (Split-Path $py) 'pythonw.exe'   # no console window flashing on the operator's screen every tick
if (Test-Path $pyw) { $py = $pyw }
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$act = New-ScheduledTaskAction -Execute $py -Argument ("`"$script`" tick") -WorkingDirectory $LabTree
$trg = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 30)
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
$pri = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $act -Trigger $trg -Settings $set -Principal $pri -Force | Out-Null
Write-Output "registered $name -> $script tick (every 30 min)"
