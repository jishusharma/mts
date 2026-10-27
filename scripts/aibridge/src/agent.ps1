$ErrorActionPreference = 'Stop'
$AgentVersion = '0.7.1'
$AgentStart = Get-Date
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$config = Get-Content -Raw -LiteralPath (Join-Path $root 'config.json') | ConvertFrom-Json
. (Join-Path $root 'checks.ps1')
. (Join-Path $root 'audit.ps1')
. (Join-Path $root 'concurrency.ps1')

foreach ($o in $config.allowed_origins) {
    $ol = ([string]$o).ToLower()
    if ($ol -eq '*' -or $ol -eq 'null' -or $ol -eq '') {
        Write-Host "refusing to start: allowed_origins contains wildcard, null, or empty"
        exit 1
    }
}

$MaxBody = 1048576
# v0.7.0: parallel chats. Commands run as child processes that the accept loop polls, so one slow
# command (a 200 s gate run) never blocks another chat's request.
$script:Jobs = New-Object System.Collections.ArrayList
$script:ChildPsVersion = ''
try { $script:ChildPsVersion = ((& powershell.exe -NoProfile -NonInteractive -Command '$PSVersionTable.PSVersion.ToString()') | Out-String).Trim() } catch {}
$script:PwshPath = ''
try { $pc = Get-Command pwsh.exe -ErrorAction SilentlyContinue; if ($pc) { $script:PwshPath = $pc.Source } } catch {}

function Send-Resp {
    param($stream, [int]$code, [string]$reason, [string]$body, [string]$corsOrigin)
    $bytes = [Text.Encoding]::UTF8.GetBytes($body)
    $extra = ''
    if ($corsOrigin) {
        $extra = "Access-Control-Allow-Origin: $corsOrigin`r`nAccess-Control-Allow-Methods: GET, POST, OPTIONS`r`nAccess-Control-Allow-Headers: Content-Type`r`nVary: Origin`r`n"
    } else {
        $extra = "Vary: Origin`r`n"
    }
    $hdr = "HTTP/1.1 $code $reason`r`nContent-Type: application/json`r`nCache-Control: no-store`r`nContent-Length: $($bytes.Length)`r`nConnection: close`r`n$extra`r`n"
    $hb = [Text.Encoding]::ASCII.GetBytes($hdr)
    $stream.Write($hb, 0, $hb.Length)
    if ($bytes.Length -gt 0) { $stream.Write($bytes, 0, $bytes.Length) }
    $stream.Flush()
}
function Read-Line {
    param($stream)
    $sb = New-Object Text.StringBuilder
    while ($true) {
        $b = $stream.ReadByte()
        if ($b -lt 0) { break }
        if ($b -eq 13) { continue }
        if ($b -eq 10) { break }
        [void]$sb.Append([char]$b)
    }
    return $sb.ToString()
}
Add-Type -TypeDefinition @"
using System; using System.IO; using System.Text; using System.Threading;
public class CapReader {
    public StringBuilder Sb = new StringBuilder();
    public long Kept = 0; public long Total = 0; public bool Truncated = false;
    StreamReader r; int cap; Thread t;
    public CapReader(StreamReader reader, int capBytes) { r = reader; cap = capBytes; t = new Thread(Run); t.IsBackground = true; t.Start(); }
    void Run() {
        char[] buf = new char[4096]; int n;
        while ((n = r.Read(buf, 0, buf.Length)) > 0) {
            int bytes = Encoding.UTF8.GetByteCount(buf, 0, n);
            Total += bytes;
            if (!Truncated && Kept + bytes <= cap) { Sb.Append(buf, 0, n); Kept += bytes; continue; }
            if (!Truncated) {
                int i = 0;
                while (i < n) { int b = Encoding.UTF8.GetByteCount(buf, i, 1); if (Kept + b > cap) break; Sb.Append(buf[i]); Kept += b; i++; }
                Truncated = true;
            }
        }
    }
    public void Wait(int ms) { t.Join(ms); }
}
"@

