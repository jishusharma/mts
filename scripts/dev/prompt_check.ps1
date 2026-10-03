<#
prompt_check.ps1 - advisory disk check of a composed prompt (B083). FAIL warns and logs; nothing stops.

Input : -Path <text file>, or the prompt piped on stdin.
Output: a PASS/FAIL table (one row per check) and a final STATUS line. Exit code is always 0: the prompt still
        ships and the operator decides.
Log   : one JSON line per check appended to MyTradingSys\runtime\prompt_check_log.jsonl (override with -LogPath).

Checks (B083 Fix section):
  1 paths      every path string in the prompt resolves on disk (Test-Path; bare file names resolve by name in the repo)
  2 citations  every file:line citation names a real line in that file (file:N, file:LN, file:N-M, file:N,M)
  3 tokens     every UPPER_SNAKE token on a line that cites a file is present in one of that line's files
  4 clauses    every clause with 'do not', 'never', 'must not', 'cannot' or a numeric cap is tagged OPERATOR-SET,
               is an operator verbatim line (starts with a double quote), or appears in -OperatorWords
  5 limits     no capability limit on another surface (cannot / has no / read-only / design-only ...) unless the
               operator's own words carry it (same three escapes as check 4)

Conventions: a path on a line marked (NEW), NEW:, CREATE: or "new file" is a file the prompt asks to create; it is
counted, not checked. Placeholders (< > * ? $ { }) and URLs are skipped.
#>
param(
    [string]$Path = '',
    [string]$RepoRoot = '',
    [string]$LogPath = '',
    [string]$OperatorWords = '',
    [string]$IgnoreTokens = ''
)
$ErrorActionPreference = 'Continue'

$piped = @()
if (-not $Path) { $piped = @($input) }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoRoot) { $RepoRoot = (Resolve-Path (Join-Path $scriptDir '..\..')).Path }
if (-not $LogPath) { $LogPath = Join-Path $RepoRoot 'MyTradingSys\runtime\prompt_check_log.jsonl' }

$sourceName = 'stdin'
$text = ''
if ($Path) {
    if (Test-Path -LiteralPath $Path) {
        $text = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path).Path)
        $sourceName = $Path
    } else {
        Write-Warning "prompt file not found: $Path"
    }
} elseif ($piped.Count -gt 0) {
    $text = ($piped | ForEach-Object { [string]$_ }) -join "`n"
}
if (-not $text) {
    Write-Output 'prompt_check: no input (give -Path <file> or pipe the prompt on stdin)'
    Write-Output 'STATUS: FAIL (advisory; no prompt text was read; nothing was stopped)'
    exit 0
}
$lines = $text -split "`r?`n"

$opText = ''
if ($OperatorWords -and (Test-Path -LiteralPath $OperatorWords)) {
    $opText = ([System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $OperatorWords).Path) -replace '\s+', ' ').ToLower()
}
$ignore = @{}
foreach ($t in ($IgnoreTokens -split '[,\s]+')) { if ($t) { $ignore[$t] = $true } }

# ---------------------------------------------------------------- repo name index
$leafs = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$gitOut = $null
try { $gitOut = & git -C $RepoRoot ls-files -co --exclude-standard 2>$null } catch { $gitOut = $null }
if ($LASTEXITCODE -eq 0 -and $gitOut) {
    foreach ($l in $gitOut) { [void]$leafs.Add($l.Substring($l.LastIndexOf('/') + 1)) }
} else {
    Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '[\\/]\.git[\\/]' } | ForEach-Object { [void]$leafs.Add($_.Name) }
}
$roots = @{}
Get-ChildItem -LiteralPath $RepoRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { -not $_.Name.StartsWith('.') } | ForEach-Object { $roots[$_.Name.ToLower()] = $true }

