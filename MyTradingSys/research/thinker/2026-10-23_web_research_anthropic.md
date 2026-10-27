# Anthropic official docs: coordinator / hooks / worktree research (2026-10-23)

Sources are official Claude Code docs, now hosted at code.claude.com/docs/en (docs.claude.com 301-redirects there). Pages show no per-page date; all were fetched 2026-10-23 and are the live 2026 versions. CHANGELOG (anthropics/claude-code, main) newest entry fetched: 2.1.309. Docs are quoted; anything not found is NOT_DOCUMENTED.

## Summary table

| # | Question | Documented answer | Fix for us | Source (fetched 2026-10-23) |
|---|---|---|---|---|
| 1 | Pre-approve start_session card | Generic MCP allow syntax is documented. Nothing documents the `mcp__ccd_*` app tools or a start_session approval card (NOT_DOCUMENTED). Bypass mode still prompts for "actions no mode auto-approves" and some "desktop actions". | Add `mcp__ccd_session__start_session` (or `mcp__ccd_session__*`) to `permissions.allow` in USER settings; test once. If the card persists it is an app-level card: use `bypassPermissions` or Auto mode for the coordinator, else treat as unfixable by config. | permissions, permission-modes, desktop |
| 2 | Which settings win in a worktree | Desktop worktree session reads settings, hooks, skills, agents, commands, .mcp.json from the MAIN checkout root. CLAUDE.md and .claude/rules still load from the worktree. Precedence: managed > CLI `--settings` > project local > shared project > user. | Edit hooks/settings in the MAIN checkout (and merge to it), not in the worktree. Use hook `cwd` for the worktree path. | worktrees, settings |
| 3 | Background subagents | Run concurrently; permission prompts surface in main session. Resume/message with SendMessage. Per-agent `model`. Subagents may spawn subagents (3 layers). 20 concurrent cap. Spawning sessions: NOT_DOCUMENTED. | Use Agent with `model` set; resume via SendMessage; raise `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` if needed. Do not rely on subagents to call start_session. | sub-agents |
| 4 | Hooks pitfalls | Exit 2 blocks; exit 1 does NOT block. PreToolUse `allow` skips the prompt but never overrides deny/ask rules. Stop hook: check `stop_hook_active`; cap of 8 consecutive blocks. Timeouts: 600s command, 30s UserPromptSubmit. | See "Q4" below: a PreToolUse hook CAN auto-approve an MCP tool (if no ask/deny rule matches). Keep UserPromptSubmit hooks fast; normalise Windows backslashes. | hooks, permissions |
| 5 | Auto-compaction, long coordinators | Auto-compacts near limit; background subagents keep running; SessionStart with source `compact` re-injects context; `/autocompact <n>` sets the threshold; idle compaction at ~54 min for >200K. | Put coordinator rules in CLAUDE.md (re-read from disk) and a SessionStart `compact` hook; keep reads in subagents; hand over at task end, not at compaction. | context-window, changelog 2.1.299 |
| 6 | Wake an idle session | Yes: cross-session messaging (SendMessage/ListAgents), idle session starts a new turn with the message. Receiving-session rules (`crossSessionInbound`) can hold it; Desktop cannot show the approval dialog. | Set `crossSessionInbound: "accept"` in USER settings of worker sessions. Do NOT use bypassPermissions on the receiver unless the sender also bypasses, or messages are held. | cross-session-messaging, permission-modes |
| 7 | Model per session | `/model`, `--model`, `ANTHROPIC_MODEL`, settings `model`; aliases sonnet/opus/haiku/fable; subagent `model` field. No documented tool-level "set model of another session" (the app tool is NOT_DOCUMENTED). | Use `--settings '{"model":"claude-opus-5-5"}'` or app set_session_model; verify with read-back as already in memory. | model-config, sub-agents |

## Q1. Pre-approving start_session

