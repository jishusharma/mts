# mts-watch.ps1
# Read-only console feed. One block per tick. Also appends to data\mts-watch.log
# so the operator can paste without a visible window.
# Stop: create data\mts_watch_stop.flag, or Ctrl-C.

param([int]$IntervalSec = 30)
$ErrorActionPreference = "Continue"
$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Set-Location $R
$stop = Join-Path $R "data\mts_watch_stop.flag"
$log  = Join-Path $R "data\mts-watch.log"
$snapDir = Join-Path $R "data\snapshots"
$appLog  = Join-Path $R "data\apparatus_log.txt"
$tapeLog = Join-Path $R "data\live_tape.md"
$scPath  = Join-Path $R "MyTradingSys\mts\runtime\state_code.json"
$cmsPath = Join-Path $R "MyTradingSys\mts\runtime\current_market_state.md"

function Emit {
    param([string]$text)
    Write-Host $text
    Add-Content -LiteralPath $log -Value $text -Encoding ASCII
}

if (-not (Test-Path $log)) {
    "# mts-watch.log - appended every tick" | Set-Content -Path $log -Encoding ASCII
}

while ($true) {
    if (Test-Path $stop) { Emit "mts-watch: stop flag, exiting"; break }
    try {
        $now = [DateTime]::UtcNow
        $s = Get-ChildItem "$snapDir\BTCUSDT_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $snapAge = [int](($now - $s.LastWriteTimeUtc).TotalSeconds)
        $j = Get-Content $s.FullName -Raw | ConvertFrom-Json
        $sc = Get-Content $scPath -Raw | ConvertFrom-Json

        Emit "=== $($now.ToString('o')) | snap_age=${snapAge}s ==="

        $sup  = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -match 'loop-supervisor' }).ProcessId
        $wrap = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -match 'start-trading-day' }).ProcessId
        $java = @(Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -match 'datafeed\.Main' }).ProcessId
        $lockPath = Join-Path $R "data\apparatus.lock"
        $lock = if (Test-Path $lockPath) { (Get-Content $lockPath -Raw).Trim() } else { "none" }
        $chain = "sup=$($sup -join '+') wrap=$($wrap -join '+') java=$($java -join '+') lock=$lock"
        if ($java.Count -ne 1) { $chain += "  !!! JAVA COUNT=$($java.Count) !!!" }
        if ($sup.Count -ne 1) { $chain += "  !!! SUP COUNT=$($sup.Count) !!!" }
        if ($wrap.Count -ne 1) { $chain += "  !!! WRAP COUNT=$($wrap.Count) !!!" }
        Emit "PROC    $chain"

        Emit "SNAP    ts=$($j.timestamp_utc) px=$($j.current_price) vwap=$($j.vwap.price)/$($j.vwap.slope)"
        Emit "VWAP    +2=$($j.vwap.bands.'+2s') +1=$($j.vwap.bands.'+1s') -1=$($j.vwap.bands.'-1s') -2=$($j.vwap.bands.'-2s')"

        $se = $j.session
        Emit "SESSION open=$($se.open_price) hi=$($se.high) lo=$($se.low) ibH=$($se.initial_balance_high) ibL=$($se.initial_balance_low)"
        Emit "        gap=$($se.gap_from_prior_close)/$($se.gap_direction) loc=$($se.open_location) sweep=$($se.sweep_flag)/$($se.liquidity_sweep_direction)"
        Emit "        day=$($se.day_type)/$($se.day_type_confidence) rpos=$($se.range_position_pct)"

        $cd = $j.conditions
        Emit "COND    va=$($cd.price_vs_va) poc=$($cd.price_vs_poc) shape=$($cd.vp_shape) vwapSlope=$($cd.vwap_slope) cvdSlope=$($cd.cvd_slope)"
        Emit "        aligned=$($cd.cvd_trade_flow_aligned) book=$($cd.book_imbalance) oi=$($cd.oi_trend) fundX=$($cd.funding_extreme)"
        $f = $cd.fvg_nearest_unfilled
        if ($f) { Emit "        fvg=$($cd.fvg_unfilled_count) nearest=$($f.type) $($f.bottom)-$($f.top)" } else { Emit "        fvg=$($cd.fvg_unfilled_count)" }
        Emit "        speed=$($cd.speed_picking_up) volSpike=$($cd.volume_spike_at_level) rejWick=$($cd.rejection_wick_at_zone)"

        $i = 0
        foreach ($c in ($j.setup_candidates | Select-Object -First 3)) {
            $i++
            Emit "SET $i   $($c.setup_type)@$($c.zone.name) $($c.zone.price) | nrr $($c.math.net_rr) | proof $($c.score.proof_count) | sub=$($c.math.substate) tier=$($c.math.tier)"
        }

        $sg = $sc.signals
        Emit "STATE   $($sc.state) bear=$($sc.bearish_count) bull=$($sc.bullish_count) avail=$($sc.available_signals) inState=$($sc.seconds_in_state)s lastTrans=$($sc.last_transition_utc)"
        Emit "        chain=$($sc.transition_chain_15m -join ',')"
        Emit "SIG     nd1m=$($sg.net_delta_1m) l3=$($sg.last_3_delta) vol=$($sg.volume_ratio) cvd=$($sg.cvd_slope) pxVwap=$($sg.price_vs_vwap)"

        $tf = $j.trade_flow
        Emit "FLOW    cvd=$($j.cvd.value)/$($j.cvd.slope) | ND1m=$($tf.net_delta_1m) ND5m=$($tf.net_delta_5m) ND15m=$($tf.net_delta_15m) ND1h=$($tf.net_delta_1h)"
        Emit "        oi=$($j.open_interest.direction) $($j.open_interest.change_1h_pct)% | fund=$($j.funding.current_rate) | basis=$($j.spot_perp_basis.basis_pct)/$($j.spot_perp_basis.direction)"

        $cycles = Get-Content $appLog -Encoding UTF8 -Tail 12 | Where-Object { $_ -match '\| 20' -and $_ -match ' \| ' }
        Emit "CYCLES"
        $cycles | Select-Object -Last 3 | ForEach-Object { Emit "        $_" }

        $t = Get-Content $tapeLog -Tail 1 -ErrorAction SilentlyContinue
        if ($t) { Emit "TAPE    $t" }

        $cmsAge = [int](($now - (Get-Item $cmsPath).LastWriteTimeUtc).TotalSeconds)
        $cmsLines = Get-Content $cmsPath
        $wPoc = ($cmsLines | Select-String '^poc:' | Select-Object -First 1).Line
        $dPoc = ($cmsLines | Select-String '^poc:' | Select-Object -Skip 1 -First 1).Line
        $wVah = ($cmsLines | Select-String '^vah:' | Select-Object -First 1).Line
        $wVal = ($cmsLines | Select-String '^val:' | Select-Object -First 1).Line
        $dVal = ($cmsLines | Select-String '^val:' | Select-Object -Skip 1 -First 1).Line
        Emit "SLOW    cms_age=${cmsAge}s | weekly $wPoc $wVah $wVal | daily $dPoc $dVal"

        Emit "---"
    } catch {
        Emit "mts-watch read failed: $_"
    }
    Start-Sleep -Seconds $IntervalSec
}
