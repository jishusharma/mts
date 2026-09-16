# MTS live: lx - quick check - live price vs snapshot, one line
# usage:    . .\scripts\load.ps1   then type: lx
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$k = Invoke-RestMethod "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=3"
$snap = Get-ChildItem "$root\data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
$j = Get-Content $snap.FullName -Raw | ConvertFrom-Json
$sc = Get-Content "$root\MyTradingSys\mts\runtime\state_code.json" -Raw | ConvertFrom-Json
$log = Get-Content "$root\data\apparatus_log.txt" -Tail 6 | Where-Object { $_ -match "\|" }
"LIVE   $([double]$k[-1][4])"
"SNAP   $($j.current_price)  $($j.timestamp_utc.Substring(11,8))  $($j.conditions.price_vs_va)"
"CVD    $([math]::Round($j.cvd.value,0)) $($j.cvd.slope)   ND_1m $([math]::Round($j.trade_flow.net_delta_1m,0))   OI $($j.open_interest.direction)"
"STATE  $($sc.state)  B=$($sc.bearish_count)  Bull=$($sc.bullish_count)  book $($j.conditions.book_imbalance)"
$log[-1]
