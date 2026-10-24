# NUC shutdown check (card nuc-unexpected-shutdown). Read-only, no admin.
#   powershell -File scripts/operator/nuc_health.ps1 [-Days 7] [-Fix]
# Prints: hard resets (Kernel-Power 142/41, EventLog 6008), standby entries (506), the applied settings,
# last logger sample. -Fix re-applies display-off=Never on AC and Fast Startup off (HiberbootEnabled needs admin).
param([int]$Days = 7, [switch]$Fix)
$since = (Get-Date).AddDays(-$Days)

function Events($ids, $provider) {
  $f = @{LogName = 'System'; Id = $ids; StartTime = $since}
  if ($provider) { $f.ProviderName = $provider }
  Get-WinEvent -FilterHashtable $f -ErrorAction SilentlyContinue | Sort-Object TimeCreated
}

$boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
"NUC health, last $Days day(s); boot $boot; now $(Get-Date)"
$wd = @(Events 142 'Microsoft-Windows-Kernel-Power')
$k41 = @(Events 41 'Microsoft-Windows-Kernel-Power')
$sb = @(Events 506 'Microsoft-Windows-Kernel-Power')
"hard resets (event 142, watchdog): $($wd.Count)"
$wd | ForEach-Object { "  {0:yyyy-MM-dd HH:mm:ss}" -f $_.TimeCreated }
"unclean boots (event 41): $($k41.Count)"
"standby entries (event 506): $($sb.Count)"
$sb | Select-Object -Last 3 | ForEach-Object { "  {0:yyyy-MM-dd HH:mm:ss}" -f $_.TimeCreated }

$mon = (powercfg /q SCHEME_CURRENT SUB_VIDEO VIDEOIDLE | Select-String 'Current AC').Line.Trim()
$fs = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -ErrorAction SilentlyContinue).HiberbootEnabled
"settings: display-off $mon ; HiberbootEnabled=$fs"
if ($Fix) {
  powercfg /change monitor-timeout-ac 0
  "re-applied display-off AC = Never (Fast Startup needs: reg add HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power /v HiberbootEnabled /t REG_DWORD /d 0 /f in an admin shell)"
}

$log = Join-Path $env:LOCALAPPDATA 'MTS\logs\nuc_watch.csv'
if (Test-Path $log) { "logger: $((Get-Item $log).Length) bytes, last write $((Get-Item $log).LastWriteTime); last line:"; Get-Content $log -Tail 1 }
else { "logger: not running (start: powershell -File scripts/operator/nuc_watch.ps1)" }

if ($wd.Count -eq 0 -and $k41.Count -eq 0) { "VERDICT: no hard resets in $Days day(s)" }
else { "VERDICT: $($wd.Count) watchdog reset(s), $($k41.Count) unclean boot(s) in $Days day(s)" }
