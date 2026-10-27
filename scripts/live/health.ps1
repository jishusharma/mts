# MTS live: health - java process, state file age, log tail
# usage:    . .\scripts\load.ps1   then type: health
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
"JAVA:"
Get-Process java -ErrorAction SilentlyContinue | Select Id, StartTime, Path | Format-Table -AutoSize
$sc = "$root\MyTradingSys\runtime\state_code.json"
$age = [math]::Round((New-TimeSpan -Start (Get-Item $sc).LastWriteTime -End (Get-Date)).TotalSeconds, 0)
"state_code age: $age s"
"apparatus tail:"
Get-Content "$root\runtime_data\apparatus_log.txt" -Tail 4
