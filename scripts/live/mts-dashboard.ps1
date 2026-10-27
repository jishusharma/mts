# mts-dashboard.ps1
# Version: v1.2.0
# v1.2.0 - 4-column layout, fixed table widths, lighter greys, color on data only.
# v1.1.0 - ASCII tables, colored decision banner and GATE cells, wide layout.
# v1.0.0 - initial one-shot dashboard.
# One-shot. No loop. Invoked by: mts-dashboard.
param([switch]$Watch)
$ErrorActionPreference = "Continue"
$R = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location $R
do {
if ($Watch) { Clear-Host }
$now = [DateTime]::UtcNow
try { $tw = [Console]::WindowWidth } catch { $tw = 132 }
$W = if ($tw -lt 132) { $tw } else { 132 }

$C_LABEL = "Gray"
$C_VALUE = "White"
$C_SECT  = "Cyan"
$C_OK    = "Green"
$C_BAD   = "Red"
$C_WARN  = "Yellow"

function SecHead { param([string]$t)
    $prefix = "-- $t "
    $fill = $W - $prefix.Length - 1
    if ($fill -lt 3) { $fill = 3 }
    Write-Host $prefix -NoNewline -ForegroundColor $C_SECT
    Write-Host ("-" * $fill) -ForegroundColor $C_SECT
}
function Row { param([string]$l,[string]$v,[int]$lw=12,[int]$vw=22,[string]$vc="White")
    Write-Host ("  " + $l.PadRight($lw)) -NoNewline -ForegroundColor $C_LABEL
    Write-Host ($v.PadRight($vw)) -NoNewline -ForegroundColor $vc
}

$snapFile = Get-ChildItem (Join-Path $R "runtime_data\snapshots") -Filter "BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
$snapAge = [int](($now - $snapFile.LastWriteTimeUtc).TotalSeconds)
$j = Get-Content $snapFile.FullName -Raw | ConvertFrom-Json
$sc = Get-Content (Join-Path $R "MyTradingSys\runtime\state_code.json") -Raw | ConvertFrom-Json

$moFile = Join-Path $env:TEMP "mts_dash_mo.json"
$null = & python "$R\MyTradingSys\runtime\build_mo_cli.py" "$($snapFile.FullName)" "$moFile" 2>&1 | Out-Null
$mo = if (Test-Path $moFile) { Get-Content $moFile -Raw -Encoding UTF8 | ConvertFrom-Json } else { $null }
Remove-Item $moFile -ErrorAction SilentlyContinue
$hs = if ($mo) { $mo.hard_stops_compiled } else { $null }

$sup  = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" | Where-Object { $_.CommandLine -match "loop-supervisor" }).ProcessId
$wrap = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" | Where-Object { $_.CommandLine -match "start-trading-day|mode\.ps1" }).ProcessId
$java = @(Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -match "datafeed\.Main" }).ProcessId
$lockPath = Join-Path $R "runtime_data\apparatus.lock"
$lock = if (Test-Path $lockPath) { (Get-Content $lockPath -Raw).Trim() } else { "none" }

$cycAll = Get-Content (Join-Path $R "runtime_data\apparatus_log.txt") -Encoding UTF8 -Tail 12 | Where-Object { $_ -match "\| 20" -and $_ -match " \| " }
$lastCycle = if ($cycAll) { $cycAll[-1] } else { "" }

# HEADER
Write-Host ("=" * $W) -ForegroundColor $C_SECT
$h1 = "  MTS DASHBOARD   " + $now.ToString("yyyy-MM-dd HH:mm:ss") + " UTC   snapshot " + $snapAge + "s"
Write-Host $h1 -ForegroundColor $C_VALUE
$h2 = "  State " + $sc.state + "   in " + $sc.seconds_in_state + "s   last " + $sc.last_transition_utc + "   bear " + $sc.bearish_count + "   bull " + $sc.bullish_count + "   avail " + $sc.available_signals
Write-Host $h2 -ForegroundColor $C_VALUE
$h3 = "  sup " + ($sup -join "+") + "   wrap " + ($wrap -join "+") + "   java " + ($java -join "+") + "   lock " + $lock
Write-Host $h3 -ForegroundColor $C_LABEL
Write-Host ("=" * $W) -ForegroundColor $C_SECT

