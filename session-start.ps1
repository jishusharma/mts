# session-start.ps1 - emits ONE paste-ready block with prompt + all boot content
[CmdletBinding()]
param([switch]$NoClipboard)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$manifestPath = 'MyTradingSys\mts\runtime\SESSION_MANIFEST.json'
$handoffPath  = 'MyTradingSys\mts\runtime\NEXT_SESSION_HANDOFF.md'
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
[void]$sb.AppendLine("Phases A/B/C done. Do not re-run. Mission per STATUS in handoff below.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("If a task needs more context, ask user to paste ONE dump from Dumps/ (menu at end).")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("BOOT CONTENT (do not ask for these again)")
[void]$sb.AppendLine("=" * 72)

foreach ($f in ($m.boot_files + $m.boot_supplemental)) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("### $($f.path) [$($f.role)] ###")
    $body = Get-ReadBody $f
    [void]$sb.AppendLine($body)
}

# Session log context
$events = (Get-Content $logPath -Raw | ConvertFrom-Json).events
$last = $events | Select-Object -Last 1
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### session_log context ###")
[void]$sb.AppendLine("events: $($events.Count)")
[void]$sb.AppendLine("last:   $($last.ts)  $($last.verdict)")

# Process check
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### java process ###")
$java = Get-Process java -ErrorAction SilentlyContinue | Select-Object Id, StartTime, Path
if ($java) { [void]$sb.AppendLine(($java | Out-String).Trim()) } else { [void]$sb.AppendLine("(none)") }

# Dumps menu
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("PASTE-ON-DEMAND DUMPS (ask user for one at a time)")
[void]$sb.AppendLine("=" * 72)
@"
  DUMP_CODE_JAVA.md    - Java: apparatus + state machine
  DUMP_CODE_RUNTIME.md - Python math layer
  DUMP_SYSTEM_DOCS.md  - system/ docs (behavior, status, capabilities)
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
[void]$sb.AppendLine("  - One IBC per task. Batch every read.")
[void]$sb.AppendLine("  - Rule 51 / 51(d-inline) / 52.")
[void]$sb.AppendLine("  - No blind java kill. No session_state.json thesis change. Human commits.")
[void]$sb.AppendLine("  - Read-only first. One decision per turn.")

$block = $sb.ToString()
Write-Host "generated: $($block.Length) chars"
if (-not $NoClipboard) {
    try { Set-Clipboard -Value $block; Write-Host "[copied to clipboard]" -ForegroundColor Green }
    catch { Write-Host "[clipboard fail - writing to Dumps\SESSION_PASTE.txt]" -ForegroundColor Yellow
            Set-Content -Path 'Dumps\SESSION_PASTE.txt' -Value $block -Encoding utf8 }
}
