# scripts\core\session-start.ps1 - emits paste-ready session-start block.
[CmdletBinding()]
param([switch]$NoClipboard)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$manifestPath = 'MyTradingSys\mts\runtime\SESSION_MANIFEST.json'
$handoffPath  = 'MyTradingSys\mts\runtime\NEXT_SESSION_HANDOFF.md'
$logPath      = 'MyTradingSys\mts\runtime\session_log.json'

$m = Get-Content $manifestPath -Raw | ConvertFrom-Json
$boot = New-Object System.Collections.Generic.List[string]

$emit = {
    param($f)
    switch ($f.read) {
        'full'        { $boot.Add("Get-Content $($f.path)") }
        'skip'        { $boot.Add("# skip $($f.path) - see Step 4 context") }
        'tail'        { $boot.Add("Get-Content $($f.path) -Tail $($f.lines)") }
        'part_I'      { $boot.Add("(Get-Content $($f.path) -Raw) -split '(?im)^##\s+Part\s+II\b',2 | Select-Object -First 1") }
        'latest_glob' { $boot.Add("Get-ChildItem $($f.path) -Filter '$($f.pattern)' | Sort-Object LastWriteTime -Descending | Select-Object -First $($f.count) | ForEach-Object { Get-Content `$_.FullName }") }
        default       { $boot.Add("Get-Content $($f.path)") }
    }
}
$m.boot_files        | ForEach-Object { & $emit $_ }
$m.boot_supplemental | ForEach-Object { & $emit $_ }

$events   = (Get-Content $logPath -Raw | ConvertFrom-Json).events
$last     = $events | Select-Object -Last 1
$lastLine = "{0}  {1}" -f $last.ts, $last.verdict

# STATUS block = first lines of handoff up to first blank line
$statusLines = Get-Content $handoffPath -TotalCount 20 |
    Where-Object { $_ -match '^STATUS' } |
    ForEach-Object { "  $_" }
$statusBlock = if ($statusLines) { $statusLines -join "`n" } else { "  STATUS: (missing)" }

$sep = "`n    "
$block = @"
Resuming MTS.

Role: state your role (COORDINATOR or WORKER) per DSA_SESSION_PROMPT.md section 1.

Step 1 - Load aliases:
    . .\scripts\load.ps1

Step 2 - Boot block (one IBC, one turn):
    $($boot -join $sep)

Step 3 - Health check:
    lh
    Get-Process java -ErrorAction SilentlyContinue | Select-Object Id, StartTime, Path

Step 4 - Context:
$statusBlock
  session_log events: $($events.Count)
  Last event:         $lastLine

Step 4b - Paste-on-demand menu (Dumps/):
  Session must ask user for one dump if the task needs it. Never assume contents.
    DUMP_CODE_JAVA.md   - Java: apparatus + state machine
    DUMP_SYSTEM_DOCS.md - system/ folder (docs, status, behavior, capabilities)
    DUMP_CODE_RUNTIME.md- Python math layer
    DUMP_CONDITIONS.md  - MTS rule files
    DUMP_METHODOLOGY.md - Tom methodology
    DUMP_RESEARCH.md    - research notes
    DUMP_CARDS.md       - historical trade cards
    DUMP_DATA.md        - schemas + sample snapshot
    DUMP_TESTS.md       - test suite
    DUMP_EXTRACTS.md    - Tom transcripts (788KB)
    alert_audit_Q2.csv / alert_audit_Q3Q4.csv - alert audit data
  Rule: one dump per ask. Wait for paste before proceeding.

Step 5 - Mission: per STATUS above. Skip any phase marked done. Full handoff is in the boot block.

Constraints:
  - USER.md binds. Terse. Answer first. No emoji.
  - One IBC per task. Batch every read.
  - Rule 51 (intent/challenge/execute/outcome). Rule 51(d-inline). Rule 52.
  - No blind java kill. No session_state.json thesis change. Human commits.
  - Read-only first. One decision per turn.
"@

Write-Host $block
if (-not $NoClipboard) {
    try { Set-Clipboard -Value $block; Write-Host "`n[copied]" -ForegroundColor Green }
    catch { Write-Host "`n[clipboard unavailable]" -ForegroundColor Yellow }
}
