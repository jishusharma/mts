# UNATTENDED_PERMISSIONS: no "Allow once" dialog, ever (operator 2026-10-26)

Goal: a session in Bypass never waits on a dialog. Researched 2026-10-26 against code.claude.com docs (permission-modes, permissions, hooks), Claude Code 2.1.293.

## Why a dialog still appears in Bypass
| Cause | Seen / likely | Fix |
|---|---|---|
| App policy: bypass disabled, "block reads outside working directories" ON (GATEWAY_NUC.md rule 3) | NUC, screenshot 3c19a6836b52 | the registry/policy file merged on the NUC (operator's Documents, outside the repo): remove those two keys, reopen the app |
| Explicit `ask` rule in any settings scope | none found on JIS-DESKTOP | `perm_audit.py` |
| Session not in Bypass: Desktop remembers the mode per folder; a new worktree folder starts in the default mode | any new worktree | mode selector once per folder, or the PermissionRequest hook below |
| Tools that need a person: `AskUserQuestion`, MCP tools marked requiresUserInteraction, `rm -rf` of a critical path (2 min countdown, then denied) | by design | briefs never use them; deny list already blocks rm |
| `.claude/settings.json` cannot set `bypassPermissions`/`auto`; only `~/.claude/settings.json` or managed policy can | docs | user-level setting (done) |

Deny rules block in every mode and allow rules do nothing in Bypass, so the deny list is the safety net; do not add `ask` rules.

## The control we own: `scripts/dev/perm_hook.py`
A user-level `PermissionRequest` hook answers any dialog with allow (deny rules still win) and logs tool, mode, 160 chars of detail to `~/.claude/perm_requests.jsonl` (outside the repo). It lives in `~/.claude/`, so a stale checkout or a new worktree cannot drop it.
- Install per machine: `python scripts/dev/perm_hook.py install` (backs up nothing itself; copy settings.json first). Check: `python scripts/dev/perm_hook.py status`.
- Unattended CLI runs: add `--permission-prompts none` (2.1.259+) or `--permission-mode dontAsk` with an allowlist, so a prompt is a denial, never a wait.
- A new dialog that still shows up: read the log tail, add the tool to this table.

## Not controllable from here
Gateway/app policy on a machine (NUC) and the Desktop mode selector. Both are operator-side one-time steps.
