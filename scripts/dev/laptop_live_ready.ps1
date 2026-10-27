# Laptop 24/7 readiness for the live testnet loop (DESKTOP-F7IU69N; LIVE_HOST_MOVE.md section 3).
# Dry run by default: prints each setting's current value and the planned one. -Apply (elevated PowerShell) changes them.
# Re-run after a Windows feature update: they can reset power and update settings.
# Not scriptable here (do by hand): charge threshold 60-80 % per battery (Lenovo Vantage), power mode Best performance
# (Settings > System > Power), Ethernet cable, a SIM in the built-in LTE modem as backup internet.
param([switch]$Apply, [switch]$SkipTools)

if ($env:COMPUTERNAME -ne 'DESKTOP-F7IU69N') { Write-Host "refused: host is $env:COMPUTERNAME, not DESKTOP-F7IU69N (RDP window?)"; exit 1 }
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($Apply -and -not $admin) { Write-Host "refused: -Apply needs an elevated PowerShell (Run as administrator)"; exit 1 }

# power settings: subgroup GUID, setting GUID, AC value, DC value (null = leave)
$power = @(
    @{ Name = 'Sleep after (s)';            Sub = '238c9fa8-0aad-41ed-83f4-97be242c8f20'; Set = '29f6c1db-86da-48c5-9fdb-f2b67b1f44da'; AC = 0; DC = 0 },
    @{ Name = 'Hibernate after (s)';        Sub = '238c9fa8-0aad-41ed-83f4-97be242c8f20'; Set = '9d7815a6-7ee4-497e-8888-515a05f02364'; AC = 0; DC = 0 },
    @{ Name = 'Lid close (0 = do nothing)'; Sub = '4f971e89-eebd-4455-a8de-9e59040e7347'; Set = '5ca83367-6e45-459f-a27b-476b1d01c936'; AC = 0; DC = 0 },
    @{ Name = 'Energy saver on battery at %'; Sub = 'de830923-a562-41af-a086-e3a2c6bad2da'; Set = 'e69653ca-cf7f-4f05-aa73-cb833fa90ad4'; AC = $null; DC = 0 },
    @{ Name = 'Critical battery action (2 = hibernate)'; Sub = 'e73a048d-bf27-4f12-9731-8b2076e8891f'; Set = '637ea02f-bbcb-4015-8e2c-a1c7b9c0b546'; AC = 2; DC = 2 },
    @{ Name = 'Wireless adapter power (0 = max performance)'; Sub = '19cbb8fa-5279-450e-9fac-8a3d5fedd0c1'; Set = '12bbebe6-58d6-4636-95bb-3217ef867c1a'; AC = 0; DC = 0 }
)

function Get-PowerValue($sub, $set) {
    # /qh also lists hidden settings (lid close and energy saver are hidden on this scheme)
    $out = powercfg /qh SCHEME_CURRENT $sub $set 2>$null
    $fmt = {
        param($label)
        $m = $out | Select-String "Current $label Power Setting Index: (0x[0-9a-f]+)" | Select-Object -First 1
        if ($m) { [Convert]::ToInt64($m.Matches[0].Groups[1].Value, 16) } else { 'n/a' }
    }
    return @((& $fmt 'AC'), (& $fmt 'DC'))
}

Write-Host ("mode: " + $(if ($Apply) { 'APPLY' } else { 'DRY RUN (add -Apply in an elevated shell to change)' }))
Write-Host "-- power (active scheme) --"
foreach ($p in $power) {
    $cur = Get-PowerValue $p.Sub $p.Set
    Write-Host ("{0,-46} now AC={1} DC={2}  want AC={3} DC={4}" -f $p.Name, $cur[0], $cur[1], $(if ($null -eq $p.AC) { '-' } else { $p.AC }), $(if ($null -eq $p.DC) { '-' } else { $p.DC }))
    if ($Apply) {
        if ($null -ne $p.AC) { powercfg /setacvalueindex SCHEME_CURRENT $p.Sub $p.Set $p.AC }
        if ($null -ne $p.DC) { powercfg /setdcvalueindex SCHEME_CURRENT $p.Sub $p.Set $p.DC }
    }
}
if ($Apply) { powercfg /setactive SCHEME_CURRENT }

Write-Host "-- network adapters: Windows may not turn them off --"
foreach ($n in @('Wi-Fi', 'Ethernet')) {
    $pm = Get-NetAdapterPowerManagement -Name $n -ErrorAction SilentlyContinue
    Write-Host ("{0,-46} now AllowComputerToTurnOffDevice={1}  want Disabled" -f $n, $(if ($pm) { $pm.AllowComputerToTurnOffDevice } else { 'n/a (needs elevation)' }))
    # Set-NetAdapterPowerManagement has no parameter for this one: change the CIM object and pipe it back
    if ($Apply -and $pm) { $pm.AllowComputerToTurnOffDevice = 'Disabled'; $pm | Set-NetAdapterPowerManagement -ErrorAction Continue }
}

Write-Host "-- Windows Update: no automatic restart while signed in; show restart notifications --"
$reg = @(
    @{ Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'; Name = 'NoAutoRebootWithLoggedOnUsers'; Value = 1 },
    @{ Path = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'; Name = 'RestartNotificationsAllowed2'; Value = 1 }
)
foreach ($r in $reg) {
    $cur = (Get-ItemProperty -Path $r.Path -Name $r.Name -ErrorAction SilentlyContinue).($r.Name)
    Write-Host ("{0,-46} now {1}  want {2}" -f $r.Name, $(if ($null -eq $cur) { 'unset' } else { $cur }), $r.Value)
    if ($Apply) {
        if (-not (Test-Path $r.Path)) { New-Item -Path $r.Path -Force | Out-Null }
        New-ItemProperty -Path $r.Path -Name $r.Name -Value $r.Value -PropertyType DWord -Force | Out-Null
    }
}

if (-not $SkipTools) {
    Write-Host "-- tools: Git 2.40+, GitHub CLI --"
    Write-Host ("git: " + (git --version) + "; gh: " + $(if (Get-Command gh -ErrorAction SilentlyContinue) { (gh --version | Select-Object -First 1) } else { 'missing' }))
    if ($Apply) {
        winget upgrade --id Git.Git -e
        if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { winget install --id GitHub.cli -e }
        Write-Host "then, in a new terminal: gh auth login"
    }
}
Write-Host "-- by hand: Vantage charge threshold 60-80 % on both batteries; Settings power mode Best performance; Ethernet cable; LTE SIM (optional backup internet) --"
