# Build-Check.ps1 - Preflight + routing manifest for DSA sessions.
# Writes MyTradingSys/runtime/BUILD_REPORT.md - paste this first at any session start.
# Does not modify any live file.
# Tiers (B091):
#   (default)   full: compile + Java tests (mvn -q test) + math tests + doc tests + registry checks; writes BUILD_REPORT.md.
#   -Quick      fast pre-commit tier: Java compile only; math tests and Java tests (mvn -q test) skipped
#               (the release gate runs them); STATUS says QUICK.
#   -ReadOnly   print the report only; BUILD_REPORT.md is not rewritten, so the tree stays clean.
# Build-Check never writes session_log.json; -ReadOnly removes its only tree write.

param([switch]$Quick, [switch]$ReadOnly)

$ErrorActionPreference = "Continue"

function Write-TextNoBom {
    param([string]$Path, $Lines)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines((Join-Path (Get-Location) $Path), $Lines, $utf8NoBom)
}
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$start = [DateTime]::UtcNow
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("BUILD_REPORT - $($start.ToString('yyyy-MM-dd HH:mm:ss')) UTC")
$lines.Add("host: $env:COMPUTERNAME")
$lines.Add("")

$overallFail = $false
$failAxes = [System.Collections.Generic.List[string]]::new()
function Add-FailAxis { param([string]$Name) if (-not $failAxes.Contains($Name)) { $failAxes.Add($Name) } }

# Why-it-failed helpers: first $Max lines matching $Pattern (else first non-empty lines), indented 4 spaces.
function Get-FailSnippet {
    param($Text, [string]$Pattern, [int]$Max = 5)
    $all = @($Text | ForEach-Object { "$_" -split "`r?`n" } | ForEach-Object { $_.TrimEnd() } | Where-Object { $_.Trim() -ne "" })
    $hit = @($all | Where-Object { $_ -match $Pattern })
    if ($hit.Count -eq 0) { $hit = $all }
    $out = @()
    foreach ($h in ($hit | Select-Object -First $Max)) {
        $t = $h.Trim(); if ($t.Length -gt 300) { $t = $t.Substring(0, 300) + "..." }
        $out += ("    " + $t)
    }
    return $out
}
function Get-ToolchainLine {
    $jv = "not found"
    try { $jo = @(& java -version 2>&1 | ForEach-Object { "$_" }); if ($jo.Count -gt 0) { $jv = $jo[0].Trim() } } catch { }
    $mv = "not found"
    $mc = Get-Command mvn -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($mc) { $mv = $mc.Source; if (-not $mv) { $mv = $mc.Definition } }
    return "  java: $jv  mvn: $mv"
}

# 1. Java compile
$t0 = Get-Date
$compOut = @(& mvn -q -DskipTests compile 2>&1 | ForEach-Object { "$_" })
$compRc = $LASTEXITCODE
$dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
if ($compRc -eq 0) {
    $lines.Add("Java compile:  PASS ($dur s)")
} else {
    $lines.Add("Java compile:  FAIL ($dur s)")
    foreach ($cl in (Get-FailSnippet $compOut '\[ERROR\]' 5)) { $lines.Add($cl) }
    $lines.Add((Get-ToolchainLine))
    $overallFail = $true; Add-FailAxis "Java compile"
}

# 1b. Java tests (T037): full tier runs mvn -q test; -Quick stays compile-only
if ($Quick) {
    $lines.Add("Java tests:    SKIP (quick tier; compile only; full pass is the release gate)")
} else {
    $t0 = Get-Date
    $jtestOut = (& mvn -q test 2>&1 | Out-String)
    $jtestRc = $LASTEXITCODE
    $dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    $jrun = 0; $jskip = 0
    if (Test-Path "target/surefire-reports") {
        foreach ($rf in (Get-ChildItem "target/surefire-reports" -Filter "*.txt" | Where-Object { $_.LastWriteTime -ge $t0 })) {
            $jm = [regex]::Match((Get-Content $rf.FullName -Raw), "Tests run: (\d+), Failures: \d+, Errors: \d+, Skipped: (\d+)")
            if ($jm.Success) { $jrun += [int]$jm.Groups[1].Value; $jskip += [int]$jm.Groups[2].Value }
        }
    }
    if ($jtestRc -eq 0 -and $jrun -gt 0) {
        $lines.Add("Java tests:    PASS $($jrun - $jskip)/$jrun run, $jskip skipped ($dur s)")
    } else {
        $lines.Add("Java tests:    FAIL ($dur s)")
        foreach ($jl in (Get-FailSnippet $jtestOut '\[ERROR\]|FAILED|Tests run:.*(Failures|Errors): [1-9]' 5)) { $lines.Add($jl) }
        $lines.Add((Get-ToolchainLine))
        $overallFail = $true; Add-FailAxis "Java tests"
    }
}

