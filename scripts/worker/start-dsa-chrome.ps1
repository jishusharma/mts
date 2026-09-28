# FILE: start-dsa-chrome.ps1
# PURPOSE: Start a separate Chrome profile for the DSA browser worker, with the
#          DevTools port open on 127.0.0.1 only. Log in to DSA in this window by
#          hand (once) and leave it open. It never touches your normal Chrome.
# RUN:     powershell -ExecutionPolicy Bypass -File scripts\worker\start-dsa-chrome.ps1
[CmdletBinding()]
param([int]$Port = 9222)

$ErrorActionPreference = 'Stop'
$candidates = @(
    (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe')
)
$chrome = $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
if (-not $chrome) { Write-Error 'chrome.exe not found in Program Files or LocalAppData'; exit 1 }

$profileDir = Join-Path $env:LOCALAPPDATA 'mts-dsa-chrome'
$args = @(
    "--remote-debugging-port=$Port",
    '--remote-debugging-address=127.0.0.1',
    "--user-data-dir=$profileDir",
    '--no-first-run'
)
Write-Host "Starting $chrome (profile $profileDir, DevTools on 127.0.0.1:$Port only)"
Start-Process -FilePath $chrome -ArgumentList $args
