# MTS live: health - java process, state file age, log tail
# usage:    . .\scripts\load.ps1   then type: health
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
"JAVA:"
Get-Process java -ErrorAction SilentlyContinue | Select Id, StartTime, Path | Format-Table -AutoSize
$sc = "$root\MyTradingSys\mts\runtime\state_code.json"
$age = [math]::Round((New-TimeSpan -Start (Get-Item $sc).LastWriteTime -End (Get-Date)).TotalSeconds, 0)
"state_code age: $age s"
"apparatus tail:"
Get-Content "$root\data\apparatus_log.txt" -Tail 4
