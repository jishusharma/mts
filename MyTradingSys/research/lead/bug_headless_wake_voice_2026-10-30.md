# Bug: Supervisor misread dictated "cloud" (= Claude) and the headless successor wake was never explained properly

Date 2026-10-30. Supervisor C (JIS-DESKTOP). Operator dictates by voice; "cloud" in his messages means "Claude".

## Verbatim conversation (operator text exactly as sent; supervisor replies condensed to their claims)

**Supervisor:** Successor wake fired 02:41Z and failed: claude exit 1, "Failed to authenticate: OAuth session expired and could not be refreshed". No successor exists. Asked operator to run `claude /login`.

**Operator:** "So what can you please explain to me why it failed? Because of the failed to authenticate. Error."

**Supervisor:** The scheduled wake ran `claude.exe -p` (headless) as a separate Windows process; it used a saved login that had expired. Cause of the expiry not proven. err.log held only harmless `Write(F:/...)` vs `Edit(...)` permission-rule warnings.

**Operator:** "Can you tell me where this scheduler wake ran? For the headless mode that you're talking about. Is it on the desktop? And if so, then tell me something that if Claude is already opened and you are working, on it, and then I go to sleep in the night, then what is the point in firing a headless cloud application? When the actual application is already opened in"

**Supervisor:** Ran on the desktop (JIS-DESKTOP) as a Windows scheduled task, "never touched the cloud" (it took his "cloud" literally). Said the wake only helps if the context fills or the app closes; offered to drop it.

**Operator:** "idiot - udo noteven know so far that cloud means claude??? i use mic!"

**Supervisor:** Apologised; restated: hidden Claude process, not the open window; default = do not re-issue the wake.

**Operator:** "log a bug you are not even able to understand my question, and react to it. So log a bug for Opus. To get this fixed, and record all my verbatim conversation with respect to this. Discussion that we are having about the cloud application running in headless mode and why it was done and things like that. And what really needs to be done? Is the bug is all about. That should be fixed."

## What the bug is (two parts)

1. **Voice misreads.** The supervisor answered "cloud" literally ("never touched the cloud") instead of reading it as "Claude" (memory `voice-dictation-mishears`: take the reading that fits the project). It then asked a question he had not asked. Fix: a rule + a check so role sessions map dictated "cloud application / cloud code" to Claude / Claude Code in this project, and answer the question he actually asked.
2. **The headless successor wake is the wrong design, and it fails silently.**
   - Why it was done: a session that runs out of context cannot restart itself; the wake (`successor_wake.py`, one-time task `MTS-SuccWake-C`, runs `claude.exe -p` hidden) was meant to open a fresh Supervisor at the 5h reset while the operator sleeps.
   - Operator's objection (valid): the Claude app is already open and working; compaction already continues the same session; a second headless process adds only a failure point.
   - Why it failed: headless `claude -p` uses the saved login in `C:\Users\E-ngineers\.claude`, not the open app's session. Token expired and refresh failed. Cause of the expiry unproven. This probably also caused the 10-29 failure (the `e1e0dba8` run.ps1 logging fix did not address it).
   - Unrelated noise in err.log: `Write(F:/...)` allow rules in `~/.claude/settings.json` should be `Edit(...)`.

## What needs to be done (Opus)

- Decide, with the operator's objection in mind, whether the successor wake should exist at all. Default recommended: retire it from the rolling-supervisor design (SCHEDULING_POLICY 4b2, `successor_wake.py`, supervisor role doc) and rely on in-app compaction + hand-over; keep a wake only for the "app closed overnight" case and then only with a pre-flight `claude -p "ok"` auth check at registration time that refuses to register on failure.
- Add the voice rule ("cloud" = Claude here) to the role docs / reply rules and a test or lint if one fits.
- Fix the `Write(...)` -> `Edit(...)` rules in settings.json (operator-owned file: propose the diff, do not edit silently).
- Also found on trunk: `OPERATOR_DECISIONS.md` ends with conflict markers (`=======` / `>>>>>>> origin/fast-track`) around entry d-fable-r5-r7-run; repair so the file parses.
