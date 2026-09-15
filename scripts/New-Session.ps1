# New-Session.ps1
# Loads USER.md + SESSION_PROMPT.md into one clipboard payload.
# Usage: .\scripts\New-Session.ps1

$root = 'C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed'
$user = Get-Content (Join-Path $root 'USER.md') -Raw -Encoding UTF8
$spr  = Get-Content (Join-Path $root 'MyTradingSys\mts\runtime\SESSION_PROMPT.md') -Raw -Encoding UTF8

$payload = @"
You are the MTS agent. Root: $root
You have no filesystem access. The user runs PowerShell and pastes output. Issue commands only.

=== USER.md ===
$user

=== SESSION_PROMPT.md ===
$spr

First line of your reply: ROLE: agent
Then execute the BOOT section in one PowerShell block. Nothing else.
"@

Set-Clipboard -Value $payload
Write-Host ""
Write-Host "Full session payload on clipboard. Paste into a fresh chat." -ForegroundColor Cyan
Write-Host "Chars: $($payload.Length)"
Write-Host ""
