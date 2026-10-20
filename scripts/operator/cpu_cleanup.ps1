<#
.SYNOPSIS
  Removes office-era and background services/tasks that burn CPU on JIS-NUC (owner-operated, Wi-Fi + Remote Desktop box).
.DESCRIPTION
  .\cpu_cleanup.ps1               dry run: lists what would change (default, changes nothing)
  .\cpu_cleanup.ps1 -Apply        disable + stop the SAFE list, disable the listed scheduled tasks
  .\cpu_cleanup.ps1 -Apply -Aggressive   also WSearch (indexer), SysMain, Print Spooler, Bluetooth, diagnostics (DPS)
  .\cpu_cleanup.ps1 -Restore      put every service/task back to the state saved by the last -Apply

  Before -Apply it saves the old state to F:\MTS\scratch\cpu_audit\cleanup_backup_<time>.json, so -Restore is exact.
  Kept on purpose: Intel Wi-Fi (the active link), Remote Desktop, Windows Update, Defender, the MTS-* and AIBridge tasks,
  Claude/ChatGPT services, per-user services, anything not named below. Services are disabled, never deleted.
#>
[CmdletBinding()]
param([switch]$Apply, [switch]$Aggressive, [switch]$Restore)

$ErrorActionPreference = 'Continue'
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $a = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"")
    if ($Apply) { $a += '-Apply' }
    if ($Aggressive) { $a += '-Aggressive' }
    if ($Restore) { $a += '-Restore' }
    Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList $a -Verb RunAs -Wait
    return
}

$dir = 'F:\MTS\scratch\cpu_audit'
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
try { Start-Transcript -Path (Join-Path $dir 'cpu_cleanup.log') -Force | Out-Null } catch { }

# Office-era agents, telemetry, updaters and hardware services this machine does not have (no cellular, no TPM provisioning,
# no AMT, no fingerprint reader, no scanner, no Lenovo hardware). Wi-Fi 6 AX201 and Remote Desktop are NOT in these lists.
$safe = @(
    'EraAgentSvc',                 # ESET Management Agent (old office AV console)
    'ForensiTAppxService',         # ForensiT profile-migration leftover
    'DSAService', 'DSAUpdateService',   # Intel Driver & Support Assistant
    'Mobile Broadband HL Service', # mbbService.exe, no cellular modem present
    'DiagTrack', 'dmwappushservice',    # telemetry
    'WerSvc', 'wisvc', 'MapsBroker', 'RetailDemo', 'Fax', 'XblAuthManager', 'XblGameSave',
    'edgeupdate', 'edgeupdatem', 'MicrosoftEdgeElevationService',
    'GoogleUpdaterInternalService157.0.8089.0', 'GoogleUpdaterService157.0.8089.0',
    'ClickToRunSvc',               # Office updater (Office keeps working)
    'Lenovo Instant On',           # not a Lenovo machine
    'LMS', 'Intel(R) TPM Provisioning Service', 'Intel(R) Capability Licensing Service TCP IP Interface',
    'Intel(R) SUR QC SAM', 'SystemUsageReportSvc_QUEENCREEK',
    'SmsRouter', 'SEMgrSvc', 'SCardSvr', 'ScDeviceEnum', 'WalletService', 'PhoneSvc', 'icssvc', 'WMPNetworkSvc',
    'WpcMonSvc', 'AJRouter', 'NcdAutoSetup', 'lfsvc', 'TabletInputService', 'WbioSrvc', 'stisvc',
    'SSDPSRV', 'upnphost', 'TrkWks', 'DoSvc', 'CDPSvc', 'PcaSvc'
)
$aggr = @('WSearch', 'SysMain', 'Spooler', 'PrintNotify', 'BTAGService', 'bthserv', 'RtkBtManServ', 'DPS', 'WdiServiceHost')

