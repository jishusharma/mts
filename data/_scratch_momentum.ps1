$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$log = Join-Path $R "data\_mom_state.json"
$lastSnap = ""
while ($true) {
  $s = Get-ChildItem "$R\data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
  if ($s.Name -eq $lastSnap) { Start-Sleep -Seconds 15; continue }
  $lastSnap = $s.Name
  $j = Get-Content $s.FullName -Raw | ConvertFrom-Json
  $sc = Get-Content "$R\MyTradingSys\mts\runtime\state_code.json" -Raw | ConvertFrom-Json
  $now = (Get-Date).ToUniversalTime().ToString("HH:mm:ss")
  $prev = if (Test-Path $log) { Get-Content $log -Raw | ConvertFrom-Json } else { $null }
  $p = @{
    t = $now
    px = [double]$j.current_price
    cvd = [double]$j.cvd.value
    nd1m = [double]$j.trade_flow.net_delta_1m
    nd5m = [double]$j.trade_flow.net_delta_5m
    nd15m = [double]$j.trade_flow.net_delta_15m
    book = [double]$j.order_book_depth.bid_ask_ratio
    bull = [int]$sc.bullish_count
    bear = [int]$sc.bearish_count
    state = $sc.state
  }
  $r1 = $j.setup_candidates | Where-Object { $_.rank -eq 1 } | Select -First 1
  $p.proof = if ($r1) { [int]$r1.score.proof_count } else { 0 }
  $p.tier = if ($r1) { $r1.math.tier } else { "-" }
  if ($prev) {
    $dPx = [math]::Round($p.px - $prev.px, 1)
    $dCvd = [math]::Round($p.cvd - $prev.cvd, 1)
    $dNd1 = [math]::Round($p.nd1m - $prev.nd1m, 1)
    $dBook = [math]::Round($p.book - $prev.book, 2)
    "=== $now  px=$($p.px) ($dPx)  bull=$($p.bull)/$($p.bear) $($p.state)  proof=$($p.proof) $($p.tier) ==="
    "  cvd=$($p.cvd) ($dCvd)  nd1m=$($p.nd1m) ($dNd1)  book=$($p.book) ($dBook)"
    $mom = 0
    if ($dPx -gt 0) { $mom++ }
    if ($dCvd -gt 0) { $mom++ }
    if ($dNd1 -gt 0) { $mom++ }
    if ($p.bull -ge 3) { $mom++ }
    if ($p.proof -ge 4) { $mom++ }
    "  MOMENTUM $mom/5  (bull>=3, proof>=4, px+, cvd+, nd1m+)"
  }
  $p | ConvertTo-Json -Compress | Set-Content -Path $log -Encoding ascii
  Start-Sleep -Seconds 15
}