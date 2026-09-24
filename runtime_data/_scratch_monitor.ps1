# ad-hoc live monitor. Ctrl-C to stop. Log: runtime_data\live_monitor.txt
$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Set-Location $R
$log = Join-Path $R "runtime_data\live_monitor.txt"
$lastSnap = ""
while ($true) {
  $now = (Get-Date).ToUniversalTime()
  $s = Get-ChildItem "$R\runtime_data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
  if (-not $s) { Start-Sleep -Seconds 10; continue }
  if ($s.Name -eq $lastSnap) { Start-Sleep -Seconds 10; continue }
  $lastSnap = $s.Name
  $j = Get-Content $s.FullName -Raw | ConvertFrom-Json
  $sc = Get-Content "$R\MyTradingSys\runtime\state_code.json" -Raw | ConvertFrom-Json
  $rg = Get-Content "$R\MyTradingSys\runtime\state_code_regime.json" -Raw | ConvertFrom-Json
  $vdt = Get-Content "$R\runtime_data\apparatus_log.txt" | Where-Object { $_ -match "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| \d{4}-" } | Select -Last 3
  $out = @()
  $out += "=== " + $now.ToString("HH:mm:ss") + "Z snapAge=$([int]($now-$s.LastWriteTimeUtc).TotalSeconds)s px=$($j.current_price) ==="
  $out += "va  wk $($j.weekly_vp.val)/$($j.weekly_vp.vah) | dy $($j.daily_vp.val)/$($j.daily_vp.vah) poc=$($j.daily_vp.poc) | 4h $($j.intraday_4h_vp.val)/$($j.intraday_4h_vp.vah) | pf $($j.post_funding_vp.val)/$($j.post_funding_vp.vah) | pd $($j.prior_day.val)/$($j.prior_day.vah) poc=$($j.prior_day.poc)"
  $out += "vw  $($j.vwap.price)/$($j.vwap.slope) -1s=$($j.vwap.bands.'-1s') +1s=$($j.vwap.bands.'+1s') -2s=$($j.vwap.bands.'-2s')"
  $out += "fl  cvd=$($j.cvd.value)/$($j.cvd.slope) last3=[$($j.cvd.last_3_delta -join [char]44)] 1h_s=$($j.cvd.cvd_recent.slope_1h) 4h_s=$($j.cvd.cvd_recent.slope_4h)"
  $out += "nd  1m=$($j.trade_flow.net_delta_1m) 5m=$($j.trade_flow.net_delta_5m) 15m=$($j.trade_flow.net_delta_15m) 1h=$($j.trade_flow.net_delta_1h)"
  $out += "oi  $($j.open_interest.direction)/$($j.open_interest.change_1h_pct)% fund=$($j.funding.current_rate) basis=$($j.spot_perp_basis.basis_pct)/$($j.spot_perp_basis.direction) book=$($j.order_book_depth.bid_ask_ratio)"
  $out += "sp  tps=$($j.order_flow.trades_per_sec) speed=$($j.order_flow.speed_state) ratio=$($j.order_flow.trades_ratio) hist=$($j.order_flow.speed_vs_historical)"
  $out += "oib retail=$($j.oi_breakdown.retail.long_short_ratio) whale=$($j.oi_breakdown.whale.long_short_ratio) top=$($j.oi_breakdown.topAccounts.long_short_ratio)"
  $out += "str 1h $($j.structure.'1h'.swing_low)/$($j.structure.'1h'.swing_high) | 15m $($j.structure.'15m'.swing_low)/$($j.structure.'15m'.swing_high) | 5m $($j.structure.'5m'.swing_low)/$($j.structure.'5m'.swing_high)"
  $out += "sig $($sc.state) b=$($sc.bearish_count)/$($sc.bullish_count) inState=$($sc.seconds_in_state)s | nd1m=$($sc.signals.net_delta_1m) l3=$($sc.signals.last_3_delta) vol=$($sc.signals.volume_ratio) cvd=$($sc.signals.cvd_slope) pxVwap=$($sc.signals.price_vs_vwap)"
  $out += "rg  $($rg.label) conf=$($rg.confidence) cyc=$($rg.consecutive_cycles)"
  $out += "set"
  $j.setup_candidates | ForEach-Object { $out += "    r$($_.rank) $($_.setup_type)@$($_.zone.name) $($_.zone.price) tier=$($_.math.tier) sub=$($_.math.substate) nrr=$($_.math.net_rr) p=$($_.score.proof_count) stop=$($_.math.stop) tgt=$($_.math.target)" }
  $out += "vdt"
  foreach ($v in $vdt) { $out += "    $v" }
  $out += ""
  $out | ForEach-Object { Write-Host $_ }
  $out | Out-File -FilePath $log -Encoding ascii -Append
  Start-Sleep -Seconds 15
}