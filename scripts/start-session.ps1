# start-session.ps1 - one-command session start.
#
# Does three things in one run:
#   1. Generates Dumps\SESSION_PASTE.txt from the boot manifest.
#   2. Loads the shortcuts (quick, deltas, trend, snapshot, overview,
#      health, alerts) into the current PowerShell window.
#   3. Prints one line telling you what to do next.
#
# Usage:
#   cd scripts
#   .\start-session.ps1
#
# Flags:
#   -NoClipboard    do not copy the paste to clipboard (file is still written)
#   -NoLoad         do not load the shortcuts

[CmdletBinding()]
param(
  [switch]$NoClipboard,
  [switch]$NoLoad
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$manifestPath = 'MyTradingSys\mts\runtime\SESSION_MANIFEST.json'
$logPath      = 'MyTradingSys\mts\runtime\session_log.json'

$m = Get-Content $manifestPath -Raw | ConvertFrom-Json

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
[void]$sb.AppendLine("Role: state your role (COORDINATOR or WORKER) per DSA_SESSION_PROMPT.md section 1.")
[void]$sb.AppendLine("Boot procedure: read SESSION_MANIFEST.json first, then read boot files in batches.")
[void]$sb.AppendLine("Confirm each batch in one line. Do not read them all at once.")
[void]$sb.AppendLine("Build check runs before any write. If status is not PASS, stop.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("If a task needs more context, ask for ONE dump from Dumps/ (menu at end).")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("BOOT CONTENT (read in batches, confirm each batch in one line)")
[void]$sb.AppendLine("=" * 72)

foreach ($f in ($m.boot_files + $m.boot_supplemental)) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("### $($f.path) [$($f.role)] ###")
    $body = Get-ReadBody $f
    [void]$sb.AppendLine($body)
}

$events = (Get-Content $logPath -Raw | ConvertFrom-Json).events
$last = $events | Select-Object -Last 1
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### session_log context ###")
[void]$sb.AppendLine("events: $($events.Count)")
[void]$sb.AppendLine("last:   $($last.ts)  $($last.verdict)")

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### java process ###")
$java = Get-Process java -ErrorAction SilentlyContinue | Select-Object Id, StartTime, Path
if ($java) { [void]$sb.AppendLine(($java | Out-String).Trim()) } else { [void]$sb.AppendLine("(none)") }

[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("PASTE-ON-DEMAND DUMPS (ask for one at a time)")
[void]$sb.AppendLine("=" * 72)
@"
  DUMP_CODE_JAVA.md    - Java: runtime + state machine
  DUMP_CODE_RUNTIME.md - Python math layer
  DUMP_SYSTEM_DOCS.md  - system/ docs
  DUMP_CONDITIONS.md   - MTS rule files
  DUMP_METHODOLOGY.md  - Tom methodology + playbook
  DUMP_RESEARCH.md     - research notes
  DUMP_CARDS.md        - historical trade cards
  DUMP_DATA.md         - schemas + sample snapshot
  DUMP_TESTS.md        - test suite
  DUMP_EXTRACTS.md     - Tom transcripts (788KB)
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
Set-Content -Path $pasteFile -Value $block -Encoding utf8
Write-Host "written:   $pasteFile" -ForegroundColor Cyan

if (-not $NoClipboard) {
    try { Set-Clipboard -Value $block; Write-Host "[copied to clipboard]" -ForegroundColor Green }
    catch { Write-Host "[clipboard unavailable - use $pasteFile]" -ForegroundColor Yellow }
}

if (-not $NoLoad) {
    . "$PSScriptRoot\load.ps1"
}

Write-Host ""
Write-Host "NEXT: open $pasteFile, select all, copy, paste into a fresh chat." -ForegroundColor Cyan
Write-Host "      shortcuts loaded in this window: quick, deltas, trend, snapshot, overview, health, alerts" -ForegroundColor Cyan