# FILE: setup-desktop.ps1
# PURPOSE: One-time setup on the desktop (jis-nb) for NUC worker version 2.
#          1. Creates the queue folders.
#          2. Creates a dedicated local account for the NUC (no admin rights,
#             hidden from the sign-in screen).
#          3. Shares ONLY the queue folder, to that account only.
#          4. Removes the old share of the whole repository.
#          5. Removes the Everyone grant that was added to the whole
#             repository, after saving all current permissions to a backup.
#          6. Publishes the worker scripts to the queue deploy folder.
#          Safe to run again: every step checks before it acts.
# RUN:     PowerShell opened with Run as administrator, from the repository root:
#          powershell -ExecutionPolicy Bypass -File scripts\worker\setup-desktop.ps1
#Requires -RunAsAdministrator
param(
    [string]$WorkerUser = 'mtsworker',
    [string]$ShareName = 'MTS-Queue',
    [string]$OldShareName = 'MTS-Repo',
    [switch]$KeepEveryoneGrant
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Queue = Join-Path $RepoRoot 'Dumps\workers\NUC-QUEUE'
$Account = "$env:COMPUTERNAME\$WorkerUser"
function Step([string]$Message) { Write-Host "[setup] $Message" }

# 1. Queue folders
foreach ($d in 'incoming', 'claimed', 'done', 'deploy', 'specs') {
    New-Item -ItemType Directory -Force -Path (Join-Path $Queue $d) | Out-Null
}
Step "queue folders ready under $Queue"

# 2. Dedicated local account
if (-not (Get-LocalUser -Name $WorkerUser -ErrorAction SilentlyContinue)) {
    $pw = Read-Host -AsSecureString "Choose a password for the new local account $WorkerUser (typed once more on the NUC)"
    New-LocalUser -Name $WorkerUser -Password $pw -PasswordNeverExpires -UserMayNotChangePassword -AccountNeverExpires `
        -Description 'MTS NUC worker: access to the queue share only' | Out-Null
    Step "created local account $Account"
} else {
    Step "local account $Account already exists"
}
$hide = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList'
if (-not (Test-Path $hide)) { New-Item -Path $hide -Force | Out-Null }
New-ItemProperty -Path $hide -Name $WorkerUser -Value 0 -PropertyType DWord -Force | Out-Null
Step "account hidden from the sign-in screen"

# 3. Folder permission: modify, on the queue folder only
& icacls $Queue /grant "${Account}:(OI)(CI)M" /T /C /Q | Out-Null
Step "granted modify on the queue folder to $Account"

# Share permissions take the account name exactly as Windows resolves it.
# Round-trip through the SID to get that canonical name (first run failed
# with error 1332 on a hand-built name). No admin entry: the desktop uses
# the folder locally, not through the share.
$sid = (New-Object System.Security.Principal.NTAccount($Account)).Translate([System.Security.Principal.SecurityIdentifier])
$ShareAccount = $sid.Translate([System.Security.Principal.NTAccount]).Value
Step "share account resolved: $ShareAccount ($($sid.Value))"
$share = Get-SmbShare -Name $ShareName -ErrorAction SilentlyContinue
if (-not $share) {
    New-SmbShare -Name $ShareName -Path $Queue -ChangeAccess $ShareAccount | Out-Null
    Step "shared the queue folder as \\$env:COMPUTERNAME\$ShareName (change access for $ShareAccount only)"
} else {
    Step "share $ShareName already exists at $($share.Path)"
}

# 4. Old share of the whole repository (removing a share never touches files)
if (Get-SmbShare -Name $OldShareName -ErrorAction SilentlyContinue) {
    Remove-SmbShare -Name $OldShareName -Force
    Step "removed the old share $OldShareName"
} else {
    Step "old share $OldShareName not present"
}

# 5. Everyone grant on the whole repository, with a permission backup first
if (-not $KeepEveryoneGrant) {
    $backupDir = Join-Path $RepoRoot 'backup_session'
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $backup = Join-Path $backupDir ('acl-before-worker-v2-' + (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss') + '.txt')
    & icacls $RepoRoot /save $backup /T /C /Q | Out-Null
    & icacls $RepoRoot /remove:g '*S-1-1-0' /T /C /Q | Out-Null
    Step "removed the Everyone grant from the repository; previous permissions saved to $backup"
    Step ("to undo: icacls `"" + (Split-Path $RepoRoot) + "`" /restore `"$backup`"")
}

# 6. Publish the worker scripts
foreach ($f in 'nuc-worker.ps1', 'nuc-launcher.ps1', 'setup-nuc.ps1') {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $f) -Destination (Join-Path $Queue "deploy\$f") -Force
}
Step 'worker scripts published to the deploy folder'

Write-Host ''
Write-Host 'Desktop done. On the NUC, in PowerShell opened with Run as administrator:'
Write-Host '  net use Z: /delete /y'
Write-Host "  net use \\$env:COMPUTERNAME\$ShareName /user:$env:COMPUTERNAME\$WorkerUser *"
Write-Host "  powershell -ExecutionPolicy Bypass -File \\$env:COMPUTERNAME\$ShareName\deploy\setup-nuc.ps1"
