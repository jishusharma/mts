# Runaway-process check (card runaway-process-leak). Read-only unless -Stop. No admin needed.
#   powershell -File scripts/operator/runaway_check.ps1 [-Stop]
# Flags any process with more than 100k handles, or an interactive-tool process (find/grep/sort/xargs/sed/awk/tail/cat) that has
# used more than 10 CPU minutes, and prints kernel pool and free memory. -Stop ends only those flagged tool processes
# (never claude, python, java, a trading process or anything else). Born from JIS-NUC 2026-10-26: find.exe, no arguments, 9 h CPU,
# 10.9 million handles, 0 MB free memory, CPU at the 100 C limit.
param([switch]$Stop, [string]$ProcessJson = '')
# -ProcessJson <file>: test input, a JSON list of {Id,Name,CPU,HandleCount,CommandLine}; skips live counters, -Stop only prints 'would stop'.
$tools = 'find','grep','sort','xargs','sed','awk','tail','cat','head','less'
$stoppable = 'find','grep','sort'   # -Stop touches only these (OURS)
$v = @{ 'available mbytes' = 99999 }
if ($ProcessJson) {
  $parsed = ConvertFrom-Json (Get-Content -Raw $ProcessJson)
  $rows = @($parsed | ForEach-Object { $_ })
  $bad = @($rows | Where-Object { $_.HandleCount -gt 100000 -or ($tools -contains $_.Name -and $_.CPU -gt 600) })
} else {
$cs = Get-CimInstance Win32_ComputerSystem
$c = (Get-Counter '\Memory\Pool Nonpaged Bytes','\Memory\Pool Paged Bytes','\Memory\Available MBytes').CounterSamples
foreach ($s in $c) { $v[$s.Path.Split([char]92)[-1]] = $s.CookedValue }
"{0}: free {1:N0} MB of {2:N0}; paged pool {3:N0} MB; nonpaged pool {4:N0} MB" -f $env:COMPUTERNAME, $v['available mbytes'],
  ($cs.TotalPhysicalMemory / 1MB), ($v['pool paged bytes'] / 1MB), ($v['pool nonpaged bytes'] / 1MB)
$bad = @(Get-Process | Where-Object { $_.HandleCount -gt 100000 -or ($tools -contains $_.Name -and $_.CPU -gt 600) })
}
foreach ($p in $bad) {
  if ($ProcessJson) { $cmd = $p.CommandLine; $st = 'test' } else { $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine; $st = $p.StartTime }
  "RUNAWAY pid {0} {1}: cpu {2:N0} s, handles {3:N0}, started {4}, cmd {5}" -f $p.Id, $p.Name, $p.CPU, $p.HandleCount, $st, $cmd
  if ($Stop -and $stoppable -contains $p.Name) {
    if ($ProcessJson) { "  would stop pid $($p.Id)" } else { Stop-Process -Id $p.Id -Force; "  stopped pid $($p.Id)" }
  }
}
if ($v['available mbytes'] -lt 1500) { "WARN: free memory under 1.5 GB" }
if ($bad.Count -eq 0) { "OK: no process over 100k handles, no long-running find/grep/sort" } else { "FOUND $($bad.Count) runaway process(es)" + $(if (-not $Stop) { ' (rerun with -Stop to end the find/grep/sort ones)' }) }
