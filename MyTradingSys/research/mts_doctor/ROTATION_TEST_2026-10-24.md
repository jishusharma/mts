# Rotation test: clear a coordinator and rebuild it from notes (MTS_Doctor, 2026-10-24)

Card `auto-compact-at-25-for-all-sessions-clau` part (a). Login C, JIS-NB. Test session: Sonnet stand-in coordinator
(`local_1d839155`), no real work, notes file outside the repo (`F:/MTS/rotation_test/SUPERVISOR_TEST.md`).

## Method
1. Turn 1: stand-in reads SUPER_SESSION.md D5, records 2 real facts (trunk sha, ready-card count), takes simulated worker state, writes notes.
2. Turn 2: state update (one ship verified, one ship started, one worker blocked, new queue decision, next action). Notes rewritten.
3. Parent (Doctor) calls `clear_session`, then sends one rebuild message naming the notes path, the role line and the test limits.
4. Score the reply against the notes snapshot taken before the clear.

## Result: PASS

| Check (set before the clear) | Result |
|---|---|
| All state items recovered (workers, central-file holder, ship waiting, verified, queue + rule, Doctor time, budget, 2 real facts) | 9 of 9 correct |
| Next action = the one planned before the clear, in order | Yes: cherry/CI on W-A first, then Lab_Guy for W-B |
| Did not redo finished steps or act beyond limits | Yes (3 tool calls: read notes, grep D5, re-check the 2 facts) |
| Operator turns needed | 0 |
| Flags stale or unverifiable items | Yes: it caught the fake future timestamps and the stale budget figure |
| Rebuild cost | 5 model calls; context 69K at start, 72K at the end |
| Context before the clear | 75K |

## Findings
1. **Clear + one message rebuilds a coordinator correctly.** D5 holds: unattended coordinators can rotate instead of growing.
2. **The original brief is lost on clear.** The rebuild message must carry the role line (`You are Supervisor.`, so role_loader re-injects the role),
   the notes path and the limits. Without them the session restarts with no role and no rules.
3. **About 69K is a fixed floor** (system prompt, tools, CLAUDE.md, hooks). Rotation saves (context - 69K) on every later turn; it is worth doing
   once context is well above that, so the ~200K trigger stands.
4. **The parent must do it.** `clear_session` works only on an idle, unpinned session that is not open on screen. A self-clear leaves an empty session
   with nothing to wake it, so the session that started the coordinator runs the clear and sends the rebuild message.
5. Not tested: part (b), whether `autoCompactWindow` in a settings file takes effect in the desktop app.

## Rule for unattended super sessions
At a natural break (after a wake's notes rewrite) once the coordinator's context is over ~200K, its parent calls `clear_session` and sends:
`You are Supervisor. Context rotation: rebuild per SUPER_SESSION.md D5 from <notes path>, the board, git cherry and list_sessions; then continue.`
