<#
test_prompt_check.ps1 - four fixtures for scripts\dev\prompt_check.ps1 (B083). Temp directory only: no live-tree write.

Run (repo root):  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dev\test_prompt_check.ps1
Output: one PASS/FAIL line per fixture and a final TEST STATUS line. Exit code 0 when all pass, 1 otherwise
(the exit code is data; nothing reads it to stop anything).

Expected results come from the B083 Fix section (MyTradingSys\items\B083_prompt_check_gate.md), not from the script:
  1. a fake path in the prompt            -> the path check (1) FAILs
  2. all paths valid, no clauses          -> STATUS: PASS
  3. an untagged "do not" clause          -> the clause check (4) FAILs (control: the same clause tagged OPERATOR-SET passes)
  4. an uppercase token not in the file   -> the token check (3) FAILs
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
    Write-Output 'TEST STATUS: FAIL (0 of 4 fixtures ran)'
    exit 1
}

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('prompt_check_test_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $tmp 'src') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tmp 'notes') -Force | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $tmp 'src\real.py'), "REAL_TOKEN = 1`nOTHER_VALUE = 2`nprint(REAL_TOKEN)`n", $utf8)
[System.IO.File]::WriteAllText((Join-Path $tmp 'notes\plan.md'), "# plan`nline two`n", $utf8)

function Invoke-Check([string]$promptText, [string]$tag) {
    $pf = Join-Path $tmp ($tag + '.txt')
    $lg = Join-Path $tmp ($tag + '.jsonl')
    [System.IO.File]::WriteAllText($pf, $promptText, $utf8)
    $out = (& $script -Path $pf -RepoRoot $tmp -LogPath $lg 3>$null | Out-String)
    $log = @()
    if (Test-Path -LiteralPath $lg) { $log = @(Get-Content -LiteralPath $lg | ForEach-Object { $_ | ConvertFrom-Json }) }
    return [pscustomobject]@{ Out = $out; Log = $log }
}
function Get-Row($r, [string]$id) { return ($r.Log | Where-Object { $_.id -eq $id } | Select-Object -First 1) }

try {
    # 1. fake path in prompt -> path check FAILs
    $r = Invoke-Check ("Read docs/never_written_file.md and src/real.py first.`nReport when done.`n") 'f1'
    $row = Get-Row $r '1'
    Add-Result 'fixture 1: fake path -> check 1 FAIL' ($row -and $row.status -eq 'FAIL' -and $row.detail -match 'never_written_file' -and $r.Out -match 'STATUS: FAIL' -and $r.Log.Count -eq 5) ("status=" + $(if ($row) { $row.status } else { 'no row' }) + "; log rows=" + $r.Log.Count)

    # 2. all paths valid, no clauses -> STATUS PASS (a valid file:line and a present token ride along)
    $r = Invoke-Check ("Read src/real.py:3 and notes/plan.md first.`nsrc/real.py defines REAL_TOKEN.`nReport when done.`n") 'f2'
    $failedRows = @($r.Log | Where-Object { $_.status -ne 'PASS' })
    Add-Result 'fixture 2: valid paths, no clauses -> STATUS PASS' ($r.Out -match 'STATUS: PASS' -and $failedRows.Count -eq 0 -and $r.Log.Count -eq 5) ("failed rows=" + $failedRows.Count + "; log rows=" + $r.Log.Count)

    # 3. untagged "do not" clause -> clause check FAILs; the tagged control passes
    $r = Invoke-Check ("Read src/real.py first.`nDo not touch the notes folder.`nReport when done.`n") 'f3'
    $row = Get-Row $r '4'
    $c = Invoke-Check ("Read src/real.py first.`nDo not touch the notes folder (OPERATOR-SET).`nReport when done.`n") 'f3c'
    $rowc = Get-Row $c '4'
    Add-Result 'fixture 3: untagged do-not -> check 4 FAIL (tagged control PASS)' ($row -and $row.status -eq 'FAIL' -and $rowc -and $rowc.status -eq 'PASS') ("untagged=" + $(if ($row) { $row.status } else { 'no row' }) + "; tagged=" + $(if ($rowc) { $rowc.status } else { 'no row' }))

    # 4. uppercase token not in file -> token check FAILs
    $r = Invoke-Check ("Read src/real.py first.`nsrc/real.py holds MISSING_TOKEN and REAL_TOKEN.`nReport when done.`n") 'f4'
    $row = Get-Row $r '3'
    Add-Result 'fixture 4: absent token -> check 3 FAIL' ($row -and $row.status -eq 'FAIL' -and $row.detail -match 'MISSING_TOKEN' -and $row.detail -notmatch 'REAL_TOKEN not') ("status=" + $(if ($row) { $row.status } else { 'no row' }))
}
catch {
    Add-Result 'fixture run' $false ('exception: ' + $_.Exception.Message)
}
finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

foreach ($x in $results) { Write-Output ('{0} {1} ({2})' -f $(if ($x.Ok) { 'PASS' } else { 'FAIL' }), $x.Name, $x.Why) }
$bad = @($results | Where-Object { -not $_.Ok })
if ($results.Count -eq 4 -and $bad.Count -eq 0) {
    Write-Output 'TEST STATUS: PASS (4 of 4 fixtures)'
    exit 0
}
Write-Output ('TEST STATUS: FAIL ({0} of {1} fixtures failed or did not run)' -f [Math]::Max($bad.Count, 4 - $results.Count + $bad.Count), 4)
exit 1
