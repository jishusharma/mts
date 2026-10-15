# MTS feed watchdog (D4): one-shot, run every 60 s by scheduled task MTS-Feed-Watchdog.
# Logs snapshot age + state_code age to runtime_data\feed_watchdog.log; WARN above threshold.
# Keeps the HTF context writer (htf_context_live --loop) and the order-flow writer (orderflow_live) alive: starts them if absent. Never touches java.
param([int]$MaxSnapshotAgeSec = 180, [int]$MaxStateAgeSec = 180)
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$log  = "$root\runtime_data\feed_watchdog.log"
$now  = Get-Date
function Age($p) { if (Test-Path $p) { [Math]::Max(0,[int]($now - (Get-Item $p).LastWriteTime).TotalSeconds) } else { -1 } }
$snap = Get-ChildItem "$root\runtime_data\snapshots\BTCUSDT_*.json" -ErrorAction SilentlyContinue | Sort LastWriteTime -Desc | Select -First 1
$sAge = if ($snap) { Age $snap.FullName } else { -1 }
$cAge = Age "$root\MyTradingSys\runtime\state_code.json"
$lvl  = if ($sAge -lt 0 -or $sAge -gt $MaxSnapshotAgeSec -or $cAge -lt 0 -or $cAge -gt $MaxStateAgeSec) { "WARN" } else { "OK" }
$htf = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" | Where-Object { $_.CommandLine -match 'htf_context_live' } | Select -First 1
$htfNote = "htf_pid=$($htf.ProcessId)"
if (-not $htf) {
    $py = (Get-Command pythonw).Source
    if (-not $py) { $py = (Get-Command python).Source }
    $p = Start-Process $py -ArgumentList "-m","MyTradingSys.backtest.layers.fabio.htf_context_live","--loop" -WorkingDirectory $root -WindowStyle Hidden `
         -RedirectStandardOutput "$root\runtime_data\htf_context_live.out.txt" -RedirectStandardError "$root\runtime_data\htf_context_live.err.txt" -PassThru
    $htfNote = "htf_started_pid=$($p.Id)"
}
$of = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" | Where-Object { $_.CommandLine -match 'fabio\.orderflow_live' } | Select -First 1
$ofNote = "of_pid=$($of.ProcessId)"
if ($of) {
    # 2026-10-16: the writer process was alive but hung since 2026-10-14 (no csv row for 1.4 days). Alive is not healthy:
    # no csv write for 10 min while the market is open = kill and let the start below resume from _state.json.
    # At most one such kill per 15 min (marker file), so a market-data outage cannot make a kill loop.
    $csv = Get-ChildItem "$root\MyTradingSys\runtime\orderflow_live\*.csv" -ErrorAction SilentlyContinue | Sort LastWriteTime -Desc | Select -First 1
    $csvAge = if ($csv) { [int]($now - $csv.LastWriteTime).TotalSeconds } else { 999999 }
    $mark = "$root\runtime_data\orderflow_watchdog_kill.txt"
    $markAge = if (Test-Path $mark) { [int]($now - (Get-Item $mark).LastWriteTime).TotalSeconds } else { 999999 }
    if ($csvAge -gt 600 -and $markAge -gt 900) {
        Set-Content -Path $mark -Value ("{0} killed pid {1}, csv age {2}s" -f $now.ToUniversalTime().ToString("o"), $of.ProcessId, $csvAge)
        Stop-Process -Id $of.ProcessId -Force -ErrorAction SilentlyContinue
        $of = $null
        $ofNote = "of_hung_killed csv_age_s=$csvAge"
    }
}
if (-not $of) {
    # 2026-10-14: the writer died and nothing restarted it; live health stayed RED on orderflow for 1.4 days. Resumes from _state.json.
    $py2 = (Get-Command pythonw).Source
    if (-not $py2) { $py2 = (Get-Command python).Source }
    $p2 = Start-Process $py2 -ArgumentList "-m","MyTradingSys.backtest.layers.fabio.orderflow_live" -WorkingDirectory $root -WindowStyle Hidden `
         -RedirectStandardOutput "$root\runtime_data\orderflow_live.out.txt" -RedirectStandardError "$root\runtime_data\orderflow_live.err.txt" -PassThru
    $ofNote = "$ofNote of_started_pid=$($p2.Id)"
}
Add-Content -Path $log -Value ("{0} {1} snapshot_age_s={2} state_code_age_s={3} {4}" -f $now.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $lvl, $sAge, $cAge, "$htfNote $ofNote")
