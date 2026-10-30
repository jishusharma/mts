# run-task.ps1 - AIBridge task runner: many steps, ONE bridge call, ONE compact report.
# Called by the agent when an AIRUN block carries task=<name> (playbook in <root>\tasks\<name>.json) or task=inline
# (the block body is the JSON plan). Windows PowerShell 5.1 compatible. Not meant to be typed by hand.
#
# Spec:  { "name": "...", "description": "...",
#          "params": { "repo": "C:\\default\\path", "slug": null },        # null = required
#          "steps": [ { "name": "gate", "cmd": "python scripts/dev/x.py {slug}", "cwd": "{repo}", "timeout_s": 300,
#                       "on_fail": "stop" | "continue" | "retry:2",           # default stop
#                       "expect": "regex that stdout must match",              # optional extra pass condition
#                       "capture": { "wt": "WORKTREE: (.+)" },                 # regex group 1 -> {wt} for later steps
#                       "show": 3 } ] }                                        # tail lines shown on PASS (default 1)
# {name} placeholders in cmd/cwd/expect are filled from params then captures. A failed step shows its last 25 lines.
param([Parameter(Mandatory)][string]$SpecFile)
$ErrorActionPreference = 'Stop'
$base = Split-Path -Parent $PSScriptRoot
$in = [IO.File]::ReadAllText($SpecFile) | ConvertFrom-Json
$taskId = [guid]::NewGuid().ToString('N').Substring(0, 8)
$logDir = Join-Path $base 'run\tasks'
if (-not (Test-Path -LiteralPath $logDir)) { [void](New-Item -ItemType Directory -Path $logDir -Force) }
$logFile = Join-Path $logDir ("$taskId.log")

function Write-Report { param([string]$s) Write-Output $s }

if ([string]$in.name -eq 'list') {
    foreach ($f in Get-ChildItem -LiteralPath (Join-Path $base 'tasks') -Filter *.json -ErrorAction SilentlyContinue) {
        $t = [IO.File]::ReadAllText($f.FullName) | ConvertFrom-Json
        $ps = @(); if ($t.params) { foreach ($p in $t.params.PSObject.Properties) { $ps += $(if ($null -eq $p.Value) { $p.Name + '=<required>' } else { $p.Name + '=' + $p.Value }) } }
        Write-Report ("{0}: {1}  [{2}]  steps={3}" -f $f.BaseName, $t.description, ($ps -join ', '), @($t.steps).Count)
    }
    Write-Report 'inline: put task=inline on the AIRUN line and a JSON plan {"steps":[{"name":..,"cmd":..}]} in the block body'
    exit 0
}

