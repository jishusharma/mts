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


# BOM-free write helpers. PS 5.1 Set-Content -Encoding UTF8 always
# writes a BOM. Use these instead. Added 2026-09-16.
function Write-NoBom {
    param([string]$Path, [string]$Text)
    $enc = New-Object System.Text.UTF8Encoding($false)
    $full = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path (Get-Location) $Path }
    [System.IO.File]::WriteAllText($full, $Text, $enc)
}
function Write-NoBomLines {
    param([string]$Path, [string[]]$Lines)
    $enc = New-Object System.Text.UTF8Encoding($false)
    $full = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path (Get-Location) $Path }
    [System.IO.File]::WriteAllLines($full, $Lines, $enc)
}
function Test-HasBom {
    param([string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $Path))
    if ($bytes.Length -lt 3) { return $false }
    return ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
}