# Runaway-process check (card runaway-process-leak). Read-only unless -Stop. No admin needed.
#   powershell -File scripts/operator/runaway_check.ps1 [-Stop]
# Flags any process with more than 100k handles, or an interactive-tool process (find/grep/sort/xargs/sed/awk/tail/cat) that has
# used more than 10 CPU minutes, and prints kernel pool and free memory. -Stop ends only those flagged tool processes
# (never claude, python, java, a trading process or anything else). Born from JIS-NUC 2026-10-26: find.exe, no arguments, 9 h CPU,
# 10.9 million handles, 0 MB free memory, CPU at the 100 C limit.
param([switch]$Stop)
$tools = 'find','grep','sort','xargs','sed','awk','tail','cat','head','less'
$cs = Get-CimInstance Win32_ComputerSystem
$c = (Get-Counter '\Memory\Pool Nonpaged Bytes','\Memory\Pool Paged Bytes','\Memory\Available MBytes').CounterSamples
$v = @{}; foreach ($s in $c) { $v[$s.Path.Split('\')[-1]] = $s.CookedValue }
"{0}: free {1:N0} MB of {2:N0}; paged pool {3:N0} MB; nonpaged pool {4:N0} MB" -f $env:COMPUTERNAME, $v['available mbytes'],
  ($cs.TotalPhysicalMemory / 1MB), ($v['pool paged bytes'] / 1MB), ($v['pool nonpaged bytes'] / 1MB)
$bad = @(Get-Process | Where-Object { $_.HandleCount -gt 100000 -or ($tools -contains $_.Name -and $_.CPU -gt 600) })
foreach ($p in $bad) {
  $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
  "RUNAWAY pid {0} {1}: cpu {2:N0} s, handles {3:N0}, started {4}, cmd {5}" -f $p.Id, $p.Name, $p.CPU, $p.HandleCount, $p.StartTime, $cmd
  if ($Stop -and $tools -contains $p.Name) { Stop-Process -Id $p.Id -Force; "  stopped pid $($p.Id)" }
}
if ($v['available mbytes'] -lt 1500) { "WARN: free memory under 1.5 GB" }
if ($bad.Count -eq 0) { "OK: no process over 100k handles, no long-running find/grep/sort" } else { "FOUND $($bad.Count) runaway process(es)" + $(if (-not $Stop) { ' (rerun with -Stop to end the find/grep/sort ones)' }) }
