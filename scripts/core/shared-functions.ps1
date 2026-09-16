# Shared functions used by more than one core script.
# Add a function here only when two or more scripts need it.

function Get-Descendants([int]$rootPid) {
    $out = New-Object System.Collections.Generic.List[int]
    $queue = New-Object System.Collections.Generic.Queue[int]
    $queue.Enqueue($rootPid)
    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$parent" -ErrorAction SilentlyContinue
        foreach ($c in $children) {
            $cid = [int]$c.ProcessId
            $out.Add($cid)
            $queue.Enqueue($cid)
        }
    }
    return $out
}
