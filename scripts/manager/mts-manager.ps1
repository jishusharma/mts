# mts-manager.ps1 - front door for the Claude manager (CLAUDE_MANAGER_SPEC.md). Thin wrapper; logic is in claude_manager.py.
#   .\scripts\manager\mts-manager.ps1 go "fix the alert rate check"
#   .\scripts\manager\mts-manager.ps1 status | resume | stop <slug> | usage <percent>
# Verbs are NOT merged into mts.ps1: mts status/resume/stop already mean market loop / HALT brakes there.
param([Parameter(Position = 0)][string]$Verb = "status", [Parameter(Position = 1)][string]$Arg = "")
$ErrorActionPreference = "Stop"
$env:PYTHONUNBUFFERED = "1"
$py = Join-Path $PSScriptRoot "claude_manager.py"
if ($Verb -in @("go", "stop", "usage") -and -not $Arg) { Write-Host "usage: mts-manager $Verb <argument>" -ForegroundColor Red; exit 2 }
if ($Verb -notin @("go", "status", "resume", "stop", "usage")) { Write-Host "verbs: go status resume stop usage" -ForegroundColor Red; exit 2 }
$a = @($py, $Verb); if ($Arg) { $a += $Arg }
& python @a
exit $LASTEXITCODE
