# Run ONCE on JIS-NUC in an ELEVATED PowerShell (operator). Creates the four LIVE_HOST_MOVE s5 shares.
# Verified 2026-10-21 by Supervisor B: `net share` on JIS-NUC lists only C$ F$ IPC$ ADMIN$, so none exist yet.
# It asks for the share user's password itself; nothing is stored in the repo. Re-running is safe.
#   powershell -ExecutionPolicy Bypass -File scripts\ops\nuc_create_mts_shares.ps1
param([string]$User = 'mtsshare')

$ErrorActionPreference = 'Stop'
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole('Administrator')) {
    throw 'Run this in an elevated (Administrator) PowerShell.'
}

# One local account the laptop and JIS-NB store a credential for (cmdkey /add:JIS-NUC ...).
if (-not (Get-LocalUser -Name $User -ErrorAction SilentlyContinue)) {
    $pw = Read-Host "New password for local user '$User'" -AsSecureString
    New-LocalUser -Name $User -Password $pw -PasswordNeverExpires -UserMayNotChangePassword -Description 'MTS share access (laptop, JIS-NB)' | Out-Null
}

# name -> folder, access. Data is read-only (the NUC is the only writer); the rest take CHANGE.
$shares = @(
    @{ Name = 'MTS-Data';   Path = 'F:\MTS\data';        Access = 'Read'   },
    @{ Name = 'MTS-Live';   Path = 'F:\MTS\live_owner';   Access = 'Change' },
    @{ Name = 'MTS-Mirror'; Path = 'F:\MTS\Mirror';       Access = 'Change' },
    @{ Name = 'MTS-Backup'; Path = 'F:\MTS\backup_share'; Access = 'Change' }
)
foreach ($s in $shares) {
    New-Item -ItemType Directory -Force -Path $s.Path | Out-Null
    if (Get-SmbShare -Name $s.Name -ErrorAction SilentlyContinue) { Remove-SmbShare -Name $s.Name -Force }
    if ($s.Access -eq 'Read') { New-SmbShare -Name $s.Name -Path $s.Path -ReadAccess $User | Out-Null }
    else                      { New-SmbShare -Name $s.Name -Path $s.Path -ChangeAccess $User | Out-Null }
    # NTFS side matches the share side.
    $rights = if ($s.Access -eq 'Read') { '(OI)(CI)RX' } else { '(OI)(CI)M' }
    icacls $s.Path /grant "${User}:$rights" | Out-Null
}
Get-SmbShare -Name 'MTS-*' | Format-Table Name, Path -AutoSize
Write-Host "Done. On the laptop and on JIS-NB run (once, they ask for the password):"
Write-Host "  cmdkey /add:192.168.29.110 /user:JIS-NUC\$User /pass"
Write-Host "  net use \\192.168.29.110\MTS-Live"