$tasks = @(   # [path, name]; Microsoft telemetry tasks plus third-party updaters
    @('\', 'G2MUpdateTask-S-1-5-21-687432862-3710358895-3648789087-1001'),
    @('\', 'G2MUploadTask-S-1-5-21-687432862-3710358895-3648789087-1001'),
    @('\', 'OneDrive Reporting Task-S-1-5-21-687432862-3710358895-3648789087-1001'),
    @('\', 'OneDrive Standalone Update Task-S-1-5-21-687432862-3710358895-3648789087-1001'),
    @('\Lenovo\Power Manager\', 'Background monitor'),
    @('\Microsoft\Windows\Application Experience\', 'Microsoft Compatibility Appraiser'),
    @('\Microsoft\Windows\Application Experience\', 'ProgramDataUpdater'),
    @('\Microsoft\Windows\Application Experience\', 'PcaPatchDbTask'),
    @('\Microsoft\Windows\Customer Experience Improvement Program\', 'Consolidator'),
    @('\Microsoft\Windows\Customer Experience Improvement Program\', 'UsbCeip'),
    @('\Microsoft\Windows\Windows Error Reporting\', 'QueueReporting')
)

function Svc($n) { Get-CimInstance Win32_Service -Filter "Name='$($n -replace "'", "''")'" -ErrorAction SilentlyContinue }
$modeMap = @{ Auto = 'auto'; Manual = 'demand'; Disabled = 'disabled' }

if ($Restore) {
    $f = Get-ChildItem $dir -Filter 'cleanup_backup_*.json' | Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $f) { Write-Host 'no backup found'; return }
    $b = Get-Content $f.FullName -Raw | ConvertFrom-Json
    foreach ($s in $b.services) {
        & sc.exe config $s.name start= $modeMap[$s.mode] | Out-Null
        if ($s.state -eq 'Running') { & sc.exe start $s.name | Out-Null }
        Write-Host "restored service $($s.name) -> $($s.mode)"
    }
    foreach ($t in $b.tasks) {
        if ($t.state -ne 'Disabled') { Enable-ScheduledTask -TaskPath $t.path -TaskName $t.name -ErrorAction SilentlyContinue | Out-Null; Write-Host "restored task $($t.name)" }
    }
    try { Stop-Transcript | Out-Null } catch { }
    return
}

$list = @($safe); if ($Aggressive) { $list += $aggr }
$bk = @{ time = (Get-Date).ToString('s'); services = @(); tasks = @() }
$n = 0
foreach ($name in $list) {
    $s = Svc $name
    if (-not $s) { continue }
    if ($s.StartMode -eq 'Disabled' -and $s.State -eq 'Stopped') { continue }
    $n++
    Write-Host ("{0,-8} service {1,-48} {2}/{3}" -f ($(if ($Apply) { 'disable' } else { 'would' })), $name, $s.State, $s.StartMode)
    if (-not $Apply) { continue }
    $bk.services += @{ name = $name; mode = $s.StartMode; state = $s.State }
    & sc.exe config $name start= disabled | Out-Null
    if ($s.State -eq 'Running') {
        & sc.exe stop $name | Out-Null
        $deadline = (Get-Date).AddSeconds(8)
        while ((Svc $name).State -ne 'Stopped' -and (Get-Date) -lt $deadline) { Start-Sleep 1 }
        $left = Svc $name
        if ($left.State -ne 'Stopped' -and $left.ProcessId) {
            # hung stop: end the process only when it hosts this service alone
            $others = @(Get-CimInstance Win32_Service -Filter "ProcessId=$($left.ProcessId)" | Where-Object Name -ne $name)
            if ($others.Count -eq 0) { Stop-Process -Id $left.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host "         ended hung host pid $($left.ProcessId)" }
            else { Write-Host "         still running (shares pid with $($others.Name -join ',')); gone after reboot" }
        }
    }
}
foreach ($t in $tasks) {
    $x = Get-ScheduledTask -TaskPath $t[0] -TaskName $t[1] -ErrorAction SilentlyContinue
    if (-not $x -or $x.State -eq 'Disabled') { continue }
    $n++
    Write-Host ("{0,-8} task    {1}{2}" -f ($(if ($Apply) { 'disable' } else { 'would' }), $t[0], $t[1]))
    if ($Apply) {
        $bk.tasks += @{ path = $t[0]; name = $t[1]; state = [string]$x.State }
        Disable-ScheduledTask -TaskPath $t[0] -TaskName $t[1] | Out-Null
    }
}
if ($Apply -and $n) {
    $bf = Join-Path $dir ("cleanup_backup_{0}.json" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
    $bk | ConvertTo-Json -Depth 4 | Set-Content $bf -Encoding utf8
    Write-Host "backup: $bf"
}
Write-Host "$n item(s) $(if ($Apply) { 'changed' } else { 'would change (re-run with -Apply)' })"
Write-Host 'Manual step: uninstall "ESET Management Agent" in Settings > Apps (needs no password on a standalone agent).'
try { Stop-Transcript | Out-Null } catch { }
Read-Host 'Press Enter to close' | Out-Null
