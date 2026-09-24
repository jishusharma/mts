$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$now = (Get-Date).ToUniversalTime()
$s = Get-ChildItem "$R\runtime_data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
$j = Get-Content $s.FullName -Raw | ConvertFrom-Json
$sc = Get-Content "$R\MyTradingSys\runtime\state_code.json" -Raw | ConvertFrom-Json
$rg = Get-Content "$R\MyTradingSys\runtime\state_code_regime.json" -Raw | ConvertFrom-Json
"snap age=$([int]($now - $s.LastWriteTimeUtc).TotalSeconds)s price=$($j.current_price)"
"VA day: poc=$($j.daily_vp.poc) vah=$($j.daily_vp.vah) val=$($j.daily_vp.val)"
"VA 4h:  poc=$($j.intraday_4h_vp.poc) vah=$($j.intraday_4h_vp.vah) val=$($j.intraday_4h_vp.val)"
"VA pd:  poc=$($j.prior_day.poc) vah=$($j.prior_day.vah) val=$($j.prior_day.val)"
"VWAP $($j.vwap.price)/$($j.vwap.slope) -1s=$($j.vwap.bands.'-1s') -2s=$($j.vwap.bands.'-2s')"
"cvd=$($j.cvd.value)/$($j.cvd.slope) last3=[$($j.cvd.last_3_delta -join ',')] cvd1h_s=$($j.cvd.cvd_recent.slope_1h) cvd1h_d=$($j.cvd.cvd_recent.delta_1h)"
"nd 1m=$($j.trade_flow.net_delta_1m) 5m=$($j.trade_flow.net_delta_5m) 15m=$($j.trade_flow.net_delta_15m) 1h=$($j.trade_flow.net_delta_1h)"
"oi=$($j.open_interest.direction)/$($j.open_interest.change_1h_pct)% book=$($j.order_book_depth.bid_ask_ratio) fund=$($j.funding.current_rate) basis=$($j.spot_perp_basis.basis_pct)"
"tps=$($j.order_flow.trades_per_sec) speed=$($j.order_flow.speed_state) ratio=$($j.order_flow.trades_ratio) hist=$($j.order_flow.speed_vs_historical)"
"oibrk retail=$($j.oi_breakdown.retail.long_short_ratio) whale=$($j.oi_breakdown.whale.long_short_ratio) top=$($j.oi_breakdown.topAccounts.long_short_ratio)"
"struct 1h=$($j.structure.'1h'.swing_low)/$($j.structure.'1h'.swing_high) 15m=$($j.structure.'15m'.swing_low)/$($j.structure.'15m'.swing_high) 5m=$($j.structure.'5m'.swing_low)/$($j.structure.'5m'.swing_high)"
"state=$($sc.state) b=$($sc.bearish_count)/$($sc.bullish_count) inState=$($sc.seconds_in_state)s nd1m=$($sc.signals.net_delta_1m) cvd=$($sc.signals.cvd_slope) pxVwap=$($sc.signals.price_vs_vwap)"
"regime=$($rg.label) conf=$($rg.confidence) cyc=$($rg.consecutive_cycles)"
"--- setups ---"
$j.setup_candidates | ForEach-Object {
  $p=$_.proof
  "r$($_.rank) $($_.setup_type)@$($_.zone.name) $($_.zone.price) tier=$($_.math.tier) sub=$($_.math.substate) nrr=$($_.math.net_rr) p=$($_.score.proof_count) stop=$($_.math.stop) tgt=$($_.math.target) rw=$($p.rejection_wick) fa=$($p.finished_auction.detected)/$($p.finished_auction.direction) df=$($p.delta_flip.detected) spd=$($p.speed.picking_up)/$($p.speed.score)"
}
"--- last 3 verdicts ---"
Get-Content "$R\runtime_data\apparatus_log.txt" | Where-Object { $_ -match "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| \d{4}-" } | Select -Last 3