# start_trading_day.ps1
# MTS trading-day apparatus. Repo root. Ctrl+C to stop.
# Usage: .\start-trading-day.ps1
#        .\start-trading-day.ps1 -Once
#        .\start-trading-day.ps1 -IntervalMin 30 -NoBeep

param(
    [int]$IntervalMin = 0,
    [string]$Symbol = "BTCUSDT",
    [ValidateSet("prep","armed","live")]
    [string]$Mode = "prep",
    [ValidateSet("short","long","")]
    [string]$Direction = "",
    [double]$Entry = 0,
    [double]$Stop = 0,
    [double]$Target = 0,
    [switch]$Once,
    [switch]$NoBeep,
    [ValidateSet("on","off")]
    [string]$Popups = "on"
)

if ($IntervalMin -le 0) {
    switch ($Mode) {
        "prep"  { $IntervalMin = 5 }
        "armed" { $IntervalMin = 1 }
        "live"  { $IntervalMin = 1 }
    }
}
$PriceMovePct = if ($Mode -eq "prep") { 0.30 } elseif ($Mode -eq "armed") { 0.15 } else { 0.10 }
$AlertProofChange = ($Mode -in @("armed","live"))
$StopProxPct = 0.15
$TargetProxPct = 0.15

$ErrorActionPreference = "Continue"
$R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Set-Location $R

$LogDir = Join-Path $R "data"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$LogFile = Join-Path $LogDir "apparatus_log.txt"
$CounterFile = Join-Path $LogDir "alert_counter.txt"
$script:AlertCount = 0
if (Test-Path $CounterFile) {
    try { $script:AlertCount = [int](Get-Content $CounterFile -Raw).Trim() } catch { $script:AlertCount = 0 }
}

Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
$script:NotifyIcon = $null
if (-not $NoBeep) {
    try {
        $script:NotifyIcon = New-Object System.Windows.Forms.NotifyIcon
        $script:NotifyIcon.Icon = [System.Drawing.SystemIcons]::Warning
        $script:NotifyIcon.BalloonTipTitle = "MTS ALERT"
        $script:NotifyIcon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
        $script:NotifyIcon.Visible = $true
    } catch {
        Write-Host "[apparatus] NotifyIcon unavailable: $_"
    }
}

function Log-Line {
    param([string]$msg)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
    $line = "$stamp | $msg"
    Write-Host $line
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
}

function Invoke-WithTimeout {
    param(
        [Parameter(Mandatory=$true)][string]$File,
        [Parameter(Mandatory=$false)][string[]]$ArgList = @(),
        [Parameter(Mandatory=$true)][int]$TimeoutSec,
        [Parameter(Mandatory=$false)][string]$Tag = "call",
        [Parameter(Mandatory=$false)][string]$WorkDir = ""
    )
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $File
    if ($ArgList.Count -eq 1) {
        $psi.Arguments = $ArgList[0]
    } elseif ($ArgList.Count -gt 1) {
        $psi.Arguments = ($ArgList | Select-Object -Skip 1 | ForEach-Object { '"' + $_ + '"' }) -join ' '
        $psi.Arguments = $ArgList[0] + ' ' + $psi.Arguments
    }
    if ($WorkDir -ne "") { $psi.WorkingDirectory = $WorkDir }
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $false
    $psi.RedirectStandardError = $false
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    try {
        $null = $proc.Start()
        $exited = $proc.WaitForExit($TimeoutSec * 1000)
        if (-not $exited) {
            Log-Line ("TIMEOUT {0} {1}s PID={2}" -f $Tag, $TimeoutSec, $proc.Id)
            try { & taskkill.exe /T /F /PID $proc.Id 2>&1 | Out-Null } catch {}
            return -1
        }
        return $proc.ExitCode
    } catch {
        Log-Line ("SPAWN_FAIL {0} : {1}" -f $Tag, $_)
        return -2
    } finally {
        try {
            if ($proc -and -not $proc.HasExited) {
                & taskkill.exe /T /F /PID $proc.Id 2>&1 | Out-Null
            }
        } catch {}
        try { if ($proc) { $proc.Dispose() } } catch {}
    }
}

