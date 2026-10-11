# Supervisor single-instance lock check (apparatus_fixes.md 2026-10-11: recycled pid 4468 -> svchost).
# Lock file text is "<pid> <utc iso time>". The holder is live only if that pid exists AND the process
# started no later than the lock time (a recycled pid starts after the lock was written).
# Returns the live pid, or 0 when the lock is stale. Unparseable time: pid must be a powershell/pwsh process.
function Get-SupLockLivePid {
    param([string]$Content)
    if (-not $Content) { return 0 }
    $parts = $Content.Trim() -split "\s+"
    $ep = 0
    if (-not [int]::TryParse($parts[0], [ref]$ep) -or $ep -le 0) { return 0 }
    $p = Get-Process -Id $ep -ErrorAction SilentlyContinue
    if (-not $p) { return 0 }
    $lockUtc = [DateTime]::MinValue
    $ok = $parts.Count -gt 1 -and [DateTime]::TryParse($parts[1], [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind, [ref]$lockUtc)
    if ($ok) {
        try { $start = $p.StartTime.ToUniversalTime() } catch { return 0 }
        if ($start -gt $lockUtc.ToUniversalTime().AddSeconds(5)) { return 0 }
        return $ep
    }
    if ($p.ProcessName -match '^(powershell|pwsh)$') { return $ep }
    return 0
}