# ---- fresh environment (A7): a child sees the registry as it is NOW, not what the agent saw at its own start ----
function Expand-Fresh {
    param([string]$s, $vars)
    if (-not $s) { return $s }
    return [regex]::Replace($s, '%([^%]+)%', {
        param($m)
        $n = $m.Groups[1].Value
        foreach ($k in $vars.Keys) { if ([string]$k -ieq $n) { return [string]$vars[$k] } }
        $v = [Environment]::GetEnvironmentVariable($n)
        if ($null -ne $v) { return $v }
        return $m.Value
    })
}
function Set-FreshEnv {
    param($psi, [string]$TempDir)
    $fresh = @{}
    foreach ($scope in 'Machine', 'User') {
        $vars = [Environment]::GetEnvironmentVariables($scope)
        foreach ($k in $vars.Keys) {
            $kn = [string]$k
            if ($kn -ieq 'Path' -or $kn -ieq 'PSModulePath') { continue }
            $fresh[$kn] = [string]$vars[$k]
        }
    }
    $expanded = @{}
    foreach ($k in $fresh.Keys) { $expanded[$k] = Expand-Fresh $fresh[$k] $fresh }
    foreach ($k in $expanded.Keys) { $psi.EnvironmentVariables[$k] = $expanded[$k] }
    $mp = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $up = [Environment]::GetEnvironmentVariable('Path', 'User')
    $psi.EnvironmentVariables['Path'] = (Expand-Fresh (($mp + ';' + $up).Trim(';')) $fresh)
    if ($TempDir) {
        if (-not (Test-Path -LiteralPath $TempDir)) { [void](New-Item -ItemType Directory -Path $TempDir -Force) }
        $psi.EnvironmentVariables['TEMP'] = $TempDir
        $psi.EnvironmentVariables['TMP'] = $TempDir
    }
}

function Start-Cmd {
    param([string]$Cmd, [string]$Cwd, [int]$MaxBytes, $pol, [string]$Shell)
    $wrapped = "`$ProgressPreference='SilentlyContinue'; [Console]::OutputEncoding=[Text.Encoding]::UTF8; " + $Cmd
    $runDir = Join-Path $root 'run'
    if (-not (Test-Path -LiteralPath $runDir)) { [void](New-Item -ItemType Directory -Path $runDir) }
    $tmpPs1 = Join-Path $runDir ([guid]::NewGuid().ToString('N') + '.ps1')
    [IO.File]::WriteAllText($tmpPs1, $wrapped, [Text.UTF8Encoding]::new($true))
    $psi = New-Object Diagnostics.ProcessStartInfo
    if ($Shell -eq 'pwsh' -and $script:PwshPath) { $psi.FileName = $script:PwshPath } else { $psi.FileName = 'powershell.exe' }
    $psi.Arguments = "-NoProfile -NonInteractive -OutputFormat Text -ExecutionPolicy Bypass -File `"$tmpPs1`""
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [Text.Encoding]::UTF8
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WorkingDirectory = $Cwd
    $tmpDir = [string]$pol.child_temp
    if (-not $tmpDir) { $tmpDir = Join-Path $root 'run\tmp' } elseif (-not [IO.Path]::IsPathRooted($tmpDir)) { $tmpDir = Join-Path $root $tmpDir }
    if ([string]$pol.fresh_env -ne 'false') { try { Set-FreshEnv $psi $tmpDir } catch {} }
    $p = [Diagnostics.Process]::Start($psi)
    $ro = New-Object CapReader($p.StandardOutput, $MaxBytes)
    $re = New-Object CapReader($p.StandardError, $MaxBytes)
    return @{ p = $p; ro = $ro; re = $re; tmp = $tmpPs1; max = $MaxBytes }
}
function Complete-Cmd {
    param($h, [int]$TimeoutS, [bool]$TimedOut)
    $p = $h.p; $ro = $h.ro; $re = $h.re
    if ($TimedOut) {
        try { & taskkill.exe /T /F /PID $p.Id | Out-Null } catch { try { $p.Kill() } catch {} }
        try { $p.WaitForExit(5000) | Out-Null } catch {}
    }
    $ro.Wait(5000); $re.Wait(5000)
    $MaxBytes = $h.max
    $out = $ro.Sb.ToString(); $err = $re.Sb.ToString()
    if ($ro.Truncated) { $out += "`n[TRUNCATED: stdout cut at $MaxBytes bytes; $($ro.Total - $ro.Kept) further bytes discarded]" }
    if ($re.Truncated) { $err += "`n[TRUNCATED: stderr cut at $MaxBytes bytes; $($re.Total - $re.Kept) further bytes discarded]" }
    try { Remove-Item -LiteralPath $h.tmp -Force -ErrorAction SilentlyContinue } catch {}
    $code = if ($TimedOut) { -1 } else { $p.ExitCode }
    if ($TimedOut) { $err += "`n[TIMEOUT: killed after $TimeoutS s]" }
    return @{ exit = $code; out = $out; err = $err; timed_out = $TimedOut; out_truncated = $ro.Truncated; out_bytes = $ro.Total }
}

