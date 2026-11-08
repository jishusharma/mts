# lease.ps1 - account lease: one machine per DeepSeek account (0.7.33, card dsa-bridge-avoid-deepseek-block-1108).
# One file per account label in a lease folder that every host can see (config lease_dir; default run\leases on this host only):
# {account, host, ts}. Another host's lease younger than TtlS refuses the request (account_in_use); the holder renews; release
# removes it only for the holder. NowS = epoch seconds (tests pass a fake clock). Non-atomic by design: two hosts racing inside
# one second can both win once; the next heartbeat refuses the loser.

function Invoke-AccountLease {
    param(
        [string]$Account,
        [string]$Dir,
        [string]$Me,
        [ValidateSet('acquire', 'beat', 'release')][string]$Action = 'acquire',
        [int]$TtlS = 180,
        [long]$NowS = 0
    )
    if ($NowS -le 0) { $NowS = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() }
    $safe = ($Account.ToLower() -replace '[^a-z0-9._-]', '_')
    if ($safe.Length -gt 40) { $safe = $safe.Substring(0, 40) }
    if (-not $safe) { $safe = 'deepseek-default' }
    if (-not (Test-Path -LiteralPath $Dir)) { New-Item -ItemType Directory -Path $Dir -Force | Out-Null }
    $f = Join-Path $Dir ($safe + '.json')
    $cur = $null
    if (Test-Path -LiteralPath $f) {
        try { $cur = (Get-Content -Raw -LiteralPath $f) | ConvertFrom-Json } catch { $cur = $null }
    }
    $other = $null
    if ($cur -and $cur.host -and ([string]$cur.host).ToLower() -ne $Me.ToLower()) {
        $age = $NowS - [int64]$cur.ts
        if ($age -lt $TtlS) { $other = [string]$cur.host }
    }
    if ($Action -eq 'release') {
        if ($other) { return [ordered]@{ ok = $false; reason = 'not_holder'; holder = $other } }
        if ($cur -and ([string]$cur.host).ToLower() -eq $Me.ToLower()) { Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue }
        return [ordered]@{ ok = $true; reason = 'released'; holder = '' }
    }
    if ($other) { return [ordered]@{ ok = $false; reason = 'account_in_use'; holder = $other } }
    $rec = [ordered]@{ account = $safe; host = $Me; ts = $NowS } | ConvertTo-Json -Compress
    [IO.File]::WriteAllText($f, $rec, (New-Object Text.UTF8Encoding $false))
    return [ordered]@{ ok = $true; reason = 'ok'; holder = $Me }
}
