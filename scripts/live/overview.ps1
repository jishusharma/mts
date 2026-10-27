# MTS live: overview - live, snapshot, state, and log together
# usage:    . .\scripts\load.ps1   then type: overview
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$k = Invoke-RestMethod "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=5"
$snap = Get-ChildItem "$root\runtime_data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
$j = Get-Content $snap.FullName -Raw | ConvertFrom-Json
$sc = Get-Content "$root\MyTradingSys\runtime\state_code.json" -Raw | ConvertFrom-Json
"===== DECIDE $(Get-Date -Format 'HH:mm:ss') ====="
"LIVE   $([double]$k[-1][4])   SNAP $($j.current_price) @ $($j.timestamp_utc.Substring(11,8))"
"VWAP   $($j.vwap.price) $($j.vwap.slope)"
"CVD    $([math]::Round($j.cvd.value,0)) $($j.cvd.slope)   1h Delta $([math]::Round($j.cvd.cvd_recent.delta_1h,0))"
"FLOW   ND_1m $([math]::Round($j.trade_flow.net_delta_1m,0))  ND_5m $([math]::Round($j.trade_flow.net_delta_5m,0))  ND_15m $([math]::Round($j.trade_flow.net_delta_15m,0))"
"OI     $($j.open_interest.direction)  book $($j.conditions.book_imbalance)"
"STATE  $($sc.state)  B=$($sc.bearish_count)  Bull=$($sc.bullish_count)"
"---- last 3 cycles ----"
Get-Content "$root\runtime_data\apparatus_log.txt" -Tail 6 | Where-Object { $_ -match "\|" }
"---- last 5 1m bars ----"
$k | ForEach-Object {
  "{0}  C={1}  V={2}  D={3}" -f `
    ([DateTimeOffset]::FromUnixTimeMilliseconds($_[0])).ToString("HH:mm"),
    [double]$_[4],
    [math]::Round([double]$_[5],1),
    [math]::Round((2*[double]$_[9] - [double]$_[5]),1)
}
