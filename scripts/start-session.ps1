# start-session.ps1 - one-command session start.
#
# Does three things in one run:
#   1. Generates Dumps\SESSION_PASTE.txt from the boot manifest.
#   2. Loads the shortcuts into the current PowerShell window.
#   3. Prints one line telling you what to do next.
#
# Usage:
#   cd scripts
#   .\start-session.ps1
#
# Flags:
#   -NoClipboard    do not copy to clipboard (file is still written)
#   -NoLoad         do not load the shortcuts

[CmdletBinding()]
param(
  [switch]$NoClipboard,
  [switch]$NoLoad
)

$ErrorActionPreference = 'Stop'

function Write-TextNoBom {
    param([string]$Path, [string]$Text)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) $Path), $Text, $utf8NoBom)
}

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# Fresh build check before assembling paste.
try {
    & (Join-Path $root 'scripts\Build-Check.ps1')
} catch {
    Write-Host "Build-Check failed: $_" -ForegroundColor Yellow
}

$manifestPath = 'MyTradingSys\mts\runtime\SESSION_MANIFEST.json'
$logPath      = 'MyTradingSys\mts\runtime\session_log.json'

$m = Get-Content $manifestPath -Raw | ConvertFrom-Json

# Session name for the chat UI. Format: MTS YYYY-MM-DD HH:MM
$sessionName = 'MTS-' + [DateTime]::UtcNow.ToString('yyyy-MM-dd-HHmm') + 'Z'

function Get-ReadBody {
    param($f)
    if (-not (Test-Path $f.path)) { return "MISSING: $($f.path)" }
    switch ($f.read) {
        'full'        { return (Get-Content $f.path -Raw) }
        'tail'        { $n = if ($f.lines) { [int]$f.lines } else { 60 }; return ((Get-Content $f.path -Tail $n) -join "`n") }
        'part_I'      { return (((Get-Content $f.path -Raw) -split '(?im)^##\s+Part\s+II\b',2)[0]) }
        'latest_glob' {
            $file = Get-ChildItem $f.path -Filter $f.pattern | Sort-Object LastWriteTime -Descending | Select-Object -First $f.count
            if ($file) { return (Get-Content $file.FullName -Raw) } else { return "(no snapshot)" }
        }
        'skip'        { return "(skipped - see session_log context below)" }
        'open_only'   {
            $src = Get-Content $f.path -Raw
            $kept = New-Object System.Collections.Generic.List[string]
            $kept.Add('(CLOSED and WONTFIX rows omitted; full file at ' + $f.path + ')')
            foreach ($ln in ($src -split "`n")) {
                if ($ln -match '^\| [BT]\d{3} ') {
                    $parts = $ln -split '\|'
                    if ($parts.Count -ge 5) {
                        $status = $parts[3].Trim()
                        if ($status -eq 'CLOSED' -or $status -eq 'WONTFIX') { continue }
                    }
                }
                $kept.Add($ln)
            }
            return ($kept -join "`n")
        }
        'sections'    {
            $src = Get-Content $f.path -Raw
            $names = @($f.sections)
            $kept = New-Object System.Collections.Generic.List[string]
            $emit = $false
            foreach ($ln in ($src -split "`n")) {
                if ($ln -match '^## ') {
                    $title = $ln.Substring(3).Trim()
                    $emit = $false
                    foreach ($n in $names) {
                        if ($title -like ($n + '*')) { $emit = $true; break }
                    }
                }
                if ($emit) { $kept.Add($ln) }
            }
            return ($kept -join "`n")
        }
        'head_to_end' {
            $content = Get-Content $f.path -Raw
            $idx = $content.IndexOf("`n# END")
            if ($idx -ge 0) { return $content.Substring(0, $idx).TrimEnd() }
            return $content
        }
        default       { return (Get-Content $f.path -Raw) }
    }
}

$sb = [System.Text.StringBuilder]::new()