# 2. Math tests
$t0 = Get-Date
if ($Quick) {
    $lines.Add("Math tests:    SKIP (quick tier; full pass is the release gate)")
} else {
$mtestOut = (& python -m pytest MyTradingSys/tests --ignore=MyTradingSys/tests/docs -q --basetemp=$env:TEMP/mts_pytest_math 2>&1 | Out-String)
$dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
$m = [regex]::Match($mtestOut, "(\d+) passed")
if ($LASTEXITCODE -eq 0 -and $m.Success) {
    $lines.Add("Math tests:    PASS $($m.Groups[1].Value)/$($m.Groups[1].Value) ($dur s)")
} else {
    $lines.Add("Math tests:    FAIL ($dur s)")
    $overallFail = $true; Add-FailAxis "Math tests"
}
}

# 3. Doc tests
$docsDir = "MyTradingSys/tests/docs"
if (Test-Path $docsDir) {
    $t0 = Get-Date
    $dtestOut = (& python -m pytest $docsDir -q --basetemp=$env:TEMP/mts_pytest_docs 2>&1 | Out-String)
    $dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    $dm = [regex]::Match($dtestOut, "(\d+) passed")
    $df = [regex]::Match($dtestOut, "(\d+) failed")
    if ($LASTEXITCODE -eq 0 -and $dm.Success) {
        $lines.Add("Doc tests:     PASS $($dm.Groups[1].Value)/$($dm.Groups[1].Value) ($dur s)")
    } else {
        $failedN = if ($df.Success) { $df.Groups[1].Value } else { "?" }
        $lines.Add("Doc tests:     FAIL $failedN failed ($dur s)")
        $overallFail = $true; Add-FailAxis "Doc tests"
    }
} else {
    $lines.Add("Doc tests:     SKIP (no docs dir)")
}

$lines.Add("")

# In-flight .new files (parallel work visibility)
$allNew = @(Get-ChildItem "MyTradingSys" -Recurse -File -Filter "*.new" -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch "\\archive\\" })
$staleCut = (Get-Date).AddHours(-48)
$inFlight = @($allNew | Where-Object { $_.LastWriteTime -ge $staleCut })
$staleNew = @($allNew | Where-Object { $_.LastWriteTime -lt $staleCut })
$lines.Add("In-flight .new files: " + $inFlight.Count)
foreach ($f in $inFlight) {
    $rel = $f.FullName.Substring((Resolve-Path "MyTradingSys").Path.Length + 1)
    $age = [int]((Get-Date) - $f.LastWriteTime).TotalMinutes
    $lines.Add("  - $rel (age ${age}m)")
}
if ($staleNew.Count -gt 0) {
    $lines.Add("")
    $lines.Add("Stale .new files (older than 48 h; archive with python scripts/dev/declutter_backups.py --apply):")
    foreach ($f in $staleNew) {
        $rel = $f.FullName.Substring((Resolve-Path "MyTradingSys").Path.Length + 1)
        $ageH = [int]((Get-Date) - $f.LastWriteTime).TotalHours
        $lines.Add("  - $rel (age ${ageH}h)")
    }
}
$lines.Add("")

