<#
prompt_check.ps1 - blocking disk check of a composed prompt (B083, B104). Any FAIL exits 1; the composer must not print the prompt.

Input : -Path <text file>, or the prompt piped on stdin.
Output: a PASS/FAIL table (one row per check) and a final STATUS line naming each failing check. Exit code 0 when
        every check passes, 1 on any FAIL or on missing input.
Log   : one JSON line per check appended to MyTradingSys\runtime\prompt_check_log.jsonl (override with -LogPath).

Checks (B083 Fix section):
  1 paths      every path string in the prompt resolves on disk (Test-Path; bare file names resolve by name in the repo)
  2 citations  every file:line citation names a real line in that file (file:N, file:LN, file:N-M, file:N,M)
  3 tokens     every UPPER_SNAKE token on a line that cites a file is present in one of that line's files
  4 clauses    every clause with 'do not', 'never', 'must not', 'cannot' or a numeric cap is tagged OPERATOR-SET,
               is an operator verbatim line (starts with a double quote), or appears in -OperatorWords
  5 limits     no capability limit on another surface (cannot / has no / read-only / design-only ...) unless the
               operator's own words carry it (same three escapes as check 4)

  6 session-id  a session ID MTS-YYYY-MM-DD-HHMMZ-<SURF>-<ROLE> is present and its stamp is within -MaxSkewMinutes
               of the disk clock (UTC now; -NowUtc overrides for tests); a stamp typed from memory fails
  7 mode-line   a line 'Mode: live' or 'Mode: static'
  8 placeholder no angle-bracket placeholder such as <HHMM> or <ID> left in the prompt
  9 restrictions no restriction words (do not, don't, must not, never, forbidden, prohibited, off-limits, keep separate,
               not allowed) unless the line passes the check-4 escapes (OPERATOR-SET, verbatim quote, -OperatorWords)
  10 signature  a line 'P.S : All Access'
  11 line-ending (B104 C) with -Target <file>: the text under check is the content about to be written to <file>; FAIL when
               its line endings (CRLF or LF) differ from the target's on-disk line endings, or when it mixes both
               against a single-style target. No -Target, no newline in the content, a missing target (new file) or a
               target with no newline: PASS (not applicable). Give the content with -Path; stdin loses CR.
  12 surface-mismatch (B133) a prompt whose surface marker is APP must not carry the CLI launch line 'mts go'; a CLI marker
               or no marker (check 13 reports that) is not applicable
  13 surface-marker (B133) exactly one line 'SURFACE: APP' or 'SURFACE: CLI'; zero or two (or more) markers FAIL

Conventions: a path on a line marked (NEW), NEW:, CREATE: or "new file" is a file the prompt asks to create; it is
counted, not checked. Placeholders (< > * ? $ { }) and URLs are skipped.
#>
param(
    [string]$Path = '',
    [string]$RepoRoot = '',
    [string]$LogPath = '',
    [string]$OperatorWords = '',
    [string]$IgnoreTokens = '',
    [string]$NowUtc = '',
    [string]$Target = '',
    [int]$MaxSkewMinutes = 30
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
    Write-Output 'STATUS: FAIL (no prompt text was read) FAILED: input'
    exit 1
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

# 6 session ID composed from the disk clock
$idRx = 'MTS-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})Z-(CLD|APP|CLI|DSA|COD)-(SUP|BLD|ANA|EXT|MON|COO|WRK)\b'
$idM = [regex]::Match($text, $idRx)
$now = [DateTime]::UtcNow
if ($NowUtc) { $now = [DateTime]::Parse($NowUtc, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AdjustToUniversal -bor [Globalization.DateTimeStyles]::AssumeUniversal) }
if (-not $idM.Success) {
    Add-Row '6' 'session id from disk clock' $false 'no session ID MTS-YYYY-MM-DD-HHMMZ-SURF-ROLE found' 0
} else {
    $stamp = $null
    try { $stamp = New-Object DateTime ([int]$idM.Groups[1].Value), ([int]$idM.Groups[2].Value), ([int]$idM.Groups[3].Value), ([int]$idM.Groups[4].Value), ([int]$idM.Groups[5].Value), 0, ([DateTimeKind]::Utc) } catch { $stamp = $null }
    if (-not $stamp) {
        Add-Row '6' 'session id from disk clock' $false ('{0} is not a valid UTC time' -f $idM.Value) 1
    } else {
        $skew = [Math]::Abs(($now - $stamp).TotalMinutes)
        Add-Row '6' 'session id from disk clock' ($skew -le $MaxSkewMinutes) ('{0}: stamp is {1:N0} min from disk UTC {2:yyyy-MM-dd HHmm}Z (max {3})' -f $idM.Value, $skew, $now, $MaxSkewMinutes) 1
    }
}

# 7 mode line
$modeOk = [regex]::IsMatch($text, '(?im)^\s*Mode\s*:\s*(live|static)\b')
Add-Row '7' 'mode line (live / static)' $modeOk $(if ($modeOk) { 'mode line present' } else { "no line 'Mode: live' or 'Mode: static'" }) $(if ($modeOk) { 1 } else { 0 })

# 8 angle-bracket placeholders
$phs = @()
for ($i = 0; $i -lt $lines.Count; $i++) {
    foreach ($m in [regex]::Matches($lines[$i], '<[A-Za-z][A-Za-z0-9 _\-/:.]{0,40}>')) { $phs += ('L{0} {1}' -f ($i + 1), $m.Value) }
}
$d8 = '{0} placeholder(s)' -f $phs.Count
if ($phs.Count) { $d8 += ': ' + (($phs | Select-Object -First 8) -join '; ') }
Add-Row '8' 'no placeholder' ($phs.Count -eq 0) $d8 $phs.Count

# 9 restriction words the operator did not say
$restrRx = '(?i)\b(do not|don''t|must not|never|forbidden|prohibited|off-limits|keep separate|not allowed)\b'
$badRestr = @(); $nRestr = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    $ln = $lines[$i]
    if ($ln -notmatch $restrRx) { continue }
    $nRestr++
    if (-not (Test-OperatorLine $ln)) { $badRestr += ('L{0} "{1}"' -f ($i + 1), (Short $ln 70)) }
}
$d9 = '{0} restriction line(s), {1} without the operator''s words' -f $nRestr, $badRestr.Count
if ($badRestr.Count) { $d9 += ': ' + (($badRestr | Select-Object -First 8) -join '; ') }
Add-Row '9' 'no unstated restriction' ($badRestr.Count -eq 0) $d9 $nRestr

