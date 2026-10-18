# start-agent.ps1 - idempotent start for the AIBridge agent (the one documented start command).
#   powershell -NoProfile -ExecutionPolicy Bypass -File F:\AIBridge\scripts\start-agent.ps1 [-Watch]
# Already listening: prints who answers and exits 0. Not listening: starts src\agent.ps1 hidden and waits for /ping.
# -Watch keeps this window looping every 20 s and restarts the agent when it stops answering (watchdog).
param([switch]$Watch)
$ErrorActionPreference = 'Stop'
$base = Split-Path -Parent $PSScriptRoot
$cfg = Get-Content -Raw -LiteralPath (Join-Path $base 'src\config.json') | ConvertFrom-Json
$url = "http://$($cfg.bind):$($cfg.port)/ping"
function Test-Agent {
    try { return (Invoke-RestMethod -Uri $url -TimeoutSec 3 -Headers @{ Origin = [string]$cfg.allowed_origins[0] }) } catch { return $null }
}
function Start-Agent {
    Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $base 'src\agent.ps1'))
    for ($i = 0; $i -lt 30; $i++) { Start-Sleep -Milliseconds 500; $r = Test-Agent; if ($r) { return $r } }
    return $null
}
$r = Test-Agent
if ($r) { "agent already running: $($r.agent) on $($r.host) pid $($r.pid)" }
else {
    $r = Start-Agent
    if ($r) { "agent started: $($r.agent) on $($r.host) pid $($r.pid)" } else { 'agent did not answer /ping within 15 s; run src\agent.ps1 in a visible window to see the error'; exit 1 }
}
if ($Watch) {
    while ($true) {
        Start-Sleep -Seconds 20
        if (-not (Test-Agent)) { $r = Start-Agent; "$(Get-Date -Format s) restarted: $(if ($r) { $r.pid } else { 'FAILED' })" }
    }
}