$extGeneric = '\.[A-Za-z][A-Za-z0-9]{0,5}$'
$extBare = '^[A-Za-z0-9_][A-Za-z0-9_.\-]*\.(md|py|ps1|java|json|jsonl|txt|csv|xml|vbs|cmd|yml|yaml|flag|new|html|sh|bat|toml|ini|log)$'
$newMarker = '(\(NEW\)|\bNEW:|\bCREATE:|\bnew file\b)'

function Resolve-Cited([string]$p) {
    $q = $p -replace '\\', '/'
    while ($q.StartsWith('./')) { $q = $q.Substring(2) }
    if ($q -match '^[A-Za-z]:/') { return (Test-Path -LiteralPath $q) }
    if ($q.Contains('/')) { return (Test-Path -LiteralPath (Join-Path $RepoRoot $q)) }
    return $leafs.Contains($q)
}

function Get-FullPath([string]$p) {
    $q = $p -replace '\\', '/'
    while ($q.StartsWith('./')) { $q = $q.Substring(2) }
    if ($q -match '^[A-Za-z]:/') { return $q }
    if ($q.Contains('/')) { return (Join-Path $RepoRoot $q) }
    $hit = $null
    if ($gitOut) { $hit = $gitOut | Where-Object { $_ -eq $q -or $_.EndsWith('/' + $q) } | Select-Object -First 1 }
    if ($hit) { return (Join-Path $RepoRoot $hit) }
    return $null
}

# One entry per path-like token: Path, Line (1-based), Spec (line spec or ''), New (bool), Text (the prompt line).
$cites = New-Object System.Collections.ArrayList
$splitRx = '[\s"''\x60()\[\],;|=]+'
for ($i = 0; $i -lt $lines.Count; $i++) {
    $ln = $lines[$i]
    $isNew = $ln -match $newMarker
    foreach ($raw in ($ln -split $splitRx)) {
        if (-not $raw) { continue }
        $tok = $raw.TrimEnd('.', ':', ';', ',', '!', '?')
        if (-not $tok -or $tok.StartsWith('-') -or $tok.StartsWith('@')) { continue }
        if ($tok -match '[<>*?$%{}]' -or $tok -match '://' -or $tok.StartsWith('www.')) { continue }
        $p = $tok; $spec = ''
        if ($tok -match '^(?<p>.+?):L?(?<l>\d+(?:[-,]L?\d+)*)$') { $p = $Matches['p']; $spec = $Matches['l'] }
        $norm = $p -replace '\\', '/'
        $ok = $false
        if ($norm.Contains('/')) {
            $first = ($norm.TrimStart('.', '/') -split '/')[0].ToLower()
            if ($norm -match $extGeneric -or $norm.EndsWith('/') -or $roots.ContainsKey($first)) { $ok = $true }
            if ($norm -match '^[A-Za-z]:/') { $ok = $true }
        } elseif ($norm -match $extBare) { $ok = $true }
        if (-not $ok) { continue }
        [void]$cites.Add([pscustomobject]@{ Path = $p; Line = $i + 1; Spec = $spec; New = $isNew; Text = $ln })
    }
}

# ---------------------------------------------------------------- checks
$rows = New-Object System.Collections.ArrayList
function Add-Row([string]$id, [string]$name, [bool]$ok, [string]$detail, [int]$count) {
    [void]$rows.Add([pscustomobject]@{ Id = $id; Name = $name; Status = $(if ($ok) { 'PASS' } else { 'FAIL' }); Detail = $detail; Count = $count })
}
function Short([string]$s, [int]$n) { $s = ($s -replace '\s+', ' ').Trim(); if ($s.Length -gt $n) { return $s.Substring(0, $n) + '...' } else { return $s } }

