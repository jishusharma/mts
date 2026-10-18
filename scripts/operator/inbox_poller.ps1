# Operator inbox poller. Polls a directory listing only; runs headless Claude once per new request.
param([int]$IntervalSec = 20, [int]$TimeoutMin = 30, [switch]$Once, [int]$RetentionDays = 14,
      [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent | Split-Path -Parent),
      [string]$Root = '')
if (-not $Root) { $Root = Join-Path $RepoRoot 'Dumps\operator' }
$utf8 = New-Object Text.UTF8Encoding($false)
foreach ($d in 'inbox','outbox','done','archive') { New-Item -ItemType Directory -Force (Join-Path $Root $d) | Out-Null }
$logFile = Join-Path $Root 'poller.log'
function Log($m) { Add-Content -Path $logFile -Value "$((Get-Date).ToString('s')) $m" -Encoding utf8 }

$preamble = @"
You are the MTS operator assistant. Read CLAUDE.md and MyTradingSys/research/STATUS.md only as needed. Do the request below. Reply in <= 30 lines. If the request needs the long-running supervisor session, say so instead of attempting it.

REQUEST:
"@

function Invoke-Request($file) {
    $base = [IO.Path]::GetFileNameWithoutExtension($file.Name)
    $working = Join-Path $Root "inbox\$base.working"
    $reply = Join-Path $Root "outbox\$base.reply.md"
    Move-Item $file.FullName $working -Force
    $raw = [IO.File]::ReadAllText($working)
    $model = 'haiku'   # CLAUDE.md Cost and routing: question/status -> Haiku; a request escalates with `model: sonnet|opus`
    $text = $raw
    $parts = $raw -split "(?m)^---\r?\n", 2
    if ($parts.Count -eq 2) {
        $text = $parts[1]
        if ($parts[0] -match '(?im)^model:\s*(\w+)') { $model = $Matches[1].ToLower() }
    }
    if ($model -notin 'sonnet','opus','haiku') { $model = 'haiku' }
    Log "start $base model=$model"
    $claude = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $claude) {
        [IO.File]::WriteAllText($reply, "CLI missing: install with irm https://claude.ai/install.ps1 | iex, then run claude once to log in`n", $utf8)
        Log "CLI missing for $base"
    } else {
        $tmp = Join-Path $Root "$base.prompt.tmp"; $out = Join-Path $Root "$base.out.tmp"; $err = Join-Path $Root "$base.err.tmp"
        [IO.File]::WriteAllText($tmp, "$preamble`n$text", $utf8)
        try {
            $p = Start-Process -FilePath $claude.Source -WorkingDirectory $RepoRoot -NoNewWindow -PassThru `
                -ArgumentList @('-p','--model',$model,'--permission-mode','acceptEdits') `
                -RedirectStandardInput $tmp -RedirectStandardOutput $out -RedirectStandardError $err
            if (-not $p.WaitForExit($TimeoutMin * 60000)) {
                & taskkill /PID $p.Id /T /F 2>&1 | Out-Null
                [IO.File]::WriteAllText($reply, "TIMEOUT after $TimeoutMin min; request aborted.`n", $utf8)
                Log "timeout $base"
            } else {
                $p.WaitForExit()
                $o = if (Test-Path $out) { [IO.File]::ReadAllText($out) } else { '' }
                if ($p.ExitCode -ne 0) { $o += "`n[exit $($p.ExitCode)] " + $(if (Test-Path $err) { [IO.File]::ReadAllText($err) }) }
                [IO.File]::WriteAllText($reply, $o, $utf8)
                Log "done $base exit=$($p.ExitCode)"
            }
        } catch {
            [IO.File]::WriteAllText($reply, "poller error: $_`n", $utf8); Log "error $base $_"
        } finally { Remove-Item $tmp,$out,$err -ErrorAction SilentlyContinue }
    }
    Move-Item $working (Join-Path $Root "done\$base.md") -Force
}

function Invoke-Retention {
    $cut = (Get-Date).AddDays(-$RetentionDays)
    foreach ($d in 'done','outbox') {
        Get-ChildItem (Join-Path $Root $d) -File -ErrorAction SilentlyContinue | Where-Object LastWriteTime -lt $cut |
            ForEach-Object { Move-Item $_.FullName (Join-Path $Root "archive\$($_.Name)") -Force }
    }
}

Log "poller started (interval ${IntervalSec}s, root $Root)"
$lastRet = [datetime]::MinValue
do {
    try {
        # recover requests stranded by a crash
        Get-ChildItem (Join-Path $Root 'inbox') -Filter *.working -File -ErrorAction SilentlyContinue |
            ForEach-Object { Move-Item $_.FullName ($_.FullName -replace '\.working$','.md') -Force }
        $new = @(Get-ChildItem (Join-Path $Root 'inbox') -Filter *.md -File -ErrorAction SilentlyContinue | Sort-Object Name)
        foreach ($f in $new) { Invoke-Request $f }
        if (((Get-Date) - $lastRet).TotalHours -ge 1) { Invoke-Retention; $lastRet = Get-Date }
    } catch { Log "loop error: $_" }
    if (-not $Once) { Start-Sleep -Seconds $IntervalSec }
} while (-not $Once)
