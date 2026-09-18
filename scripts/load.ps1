# MTS aliases. Dot-source once: . .\scripts\load.ps1
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
function regime   { python "$ScriptDir\..\MyTradingSys\mts\runtime\regime_classifier.py" }

"mts loaded: live quick deltas trend snapshot overview health alerts context regime dashboard"

function mts-start { & "$ScriptDir\start-session.ps1" @args }

# live feed (canonical) - see MTS_DICTIONARY.md LIVE FEED NAMES
function mts-live      { Remove-Item "$ScriptDir\..\data\mts_watch_stop.flag" -ErrorAction SilentlyContinue | Out-Null; & "$ScriptDir\live\mts-watch.ps1" @args }
function mts-live-fast { & "$ScriptDir\live\mts-watch.ps1" -IntervalSec 10 }
function mts-live-stop { New-Item "$ScriptDir\..\data\mts_watch_stop.flag" -ItemType File -Force | Out-Null; "stop flag written" }
function mts-live-log  { Get-Content "$ScriptDir\..\data\mts-watch.log" -Tail 40 }
function mts-tape      { & "$ScriptDir\live\tape-watch.ps1" @args }
function mts-dashboard { & "$ScriptDir\live\mts-dashboard.ps1" @args }

# git shortcuts - stripped ceremony
function gitsnap { git add -A; git commit -m "$args" -q; git tag -f last-snapshot; "committed: " + (git rev-parse --short HEAD) }
function gitsee  { git log --oneline -5; "dirty: " + (git status --short | Measure-Object -Line).Lines }
function gitundo { git reset --hard last-snapshot; "reverted to last-snapshot" }


