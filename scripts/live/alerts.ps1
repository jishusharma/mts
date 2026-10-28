# MTS live: alerts - last 10 alerts from the system log
# usage:    . .\scripts\load.ps1   then type: alerts
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Get-Content "$root\runtime_data\apparatus_log.txt" | Select-String "ALERT #" | Select -Last 10
