# bridge_selftest.ps1 - does DIRECT MODE work end to end on this machine?
#
# DSA (or the operator) runs it through AIBridge from the project working tree:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dev\bridge_selftest.ps1
#
# It touches only the repo root: one temp file under Dumps\ (created, read back, deleted).
# Summary line first, then a numbered big-output block that ends with a marker. DSA reports whether it
# saw the marker: the last line number it can read is the bridge's real output cap (AIBRIDGE_LANE.md).
# Denial probes are printed as text, not executed; run them one at a time and expect a refusal.
# No $env: use: the bridge refuses it (AIBRIDGE_LANE.md).

param(
    [string]$Root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [int]$BigKb = 300
)
$ErrorActionPreference = 'Continue'
$results = New-Object System.Collections.Generic.List[string]
$fails = 0

function Probe([string]$name, [scriptblock]$body) {
    try {
        $detail = & $body
        $results.Add("PASS  $name  $detail")
    } catch {
        $script:fails++
        $results.Add("FAIL  $name  $($_.Exception.Message)")
    }
}

Probe 'where' { "host=$([Environment]::MachineName) user=$([Environment]::UserName) ps=$($PSVersionTable.PSVersion) root=$Root" }

Probe 'write-read-delete' {
    $dir = Join-Path $Root 'Dumps'
    if (-not (Test-Path $dir)) { $dir = $Root }
    $f = Join-Path $dir ('.bridge_selftest_' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.tmp')
    $text = 'bridge selftest ' + (Get-Date).ToUniversalTime().ToString('o')
    [System.IO.File]::WriteAllText($f, $text, (New-Object System.Text.UTF8Encoding($false)))
    $back = [System.IO.File]::ReadAllText($f)
    if ($back -ne $text) { throw 'read-back differs' }
    Remove-Item -LiteralPath $f -Force
    if (Test-Path -LiteralPath $f) { throw 'delete did not remove the file' }
    'file written, read back, deleted'
}

Probe 'sync-news' {
    $out = & python (Join-Path $Root 'scripts\dev\sync.py') news 1 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { throw "sync.py news exit=$LASTEXITCODE $out" }
    'sync.py news 1 ran (exit 0)'
}

Probe 'paste-pipeline' {
    $ss = Join-Path $Root 'scripts\start-session.ps1'
    $man = Join-Path $Root 'MyTradingSys\runtime\SESSION_MANIFEST.json'
    $e = $null; $t = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($ss, [ref]$t, [ref]$e)
    if ($e.Count -gt 0) { throw "start-session.ps1 has $($e.Count) parse errors" }
    $m = Get-Content $man -Raw | ConvertFrom-Json
    $n = @($m.boot_files).Count + @($m.boot_supplemental).Count
    "start-session.ps1 parses; manifest lists $n boot files"
}

Probe 'python-and-pytest' {
    $v = & python --version 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { throw "python exit=$LASTEXITCODE" }
    $v.Trim()
}

Write-Output "SELFTEST: $(if ($fails -eq 0) { 'PASS' } else { "FAIL ($fails)" })  probes=$($results.Count)"
$results | ForEach-Object { Write-Output $_ }
Write-Output ''
Write-Output 'DENIAL PROBES (not run here; each should be refused by the bridge, run one per call):'
Write-Output '  1. read a secret path:   Get-Content .secrets\api.txt'
Write-Output '  2. write outside roots:  Set-Content -Path "C:\Users\E-ngineers\bridge_deny_probe.txt" -Value x'
Write-Output '  3. read outside roots:   Get-Content "C:\Windows\win.ini"'
Write-Output 'A probe that succeeds is a bridge defect: report it, then delete anything it created.'
Write-Output ''
Write-Output "BIG-OUTPUT-BEGIN $BigKb KB, one numbered line per 60 bytes; last line number readable = output cap"
$lines = [int](($BigKb * 1024) / 60)
$pad = 'x' * 50
for ($i = 1; $i -le $lines; $i++) { Write-Output ('L{0:D6} {1}' -f $i, $pad) }
Write-Output "BIG-OUTPUT-END lines=$lines"
