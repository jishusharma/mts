# verify_data.ps1 - data integrity check. Read-only.
# Run: .\scripts\tools\verify_data.ps1
$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
$sd = "$root\runtime_data\snapshots"
$sc = "$root\MyTradingSys\runtime\state_code.json"
$fail = @()
$sf = Get-ChildItem "$sd\BTCUSDT_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$snap = Get-Content $sf.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
"snap: $($sf.Name)  ts=$($snap.timestamp_utc)"
try {
  $k = Invoke-RestMethod "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=60" -TimeoutSec 10
  $ms = ([DateTime]::Parse($snap.timestamp_utc).ToUniversalTime() - [datetime]'1970-01-01').TotalMilliseconds
  $m = $k | Where-Object { [int64]$_[6] -le $ms } | Select-Object -Last 1
  if (-not $m) { throw "no kline for snapshot minute" }
  $bn = [double]$m[4]
  $d = [math]::Abs([double]$snap.current_price - $bn)
  "A: snap=$($snap.current_price)  bn=$bn  diff=$([math]::Round($d,2))"
  if ($d -ge 5) { $fail += "A: diff=$d" }
} catch { "A: err $_" }
$sp = $snap.spot_perp_basis
$c = ($sp.mark_price - $sp.spot_price) / $sp.spot_price * 100
$bd = [math]::Abs($c - $sp.basis_pct)
"B: spot=$($sp.spot_price)  mark=$($sp.mark_price)  rep=$($sp.basis_pct)  calc=$([math]::Round($c,4))  d=$([math]::Round($bd,4))"
if ($bd -ge 0.05) { $fail += "B: basis drift $bd" }
$p = [double]$snap.current_price
$w = $snap.conditions.price_vs_va
$ok = $false
foreach ($n in @('weekly_vp','daily_vp','intraday_4h_vp','post_funding_vp')) {
  $vp = $snap.$n; if (-not $vp) { continue }
  if ($w -eq 'above_vah' -and $p -gt $vp.vah) { $ok = $true }
  if ($w -eq 'below_val' -and $p -lt $vp.val) { $ok = $true }
  if ($w -eq 'in_va' -and $p -ge $vp.val -and $p -le $vp.vah) { $ok = $true }
}
"C: p=$p  w=$w  ok=$ok"
if (-not $ok) { $fail += "C: $w not consistent with any VP" }
$sco = Get-Content $sc -Raw -Encoding UTF8 | ConvertFrom-Json
$age = ([DateTimeOffset]::UtcNow - [DateTime]::Parse($sco.timestamp_utc)).TotalSeconds
"E: age=$([math]::Round($age,1))s  state=$($sco.state)"
if ($age -gt 90) { $fail += "E: age $age > 90" }
""
if ($fail.Count) { "STATUS: FAIL"; $fail; exit 1 } else { "STATUS: PASS" }
