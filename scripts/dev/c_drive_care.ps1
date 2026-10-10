<#
c_drive_care.ps1 - keep C: from filling. Report by default; -Apply does only the SAFE deletes below.

  powershell -File scripts\dev\c_drive_care.ps1                         report only (sizes + free space), deletes nothing
  powershell -File scripts\dev\c_drive_care.ps1 -Apply                  delete: user TEMP files older than 7 days,
                                                                         Chrome Cache / Code Cache / GPUCache (all profiles; only if Chrome is closed)
  ... -Apply -IncludeServiceWorkerCache                                  also Chrome Service Worker CacheStorage + ScriptCache

NEVER touched: Chrome Cookies, Login Data, Local Storage, IndexedDB, Extensions, Preferences, Network (these hold logins
and settings). Never touched: Claude vm_bundles (operator decision, see DEVICES.md section 6), repo, F:, D:.
Log: %LOCALAPPDATA%\MTS-DiskCare\c_drive_latest.md (overwritten each run). WARN line when C: free is below 15 GB.
#>
param([switch]$Apply, [switch]$IncludeServiceWorkerCache, [double]$WarnFreeGB = 15)
$ErrorActionPreference = 'Continue'
$logDir = Join-Path $env:LOCALAPPDATA 'MTS-DiskCare'
New-Item -ItemType Directory -Force $logDir | Out-Null
$lines = New-Object System.Collections.Generic.List[string]
function Say($t) { $lines.Add($t); Write-Output $t }

function DirBytes($p) {
    if (-not (Test-Path -LiteralPath $p)) { return 0 }
    $m = Get-ChildItem -LiteralPath $p -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum
    if ($m.Sum) { return [long]$m.Sum } else { return 0 }
}
function GB($b) { return [math]::Round($b / 1GB, 2) }

$c = Get-PSDrive C
$freeBefore = $c.Free
Say ("# C: drive care {0}  mode={1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $(if ($Apply) { 'APPLY' } else { 'REPORT' }))
Say ("C: free {0} GB of {1} GB" -f (GB $c.Free), (GB ($c.Free + $c.Used)))
if ($c.Free / 1GB -lt $WarnFreeGB) { Say ("WARN: C: free is below {0} GB" -f $WarnFreeGB) }

# --- candidates ---
$chromeRoot = Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data'
$chromeOpen = [bool](Get-Process chrome -ErrorAction SilentlyContinue)
$cacheDirs = @()
if (Test-Path $chromeRoot) {
    foreach ($prof in Get-ChildItem $chromeRoot -Directory | Where-Object { $_.Name -match '^(Default|Profile \d+)$' }) {
        $names = @('Cache', 'Code Cache', 'GPUCache')
        if ($IncludeServiceWorkerCache) { $names += @('Service Worker\CacheStorage', 'Service Worker\ScriptCache') }
        foreach ($n in $names) { $cacheDirs += Join-Path $prof.FullName $n }
    }
}
$tempDir = $env:TEMP
$cutoff = (Get-Date).AddDays(-7)

Say ''
Say '## Sizes (GB)'
$chromeTotal = 0L
foreach ($d in $cacheDirs) { $chromeTotal += DirBytes $d }
Say ("Chrome cache dirs (safe to clear, Chrome open={0}): {1}" -f $chromeOpen, (GB $chromeTotal))
$m = Get-ChildItem -LiteralPath $tempDir -Recurse -Force -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt $cutoff } | Measure-Object Length -Sum
$tempOld = if ($m.Sum) { [long]$m.Sum } else { 0 }
Say ("User TEMP files older than 7 days: {0}" -f (GB $tempOld))
$vm = Join-Path $env:LOCALAPPDATA 'Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\vm_bundles'
Say ("Claude vm_bundles (REPORT ONLY, never deleted here): {0}" -f (GB (DirBytes $vm)))
Say ("Chrome profile total (REPORT ONLY): {0}" -f (GB (DirBytes $chromeRoot)))
Say ("Windows Update download cache (REPORT ONLY; use Disk Cleanup 'system files'): {0}" -f (GB (DirBytes 'C:\Windows\SoftwareDistribution\Download')))

# --- apply ---
if ($Apply) {
    Say ''
    Say '## Apply'
    if ($chromeOpen) {
        Say 'SKIP Chrome cache: Chrome is running (close every Chrome window, then re-run).'
    } else {
        foreach ($d in $cacheDirs) {
            if (Test-Path -LiteralPath $d) {
                Get-ChildItem -LiteralPath $d -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                Say ("cleared {0}" -f $d)
            }
        }
    }
    $n = 0
    if (Test-Path $tempDir) {
        Get-ChildItem -LiteralPath $tempDir -Recurse -Force -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt $cutoff } |
            ForEach-Object { try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop; $n++ } catch {} }
    }
    Say ("removed {0} old TEMP files (in-use files are skipped)" -f $n)
    $after = (Get-PSDrive C).Free
    Say ("C: free after {0} GB (freed {1} GB)" -f (GB $after), (GB ($after - $freeBefore)))
}

$lines | Set-Content -Path (Join-Path $logDir 'c_drive_latest.md') -Encoding UTF8