# Active sessions
$lines.Add("Active sessions:")
$locksDir = "MyTradingSys/runtime/locks"
if (Test-Path $locksDir) {
    $locks = @(Get-ChildItem $locksDir -Filter "session_*.lock" -ErrorAction SilentlyContinue)
    if ($locks.Count -eq 0) {
        $lines.Add("  (none)")
    } else {
        foreach ($l in $locks) {
            try {
                $d = Get-Content $l.FullName -Raw | ConvertFrom-Json
                $age = [int]([DateTime]::UtcNow - ([datetime]$d.start_utc).ToUniversalTime()).TotalMinutes
                $lines.Add("  - $($d.id) / $($d.host) / started $($d.start_utc) (age ${age}m) / focus: $($d.focus)")
            } catch {
                $lines.Add("  - $($l.Name) (unreadable)")
            }
        }
        if ($locks.Count -gt 1) { $lines.Add("  (multiple active - check file ownership)") }
    }
} else {
    $lines.Add("  (locks dir not present)")
}

$lines.Add("")
# BOM + non-ASCII scan: files that will bite Python json.load or carry corrupted text
$bomHits = @()
$nonAsciiHits = @()
$scan = @()
$scan += Get-ChildItem "MyTradingSys\runtime" -File -Filter "*.py" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\runtime" -File -Filter "*.json" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\research" -File -Filter "*.md" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\runtime" -File -Filter "*.md" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\runtime" -File -Filter "*.md" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\conditions" -File -Filter "*.md" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\system" -File -Filter "*.md" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "scripts" -Recurse -File -Filter "*.ps1" -ErrorAction SilentlyContinue
foreach ($f in $scan) { if (-not $f.FullName) { continue }
  $b = [System.IO.File]::ReadAllBytes($f.FullName)
  $rel = $f.FullName.Substring((Get-Location).Path.Length + 1)
  $ext = [System.IO.Path]::GetExtension($f.FullName).ToLower()
  if (($ext -eq ".py" -or $ext -eq ".json" -or $ext -eq ".ps1") -and $b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) {
    $bomHits += $rel
  }
  $txt = [System.Text.Encoding]::UTF8.GetString($b)
  $na = 0
  foreach ($ch in $txt.ToCharArray()) {
    $ci = [int]$ch
    if ($ci -ge 0x0400 -and $ci -le 0x04FF) { $na++ }
  }
  if ($na -gt 0) { $nonAsciiHits += ("{0} ({1})" -f $rel, $na) }
}
$lines.Add("BOM files: " + $bomHits.Count)
foreach ($h in $bomHits) { $lines.Add("  - $h") }
$lines.Add("Cyrillic codepoints (0x0400-0x04FF): " + $nonAsciiHits.Count)
foreach ($h in $nonAsciiHits) { $lines.Add("  - $h") }
$lines.Add("")
# Bug list validation
$bugsPath = "MyTradingSys\research\BUGS.md"
$bugFail = @()
$bugRows = 0
if (Test-Path $bugsPath) {
  $validStatus = @("OPEN","IN-FIX","BLOCKED","CLOSED","WONTFIX")
  $validSeverity = @("HIGH","MED","LOW","COSMETIC")
  $seenIds = @{}
  $openIds = @{}
  $bugLines = [System.IO.File]::ReadAllLines((Resolve-Path $bugsPath), [System.Text.Encoding]::UTF8)
  foreach ($bl in $bugLines) {
    if ($bl -match '^\|\s*[BT]\d+\s*\|') {
      $cells = $bl.Split('|') | ForEach-Object { $_.Trim() }
      if ($cells.Count -lt 9) { $bugFail += "malformed row: $bl"; continue }
      $bid = $cells[1]; $bopened = $cells[2]; $bstatus = $cells[3]; $bsev = $cells[4]; $breceipt = $cells[7]
      $bugRows++
      if ($seenIds.ContainsKey($bid)) { $bugFail += "duplicate ID: $bid" } else { $seenIds[$bid] = 1 }
      if ($validStatus -notcontains $bstatus) { $bugFail += "$bid bad status: $bstatus" }
      if ($bstatus -eq "OPEN" -or $bstatus -eq "IN-FIX" -or $bstatus -eq "BLOCKED") { $openIds[$bid] = 1 }
      if ($validSeverity -notcontains $bsev) { $bugFail += "$bid bad severity: $bsev" }
      if ($bstatus -eq "CLOSED" -and ($breceipt -eq "-" -or $breceipt -eq "")) { $bugFail += "$bid CLOSED with no receipt" }
      if ($bstatus -eq "IN-FIX") {
        try {
          $od = [datetime]::ParseExact($bopened, "yyyy-MM-dd", $null)
          if (((Get-Date) - $od).TotalDays -gt 14) { $bugFail += "$bid IN-FIX older than 14 days" }
        } catch { $bugFail += "$bid bad Opened date: $bopened" }
      }
      if ($bstatus -eq "OPEN" -or $bstatus -eq "IN-FIX" -or $bstatus -eq "BLOCKED") {
        $itemsDir = "MyTradingSys\items"
        $hasItem = (Test-Path $itemsDir) -and @(Get-ChildItem $itemsDir -Filter "$bid`_*.md" -ErrorAction SilentlyContinue).Count -gt 0
        if (-not $hasItem) { $bugFail += "$bid $bstatus with no items/ file" }
      }
    }
  }
  if ($bugFail.Count -gt 0) {
    $lines.Add("Bugs: FAIL (" + $bugFail.Count + " issues)")
    foreach ($bf in $bugFail) { $lines.Add("  - $bf") }
    $overallFail = $true; Add-FailAxis "Bugs"
  } else {
    $lines.Add("Bugs: OK (" + $bugRows + " rows)")
  }
  # items/INDEX.md mechanical check (Claude ask 2026-09-24)
  $idxPath = "MyTradingSys\items\INDEX.md"
  if (Test-Path $idxPath) {
    $idxTxt = [System.IO.File]::ReadAllText((Resolve-Path $idxPath))
    $idxMiss = @()
    foreach ($k in $openIds.Keys) {
      $re = "(?m)^" + [regex]::Escape($k) + "\s*\|"
      if (([regex]::Matches($idxTxt,$re)).Count -eq 0) { $idxMiss += $k }
    }
    if ($idxMiss.Count -gt 0) {
      $lines.Add("Index: FAIL (" + $idxMiss.Count + " IDs not in INDEX.md)")
      foreach ($k in $idxMiss) { $lines.Add("  - $k missing from items/INDEX.md") }
      $overallFail = $true; Add-FailAxis "Index"
    } else {
      $lines.Add("Index: OK (" + $openIds.Count + " open IDs in items/INDEX.md)")
    }
  } else {
    $lines.Add("Index: file missing ($idxPath)")
    $overallFail = $true; Add-FailAxis "Index"
  }
} else {
  $lines.Add("Bugs: file missing ($bugsPath)")
}
$lines.Add("")

