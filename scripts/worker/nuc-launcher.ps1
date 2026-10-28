# FILE: nuc-launcher.ps1
# PURPOSE: Keeps the NUC worker running. Before each start it installs a
#          newer worker from the queue deploy folder if one is there, then
#          runs it, and starts it again whenever it exits (crash, update,
#          share outage). This file is small on purpose and is not updated
#          automatically; new behavior goes into nuc-worker.ps1.
# RUN:     By the scheduled task MTS-NUC-Worker at sign-in (see setup-nuc.ps1).
# COMPAT:  Windows PowerShell 5.1.
param(
    [string]$QueueRoot = '\\jis-nb\MTS-Queue',
    [string]$LocalRoot = 'C:\MTS-Worker',
    [int]$RestartDelaySec = 20
)

$ErrorActionPreference = 'Continue'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$LogDir = Join-Path $LocalRoot 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir 'launcher.log'
$Source = Join-Path (Join-Path $QueueRoot 'deploy') 'nuc-worker.ps1'
$Target = Join-Path $LocalRoot 'nuc-worker.ps1'
$HostExe = (Get-Process -Id $PID).Path

function Write-Log([string]$Message) {
    $line = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') + " $Message"
    try { [System.IO.File]::AppendAllText($LogFile, $line + "`n", $Utf8NoBom) } catch { }
}

Write-Log "launcher started; queue $QueueRoot"
while ($true) {
    try {
        if (Test-Path -LiteralPath $Source) {
            $install = -not (Test-Path -LiteralPath $Target)
            if (-not $install) {
                $install = (Get-FileHash -LiteralPath $Source).Hash -ne (Get-FileHash -LiteralPath $Target).Hash
            }
            if ($install) {
                Copy-Item -LiteralPath $Source -Destination $Target -Force
                Write-Log ('installed worker ' + (Get-FileHash -LiteralPath $Target).Hash.Substring(0, 12).ToLower())
            }
        }
    } catch {
        Write-Log "update check failed: $($_.Exception.Message)"
    }
    if (Test-Path -LiteralPath $Target) {
        & $HostExe -NoProfile -ExecutionPolicy Bypass -File $Target -QueueRoot $QueueRoot -LocalRoot $LocalRoot
        Write-Log "worker exited with code $LASTEXITCODE"
    } else {
        Write-Log 'no worker installed yet; waiting for the queue share'
    }
    Start-Sleep -Seconds $RestartDelaySec
}
