# FILE: nuc-worker.ps1
# PURPOSE: NUC worker, version 2. Takes self-contained task packages from the
#          queue share, runs each through the local model over the Ollama
#          HTTP interface with an explicit context window, and returns a reply.
#          Needs no access to the repository: every package already carries
#          the file contents it needs.
# RUN:     Started and restarted by nuc-launcher.ps1 (scheduled task
#          MTS-NUC-Worker, at sign-in). Manual one-task test:
#          powershell -ExecutionPolicy Bypass -File C:\MTS-Worker\nuc-worker.ps1 -Once
# STOP:    End the scheduled task. A named lock allows only one copy at a time.
# SAFETY:  Never runs a command from a task, never writes outside the queue
#          share and its own folder. Everything it returns is reviewed on the
#          desktop before use.
# COMPAT:  Windows PowerShell 5.1.
[CmdletBinding()]
param(
    [string]$QueueRoot = '\\jis-nb\MTS-Queue',
    [string]$LocalRoot = 'C:\MTS-Worker',
    [string]$OllamaUrl = 'http://127.0.0.1:11434',
    [int]$PollSeconds = 15,
    [int]$RequestTimeoutSec = 7200,
    [int]$NumThread = 4,          # thermal cap 2026-09-29 (NUC ~98 C at 6 threads); a task's num_thread overrides
    [switch]$Once
)

$ErrorActionPreference = 'Stop'
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$SelfHash   = (Get-FileHash -Algorithm SHA256 -LiteralPath $PSCommandPath).Hash.Substring(0, 12).ToLower()
$Incoming   = Join-Path $QueueRoot 'incoming'
$Claimed    = Join-Path $QueueRoot 'claimed'
$Done       = Join-Path $QueueRoot 'done'
$DeployFile = Join-Path (Join-Path $QueueRoot 'deploy') 'nuc-worker.ps1'
$Outbox     = Join-Path $LocalRoot 'outbox'
$LogDir     = Join-Path $LocalRoot 'logs'
$LogFile    = Join-Path $LogDir 'worker.log'

function Get-UtcStamp { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }

function Write-TextNoBom([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, $Utf8NoBom)
}

function Write-Log([string]$Message) {
    $line = "$(Get-UtcStamp) $Message"
    Write-Host $line
    try { [System.IO.File]::AppendAllText($LogFile, $line + "`n", $Utf8NoBom) } catch { }
}

function Set-Heartbeat([string]$State, [string]$TaskId) {
    $hb = [ordered]@{ host = $env:COMPUTERNAME; state = $State; task = $TaskId; utc = (Get-UtcStamp); worker = $SelfHash; pid = $PID }
    $tmp = Join-Path $QueueRoot '.heartbeat.json.tmp'
    try {
        Write-TextNoBom $tmp ($hb | ConvertTo-Json -Compress)
        Move-Item -LiteralPath $tmp -Destination (Join-Path $QueueRoot 'heartbeat.json') -Force
    } catch { }
}

function Get-TaskId([string]$FileName, [string]$Suffix) {
    return $FileName.Substring(0, $FileName.Length - $Suffix.Length)
}

function Test-Ollama {
    try {
        $null = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 10 -UseBasicParsing
        return $true
    } catch { return $false }
}

function Test-NewVersion {
    if (-not (Test-Path -LiteralPath $DeployFile)) { return $false }
    try {
        $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $DeployFile).Hash.Substring(0, 12).ToLower()
        return ($h -ne $SelfHash)
    } catch { return $false }
}

# A task left in claimed\ with no local reply was interrupted (power cut,
# crash). Put it back so it runs again. Called once per start.
function Restore-Claimed {
    foreach ($f in @(Get-ChildItem -LiteralPath $Claimed -Filter '*.task.json' -File -ErrorAction SilentlyContinue)) {
        $id = Get-TaskId $f.Name '.task.json'
        if (Test-Path -LiteralPath (Join-Path $Outbox "$id.reply.json")) { continue }
        Move-Item -LiteralPath $f.FullName -Destination (Join-Path $Incoming $f.Name) -Force
        Write-Log "requeued interrupted task $id"
    }
}

# Replies are written locally first and delivered when the share is
# reachable, so a desktop that sleeps mid-task loses nothing.
function Send-Outbox {
    foreach ($r in @(Get-ChildItem -LiteralPath $Outbox -Filter '*.reply.json' -File -ErrorAction SilentlyContinue)) {
        $id = Get-TaskId $r.Name '.reply.json'
        $task = Join-Path $Claimed "$id.task.json"
        if (Test-Path -LiteralPath $task) {
            Move-Item -LiteralPath $task -Destination (Join-Path $Done "$id.task.json") -Force
        }
        $tmp = Join-Path $Done ".$id.reply.json.tmp"
        Copy-Item -LiteralPath $r.FullName -Destination $tmp -Force
        Move-Item -LiteralPath $tmp -Destination (Join-Path $Done $r.Name) -Force
        Remove-Item -LiteralPath $r.FullName -Force
        Write-Log "delivered $id"
    }
}

