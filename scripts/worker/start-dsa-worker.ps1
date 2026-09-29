# FILE: start-dsa-worker.ps1
# PURPOSE: Run the DSA browser worker on the DESKTOP (JIS-NB) with its log on F:.
#          Queue = the local repo queue (same machine, no share). Chrome must already be
#          running via start-dsa-chrome.ps1 and logged in to DSA.
# RUN:     powershell -ExecutionPolicy Bypass -File scripts\worker\start-dsa-worker.ps1 [-Once] [-Calibrate]
[CmdletBinding()]
param([switch]$Once, [switch]$Calibrate, [string]$Root = 'F:\MTS\dsa')

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$logDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmm'
$pyArgs = @('-u', (Join-Path $repo 'scripts\worker\dsa_worker.py'))
if ($Once) { $pyArgs += '--once' }
if ($Calibrate) { $pyArgs += '--calibrate' }
if ($Once -or $Calibrate) {
    & python @pyArgs 2>&1 | Tee-Object -FilePath (Join-Path $logDir "dsa_worker_$stamp.log")
    exit $LASTEXITCODE
}
Start-Process -FilePath python -ArgumentList $pyArgs -WorkingDirectory $repo -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $logDir "dsa_worker_$stamp.out") -RedirectStandardError (Join-Path $logDir "dsa_worker_$stamp.err")
Write-Host "DSA worker started; logs in $logDir; queue $repo\Dumps\workers\NUC-QUEUE (lane incoming_dsa)"
