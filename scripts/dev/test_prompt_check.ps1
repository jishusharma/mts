<#
test_prompt_check.ps1 - twelve fixtures for scripts\dev\prompt_check.ps1 (B083, B104). Temp directory only: no live-tree write.

Run (repo root):  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dev\test_prompt_check.ps1
Output: one PASS/FAIL line per fixture and a final TEST STATUS line. Exit code 0 when all pass, 1 otherwise.

Expected results come from the B083 Fix section (MyTradingSys\items\B083_prompt_check_gate.md), not from the script:
  1. a fake path in the prompt            -> the path check (1) FAILs
  2. all paths valid, no clauses          -> STATUS: PASS
  3. an untagged "do not" clause          -> the clause check (4) FAILs (control: the same clause tagged OPERATOR-SET passes)
  4. an uppercase token not in the file   -> the token check (3) FAILs
  5. stale / missing session ID           -> check 6 FAILs (control: stamp equal to the injected disk clock passes)
  6. no mode line                         -> check 7 FAILs (control: 'Mode: live' passes)
  7. <HHMM> placeholder                   -> check 8 FAILs (control: filled value passes)
  8. unstated restriction words           -> check 9 FAILs (control: tagged OPERATOR-SET passes)
  9. no signature line                    -> check 10 FAILs (control: 'P.S : All Access' passes)
 10. exit code                            -> 1 on any FAIL with the failing check named in STATUS, 0 on PASS
 11. CRLF content, LF target              -> check 11 FAILs (reverse case too)
 12. LF into LF, CRLF into CRLF           -> check 11 PASS (controls)
Fixtures 5-12 are derived from the B104 item doc (MyTradingSys\items\B104_rules_vs_gates.md), not from the script.
#>
$ErrorActionPreference = 'Continue'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $here 'prompt_check.ps1'
$results = New-Object System.Collections.ArrayList

function Add-Result([string]$name, [bool]$ok, [string]$why) {
    [void]$results.Add([pscustomobject]@{ Name = $name; Ok = $ok; Why = $why })
}

if (-not (Test-Path -LiteralPath $script)) {
    Write-Output "FAIL all fixtures: $script does not exist"
    Write-Output 'TEST STATUS: FAIL (0 of 12 fixtures ran)'
    exit 1
}

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('prompt_check_test_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $tmp 'src') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tmp 'notes') -Force | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $tmp 'src\real.py'), "REAL_TOKEN = 1`nOTHER_VALUE = 2`nprint(REAL_TOKEN)`n", $utf8)
[System.IO.File]::WriteAllText((Join-Path $tmp 'notes\plan.md'), "# plan`nline two`n", $utf8)
[System.IO.File]::WriteAllText((Join-Path $tmp 'crlf_target.txt'), "one`r`ntwo`r`n", $utf8)

$nowUtc = '2026-10-04T12:00:00Z'
$hdr = "Session: MTS-2026-10-04-1200Z-APP-BLD-fixture`nMode: static`n"
$sig = "P.S : All Access`n"
function Invoke-Check([string]$promptText, [string]$tag) {
    $pf = Join-Path $tmp ($tag + '.txt')
    $lg = Join-Path $tmp ($tag + '.jsonl')
    [System.IO.File]::WriteAllText($pf, $promptText, $utf8)
    $out = (& $script -Path $pf -RepoRoot $tmp -LogPath $lg -NowUtc $nowUtc 3>$null | Out-String)
    $code = $LASTEXITCODE
    $log = @()
    if (Test-Path -LiteralPath $lg) { $log = @(Get-Content -LiteralPath $lg | ForEach-Object { $_ | ConvertFrom-Json }) }
    return [pscustomobject]@{ Out = $out; Log = $log; Code = $code }
}
function Invoke-Eol([string]$content, [string]$targetName, [string]$tag) {
    $pf = Join-Path $tmp ($tag + '.txt')
    $lg = Join-Path $tmp ($tag + '.jsonl')
    [System.IO.File]::WriteAllText($pf, $content, $utf8)
    $null = (& $script -Path $pf -RepoRoot $tmp -LogPath $lg -NowUtc $nowUtc -Target (Join-Path $tmp $targetName) 3>$null | Out-String)
    return @(Get-Content -LiteralPath $lg | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.id -eq '11' } | Select-Object -First 1)[0]
}
function Get-Row($r, [string]$id) { return ($r.Log | Where-Object { $_.id -eq $id } | Select-Object -First 1) }