$spec = $in.spec
if (-not $spec) {
    $pf = Join-Path $base ('tasks\' + [string]$in.name + '.json')
    if (-not (Test-Path -LiteralPath $pf)) { Write-Report ("TASK RESULT: FAIL unknown task '{0}'. Send task=list to see the playbooks." -f $in.name); exit 2 }
    $spec = [IO.File]::ReadAllText($pf) | ConvertFrom-Json
}
$vars = @{}
if ($spec.params) { foreach ($p in $spec.params.PSObject.Properties) { if ($null -ne $p.Value) { $vars[$p.Name] = [string]$p.Value } } }
if ($in.params) { foreach ($p in $in.params.PSObject.Properties) { $vars[$p.Name] = [string]$p.Value } }
if ($spec.params) {
    $missing = @($spec.params.PSObject.Properties | Where-Object { $null -eq $_.Value -and -not $vars.ContainsKey($_.Name) } | ForEach-Object { $_.Name })
    if ($missing.Count) { Write-Report ("TASK RESULT: FAIL missing parameter(s): {0}. Add {0}=<value> to the AIRUN line." -f ($missing -join ', ')); exit 2 }
}
function Expand-Vars { param([string]$s) if (-not $s) { return $s }; return [regex]::Replace($s, '\{([A-Za-z_][A-Za-z0-9_]*)\}', { param($m) if ($vars.ContainsKey($m.Groups[1].Value)) { $vars[$m.Groups[1].Value] } else { $m.Value } }) }

$steps = @($spec.steps)
$label = if ($spec.name) { [string]$spec.name } else { [string]$in.name }
$report = New-Object System.Collections.Generic.List[string]
$report.Add(("TASK {0} id={1} steps={2} host={3}" -f $label, $taskId, $steps.Count, $env:COMPUTERNAME))
$failedAt = 0; $failedName = ''; $totalSw = [Diagnostics.Stopwatch]::StartNew()
$i = 0
foreach ($st in $steps) {
    $i++
    $sname = if ($st.name) { [string]$st.name } else { "step$i" }
    if ($failedAt) { $report.Add(("{0,2} SKIP  {1} (stopped at step {2})" -f $i, $sname, $failedAt)); continue }
    $cmd = Expand-Vars ([string]$st.cmd)
    $cwd = Expand-Vars ([string]$st.cwd)
    if (-not $cwd) { $cwd = (Get-Location).Path }
    $tmo = if ($st.timeout_s) { [int]$st.timeout_s } else { 120 }
    $retries = 0; $onFail = if ($st.on_fail) { [string]$st.on_fail } else { 'stop' }
    if ($onFail -match '^retry:(\d+)$') { $retries = [int]$Matches[1]; $onFail = 'stop' }
    $attempt = 0; $ok = $false; $out = ''; $code = 0; $ms = 0; $why = ''
    do {
        $attempt++
        $ps1 = Join-Path $base ('run\' + [guid]::NewGuid().ToString('N') + '.ps1')
        [IO.File]::WriteAllText($ps1, "`$ProgressPreference='SilentlyContinue'; [Console]::OutputEncoding=[Text.Encoding]::UTF8; " + $cmd, [Text.UTF8Encoding]::new($true))
        $so = $ps1 + '.out'; $se = $ps1 + '.err'
        $sw = [Diagnostics.Stopwatch]::StartNew()
        try {
            $p = Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', $ps1) -WorkingDirectory $cwd -RedirectStandardOutput $so -RedirectStandardError $se -PassThru -WindowStyle Hidden
            $null = $p.Handle   # without this ExitCode can read back empty after WaitForExit(ms)
            if (-not $p.WaitForExit($tmo * 1000)) { try { & taskkill.exe /T /F /PID $p.Id | Out-Null } catch {}; $why = "timeout after $tmo s"; $code = -1 } else { $p.WaitForExit(); $code = [int]$p.ExitCode }
        } catch { $why = $_.Exception.Message; $code = -2 }
        $sw.Stop(); $ms = $sw.ElapsedMilliseconds
        $out = ''
        if (Test-Path -LiteralPath $so) { $out = [IO.File]::ReadAllText($so) }
        if (Test-Path -LiteralPath $se) { $e = [IO.File]::ReadAllText($se); if ($e) { $out += "`n" + $e } }
        Remove-Item -LiteralPath $ps1, $so, $se -Force -ErrorAction SilentlyContinue
        $ok = ($code -eq 0)
        if ($ok -and $st.expect) {
            $ex = Expand-Vars ([string]$st.expect)
            if ($out -notmatch $ex) { $ok = $false; $why = "output did not match expect /$ex/" }
        }
        if (-not $ok -and -not $why) { $why = "exit $code" }
    } while (-not $ok -and $attempt -le $retries)
    Add-Content -LiteralPath $logFile -Value ("=== step {0} {1} exit={2} ms={3} ok={4}`n{5}`n" -f $i, $sname, $code, $ms, $ok, $out) -Encoding UTF8
    $lines = @(($out -split "`r?`n") | Where-Object { $_.Trim() -ne '' })
    if ($ok -and $st.capture) {
        foreach ($c in $st.capture.PSObject.Properties) { $m = [regex]::Match($out, [string]$c.Value); if ($m.Success) { $vars[$c.Name] = $m.Groups[1].Value.Trim() } }
    }
    $secs = [math]::Round($ms / 1000, 1)
    $retryNote = if ($attempt -gt 1) { " (attempt $attempt)" } else { '' }
    if ($ok) {
        $report.Add(("{0,2} PASS  {1}  {2}s{3}" -f $i, $sname, $secs, $retryNote))
        $show = if ($null -ne $st.show) { [int]$st.show } else { 1 }
        if ($show -gt 0) { foreach ($l in ($lines | Select-Object -Last $show)) { $report.Add('   | ' + $(if ($l.Length -gt 240) { $l.Substring(0, 240) + '...' } else { $l })) } }
    } else {
        $report.Add(("{0,2} FAIL  {1}  {2}s  {3}{4}" -f $i, $sname, $secs, $why, $retryNote))
        foreach ($l in ($lines | Select-Object -Last 25)) { $report.Add('   | ' + $(if ($l.Length -gt 240) { $l.Substring(0, 240) + '...' } else { $l })) }
        if ($onFail -ne 'continue') { $failedAt = $i; $failedName = $sname }
    }
}
$totalSw.Stop()
$secsAll = [math]::Round($totalSw.Elapsed.TotalSeconds, 1)
if ($failedAt) { $report.Add(("TASK RESULT: FAIL at step {0} ({1}) after {2}s; full log: {3}" -f $failedAt, $failedName, $secsAll, $logFile)) }
else { $report.Add(("TASK RESULT: PASS {0} steps in {1}s; full log: {2}" -f $steps.Count, $secsAll, $logFile)) }
$report | ForEach-Object { Write-Output $_ }
if ($failedAt) { exit 1 } else { exit 0 }