[void]$sb.AppendLine("Resuming MTS. Paste-once session start.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("Session name: $sessionName")
[void]$sb.AppendLine("Set your chat title in the UI to exactly this.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("Role: state your role (COORDINATOR or WORKER) per DSA_SESSION_PROMPT.md section 1.")
[void]$sb.AppendLine("Boot: all content is in this file. Confirm the manifest, run the build check.")
[void]$sb.AppendLine("If build status is not PASS, stop and report. Do not proceed.")
[void]$sb.AppendLine("Read the current-state section of the prompt. Then state role and mission.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("If a task needs more context, ask for ONE dump from Dumps/ (menu at end).")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("BOOT CONTENT (all files, read the whole block)")
[void]$sb.AppendLine("=" * 72)

foreach ($f in ($m.boot_files + $m.boot_supplemental)) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("### $($f.path) [$($f.role)] ###")
    $body = Get-ReadBody $f
    [void]$sb.AppendLine($body)
}

# SESSION_MANIFEST.json raw (boot rule 3.1)
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### SESSION_MANIFEST.json [manifest_raw] ###")
[void]$sb.AppendLine((Get-Content $manifestPath -Raw))

# Reference index. Files on disk not pasted. Request by path + line range.
$refPaths = @(
    @{ path='MyTradingSys/mts/research/AUDIT_2026-09-17_TRACKER.md'; role='audit_work' },
    @{ path='MyTradingSys/mts/research/LOOP_LIFECYCLE_DESIGN_2026-09-19.md'; role='plan' },
    @{ path='MyTradingSys/mts/research/EXTRACTION_TO_ALERT_AUDIT_2026-09-19.md'; role='audit' },
    @{ path='MyTradingSys/mts/runtime/SESSION_RESUME.md'; role='historical' },
    @{ path='MyTradingSys/mts/research/L_ITEMS_MASTER.md'; role='frozen' },
    @{ path='MyTradingSys/mts/research/INDICATOR_IMPLEMENTATION_HANDOFF.md'; role='research' },
    @{ path='MyTradingSys/PROJECT_VISION.md'; role='direction' },
    @{ path='MyTradingSys/mts/research/TOM_VERBATIM_INDEX.md'; role='citation_index' },
    @{ path='MyTradingSys/mts/research/schema_v5.1.0_spec.md'; role='schema' },
    @{ path='MyTradingSys/mts/research/open_loops_status.md'; role='stale_loops' },
    @{ path='MyTradingSys/mts/research/compiled_output_audit_20260915.md'; role='audit' }
)
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### REFERENCE INDEX (not pasted; request by path + line range) ###")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("| Path | Lines | Hash8 | mtime | Role |")
[void]$sb.AppendLine("|---|---|---|---|---|")
foreach ($r in $refPaths) {
    $fp = Join-Path $root $r.path
    if (Test-Path $fp) {
        $lineCount = (Get-Content $fp -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
        $hash8 = (Get-FileHash $fp -Algorithm SHA256).Hash.Substring(0,8)
        $mt = (Get-Item $fp).LastWriteTimeUtc.ToString('yyyy-MM-dd')
        [void]$sb.AppendLine("| $($r.path) | $lineCount | $hash8 | $mt | $($r.role) |")
    } else {
        [void]$sb.AppendLine("| $($r.path) | MISSING | - | - | $($r.role) |")
    }
}
[void]$sb.AppendLine("")
[void]$sb.AppendLine("Directories:")
[void]$sb.AppendLine("  MyTradingSys/mts/conditions/  - MTS rule files")
[void]$sb.AppendLine("  MyTradingSys/extracts/        - analyst extracts")
[void]$sb.AppendLine("  raw_transcripts_canonical/    - Tom transcripts")
[void]$sb.AppendLine("  Dumps/workers/                - worker dispatches and replies")
$events = (Get-Content $logPath -Raw | ConvertFrom-Json).events | Sort-Object ts
$last = $events | Select-Object -Last 1
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### session_log context ###")
[void]$sb.AppendLine("events: $($events.Count)")
[void]$sb.AppendLine("latest by timestamp: $($last.ts)  $($last.verdict)")
[void]$sb.AppendLine("last 5 entries:")
foreach ($e in ($events | Select-Object -Last 5)) {
    [void]$sb.AppendLine("  $($e.ts)  $($e.verdict)  $($e.reason)")
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### java process ###")
$java = Get-Process java -ErrorAction SilentlyContinue | Select-Object Id, StartTime, Path
if ($java) { [void]$sb.AppendLine(($java | Out-String).Trim()) } else { [void]$sb.AppendLine("(none)") }

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### git state ###")
try {
    $gHead  = (& git -C $root rev-parse --short HEAD 2>$null)
    $gDirty = (& git -C $root status --short 2>$null | Measure-Object -Line).Lines
    $gTag   = (& git -C $root describe --tags --abbrev=0 2>$null)
    [void]$sb.AppendLine("HEAD:  $gHead")
    [void]$sb.AppendLine("Tag:   $gTag")
    [void]$sb.AppendLine("Dirty: $gDirty file(s)")
    if ($gDirty -gt 0) {
        [void]$sb.AppendLine("Dirty files:")
        (& git -C $root status --short 2>$null) | ForEach-Object { [void]$sb.AppendLine("  $_") }
    }
} catch {
    [void]$sb.AppendLine("(git unavailable)")
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### loop health ###")
$lockPath = Join-Path $root 'data\apparatus.lock'
if (Test-Path $lockPath) {
    $lockLine = (Get-Content $lockPath -Raw).Trim()
    [void]$sb.AppendLine("lock:      $lockLine")
} else {
    [void]$sb.AppendLine("lock:      none")
}
$newest = Get-ChildItem (Join-Path $root 'data\snapshots\BTCUSDT_*.json') -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$snapAgeMin = $null
if ($newest) {
    $snapAgeMin = [math]::Round(((Get-Date) - $newest.LastWriteTime).TotalMinutes, 1)
    [void]$sb.AppendLine("snapshot:  $($newest.Name)  age=$snapAgeMin min")
} else {
    [void]$sb.AppendLine("snapshot:  none")
}
$stateFile = Join-Path $root 'MyTradingSys\mts\runtime\state_code.json'
$stAgeMin = $null
if (Test-Path $stateFile) {
    $stAgeMin = [math]::Round(((Get-Date) - (Get-Item $stateFile).LastWriteTime).TotalMinutes, 1)
    [void]$sb.AppendLine("state_code: age=$stAgeMin min")
}
$javaProc = Get-Process java -ErrorAction SilentlyContinue
$supProc = Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'loop-supervisor' }
[void]$sb.AppendLine("java:      $(if ($javaProc) { 'present' } else { 'absent' })")
[void]$sb.AppendLine("supervisor: $(if ($supProc) { 'present' } else { 'absent' })")
$healthReasons = @()
if (-not $javaProc) { $healthReasons += 'java_absent' }
if (-not $supProc)  { $healthReasons += 'supervisor_absent' }
if ($null -eq $snapAgeMin -or $snapAgeMin -gt 5) { $healthReasons += "snapshot_age=$(if ($null -eq $snapAgeMin) { 'missing' } else { $snapAgeMin })" }
if ($null -eq $stAgeMin -or $stAgeMin -gt 5)     { $healthReasons += "state_code_age=$(if ($null -eq $stAgeMin) { 'missing' } else { $stAgeMin })" }
if ($healthReasons.Count -eq 0) {
    [void]$sb.AppendLine("loop health: PASS")
    Write-Host "loop health: PASS" -ForegroundColor Green
} else {
    $reasonStr = ($healthReasons -join ',')
    [void]$sb.AppendLine("loop health: FAIL reason=$reasonStr")
    Write-Host "loop health: FAIL reason=$reasonStr" -ForegroundColor Red
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### scripts inventory ###")
$scriptFiles = Get-ChildItem (Join-Path $root 'scripts') -Recurse -File -Include '*.ps1' -ErrorAction SilentlyContinue | Sort-Object FullName
foreach ($sf in $scriptFiles) {
    $rel = $sf.FullName.Replace((Join-Path $root 'scripts') + '\','')
    [void]$sb.AppendLine("  $rel")
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### COMMANDS.md ###")
$cmdPath = Join-Path $root 'COMMANDS.md'
if (Test-Path $cmdPath) {
    # Wrap contiguous 4-space-indented blocks in powershell fences for one-click copy.
    $cmdLines = Get-Content $cmdPath
    $inBlock = $false
    foreach ($cl in $cmdLines) {
        $isIndent = ($cl -match '^    ') -and ($cl.Trim().Length -gt 0)
        if ($isIndent -and -not $inBlock) {
            [void]$sb.AppendLine('```powershell')
            $inBlock = $true
        }
        if (-not $isIndent -and $inBlock) {
            [void]$sb.AppendLine('```')
            $inBlock = $false
        }
        [void]$sb.AppendLine($cl)
    }
    if ($inBlock) { [void]$sb.AppendLine('```') }
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("PASTE-ON-DEMAND DUMPS (ask for one at a time)")
[void]$sb.AppendLine("=" * 72)
@"
  dump_java.md             - Java source
  dump_runtime.md          - Python math layer + runtime
  dump_system_support.md   - system/ docs
  dump_conditions.md       - MTS rule files
  dump_methodology.md      - Tom methodology + playbook
  dump_research.md         - research notes
  dump_cards.md            - historical trade cards
  dump_data.md             - schemas + sample snapshot
  dump_tests.md            - test suite
  dump_extracts.md         - Tom transcripts
  dump_core.md             - behavior + index
  alert_audit_Q2.csv / Q3Q4.csv - alert audit data
"@ -split "`n" | ForEach-Object { [void]$sb.AppendLine($_) }

[void]$sb.AppendLine("")
[void]$sb.AppendLine("Constraints:")
[void]$sb.AppendLine("  - USER.md binds. Terse. Answer first. No emoji.")
[void]$sb.AppendLine("  - One block at a time. Long pastes split with a confirmation between each.")
[void]$sb.AppendLine("  - Read-only first. One decision per turn.")
[void]$sb.AppendLine("  - No blind java kill. No session_state.json thesis change without approval.")
[void]$sb.AppendLine("  - Plain language. No codes. No shorthand.")

$block = $sb.ToString()
Write-Host "generated: $($block.Length) chars"

$sizeKb = [math]::Round($block.Length / 1024, 1)
Write-Host "paste size: $sizeKb KB"
if ($sizeKb -gt 80) {
    Write-Host "WARNING: paste over 80 KB (DSA section 2 threshold)" -ForegroundColor Yellow
    $contrib = @()
    foreach ($f in ($m.boot_files + $m.boot_supplemental)) {
        $body = Get-ReadBody $f
        $contrib += [PSCustomObject]@{ path=$f.path; size=$body.Length }
    }
    $contrib | Sort-Object size -Descending | Select-Object -First 3 | ForEach-Object {
        Write-Host ("  {0}  {1} KB" -f $_.path, [math]::Round($_.size/1024,1))
    }
}

$pasteFile = 'Dumps\SESSION_PASTE.txt'
Write-TextNoBom -Path $pasteFile -Text $block
Write-Host "written:   $pasteFile" -ForegroundColor Cyan

if (-not $NoClipboard) {
    try { Set-Clipboard -Value $block; Write-Host "[copied to clipboard]" -ForegroundColor Green }
    catch { Write-Host "[clipboard unavailable - use $pasteFile]" -ForegroundColor Yellow }
}

if (-not $NoLoad) {
    . "$PSScriptRoot\load.ps1"
}

Write-Host ""
Write-Host ""
Write-Host "====================== SESSION NAME ======================" -ForegroundColor Yellow
Write-Host "  $sessionName" -ForegroundColor Yellow
Write-Host "  Set your chat title to exactly this." -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "NEXT: open $pasteFile, select all, copy, paste into a fresh chat." -ForegroundColor Cyan
Write-Host "      shortcuts loaded: live quick deltas trend snapshot overview health alerts mts-start gitsnap gitsee gitundo" -ForegroundColor Cyan