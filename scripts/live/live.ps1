# MTS live: live - compact per-minute block for chat paste.
# usage:    . .\scripts\load.ps1   then type: live
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

function Fmt($v, $d) { if ($null -eq $v) { "n/a" } else { [math]::Round([double]$v, $d).ToString() } }
function Dlt($a, $b, $d) {
  if ($null -eq $a -or $null -eq $b) { return "n/a" }
  $v = [double]$b - [double]$a
  $s = if ($v -ge 0) { "+" } else { "" }
  return ("{0}{1}" -f $s, [math]::Round($v, $d))
}

$snaps = Get-ChildItem "$root\runtime_data\snapshots\BTCUSDT_*.json" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 2

if (-not $snaps) { "no snapshots"; return }

$new = Get-Content $snaps[0].FullName -Raw | ConvertFrom-Json
$old = if ($snaps.Count -gt 1) { Get-Content $snaps[1].FullName -Raw | ConvertFrom-Json } else { $null }

$sc  = Get-Content "$root\MyTradingSys\runtime\state_code.json" -Raw | ConvertFrom-Json
$log = Get-Content "$root\runtime_data\apparatus_log.txt" -Tail 30 |
  Where-Object { $_ -match "\| \d{4}-\d{2}-\d{2}T" } | Select-Object -Last 1

$tNew = $new.timestamp_utc.Substring(11,8)
$tOld = if ($old) { $old.timestamp_utc.Substring(11,8) } else { "n/a" }

"TIME   $tOld -> $tNew   dt=60s"
"PRICE  {0} -> {1}   ({2})   va={3}  poc={4}" -f `
  (Fmt $old.current_price 2), (Fmt $new.current_price 2), `
  (Dlt $old.current_price $new.current_price 2), `
  $new.conditions.price_vs_va, $new.conditions.price_vs_poc
"VWAP   {0}  slope={1}  d1h={2}" -f (Fmt $new.vwap.price 2), $new.vwap.slope, $new.vwap.slope_pct
"CVD    {0}  slope={1}  1h={2}  4h={3}" -f `
  (Fmt $new.cvd.value 0), $new.cvd.slope, `
  (Fmt $new.cvd.cvd_recent.delta_1h 1), (Fmt $new.cvd.cvd_recent.delta_4h 1)
"ND     1m={0}  5m={1}  15m={2}  1h={3}" -f `
  (Fmt $new.trade_flow.net_delta_1m 1), (Fmt $new.trade_flow.net_delta_5m 1), `
  (Fmt $new.trade_flow.net_delta_15m 1), (Fmt $new.trade_flow.net_delta_1h 1)
"OI     {0}  chg1h={1}%  book={2}  fund={3}  basis={4}%" -f `
  $new.open_interest.direction, (Fmt $new.open_interest.change_1h_pct 3), `
  (Fmt $new.conditions.book_imbalance 2), (Fmt $new.funding.current_rate 7), (Fmt $new.spot_perp_basis.basis_pct 3)
"VA     wk={0}/{1}  dy={2}/{3}  4h={4}/{5}" -f `
  (Fmt $new.weekly_vp.vah 2), (Fmt $new.weekly_vp.val 2), `
  (Fmt $new.daily_vp.vah 2), (Fmt $new.daily_vp.val 2), `
  (Fmt $new.intraday_4h_vp.vah 2), (Fmt $new.intraday_4h_vp.val 2)
"STATE  {0}  B={1}  Bull={2}  secs={3}" -f `
  $sc.state, $sc.bearish_count, $sc.bullish_count, $sc.seconds_in_state
"VERDICT $log"

if ($new.setup_candidates) {
  "TOPSETUP"
  $new.setup_candidates | ForEach-Object {
    "  #{0} {1} @ {2} {3}  nrr={4}  p={5}  conf={6}" -f `
      $_.rank, $_.setup_type, $_.zone.name, (Fmt $_.zone.price 2), `
      (Fmt $_.math.net_rr 2), $_.score.proof_count, $_.score.confidence
  }
}