# 1 paths
$checked = @{}; $missing = @(); $planned = 0
foreach ($c in $cites) {
    if ($c.New) { $planned++; continue }
    $key = $c.Path.ToLower()
    if ($checked.ContainsKey($key)) { continue }
    $checked[$key] = Resolve-Cited $c.Path
    if (-not $checked[$key]) { $missing += ('L{0} {1}' -f $c.Line, $c.Path) }
}
$d1 = '{0} path(s) checked, {1} missing{2}' -f $checked.Count, $missing.Count, $(if ($planned) { "; $planned marked NEW/CREATE (not checked)" } else { '' })
if ($missing.Count) { $d1 += ': ' + (($missing | Select-Object -First 12) -join '; ') }
Add-Row '1' 'paths resolve' ($missing.Count -eq 0) $d1 $checked.Count

# 2 file:line citations
$lcCache = @{}
$badCite = @(); $nCite = 0
foreach ($c in $cites) {
    if (-not $c.Spec -or $c.New) { continue }
    $nCite++
    $full = Get-FullPath $c.Path
    if (-not $full -or -not (Test-Path -LiteralPath $full -PathType Leaf)) { $badCite += ('L{0} {1}:{2} (file missing)' -f $c.Line, $c.Path, $c.Spec); continue }
    if (-not $lcCache.ContainsKey($full)) { $lcCache[$full] = @([System.IO.File]::ReadAllLines($full)).Count }
    foreach ($n in ($c.Spec -split '[-,]')) {
        $num = [int]($n -replace '[^\d]', '')
        if ($num -lt 1 -or $num -gt $lcCache[$full]) { $badCite += ('L{0} {1}:{2} (file has {3} lines)' -f $c.Line, $c.Path, $num, $lcCache[$full]); break }
    }
}
$d2 = '{0} file:line citation(s) checked, {1} bad' -f $nCite, $badCite.Count
if ($badCite.Count) { $d2 += ': ' + (($badCite | Select-Object -First 12) -join '; ') }
Add-Row '2' 'file:line is a real line' ($badCite.Count -eq 0) $d2 $nCite

# 3 uppercase tokens cited as being in a file
$tokRx = '\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b'
$textCache = @{}
$badTok = @(); $nTok = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    $files = @($cites | Where-Object { $_.Line -eq ($i + 1) -and -not $_.New } | ForEach-Object { Get-FullPath $_.Path } |
        Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -Unique)
    if ($files.Count -eq 0) { continue }
    $rest = $lines[$i]
    foreach ($c in ($cites | Where-Object { $_.Line -eq ($i + 1) })) { $rest = $rest.Replace($c.Path, ' ') }
    foreach ($m in [regex]::Matches($rest, $tokRx)) {
        $t = $m.Value
        if ($ignore.ContainsKey($t)) { continue }
        $nTok++
        $found = $false
        foreach ($f in $files) {
            if (-not $textCache.ContainsKey($f)) {
                $len = (Get-Item -LiteralPath $f).Length
                $textCache[$f] = $(if ($len -gt 20MB) { '' } else { [System.IO.File]::ReadAllText($f) })
            }
            if ($textCache[$f].Contains($t)) { $found = $true; break }
        }
        if (-not $found) { $badTok += ('L{0} {1} not in {2}' -f ($i + 1), $t, (($files | ForEach-Object { Split-Path -Leaf $_ }) -join '/')) }
    }
}
$d3 = '{0} token claim(s) checked, {1} absent' -f $nTok, $badTok.Count
if ($badTok.Count) { $d3 += ': ' + (($badTok | Select-Object -First 12) -join '; ') }
Add-Row '3' 'tokens present in file' ($badTok.Count -eq 0) $d3 $nTok

# helpers for 4 and 5
function Test-OperatorLine([string]$ln) {
    if ($ln -cmatch 'OPERATOR-SET') { return $true }
    if ($ln.TrimStart().StartsWith('"')) { return $true }
    if ($opText) {
        $n = (($ln -replace '\s+', ' ').Trim(' ', '"', '-', '*', '`')).ToLower()
        if ($n.Length -ge 12 -and $opText.Contains($n)) { return $true }
    }
    return $false
}