function Get-Sha12 {
    param([string]$s)
    $sha = [Security.Cryptography.SHA256]::Create()
    $hb = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($s))
    return ((-join ($hb | ForEach-Object { '{0:x2}' -f $_ })).Substring(0, 12))
}
function Get-Meta {
    # receipt fields echoed on EVERY response (ok, refused, error): which request this answers and what the agent received
    param($req, [string]$cmd, [string]$kind)
    $lines = 0
    if ($cmd) { $lines = ($cmd -split "`n").Count }
    return [ordered]@{
        rid = [string]$req.rid; host = $env:COMPUTERNAME; agent = $AgentVersion; kind = $kind
        cmd_lines = $lines; cmd_len = $cmd.Length; cmd_sha = (Get-Sha12 $cmd)
        at = (Get-Date).ToUniversalTime().ToString('o')
    }
}

if (-not (Test-AuditChain)) {
    Write-Host 'refusing to start: audit chain invalid'
    exit 1
}

function Complete-Job {
    param($j)
    try {
        $result = Complete-Cmd $j.h $j.tmo $j.timedOut
        if ($j.taskfile) { try { Remove-Item -LiteralPath $j.taskfile -Force -ErrorAction SilentlyContinue } catch {} }
        $j.sw.Stop()
        $hash = ''
        if ($result.out) { $hash = Get-Sha12 $result.out }
        $audit = $j.audit
        $audit.result = 'ok'; $audit.reason = 'ok'
        $audit.exit = $result.exit; $audit.out_bytes = $result.out_bytes; $audit.out_truncated = $result.out_truncated; $audit.timed_out = $result.timed_out; $audit.out_hash = $hash; $audit.ms = $j.sw.ElapsedMilliseconds
        Write-Audit $audit
        $resp = [ordered]@{ exit = $result.exit; out = $result.out; err = $result.err; ms = $j.sw.ElapsedMilliseconds; timed_out = $result.timed_out; out_truncated = $result.out_truncated; out_bytes = $result.out_bytes; timeout_s = $j.tmo; shell = $j.shell }
        foreach ($k in $j.meta.Keys) { $resp[$k] = $j.meta[$k] }
        Send-Resp $j.stream 200 'OK' ($resp | ConvertTo-Json -Depth 6 -Compress) $j.cors
    } catch {
        try { $j.audit.result = 'error'; $j.audit.reason = $_.Exception.Message; Write-Audit $j.audit } catch {}
        try { Send-Resp $j.stream 500 'Error' (@{ error = $_.Exception.Message } | ConvertTo-Json -Compress) $j.cors } catch {}
    } finally {
        try { $j.client.Close() } catch {}
        Release-ConnectionSlot
    }
}

