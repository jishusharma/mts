# B138: finish the Dumps move from C: to F:. One script, one quiet window.
# Run on JIS-NB only, as E-ngineers, in a normal (non-admin) pwsh:
#   pwsh -File move_dumps_to_F.ps1            (dry run: checks and counts only, changes nothing)
#   pwsh -File move_dumps_to_F.ps1 -Apply     (does the move)
# Run -Apply only after the supervisor / flashing-fix thread confirms no one else
# is changing the live system. This script never stops a process, never touches
# HALT files, trades or scheduled tasks, and never deletes anything: the old
# folder is renamed Dumps.pre_B138 and kept.
# Rollback (any time): rmdir the junction (removes only the link), then rename
# Dumps.pre_B138 back to Dumps.

param([switch]$Apply)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed'
$Src  = Join-Path $Repo 'Dumps'
$Dst  = 'F:\MTS\Dumps'
$Old  = Join-Path $Repo 'Dumps.pre_B138'

function Fail($m) { Write-Host "ABORT: $m" -ForegroundColor Red; exit 1 }
function Info($m) { Write-Host $m }

if ($env:COMPUTERNAME -ne 'JIS-NB') { Fail "this is $env:COMPUTERNAME, not JIS-NB" }
if (-not (Test-Path $Src)) { Fail "$Src not found" }
if ((Get-Item $Src).Attributes -band [IO.FileAttributes]::ReparsePoint) { Fail "$Src is already a junction; nothing to do" }
if (Test-Path $Old) { Fail "$Old already exists; resolve it first" }
if (-not (Test-Path 'F:\MTS')) { Fail 'F:\MTS not found' }

$tracked = & git -C $Repo ls-files -- Dumps
if ($tracked) { Fail "git tracks files under Dumps ($(@($tracked).Count)); a junction would confuse git. Ask the supervisor." }

$srcStat = Get-ChildItem $Src -Recurse -File -Force | Measure-Object Length -Sum
$free = (Get-PSDrive F).Free
Info ("C: Dumps: {0} files, {1:N0} MB. F: free: {2:N0} MB" -f $srcStat.Count, ($srcStat.Sum/1MB), ($free/1MB))
if ($free -lt ($srcStat.Sum * 2)) { Fail 'F: has less than 2x the Dumps size free' }

$share = Get-SmbShare -Name 'MTS-Queue' -ErrorAction SilentlyContinue
if ($share) { Info "MTS-Queue share path now: $($share.Path)" } else { Info 'MTS-Queue share not found (ok if not created here)' }

Info 'Dry-run of the first copy (what would be copied to F:):'
robocopy $Src $Dst /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /L /NJH /NP /NDL /NFL | Select-Object -Last 12

if (-not $Apply) { Info 'Dry run only. Nothing changed. Re-run with -Apply in the agreed window.'; exit 0 }

Info '1/5 bulk copy C: -> F: (live, nothing removed on F:)'
robocopy $Src $Dst /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /NP /NFL /NDL | Select-Object -Last 10
if ($LASTEXITCODE -ge 8) { Fail "robocopy failed with exit $LASTEXITCODE; nothing was changed on C:" }

Info '2/5 rename C: Dumps -> Dumps.pre_B138 (fails if any process holds files open)'
try { Rename-Item -Path $Src -NewName 'Dumps.pre_B138' }
catch { Fail "rename refused (something has Dumps open): $($_.Exception.Message). C: is unchanged." }

try {
    Info '3/5 final delta copy'
    robocopy $Old $Dst /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /NP /NFL /NDL | Select-Object -Last 10
    if ($LASTEXITCODE -ge 8) { throw "delta copy failed with exit $LASTEXITCODE" }

    Info '4/5 create junction C:\...\Dumps -> F:\MTS\Dumps'
    New-Item -ItemType Junction -Path $Src -Target $Dst | Out-Null
}
catch {
    Write-Host "ERROR: $($_.Exception.Message) - rolling back" -ForegroundColor Red
    if (Test-Path $Src) { cmd /c rmdir "$Src" | Out-Null }
    Rename-Item -Path $Old -NewName 'Dumps'
    exit 1
}

Info '5/5 verify'
$a = Get-ChildItem $Old -Recurse -File -Force | Measure-Object Length -Sum
$b = Get-ChildItem $Src -Recurse -File -Force | Measure-Object Length -Sum
Info ("old: {0} files {1} bytes | through junction: {2} files {3} bytes" -f $a.Count, $a.Sum, $b.Count, $b.Sum)
$probe = Join-Path $Src 'workers\NUC-QUEUE\_b138_probe.tmp'
Set-Content -Path $probe -Value 'ok' -Encoding ascii
$ok = Test-Path (Join-Path $Dst 'workers\NUC-QUEUE\_b138_probe.tmp')
Remove-Item $probe
if ($share) { Info ("share path resolves: " + (Test-Path "\\JIS-NB\MTS-Queue")) }
if ($ok -and $b.Count -ge $a.Count) {
    Info 'DONE. Keep Dumps.pre_B138 for a few days, then archive it with scripts\dev\declutter_backups.py.'
} else {
    Fail 'verification failed. Roll back: cmd /c rmdir the junction, then rename Dumps.pre_B138 back to Dumps.'
}
