# run_replay.ps1 - L1 Tom-core replay (steps 1-8). Desktop, repo root. Read-only on src/.
# Builds a throwaway test copy of SetupCandidatesBuilder (MAX_CANDIDATES 3 -> 999) in $env:TEMP.
# Usage: .\MyTradingSys\research\core_readiness_2026-09-27\harness\java\run_replay.ps1 [-SinceMs 1790257892000]
# Default SinceMs = 2026-09-24T13:51:32Z, last SetupCandidatesBuilder change (golden boundary).
param([long]$SinceMs = 1790257892000)
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
$files = Get-ChildItem "$R\runtime_data\snapshots\BTCUSDT_*.json" | Where-Object { [long]($_.BaseName.Split("_")[-1]) -ge $SinceMs } | ForEach-Object FullName
java -cp "$T\out;$cp" datafeed.ReplayScbSteps1to8 @files
Remove-Item $T -Recurse -Force
