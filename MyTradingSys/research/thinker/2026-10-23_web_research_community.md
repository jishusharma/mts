# Community web research, 2026-10-23 (Claude Code desktop, Windows, coordinator sessions)

Method: WebSearch, then WebFetch of each page listed. Only pages actually opened are cited as read. claudeissues.com mirror
fetches timed out, so issues were re-fetched on github.com. No Reddit/HN thread was reachable via search (results were blogs and
GitHub only), so nothing from Reddit/HN is claimed. "Staff" = Anthropic employee comment; almost every thread had only the
github-actions bot (stale/duplicate/lock). Bot "closed as not planned" means inactivity, NOT a decision.

## Top table

| Problem | Community finding | Working fix | URL + date | Staff confirmed? |
|---|---|---|---|---|
| A. Approval card on start_session | No issue found for start_session or its card. Official docs: the Start card is a button press; the docs list a skipped-card rule only for ARCHIVE (skipped in Auto and Bypass). Nothing on skipping the start card. | None documented. Test: coordinator in Bypass permissions (Settings, Max plan), call start_session once, see if the card disappears. If not, it is by design. | code.claude.com/docs/en/desktop (read 2026-10-23) | Docs only; no statement on start |
| A. MCP/app tools prompt even in bypass/auto | MCP tools flagged requiresUserInteraction are blocked in Bypass (Windows, built-in scheduled-tasks server). MCP allow rules ignored in auto mode. MCP tools prompt under bypass-all (CLI). | Ask mode, click "Always allow" once per tool (sometimes stays after returning to Bypass). Pre-add exact `mcp__server__tool` names to permissions.allow (worked for subagents, #64750). Otherwise none. | github.com/anthropics/claude-code/issues/58757 (2026-05-13), /77688 (2026-07-15), /52698 (2026-04-24), /64750 (2026-06-02) | No staff reply in any |
| A. Desktop approvals only Once / Always | No "allow for session"; Desktop persists to .claude/settings.local.json | Click Always Allow once per tool; allowlist in settings | github.com/anthropics/claude-code/issues/48479 (2026-04-15) | No (bot: dup of #17079) |
| B. Hooks/settings missing or stale in worktrees | Project hooks are branch-local when tracked, absent when .claude/ is gitignored; .worktreeinclude only covers worktrees Claude itself creates. Hooks silently skipped in a linked worktree. $CLAUDE_PROJECT_DIR points at the worktree so helper scripts are missing. | Guard hooks at USER scope with the script copied outside any work tree (claude-multisession approach); manual copy of .claude/helpers into the worktree; session-start check that warns in a linked worktree (bkit plugin). | github.com/anthropics/claude-code/issues/83953 (2026-08-04, OPEN), /46808 (2026-04-11), /36656 (2026-03-20), /36360 (2026-03-19) | No. bcherny only added labels (area:hooks) on 83953 |
| B. Stop hook forces loops | Stop hook returning ok:false loops while a background subagent is pending (about 50 min, quota burned). stop_hook_active stays false on repeat fires when reminders/task notifications interleave. | Hook exits 0 when stop_hook_active is true AND when background work is pending; add a cooldown sentinel (60 s). No harness fix. | github.com/anthropics/claude-code/issues/55754 (2026-05-03), /54360 (2026-04-28) | No |
| B. PreToolUse deny problems | Search shows mostly the reverse: deny/exit 2 ignored, hooks never firing on Windows (v2.1.240, Aug 2026). No genuine "harness wrongly blocks" bug found; false positives were broad regexes in the user's own script. Those pages NOT opened. | Narrow the regex; log every deny with the matched rule; allowlist escape. | claudeissues.com search hits only (unopened): 43407, 88896, 26923 | Unknown |
| C. Background subagent model override lost | Pinned model drops to the session model after SendMessage resume, task-notification wake, or session resume; TUI badge hides it. 470 unintended turns in one night. Several duplicate issues (titles only seen). | Treat resumed pinned agents as suspect; check with `grep -o '"model":"[^"]*"' <task output> , sort, uniq -c`; kill and respawn with explicit model instead of resuming; do not use CLAUDE_CODE_SUBAGENT_MODEL (hard value overrides per-launch pins). | github.com/anthropics/claude-code/issues/75054 (2026-07-07, OPEN, assignee bogini, staff status unclear) | No staff comment |
| C. Subagent vs separate session | Subagents: summaries only, no peer talk, cannot answer permission prompts (silently denied unless pre-allowed). Separate sessions/worktrees: manual merge but independent. Blog consensus: subagents for independent narrow tasks, separate sessions only when coordination is needed (blogs, unopened, unverified numbers). | Narrow scope, return summaries, pre-allow MCP tools in settings for subagents. | github.com/anthropics/claude-code/issues/64750 (2026-06-02) | No |
| D. Compaction loses coordinator state | Claude writes SESSION.md too late; SessionStart(compact) re-read hook is hit-and-miss; PreCompact hook cannot make Claude act. Closed "not planned" by bot. | State on disk written continuously at task boundaries, SessionStart hook with matcher compact re-injecting the file, PreCompact shell script that dumps state itself. Our STATUS.md / NEXT_SESSION.md pattern matches. | github.com/anthropics/claude-code/issues/43733 (2026-04-05) | No |
| E. Wake idle session without a human | `claude -p --resume <id> "msg"` works with the message as an argv positional; piped stdin hung on WSL. Remote Control cannot attach to a finished -p session without spending a turn. Desktop docs: Claude can list/read/message desktop-run local/SSH/WSL sessions; crossSessionInbound=refuse blocks it. | argv prompt, not stdin. For desktop sessions use the in-app send_message (docs "Work across sessions"). RC attach: pipe a prompt (costs a turn). | github.com/anthropics/claude-code/issues/73373 (2026-07-02), /80954 (2026-07-24), code.claude.com/docs/en/desktop | YES on 73373: bcherny 2026-08-17 could not reproduce, suspects WSL pipe EOF; closed needs-repro |
| F. CLAUDE.md ignored / over-promised | CLAUDE.md is advisory. Even with a PreToolUse hook, the hook proves a verify tool was CALLED, not that its output was USED. Hook-instruction compliance also dropped from March 2026. | Deterministic gates: PostToolUse linter/compiler that fails the turn; Stop hook that runs tests and refuses "done" (guard stop_hook_active); permission rules; CI. Layer: UserPromptSubmit hook + short CLAUDE.md saying hook text is mandatory + detail in on-demand skills (author: more reliable, skips still happen). | github.com/anthropics/claude-code/issues/14417 (2025-12-18), scottspence.com/posts/how-to-make-claude-code-follow-hook-instructions (2026-03-22) | No staff on 14417 |

## Detail by problem

### A. Zero-click start_session
- No GitHub issue, post or doc sentence about the approval card on start_session was found. Treat as UNKNOWN, not "by design".
- Docs (code.claude.com/docs/en/desktop, fetched 2026-10-23): "Start: starts the task in another session" is a card button. "You get an approval card before Claude archives a session, except in Auto mode and Bypass permissions mode." Incoming cross-session messages keep the RECEIVING session's own permission settings. Bypass "runs without permission prompts, except for the actions no mode auto-approves ... or desktop actions such as deleting a session".
  Reading: Anthropic carved out specific desktop actions; start may be one. Cheapest test: run the coordinator in Bypass, call start_session once.
- #58757 (Windows, built-in MCP server): tools flagged requiresUserInteraction stay blocked in Bypass ("unavailable in unsupervised mode"). If the ccd_session tools carry that flag, no mode removes the card. Reporter workaround: Ask mode, Always allow, later calls passed. Closed by stale bot, locked; no staff.
- #77688 (July 2026, v2.1.210): permissions.allow entry for an MCP tool still prompts in auto mode; classifier suspected. Closed as dup of #76238 (not opened); no fix known.
- #52698 (April 2026): bypass-all still prompts for MCP tools; dup of #38834 (not opened).
- #48479: Desktop offers Allow Once / Always Allow only; Always Allow writes .claude/settings.local.json. Idea (unverified for the desktop card): add `mcp__ccd_session__start_session` to permissions.allow, as exact-name pre-allow worked for subagents in #64750.
- A PreToolUse hook returning permissionDecision "allow" is the documented auto-approve route; no post found proving it removes a desktop card. Untested.

### B. Hooks and worktrees
- #83953 is our problem, still open, no staff answer. Reporter design: hooks at user scope, script copy outside the tree, allowlist of checkouts, status check for stale copies. Our memory note (hooks come from main checkout) matches.
- #36656/#36360: reporter workaround copy .claude/helpers into the worktree; proposals (symlink, new env var) not implemented.
- #46808: hooks silently skipped in a linked worktree; reporter suggests `git rev-parse --show-toplevel`; bkit plugin prints a warning at session start.
- #83951 (open): no supported way to list Claude config roots; matters if installing hooks into every root.
- Stop-loop numbers: #55754 about 50 min; #54360 5+ fires in 10 min. Bot closed/locked, no fix.

### C. Subagents
- Cluster of at least 6 issues (July 2026, versions 2.1.201 to 2.1.207). One was marked resolved 2026-07-11 per a search snippet (#75565, not opened); unclear if shipped. #75054 open.
- Consistent with our "separate sessions, not agents" rule: resumed agents drift off the pinned model, and agents cannot take permission prompts.

### D. Compaction
- #43733 comments hold every fix people use; none is harness-level. Bot closed not planned 2026-05-16.

### E. Waking sessions
- Desktop in-app route (docs): Claude can message other desktop-run sessions; receiving session's permissions apply. This is our send_message path.
- Headless: positional prompt worked across a 40-turn chained run (#73373).
- #80954: RC attach to a finished headless session needs a prompt piped (a full turn). Closed not planned.

### F. Rules ignored
- #14417: hooks verify action, not use. Community answer: put the check on something that reads the result (compiler, test, CI) and block Stop on failure. Matches our "new tests must fail pre-change" rule; add a Stop/PostToolUse hook that runs it rather than trusting a claim.

## Gaps
- No Reddit or Hacker News threads opened. No X posts from Anthropic staff found. Discord not searched.
- Only staff comment found: bcherny on #73373 (2026-08-17); bcherny label edits on #83953/#83951. Everything else is bot-only.
