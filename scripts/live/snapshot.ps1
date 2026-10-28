# MTS live: snapshot - one snapshot, all decision fields
# usage:    . .\scripts\load.ps1   then type: snapshot
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$snap = Get-ChildItem "$root\runtime_data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
$j = Get-Content $snap.FullName -Raw | ConvertFrom-Json
"TIME   $($j.timestamp_utc)"
"PRICE  $($j.current_price)  $($j.conditions.price_vs_va)"
"VWAP   $($j.vwap.price)  slope=$($j.vwap.slope)"
"CVD    $([math]::Round($j.cvd.value,1))  slope=$($j.cvd.slope)  1h=$([math]::Round($j.cvd.cvd_recent.delta_1h,1))"
"ND     1m=$([math]::Round($j.trade_flow.net_delta_1m,1))  5m=$([math]::Round($j.trade_flow.net_delta_5m,1))  15m=$([math]::Round($j.trade_flow.net_delta_15m,1))"
"OI     $($j.open_interest.direction)  book=$($j.conditions.book_imbalance)"
"FUND   $($j.funding.current_rate)  basis=$($j.spot_perp_basis.basis_pct)%"
"ZONES  wk VAH $($j.weekly_vp.vah)  dy VAH $($j.daily_vp.vah)  4h VAH $($j.intraday_4h_vp.vah)"
"CANDIDATES:"
$j.setup_candidates | ForEach-Object {
  "  #$($_.rank) $($_.setup_type) @ $($_.zone.name) $($_.zone.price)  nrr=$($_.math.net_rr)  p=$($_.score.proof_count)"
}