function Invoke-TaskPackage([string]$Path, [string]$Id) {
    $started = Get-Date
    $reply = [ordered]@{ schema = 1; id = $Id; worker = $SelfHash; host = $env:COMPUTERNAME; started_utc = (Get-UtcStamp) }
    try {
        $pkg = [System.IO.File]::ReadAllText($Path, $Utf8NoBom) | ConvertFrom-Json
        $reply.num_ctx = [int]$pkg.num_ctx
        $body = [ordered]@{
            model      = [string]$pkg.model
            prompt     = [string]$pkg.prompt
            stream     = $false
            keep_alive = '30m'
            options    = [ordered]@{ num_ctx = [int]$pkg.num_ctx; num_predict = [int]$pkg.num_predict; temperature = 0.2 }
        }
        if ($null -ne $pkg.think) { $body.think = [bool]$pkg.think }
        $nt = if ($null -ne $pkg.num_thread) { [int]$pkg.num_thread } else { $NumThread }
        if ($nt -gt 0) { $body.options.num_thread = $nt }
        $body = $body | ConvertTo-Json -Depth 5 -Compress
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
        $r = Invoke-RestMethod -Uri "$OllamaUrl/api/generate" -Method Post -Body $bytes `
            -ContentType 'application/json; charset=utf-8' -TimeoutSec $RequestTimeoutSec -UseBasicParsing
        $reply.worker_status     = 'ok'
        $reply.model             = $r.model
        $reply.response          = $r.response
        $reply.done_reason       = $r.done_reason
        $reply.prompt_eval_count = $r.prompt_eval_count
        $reply.eval_count        = $r.eval_count
        if ($r.total_duration) { $reply.model_seconds = [math]::Round([double]$r.total_duration / 1e9, 1) }
    } catch {
        $reply.worker_status = 'error'
        $reply.error = "$($_.Exception.Message)"
    }
    $reply.finished_utc = Get-UtcStamp
    $reply.wall_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1)
    return $reply
}

# ---- single-copy lock ----
$lockOwned = $false
$mutex = $null
try {
    $mutex = New-Object System.Threading.Mutex($true, 'Global\MTS-NUC-Worker', [ref]$lockOwned)
} catch { $lockOwned = $true }
if (-not $lockOwned) {
    Write-Host 'Another NUC worker is already running on this machine. Exiting.'
    exit 2
}

New-Item -ItemType Directory -Force -Path $Outbox, $LogDir | Out-Null
if ((Test-Path -LiteralPath $LogFile) -and ((Get-Item -LiteralPath $LogFile).Length -gt 5MB)) {
    Move-Item -LiteralPath $LogFile -Destination "$LogFile.1" -Force
}
Write-Log "worker $SelfHash started; queue $QueueRoot; model server $OllamaUrl"

$lastState = ''
$restored = $false
while ($true) {
    $state = 'idle'
    try {
        if (-not (Test-Path -LiteralPath $Incoming)) {
            $state = 'queue-unreachable'
        } elseif (Test-NewVersion) {
            Write-Log 'new worker version in the deploy folder; exiting so the launcher installs it'
            Set-Heartbeat 'updating' ''
            exit 10
        } else {
            foreach ($d in @($Claimed, $Done)) {
                if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
            }
            if (-not $restored) { Restore-Claimed; $restored = $true }
            Send-Outbox
            if (-not (Test-Ollama)) {
                $state = 'waiting-for-model-server'
            } else {
                $next = @(Get-ChildItem -LiteralPath $Incoming -Filter '*.task.json' -File |
                          Where-Object { $_.Name -notlike '.*' } | Sort-Object Name) | Select-Object -First 1
                if ($next) {
                    $id = Get-TaskId $next.Name '.task.json'
                    $claimedPath = Join-Path $Claimed $next.Name
                    $got = $true
                    try { Move-Item -LiteralPath $next.FullName -Destination $claimedPath -ErrorAction Stop } catch { $got = $false }
                    if ($got) {
                        Set-Heartbeat 'running' $id
                        Write-Log "running $id"
                        $reply = Invoke-TaskPackage $claimedPath $id
                        Write-TextNoBom (Join-Path $Outbox "$id.reply.json") ($reply | ConvertTo-Json -Depth 5)
                        Write-Log ("finished {0}: {1}; tokens in {2}, out {3}; {4} s" -f $id, $reply.worker_status, $reply.prompt_eval_count, $reply.eval_count, $reply.wall_seconds)
                        Send-Outbox
                        Set-Heartbeat 'idle' ''
                        if ($Once) { break }
                        continue
                    }
                }
            }
        }
    } catch {
        $state = 'error'
        Write-Log "loop error: $($_.Exception.Message)"
    }
    if ($state -ne $lastState) { Write-Log "state: $state"; $lastState = $state }
    if ($state -ne 'queue-unreachable') { Set-Heartbeat $state '' }
    if ($Once) { break }
    Start-Sleep -Seconds $PollSeconds
}
if ($mutex) { try { $mutex.ReleaseMutex() } catch { } }