function Beep-Alert {
    param([string]$Msg = "verdict changed", [string]$Title = "MTS ALERT")
    if ($NoBeep) { return }
    try {
        [console]::beep(800, 200); Start-Sleep -Milliseconds 80
        [console]::beep(1000, 200); Start-Sleep -Milliseconds 80
        [console]::beep(1200, 300)
    } catch {}
    # Balloon disabled — custom popup (show_alert.ps1) handles the visible alert.

}

function Compute-Verdict {
    param($snap, $proofDir = "aligned")
    $price = [double]$snap.current_price
    $ts = [string]$snap.timestamp_utc
    $cond = $snap.conditions
    $state = "$($cond.vp_shape)/$($cond.price_vs_va)"
    $cands = @($snap.setup_candidates)

    if ($cands.Length -eq 0 -or $null -eq $cands[0]) {
        return [PSCustomObject]@{
            verdict = "NO_TRADE"; reason = "no candidates"
            setup = "-"; zone = "-"; zone_price = 0.0
            net_rr = 0.0; proof = 0
            price = $price; ts = $ts; state = $state
        }
    }

    $top = $cands[0]
    $net_rr = [double]$top.math.net_rr
    $net_ok = [bool]$top.math.net_rr_sanity
    $tier   = [string]$top.math.tier
    $proof  = [int]$top.score.proof_count
    $setup  = [string]$top.setup_type
    $zone   = [string]$top.zone.name
    $zprice = [double]$top.zone.price

    if (-not $net_ok) {
        $v = "WAIT_RR"; $reason = ("net_rr {0:N2} < 2.0" -f $net_rr)
    } elseif ($tier -eq "ignore") {
        $v = "WAIT_FAR"; $reason = "tier=ignore"
    } elseif ($tier -eq "conditional") {
        $v = "WAIT_TRIGGER"; $reason = "price not at zone"
    } elseif ($proof -lt 3) {
        $v = "WAIT_PROOF"; $reason = "proof $proof"
    } elseif ($proof -lt 5) {
        $v = "WATCH"; $reason = "proof $proof"
    } else {
        $v = "SETUP_FORMING"; $reason = "proof $proof"
    }
    if ($proofDir -eq "contradiction" -and $v -eq "SETUP_FORMING") {
        $v = "WATCH"; $reason = "proof $proof contradicted"
    }

    # broken-value override - suppress CT against confirmed flow direction
    $pvVa = $snap.conditions.price_vs_va
    $cvdSlope = $snap.conditions.cvd_slope
    $setupDir = ""
    if ($cands.Length -gt 0) { $setupDir = [string]$cands[0].direction }
    if ($pvVa -eq "below_val" -and $cvdSlope -eq "falling" -and $setupDir -eq "long") {
        if ($v -in @("SETUP_FORMING","SETUP_CONFIRMED")) {
            $v = "WAIT_RR"; $reason = "broken below_val + CVD falling vs LONG"
        }
    }
    if ($pvVa -eq "above_vah" -and $cvdSlope -eq "rising" -and $setupDir -eq "short") {
        if ($v -in @("SETUP_FORMING","SETUP_CONFIRMED")) {
            $v = "WAIT_RR"; $reason = "broken above_vah + CVD rising vs SHORT"
        }
    }

    return [PSCustomObject]@{
        verdict = $v; reason = $reason
        setup = $setup; zone = $zone; zone_price = $zprice
        net_rr = $net_rr; proof = $proof
        price = $price; ts = $ts; state = $state
    }
}