# 10 signature line
$sigOk = [regex]::IsMatch($text, '(?im)^\s*P\.S\s*:\s*All Access\b')
Add-Row '10' 'signature line' $sigOk $(if ($sigOk) { 'signature present' } else { "no line 'P.S : All Access'" }) $(if ($sigOk) { 1 } else { 0 })

# 11 write-time line-ending gate (B104 C)
function Get-Eol([string]$t) {
    $crlf = [regex]::Matches($t, "`r`n").Count
    $lf = [regex]::Matches($t, "(?<!`r)`n").Count
    $style = 'none'
    if ($crlf -gt 0 -and $lf -eq 0) { $style = 'CRLF' } elseif ($lf -gt 0 -and $crlf -eq 0) { $style = 'LF' } elseif ($crlf -gt 0 -and $lf -gt 0) { $style = 'mixed' }
    return [pscustomobject]@{ Style = $style; Crlf = $crlf; Lf = $lf }
}
$eolOk = $true; $d11 = 'no -Target given (not applicable)'; $n11 = 0
if ($Target) {
    if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) {
        $d11 = 'target not on disk (new file; not applicable)'
    } else {
        $tt = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $Target).Path)
        $te = Get-Eol $tt; $ce = Get-Eol $text; $n11 = 1
        $d11 = 'content {0} (CRLF {1}, LF {2}) vs target {3} (CRLF {4}, LF {5})' -f $ce.Style, $ce.Crlf, $ce.Lf, $te.Style, $te.Crlf, $te.Lf
        if ($ce.Style -eq 'none' -or $te.Style -eq 'none' -or $te.Style -eq 'mixed') {
            $d11 += '; not applicable'
        } elseif ($ce.Style -ne $te.Style) {
            $eolOk = $false
            $d11 += '; refuse write: line endings differ from the target'
        }
    }
}
Add-Row '11' 'write line ending matches target' $eolOk $d11 $n11

# 12 and 13 surface marker (B133)
$surfM = @([regex]::Matches($text, '(?im)^[ 	]*SURFACE[ 	]*:[ 	]*(APP|CLI)[ 	]*$'))
$surfKinds = @($surfM | ForEach-Object { $_.Groups[1].Value.ToUpper() })
$goLines = @()
for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i] -match '(?i)\bmts\s+go\b') { $goLines += ('L{0}' -f ($i + 1)) } }
if ($surfKinds.Count -eq 1 -and $surfKinds[0] -eq 'APP') {
    $d12 = if ($goLines.Count) { 'SURFACE: APP but the CLI launch line mts go is present at ' + ($goLines -join ', ') } else { 'SURFACE: APP, no mts go line' }
    Add-Row '12' 'no mts go on an App prompt' ($goLines.Count -eq 0) $d12 $goLines.Count
} else {
    Add-Row '12' 'no mts go on an App prompt' $true 'not an App prompt (see check 13); not applicable' 0
}
$d13 = '{0} surface marker line(s): {1}' -f $surfKinds.Count, $(if ($surfKinds.Count) { $surfKinds -join ', ' } else { 'none' })
Add-Row '13' 'one surface marker' ($surfKinds.Count -eq 1) $d13 $surfKinds.Count

# ---------------------------------------------------------------- report and log
Write-Output ('{0,-3} {1,-30} {2,-6} {3}' -f '#', 'CHECK', 'RESULT', 'DETAIL')
foreach ($r in $rows) { Write-Output ('{0,-3} {1,-30} {2,-6} {3}' -f $r.Id, $r.Name, $r.Status, $r.Detail) }
$failed = @($rows | Where-Object { $_.Status -eq 'FAIL' })
foreach ($r in $failed) { Write-Warning ('prompt_check FAIL check {0}: {1}' -f $r.Id, $r.Name) }
if ($failed.Count -eq 0) {
    Write-Output 'STATUS: PASS'
} else {
    Write-Output ('STATUS: FAIL ({0} of {1} checks) FAILED: {2}' -f $failed.Count, $rows.Count, (($failed | ForEach-Object { '{0} {1}' -f $_.Id, $_.Name }) -join '; '))
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
if ($failed.Count -gt 0) { exit 1 }
exit 0