# DECISION
$top = $j.setup_candidates[0]
$verdictWord = "UNKNOWN"; $reason = ""; $waitKind = "OTHER"
$vparts = $lastCycle -split ' \| '
$validWords = @("WATCH","WAIT_RR","WAIT_TRIGGER","WAIT_PROOF","WAIT_FAR","SETUP_FORMING","SETUP_CONFIRMED")
if ($vparts.Count -ge 5) {
    $candidate = ($vparts[4] -replace '\s*\(.*$', '').Trim()
    if ($validWords -contains $candidate) { $verdictWord = $candidate } else { $verdictWord = "UNKNOWN"; $reason = "parse mismatch: " + $vparts[4] }
}
if ($verdictWord -eq "") { $verdictWord = "UNKNOWN" }
if ($lastCycle -match 'WAIT_RR \(net_rr ([\d\.]+) < ([\d\.]+)\)') { $reason = "net reward to risk " + $matches[1] + " below the " + $matches[2] + " gate"; $waitKind = "RR" }
elseif ($lastCycle -match 'WAIT_TRIGGER \(price not at zone\)') { $reason = "price not at zone"; $waitKind = "TRIGGER" }
elseif ($verdictWord -eq "WATCH") { $reason = "setup being watched"; $waitKind = "WATCH" }
elseif ($verdictWord -eq "SETUP_FORMING") { $reason = "setup forming"; $waitKind = "FORMING" }
elseif ($verdictWord -eq "SETUP_CONFIRMED") { $reason = "setup confirmed"; $waitKind = "CONFIRMED" }
else { $reason = $lastCycle; $waitKind = "OTHER" }
$bannerColor = $C_WARN
if ($verdictWord -eq "SETUP_CONFIRMED") { $bannerColor = $C_OK }
Write-Host "  [ " -NoNewline -ForegroundColor $bannerColor
Write-Host $verdictWord -NoNewline -ForegroundColor $bannerColor
Write-Host " ]  " -NoNewline -ForegroundColor $bannerColor
Write-Host $reason -ForegroundColor $C_VALUE

$distAbs = [math]::Abs([math]::Round([double]$j.current_price - [double]$top.zone.price, 1))
$unblock = "wait"
if ($waitKind -eq "RR") { $unblock = "net reward to risk must rise above 2.0" }
elseif ($waitKind -eq "TRIGGER") { $unblock = "price must reach the zone" }
elseif ($waitKind -eq "OTHER") { $unblock = "wait" }
Write-Host "  Setup      " -NoNewline -ForegroundColor $C_LABEL
Write-Host ($top.setup_type + " @ " + $top.zone.name + " " + $top.zone.price).PadRight(40) -NoNewline -ForegroundColor $C_VALUE
Write-Host "Unblock    " -NoNewline -ForegroundColor $C_LABEL
Write-Host $unblock -ForegroundColor $C_VALUE
Write-Host "  Price      " -NoNewline -ForegroundColor $C_LABEL
Write-Host ([string]$j.current_price).PadRight(11) -NoNewline -ForegroundColor $C_VALUE
Write-Host "Distance   " -NoNewline -ForegroundColor $C_LABEL
Write-Host ($distAbs.ToString() + " pts (" + $top.math.distance_pct + "%)") -ForegroundColor $C_VALUE
Write-Host ""

# TRADES
SecHead "TRADES IN ORDER OF BEST TO WORST"
Write-Host "  +------+-------------+-----------------------+-------+---------+--------+------+-----------+" -ForegroundColor $C_LABEL
Write-Host "  | RANK | SETUP       | ZONE                  | DIST  | NET R:R | PROOFS | GATE | DIRECTION |" -ForegroundColor $C_LABEL
Write-Host "  +------+-------------+-----------------------+-------+---------+--------+------+-----------+" -ForegroundColor $C_LABEL
$i = 0
foreach ($c in ($j.setup_candidates | Select-Object -First 5)) {
    $i++
    $rk = ([string]$i).PadRight(5)
    $st = $c.setup_type.PadRight(12)
    $zn = (("{0} {1}" -f $c.zone.name, $c.zone.price)).PadRight(22)
    $dp = (([string]$c.math.distance_pct) + "%").PadRight(6)
    $nr = ([string]$c.math.net_rr).PadRight(8)
    $pf = ([string]$c.score.proof_count).PadRight(7)
    $dr = ([string]$c.direction).PadRight(9)
    $isRank1 = ($i -eq 1)
    $gt = "-"
    $gc = $C_LABEL
    if ($isRank1) {
        $gt = $verdictWord
        if ($verdictWord -eq "SETUP_CONFIRMED") { $gc = $C_OK } else { $gc = $C_WARN }
    }
    Write-Host "  | " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $rk -NoNewline -ForegroundColor $C_VALUE
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $st -NoNewline -ForegroundColor $C_VALUE
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $zn -NoNewline -ForegroundColor $C_VALUE
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $dp -NoNewline -ForegroundColor $C_VALUE
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $nr -NoNewline -ForegroundColor $C_VALUE
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $pf -NoNewline -ForegroundColor $C_VALUE
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $gt -NoNewline -ForegroundColor $gc
    Write-Host "| " -NoNewline -ForegroundColor $C_LABEL
    Write-Host $dr -NoNewline -ForegroundColor $C_VALUE
    Write-Host " |" -ForegroundColor $C_LABEL
}
Write-Host "  +------+-------------+-----------------------+-------+---------+--------+------+-----------+" -ForegroundColor $C_LABEL
Write-Host ("  Engine says: " + $verdictWord + ". " + $reason) -ForegroundColor $C_WARN
Write-Host ""

