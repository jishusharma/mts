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
  [string]$Manifest = 'MyTradingSys\runtime\SESSION_MANIFEST.json',
  [string]$Out = 'Dumps\SESSION_PASTE.txt',
  [switch]$FullBuild,
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

# Build check before assembling paste. The full tier is ~100 s (math tests alone 78 s), so:
#   - last report is a full PASS and no Java/Python source is newer than it -> reuse it, say so
#   - otherwise -> quick tier (compile + registry checks)
#   - -FullBuild forces the full tier
$reportPath = Join-Path $root 'MyTradingSys\runtime\BUILD_REPORT.md'
$buildMode  = 'quick'
$buildWhy   = ''
if ($FullBuild) {
    $buildMode = 'full'; $buildWhy = '-FullBuild'
} elseif (Test-Path $reportPath) {
    $rep = Get-Content $reportPath -Raw
    $okFull = ($rep -match '(?m)^STATUS: PASS\s*$')
    $repTime = (Get-Item $reportPath).LastWriteTimeUtc
    $roots = @((Join-Path $root 'src'), (Join-Path $root 'MyTradingSys')) | Where-Object { Test-Path $_ }
    $newer = Get-ChildItem $roots -Recurse -File -Include '*.java','*.py' -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\(research|archive|runtime_data|__pycache__)\\' -and $_.LastWriteTimeUtc -gt $repTime } |
        Select-Object -First 1
    $pom = Join-Path $root 'pom.xml'
    if (-not $newer -and (Test-Path $pom) -and (Get-Item $pom).LastWriteTimeUtc -gt $repTime) { $newer = Get-Item $pom }
    if ($okFull -and -not $newer) {
        $buildMode = 'reuse'
        $buildWhy  = "full PASS from $([math]::Round(((Get-Date).ToUniversalTime() - $repTime).TotalMinutes)) min ago, no source newer"
    } elseif ($newer) {
        $buildWhy = "source newer than report: $($newer.Name)"
    } else {
        $buildWhy = 'last report is not a full PASS'
    }
}
Write-Host "build check: $buildMode ($buildWhy)" -ForegroundColor Cyan
if ($buildMode -ne 'reuse') {
    try {
        if ($buildMode -eq 'full') { & (Join-Path $root 'scripts\Build-Check.ps1') }
        else                       { & (Join-Path $root 'scripts\Build-Check.ps1') -Quick }
    } catch {
        Write-Host "Build-Check failed: $_" -ForegroundColor Yellow
    }
}

