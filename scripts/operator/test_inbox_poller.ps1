# Offline test: poll cycles with a stub `claude` first on PATH.
$ErrorActionPreference = 'Stop'
$t = Join-Path ([IO.Path]::GetTempPath()) ("optest_" + [guid]::NewGuid().ToString('N').Substring(0,8))
$bin = Join-Path $t 'bin'; $root = Join-Path $t 'operator'; $calls = Join-Path $t 'calls.txt'
New-Item -ItemType Directory -Force $bin,$root | Out-Null
# stub: logs args + stdin, prints a reply
$stub = "@echo off`r`necho %* >> `"$calls`"`r`nfindstr /R `".*`" >> `"$calls`"`r`necho STUB REPLY`r`n"
[IO.File]::WriteAllText((Join-Path $bin 'claude.cmd'), $stub)
$oldPath = $env:PATH; $env:PATH = "$bin;$oldPath"
$poller = Join-Path $PSScriptRoot 'inbox_poller.ps1'
$ask = Join-Path $PSScriptRoot 'ask.ps1'
$fail = @()
try {
    & $poller -Once -Root $root -RepoRoot $t | Out-Null
    if (Test-Path $calls) { $fail += 'empty inbox called stub' }
    & $ask "hello world" -Model opus -Root $root | Out-Null
    & $poller -Once -Root $root -RepoRoot $t | Out-Null
    if (-not (Test-Path $calls)) { $fail += 'stub not called' } else {
        $c = Get-Content $calls -Raw
        if ($c -notmatch '--model opus') { $fail += 'model flag missing' }
        if ($c -notmatch 'hello world') { $fail += 'request text not passed' }
    }
    if (@(Get-ChildItem "$root\inbox" -File).Count) { $fail += 'inbox not empty' }
    if (@(Get-ChildItem "$root\done" -Filter req_*.md).Count -ne 1) { $fail += 'request not in done' }
    $r = @(Get-ChildItem "$root\outbox" -Filter *.reply.md)
    if ($r.Count -ne 1 -or (Get-Content $r[0].FullName -Raw) -notmatch 'STUB REPLY') { $fail += 'reply missing/wrong' }
    # CLI-missing path (only checkable if no real claude elsewhere on PATH)
    Remove-Item (Join-Path $bin 'claude.cmd')
    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Start-Sleep -Seconds 1; & $ask "second" -Root $root | Out-Null; & $poller -Once -Root $root -RepoRoot $t | Out-Null
        $m = Get-ChildItem "$root\outbox" -Filter *.reply.md | Sort-Object Name | Select-Object -Last 1
        if ((Get-Content $m.FullName -Raw) -notmatch 'CLI missing') { $fail += 'no CLI-missing reply' }
    }
} finally { $env:PATH = $oldPath; Remove-Item $t -Recurse -Force -ErrorAction SilentlyContinue }
if ($fail) { Write-Output ("FAIL: " + ($fail -join '; ')); exit 1 } else { Write-Output 'PASS' }
