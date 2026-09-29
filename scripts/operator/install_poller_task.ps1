# Registers scheduled task 'MTS-OperatorPoller' (at logon, current user, hidden). Run once, manually.
$script = Join-Path $PSScriptRoot 'inbox_poller.ps1'
$arg = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg -WorkingDirectory (Split-Path $PSScriptRoot -Parent | Split-Path -Parent)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$settings = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
Register-ScheduledTask -TaskName 'MTS-OperatorPoller' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
Write-Output "registered MTS-OperatorPoller (starts at next logon; start now: Start-ScheduledTask MTS-OperatorPoller)"