# 4-COLUMN GRID
$cvdC  = if ($j.cvd.slope -eq "rising") { $C_OK } else { $C_BAD }
$nd1m  = if ([double]$j.trade_flow.net_delta_1m  -ge 0) { $C_OK } else { $C_BAD }
$nd5m  = if ([double]$j.trade_flow.net_delta_5m  -ge 0) { $C_OK } else { $C_BAD }
$nd15m = if ([double]$j.trade_flow.net_delta_15m -ge 0) { $C_OK } else { $C_BAD }
$nd1h  = if ([double]$j.trade_flow.net_delta_1h  -ge 0) { $C_OK } else { $C_BAD }
$bkC   = if ($j.order_book_depth.bid_ask_ratio -gt 1) { $C_OK } else { $C_BAD }
$oiC   = if ($j.open_interest.direction -eq "rising") { $C_OK } else { $C_BAD }
$bookDir = if ($j.order_book_depth.bid_ask_ratio -gt 1) { "bid-heavy" } else { "ask-heavy" }
$mkt = @(
  @("Price",     [string]$j.current_price, $C_VALUE),
  @("VWAP",      ("{0} {1}" -f $j.vwap.price, $j.vwap.slope), $C_VALUE),
  @("Shape",     [string]$j.conditions.vp_shape, $C_VALUE),
  @("Position",  [string]$j.conditions.price_vs_va, $C_VALUE),
  @("Day type",  ("{0} {1}" -f $j.session.day_type, $j.session.day_type_confidence), $C_VALUE),
  @("Range pos", ("{0}%" -f $j.session.range_position_pct), $C_VALUE),
  @("Sess hi/lo",("{0}/{1}" -f $j.session.high, $j.session.low), $C_VALUE),
  @("Sweep",     ("{0} {1}" -f $j.session.sweep_flag, $j.session.liquidity_sweep_direction), $C_WARN)
)
$flw = @(
  @("CVD",       ("{0} {1}" -f $j.cvd.value, $j.cvd.slope), $cvdC),
  @("Delta 1m",  [string]$j.trade_flow.net_delta_1m,  $nd1m),
  @("Delta 5m",  [string]$j.trade_flow.net_delta_5m,  $nd5m),
  @("Delta 15m", [string]$j.trade_flow.net_delta_15m, $nd15m),
  @("Delta 1h",  [string]$j.trade_flow.net_delta_1h,  $nd1h),
  @("Book",      ("{0} {1}" -f $j.order_book_depth.bid_ask_ratio, $bookDir), $bkC),
  @("OI",        ("{0} {1}%" -f $j.open_interest.direction, $j.open_interest.change_1h_pct), $oiC),
  @("Basis",     ("{0} {1}" -f $j.spot_perp_basis.basis_pct, $j.spot_perp_basis.direction), $C_VALUE)
)
$lvl = @(
  @("Weekly VAH",[string]$j.weekly_vp.vah,    $C_VALUE),
  @("Daily VAH", [string]$j.daily_vp.vah,     $C_VALUE),
  @("4h VAH",    [string]$j.intraday_4h_vp.vah,$C_VALUE),
  @("Daily POC", [string]$j.daily_vp.poc,     $C_VALUE),
  @("VWAP",      [string]$j.vwap.price,       $C_VALUE),
  @("Daily VAL", [string]$j.daily_vp.val,     $C_VALUE),
  @("Sess low",  [string]$j.session.low,      $C_VALUE),
  @("Prior POC", [string]$j.prior_day.poc,    $C_VALUE)
)
$wtc = @(
  @("W1", ("{0} {1}" -f $top.zone.name, $top.zone.price), $C_VALUE),
  @("W2", "book flips often, do not trust", $C_WARN),
  @("W3", ("CVD {0} {1}" -f $j.cvd.value, $j.cvd.slope), $cvdC)
)
if ($j.setup_candidates.Count -gt 1) { $wtc = @( @("W1", ("{0} {1}" -f $j.setup_candidates[0].zone.name, $j.setup_candidates[0].zone.price), $C_VALUE), @("W2", ("{0} {1}" -f $j.setup_candidates[1].zone.name, $j.setup_candidates[1].zone.price), $C_VALUE), @("W3", "book flips often", $C_WARN), @("W4", ("CVD {0} {1}" -f $j.cvd.value, $j.cvd.slope), $cvdC) ) }

