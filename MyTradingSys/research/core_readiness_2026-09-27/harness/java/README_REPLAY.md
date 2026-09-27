# Tom core replay (Java, steps 1-8) - desktop runbook
# Date: 2026-09-27
# Purpose: replay SetupCandidatesBuilder steps 1-8 against archived snapshots
# Status: FRESH (verified 2026-09-27 in a cloud sandbox: 49 snapshots, 118/118 candidates, 1652/1652 fields; two mutations detected)

Never compiles into src/ or target/. Builds a throwaway copy in %TEMP%.
MAX_CANDIDATES is raised in the COPY only, because rank truncation depends on
proof scores and proofs cannot be replayed without 1m klines (task A4).

PowerShell, repo root (Maven must have run once so jars exist in %USERPROFILE%\.m2):

    $T = Join-Path $env:TEMP "scb_replay"; Remove-Item $T -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory "$T\src","$T\out" | Out-Null
    Copy-Item src\main\java\datafeed\SetupCandidatesBuilder.java,src\main\java\datafeed\ExtraSetupBuilder.java,src\main\java\datafeed\NakedPocTracker.java,src\main\java\datafeed\FvgCalculator.java "$T\src"
    Copy-Item MyTradingSys\research\core_readiness_2026-09-27\harness\java\ReplayScbSteps1to8.java "$T\src"
    (Get-Content "$T\src\SetupCandidatesBuilder.java") -replace 'MAX_CANDIDATES = 3;','MAX_CANDIDATES = 999;' | Set-Content "$T\src\SetupCandidatesBuilder.java"
    $M = "$env:USERPROFILE\.m2\repository\com\fasterxml\jackson\core"
    $CP = "$M\jackson-databind\2.16.0\jackson-databind-2.16.0.jar;$M\jackson-core\2.16.0\jackson-core-2.16.0.jar;$M\jackson-annotations\2.16.0\jackson-annotations-2.16.0.jar"
    javac -nowarn -d "$T\out" -cp $CP "$T\src\*.java"
    $files = Get-ChildItem runtime_data\snapshots\BTCUSDT_*.json | Where-Object { $_.LastWriteTimeUtc -ge [datetime]"2026-09-24T13:51:32Z" } | ForEach-Object FullName
    java -cp "$T\out;$CP" datafeed.ReplayScbSteps1to8 @files

Expected: last line RESULT: PASS, missing=0, bad=0.
Run from repo root (NakedPocTracker reads runtime_data\naked_pocs relative to the working directory).
If the file list is too long for one command line, run it in chunks of 200.
Mutation check (proves the harness can fail): in the COPY change
"c.netRR = c.grossRR * 0.75;" to "* 0.70;" -> expect RESULT: FAIL with math.net_rr diffs.
