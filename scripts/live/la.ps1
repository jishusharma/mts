# MTS live: la - alerts - last 10 alert lines from the system log
# usage:    . .\scripts\load.ps1   then type: la
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Get-Content "$root\data\apparatus_log.txt" | Select-String "ALERT #" | Select -Last 10
