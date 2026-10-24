# Crash-forensics logger for the NUC (card nuc-unexpected-shutdown). Not a scheduled task: start it by hand, it ends when the
# machine hangs or you stop it. Appends one CSV row every -Seconds to %LOCALAPPDATA%\MTS\logs\nuc_watch.csv (C:, outside
# the repo, never committed). After a freeze the last row is the machine's state in the last seconds before it died.
#   powershell -File scripts/operator/nuc_watch.ps1 [-Seconds 5]
param([int]$Seconds = 5)
$dir = Join-Path $env:LOCALAPPDATA 'MTS\logs'
New-Item -ItemType Directory -Force $dir | Out-Null
$csv = Join-Path $dir 'nuc_watch.csv'
if (-not (Test-Path $csv) -or (Get-Item $csv).Length -gt 50MB) {
  'time,cpu_pct,cpu_mhz_pct,temp_k_max,mem_avail_mb,disk_busy_pct,disk_lat_ms,disk_wr_mbs,net_mbs' | Set-Content $csv -Encoding ascii
}
$c = @(
  '\Processor Information(_Total)\% Processor Utility',
  '\Processor Information(_Total)\% Processor Performance',
  '\Thermal Zone Information(*)\Temperature',
  '\Memory\Available MBytes',
  '\PhysicalDisk(_Total)\% Disk Time',
  '\PhysicalDisk(_Total)\Avg. Disk sec/Transfer',
  '\PhysicalDisk(_Total)\Disk Write Bytes/sec',
  '\Network Interface(*)\Bytes Total/sec'
)
while ($true) {
  try {
    $s = (Get-Counter -Counter $c -ErrorAction SilentlyContinue).CounterSamples
    $v = { param($p) ($s | Where-Object Path -like $p | Measure-Object CookedValue -Maximum).Maximum }
    $row = '{0:yyyy-MM-dd HH:mm:ss},{1:F0},{2:F0},{3:F0},{4:F0},{5:F0},{6:F1},{7:F1},{8:F1}' -f (Get-Date),
      (& $v '*processor utility*'), (& $v '*processor performance*'), (& $v '*thermal zone*'), (& $v '*available mbytes*'),
      (& $v '*physicaldisk(_total)*disk time*'), ((& $v '*avg. disk sec/transfer*') * 1000),
      ((& $v '*disk write bytes*') / 1MB), ((& $v '*network interface*bytes total*') / 1MB)
    Add-Content $csv $row -Encoding ascii
  } catch {}
  Start-Sleep -Seconds $Seconds
}
