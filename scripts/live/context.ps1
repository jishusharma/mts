# context.ps1 - rolling 24h per-TF envelope. Read-only. Binance REST.
# usage: . .\scripts\live\context.ps1   (or via load.ps1 as: context)
# slope_word threshold: +/-0.05 pct/hr. Provisional, not Tom-derived.
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$sym  = "BTCUSDT"

function Fmt($v, $d) {
  if ($null -eq $v) { "n/a" } else { [math]::Round([double]$v, $d).ToString() }
}

function Get-Env($interval, $label_hours) {
  $u = "https://fapi.binance.com/fapi/v1/klines?symbol=$sym&interval=$interval&limit=24"
  $k = Invoke-RestMethod $u -TimeoutSec 10
  $highs  = @($k | ForEach-Object { [double]$_[2] })
  $lows   = @($k | ForEach-Object { [double]$_[3] })
  $closes = @($k | ForEach-Object { [double]$_[4] })
  $n = $closes.Count
  if ($n -lt 2) { throw "short kline for $interval" }
  $h = ($highs | Measure-Object -Maximum).Maximum
  $l = ($lows  | Measure-Object -Minimum).Minimum
  $c = $closes[$n-1]
  $span_h = ($n - 1) * ($label_hours / 24.0)
  $slope = ($closes[$n-1] - $closes[0]) / $closes[0] * 100 / $span_h
  $range_pct = ($h - $l) / $c * 100
  $rpos = if (($h - $l) -gt 0) { ($c - $l) / ($h - $l) * 100 } else { 50 }
  $word = if ([math]::Abs($slope) -lt 0.05) { "sideways" } elseif ($slope -gt 0) { "rising" } else { "falling" }
  [pscustomobject]@{
    tf = $interval; hours = $label_hours
    high = $h; low = $l; close = $c
    range_pct = $range_pct
    slope_pct_per_hour = $slope
    range_position_pct = $rpos
    slope_word = $word
  }
}
try {
  $e1 = Get-Env "1h"  24
  $e2 = Get-Env "15m" 6
  $e3 = Get-Env "5m"  2
} catch {
  "context: fetch failed - $_"
  return
}

$now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"CONTEXT  $now   $sym   24-bar envelope"
""
"TF    window  high         low          close        range%  rpos%  slope%/h  trend"
"----  ------  -----------  -----------  -----------  ------  -----  --------  ---------"
foreach ($e in @($e1,$e2,$e3)) {
  $win = "{0}h" -f $e.hours
  "{0,-4}  {1,-6}  {2,11:N2}  {3,11:N2}  {4,11:N2}  {5,6:N2}  {6,5:N1}  {7,8:N3}  {8}" -f $e.tf, $win, $e.high, $e.low, $e.close, $e.range_pct, $e.range_position_pct, $e.slope_pct_per_hour, $e.slope_word
}
