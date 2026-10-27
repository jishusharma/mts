<#
scripts\monitor\stations.ps1
Monitoring stations - live data feed reader.
One station per switch, or -All for full paste.

On-disk stations (auto-read):
  F1 snapshot    newest runtime_data\snapshots\BTCUSDT_*.json, raw
  F2 cycles      runtime_data\apparatus_log.txt tail N
  F3 state       MyTradingSys\runtime\state_code.json + age
  F4 structure   MyTradingSys\runtime\current_market_state.md sections
  F5 ledger      MyTradingSys\runtime\session_log.json last N events
  F6 history     10 most recent snapshots

External stations (manual, no disk source):
  F7 coinglass   paste screenshot
  F8 funding     paste funding/news text

Usage:
  .\stations.ps1
  .\stations.ps1 -All
  .\stations.ps1 -Station F2 -Tail 60
#>
param(
  [ValidateSet("F1","F2","F3","F4","F5","F6","F7","F8")]
  [string[]]$Station = @("F1","F2","F3","F4","F5"),
  [int]$Tail = 30,
  [switch]$All
)

$ErrorActionPreference = "Stop"
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location $root

if ($All) { $Station = @("F1","F2","F3","F4","F5","F6","F7","F8") }

function Show-F1 {
  "=== F1 SNAPSHOT (newest) ==="
  $s = Get-ChildItem ".\runtime_data\snapshots\BTCUSDT_*.json" -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime -Desc | Select-Object -First 1
  if (-not $s) { "NO SNAPSHOT"; return }
  $s | Select-Object Name, Length, LastWriteTime
  Get-Content $s.FullName -Raw
}

function Show-F2 {
  "=== F2 APPARATUS LOG (tail $Tail) ==="
  Get-Content ".\runtime_data\apparatus_log.txt" -Tail $Tail -ErrorAction SilentlyContinue
}

function Show-F3 {
  "=== F3 STATE CODE ==="
  $p = ".\MyTradingSys\runtime\state_code.json"
  Get-Item $p | Select-Object Length, LastWriteTime
  Get-Content $p -Raw
}

function Show-F4 {
  "=== F4 STRUCTURE (sections) ==="
  $cms = ".\MyTradingSys\runtime\current_market_state.md"
  Get-Content $cms | Select-String -Pattern "^## (META|STATE|VWAP|CVD|TRADE_FLOW|FUNDING|SPOT_PERP|SWING)$" -Context 0,8
}

function Show-F5 {
  "=== F5 LEDGER (last $Tail events) ==="
  $log = Get-Content ".\MyTradingSys\runtime\session_log.json" -Raw | ConvertFrom-Json
  $log.events | Select-Object -Last $Tail | ConvertTo-Json -Depth 4
}

function Show-F6 {
  "=== F6 HISTORY (10 most recent) ==="
  Get-ChildItem ".\runtime_data\snapshots\BTCUSDT_*.json" |
    Sort-Object LastWriteTime -Desc | Select-Object -First 10 Name, Length, LastWriteTime
}

function Show-F7 { "=== F7 EXTERNAL (CoinGlass) === MANUAL: paste screenshot." }
function Show-F8 { "=== F8 EXTERNAL (funding/news) === MANUAL: paste text." }

function Show-Health {
  "=== HEALTH ==="
  $now = Get-Date
  $s = Get-ChildItem ".\runtime_data\snapshots\BTCUSDT_*.json" -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime -Desc | Select-Object -First 1
  if ($s) { "snap age (s): " + [math]::Round(($now - $s.LastWriteTime).TotalSeconds) }
  $sc = ".\MyTradingSys\runtime\state_code.json"
  if (Test-Path $sc) { "state_code age (s): " + [math]::Round(($now - (Get-Item $sc).LastWriteTime).TotalSeconds) }
  $j = Get-Process java -ErrorAction SilentlyContinue
  "java: " + (($j | Measure-Object).Count) + " proc(s)"
  $lock = ".\runtime_data\apparatus.lock"
  if (Test-Path $lock) { "lock: " + (Get-Item $lock).LastWriteTime } else { "lock: absent" }
}

foreach ($st in $Station) {
  switch ($st) {
    "F1" { Show-F1 }
    "F2" { Show-F2 }
    "F3" { Show-F3 }
    "F4" { Show-F4 }
    "F5" { Show-F5 }
    "F6" { Show-F6 }
    "F7" { Show-F7 }
    "F8" { Show-F8 }
  }
}
Show-Health
