# mts-paste.ps1 - writes one live snapshot of the system to Dumps\LIVE_PASTE.txt
# Read-only observer. Does not touch the loop, does not modify state.
# Cadence default 30s. -IntervalSec overrides. -Once writes one cycle and exits.
# Stops on runtime_data\live_paste_stop.flag.
param([int]$IntervalSec = 30, [switch]$Once)

$ErrorActionPreference = "Continue"
$Root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$Out      = Join-Path $Root "Dumps\LIVE_PASTE.txt"
$StopFlag = Join-Path $Root "runtime_data\live_paste_stop.flag"
$Log      = Join-Path $Root "runtime_data\apparatus_log.txt"
$Tape     = Join-Path $Root "runtime_data\live_tape.md"
$StateCode= Join-Path $Root "MyTradingSys\runtime\state_code.json"
$Regime   = Join-Path $Root "MyTradingSys\runtime\state_code_regime.json"
$Pos      = Join-Path $Root "MyTradingSys\runtime\position.json"
$SnapDir  = Join-Path $Root "runtime_data\snapshots"
$Lock     = Join-Path $Root "runtime_data\apparatus.lock"
$MaxBytes = 102400
function Get-FileTailLines {
  param([string]$Path, [int]$N)
  if (-not (Test-Path $Path)) { return @("<missing: $Path>") }
  return @(Get-Content $Path -Tail $N -ErrorAction SilentlyContinue)
}

function Get-FileRaw {
  param([string]$Path)
  if (-not (Test-Path $Path)) { return "<missing: $Path>" }
  return (Get-Content $Path -Raw -ErrorAction SilentlyContinue)
}

function Get-LatestSnapshot {
  $f = Get-ChildItem $SnapDir -Filter 'BTCUSDT_*.json' -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($null -eq $f) { return @{ name = "<none>"; raw = "<none>" } }
  return @{ name = $f.Name; raw = (Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue) }
}

function Write-Paste {
  param([string]$Out, [string[]]$Sections, [int]$MaxBytes)
  $joined = ($Sections -join "`n")
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($joined)
  while ($bytes.Length -gt $MaxBytes -and $Sections.Count -gt 4) {
    $Sections = $Sections[0..($Sections.Count - 2)]
    $joined = ($Sections -join "`n")
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($joined)
  }
  $tmp = "$Out.tmp"
  [System.IO.File]::WriteAllBytes($tmp, $bytes)
  if (Test-Path $Out) { Remove-Item $Out -Force }
  Move-Item $tmp $Out -Force
  return $bytes.Length
}
function Invoke-Cycle {
  $now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  $logMtime = if (Test-Path $Log) { (Get-Item $Log).LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ") } else { "missing" }
  $lockBody = if (Test-Path $Lock) { (Get-Content $Lock -Raw).Trim() } else { "none" }
  $snap = Get-LatestSnapshot
  $posBody = if (Test-Path $Pos) { Get-FileRaw $Pos } else { "none" }

  $sec = @()
  $sec += "== NOW UTC =="
  $sec += $now
  $sec += ""
  $sec += "== LOG MTIME =="
  $sec += $logMtime
  $sec += ""
  $sec += "== LOCK =="
  $sec += $lockBody
  $sec += ""
  $sec += "== LOG TAIL 5 =="
  $sec += (Get-FileTailLines $Log 5)
  $sec += ""
  $sec += "== STATE CODE =="
  $sec += (Get-FileRaw $StateCode)
  $sec += ""
  $sec += "== REGIME =="
  $sec += (Get-FileRaw $Regime)
  $sec += ""
  $sec += "== LATEST SNAPSHOT: $($snap.name) =="
  $sec += $snap.raw
  $sec += ""
  $sec += "== TAPE TAIL 20 =="
  $sec += (Get-FileTailLines $Tape 20)
  $sec += ""
  $sec += "== POSITION =="
  $sec += $posBody
  $sec += ""
  $sec += "== END =="

  return (Write-Paste -Out $Out -Sections $sec -MaxBytes $MaxBytes)
}

if ($Once) {
  $n = Invoke-Cycle
  "$((Get-Date).ToUniversalTime().ToString('HH:mm:ssZ')) wrote $n bytes -> $Out"
  exit 0
}

"mts-paste started. interval=${IntervalSec}s. stop flag: $StopFlag"
while (-not (Test-Path $StopFlag)) {
  $n = Invoke-Cycle
  "$((Get-Date).ToUniversalTime().ToString('HH:mm:ssZ')) wrote $n bytes"
  Start-Sleep -Seconds $IntervalSec
}
"stop flag seen. exiting."