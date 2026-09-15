# MTS aliases. Dot-source once: . .\scripts\load.ps1
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
function lx { & "$ScriptDir\live\lx.ps1" }
function ld { & "$ScriptDir\live\ld.ps1" }
function lt { & "$ScriptDir\live\lt.ps1" }
function lf { & "$ScriptDir\live\lf.ps1" }
function lh { & "$ScriptDir\live\lh.ps1" }
function la { & "$ScriptDir\live\la.ps1" }
function lc { & "$ScriptDir\live\lc.ps1" }
"mts loaded: lx ld lt lf lh la lc"
function mts-start { & "$ScriptDir\..\session-start.ps1" @args }

# git aliases - stripped ceremony
function gitsnap { git add -A; git commit -m "$args" -q; git tag -f last-snapshot; "committed: " + (git rev-parse --short HEAD) }
function gitsee  { git log --oneline -5; "dirty: " + (git status --short | Measure-Object -Line).Lines }
function gitundo  { git reset --hard last-snapshot; "reverted to last-snapshot" }