function Handle-Client {
    param($client)
    $stream = $client.GetStream()
    try { $client.ReceiveTimeout = 15000 } catch {}
    if (-not (Test-ConnectionSlot)) {
        $audit429 = [ordered]@{
            ts = (Get-Date).ToUniversalTime().ToString('o')
            ip = $client.Client.RemoteEndPoint.Address.ToString()
            result = 'refused'
            reason = 'too_many_connections'
        }
        try { Write-Audit $audit429 } catch {}
        try {
            $body429 = '{"error":"too_many_connections","reason":"too_many_connections: the agent is running its maximum number of commands at once; retry in a few seconds"}'
            $bb429 = [Text.Encoding]::UTF8.GetBytes($body429)
            $hdr429 = "HTTP/1.1 429 Too Many Requests`r`nContent-Type: application/json`r`nContent-Length: $($bb429.Length)`r`nConnection: close`r`nVary: Origin`r`n`r`n"
            $hb429 = [Text.Encoding]::ASCII.GetBytes($hdr429)
            $stream.Write($hb429, 0, $hb429.Length)
            $stream.Write($bb429, 0, $bb429.Length)
            $stream.Flush()
        } catch {}
        try { $client.Close() } catch {}
        return
    }

    $corsOrigin = ''
    $started = $false
    $audit = [ordered]@{
        ts = (Get-Date).ToUniversalTime().ToString('o')
        ip = $client.Client.RemoteEndPoint.Address.ToString()
    }
    try {
        $reqLine = Read-Line $stream
        $headers = @{}
        while ($true) {
            $line = Read-Line $stream
            if ($line -eq '') { break }
            $i = $line.IndexOf(':')
            if ($i -gt 0) {
                $k = $line.Substring(0, $i).Trim().ToLower()
                $headers[$k] = $line.Substring($i + 1).Trim()
            }
        }
        $reqOrigin = ''
        if ($headers['origin']) { $reqOrigin = $headers['origin'] }
        if ($config.allowed_origins -contains $reqOrigin) { $corsOrigin = $reqOrigin }

        $parts = $reqLine -split ' '
        $method = if ($parts.Count -ge 1) { $parts[0] } else { '' }
        $path   = if ($parts.Count -ge 2) { $parts[1] } else { '' }

        if ($method -eq 'OPTIONS' -and ($path -eq '/run' -or $path -eq '/ping')) {
            $audit.result = 'refused'; $audit.reason = 'preflight'
            Write-Audit $audit
            Send-Resp $stream 204 'No Content' '' $corsOrigin
            $client.Close(); return
        }
        # liveness + identity probe. No secrets, no token needed; the extension uses it as the session preflight.
        if ($method -eq 'GET' -and $path -eq '/ping') {
            $pp = Get-Content -Raw -LiteralPath (Join-Path $root 'policy.json') | ConvertFrom-Json
            $info = [ordered]@{
                ok = $true; agent = $AgentVersion; host = $env:COMPUTERNAME; pid = $PID
                shell = 'powershell.exe'; shell_version = $script:ChildPsVersion; pwsh = [bool]$script:PwshPath
                uptime_s = [int]((Get-Date) - $AgentStart).TotalSeconds; running = $script:Jobs.Count
                mode = [string]$pp.mode; auto_mode = [string]$pp.auto_mode
                time = (Get-Date).ToUniversalTime().ToString('o')
            }
            Send-Resp $stream 200 'OK' ($info | ConvertTo-Json -Compress) $corsOrigin
            $client.Close(); return
        }

        $len = 0
        if ($headers['content-length']) { $len = [int]$headers['content-length'] }
        if ($len -gt $MaxBody) {
            $audit.result = 'refused'; $audit.reason = 'body_too_large'; $audit.len = $len
            Write-Audit $audit
            Send-Resp $stream 413 'Payload Too Large' '{"error":"body_too_large"}' $corsOrigin
            $client.Close(); return
        }
        $body = ''
        if ($len -gt 0) {
            $buf = New-Object byte[] $len
            $read = 0
            while ($read -lt $len) {
                $n = $stream.Read($buf, $read, $len - $read)
                if ($n -le 0) { break }
                $read += $n
            }
            $body = [Text.Encoding]::UTF8.GetString($buf, 0, $read)
        }
        if ($method -ne 'POST' -or $path -ne '/run') {
            $audit.result = 'refused'; $audit.reason = 'not_found'
            Write-Audit $audit
            Send-Resp $stream 404 'Not Found' '{"error":"not_found"}' $corsOrigin
            $client.Close(); return
        }
        if ($config.allowed_origins -notcontains $reqOrigin) {
            $audit.result = 'refused'; $audit.reason = 'bad_origin'
            Write-Audit $audit
            Send-Resp $stream 403 'Forbidden' '{"error":"bad_origin"}' $corsOrigin
            $client.Close(); return
        }
        $req = $null
        try { $req = $body | ConvertFrom-Json } catch {}
        if ($null -eq $req -or $req.token -ne $config.token) {
            $audit.result = 'refused'; $audit.reason = 'bad_token'
            Write-Audit $audit
            Send-Resp $stream 403 'Forbidden' '{"error":"bad_token"}' $corsOrigin
            $client.Close(); return
        }

        $cmd = [string]$req.cmd
        $cwd = if ($req.cwd) { [string]$req.cwd } else { '' }
        $shell = if ([string]$req.shell -eq 'pwsh') { 'pwsh' } else { 'powershell' }
        $audit.cmd = $cmd
        $audit.cwd = $cwd
        if ($req.auto) { $audit.auto = $true }
        if ($req.rid) { $audit.rid = [string]$req.rid }
        $pol = Get-Content -Raw -LiteralPath (Join-Path $root 'policy.json') | ConvertFrom-Json
        $softS = [int]$pol.timeout_soft_s; $hardS = [int]$pol.timeout_hard_s
        # task mode: one call runs a whole playbook (tasks\<name>.json) or an inline plan through scripts\run-task.ps1
        $taskName = [string]$req.task
        $taskFile = ''
        $taskErr = $null
        if ($taskName) {
            $softS = 600; $hardS = if ($pol.timeout_task_s) { [int]$pol.timeout_task_s } else { 1800 }
            $spec = $null
            if ($taskName -eq 'inline') {
                try { $spec = ([string]$req.task_spec | ConvertFrom-Json) } catch { $taskErr = New-Refusal 'bad_task_spec' "the inline plan is not valid JSON: $($_.Exception.Message)" }
                if (-not $taskErr -and (-not $spec.steps -or @($spec.steps).Count -eq 0)) { $taskErr = New-Refusal 'bad_task_spec' 'the inline plan has no steps' }
                if (-not $taskErr) {
                    $si = 0
                    foreach ($stp in @($spec.steps)) {
                        $si++
                        $stCwd = if ($stp.cwd -and ([string]$stp.cwd -notmatch '\{')) { [string]$stp.cwd } else { $cwd }
                        $sc = Test-Allowed -Cmd ([string]$stp.cmd) -Cwd $stCwd -pol $pol -Auto ([bool]$req.auto) -Write ([bool]$req.write)
                        if ($sc.ok -and [string]$req.shell -ne 'pwsh') { $sc = Test-Ps5Lint ([string]$stp.cmd) }
                        if (-not $sc.ok) { $taskErr = @{ ok = $false; reason = ("task step $si ($($stp.name)): " + $sc.reason) }; break }
                    }
                }
            }
            $taskFile = Join-Path $root ('run\task_' + [guid]::NewGuid().ToString('N') + '.json')
            if (-not (Test-Path -LiteralPath (Join-Path $root 'run'))) { [void](New-Item -ItemType Directory -Path (Join-Path $root 'run')) }
            [IO.File]::WriteAllText($taskFile, ([ordered]@{ name = $taskName; params = $req.task_params; spec = $spec } | ConvertTo-Json -Depth 12 -Compress), [Text.UTF8Encoding]::new($false))
            $cmd = "& '" + (Join-Path (Split-Path -Parent $root) 'scripts\run-task.ps1') + "' -SpecFile '" + $taskFile + "'; exit `$LASTEXITCODE"
            $audit.cmd = 'task=' + $taskName + ' ' + ([string]($req.task_params | ConvertTo-Json -Compress))
        }
        $tmo = $softS
        if ($req.timeout_s) {
            $tmo = [int]$req.timeout_s
            if ($tmo -lt 1) { $tmo = $softS }
            if ($tmo -gt $hardS) { $tmo = $hardS; $audit.timeout_clamped = $true }
        }
        $audit.timeout_s = $tmo
        $kind = Get-CmdKind $cmd $pol
        $meta = Get-Meta $req $cmd $kind
        if ($taskName) { $meta['task'] = $taskName; $meta['kind'] = 'task' }
        $chk = Test-Allowed -Cmd $cmd -Cwd $cwd -pol $pol -Auto ([bool]$req.auto) -Write ([bool]$req.write)
        if ($taskErr) { $chk = $taskErr }
        if ($chk.ok) {
            if ($shell -eq 'pwsh' -and -not $script:PwshPath) { $chk = New-Refusal 'no_pwsh' 'shell=pwsh asked but pwsh.exe is not installed on this host; use the default Windows PowerShell 5.1' }
            elseif ($shell -ne 'pwsh' -and -not $taskName) { $chk = Test-Ps5Lint $cmd }
        }
        if ($req.dry) {
            if ($taskFile) { try { Remove-Item -LiteralPath $taskFile -Force -ErrorAction SilentlyContinue } catch {} }
            $dry = [ordered]@{ dry = $true; ok = [bool]$chk.ok; reason = [string]$chk.reason }
            foreach ($k in $meta.Keys) { $dry[$k] = $meta[$k] }
            Send-Resp $stream 200 'OK' ($dry | ConvertTo-Json -Compress) $corsOrigin
            $client.Close(); return
        }
        if (-not $chk.ok) {
            $audit.result = 'refused'; $audit.reason = $chk.reason
            Write-Audit $audit
            if ($taskFile) { try { Remove-Item -LiteralPath $taskFile -Force -ErrorAction SilentlyContinue } catch {} }
            $rb = [ordered]@{ error = 'refused'; reason = $chk.reason }
            foreach ($k in $meta.Keys) { $rb[$k] = $meta[$k] }
            Send-Resp $stream 403 'Forbidden' ( $rb | ConvertTo-Json -Compress ) $corsOrigin
            $client.Close(); return
        }
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $h = Start-Cmd -Cmd $cmd -Cwd $cwd -MaxBytes ([int]$pol.max_output_bytes) -pol $pol -Shell $shell
        $meta['started'] = (Get-Date).ToUniversalTime().ToString('o')
        [void]$script:Jobs.Add(@{
            client = $client; stream = $stream; cors = $corsOrigin; h = $h; audit = $audit; meta = $meta
            tmo = $tmo; deadline = (Get-Date).AddSeconds($tmo); sw = $sw; timedOut = $false; shell = $shell; taskfile = $taskFile
        })
        $started = $true
    } catch {
        try { $audit.result = 'error'; $audit.reason = $_.Exception.Message; Write-Audit $audit } catch {}
        try { Send-Resp $stream 500 'Error' (@{ error = $_.Exception.Message } | ConvertTo-Json -Compress) $corsOrigin } catch {}
        try { $client.Close() } catch {}
    } finally {
        if (-not $started) { Release-ConnectionSlot }
    }
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse($config.bind), [int]$config.port)
$listener.Start()
Write-Host "AIBridge agent $AgentVersion on $($config.bind):$($config.port) host $env:COMPUTERNAME"
while ($true) {
    $busy = $false
    if ($listener.Pending()) {
        $busy = $true
        $client = $listener.AcceptTcpClient()
        try { Handle-Client $client } catch { try { $client.Close() } catch {} }
    }
    for ($ji = $script:Jobs.Count - 1; $ji -ge 0; $ji--) {
        $j = $script:Jobs[$ji]
        $done = $j.h.p.HasExited
        if (-not $done -and (Get-Date) -gt $j.deadline) { $j.timedOut = $true; $done = $true }
        if ($done) {
            $script:Jobs.RemoveAt($ji)
            Complete-Job $j
            $busy = $true
        }
    }
    if (-not $busy) { Start-Sleep -Milliseconds 25 }
}