function Format-VerdictLine {
    param($v)
    $tshort = if ($v.ts.Length -ge 19) { $v.ts.Substring(0, 19) } else { $v.ts }
    $pdstr = if ($v.proof_dir) { $v.proof_dir } else { "-" }
    return ("{0} | {1:F2} | {2} | {3} ({4}) | {5} @ {6} {7:F2} | nrr={8:N2} | p={9} | pd={10}" -f `
        $tshort, $v.price, $v.state, $v.verdict, $v.reason,
        $v.setup, $v.zone, $v.zone_price, $v.net_rr, $v.proof, $pdstr)
}

function Build-Card {
    param($v, $snap)
    $lines = @()
    $lines += "ALERT #$($script:AlertCount)"
    $lines += "---"
    $lines += "VERDICT: $($v.verdict)"
    $lines += "WHY:     $($v.reason)"
    $lines += "TIME:    $($v.ts)"
    $lines += "PRICE:   $($v.price)"
    $lines += "STATE:   $($v.state)"
    $lines += ""
    $lines += "SETUP:   $($v.setup)"
    if ($v.proof_dir) { $lines += "PROOF_DIR: $($v.proof_dir) $($v.proof_dir_details)" }
    $quadLine = ""
    try {
        $qScript = Join-Path $R "MyTradingSys\mts\runtime\quad_classify.py"
        $quadLine = (python $qScript 2>&1 | Out-String).Trim()
    } catch {}
    if ($quadLine) { $lines += $quadLine }
    if ($thesisLine) { $lines += "SSOT_THESIS: $thesisLine" }
    if ($triggerLine) { $lines += "SSOT_TRIGGER: $triggerLine" }
    $lines += "ZONE:    $($v.zone) @ $($v.zone_price)"
    $lines += ""
    $cands = @($snap.setup_candidates)
    if ($cands.Length -gt 0 -and $cands[0]) {
        $top = $cands[0]
        $lines += "ENTRY:   $($top.zone.price)"
        $lines += "STOP:    $($top.math.stop)"
        $lines += "TARGET:  $($top.math.target)"
        $lines += "R:R:     gross $($top.math.gross_rr) / net $($top.math.net_rr)"
        $lines += ""
        $lines += "PROOF:"
        $p = $top.proof
        $lines += "  rejection_wick   : $($p.rejection_wick)"
        $lines += "  finished_auction : $($p.finished_auction.direction) detected=$($p.finished_auction.detected)"
        $lines += "  delta_flip       : detected=$($p.delta_flip.detected) at_zone=$($p.delta_flip.at_zone)"
        $lines += "  volume_spike     : detected=$($p.volume_spike.detected) mag=$($p.volume_spike.magnitude)"
        $lines += "  speed            : picking_up=$($p.speed.picking_up) score=$($p.speed.score)"
        $lines += "  cvd_aligned      : $($p.cvd_aligned)"
        $lines += "  book_imbalance   : $($p.book_imbalance)"
    }
    return ($lines -join "`n")
}

Log-Line "=== APPARATUS START ==="

# Singleton lock
$lockFile = Join-Path $LogDir "apparatus.lock"
if (Test-Path $lockFile) {
    $lockLines = Get-Content $lockFile -Raw -ErrorAction SilentlyContinue
    $lockPid = 0; $lockTs = 0
    if ($lockLines) {
        $parts = $lockLines.Trim() -split "\s+"
        if ($parts.Length -ge 1) { try { $lockPid = [int]$parts[0] } catch {} }
        if ($parts.Length -ge 2) { try { $lockTs = [int64]$parts[1] } catch {} }
    }
    $stale = $true
    if ($lockPid -gt 0) {
        $existing = Get-Process -Id $lockPid -ErrorAction SilentlyContinue
        if ($existing) {
            # stale if lock older than 10 min
            $nowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
            if ($lockTs -gt 0 -and ($nowEpoch - $lockTs) -lt 600) {
                $stale = $false
            }
        }
    }
    if (-not $stale) {
        Log-Line "ABORT: apparatus running PID=$lockPid (lock age $((([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) - $lockTs))s)"
        exit 1
    }
    Log-Line "stale lock cleared (was PID=$lockPid)"
    Remove-Item $lockFile -ErrorAction SilentlyContinue
}
$nowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
Set-Content -LiteralPath $lockFile -Value "$PID $nowEpoch" -Encoding ASCII
Log-Line "lock acquired PID=$PID"
Log-Line "Mode=$Mode Popups=$Popups IntervalMin=$IntervalMin Symbol=$Symbol Once=$Once Direction=$Direction Entry=$Entry Stop=$Stop Target=$Target"

# Warmup: wait for next candle close + 10s before cycle 1
if (-not $Once) {
    $nowUtc = (Get-Date).ToUniversalTime()
    $secOfDay = $nowUtc.Hour * 3600 + $nowUtc.Minute * 60 + $nowUtc.Second
    $cycleSec = $IntervalMin * 60
    $nextBoundary = [Math]::Ceiling(($secOfDay + 1) / $cycleSec) * $cycleSec
    $warmup = $nextBoundary - $secOfDay + 10
    if ($warmup -lt 15) { $warmup += $cycleSec }
    Log-Line ("warmup {0}s -> first candle close+10s" -f $warmup)
    Start-Sleep -Seconds $warmup
}

# Kill stale java (state machine from prior run)
$stale = Get-Process java -ErrorAction SilentlyContinue
if ($stale) {
    Log-Line "killing $($stale.Count) stale java"
    $stale | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Spawn state machine in its own hidden window
$smArgs = @(
    "-NoProfile","-ExecutionPolicy","Bypass",
    "-Command",
    "cd '$R'; mvn -q exec:java '-Dexec.mainClass=datafeed.Main' '-Dexec.args=statemachine $Symbol'"
)
$sm = Start-Process powershell.exe -ArgumentList $smArgs -PassThru -WindowStyle Hidden
Log-Line "state_machine PID=$($sm.Id)"
$StateMachinePID = $sm.Id

$lastVerdict = $null
$lastZone = $null
$lastPrice = $null
$lastProof = $null
$script:LastAlertMs = 0
$lastState = $null
$pendingState = $null
$pendingStateFrom = $null
$cycle = 0
$exitPhase = "startup"

try {
    while ($true) {
        $cycle++
        $exitPhase = "cycle_body"
        Log-Line "--- cycle $cycle ---"
    
        Write-Host "[apparatus] fetching snapshot..."
        $mvnCmd = 'mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=snapshot ' + $Symbol + '" > NUL 2>&1'
        $rc = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $mvnCmd) -TimeoutSec 90 -Tag "mvn_snapshot" -WorkDir $R
        if ($rc -ne 0) {
            Log-Line ("SNAPSHOT_FAIL exit=" + $rc)
            if ($Once) { break }
            Start-Sleep -Seconds 60; continue
        }
    
        $umsCmd = 'python "' + $R + '\MyTradingSys\mts\runtime\update_market_state.py" > NUL 2>&1'
        $rc = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $umsCmd) -TimeoutSec 30 -Tag "update_market_state" -WorkDir $R
        if ($rc -ne 0) {
            Log-Line ("STATE_UPDATE_WARN exit=" + $rc)
        } else {
            Log-Line "state_updated"
        }
    
        $s = Get-ChildItem "$R\data\snapshots\${Symbol}_*.json" |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if (-not $s) {
            Log-Line "NO_SNAPSHOT_FILE"
            if ($Once) { break }
            Start-Sleep -Seconds 60; continue
        }
    
        try {
            $snap = Get-Content $s.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Log-Line "JSON_PARSE_FAIL: $_"
            if ($Once) { break }
            Start-Sleep -Seconds 60; continue
        }
    
        $pd = "aligned"
        $pdd = ""
        $moFile = Join-Path $env:TEMP "app_mo.json"
        try {
            $moCmd = 'python "' + $R + '\MyTradingSys\mts\runtime\build_mo_cli.py" "' + $s.FullName + '" "' + $moFile + '" > NUL 2>&1'
            $null = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $moCmd) -TimeoutSec 30 -Tag "build_mo_cli" -WorkDir $R
            if ((Test-Path $moFile) -and (Get-Item $moFile).Length -gt 0) {
                $mo = Get-Content $moFile -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($mo.proof_direction_status) { $pd = [string]$mo.proof_direction_status }
                if ($mo.proof_direction_details) { $pdd = ($mo.proof_direction_details -join "; ") }
            }
            Remove-Item $moFile -ErrorAction SilentlyContinue
        } catch {}
        # Label past snapshots (idempotent, cheap)
    try {
        $olCmd = 'python "' + $R + '\MyTradingSys\mts\runtime\outcome_labeler.py" > NUL 2>&1'
        $null = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $olCmd) -TimeoutSec 30 -Tag "outcome_labeler" -WorkDir $R
    } catch {}

    # Feature layer: kline archive + regime classifier (additive, non-gating)
    try {
        $kaCmd = 'python "' + $R + '\MyTradingSys\mts\runtime\kline_archiver.py" > NUL 2>&1'
        $null = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $kaCmd) -TimeoutSec 30 -Tag "kline_archiver" -WorkDir $R
    } catch {}
    try {
        $rccCmd = 'python "' + $R + '\MyTradingSys\mts\runtime\regime_classifier.py" > NUL 2>&1'
        $null = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $rccCmd) -TimeoutSec 30 -Tag "regime_classifier" -WorkDir $R
    } catch {}
    $v = Compute-Verdict -snap $snap -proofDir $pd
        $v | Add-Member -NotePropertyName proof_dir -NotePropertyValue $pd -Force
        $v | Add-Member -NotePropertyName proof_dir_details -NotePropertyValue $pdd -Force
        Log-Line (Format-VerdictLine $v)
    
        $changed = $false
        $why = @()
        if ($null -ne $lastVerdict -and $lastVerdict -ne $v.verdict) {
            $changed = $true; $why += "verdict $lastVerdict -> $($v.verdict)"
        }
        if ($null -ne $lastZone -and $lastZone -ne $v.zone) {
            $changed = $true; $why += "zone $lastZone -> $($v.zone)"
        }
        if ($null -ne $lastPrice -and $lastPrice -gt 0) {
            $dp = [Math]::Abs(($v.price - $lastPrice) / $lastPrice) * 100
            if ($dp -gt $PriceMovePct) {
                $changed = $true
                $why += ("price delta {0:N2}%" -f $dp)
            }
        }
    
        if ($AlertProofChange -and $null -ne $lastProof -and (($lastProof -lt 5 -and $v.proof -ge 5) -or ($lastProof -ge 5 -and $v.proof -lt 5))) {
            $changed = $true
            $why += "proof $lastProof -> $($v.proof)"
        }
    
        # State transition (vp_shape or price_vs_va change)
        if ($null -ne $pendingState -and $pendingState -eq $v.state) {
            $changed = $true
            $why += "STATE $pendingStateFrom -> $($v.state)"
            $pendingState = $null
        } elseif ($null -ne $lastState -and $lastState -ne $v.state) {
            $pendingStateFrom = $lastState
            $pendingState = $v.state
        } else {
            $pendingState = $null
        }
    
        # state_code staleness check
        if ($Mode -eq "live") {
            try {
                $scFile = Join-Path $R "MyTradingSys\mts\runtime\state_code.json"
                if (Test-Path $scFile) {
                    $scCheck = Get-Content $scFile -Raw -Encoding UTF8 | ConvertFrom-Json
                    $scAge = ([DateTimeOffset]::UtcNow - [DateTime]::Parse($scCheck.timestamp_utc)).TotalSeconds
                    if ($scAge -gt 90) {
                        $changed = $true
                        $why += ("STATE_CODE STALE {0}s" -f [int]$scAge)
                    }
                }
            } catch {}
        }
    
        if ($Mode -eq "live" -and $Direction -ne "") {
            try {
                $scFile = Join-Path $R "MyTradingSys\mts\runtime\state_code.json"
                if (Test-Path $scFile) {
                    $sc = Get-Content $scFile -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($Direction -eq "short" -and $sc.state -match "^L") {
                        $changed = $true; $why += "ADVERSE FLOW state=$($sc.state)"
                    }
                    if ($Direction -eq "long" -and $sc.state -match "^S") {
                        $changed = $true; $why += "ADVERSE FLOW state=$($sc.state)"
                    }
                }
            } catch {}
            if ($Stop -gt 0) {
                $dS = [Math]::Abs($v.price - $Stop) / $Stop * 100
                if ($dS -lt $StopProxPct) { $changed = $true; $why += ("STOP NEAR {0:N2}%" -f $dS) }
            }
            if ($Target -gt 0) {
                $dT = [Math]::Abs($v.price - $Target) / $Target * 100
                if ($dT -lt $TargetProxPct) { $changed = $true; $why += ("TARGET NEAR {0:N2}%" -f $dT) }
            }
        }
    
        $cooldownBlock = $false
        $nowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        if ($script:LastAlertMs -gt 0 -and ($nowEpoch - $script:LastAlertMs) -lt 180) {
            $cooldownBlock = $true
        }
        # gate — only fire popup if verdict is actionable OR state changed
        $actionableVerdicts = @("SETUP_FORMING","SETUP_CONFIRMED","WATCH")
        $firePopup = $false
        if ($Popups -ne "off" -and $changed -and -not $cooldownBlock) {
            if ($v.verdict -in $actionableVerdicts) { $firePopup = $true }
            elseif ($why -match "STATE |ADVERSE|STOP NEAR|TARGET NEAR") { $firePopup = $true }
        }
        # === Precondition gate (schema v1.1.0, Rule 37 behavior restoration) ===
        if ($firePopup -and $v.setup -match 'scalp') {
            $preSnap = $s.FullName
            $prePy   = Join-Path $env:TEMP ("pre_gate_" + [Guid]::NewGuid().ToString() + ".py")
            $preOut  = Join-Path $env:TEMP ("pre_gate_" + [Guid]::NewGuid().ToString() + ".json")
            $preScript = @"
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, r'$($R)\MyTradingSys\mts\runtime')
from mts_math import check_scalp_preconditions, check_invalidation
with open(r'$($preSnap)', 'r', encoding='utf-8') as f:
    snap = json.load(f)
