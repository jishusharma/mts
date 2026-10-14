# audit.ps1 - append-only hash-chained audit for AIBridge agent.
# Format: one line per entry. "<64-hex-hash>\t<json-payload>\n"
# The payload JSON is stored verbatim. Its exact bytes are what gets
# hashed. No round-trip serialization, so hash is always reproducible.
# prev_hash is inside the payload; chain verify walks the file in order.

function Get-AuditPath { Join-Path $root 'audit.jsonl' }

function Get-LastAuditHash {
    $file = Get-AuditPath
    if (-not (Test-Path -LiteralPath $file)) { return '' }
    $lines = [IO.File]::ReadAllLines($file)
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $ln = $lines[$i]
        if (-not $ln.Trim()) { continue }
        $tab = $ln.IndexOf("`t")
        if ($tab -lt 0) { return '' }
        return $ln.Substring(0, $tab)
    }
    return ''
}
function Write-Audit {
    param($entry)
    $file = Get-AuditPath
    $prevHash = Get-LastAuditHash
    $entry.prev_hash = $prevHash
    $json = $entry | ConvertTo-Json -Depth 6 -Compress
    $sha = [Security.Cryptography.SHA256]::Create()
    $hb = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($prevHash + '|' + $json))
    $hash = -join ($hb | ForEach-Object { '{0:x2}' -f $_ })
    $line = $hash + "`t" + $json + "`n"
    [IO.File]::AppendAllText($file, $line, [System.Text.UTF8Encoding]::new($false))
}
function Test-AuditChain {
    $file = Get-AuditPath
    if (-not (Test-Path -LiteralPath $file)) { return $true }
    $expectedPrev = ''
    $lineNum = 0
    foreach ($line in [IO.File]::ReadAllLines($file)) {
        $lineNum++
        if (-not $line.Trim()) { continue }
        $tab = $line.IndexOf("`t")
        if ($tab -lt 0) {
            Write-Host "chain broken at line $lineNum : no tab separator"
            return $false
        }
        $claimed = $line.Substring(0, $tab)
        $json = $line.Substring($tab + 1)
        try { $obj = $json | ConvertFrom-Json } catch {
            Write-Host "chain broken at line $lineNum : payload not parseable"
            return $false
        }
        $prev = [string]$obj.prev_hash
        if ($prev -ne $expectedPrev) {
            Write-Host "chain broken at line $lineNum : prev_hash mismatch"
            return $false
        }
        $sha = [Security.Cryptography.SHA256]::Create()
        $hb = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($prev + '|' + $json))
        $computed = -join ($hb | ForEach-Object { '{0:x2}' -f $_ })
        if ($computed -ne $claimed) {
            Write-Host "chain broken at line $lineNum : hash mismatch"
            return $false
        }
        $expectedPrev = $claimed
    }
    return $true
}
