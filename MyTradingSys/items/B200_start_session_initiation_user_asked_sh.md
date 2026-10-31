# B200 - start_session(initiation=user_asked) showed an 'Allow once' card in a Bypass-permissions session, on a turn th

Filed: 2026-10-23
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B200 | 2026-10-23 | OPEN | HIGH | start_session(initiation=user_asked) showed an 'Allow once' card in a Bypass-permissions session, on a turn the operator had typed and fully specified; the session sat 'Needs your input' while the operator was away. model_guard.py card_reason/event_turn only DENY (they cannot create or remove the card), so the card is app-side; the guard's event-turn rule may also misclassify a turn when a task-notification and a typed message arrive together. Same defect class as the 'No click cards' rule (model_guard CARD_FIX) which is on trunk but did not prevent this. FINDING (Thinker, 2026-10-23): the Allow card is the APP's consent on any turn a message or event started, not a hook; model_guard.py:314-351 (f47d4cae, on origin/fast-track) only pre-denies it. The main checkout (head cbf5bae9, the live tree) lacks f47d4cae, so coordinators started there run the old guard: start coordinators with cwd = a fresh worktree (sync.py start), keep Agents on event turns, catch the live tree up only by the deploy (DEPLOY_RUNBOOK.md). Candidate fixes: (1) find the real source of the card (app approval for start_session vs a hook ask) by reading settings.json hooks + the app's permission rules; (2) if app-side, an allow rule for mcp__ccd_session__start_session in .claude/settings.json permissions; (3) test that replays this transcript through event_turn; (4) STATUS shows the deployed model_guard sha so the operator can see whether the fix is in the trunk and the running checkout. | [FIXER: Claude] [LOGGER: Claude DESKTOP-F7IU69N] Operator asked 2026-10-23 which hook fires this and why fixes on trunk do not show. - | - |
