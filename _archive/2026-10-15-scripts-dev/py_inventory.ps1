# py_inventory.ps1 - read-only inventory of python processes: pid|ppid|parent-name|start|MB|cpu-s|cmd. Kills nothing.
$all = Get-CimInstance Win32_Process
$ids = @{}
foreach ($p in $all) { $ids[[int]$p.ProcessId] = $p }
$all | Where-Object { $_.Name -match '^pythonw?\.exe$' } | Sort-Object CreationDate | ForEach-Object {
  $par = $ids[[int]$_.ParentProcessId]
  $pn = if ($par) { $par.Name } else { 'PARENT-DEAD' }
  $cpu = (Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue).CPU
  $cmd = $_.CommandLine.Replace('C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\', '').Replace('C:\Users\E-ngineers\IdeaProjects\', '')
  '{0}|{1}|{2}|{3}|{4}MB|{5}|{6}' -f $_.ProcessId, $_.ParentProcessId, $pn, $_.CreationDate.ToString('MM-dd HH:mm'), [int]($_.WorkingSetSize / 1MB), [int]$cpu, $cmd
}
