# Post a request to the operator inbox. Usage: .\ask.ps1 "text" [-Model sonnet|opus|haiku]
param([Parameter(Mandatory=$true, Position=0)][string]$Text,
      [ValidateSet('sonnet','opus','haiku')][string]$Model = 'haiku',
      [string]$Root = (Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) 'Dumps\operator'))
$inbox = Join-Path $Root 'inbox'
New-Item -ItemType Directory -Force $inbox | Out-Null
$name = 'req_' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.md'
$path = Join-Path $inbox $name
$body = "model: $Model`ncreated: $((Get-Date).ToString('s'))`n---`n$Text`n"
[IO.File]::WriteAllText($path, $body, (New-Object Text.UTF8Encoding($false)))
Write-Output "queued $name"