result = {"scalp": check_scalp_preconditions(snap)}
try:
    with open(r'$($R)\MyTradingSys\mts\runtime\session_state.json', 'r', encoding='utf-8') as f:
        st = json.load(f)
    clauses = (st.get('invalidates') or {}).get('clauses') or {}
    if clauses:
        result["invalidation"] = check_invalidation(clauses, snap)
    else:
        result["invalidation"] = {"fired": None, "reason": "no_clauses", "unverifiable": []}
except Exception as e:
    result["invalidation"] = {"fired": None, "reason": "state_read_error", "unverifiable": [str(e)]}
with open(r'$($preOut)', 'w', encoding='utf-8') as f:
    json.dump(result, f)
print(json.dumps(result))
"@
            Set-Content -LiteralPath $prePy -Value $preScript -Encoding UTF8
            & python $prePy 2>&1 | Out-Null
            $preResult = $null
            try {
                if (Test-Path $preOut) { $preResult = Get-Content $preOut -Raw -Encoding UTF8 | ConvertFrom-Json }
            } catch {}
            Remove-Item $prePy,$preOut -ErrorAction SilentlyContinue
            if ($preResult -and $preResult.scalp -and -not $preResult.scalp.ok) {
                $firePopup = $false
                Log-Line ("SCALP_SUPPRESSED reasons=" + ($preResult.scalp.reasons -join "; "))
            }
            if ($preResult -and $preResult.invalidation -and $preResult.invalidation.fired -eq $true) {
                Log-Line "INVALIDATION_FIRED"
            }
        }
        if ($firePopup) {
            $script:LastAlertMs = $nowEpoch
            $script:AlertCount++
            Set-Content -LiteralPath $CounterFile -Value $script:AlertCount -Encoding UTF8

        # SSOT: append to session_log.json
        try {
            $evt = @{
                ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                type = "alert"
                alert_id = $script:AlertCount
                verdict = $v.verdict
                setup = $v.setup
                action = "monitored"
                reason = $reason
            } | ConvertTo-Json -Compress
            $logScript = Join-Path $R "MyTradingSys\mts\runtime\session_state.py"
            $logPy = Join-Path $env:TEMP ("sst_append_" + [Guid]::NewGuid().ToString() + ".py")
            $evtFile = Join-Path $env:TEMP ("sst_evt_" + [Guid]::NewGuid().ToString() + ".json")
            Set-Content -LiteralPath $evtFile -Value $evt -Encoding UTF8
            $py = @"
import sys, json
sys.path.insert(0, r'C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\mts\runtime')
sys.dont_write_bytecode = True
import session_state as ss
with open(r'$($evtFile.Replace("\", "/"))', 'r', encoding='utf-8') as f:
    evt = json.load(f)
ss.append_log(evt)
print("logged")
"@
            Set-Content -LiteralPath $logPy -Value $py -Encoding UTF8
            $null = python $logPy 2>&1
            Remove-Item $logPy,$evtFile -ErrorAction SilentlyContinue
        } catch {
            Log-Line "session_log append failed: $_"
        }
            $reason = $why -join " | "
            Log-Line "ALERT #$($script:AlertCount): $reason"
            $popTitle = "MTS ALERT #$($script:AlertCount)"
            if ($reason -match "verdict") { $popTitle = "MTS #$($script:AlertCount) - VERDICT CHANGE" }
            elseif ($reason -match "zone") { $popTitle = "MTS #$($script:AlertCount) - ZONE CHANGE" }
            elseif ($reason -match "price") { $popTitle = "MTS #$($script:AlertCount) - PRICE MOVE" }
    
            # SSOT: read current thesis for context
        $thesisLine = ""
        $triggerLine = ""
        try {
            $stateScript = Join-Path $R "MyTradingSys\mts\runtime\session_state.py"
            $stateRead = python $stateScript show 2>&1 | Out-String
            $stateObj = $stateRead | ConvertFrom-Json
            if ($stateObj.thesis) {
                $thesisLine = "THESIS: $($stateObj.thesis.direction) ($($stateObj.thesis.confidence)) - $($stateObj.thesis.text)"
            }
            if ($stateObj.next_trigger -and $stateObj.next_trigger.condition) {
                $triggerLine = "NEXT_TRIGGER: $($stateObj.next_trigger.condition)"
            }
        } catch {
            $thesisLine = "THESIS: unavailable"
        }
        $session_state_read = $true

        $cardText = Build-Card -v $v -snap $snap
            $popPayload = [PSCustomObject]@{
                title     = $popTitle
                body      = "$($v.verdict) | $($v.setup) @ $($v.zone) | $reason"
                card_text = $cardText
                repo      = $R
            } | ConvertTo-Json -Depth 5
    
            $popFile = Join-Path $LogDir "last_alert.json"
            Set-Content -LiteralPath $popFile -Value $popPayload -Encoding UTF8
    
            if (-not $NoBeep) {
                # kill prior popup before spawning new - never more than 1 on screen
        Get-Process powershell -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.Id -ne $PID -and $_.MainWindowTitle -match "MTS #") {
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }
        }
        $vbsLauncher = Join-Path $R "scripts\core\launch-alert.vbs"
                $psScript = Join-Path $R "scripts\core\show-alert.ps1"
                Start-Process wscript.exe -ArgumentList @($vbsLauncher, $psScript, $popFile) -WindowStyle Hidden
            }
            Beep-Alert -Msg "" -Title $popTitle
        } else {
            Log-Line ("no change: " + $v.verdict)
        }
    
        $lastVerdict = $v.verdict
        $lastZone = $v.zone
        $lastPrice = $v.price
        $lastProof = $v.proof
        $lastState = $v.state
    
        if ($Once) { break }
    
        # ALIGN TO CANDLE CLOSE + 10s (Rule 37: engine requires closes, not wicks)
        $nowUtc = (Get-Date).ToUniversalTime()
        $secOfDay = $nowUtc.Hour * 3600 + $nowUtc.Minute * 60 + $nowUtc.Second
        $cycleSec = $IntervalMin * 60
        $nextBoundary = [Math]::Ceiling(($secOfDay + 1) / $cycleSec) * $cycleSec
        $sleepSec = $nextBoundary - $secOfDay + 10
        if ($sleepSec -lt 15) { $sleepSec += $cycleSec }
        Log-Line ("sleep {0}s -> next candle close+10s" -f $sleepSec)
        $exitPhase = "sleeping"
        Start-Sleep -Seconds $sleepSec
    }
} catch {
    Log-Line "APPARATUS ERROR phase=$exitPhase : $_"
} finally {
    if ($StateMachinePID) { try { Stop-Process -Id $StateMachinePID -Force -ErrorAction SilentlyContinue } catch {} }
    Remove-Item (Join-Path $LogDir "apparatus.lock") -ErrorAction SilentlyContinue
    Log-Line "=== APPARATUS END (finally) phase=$exitPhase ==="
}

if ($script:NotifyIcon) { try { $script:NotifyIcon.Dispose() } catch {} }
if ($StateMachinePID) {
    try {
        $p = Get-Process -Id $StateMachinePID -ErrorAction SilentlyContinue
        if ($p) { Stop-Process -Id $StateMachinePID -Force }
        Log-Line "state_machine PID=$($StateMachinePID) stopped"
    } catch {}
}
Remove-Item (Join-Path $LogDir "apparatus.lock") -ErrorAction SilentlyContinue
Log-Line "=== APPARATUS END ==="
