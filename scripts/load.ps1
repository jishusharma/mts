# MTS aliases. Dot-source once: . .\scripts\load.ps1
# mts - the one-command wrapper (mts.ps1 at repo root). Verbs: mts help
function mts { & "$ScriptDir\..\mts.ps1" @args }
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function quick    { & "$ScriptDir\live\quick.ps1" }
function deltas   { & "$ScriptDir\live\deltas.ps1" }
function trend    { & "$ScriptDir\live\trend.ps1" }
function snapshot { & "$ScriptDir\live\snapshot.ps1" }
function overview { & "$ScriptDir\live\overview.ps1" }
function health   { & "$ScriptDir\live\health.ps1" }
function alerts   { & "$ScriptDir\live\alerts.ps1" }
function live     { & "$ScriptDir\live\live.ps1" }
function verify   { & "$ScriptDir\tools\verify_data.ps1" }
function context  { & "$ScriptDir\live\context.ps1" }
function regime   { python "$ScriptDir\..\MyTradingSys\runtime\regime_classifier.py" }

"mts loaded: live quick deltas trend snapshot overview health alerts context regime dashboard"

function mts-start { & "$ScriptDir\start-session.ps1" @args }

# mts-up - idempotent loop + supervisor start. Safe to run twice.
#   both running    -> report, do nothing
#   wrapper alive   -> start supervisor only
#   supervisor alive-> report; supervisor restarts wrapper within 90s
#   both dead       -> start loop, then supervisor
function mts-up {
    $sup = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'loop-supervisor' })
    $wrp = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'start-trading-day|statemachine' })
    if ($wrp.Count -gt 0 -and $sup.Count -gt 0) {
        "mts-up: already running (wrapper=$($wrp[0].ProcessId) supervisor=$($sup[0].ProcessId))"
        return
    }
    if ($wrp.Count -gt 0 -and $sup.Count -eq 0) {
        Start-Process pwsh.exe -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$ScriptDir\core\loop-supervisor.ps1","-Mode","armed","-IntervalMin","1","-RestartGraceSec","90") -WindowStyle Hidden
        "mts-up: supervisor started (wrapper=$($wrp[0].ProcessId) already alive)"
        return
    }
    if ($wrp.Count -eq 0 -and $sup.Count -gt 0) {
        "mts-up: supervisor alive (PID $($sup[0].ProcessId)) but wrapper dead. It restarts within 90s. If stuck, kill it first:"
        "  Get-CimInstance Win32_Process | Where-Object { `$_.CommandLine -match 'loop-supervisor' } | ForEach-Object { Stop-Process -Id `$_.ProcessId -Force }"
        return
    }
    Start-Process pwsh.exe -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$ScriptDir\core\mode.ps1","-M","armed") -WindowStyle Hidden
    # Poll for wrapper lock acquisition (up to 30s). Lock is written at wrapper start.
    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $deadline -and -not (Test-Path "$ScriptDir\..\runtime_data\apparatus.lock")) {
        Start-Sleep -Milliseconds 500
    }
    Start-Process pwsh.exe -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$ScriptDir\core\loop-supervisor.ps1","-Mode","armed","-IntervalMin","1","-RestartGraceSec","90") -WindowStyle Hidden
    $wrp2 = @(); $sup2 = @()
    $deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
        $wrp2 = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'start-trading-day|statemachine' })
        $sup2 = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'loop-supervisor' })
        if ($wrp2.Count -gt 0 -and $sup2.Count -gt 0) { break }
    }
    if ($wrp2.Count -gt 0 -and $sup2.Count -gt 0) {
        "mts-up: started (wrapper=$($wrp2[0].ProcessId) supervisor=$($sup2[0].ProcessId))"
    } else {
        "mts-up: incomplete (wrapper=$($wrp2.Count) supervisor=$($sup2.Count)). Check supervisor_log.txt and apparatus_log.txt."
    }
}

# mts-loop - loop lifecycle dispatcher. start/stop/status.
function mts-loop {
    param([ValidateSet('start','stop','status')][string]$Action = 'status')
    switch ($Action) {
        'start'  { & "$ScriptDir\start-session.ps1"; mts-up }
        'stop'   { & "$ScriptDir\core\stop-day.ps1" }
        'status' {
            $st = Join-Path $ScriptDir "..\runtime_data\loop_state.json"
            if (Test-Path $st) { Get-Content $st -Raw }
            else { "loop_state.json not present" }
        }
    }
}

# live feed (canonical) - see MTS_DICTIONARY.md LIVE FEED NAMES
function mts-live      { Remove-Item "$ScriptDir\..\runtime_data\mts_watch_stop.flag" -ErrorAction SilentlyContinue | Out-Null; & "$ScriptDir\live\mts-watch.ps1" @args }
function mts-live-fast { & "$ScriptDir\live\mts-watch.ps1" -IntervalSec 10 }
function mts-live-stop { New-Item "$ScriptDir\..\runtime_data\mts_watch_stop.flag" -ItemType File -Force | Out-Null; "stop flag written" }
function mts-live-log  { Get-Content "$ScriptDir\..\runtime_data\mts-watch.log" -Tail 40 }
function mts-tape      { & "$ScriptDir\live\tape-watch.ps1" @args }
function mts-dashboard { & "$ScriptDir\live\mts-dashboard.ps1" @args }

# git shortcuts - stripped ceremony
function gitsnap { git add -A; if ($LASTEXITCODE -ne 0) { "ABORT: git add failed"; return }; git commit -m "$args" -q; if ($LASTEXITCODE -ne 0) { "ABORT: git commit failed (nothing to commit or hook rejected); tag NOT moved"; return }; git tag -f last-snapshot; "committed: " + (git rev-parse --short HEAD) }
function gitsee  { git log --oneline -5; "dirty: " + (git status --short | Measure-Object -Line).Lines }
function gitundo { git reset --hard last-snapshot; "reverted to last-snapshot" }



# mts-paste - continuous live snapshot writer. See PENDING_MTS_PASTE.
function mts-paste      { Remove-Item "$ScriptDir\..\runtime_data\live_paste_stop.flag" -ErrorAction SilentlyContinue | Out-Null; & "$ScriptDir\live\mts-paste.ps1" @args }
function mts-paste-now  { & "$ScriptDir\live\mts-paste.ps1" -Once; Get-Content "$ScriptDir\..\Dumps\LIVE_PASTE.txt" -Raw }
function mts-paste-stop { New-Item "$ScriptDir\..\runtime_data\live_paste_stop.flag" -ItemType File -Force | Out-Null; "stop flag written" }