Write-Host "  " -NoNewline -ForegroundColor $C_SECT
Write-Host ("MARKET".PadRight(33)) -NoNewline -ForegroundColor $C_SECT
Write-Host ("FLOW".PadRight(35)) -NoNewline -ForegroundColor $C_SECT
Write-Host ("LEVELS".PadRight(34)) -NoNewline -ForegroundColor $C_SECT
Write-Host "WATCH" -ForegroundColor $C_SECT
$rows = [Math]::Max($mkt.Count, [Math]::Max($flw.Count, [Math]::Max($lvl.Count, $wtc.Count)))
for ($k = 0; $k -lt $rows; $k++) {
    Write-Host "  " -NoNewline
    if ($k -lt $mkt.Count) {
        Write-Host ($mkt[$k][0].PadRight(11)) -NoNewline -ForegroundColor $C_LABEL
        Write-Host ($mkt[$k][1].PadRight(22)) -NoNewline -ForegroundColor $mkt[$k][2]
    } else { Write-Host (" " * 33) -NoNewline }
    if ($k -lt $flw.Count) {
        Write-Host ($flw[$k][0].PadRight(11)) -NoNewline -ForegroundColor $C_LABEL
        Write-Host ($flw[$k][1].PadRight(24)) -NoNewline -ForegroundColor $flw[$k][2]
    } else { Write-Host (" " * 35) -NoNewline }
    if ($k -lt $lvl.Count) {
        Write-Host ($lvl[$k][0].PadRight(12)) -NoNewline -ForegroundColor $C_LABEL
        Write-Host ($lvl[$k][1].PadRight(22)) -NoNewline -ForegroundColor $lvl[$k][2]
    } else { Write-Host (" " * 34) -NoNewline }
    if ($k -lt $wtc.Count) {
        Write-Host ($wtc[$k][0].PadRight(4)) -NoNewline -ForegroundColor $C_LABEL
        Write-Host $wtc[$k][1].PadRight(22) -ForegroundColor $wtc[$k][2]
    } else { Write-Host "" }
}
Write-Host ""

# PREPARE
SecHead "PREPARE (engine gate is rank-1 net R:R above 2.0; proof count not a gate input)"
foreach ($c in ($j.setup_candidates | Select-Object -First 3)) {
    Write-Host "  " -NoNewline
    Write-Host ($c.setup_type.PadRight(13)) -NoNewline -ForegroundColor $C_VALUE
    Write-Host ("@ " + $c.zone.name.PadRight(14)) -NoNewline -ForegroundColor $C_VALUE
    Write-Host ("Entry " + ([string]$c.zone.price).PadRight(12)) -NoNewline -ForegroundColor $C_LABEL
    Write-Host ("Stop " + ([string]$c.math.stop).PadRight(12)) -NoNewline -ForegroundColor $C_LABEL
    Write-Host ("Target " + [string]$c.math.target) -ForegroundColor $C_LABEL
}
Write-Host ""

# LEGEND
Write-Host ("=" * $W) -ForegroundColor $C_SECT
Write-Host "  VAH value area high | VAL value area low | POC point of control | VWAP volume weighted avg | CVD cumulative volume delta | FVG fair value gap | R:R reward to risk" -ForegroundColor $C_LABEL
Write-Host ("=" * $W) -ForegroundColor $C_SECT
if ($Watch) { Start-Sleep -Seconds 30 }
} while ($Watch)
