# FILE: start-dsa-chrome.ps1
# PURPOSE: Start a separate Chrome profile for the DSA browser worker, with the
#          DevTools port open on 127.0.0.1 only. Log in to DSA in this window by
#          hand (once) and leave it open. It never touches your normal Chrome.
# RUN:     powershell -ExecutionPolicy Bypass -File scripts\worker\start-dsa-chrome.ps1
[CmdletBinding()]
param([int]$Port = 9222, [string]$Root = 'F:\MTS\dsa')

$ErrorActionPreference = 'Stop'
$candidates = @(
    (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe')
)
$chrome = $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
if (-not $chrome) { Write-Error 'chrome.exe not found in Program Files or LocalAppData'; exit 1 }

# Working storage lives on F: (operator 2026-09-29): profile, downloads, logs under $Root.
$profileDir  = Join-Path $Root 'chrome-profile'
$downloadDir = Join-Path $Root 'downloads'
foreach ($d in @($profileDir, $downloadDir, (Join-Path $Root 'logs'))) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
# First start only: seed the profile's download folder (Chrome reads Default\Preferences at launch).
$prefDir = Join-Path $profileDir 'Default'
$prefFile = Join-Path $prefDir 'Preferences'
if (-not (Test-Path $prefFile)) {
    New-Item -ItemType Directory -Force -Path $prefDir | Out-Null
    $prefs = @{ download = @{ default_directory = $downloadDir; prompt_for_download = $false } } | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($prefFile, $prefs, (New-Object System.Text.UTF8Encoding($false)))
}
$args = @(
    "--remote-debugging-port=$Port",
    '--remote-debugging-address=127.0.0.1',
    "--user-data-dir=$profileDir",
    '--no-first-run'
)
Write-Host "Starting $chrome (profile $profileDir, DevTools on 127.0.0.1:$Port only)"
Start-Process -FilePath $chrome -ArgumentList $args
