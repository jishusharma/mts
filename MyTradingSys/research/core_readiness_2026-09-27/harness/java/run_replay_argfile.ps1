# run_replay_argfile.ps1 - batched variant.
# The @files splat exceeds Windows command-line limit; the @argfile trick
# doesn't expand reliably on JDK 17 Windows. Instead: run java in N-file batches.
param([long]$SinceMs = 1790257892000, [int]$BatchSize = 100)
$ErrorActionPreference = "Stop"
$R = (Get-Location).Path
$H = Join-Path $R "MyTradingSys\research\core_readiness_2026-09-27\harness\java"
$T = Join-Path $env:TEMP ("scb_replay_" + [Guid]::NewGuid().ToString("N").Substring(0,8))
New-Item -ItemType Directory -Path "$T\src","$T\out" | Out-Null
foreach ($f in "SetupCandidatesBuilder","ExtraSetupBuilder","NakedPocTracker","FvgCalculator") {
  Copy-Item "$R\src\main\java\datafeed\$f.java" "$T\src\"
}
(Get-Content "$T\src\SetupCandidatesBuilder.java" -Raw).Replace("MAX_CANDIDATES = 3;","MAX_CANDIDATES = 999;") |
  Set-Content "$T\src\SetupCandidatesBuilder.java" -NoNewline
Copy-Item "$H\ReplayScbSteps1to8.java" "$T\src\"
$m2 = Join-Path $env:USERPROFILE ".m2\repository\com\fasterxml\jackson\core"
$cp = (Get-ChildItem $m2 -Recurse -Filter "jackson-*-2.16.0.jar" | ForEach-Object FullName) -join ";"
if (-not $cp) { throw "jackson 2.16.0 jars not found under $m2 - run Build-Check.ps1 once first" }
javac -nowarn -d "$T\out" -cp $cp (Get-ChildItem "$T\src\*.java" | ForEach-Object FullName)
$files = @(Get-ChildItem "$R\runtime_data\snapshots\BTCUSDT_*.json" |
  Where-Object { [long]($_.BaseName.Split("_")[-1]) -ge $SinceMs } | ForEach-Object FullName)
$total = $files.Count
Write-Host ("Snapshot count: {0}, batch size: {1}, batches: {2}" -f $total, $BatchSize, [Math]::Ceiling($total / $BatchSize))
$totalPass = 0
$failBatches = @()
$lastResultLine = ""
for ($i = 0; $i -lt $total; $i += $BatchSize) {
    $end = [Math]::Min($i + $BatchSize - 1, $total - 1)
    $batch = @($files[$i..$end])
    $out = & java -cp "$T\out;$cp" datafeed.ReplayScbSteps1to8 @batch 2>&1 | Out-String
    $rc = $LASTEXITCODE
    $rline = ($out -split "`n" | Where-Object { $_ -match "RESULT" } | Select-Object -Last 1)
    if ($rline) { $lastResultLine = $rline.Trim() }
    Write-Host ("Batch {0,3}: idx {1,5}..{2,5}  rc={3}  {4}" -f ($i / $BatchSize + 1), $i, $end, $rc, $lastResultLine)
    if ($rc -eq 0) { $totalPass += $batch.Count } else { $failBatches += ,@($i, $end, $out) }
}
Remove-Item $T -Recurse -Force
Write-Host ""
if ($failBatches.Count -eq 0) {
    Write-Host ("A3 OVERALL: PASS ({0}/{1} snapshots, {2} batches)" -f $totalPass, $total, [Math]::Ceiling($total / $BatchSize))
    exit 0
} else {
    Write-Host ("A3 OVERALL: FAIL - {0} batch(es) failed" -f $failBatches.Count)
    foreach ($fb in $failBatches) {
        Write-Host ("--- Batch idx {0}..{1} output ---" -f $fb[0], $fb[1])
        Write-Host $fb[2]
    }
    exit 1
}