# 4 clauses and numeric caps
$clauseRx = '(?i)\b(do not|never|must not|cannot|can not)\b'
$capRx = '(?i)(<=|>=)\s*\d|\b(max(imum)?|cap|capped|limit|at most|no more than|up to)\b[^\r\n]{0,30}\d|\b\d[\d,\.]*\s*(k|kb|mb|lines?|tokens?|chars?|files?|rows?|items?|hours?|minutes?)\s+(max|maximum|cap|limit)\b'
$badClause = @(); $nClause = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    $ln = $lines[$i]
    if ($ln -notmatch $clauseRx -and $ln -notmatch $capRx) { continue }
    $nClause++
    if (-not (Test-OperatorLine $ln)) { $badClause += ('L{0} "{1}"' -f ($i + 1), (Short $ln 70)) }
}
$d4 = '{0} clause(s) with do not / never / must not / cannot / numeric cap, {1} untagged' -f $nClause, $badClause.Count
if ($badClause.Count) { $d4 += ': ' + (($badClause | Select-Object -First 8) -join '; ') }
Add-Row '4' 'clauses tagged OPERATOR-SET' ($badClause.Count -eq 0) $d4 $nClause

# 5 capability limits on another surface
$limitA = '(?i)\b(DSA|CL|CC|Opus|Sonnet|Haiku|Claude|cloud|worker|CLI|chat|surface|session)\b[^.\r\n]{0,40}\b(cannot|can not|can''t|has no|have no|no access|not able to|is read-only|are read-only)\b'
$limitB = '(?i)\b(design[- ]only|read[- ]only|no disk|no shell|no network|no write access|text[- ]only)\b'
$badLimit = @(); $nLimit = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    $ln = $lines[$i]
    if ($ln -notmatch $limitA -and $ln -notmatch $limitB) { continue }
    $nLimit++
    if (-not (Test-OperatorLine $ln)) { $badLimit += ('L{0} "{1}"' -f ($i + 1), (Short $ln 70)) }
}
$d5 = '{0} capability-limit line(s), {1} without the operator''s words' -f $nLimit, $badLimit.Count
if ($badLimit.Count) { $d5 += ': ' + (($badLimit | Select-Object -First 8) -join '; ') }
Add-Row '5' 'no invented capability limit' ($badLimit.Count -eq 0) $d5 $nLimit

# ---------------------------------------------------------------- report and log
Write-Output ('{0,-2} {1,-30} {2,-5} {3}' -f '#', 'CHECK', 'RESULT', 'DETAIL')
foreach ($r in $rows) { Write-Output ('{0,-2} {1,-30} {2,-5} {3}' -f $r.Id, $r.Name, $r.Status, $r.Detail) }
$failed = @($rows | Where-Object { $_.Status -eq 'FAIL' })
foreach ($r in $failed) { Write-Warning ('prompt_check FAIL {0} {1}' -f $r.Id, $r.Name) }
if ($failed.Count -eq 0) {
    Write-Output 'STATUS: PASS'
} else {
    Write-Output ('STATUS: FAIL ({0} of 5 checks; advisory: the prompt still ships, the operator decides, nothing was stopped)' -f $failed.Count)
}

try {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $h = ([System.BitConverter]::ToString($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($text))) -replace '-', '').ToLower().Substring(0, 8)
    $utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $dir = Split-Path -Parent $LogPath
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $enc = New-Object System.Text.UTF8Encoding($false)
    $sb = New-Object System.Text.StringBuilder
    foreach ($r in $rows) {
        $o = [ordered]@{ utc = $utc; source = $sourceName; prompt_sha256_8 = $h; check = $r.Name; id = $r.Id; status = $r.Status; count = $r.Count; detail = $r.Detail }
        [void]$sb.Append(($o | ConvertTo-Json -Compress)).Append("`n")
    }
    [System.IO.File]::AppendAllText($LogPath, $sb.ToString(), $enc)
} catch {
    Write-Warning ('prompt_check: log write failed: ' + $_.Exception.Message)
}
exit 0