$manifestPath = $Manifest
$logPath      = 'MyTradingSys\runtime\session_log.json'

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
        'pointer'     { return "(not pasted; read it through the AIRUN boot block, DSA_SESSION_PROMPT.md section 3: $($f.path))" }
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
[void]$sb.AppendLine("")
[void]$sb.AppendLine("Role: BUILDER (bridge connected, the default), RUN-AND-REPORT or WORKER (no bridge) per DSA_SESSION_PROMPT.md section 1.")
[void]$sb.AppendLine("Boot: prompt section 3 - your own worktree for this chat, then # AIRUN task=mts-boot, then python scripts/dev/dsa.py boot. Facts about this machine (Java, Maven, build status) come only from that output.")
[void]$sb.AppendLine("Build check: the report below counts only for the host it names (prompt section 3). A FAIL is work to fix or route, not a reason to stop.")
[void]$sb.AppendLine("Read the current-state section of the prompt. Then state role and mission and start working.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("More context: read any file yourself with an AIRUN block (dump files are listed at the end). Never ask the operator to paste.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("HOW YOU ARE USED (AIBridge v0.7; DSA_SESSION_PROMPT.md section 0 is the rule, and where older text in this paste disagrees, section 0 wins):")
[void]$sb.AppendLine("- You run commands yourself through # AIRUN blocks; they run by themselves and the result comes back as [AIRUN RESULT]. Never ask the operator to run, paste or read back.")
[void]$sb.AppendLine("- Up to 6 blocks per reply, run in order. Task mode (task=mts-boot, mts-gate, mts-ship) runs boot, the test gate and ship in one call.")
[void]$sb.AppendLine("- Reach: IdeaProjects, F:\MTS and Temp (F:\AIBridge read only). Refused: .secrets, .env, key files, HALT files. Irreversible forms (forced deletes, hard resets) wait for a click: use the safe form instead.")
[void]$sb.AppendLine("- You finish your own tasks: claim, test first, change (dsa.py put / edit), gate, dsa.py commit, task=mts-ship, release (prompt section 5a). Live-path code and the section 5d list stay with Claude.")
[void]$sb.AppendLine("- Never claim a command ran until its [AIRUN RESULT] exists. Builders never stop or restart processes, touch HALT files or open trades.")
[void]$sb.AppendLine("- A WORKER chat has no bridge: no shell, no disk, interprets pasted evidence only (prompt section 1).")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=" * 72)
[void]$sb.AppendLine("BOOT CONTENT (all files, read the whole block)")
[void]$sb.AppendLine("=" * 72)

$bootMode = if (Get-Process -Name java -ErrorAction SilentlyContinue) { "live" } else { "static" }
[void]$sb.AppendLine("MODE: $bootMode")

foreach ($f in ($m.boot_files + $m.boot_supplemental)) {
    $fMode = if ($f.mode) { $f.mode } else { "always" }
    if ($fMode -eq "live_only" -and $bootMode -eq "static") { continue }
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("### $($f.path) [$($f.role)] ###")
    $body = Get-ReadBody $f
    [void]$sb.AppendLine($body)
}

# SESSION_MANIFEST.json raw (boot rule 3.1)
[void]$sb.AppendLine("")
[void]$sb.AppendLine("### SESSION_MANIFEST.json [manifest_raw] ###")
[void]$sb.AppendLine('(not pasted; read it on disk if needed: ' + $manifestPath + ')')

# Reference index. Files on disk not pasted. Request by path + line range.
$refPaths = @(
    @{ path='MyTradingSys/research/AUDIT_2026-09-17_TRACKER.md'; role='audit_work' },
    @{ path='MyTradingSys/research/LOOP_LIFECYCLE_DESIGN_2026-09-19.md'; role='plan' },
    @{ path='MyTradingSys/research/EXTRACTION_TO_ALERT_AUDIT_2026-09-19.md'; role='audit' },
    @{ path='MyTradingSys/runtime/SESSION_RESUME.md'; role='historical' },
    @{ path='MyTradingSys/research/L_ITEMS_MASTER.md'; role='frozen' },
    @{ path='MyTradingSys/research/INDICATOR_IMPLEMENTATION_HANDOFF.md'; role='research' },
    @{ path='MyTradingSys/PROJECT_VISION.md'; role='direction' },
    @{ path='MyTradingSys/research/TOM_VERBATIM_INDEX.md'; role='citation_index' },
    @{ path='MyTradingSys/research/schema_v5.1.0_spec.md'; role='schema' },
    @{ path='MyTradingSys/research/open_loops_status.md'; role='stale_loops' },
    @{ path='MyTradingSys/research/compiled_output_audit_20260915.md'; role='audit' }
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
[void]$sb.AppendLine("  MyTradingSys/conditions/  - MTS rule files")
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
        $dirtyLines = @(& git -C $root status --short 2>$null)
        $dirtyLines | Select-Object -First 30 | ForEach-Object { [void]$sb.AppendLine("  $_") }
        if ($dirtyLines.Count -gt 30) { [void]$sb.AppendLine("  ... $($dirtyLines.Count - 30) more (run git status --short)") }
    }
} catch {
    [void]$sb.AppendLine("(git unavailable)")
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### news: NOT PASTED (operator 2026-10-10: the 72 h news was 61 KB, a third of the paste). Run it yourself at boot: python scripts/dev/sync.py news 72 (DSA_SESSION_PROMPT.md 0.8b, boot step 12). If it fails, say 'news unavailable' and read git log. ###")
Write-Host "news: pointer only (run sync.py news 72 at boot)" -ForegroundColor Green

[void]$sb.AppendLine("")
[void]$sb.AppendLine("### loop health ###")
$lockPath = Join-Path $root 'runtime_data\apparatus.lock'
if (Test-Path $lockPath) {
    $lockLine = (Get-Content $lockPath -Raw).Trim()
    [void]$sb.AppendLine("lock:      $lockLine")
} else {
    [void]$sb.AppendLine("lock:      none")
}
$newest = Get-ChildItem (Join-Path $root 'runtime_data\snapshots\BTCUSDT_*.json') -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$snapAgeMin = $null
if ($newest) {
    $snapAgeMin = [math]::Round(((Get-Date) - $newest.LastWriteTime).TotalMinutes, 1)
    [void]$sb.AppendLine("snapshot:  $($newest.Name)  age=$snapAgeMin min")
} else {
    [void]$sb.AppendLine("snapshot:  none")
}
$stateFile = Join-Path $root 'MyTradingSys\runtime\state_code.json'
$stAgeMin = $null
if (Test-Path $stateFile) {
    $stAgeMin = [math]::Round(((Get-Date) - (Get-Item $stateFile).LastWriteTime).TotalMinutes, 1)
    [void]$sb.AppendLine("state_code: age=$stAgeMin min")
}
$supLogFile = Join-Path $root 'runtime_data\supervisor_log.txt'
$supAgeSec = $null
if (Test-Path $supLogFile) {
    $supAgeSec = [int]((Get-Date) - (Get-Item $supLogFile).LastWriteTime).TotalSeconds
    [void]$sb.AppendLine("supervisor_heartbeat: age=$supAgeSec sec")
}
$javaProc = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'datafeed|statemachine|mts|BinanceDataFeed' }
$supProc = Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'loop-supervisor' }
[void]$sb.AppendLine("java:      $(if ($javaProc) { 'present' } else { 'absent' })")
[void]$sb.AppendLine("supervisor: $(if ($supProc) { 'present' } else { 'absent' })")
$healthReasons = @()
if (-not $javaProc) { $healthReasons += 'java_absent' }
if (-not $supProc)  { $healthReasons += 'supervisor_absent' }
if ($null -eq $snapAgeMin -or $snapAgeMin -gt 5) { $healthReasons += "snapshot_age=$(if ($null -eq $snapAgeMin) { 'missing' } else { $snapAgeMin })" }
if ($null -eq $stAgeMin -or $stAgeMin -gt 5)     { $healthReasons += "state_code_age=$(if ($null -eq $stAgeMin) { 'missing' } else { $stAgeMin })" }
if ($null -eq $supAgeSec -or $supAgeSec -gt 90) { $healthReasons += "supervisor_age=$(if ($null -eq $supAgeSec) { 'missing' } else { $supAgeSec })" }
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
[void]$sb.AppendLine("DUMP FILES (read the one you need with an AIRUN block; they are in Dumps\)")
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
[void]$sb.AppendLine("  - Up to 6 blocks per reply, run in order (prompt section 0.1). This paste is read whole, whatever its size.")
[void]$sb.AppendLine("  - Direct mode: you have a shell through AIBridge. Run commands yourself (DSA_SESSION_PROMPT.md section 0).")
[void]$sb.AppendLine("  - Work each task to its end (prompt section 5a); stop only for the section 5d list.")
[void]$sb.AppendLine("  - No blind java kill. No session_state.json thesis change without approval.")
[void]$sb.AppendLine("  - Plain language. No codes. No shorthand.")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("LAST CHECK (same as DSA_SESSION_PROMPT.md section 0, restated at the end on purpose):")
[void]$sb.AppendLine("  1. Claim only what you saw pasted or in an [AIRUN RESULT]. 2. No invented number, path, alias or restriction.")
[void]$sb.AppendLine("  3. Tom's transcripts are the only source for rules. 4. Clear task-aligned default: take it, flag after.")
[void]$sb.AppendLine("  5. Answer first, then act through blocks, never through requests to the operator. 6. Testnet only; nothing live touched.")
[void]$sb.AppendLine("  7. Handoff files in this paste can be old: check their date. The queue in prompt section 5 decides the task; write your handoff at close (prompt section 13).")

$block = $sb.ToString()
Write-Host "generated: $($block.Length) chars"

$sizeKb = [math]::Round($block.Length / 1024, 1)
Write-Host "paste size: $sizeKb KB"
if ($sizeKb -gt 400) {
    Write-Host "WARNING: paste over 400 KB (100-250 KB is normal; operator 2026-10-08)" -ForegroundColor Yellow
    $contrib = @()
    foreach ($f in ($m.boot_files + $m.boot_supplemental)) {
        $body = Get-ReadBody $f
        $contrib += [PSCustomObject]@{ path=$f.path; size=$body.Length }
    }
    $contrib | Sort-Object size -Descending | Select-Object -First 3 | ForEach-Object {
        Write-Host ("  {0}  {1} KB" -f $_.path, [math]::Round($_.size/1024,1))
    }
}

$pasteFile = $Out
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