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
        'tail'        { return ((Get-Content $f.path -Tail $f.lines) -join "`n") }
        'part_I'      { return (((Get-Content $f.path -Raw) -split '(?im)^##\s+Part\s+II\b',2)[0]) }
        'latest_glob' {
            $file = Get-ChildItem $f.path -Filter $f.pattern | Sort-Object LastWriteTime -Descending | Select-Object -First $f.count
            if ($file) { return (Get-Content $file.FullName -Raw) } else { return "(no snapshot)" }
        }
        'skip'        { return "(skipped - see session_log context below)" }
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

# Audit tracker, inlined when present (active audit sessions only)
$auditPath = Join-Path $root 'MyTradingSys\mts\research\AUDIT_2026-09-17_TRACKER.md'
if (Test-Path $auditPath) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("### MyTradingSys/mts/research/AUDIT_2026-09-17_TRACKER.md [active_audit] ###")
    [void]$sb.AppendLine((Get-Content $auditPath -Raw))
}
$events = (Get-Content $logPath -Raw | ConvertFrom-Json).events | Sort-Object ts
$last = $events | Select-Object -Last 1
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### session_log context ###")
[void]$sb.AppendLine("events: $($events.Count)")
[void]$sb.AppendLine("latest by timestamp: $($last.ts)  $($last.verdict)")

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
if ($newest) {
    $ageMin = [math]::Round(((Get-Date) - $newest.LastWriteTime).TotalMinutes, 1)
    [void]$sb.AppendLine("snapshot:  $($newest.Name)  age=$ageMin min")
} else {
    [void]$sb.AppendLine("snapshot:  none")
}
$stateFile = Join-Path $root 'MyTradingSys\mts\runtime\state_code.json'
if (Test-Path $stateFile) {
    $stAge = [math]::Round(((Get-Date) - (Get-Item $stateFile).LastWriteTime).TotalMinutes, 1)
    [void]$sb.AppendLine("state_code: age=$stAge min")
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### scripts inventory ###")
$scriptFiles = Get-ChildItem (Join-Path $root 'scripts') -Recurse -File -Include '*.ps1' -ErrorAction SilentlyContinue | Sort-Object FullName
foreach ($sf in $scriptFiles) {
    $rel = $sf.FullName.Replace((Join-Path $root 'scripts') + '\','')
    [void]$sb.AppendLine("  $rel")
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### MTS_DICTIONARY - CANONICAL FIELDS ###")
$dictPath = Join-Path $root 'MyTradingSys\mts\research\MTS_DICTIONARY.md'
if (Test-Path $dictPath) {
    $dict = Get-Content $dictPath -Raw
    if ($dict -match '(?s)## CANONICAL FIELDS.*?(?=\r?\n## |\z)') {
        [void]$sb.AppendLine($Matches[0])
    }
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### COMMANDS.md ###")
$cmdPath = Join-Path $root 'COMMANDS.md'
if (Test-Path $cmdPath) {
    [void]$sb.AppendLine((Get-Content $cmdPath -Raw))
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