# Print newest replies. Usage: .\replies.ps1 [-Count 1] [-List]
param([int]$Count = 1, [switch]$List,
      [string]$Root = (Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) 'Dumps\operator'))
$files = @(Get-ChildItem (Join-Path $Root 'outbox') -Filter *.reply.md -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
if (-not $files) { Write-Output 'no replies yet'; return }
if ($List) { $files | Select-Object -First 20 | ForEach-Object { "$($_.LastWriteTime.ToString('s'))  $($_.Name)" }; return }
$files | Select-Object -First $Count | ForEach-Object { "=== $($_.Name) ==="; Get-Content $_.FullName -Raw }
