# MTS feed watchdog (D4): one-shot, run every 60 s by scheduled task MTS-Feed-Watchdog.
# Logs snapshot age + state_code age to runtime_data\feed_watchdog.log; WARN above threshold.
# Keeps the HTF context writer (htf_context_live --loop) alive: starts it if absent. Never touches java.
param([int]$MaxSnapshotAgeSec = 180, [int]$MaxStateAgeSec = 180)
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$log  = "$root\runtime_data\feed_watchdog.log"
$now  = Get-Date
function Age($p) { if (Test-Path $p) { [Math]::Max(0,[int]($now - (Get-Item $p).LastWriteTime).TotalSeconds) } else { -1 } }
$snap = Get-ChildItem "$root\runtime_data\snapshots\BTCUSDT_*.json" -ErrorAction SilentlyContinue | Sort LastWriteTime -Desc | Select -First 1
$sAge = if ($snap) { Age $snap.FullName } else { -1 }
$cAge = Age "$root\MyTradingSys\runtime\state_code.json"
$lvl  = if ($sAge -lt 0 -or $sAge -gt $MaxSnapshotAgeSec -or $cAge -lt 0 -or $cAge -gt $MaxStateAgeSec) { "WARN" } else { "OK" }
$htf = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'htf_context_live' } | Select -First 1
$htfNote = "htf_pid=$($htf.ProcessId)"
if (-not $htf) {
    $py = (Get-Command python).Source
    $p = Start-Process $py -ArgumentList "-m","MyTradingSys.backtest.layers.fabio.htf_context_live","--loop" -WorkingDirectory $root -WindowStyle Hidden `
         -RedirectStandardOutput "$root\runtime_data\htf_context_live.out.txt" -RedirectStandardError "$root\runtime_data\htf_context_live.err.txt" -PassThru
    $htfNote = "htf_started_pid=$($p.Id)"
}
Add-Content -Path $log -Value ("{0} {1} snapshot_age_s={2} state_code_age_s={3} {4}" -f $now.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $lvl, $sAge, $cAge, $htfNote)
