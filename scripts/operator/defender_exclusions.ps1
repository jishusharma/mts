<#
.SYNOPSIS
  Microsoft Defender exclusions for the MTS work trees and the Gemini / GPT (Codex) agent lanes. B175.
.DESCRIPTION
  Real-time scanning of every file that pytest, git, node, codex and gemini touch holds MsMpEng at 25-30 % CPU
  while the agent lanes run parallel test gates. This adds path, process and extension exclusions so that traffic
  is not scanned. Idempotent: running it twice changes nothing. Needs an elevated shell (it re-launches itself).

  .\defender_exclusions.ps1               apply
  .\defender_exclusions.ps1 -Check        list what is missing, change nothing
  .\defender_exclusions.ps1 -Remove       take every exclusion this script adds back out
  .\defender_exclusions.ps1 -StopIntelSur also stop Intel System Usage Report (SystemUsageReportSvc_QUEENCREEK)

  Risk: process exclusions for python/node/git/java mean files those processes open are not scanned in real time.
  Downloaded executables are still scanned when written by a browser or Explorer. Testnet-only box; keep it that way.
#>
[CmdletBinding()]
param([switch]$Check, [switch]$Remove, [switch]$StopIntelSur, [switch]$StopPcaSvc, [switch]$Diagnose)

$ErrorActionPreference = 'Stop'
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"")
    if ($Check) { $argList += '-Check' }
    if ($Remove) { $argList += '-Remove' }
    if ($StopIntelSur) { $argList += '-StopIntelSur' }
    if ($StopPcaSvc) { $argList += '-StopPcaSvc' }
    if ($Diagnose) { $argList += '-Diagnose' }
    Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList $argList -Verb RunAs -Wait
    return
}

$logDir = 'F:\MTS\scratch'
if (-not (Test-Path $logDir)) { $logDir = $env:TEMP }
try { Start-Transcript -Path (Join-Path $logDir 'defender_exclusions.log') -Force | Out-Null } catch { }
$up = $env:USERPROFILE
$la = $env:LOCALAPPDATA
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

$paths = @(
    $repo,                                   # IdeaProjects\BinanceDataFeed (this tree)
    'F:\MTS',                                # every lane tree: mts-gemini, mts-codex, mts-codex-lab, mts-dsa, data, backups
    "$up\IdeaProjects",
    "$up\.claude",                           # Claude Code transcripts, hook state (turn meter, signals), plugins
    "$up\.gemini",                           # Gemini CLI / Antigravity state, logs, tmp
    "$up\.cache\codex-runtimes",             # Codex node runtime + dependencies
    "$la\OpenAI\Codex",                      # codex.exe, cua_node, sandbox service
    "$up\.codex",
    "$la\Temp\pytest-of-$env:USERNAME",
    "$up\.m2",
    "$up\.gradle",
    "$la\pip\Cache",
    "$la\Programs\Python",
    'C:\Program Files\Git',
    'C:\Program Files\nodejs'
) | Where-Object { $_ } | Select-Object -Unique

$procs = @(
    'python.exe', 'pythonw.exe', 'pytest.exe',
    'git.exe', 'git-remote-https.exe',
    'node.exe', 'node_repl.exe', 'npx.cmd',
    'codex.exe', 'codex-windows-sandbox-service.exe', 'codex-computer-use-swift.exe',
    'java.exe', 'javaw.exe', 'mvn.cmd',
    'gemini.exe',
    'sh.exe', 'bash.exe', 'Code.exe', 'claude.exe', 'ChatGPT.exe'
)

$exts = @('class', 'jar', 'pyc', 'pyo', 'obj')

$pref = Get-MpPreference
$have = @{
    Path      = @($pref.ExclusionPath)
    Process   = @($pref.ExclusionProcess)
    Extension = @($pref.ExclusionExtension)
}
function Has($kind, $v) { $have[$kind] -contains $v -or ($have[$kind] | Where-Object { $_ -ieq $v }) }

$missing = 0
function Apply($kind, $items) {
    foreach ($i in $items) {
        $present = [bool](Has $kind $i)
        if ($Remove) {
            if (-not $present) { continue }
            $arg = @{ "Exclusion$kind" = $i }
            if (-not $Check) { Remove-MpPreference @arg }
            Write-Host "remove  $kind  $i"
        } elseif (-not $present) {
            $script:missing++
            $arg = @{ "Exclusion$kind" = $i }
            if (-not $Check) { Add-MpPreference @arg }
            Write-Host "add     $kind  $i"
        }
    }
}
Apply 'Path' $paths
Apply 'Process' $procs
Apply 'Extension' $exts

if (-not $Check -and -not $Remove) {
    # scheduled scans only, real-time protection untouched
    Set-MpPreference -ScanAvgCPULoadFactor 10 -DisableCpuThrottleOnIdleScans $false
}

if ($StopIntelSur -and -not $Check) {
    $svc = 'SystemUsageReportSvc_QUEENCREEK'
    if ($Remove) {
        Set-Service $svc -StartupType Automatic; Start-Service $svc -ErrorAction SilentlyContinue
        Write-Host "Intel SUR restored to Automatic"
    } else {
        Stop-Service $svc -Force -ErrorAction SilentlyContinue; Set-Service $svc -StartupType Manual
        Write-Host "Intel SUR stopped, startup Manual (undo with -Remove -StopIntelSur)"
    }
}

if ($StopPcaSvc -and -not $Check) {
    # Program Compatibility Assistant: 25 % CPU from the constant python/git process launches; hosts only itself
    if ($Remove) { Set-Service PcaSvc -StartupType Automatic; Start-Service PcaSvc -ErrorAction SilentlyContinue; Write-Host 'PcaSvc restored' }
    else {
        # disable first: the stop can hang in Stop Pending, which blocked the old order
        & sc.exe config PcaSvc start= disabled | Out-Host
        $host7 = (Get-CimInstance Win32_Service -Filter "Name='PcaSvc'").ProcessId
        & sc.exe stop PcaSvc | Out-Host
        Start-Sleep 5
        $left = (Get-CimInstance Win32_Service -Filter "Name='PcaSvc'")
        if ($left.State -ne 'Stopped' -and $host7) {
            # a hung stop: end the host process, but only when it hosts PcaSvc alone
            $others = @(Get-CimInstance Win32_Service -Filter "ProcessId=$host7" | Where-Object Name -ne 'PcaSvc')
            if ($others.Count -eq 0) { Stop-Process -Id $host7 -Force; Write-Host "ended hung PcaSvc host pid $host7" }
            else { Write-Host "pid $host7 also hosts $($others.Name -join ','); left running" }
        }
        Write-Host ("PcaSvc now: " + (Get-Service PcaSvc).Status + ' (undo: -Remove -StopPcaSvc)')
    }
}

if ($Diagnose) {
    # 30 s Defender performance recording: what MsMpEng is still scanning
    $rec = Join-Path $env:TEMP 'mpperf.etl'
    New-MpPerformanceRecording -RecordTo $rec -Seconds 30
    Get-MpPerformanceReport -Path $rec -TopScans 15 -TopProcesses 10 -TopPaths 15 -TopExtensions 8 | Out-String -Width 200 | Write-Host
}

if ($Check) { Write-Host "$missing exclusion(s) missing" } else { Write-Host 'done; re-run with -Check to verify' }
try { Stop-Transcript | Out-Null } catch { }
Read-Host 'Press Enter to close' | Out-Null
