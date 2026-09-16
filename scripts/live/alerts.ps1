# MTS live: alerts - last 10 alerts from the system log
# usage:    . .\scripts\load.ps1   then type: alerts
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Get-Content "$root\data\apparatus_log.txt" | Select-String "ALERT #" | Select -Last 10
