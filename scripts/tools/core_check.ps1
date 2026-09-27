# core_check.ps1 - standing pre/post-change guardrail for core-readiness work.
# Task A2 of MyTradingSys/research/core_readiness_2026-09-27/CORE_READINESS_PLAN.md.
# Runs, in order, every read-only harness check and prints one STATUS line.
# Not wired into Build-Check.ps1 (4-5 min runtime). Run before and after every
# core change (Java Tom core, verdict.py/Compute-Verdict, math_object_builder.py)
# and at session end. Does not modify any live file - every harness script is
# pure-read. Written 2026-09-27; logic verified against the live repo via the
# device bridge (python3 directly), but this exact .ps1 file has not itself been
# executed under pwsh - no PowerShell available in that sandbox. Run once on the
# desktop to get a real PASS/FAIL before relying on it.

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$H = "MyTradingSys\research\core_readiness_2026-09-27\harness"
$golden = "2026-09-24T13:51:32Z"

$overallFail = $false
$results = [System.Collections.Generic.List[string]]::new()

function Run-Check {
    param([string]$Name, [string]$Cmd)
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    $out = Invoke-Expression $Cmd 2>&1 | Tee-Object -Variable capturedOut
    $capturedOut | ForEach-Object { Write-Host $_ }
    $last = ($capturedOut | Select-Object -Last 1)
    $pass = ($last -match "RESULT:\s*PASS") -or ($last -match "NO CHANGE") -or ($LASTEXITCODE -eq 0)
    if (-not $pass) { $script:overallFail = $true }
    $script:results.Add("$Name : $(if ($pass) {'PASS'} else {'FAIL'})")
}

Run-Check "core_invariants (since golden boundary)" "python $H\core_invariants.py --since $golden"
Run-Check "verdict_golden" "python $H\verdict_golden.py"
Run-Check "module_isolation group A" "python $H\module_isolation.py --group A"
Run-Check "module_isolation group B" "python $H\module_isolation.py --group B"
Run-Check "snapshot_contract" "python $H\snapshot_contract.py --since $golden"
Run-Check "proof_direction_cases" "python $H\proof_direction_cases.py"
Run-Check "backtest parity" "python MyTradingSys\backtest\parity.py"

Write-Host ""
Write-Host "--- core_check summary ---"
$results | ForEach-Object { Write-Host $_ }
Write-Host "STATUS:" ($(if ($overallFail) {"FAIL"} else {"PASS"}))
if ($overallFail) { exit 1 } else { exit 0 }