Official, MCP rule syntax (permissions page):
- "`mcp__puppeteer` matches any tool provided by the `puppeteer` server"
- "`mcp__puppeteer__*` uses wildcard syntax and also matches all tools from the `puppeteer` server"
- "`mcp__puppeteer__puppeteer_navigate` matches the `puppeteer_navigate` tool"
- "To match a parameter on an MCP tool, pass a deny rule with `--disallowedTools`. ... it skips any `mcp__` rule that has parentheses." (no `mcp__x(arg)` allow rules)
- Changelog 2.1.300: "MCP allow rules reach only the server they name. `mcp__a` no longer allows a server named `a__b`. Use `mcp__<server>__*`."
- Allow globs only after a literal `mcp__<server>__` prefix; `"mcp__*"` "is skipped and doesn't auto-approve anything".

So the exact entries for us are: `mcp__ccd_session__start_session` or `mcp__ccd_session__*`.

Where it applies: "`permissions.allow` rules ... apply only after each teammate trusts the folder" (project file needs workspace trust). `.claude/settings.local.json` allow rules apply without the trust step. User settings (`~/.claude/settings.json`) apply everywhere.

Permission modes (permission-modes page):
- `acceptEdits`: "Reads, file edits, and common filesystem commands" - does not include MCP.
- `auto`: "Everything, with background safety checks" (a classifier, default Sonnet 5, reviews actions).
- `bypassPermissions`: "Everything", but "Claude Code doesn't auto-approve the following in any mode, including `bypassPermissions`: tools matched by an explicit ask rule; connector tools your organization set to ask; tools that require user interaction (`AskUserQuestion`, MCP tools marked `requiresUserInteraction`); ... the cross-session messaging safeguards".
- Desktop page: Bypass runs "without permission prompts, except for the actions no mode auto-approves, safety classifiers when Claude acts on external sites, or desktop actions such as deleting a session, though not archiving one." Bypass in Desktop "requires the Allow bypass permissions mode toggle in Desktop settings on Pro and Max plans".
- `defaultMode`: "The desktop app reads the same settings files as the CLI and applies the permission mode to new local sessions." "A mode you pick in the mode selector is remembered per folder and takes precedence over defaultMode for that folder." Settings page: `defaultMode` values `auto` and `bypassPermissions` "don't take effect from project or local settings; set them in user or managed settings" (or `--permission-mode`).
- Managed settings: `permissions.disableBypassPermissionsMode` / `disableAutoMode` can lock these off. Managed is the top of precedence; nothing in user/project overrides it.

NOT_DOCUMENTED: the `mcp__ccd_session__*` / `mcp__ccd_*` tools themselves, a start_session approval card, and whether app-provided tools honour `permissions.allow`. The desktop page documents a "suggested task" card (Start / Start all / Do it here) and an archive approval card ("except in Auto mode and Bypass permissions mode"), but no card for a tool-initiated start. Hypothesis (not documented): the card is the app's own suggested-task UI, which a settings rule cannot suppress.

Fix: (1) add the allow rule to USER settings, restart the session, call start_session once; (2) if the card still shows, set the coordinator to Auto or Bypass via the desktop mode selector (Bypass needs the Desktop toggle) and re-test; (3) if still shown, it is app UI: stop trying config, record NOT_DOCUMENTED and use `claude --bg` / agent view as the documented non-card way to start sessions.

Documented alternative that avoids the card: `claude --bg --name "x" --model sonnet "prompt"` (agent-view page) starts a background session; `claude agents --permission-mode plan --model opus --effort high` sets dispatch defaults.

## Q2. Settings in a git worktree

Quote (worktrees page, "What worktrees share with the main checkout"): "In a worktree session you start from the desktop app, Claude Code reads project configuration such as settings, hooks, skills, agents, commands, and `.mcp.json` servers from the main checkout's root. Hook commands run in that root, and `${CLAUDE_PROJECT_DIR}` points at it. To reach the files Claude is working on, read the worktree's path from the hook's `cwd` input field. `CLAUDE.md` files and `.claude/rules/` still load from the worktree."

