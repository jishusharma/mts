# verify_rule_citations.ps1
# Checks that every rule tag in conditions/ resolves to a quote in TOM_VERBATIM_INDEX.md.
# And that every TOM-NNN in the index is referenced by at least one rule.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$condDir = Join-Path $root 'MyTradingSys\conditions'
$engineFile = Join-Path $root 'MyTradingSys\runtime\compiled_engine.md'
$indexPath = Join-Path $root 'MyTradingSys\research\TOM_VERBATIM_INDEX.md'

if (-not (Test-Path $indexPath)) { Write-Host 'FAIL: index missing'; exit 1 }

$indexText = Get-Content $indexPath -Raw
$definedIds = [regex]::Matches($indexText, 'TOM-\d{3}') | ForEach-Object { $_.Value } | Sort-Object -Unique

$untagged = @()
$unknownTags = @()
$usedIds = @{}

# Scanned files: the six condition files (every derived rule there carries
# [TOM-NNN] or [SCREENER] by TOM_VERBATIM_INDEX.md's own rule) plus
# runtime/compiled_engine.md (T049 phase 5, 2026-09-26: rule tagging and
# source tracing extended to the compiled file, since a citation living
# only there previously read as unreferenced and failed this check).
$scanFiles = @(Get-ChildItem -Path (Join-Path $condDir '*.md'))
if (Test-Path $engineFile) { $scanFiles += Get-Item $engineFile }

foreach ($file in $scanFiles) {
  $lines = Get-Content $file.FullName
  $n = 0
  foreach ($line in $lines) {
    $n++
    if ($line -match '^##\s' -or $line -match '^#\s' -or $line.Trim() -eq '') { continue }
    if ($line -match '\[TOM-\d{3}\]' -or $line -match '\[SCREENER\]') {
      [regex]::Matches($line, 'TOM-\d{3}') | ForEach-Object {
        $id = $_.Value
        $usedIds[$id] = $true
        if ($definedIds -notcontains $id) { $unknownTags += "$($file.Name):$n  unknown $id" }
      }
    }
  }
}

$unusedIds = $definedIds | Where-Object { -not $usedIds.ContainsKey($_) }

Write-Host "Index ids defined: $($definedIds.Count)"
Write-Host "Index ids referenced: $($usedIds.Count)"
Write-Host "Unknown tags in conditions: $($unknownTags.Count)"
$unknownTags | ForEach-Object { Write-Host "  $_" }
Write-Host "Index ids not referenced: $($unusedIds.Count)"
$unusedIds | ForEach-Object { Write-Host "  $_" }

if ($unknownTags.Count -gt 0) { Write-Host 'STATUS: FAIL (unknown tags)'; exit 1 }
if ($definedIds.Count -gt 0 -and $usedIds.Count -eq 0) { Write-Host 'STATUS: FAIL (no ids referenced)'; exit 1 }
if ($unusedIds.Count -gt 0) { Write-Host "STATUS: FAIL ($($unusedIds.Count) ids unreferenced)"; exit 1 }
Write-Host 'STATUS: PASS'
