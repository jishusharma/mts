# Build-Check.ps1 - Preflight + routing manifest for DSA sessions.
# Writes Dumps/BUILD_REPORT.md - paste this first at any session start.
# Does not modify any live file.

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

# 1. Java compile
$t0 = Get-Date
& mvn -q -DskipTests compile 2>&1 | Out-Null
$dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
if ($LASTEXITCODE -eq 0) {
    $lines.Add("Java compile:  PASS ($dur s)")
} else {
    $lines.Add("Java compile:  FAIL ($dur s)")
    $overallFail = $true
}

# 2. Math tests
$t0 = Get-Date
$mtestOut = (& python -m pytest MyTradingSys/mts/tests --ignore=MyTradingSys/mts/tests/docs -q 2>&1 | Out-String)
$dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
$m = [regex]::Match($mtestOut, "(\d+) passed")
if ($LASTEXITCODE -eq 0 -and $m.Success) {
    $lines.Add("Math tests:    PASS $($m.Groups[1].Value)/$($m.Groups[1].Value) ($dur s)")
} else {
    $lines.Add("Math tests:    FAIL ($dur s)")
    $overallFail = $true
}

# 3. Doc tests
$docsDir = "MyTradingSys/mts/tests/docs"
if (Test-Path $docsDir) {
    $t0 = Get-Date
    $dtestOut = (& python -m pytest $docsDir -q 2>&1 | Out-String)
    $dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    $dm = [regex]::Match($dtestOut, "(\d+) passed")
    $df = [regex]::Match($dtestOut, "(\d+) failed")
    if ($LASTEXITCODE -eq 0 -and $dm.Success) {
        $lines.Add("Doc tests:     PASS $($dm.Groups[1].Value)/$($dm.Groups[1].Value) ($dur s)")
    } else {
        $failedN = if ($df.Success) { $df.Groups[1].Value } else { "?" }
        $lines.Add("Doc tests:     FAIL $failedN failed ($dur s)")
        $overallFail = $true
    }
} else {
    $lines.Add("Doc tests:     SKIP (no docs dir)")
}

$lines.Add("")

# In-flight .new files (parallel work visibility)
$inFlight = @(Get-ChildItem "MyTradingSys" -Recurse -File -Filter "*.new" -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch "\\archive\\" })
$lines.Add("In-flight .new files: " + $inFlight.Count)
foreach ($f in $inFlight) {
    $rel = $f.FullName.Substring((Resolve-Path "MyTradingSys").Path.Length + 1)
    $age = [int]((Get-Date) - $f.LastWriteTime).TotalMinutes
    $lines.Add("  - $rel (age ${age}m)")
}
$lines.Add("")

# Active sessions
$lines.Add("Active sessions:")
$locksDir = "MyTradingSys/mts/runtime/locks"
if (Test-Path $locksDir) {
    $locks = @(Get-ChildItem $locksDir -Filter "session_*.lock" -ErrorAction SilentlyContinue)
    if ($locks.Count -eq 0) {
        $lines.Add("  (none)")
    } else {
        foreach ($l in $locks) {
            try {
                $d = Get-Content $l.FullName -Raw | ConvertFrom-Json
                $age = [int]((Get-Date) - [datetime]$d.start_utc).TotalMinutes
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
$scan += Get-ChildItem "MyTradingSys\mts\runtime" -File -Filter "*.py" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\mts\runtime" -File -Filter "*.json" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\mts\research" -File -Filter "*.md" -ErrorAction SilentlyContinue
$scan += Get-ChildItem "MyTradingSys\mts\conditions" -File -Filter "*.md" -ErrorAction SilentlyContinue
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
$lines.Add("Non-ASCII files: " + $nonAsciiHits.Count)
foreach ($h in $nonAsciiHits) { $lines.Add("  - $h") }
$lines.Add("")
# Bug list validation
$bugsPath = "MyTradingSys\mts\research\BUGS.md"
$bugFail = @()
$bugRows = 0
if (Test-Path $bugsPath) {
  $validStatus = @("OPEN","IN-FIX","BLOCKED","CLOSED","WONTFIX")
  $validSeverity = @("HIGH","MED","LOW","COSMETIC")
  $seenIds = @{}
  $bugLines = [System.IO.File]::ReadAllLines((Resolve-Path $bugsPath), [System.Text.Encoding]::UTF8)
  foreach ($bl in $bugLines) {
    if ($bl -match '^\|\s*B\d+\s*\|') {
      $cells = $bl.Split('|') | ForEach-Object { $_.Trim() }
      if ($cells.Count -lt 9) { $bugFail += "malformed row: $bl"; continue }
      $bid = $cells[1]; $bopened = $cells[2]; $bstatus = $cells[3]; $bsev = $cells[4]; $breceipt = $cells[7]
      $bugRows++
      if ($seenIds.ContainsKey($bid)) { $bugFail += "duplicate ID: $bid" } else { $seenIds[$bid] = 1 }
      if ($validStatus -notcontains $bstatus) { $bugFail += "$bid bad status: $bstatus" }
      if ($validSeverity -notcontains $bsev) { $bugFail += "$bid bad severity: $bsev" }
      if ($bstatus -eq "CLOSED" -and ($breceipt -eq "-" -or $breceipt -eq "")) { $bugFail += "$bid CLOSED with no receipt" }
      if ($bstatus -eq "IN-FIX") {
        try {
          $od = [datetime]::ParseExact($bopened, "yyyy-MM-dd", $null)
          if (((Get-Date) - $od).TotalDays -gt 14) { $bugFail += "$bid IN-FIX older than 14 days" }
        } catch { $bugFail += "$bid bad Opened date: $bopened" }
      }
    }
  }
  if ($bugFail.Count -gt 0) {
    $lines.Add("Bugs: FAIL (" + $bugFail.Count + " issues)")
    foreach ($bf in $bugFail) { $lines.Add("  - $bf") }
    $overallFail = $true
  } else {
    $lines.Add("Bugs: OK (" + $bugRows + " rows)")
  }
} else {
  $lines.Add("Bugs: file missing ($bugsPath)")
}
$lines.Add("")
if ($bomHits.Count -gt 0 -or $nonAsciiHits.Count -gt 0) { $overallFail = $true }
if ($overallFail) { $lines.Add("STATUS: FAIL") } else { $lines.Add("STATUS: PASS") }
$lines.Add("")
$lines.Add("Pastes for this session:")
$lines.Add("  Always:   Dumps/BUILD_REPORT.md")
$lines.Add("  JSON:     Dumps/dump_core.md + dump_runtime.md")
$lines.Add("  Data:     Dumps/dump_data.md")
$lines.Add("  System:   Dumps/dump_system_support.md")
$lines.Add("  Extract:  Dumps/dump_extracts.md (paste sections only)")
$lines.Add("")

# Write
$outDir = "Dumps"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
$outFile = Join-Path $outDir "BUILD_REPORT.md"
Write-TextNoBom -Path $outFile -Lines $lines

$lines | ForEach-Object { Write-Host $_ }
Write-Host ""
Write-Host "Report: $((Resolve-Path $outFile).Path)"
