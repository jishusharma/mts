# checks.ps1 - path policy for AIBridge agent. Dot-sourced from agent.ps1.
# No per-command allowlist. Policy lives in policy.json. Denials always win.
# Order: cwd in roots, parse, deny regex, command-level rules, path tokens.
# Every refusal returns reason "code: text". Static analysis is best effort;
# the limited OS account is the hard boundary (docs\LIMITED_ACCOUNT.md).

function New-Refusal {
    param([string]$Code, [string]$Text)
    return @{ ok = $false; reason = ($Code + ': ' + $Text) }
}

function Test-InRoots {
    param([string]$Full, $Roots)
    $fullN = $Full.TrimEnd('\')
    foreach ($r in $Roots) {
        $rf = [IO.Path]::GetFullPath([string]$r).TrimEnd('\')
        if ($fullN.Equals($rf, [StringComparison]::OrdinalIgnoreCase) -or
            $fullN.StartsWith($rf + '\', [StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}

function Test-PathLike {
    param([string]$v)
    if ($v -match '^[A-Za-z]:[\\/]') { return $true }
    if ($v -match '^\\\\') { return $true }
    if ($v -match '^\\[^\\/\s]') { return $true }
    if ($v -match '^/[^/\s]*[\\/]') { return $true }
    if ($v -match '(^|[\\/])\.\.([\\/]|$)') { return $true }
    if ($v -match '^~([\\/]|$)') { return $true }
    if ($v -match '%[A-Za-z_]+%') { return $true }
    return $false
}

function Get-CmdBaseName {
    param([string]$n)
    $b = [IO.Path]::GetFileName(($n -replace '/', '\'))
    if ($b -match '\.(exe|cmd|bat|com)$') { $b = $b.Substring(0, $b.LastIndexOf('.')) }
    return $b
}

function Test-Allowed {
    param([string]$Cmd, [string]$Cwd, $pol, [bool]$Auto = $false, [bool]$Write = $false)
    $cmdT = $Cmd.Trim()
    if (-not $cmdT) { return (New-Refusal 'empty_command' 'no command given') }

    # 1. cwd must be inside a root
    if (-not $Cwd) { return (New-Refusal 'cwd_required' "no cwd given; send cwd inside an allowed root ($(($pol.roots) -join ', '))") }
    try { $cwdF = [IO.Path]::GetFullPath($Cwd) } catch { return (New-Refusal 'bad_cwd' "cwd '$Cwd' is not a valid path") }
    if (-not (Test-InRoots $cwdF $pol.roots)) {
        return (New-Refusal 'cwd_outside_roots' "cwd '$cwdF' is not inside an allowed root ($(($pol.roots) -join ', '))")
    }

    # OPEN MODE (policy.mode = open): read/write/delete anywhere under the roots on a manual click.
    # Only secrets/keys/HALT denies remain. Auto-run (no click) may not write or delete.
    if ([string]$pol.mode -eq 'open') {
        foreach ($d in $pol.deny_path_regex) {
            $m = [regex]::Match($cmdT, [string]$d.re, 'IgnoreCase')
            if ($m.Success) { return (New-Refusal 'denied_path' "$($d.why) - command text matches '$($m.Value.Trim())'. Never allowed through the bridge") }
        }
        $m = [regex]::Match($cwdF, [string]$pol.deny_path_regex[0].re, 'IgnoreCase')
        if ($m.Success) { return (New-Refusal 'denied_path' "cwd '$cwdF' is inside a secrets directory") }
        if ($Auto) {
            # v0.7.0 fluent auto-run: a pure function of (command text, policy). The UI write checkbox no longer
            # changes the verdict, so identical commands always get the identical answer. Only the narrow
            # auto_confirm_regex (irreversible forms) needs a manual click; empty it in policy.json to remove that too.
            if ([string]$pol.auto_mode -eq 'fluent') {
                if ($pol.auto_confirm_regex) {
                    $cm = [regex]::Match($cmdT, [string]$pol.auto_confirm_regex)
                    if ($cm.Success) {
                        return (New-Refusal 'manual_click_required' "irreversible form '$($cm.Value.Trim())' is never auto-run; click the Run button under the block (it is labelled 'Run (click needed)')")
                    }
                }
                return @{ ok = $true; reason = 'auto_fluent' }
            }
            if ($pol.auto_write_regex -and ($cmdT -match [string]$pol.auto_write_regex)) {
                if ($Write) { return @{ ok = $true; reason = 'write_allowed_by_ui' } }
                return (New-Refusal 'manual_click_required' 'this command writes, deletes, moves or runs a program; auto-run only does read-only commands. Click Run on the block yourself')
            }
        }
        return @{ ok = $true; reason = 'ok' }
    }

    # 2. parse
    $tokens = $null; $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseInput($cmdT, [ref]$tokens, [ref]$errors)
    if ($errors -and $errors.Count -gt 0) {
        return (New-Refusal 'parse_error' "command does not parse: $($errors[0].Message)")
    }

    # 3. deny regexes over full text (secrets, keys, HALT)
    foreach ($d in $pol.deny_path_regex) {
        $m = [regex]::Match($cmdT, [string]$d.re, 'IgnoreCase')
        if ($m.Success) {
            return (New-Refusal 'denied_path' "$($d.why) - command text matches '$($m.Value.Trim())'. Access to $($d.why) is never allowed through the bridge")
        }
    }
    $m = [regex]::Match($cwdF, [string]$pol.deny_path_regex[0].re, 'IgnoreCase')
    if ($m.Success) { return (New-Refusal 'denied_path' "cwd '$cwdF' is inside a secrets directory") }
    if ($cmdT -match $pol.kill_regex) {
        return (New-Refusal 'kill_denied' "process termination calls (.Kill(), Terminate()) are refused; the only permitted route is scripts\core\stop-day.ps1 or scripts\core\mode.ps1")
    }
    if ($cmdT -match '\[\s*(System\.)?(Diagnostics\.Process|Reflection\.[A-Za-z]+|Runtime\.InteropServices\.Marshal)\s*\]') {
        return (New-Refusal 'dynamic_denied' 'direct .NET process/reflection/interop calls are refused because they bypass the path checks')
    }

    # 4. command-level rules
    $cmds = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.CommandAst] }, $true)
    $killSet = @{}; foreach ($k in $pol.kill_verbs) { $killSet[([string]$k).ToLower()] = $true }
    $dynSet  = @{}; foreach ($k in $pol.refuse_dynamic) { $dynSet[([string]$k).ToLower()] = $true }
    $dynSet['start-process'] = $true; $dynSet['saps'] = $true; $dynSet['start'] = $true
    $shellSet = @{}; foreach ($k in $pol.nested_shells) { $shellSet[(Get-CmdBaseName ([string]$k)).ToLower()] = $true }
    $readSet = @{}; foreach ($k in $pol.git_read_verbs) { $readSet[([string]$k).ToLower()] = $true }
    foreach ($k in 'set-location','cd','push-location','pop-location','sl','pushd','popd','ls','dir','gci','cat','gc','type') { $readSet[$k] = $true }

    $gitTouch = ($cmdT -match $pol.git_internals_regex) -or ($cwdF -match $pol.git_internals_regex)
    $hasRedir = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.RedirectionAst] }, $true).Count -gt 0

    foreach ($c in $cmds) {
        $name = $c.GetCommandName()
        if (-not $name) {
            return (New-Refusal 'dynamic_command' "command name is computed at run time ('$($c.CommandElements[0].Extent.Text)'); write the command name literally so it can be checked")
        }
        $base = Get-CmdBaseName $name
        $bl = $base.ToLower()
        if ($killSet.ContainsKey($bl)) {
            return (New-Refusal 'kill_denied' "'$base' is refused; killing or stopping processes is only permitted through scripts\core\stop-day.ps1 or scripts\core\mode.ps1")
        }
        if ($dynSet.ContainsKey($bl)) {
            return (New-Refusal 'dynamic_denied' "'$base' is refused because it hides what will run from the path checks; call the script or program directly")
        }
        $isShell = $shellSet.ContainsKey($bl)
        if ($isShell) {
            if ($bl -notin 'powershell','pwsh') {
                return (New-Refusal 'nested_shell_denied' "'$base' is refused; use PowerShell directly")
            }
            $hasFile = $false; $skip = $false
            for ($i = 1; $i -lt $c.CommandElements.Count; $i++) {
                $t = $c.CommandElements[$i].Extent.Text
                if ($skip) { $skip = $false; continue }
                if ($hasFile) { break }
                if ($t -match '^-(f|fi|fil|file)$') { $hasFile = $true }
                elseif ($t -match '^-(c|co|com|comm|comma|comman|command|e|ec|en|enc|encodedcommand)$') {
                    return (New-Refusal 'nested_shell_denied' "'$base $t' is refused; only '$base -File <script inside a root>' is allowed")
                }
                elseif ($t -match '^-(ExecutionPolicy|ep|WindowStyle|w|WorkingDirectory|wd)$') { $skip = $true }
                elseif ($t -match '^-(NoProfile|NonInteractive|NoLogo|NoExit|Bypass)$') { }
                else { return (New-Refusal 'nested_shell_denied' "'$base $t' is refused; use '$base [-NoProfile] -File <script inside a root> [args]'") }
            }
            if (-not $hasFile) { return (New-Refusal 'nested_shell_denied' "'$base' without -File is refused") }
        }
        foreach ($el in $c.CommandElements) {
            if ($el.Extent.Text -match '^-(e|ec|en|enc|encodedcommand)$' -and -not $isShell) {
                return (New-Refusal 'encoded_flag' "encoded command flag '$($el.Extent.Text)' is refused")
            }
        }
        if ($gitTouch -and -not $readSet.ContainsKey($bl)) {
            return (New-Refusal 'git_internals_write' ".git internals may be read but not written; '$base' is not a read-only command and the command (or cwd) touches .git")
        }
    }
    if ($gitTouch -and $hasRedir) {
        return (New-Refusal 'git_internals_write' 'output redirection is refused in a command that touches .git internals')
    }

    # 5. path-like tokens must lie inside a root
    foreach ($t in $tokens) {
        $k = [string]$t.Kind
        if ($k -eq 'Variable' -or $k -eq 'SplattedVariable') {
            if ([string]$t.Text -match '^[$@]\{?(env:|HOME\b|PROFILE\b|PSHOME\b|env\b|variable:|function:|alias:|cert:|HK[A-Za-z]+:)') {
                return (New-Refusal 'variable_path_denied' "variable $($t.Text) is refused; environment and profile paths cannot be checked statically")
            }
            continue
        }
        if ($k -notin 'StringLiteral','StringExpandable','Generic','HereStringLiteral','HereStringExpandable','Identifier') { continue }
        $v = [string]$t.Value
        if (-not $v) { $v = [string]$t.Text }
        if ($v -match '^(env|variable|function|alias|cert|HKLM|HKCU|HKCR|wsman):') {
            return (New-Refusal 'provider_denied' "provider path '$v' is refused")
        }
        if ($k -eq 'StringExpandable' -and $t.Text -match '\$(env:|\{env:|HOME|PROFILE|PSHOME)') {
            return (New-Refusal 'variable_path_denied' "expandable string '$($t.Text)' uses an environment or profile variable and cannot be checked")
        }
        if ($v.Contains("`n")) { continue }
        if (Test-PathLike $v) {
            if ($v -match '%[A-Za-z_]+%') { return (New-Refusal 'variable_path_denied' "'$v' uses an environment variable and cannot be checked") }
            try {
                if ($v -match '^[A-Za-z]:[\\/]|^\\\\|^[\\/]') { $full = [IO.Path]::GetFullPath($v) }
                else { $full = [IO.Path]::GetFullPath((Join-Path $cwdF $v)) }
            } catch { return (New-Refusal 'bad_path' "'$v' is not a valid path") }
            if (-not (Test-InRoots $full $pol.roots)) {
                return (New-Refusal 'path_outside_roots' "'$v' resolves to '$full', which is not inside an allowed root ($(($pol.roots) -join ', '))")
            }
        }
    }
    return @{ ok = $true; reason = 'ok' }
}


function Get-CmdKind {
    # information only (never decides): read | write | program. Lets a refusal and a receipt say WHICH kind it was.
    param([string]$Cmd, $pol)
    $w = [string]$pol.kind_write_regex
    $r = [string]$pol.kind_program_regex
    if (-not $w) { $w = '(?i)(\b(Remove-Item|ri|rm|rmdir|del|erase|rd|Set-Content|sc|Add-Content|ac|Out-File|New-Item|ni|Move-Item|mv|mi|move|Copy-Item|cp|copy|cpi|Rename-Item|rni|ren|Clear-Content|Set-Item)\b|git\s+(add|commit|push|reset|checkout|clean|rm|mv|merge|rebase|stash|restore|apply|cherry-pick|revert|tag|branch)\b|\[IO\.File\]::(Write|Delete|Move|Copy|Append)|[^-]>{1,2}\s*(?!\$null\b)(?!nul\b)[^\s&])' }
    if (-not $r) { $r = '(?i)\b(python|py|node|npm|mvn|pip|pytest|java|powershell|pwsh|cmd|bash|Start-Process|saps|Invoke-Expression|iex)\b|\.(ps1|exe|bat|cmd|py)\b' }
    if ($Cmd -match $w) { return 'write' }
    if ($Cmd -match $r) { return 'program' }
    return 'read'
}

function Test-Ps5Lint {
    # The shell is Windows PowerShell 5.1 (powershell.exe). PS7-only syntax makes the whole script fail to parse,
    # so no line runs. Say so BEFORE running, with the fix. Strings and comments are blanked first.
    param([string]$Cmd)
    $tokens = $null; $errors = $null
    try { [void][System.Management.Automation.Language.Parser]::ParseInput($Cmd, [ref]$tokens, [ref]$errors) } catch { return @{ ok = $true; reason = 'ok' } }
    $chars = $Cmd.ToCharArray()
    foreach ($t in $tokens) {
        $k = [string]$t.Kind
        if ($k -in 'StringLiteral', 'StringExpandable', 'HereStringLiteral', 'HereStringExpandable', 'Comment') {
            for ($i = $t.Extent.StartOffset; $i -lt $t.Extent.EndOffset -and $i -lt $chars.Length; $i++) { if ($chars[$i] -ne "`n") { $chars[$i] = ' ' } }
        }
    }
    $code = -join $chars
    $hits = @(
        @{ re = '&&'; what = '&& (pipeline chain)'; fix = 'use ; or: cmd1; if ($?) { cmd2 }' },
        @{ re = '\|\|'; what = '|| (pipeline chain)'; fix = 'use: cmd1; if (-not $?) { cmd2 }' },
        @{ re = '\?\?'; what = '?? / ??= (null coalescing)'; fix = 'use: if ($null -eq $x) { ... }' },
        @{ re = '\?\.[A-Za-z_]|\?\['; what = '?. / ?[] (null conditional)'; fix = 'test for $null first' },
        @{ re = '(?i)\s-(AsHashtable|Parallel|AsByteStream|SkipHttpErrorCheck|ThrottleLimit)\b'; what = 'a PowerShell 7 only parameter'; fix = 'drop it, or' }
    )
    foreach ($h in $hits) {
        $m = [regex]::Match($code, $h.re)
        if ($m.Success) {
            return (New-Refusal 'ps7_only' "this host runs Windows PowerShell 5.1 (powershell.exe); $($h.what) is PowerShell 7 only, so the whole block would fail to parse and nothing would run. Fix: $($h.fix). Or put shell=pwsh on the AIRUN line to run the block in PowerShell 7")
        }
    }
    if ($Cmd -match '(?i)-Encoding\s+(utf8NoBOM|utf8BOM)\b') {
        return (New-Refusal 'ps7_only' "this host runs Windows PowerShell 5.1; -Encoding utf8NoBOM/utf8BOM do not exist there. Use [IO.File]::WriteAllText(path, text, (New-Object Text.UTF8Encoding(`$false))) or put shell=pwsh on the AIRUN line")
    }
    return @{ ok = $true; reason = 'ok' }
}