# items/*.md <-> INDEX.md two-way file check (T049 phase 4, 2026-09-26).
# Independent of BUGS.md: the check above only catches an id already listed
# there. This catches a missing or stale INDEX.md row directly, for any
# item file, and the reverse - an INDEX.md row pointing at a file that is
# not there.
$idxPath2 = "MyTradingSys\items\INDEX.md"
$itemsDir2 = "MyTradingSys\items"
if ((Test-Path $itemsDir2) -and (Test-Path $idxPath2)) {
    $idxText2 = [System.IO.File]::ReadAllText((Resolve-Path $idxPath2))
    $idxRows2 = [regex]::Matches($idxText2, '(?m)^([BT]\d+)\s*\|\s*\S+\s*\|\s*([^\|]+?)\s*\|')
    $idxIds2 = @{}
    foreach ($m in $idxRows2) { $idxIds2[$m.Groups[1].Value] = $m.Groups[2].Value.Trim() }

    $itemFiles2 = @(Get-ChildItem $itemsDir2 -Filter "*.md" -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "INDEX.md" })
    $fileMiss2 = @()
    foreach ($f in $itemFiles2) {
        if ($f.Name -match '^([BT]\d+)_') {
            $id2 = $matches[1]
            if (-not $idxIds2.ContainsKey($id2)) { $fileMiss2 += "$id2 ($($f.Name)) has no row in items/INDEX.md" }
        }
    }
    $rowMiss2 = @()
    foreach ($id2 in $idxIds2.Keys) {
        $rowFile2 = $idxIds2[$id2]
        $rowPath2 = Join-Path $itemsDir2 $rowFile2
        if (-not (Test-Path $rowPath2)) { $rowMiss2 += "$id2 row in INDEX.md points at missing file: $rowFile2" }
    }

    $idxFail2 = @($fileMiss2 + $rowMiss2)
    if ($idxFail2.Count -gt 0) {
        $lines.Add("Index (files cross-check): FAIL (" + $idxFail2.Count + " issues)")
        foreach ($x2 in $idxFail2) { $lines.Add("  - $x2") }
        $overallFail = $true; Add-FailAxis "Index (files cross-check)"
    } else {
        $lines.Add("Index (files cross-check): OK (" + $itemFiles2.Count + " item files, " + $idxIds2.Count + " INDEX rows)")
    }
} else {
    $lines.Add("Index (files cross-check): SKIP (items dir or INDEX.md missing)")
}
$lines.Add("")
# Dispatch checks
$dispatchFail = @()
$dispatchDir = "Dumps\workers"
$dispatchFiles = @()
if (Test-Path $dispatchDir) {
  $dispatchFiles = @(Get-ChildItem $dispatchDir -Recurse -File -Filter "DISPATCH.md" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\_archive\\" })
}
foreach ($df in $dispatchFiles) {
  $rel = $df.FullName.Substring((Get-Location).Path.Length + 1)
  $body = [System.IO.File]::ReadAllText($df.FullName, [System.Text.Encoding]::UTF8)

  # Check 1: OUTPUT path line
  if ($body -notmatch "Write reply to Dumps/workers/") {
    $dispatchFail += "$rel missing 'Write reply to Dumps/workers/' line"
  }

  # Check 2: referenced repo paths resolve
  $pathMatches = [regex]::Matches($body, '(?m)^\s+((?:MyTradingSys|scripts|src|data)[\\/][^\s`"]+\.(?:md|py|ps1|java|json))')
  $seen = @{}
  foreach ($pm in $pathMatches) {
    $raw = $pm.Groups[1].Value -replace '/', '\'
    if ($seen.ContainsKey($raw)) { continue }
    $seen[$raw] = 1
    $full = Join-Path (Get-Location) $raw
    if (-not (Test-Path $full)) {
      $dispatchFail += "$rel references missing path: $raw"
    }
  }
}
if ($dispatchFail.Count -gt 0) {
  $lines.Add("Dispatches: FAIL (" + $dispatchFail.Count + " issues)")
  foreach ($dd in $dispatchFail) { $lines.Add("  - $dd") }
  $overallFail = $true; Add-FailAxis "Dispatches"
} else {
  $lines.Add("Dispatches: OK (" + $dispatchFiles.Count + " files)")
}
$lines.Add("")
if ($bomHits.Count -gt 0) { $overallFail = $true; Add-FailAxis "BOM files" }
if ($nonAsciiHits.Count -gt 0) { $overallFail = $true; Add-FailAxis "Cyrillic codepoints" }
# The one STATUS line sits right after the host line (lines[0] title, [1] host, [2] blank) and names the failing axes.
$tier = if ($Quick) { " (QUICK: math tests and Java tests not run)" } else { "" }
if ($overallFail) {
    $axes = if ($failAxes.Count -gt 0) { " (" + ($failAxes -join ", ") + ")" } else { "" }
    $lines.Insert(2, "STATUS: FAIL$axes$tier")
} else {
    $lines.Insert(2, "STATUS: PASS$tier")
}
$lines.Add("Pastes for this session:")
$lines.Add("  Always:   MyTradingSys/runtime/BUILD_REPORT.md")
$lines.Add("  JSON:     Dumps/dump_core.md + dump_runtime.md")
$lines.Add("  Data:     Dumps/dump_data.md")
$lines.Add("  System:   Dumps/dump_system_support.md")
$lines.Add("  Extract:  Dumps/dump_extracts.md (paste sections only)")
$lines.Add("")

# Write
$lines | ForEach-Object { Write-Host $_ }
Write-Host ""
if ($ReadOnly) {
    Write-Host "Report: not written (-ReadOnly)"
} else {
    $outDir = "MyTradingSys/runtime"
    if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
    $outFile = Join-Path $outDir "BUILD_REPORT.md"
    Write-TextNoBom -Path $outFile -Lines $lines
    Write-Host "Report: $((Resolve-Path $outFile).Path)"
}
if ($overallFail) { exit 1 }
