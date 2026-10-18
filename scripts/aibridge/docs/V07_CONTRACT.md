# AIBridge v0.7.0 contract (what the bridge really does)

Source of truth for DSA_SESSION_PROMPT. Payload: MTS repo `scripts/aibridge/`, installer `scripts/dev/aibridge_install.py`.
Tests: `python tests/agent_live_selftest.py` (36 live checks) and `node tests/loop.test.js`.

## Block format
```
# AIRUN cwd=<dir> timeout=<s> [host=NUC] [shell=pwsh]
<any number of command lines>
```
- Every line of the block runs (the block text is read with line breaks intact; the agent reports `lines=N` back so a lost line is visible).
- A reply may carry several AIRUN blocks. They run IN ORDER, up to 6 per reply (`aibridge_max_blocks`), and ONE message returns
  with a receipt per block, headed `[AIRUN BATCH] blocks_seen=N blocks_run=M not_run=K`.
  A block that is not run still gets a receipt that says why: `NOT RUN: over the per-reply cap` or
  `NOT RUN: block 2 ended with exit 1 and this block may depend on it`. After a refusal, error, timeout, or a non-zero exit of a
  non-read command, the remaining blocks of the reply are skipped (read-only commands may exit non-zero without stopping the batch).
- Result numbers `#n` are monotonic per chat page (each page keeps its own counter). Each result header carries
  `host= agent= kind=read|write|program|task lines= sha= rid=` plus `ran_at:` and the whole command (first 600 chars, lines joined with ` ; `).
  The extension discards any answer whose `rid` is not the one it asked for (`STALE_REPLY`).

## Task mode (end to end in one call)
```
# AIRUN task=mts-boot hours=48
```
runs the playbook `tasks\mts-boot.json` (steps, params, capture, expect, on_fail=stop|continue|retry:N) and returns ONE report:
per step PASS/FAIL/SKIP with seconds and the tail lines (25 lines for a failed step), `TASK RESULT: PASS|FAIL at step N`, full log path.
- `# AIRUN task=list` lists the playbooks and their parameters. Shipped: mts-boot, mts-gate, mts-ship, build-check.
- `# AIRUN task=inline` with a JSON plan in the body: `{"steps":[{"name":"a","cmd":"...","cwd":"...","timeout_s":120,"on_fail":"stop","expect":"regex","capture":{"var":"regex with one group"},"show":3}]}`.
  `{var}` / `{param}` placeholders are filled from params and captures. Every inline step is screened like a normal command BEFORE anything runs.
- Task timeout: default 600 s, hard cap 1800 s (`timeout=` on the AIRUN line). Normal blocks: default 60, hard cap 300.

## Auto-run (hands-free)
Per COMMAND TEXT and deterministic (the same text always gets the same answer; no UI checkbox changes it).
Everything the path rules allow runs without a click: python (scripts/dev, scripts/sched, `-m pytest`), git read AND write verbs
(add, commit, checkout, merge, push without force ...), mvn, pip, node, redirects, Set-Content, Remove-Item of single files.
Needs a manual click (Run button labelled `Run (click needed: manual_click_required)`):
`Remove-Item/rm/del/rd -Recurse|-Force`, `rm -rf`, `rmdir /s`, `del /s|/f|/q`, `git reset --hard`, `git clean`, `git branch -D`,
`git checkout -- <path>`, `git stash drop|clear`, `git push --force|-f|--force-with-lease|--delete`, `Format-Volume`, `Clear-Disk`,
`Stop-Process`, `taskkill`, `Stop-Service`, `Restart-Service`, `Stop-Computer`, `Restart-Computer`, `shutdown`.
Refusal text: `manual_click_required: irreversible form '<match>' is never auto-run; click the Run button under the block (it is labelled 'Run (click needed)')`.
Edit `auto_confirm_regex` in `src\policy.json` (re-read on every request) to change the list; empty it to remove it.
Never allowed, click or not: `.secrets`, `.env*`, key files, `id_rsa*`, `HALT*` (`denied_path`).
Every refusal and every result names its kind (`read|write|program|task`). The Run button is labelled by a dry run (`dry: true`) of the same check.

## Roots, paths, shell, environment
- Roots: `C:\Users\E-ngineers\IdeaProjects` (all worktrees), `C:\Users\E-ngineers\AppData\Local\Temp`, `F:\AIBridge`, `F:\MTS`. cwd must be inside a root.
- `$env:` and other variables are NOT refused (open mode). Child TEMP/TMP = `<AIBridge>\run\tmp` (no shared pytest-of-<user> lock); `--basetemp` is no longer needed.
- Shell: Windows PowerShell 5.1 (`powershell.exe`). PS7-only syntax (`&&`, `||`, `??`, `?.`, `-AsHashtable`, `-Parallel`, `-Encoding utf8NoBOM` ...)
  is refused BEFORE running with code `ps7_only` and the fix. `shell=pwsh` on the AIRUN line runs the block in PowerShell 7 when the host has pwsh.
- Environment: each command starts with the machine+user environment read from the registry NOW (JAVA_HOME, PATH changes are live, no agent restart).
- First line of every block should still be `Set-Location <dir>` when the operator may run the block by hand: the `# AIRUN` line is a comment to PowerShell.
- `host=NUC` routes through a loopback tunnel only if `aibridge_machines` is configured in the extension storage; not configured by default.

## Parallel chats
- Each chat page has its own state (auto switch, counters, ran-block memory); nothing is shared through chrome.storage.
- Background / unfocused windows keep running: the extension worker pushes a 500 ms tick over a port (page timers are throttled when hidden)
  and the page holds a Web Lock so Chrome does not freeze it. The agent runs up to 8 commands at once, so a slow gate run never blocks another chat.

## Errors are labelled by layer
- `ERROR extension_link` : the extension did not answer (disabled / reloaded; F5 the page).
- `ERROR agent_unreachable` : the extension is alive, nothing listens on the port (start: `scripts\start-agent.ps1`, watchdog: add `-Watch`).
- `GET /ping` (and the control box line on load) shows agent version, host, PowerShell version, running commands.