try {
    # 1. fake path in prompt -> path check FAILs
    $r = Invoke-Check ($hdr + ("Read docs/never_written_file.md and src/real.py first.`nReport when done.`n") + $sig) 'f1'
    $row = Get-Row $r '1'
    Add-Result 'fixture 1: fake path -> check 1 FAIL' ($row -and $row.status -eq 'FAIL' -and $row.detail -match 'never_written_file' -and $r.Out -match 'STATUS: FAIL' -and $r.Log.Count -eq 11) ("status=" + $(if ($row) { $row.status } else { 'no row' }) + "; log rows=" + $r.Log.Count)

    # 2. all paths valid, no clauses -> STATUS PASS (a valid file:line and a present token ride along)
    $r = Invoke-Check ($hdr + ("Read src/real.py:3 and notes/plan.md first.`nsrc/real.py defines REAL_TOKEN.`nReport when done.`n") + $sig) 'f2'
    $failedRows = @($r.Log | Where-Object { $_.status -ne 'PASS' })
    Add-Result 'fixture 2: valid paths, no clauses -> STATUS PASS' ($r.Out -match 'STATUS: PASS' -and $failedRows.Count -eq 0 -and $r.Log.Count -eq 11) ("failed rows=" + $failedRows.Count + "; log rows=" + $r.Log.Count)

    # 3. untagged "do not" clause -> clause check FAILs; the tagged control passes
    $r = Invoke-Check ($hdr + ("Read src/real.py first.`nDo not touch the notes folder.`nReport when done.`n") + $sig) 'f3'
    $row = Get-Row $r '4'
    $c = Invoke-Check ($hdr + ("Read src/real.py first.`nDo not touch the notes folder (OPERATOR-SET).`nReport when done.`n") + $sig) 'f3c'
    $rowc = Get-Row $c '4'
    Add-Result 'fixture 3: untagged do-not -> check 4 FAIL (tagged control PASS)' ($row -and $row.status -eq 'FAIL' -and $rowc -and $rowc.status -eq 'PASS') ("untagged=" + $(if ($row) { $row.status } else { 'no row' }) + "; tagged=" + $(if ($rowc) { $rowc.status } else { 'no row' }))

    # 4. uppercase token not in file -> token check FAILs
    $r = Invoke-Check ($hdr + ("Read src/real.py first.`nsrc/real.py holds MISSING_TOKEN and REAL_TOKEN.`nReport when done.`n") + $sig) 'f4'
    $row = Get-Row $r '3'
    Add-Result 'fixture 4: absent token -> check 3 FAIL' ($row -and $row.status -eq 'FAIL' -and $row.detail -match 'MISSING_TOKEN' -and $row.detail -notmatch 'REAL_TOKEN not') ("status=" + $(if ($row) { $row.status } else { 'no row' }))

    # 5. session ID from disk clock: stale stamp FAILs, matching stamp passes, missing ID FAILs
    $body = "Read src/real.py first.`n"
    $r = Invoke-Check ("Session: MTS-2026-10-04-0930Z-APP-BLD-fixture`nMode: static`n" + $body + $sig) 'f5'
    $c = Invoke-Check ($hdr + $body + $sig) 'f5c'
    $n = Invoke-Check ("Mode: static`n" + $body + $sig) 'f5n'
    $row = Get-Row $r '6'; $rowc = Get-Row $c '6'; $rown = Get-Row $n '6'
    Add-Result 'fixture 5: stale/missing session ID -> check 6 FAIL (matching control PASS)' ($row.status -eq 'FAIL' -and $rown.status -eq 'FAIL' -and $rowc.status -eq 'PASS') ("stale=" + $row.status + "; missing=" + $rown.status + "; ok=" + $rowc.status)

    # 6. mode line
    $r = Invoke-Check ("Session: MTS-2026-10-04-1200Z-APP-BLD-fixture`n" + $body + $sig) 'f6'
    $c = Invoke-Check ("Session: MTS-2026-10-04-1200Z-APP-BLD-fixture`nMode: live`n" + $body + $sig) 'f6c'
    Add-Result 'fixture 6: no mode line -> check 7 FAIL (Mode: live control PASS)' ((Get-Row $r '7').status -eq 'FAIL' -and (Get-Row $c '7').status -eq 'PASS') ("no-mode=" + (Get-Row $r '7').status + "; live=" + (Get-Row $c '7').status)

    # 7. placeholder
    $r = Invoke-Check ($hdr + "Report at <HHMM> UTC.`n" + $body + $sig) 'f7'
    $c = Invoke-Check ($hdr + "Report at 1215 UTC.`n" + $body + $sig) 'f7c'
    $row = Get-Row $r '8'
    Add-Result 'fixture 7: <HHMM> placeholder -> check 8 FAIL (filled control PASS)' ($row.status -eq 'FAIL' -and $row.detail -match 'HHMM' -and (Get-Row $c '8').status -eq 'PASS') ("placeholder=" + $row.status + "; filled=" + (Get-Row $c '8').status)

    # 8. unstated restriction words (check 9; wording avoids the check-4 clause words)
    $r = Invoke-Check ($hdr + $body + "Keep separate from the notes folder; writing there is forbidden.`n" + $sig) 'f8'
    $c = Invoke-Check ($hdr + $body + "Keep separate from the notes folder; writing there is forbidden (OPERATOR-SET).`n" + $sig) 'f8c'
    Add-Result 'fixture 8: unstated restriction -> check 9 FAIL (tagged control PASS)' ((Get-Row $r '9').status -eq 'FAIL' -and (Get-Row $c '9').status -eq 'PASS') ("untagged=" + (Get-Row $r '9').status + "; tagged=" + (Get-Row $c '9').status)

    # 9. signature
    $r = Invoke-Check ($hdr + $body) 'f9'
    $c = Invoke-Check ($hdr + $body + $sig) 'f9c'
    Add-Result 'fixture 9: no signature -> check 10 FAIL (P.S : All Access control PASS)' ((Get-Row $r '10').status -eq 'FAIL' -and (Get-Row $c '10').status -eq 'PASS') ("no-sig=" + (Get-Row $r '10').status + "; sig=" + (Get-Row $c '10').status)

    # 10. exit code is blocking and names the failing check
    $r = Invoke-Check ($hdr + $body) 'f10'
    $c = Invoke-Check ($hdr + $body + $sig) 'f10c'
    Add-Result 'fixture 10: exit 1 on FAIL naming the check, exit 0 on PASS' ($r.Code -eq 1 -and $r.Out -match 'FAILED: 10 signature line' -and $c.Code -eq 0 -and $c.Out -match 'STATUS: PASS') ("fail exit=" + $r.Code + "; pass exit=" + $c.Code)

    # 11. write-time line-ending gate: CRLF content into an LF target FAILs (and the reverse)
    $base = $hdr + "Read src/real.py first.`n" + $sig
    $crlfBase = $base -replace "`n", "`r`n"
    $row = Invoke-Eol $crlfBase 'src\real.py' 'f11'
    $rev = Invoke-Eol $base 'crlf_target.txt' 'f11r'
    Add-Result 'fixture 11: CRLF content -> LF target FAILs check 11 (reverse FAILs too)' ($row.status -eq 'FAIL' -and $row.detail -match 'refuse write' -and $rev.status -eq 'FAIL') ("crlf->lf=" + $row.status + "; lf->crlf=" + $rev.status)

    # 12. controls: LF into LF, CRLF into CRLF PASS
    $c1 = Invoke-Eol $base 'src\real.py' 'f12a'
    $c2 = Invoke-Eol $crlfBase 'crlf_target.txt' 'f12b'
    Add-Result 'fixture 12: LF->LF and CRLF->CRLF PASS check 11' ($c1.status -eq 'PASS' -and $c2.status -eq 'PASS') ("lf->lf=" + $c1.status + "; crlf->crlf=" + $c2.status)
}
catch {
    Add-Result 'fixture run' $false ('exception: ' + $_.Exception.Message)
}
finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

foreach ($x in $results) { Write-Output ('{0} {1} ({2})' -f $(if ($x.Ok) { 'PASS' } else { 'FAIL' }), $x.Name, $x.Why) }
$bad = @($results | Where-Object { -not $_.Ok })
if ($results.Count -eq 12 -and $bad.Count -eq 0) {
    Write-Output 'TEST STATUS: PASS (12 of 12 fixtures)'
    exit 0
}
Write-Output ('TEST STATUS: FAIL ({0} of {1} fixtures failed or did not run)' -f [Math]::Max($bad.Count, 12 - $results.Count + $bad.Count), 12)
exit 1
