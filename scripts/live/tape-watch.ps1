# tape-watch.ps1
# Sidecar divergence watcher. Popup on non-neutral. Read-only on loop.

param([int]$IntervalSec = 30, [int]$PopCooldownSec = 180)
$ErrorActionPreference = "Continue"
$R = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location $R
$out     = Join-Path $R "runtime_data\live_tape.md"
$stop    = Join-Path $R "runtime_data\tape_stop.flag"
$alertJs = Join-Path $R "runtime_data\last_tape_alert.json"
$alertPs = Join-Path $R "scripts\core\show-alert.ps1"
if (-not (Test-Path $out)) {
    "# LIVE TAPE" | Set-Content -Path $out -Encoding ASCII
    "# ts | price | dPx | dCVD | dND5m | dOI | state | setup nrr | divergence" | Add-Content -Path $out -Encoding ASCII
    "" | Add-Content -Path $out -Encoding ASCII
}
$prev = $null
$popAt = @{}
$tickN = 0
$lastSnap = $null
$histN = 40
if (Test-Path $out) {
    Write-Host "--- last $histN tape lines (about 40 minutes) ---"
    Get-Content $out -Tail $histN | ForEach-Object { Write-Host $_ }
    Write-Host "--- live ---"
}

while ($true) {
    if (Test-Path $stop) { "tape-watch: stop"; break }
    try {
        $s = Get-ChildItem "$R\runtime_data\snapshots\BTCUSDT_*.json" -ErrorAction Stop |
             Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($lastSnap -and $s.FullName -eq $lastSnap) {
            Start-Sleep -Seconds $IntervalSec
            continue
        }
        $lastSnap = $s.FullName
        $j = Get-Content $s.FullName -Raw | ConvertFrom-Json
        $sc = Get-Content "$R\MyTradingSys\runtime\state_code.json" -Raw | ConvertFrom-Json
        $top = $j.setup_candidates | Select-Object -First 1
        $row = [ordered]@{
            ts = $j.timestamp_utc
            price = [double]$j.current_price
            cvd = [double]$j.cvd.value
            nd5m = [double]$j.trade_flow.net_delta_5m
            oi_pct = [double]$j.open_interest.change_1h_pct
            state = [string]$sc.state
            setup = if ($top) { "$($top.setup_type)@$($top.zone.name)" } else { "none" }
            nrr = if ($top) { [double]$top.math.net_rr } else { 0 }
        }
        if ($prev) {
            $dPx = $row.price - $prev.price
            $dCvd = $row.cvd - $prev.cvd
            $dNd5 = $row.nd5m - $prev.nd5m
            $dOi = $row.oi_pct - $prev.oi_pct
            $pxUp = $dPx -gt 2; $pxDn = $dPx -lt -2
            $cvdUp = $dCvd -gt 5; $cvdDn = $dCvd -lt -5
            $oiUp = $dOi -gt 0.02; $oiDn = $dOi -lt -0.02
            if     ($pxUp -and $cvdDn) { $div = "bearish_div" }
            elseif ($pxDn -and $cvdUp) { $div = "bullish_div" }
            elseif ($pxUp -and $cvdUp -and $oiUp) { $div = "confirm_up_long" }
            elseif ($pxDn -and $cvdDn -and $oiUp) { $div = "confirm_down_short" }
            elseif ($pxUp -and $oiDn) { $div = "short_cover" }
            elseif ($pxDn -and $oiDn) { $div = "long_liquidate" }
            else { $div = "neutral" }
            $line = "{0} | {1} | dPx {2:+0.0;-0.0;0} | dCVD {3:+0;-0;0} | dND5m {4:+0;-0;0} | dOI {5:+0.00;-0.00;0.00} | {6} | {7} nrr {8:N2} | {9}" -f `
                $row.ts, $row.price, $dPx, $dCvd, $dNd5, $dOi, $row.state, $row.setup, $row.nrr, $div
            Write-Host $line
            Add-Content -Path $out -Value $line -Encoding ASCII
            if ($div -ne "neutral") {
                $tickN++
                $now = [DateTime]::UtcNow
                $last = if ($popAt.ContainsKey($div)) { $popAt[$div] } else { [DateTime]::MinValue }
                if (($now - $last).TotalSeconds -ge $PopCooldownSec) {
                    $cardLines = @(
                        "DIVERGENCE: $div"
                        ""
                        "price  $($row.price)   dPx  $($dPx.ToString("+0.0;-0.0;0"))"
                        "CVD    $($row.cvd)   dCVD $($dCvd.ToString("+0;-0;0"))"
                        "ND5m   $($row.nd5m)   dND  $($dNd5.ToString("+0;-0;0"))"
                        "OI 1h% $($row.oi_pct)   dOI  $($dOi.ToString("+0.00;-0.00;0.00"))"
                        ""
                        "state  $($row.state)"
                        "setup  $($row.setup)   nrr $($row.nrr.ToString("N2"))"
                    )
                    $card = $cardLines -join "`n"
                    $obj = [ordered]@{ title = "TAPE #$tickN - $div"; card_text = $card }
                    $obj | ConvertTo-Json -Depth 3 | Set-Content -Path $alertJs -Encoding UTF8
                    Start-Process pwsh.exe -ArgumentList @(
                        "-NoProfile","-ExecutionPolicy","Bypass",
                        "-File",$alertPs,
                        "-AlertFile",$alertJs
                    ) -WindowStyle Hidden | Out-Null
                    $popAt[$div] = $now
                }
            }
        } else {
            $line = "{0} | {1} | baseline | {2} | {3} nrr {4:N2}" -f $row.ts, $row.price, $row.state, $row.setup, $row.nrr
            Write-Host $line
            Add-Content -Path $out -Value $line -Encoding ASCII
        }
        $prev = $row
    } catch {
        Write-Host "tape-watch read failed: $_"
    }
    Start-Sleep -Seconds $IntervalSec
}