Also: "Permission approvals: choosing 'Yes, and don't ask again' ... saves the rule to the main checkout's `.claude/settings.local.json` ... On Windows ... the rule stays with that worktree" (v2.1.211+). Settings page says the same: "In a worktree, it uses the file at the main checkout's root", and for Windows/home-dir roots "the file stays with `.claude/settings.json` instead".

Precedence (settings page), highest first: managed; command line (`--settings`); project local (`.claude/settings.local.json`); shared project (`.claude/settings.json`); user (`~/.claude/settings.json`). "Lists merge instead of overriding" (`permissions.allow` is combined across files). Edits reload live ("Claude Code watches your settings files and reloads them"), incl. `hooks` and `permissions`.

Implication: a hook change committed on a worktree branch does NOT take effect in that desktop worktree session; it takes effect when the MAIN checkout's file changes. This matches our memory note "hooks come from main checkout". Hook scripts referenced via `${CLAUDE_PROJECT_DIR}` run the MAIN checkout's copy.

## Q3. Background subagents (sub-agents page)

- Background: "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." Changelog 2.1.302: "The desktop app and VS Code now run the main conversation's subagents in the background."
- Permissions: "Background subagents surface every permission prompt in your main session." A broad answer "applies to the whole session". Background subagents have "a smaller built-in tool set".
- Resume/message: "Claude uses the `SendMessage` tool with the agent's ID or name as the `to` field to resume it." Resumed agents "retain their full conversation history". Explore and Plan are one-shot: "Claude can't resume them. Use general-purpose or a custom subagent."
- Interactive: no. Only the summary returns to the parent; a subagent that launches background subagents waits for their results.
- Model: alias `sonnet|opus|haiku|fable`, full ID, or `inherit`. Order: per-invocation `model` param, then definition frontmatter, then `CLAUDE_CODE_SUBAGENT_MODEL`, then main model.
- Nesting: "a subagent can spawn subagents of its own, up to three layers"; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` turns it off.
- Limits: "when 20 subagents are running ... spawning another fails with `Concurrent subagent limit reached`"; no total cap; `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` raises it.
- Subagents starting app sessions (start_session): NOT_DOCUMENTED. Subagent tool inheritance for MCP tools is not stated in the fetched text.
- Worktree subagents: `isolation: worktree` frontmatter; such a subagent does not load the worktree's CLAUDE.md.

Fix: give each Agent call an explicit `model` (haiku for mechanical, sonnet default); resume with SendMessage rather than respawn; keep session-spawning in the coordinator itself.

## Q4. Hooks (hooks + permissions pages)

- Exit codes: "Success: exits 0 ... Blocking: exits 2 ... any other code ... The action goes ahead." "Exit code 1 without valid JSON output is a non-blocking error ... If your hook is meant to enforce a policy, use `exit 2`." Exit 2 beats JSON: "Even a `permissionDecision` of `allow` doesn't let the action through."
- PreToolUse JSON: `hookSpecificOutput.permissionDecision` = `allow` | `deny` | `ask` | `defer` (defer only with `-p`), plus `permissionDecisionReason`, `updatedInput`, `additionalContext`. Quote: "`allow` skips the permission prompt, except for actions no mode auto-approves and reads from network paths." Multiple hooks: "deny > defer > ask > allow". "Exit code 0 with no output ... staying silent doesn't approve it."
- Can a hook auto-approve an MCP call? Yes in principle: PreToolUse matches `mcp__<server>__<tool>`; "`allow` skips the permission prompt". Limits: "PreToolUse hook decisions don't bypass permission rules ... a matching deny rule blocks the call, and a matching ask rule still prompts even when the hook returned allow." MCP tools marked `_meta["anthropic/requiresUserInteraction"]` cannot be skipped. Whether an APP-provided tool's own card (Q1) is reachable by a hook: NOT_DOCUMENTED. Note permissions page also lists: "PreToolUse hooks: a hook that returns allow doesn't skip the prompt" for one case (reads outside working dirs / network paths); and the hooks page says "use the permission system rather than a hook to enforce a hard allow or deny" (the `if` filter is best-effort).
- MCP matcher: "append `.*` ... `mcp__memory__.*`. ... a matcher like `mcp__memory` ... matches no tool." (hooks matcher needs `.*`; permission rules use `mcp__server__*`; do not mix.)
- Stop hooks: `decision: "block"` + `reason` keeps Claude going. "`stop_hook_active` is true when Claude Code is already continuing as a result of a stop hook. Check this value ... to avoid blocking on a condition that will never resolve." Safety cap: "after stop hooks have continued the turn eight times in a row, Claude Code overrides the next block and ends the turn ... `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`."
- Timeouts: "Defaults: 600 for command, http, mcp_tool; 30 for prompt; 60 for agent." Lowered to 30 on `UserPromptSubmit`; "a stuck hook stalls the session". Timed-out command hooks are cancelled and output discarded. Matching hooks "run in parallel"; the same handler in two settings files "runs once".
- Output injection: SessionStart/UserPromptSubmit plain stdout becomes context Claude sees. SessionStart `source` = startup | resume | clear | compact | fork.
- Windows pitfalls: "file paths arrive with backslashes ... A comparison written with forward slashes ... never matches ... the tool call proceeds as if the hook had nothing to block." Normalise separators. Changelog 2.1.309: "Hooks that run in PowerShell now block when they exit with code 2. On Windows, some PreToolUse and PermissionRequest hooks no longer fail open when Git for Windows is missing." (Fail-open risk: our hooks should be tested on Windows.)
- Worktree: `${CLAUDE_PROJECT_DIR}` stays at project root; hook input `cwd` follows the worktree.
- Performance: keep UserPromptSubmit and MessageDisplay hooks fast; hooks run in parallel, so no ordering dependence.

Fix for us: never rely on exit 1 to block; return JSON deny or exit 2; guard Stop hooks with `stop_hook_active`; set explicit `timeout` on every hook; backslash-normalise paths in PreToolUse; do not use a hook as the only guard for something an ask/deny rule could also hit.

## Q5. Compaction (context-window page, how-claude-code-works)

- "Claude Code compacts automatically as you approach the limit, so a full context window doesn't end your session."
- Survives: system prompt, project-root CLAUDE.md and unscoped rules ("Re-injected from disk"), auto memory, plan-mode plan, up to five recent files; "Background commands and background subagents: Keep running. Claude Code reminds Claude which ones are still running"; "SessionStart hooks that match the `compact` source: Claude Code runs them and adds their output".
- Does not survive: "Context that hooks added earlier: Summarized with the rest of the conversation"; path-scoped rules and nested CLAUDE.md "compaction summarizes them away".
- Controls: `/compact focus on ...`; `/autocompact 500k` ("how full the context window gets before the automatic pass runs"); `/clear` between tasks; "Delegate large reads: send research to a subagent"; `[1m]` model variants; idle compaction (changelog 2.1.299: ">200K tokens left idle for about 54 minutes", terminal).
- Known issues fixed (changelog 2.1.306 to 2.1.309): repeated compaction/thrash with many MCP tools or huge nested CLAUDE.md. Keep CLAUDE.md small.

No official "coordinator" guidance on very long sessions beyond the above. Fix: coordinator rules live in CLAUDE.md or a SessionStart `matcher: compact` hook, not in chat; offload reads to subagents; run `/autocompact` lower for coordinators; state is on disk (STATUS.md), which matches our boot design.

## Q6. Waking an idle session (cross-session-messaging page)

- "Cross-session messaging lets Claude deliver a message from one of your Claude Code sessions to another." Requires v2.1.224+ (macOS/Linux), "On native Windows, it requires Claude Code v2.1.234 or later." On by default.
- "When the receiving session is idle, Claude Code starts a new turn with the message." Active turns read it "between tool calls".
- Claude uses `ListAgents` and `SendMessage` ("you never call either tool yourself"). Same-machine transport is a per-session named pipe on Windows; never via Anthropic servers. `SendMessage` also takes `notify_when_idle` (v2.1.236+) for a one-time idle/exit notice (12 h expiry; main conversation to own local sessions only).
- Receiver controls: `crossSessionInbound` = `accept` | `hold` | `refuse`. With no value set: a receiver that prompts for permissions gets messages delivered unless the sender bypasses; "The receiving session bypasses permission prompts: Claude Code holds each message for your approval. It delivers one only when the sending session identifies itself as also bypassing."
- Desktop gotcha: "A session in the VS Code extension or the Desktop app can't show the dialog. Claude Code keeps a held message there until the same deadline [`dialogExpiry`, default five minutes]" then drops it. So a held message to a Desktop session is silently lost after 5 min.
- Message limits: cannot approve anything, cannot change config, commands like `/compact` arrive as plain text; max ~1M chars; bursts throttled; queue 50; identical repeats dropped.
- Outside Claude's own tools: a hook or script can post to the session socket (`CLAUDE_CODE_MESSAGING_SOCKET`, token `CLAUDE_CODE_MESSAGING_TOKEN`, Windows needs the auth line). Agent view: reply to an idle background session; "the next time you attach or reply, the session resumes"; unattended ~1 h sessions are stopped and restarted on reply.
- Our app tool `mcp__ccd_session_mgmt__send_message`: NOT_DOCUMENTED.

Fix: put `"crossSessionInbound": "accept"` in USER settings (or worker `--settings`), keep workers NOT in bypass mode (or both in bypass), and use `notify_when_idle` instead of polling. Do not assume a `/command` in a message runs.

## Q7. Model selection (model-config, sub-agents, agent-view)

- Aliases: `fable` (hardest, longest tasks), `sonnet` ("daily coding tasks"), `opus` ("complex reasoning tasks"), `haiku` ("simple tasks"), `opusplan` (opus in plan mode, sonnet to execute), `[1m]` variants.
- Set per session: `/model <alias|name>` (Enter saves as default; `s` = this session only), `claude --model`, `ANTHROPIC_MODEL`, settings `model`, `ANTHROPIC_DEFAULT_MODEL`. One-off: `claude --settings '{"model": "claude-opus-5-5"}'` (settings page). Settings precedence: a project `model` is overridden by `.claude/settings.local.json`.
- Switching mid-session: "Each model has its own prompt cache, so the first request after a switch re-reads the whole conversation uncached."
- Background sessions: `claude --bg --model ...`; "Each background session can run on a different model"; permission mode, model, effort persist across supervisor restarts.
- Effort: `low|medium|high|xhigh|max`; defaults `medium` on Opus 5.5 / Sonnet 5.5 / Haiku 5.5; `max` "prone to overthinking".
- Task-to-model guidance: the page defers to claude.com/blog/claude-model-and-effort-level-in-claude-code (not fetched). Own table: NOT_DOCUMENTED beyond the one-line alias descriptions above.
- Setting another session's model through the app tool (`set_session_model`): NOT_DOCUMENTED; the settings key `model` and `--model` are the documented routes. Settings page warns a managed `model` is a default and `availableModels` is the lock.

## Source URLs (all fetched 2026-10-23, no per-page dates; version context CHANGELOG 2.1.309)
- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/permission-modes
- https://code.claude.com/docs/en/settings
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/worktrees
- https://code.claude.com/docs/en/desktop
- https://code.claude.com/docs/en/cross-session-messaging
- https://code.claude.com/docs/en/agent-view
- https://code.claude.com/docs/en/model-config
- https://code.claude.com/docs/en/context-window
- https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md

## Gaps (not fetched or NOT_DOCUMENTED)
- App tools `mcp__ccd_session__*`, `mcp__ccd_session_mgmt__*`: no official page found (searched code.claude.com, docs.claude.com, support pages).
- Hooks page chars 200000+ (end of hooks reference), settings-reference `defaultMode`/`crossSessionInbound` entries, hooks-guide, and the claude.com model/effort blog were not read.
- No support.anthropic.com or engineering-blog material was used.
