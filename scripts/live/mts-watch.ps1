# mts-watch.ps1
# Version: v1.1.3
# Canonical: scripts\live\mts-watch.ps1
# Invoked by: mts-live (see scripts\load.ps1). See MTS_DICTIONARY.md LIVE FEED NAMES.
# 2026-09-17 v1.1.1 - display text reword.
# 2026-09-22 v1.1.2 - wrapper detection falls back to lock PID when command line does not match.
# 2026-09-22 v1.1.3 - added MTS-OID block for T033 fields, plus wrapSrc token on MTS-PROC.
# 2026-09-17 v1.1.0 - added compiled blocks MTS-HSTOP, MTS-PROOF, MTS-CAND, MTS-DELTA.
# 2026-09-17 v1.0.0 - initial console feed.
# Read-only console feed. One block per tick. Also appends to runtime_data\mts-watch.log
# so the operator can paste without a visible window.
# Stop: create runtime_data\mts_watch_stop.flag, or Ctrl-C.

param([int]$IntervalSec = 30)
$ErrorActionPreference = "Continue"
$R = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location $R
$stop = Join-Path $R "runtime_data\mts_watch_stop.flag"
$log  = Join-Path $R "runtime_data\mts-watch.log"
$snapDir = Join-Path $R "runtime_data\snapshots"
$appLog  = Join-Path $R "runtime_data\apparatus_log.txt"
$tapeLog = Join-Path $R "runtime_data\live_tape.md"
$scPath  = Join-Path $R "MyTradingSys\runtime\state_code.json"
$cmsPath = Join-Path $R "MyTradingSys\runtime\current_market_state.md"

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

        $sup  = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" | Where-Object { $_.CommandLine -match 'loop-supervisor' }).ProcessId
        $lockPath = Join-Path $R "runtime_data\apparatus.lock"
        $lock = if (Test-Path $lockPath) { (Get-Content $lockPath -Raw).Trim() } else { "none" }
        $lockPid = if ($lock -match '^(\d+)\s') { [int]$Matches[1] } else { 0 }
        $wrap = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" | Where-Object { $_.CommandLine -match 'start-trading-day|mode\.ps1' -or $_.ProcessId -eq $lockPid }).ProcessId
        $java = @(Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -match 'datafeed\.Main' }).ProcessId
        $wrapSrc = if ($wrap -contains $lockPid) { "lock" } elseif ($wrap.Count -gt 0) { "cmdline" } else { "none" }
        $chain = "sup=$($sup -join '+') wrap=$($wrap -join '+') wrapSrc=$wrapSrc java=$($java -join '+') lock=$lock"
        if ($java.Count -ne 1) { $chain += "  !!! JAVA COUNT=$($java.Count) !!!" }
        if ($sup.Count -ne 1) { $chain += "  !!! SUP COUNT=$($sup.Count) !!!" }
        if ($wrap.Count -ne 1) { $chain += "  !!! WRAP COUNT=$($wrap.Count) !!!" }
        Emit "MTS-PROC    $chain"

        Emit "MTS-SNAP    ts=$($j.timestamp_utc) px=$($j.current_price) vwap=$($j.vwap.price)/$($j.vwap.slope)"
        Emit "MTS-VWAP    +2=$($j.vwap.bands.'+2s') +1=$($j.vwap.bands.'+1s') -1=$($j.vwap.bands.'-1s') -2=$($j.vwap.bands.'-2s')"

        $se = $j.session
        Emit "MTS-SESS open=$($se.open_price) hi=$($se.high) lo=$($se.low) ibH=$($se.initial_balance_high) ibL=$($se.initial_balance_low)"
        Emit "        gap=$($se.gap_from_prior_close)/$($se.gap_direction) loc=$($se.open_location) sweep=$($se.sweep_flag)/$($se.liquidity_sweep_direction)"
        Emit "        day=$($se.day_type)/$($se.day_type_confidence) rpos=$($se.range_position_pct)"

        $cd = $j.conditions
        Emit "MTS-COND    va=$($cd.price_vs_va) poc=$($cd.price_vs_poc) shape=$($cd.vp_shape) vwapSlope=$($cd.vwap_slope) cvdSlope=$($cd.cvd_slope)"
        Emit "        aligned=$($cd.cvd_trade_flow_aligned) book=$($cd.book_imbalance) oi=$($cd.oi_trend) fundX=$($cd.funding_extreme)"
        $f = $cd.fvg_nearest_unfilled
        if ($f) { Emit "        fvg=$($cd.fvg_unfilled_count) nearest=$($f.type) $($f.bottom)-$($f.top)" } else { Emit "        fvg=$($cd.fvg_unfilled_count)" }
        Emit "        speed=$($cd.speed_picking_up) volSpike=$($cd.volume_spike_at_level) rejWick=$($cd.rejection_wick_at_zone)"

        $i = 0
        foreach ($c in ($j.setup_candidates | Select-Object -First 3)) {
            $i++
            Emit "MTS-SET $i   $($c.setup_type)@$($c.zone.name) $($c.zone.price) | nrr $($c.math.net_rr) | proof $($c.score.proof_count) | sub=$($c.math.substate) tier=$($c.math.tier)"
        }

        $sg = $sc.signals
        Emit "MTS-STATE   $($sc.state) bear=$($sc.bearish_count) bull=$($sc.bullish_count) avail=$($sc.available_signals) inState=$($sc.seconds_in_state)s lastTrans=$($sc.last_transition_utc)"
        Emit "        chain=$($sc.transition_chain_15m -join ',')"
        Emit "MTS-SIG     nd1m=$($sg.net_delta_1m) l3=$($sg.last_3_delta) vol=$($sg.volume_ratio) cvd=$($sg.cvd_slope) pxVwap=$($sg.price_vs_vwap)"

        # MTS-FRAME: regime label from regime_classifier.py. Added 2026-09-18.
        $rgPath = Join-Path $R "MyTradingSys\runtime\state_code_regime.json"
        if (Test-Path $rgPath) {
            try {
                $rg = Get-Content $rgPath -Raw -Encoding UTF8 | ConvertFrom-Json
                Emit "MTS-FRAME   label=$($rg.label) conf=$($rg.confidence) cycles=$($rg.consecutive_cycles) entered=$($rg.entered_at_utc)"
            } catch { Emit "MTS-FRAME   read failed: $_" }
        } else { Emit "MTS-FRAME   file missing" }

        $tf = $j.trade_flow
        Emit "MTS-FLOW    cvd=$($j.cvd.value)/$($j.cvd.slope) | ND1m=$($tf.net_delta_1m) ND5m=$($tf.net_delta_5m) ND15m=$($tf.net_delta_15m) ND1h=$($tf.net_delta_1h)"
        Emit "        oi=$($j.open_interest.direction) $($j.open_interest.change_1h_pct)% | fund=$($j.funding.current_rate) | basis=$($j.spot_perp_basis.basis_pct)/$($j.spot_perp_basis.direction)"
        $oi  = $j.open_interest
        $ds  = if ($oi.delta_state)       { $oi.delta_state }       else { "n/a" }
        $dsp = if ($oi.delta_state_price) { $oi.delta_state_price } else { "n/a" }
        Emit "MTS-OID     delta_state=$ds delta_state_price=$dsp dir=$($oi.direction) chg1h=$($oi.change_1h_pct)%"

        # --- COMPILED: hard_stops + proof_direction from build_mo_cli ---
        $moFile = Join-Path $env:TEMP "mts_watch_mo.json"
        try {
            $snapFile = Get-ChildItem (Join-Path $R 'runtime_data\snapshots') -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
            $moCmd = 'python "' + $R + '\MyTradingSys\runtime\build_mo_cli.py" "' + $snapFile.FullName + '" "' + $moFile + '" > NUL 2>&1'
            $null = & cmd.exe /c $moCmd
            if ((Test-Path $moFile) -and (Get-Item $moFile).Length -gt 0) {
                $mo = Get-Content $moFile -Raw -Encoding UTF8 | ConvertFrom-Json
                $hs = $mo.hard_stops_compiled
                Emit "MTS-HSTOP   at a trigger-ready zone: $(-not $hs.price_not_at_zone)"
                Emit "        any zone gross reward-to-risk below 1.5: $($hs.any_zone_rr_below_threshold) | top candidate net reward-to-risk below 2.0: $($hs.top_candidate_rr_below_threshold) | price chasing (all zones ignored): $($hs.chasing_price)"
                Emit "MTS-PROOF   proof direction: $($mo.proof_direction_status)"
                if ($mo.proof_direction_details) { $mo.proof_direction_details | ForEach-Object { Emit "        $_" } }
            }
            Remove-Item $moFile -ErrorAction SilentlyContinue
        } catch { Emit "COMPILED-MO fetch failed: $_" }

        # --- COMPILED: rank-1 candidate ---
        if ($j.setup_candidates -and $j.setup_candidates.Count -gt 0) {
            $top = $j.setup_candidates[0]
            Emit "MTS-CAND    rank-1 $($top.setup_type) $($top.direction) at $($top.zone.name) $($top.zone.price)"
            Emit "        distance $($top.math.distance_pct)% | tier $($top.math.tier) | substate $($top.math.substate) | net reward-to-risk $($top.math.net_rr) | rr_gate $($top.math.net_rr_sanity) | proofs $($top.score.proof_count) | confidence $($top.score.confidence)"
            Emit "        stop $($top.math.stop) | target $($top.math.target) | gross reward-to-risk $($top.math.gross_rr)"
        }

        # --- DELTA vs prior snapshot ---
        try {
            $s2 = Get-ChildItem (Join-Path $R 'runtime_data\snapshots') -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -Skip 1 -First 1
            if ($s2) {
                $j2 = Get-Content $s2.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                $dpx = $j.current_price - $j2.current_price
                $dcvd = $j.cvd.value - $j2.cvd.value
                $dbk = $j.order_book_depth.bid_ask_ratio - $j2.order_book_depth.bid_ask_ratio
                Emit ("MTS-DELTA   price {0:+0.00;-0.00} | cvd {1:+0.000;-0.000} | book {2:+0.00;-0.00}" -f $dpx, $dcvd, $dbk)
            }
        } catch { Emit "DELTA failed: $_" }

        $cycles = Get-Content $appLog -Encoding UTF8 -Tail 12 | Where-Object { $_ -match '\| 20' -and $_ -match ' \| ' }
        Emit "MTS-CYCLES"
        $cycles | Select-Object -Last 3 | ForEach-Object { Emit "        $_" }

        $tapeAge = -1
        if (Test-Path $tapeLog) { $tapeAge = [int]((Get-Date).ToUniversalTime() - (Get-Item $tapeLog).LastWriteTimeUtc).TotalSeconds }
        $t = Get-Content $tapeLog -Tail 1 -ErrorAction SilentlyContinue
        if ($t) {
            if ($tapeAge -gt 120) { Emit "MTS-TAPE    STALE ${tapeAge}s | $t" } else { Emit "MTS-TAPE    age=${tapeAge}s | $t" }
        } else { Emit "MTS-TAPE    no data" }

        $cmsAge = [Math]::Max(0, [int](($now - (Get-Item $cmsPath).LastWriteTimeUtc).TotalSeconds))
        $cmsLines = Get-Content $cmsPath
        $wPoc = ($cmsLines | Select-String '^poc:' | Select-Object -First 1).Line
        $dPoc = ($cmsLines | Select-String '^poc:' | Select-Object -Skip 1 -First 1).Line
        $wVah = ($cmsLines | Select-String '^vah:' | Select-Object -First 1).Line
        $wVal = ($cmsLines | Select-String '^val:' | Select-Object -First 1).Line
        $dVal = ($cmsLines | Select-String '^val:' | Select-Object -Skip 1 -First 1).Line
        Emit "MTS-SLOW    cms_age=${cmsAge}s | weekly $wPoc $wVah $wVal | daily $dPoc $dVal"

        Emit "---"
    } catch {
        Emit "mts-watch read failed: $_"
    }
    Start-Sleep -Seconds $IntervalSec
}
