# stop_day.ps1 - request clean loop shutdown via flag; wait for lock release.
# Stage 3b of LOOP_LIFECYCLE_DESIGN_2026-09-19.md. No kill.

$R = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$LockFile = Join-Path $R "runtime_data\apparatus.lock"
$FlagFile = Join-Path $R "runtime_data\loop_stop.flag"
$TimeoutSec = 60

# 1. Write stop flag. Loop reads at next cycle top, breaks, runs finally,
#    removes flag then lock.
New-Item -Path $FlagFile -ItemType File -Force | Out-Null
Write-Host "stop flag written: $FlagFile"

# 2. Poll for lock release AND supervisor exit.
$SupLock = Join-Path $R "runtime_data\supervisor.lock"
$t0 = Get-Date
while (((Get-Date) - $t0).TotalSeconds -lt $TimeoutSec) {
    if ((-not (Test-Path $LockFile)) -and (-not (Test-Path $SupLock))) { break }
    Start-Sleep -Seconds 2
}

# 3. Remove flag (idempotent; loop already did it in finally on clean exit).
#    On timeout this still removes the flag, so supervisor restart is not
#    immediately re-triggered by a stale flag (see B056).
if (Test-Path $FlagFile) {
    Remove-Item $FlagFile -ErrorAction SilentlyContinue
    Write-Host "flag removed"
}

# 4. Report.
if (Test-Path $LockFile) {
    $lock = (Get-Content $LockFile -Raw).Trim()
    Write-Host "TIMEOUT: lock still present after ${TimeoutSec}s: $lock"
    exit 1
} else {
    Write-Host "stopped: lock released"
    exit 0
}
