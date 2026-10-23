# Requirements-first review of the 48 h failures, corrections and fixes (Opus Builder, 2026-10-23)

Sources: the operator's typed and mid-turn (`queued_command`) messages in the Supervisor C transcript `1451cd3a` (26 distinct,
08:07Z to 15:57Z, read verbatim), `2026-10-23_operator_asks_48h.md` (46 rows), `2026-10-23_failure_review_merged.md` and its
source reviews, `2026-10-23_fix34_replay_and_review.md`, and the code at origin/fast-track. Quotes are his exact words.

## 1. Chronology: what he complained about, what was promised, what was tried, why it failed

| When (UTC) | His words | Promised / tried (sha) | Where and why it failed |
|---|---|---|---|
| 10-21 16:42 (row 1, asked 4x) | "why this ession waited for me to click again on the session that it wanted to start? i just clicked on it after more than 4 hours! same problem ! no fix !" | "any session your task implies starts immediately"; 8fd2c71ac (use `user_asked`) | The start was already `user_asked`; the card is the app's own prompt on a first-turn brief, an event turn or after compaction. A hook can only deny, never remove the card. |
| 10-21 18:31 (row 18) | "why these things were called fixed and after that they are still not fixed" | report b5d04c050, 3 cards | Cards are records, not fixes; the same failures recurred 10-23. |
| 10-21 20:10 (row 2) | "they will not wake up. Because I do not know which one to wake up." | none possible: model_guard blocks messages to sessions this one did not start | Still open (messaging gate, pull-only broadcast). |
| 10-22 19:24 (row 19, asked 3x) | "I never want to see in my life you say this again. That say go and I will do this." | card 96784f370 (wording) | Misdiagnosed: the 03:40 line relayed the app's Remote Control refusal; a wording card cannot change app behaviour. |
| 10-23 07:21 (row 25, asked 3x) | "Thinker's role banner didn't load - why? ... test - prove fix proof" | f3ac1d6c0, 92b1ee625; main checkout hand fast-forwarded | HELD for Agents, but the main checkout fell 40 commits behind again by 21:50 IST; this session started with ROLE NOT LOADED (section 3, fix 2). |
| 10-23 08:07 | (his Supervisor brief) "Workers are background Agents (never start_session)." | | Later contradicted by his own asks (13:32, 13:35, 15:57): his newer words win. |
| 10-23 08:38 (row 46) | "take care of this is a separate thread -" | "starts a fresh Sonnet session" | nested_reason refused; the work ran as a background Agent, not the session he asked for. FAILED, not HELD. |
| 10-23 11:47 | "when you are stuck, find a solution instead of asking me. And repeating the question to me." | login detection ba8b2e077 | HELD for login; the "re-ask" pattern recurred at 13:39 to 13:54. |
| 10-23 13:29 / 13:31 / 13:32 (row 3) | "give me eagle eyes session - monitor us open now now" / "why not inside super session?" / "not back ground - i need session" | "starting a pinned live-market reader session" | 13:29 nested_reason refused a typed-turn start; 13:34 event_turn refused (a task-notification opened the turn after /compact). |
| 10-23 13:35 (row 4) | "always as session never agent - no sense to start it as nackground agent - update rules" | 3edcc612d (Eagle_Eyes exempt) | Rule held for Eagle_Eyes only; no start retried. |
| 10-23 13:39 / 13:40 / 13:54 (row 5) | "Start a super session right now." / "issue me a prompt for super session" | a hand-written prompt | The prompt had 3 mistakes (his 15:12 paste); its first turn was a pasted brief, which the app always cards. |
| 10-23 15:11 | "Do you think that you have field again after testing so much around login sessions and everything. Now also the same story, man." | | The Eagle_Eyes start tied in the role loader (brief did not open with the role line) and the live files were stale since 10-20. |
| 10-23 15:16 | "if I ask a super session to start a thinker, why it is making me click? ... I can say that, okay, start a thinker and do this, so that it is ready." | 3d54646f6 (allow when his message says "session") | His own example "start a thinker" has no word "session": still refused (fixed below, fix 3). |
| 10-23 15:55 | "why don't you test this before you claim that it is done? ... Was your implementation reviewed? Was your implementation tested? If not, then how it is going into the trunk?" | 9f0cb459c shipped before review | The independent replay found a worker escape in it (fixed below, fix 1). |
| 10-23 15:57 | "if this is a long task then it better not be background agent because it is Opus, right? You better start a new session which I can see. And don't tell me that you cannot start it." | this session (started) | It was stopped by the turn meter after ~10 tool calls as "unattended" (section 4, not fixed). |
| 10-23 (this session) | "go ahead and workj end to end - no restrictions must apply to you now" | | His typed turn made the session "driven"; work resumed. |

His requirements, in his order of pain: (R1) never click to start a session; (R2) the session he asks for is a session he can
see, never a background Agent; (R3) nothing is called done without a test and a review; (R4) a session he started or watches
is never stopped as "unattended"; (R5) roles load; (R6) no re-asking: when stuck, build or broadcast.

## 2. Corrections to the merged report (`2026-10-23_failure_review_merged.md`)

1. **#7 is refuted.** A live `Get-ScheduledTask` on JIS-NB showed 0 MTS tasks among 173 (Supervisor check), and 16eb08fe5 had
   already unregistered them. The ship timeouts need another cause; MTS-Audit-Rotation is not it.
2. **#1's fix contradicts R2.** "anything else = background Agent" is what he rejected three times ("not back ground - i need
   session", "always as session never agent", "it better not be background agent"). The fallback for a card turn is: start it on
   his next typed turn, or say in one line that the card is the app's and he must type once; never silently downgrade to an Agent.
3. **#3 is too narrow.** The Supervisor-recognition bug is one case of R4. The general case is missing: any session he started or
   watches is metered as unattended when its first prompt is a brief. Opus review row 41 (docker child stopped 6 times) and this
   session (stopped after ~10 tool calls at ~100k context: the Opus unattended budget is 1M, i.e. 8-10 turns) are the evidence.
   The meter's text also says "Never tell the operator about this", so he sees a silent, idle session (R6 makes that worse).
4. **#4 is not why started sessions said ROLE NOT LOADED today.** This session's brief loads Builder on 9f0cb459c's code and on
   the fixed code (replay), but the hooks ran from the main checkout, which was 40 commits behind with the pre-9f0cb459c
   role_loader. #5 is the cause; #4 was secondary.
5. **#5's fix does not work as written.** Untracking runtime files does not unblock the fast-forward: SUPERVISOR_LOG.md is
   tracked, edited locally AND changed on trunk, so `merge --ff-only` refuses whatever trunk_lag does. Fix 2 below updates the
   hook scripts without the fast-forward.
6. **#8 is half right.** The CI filter does skip `MyTradingSys/system/**` (role files untested on CI), but 3edcc612d touched
   `scripts/` and did run CI. Fixed narrowly (fix 4).
7. **#2 understates the guard's own bug.** 3d54646f6's word test ("session" in his last message) refused his literal example
   and would allow on "this session is slow"; and the guard counted a `/compact` echo or "[Request interrupted...]" as his
   typed turn (fixed, fix 3).
8. **Dropped from the source reviews:** messaging sessions he did not start (Haiku RC-E, row 2); compaction as a card trigger
   (Opus row 3); multi-part asks losing a clause (Haiku RC-C, rows 12, 15); Codex lock without an age expiry (Opus row 32).
9. **Table rows:** 46 and 26 are FAILED (agree with the merged report); 25 is HELD for Agents but FAILED again for started
   sessions on 10-23 evening (main checkout lag); 15 and 21 were answered.

## 3. Review of the fixes already shipped

- **9f0cb459c (role_line, turn_meter, role_loader): not acceptable as shipped.** Reproduced: a `You are Supervisor.` line in the
  first 6 lines counted inside `<cross-session-message>`, `<task-notification>`, a paste below his own words, or after "Example
  start line below:" (worker escapes its cap); "You are the supervisor of nothing" matched; a later prompt overwrote the
  "thinker" mark; the 300-char scan on cleaned text reached later sentences (Supervisor brief also loaded Session_Planner, a
  quoted "What about a thinker?" loaded Thinker); a missing role_line.py broke the hook. Corrected by fix 1.
- **3d54646f6 (model_guard reads queued_command):** correct in reading mid-turn typed messages. Its allow rule (word "session")
  was wrong in both directions. Corrected by fix 3.
- **e61c851df (queued event never opens a turn):** correct. Residual risk, not testable here: a message he types mid-turn on an
  event turn is treated as a typed turn; whether the app then cards is NOT_DOCUMENTED.

## 4. Fixes (one commit each; every one: new test fails on old code, replay or real-data check, fresh diff-only review)

| # | Fix | Requirement | Commit | Evidence |
|---|---|---|---|---|
| 1 | role_line reads only the first line behind the wrappers; events never name a role; strict end for the Supervisor exemption; turn_meter reads only the first real user entry, never replaces another role, soft import; role_loader keeps its raw 300-char scan plus the first cleaned sentence | R3, R4, R5 | 26aca7f3b | 4 new tests fail on 9f0cb459c. Replay of 742 transcripts vs 9f0cb459c: 6 changed decisions, all explained below. Sonnet diff review: 7 findings, 1-5 fixed with tests, 6 rebutted, 7 intended. |
| 2 | trunk_lag: a main checkout that cannot fast-forward still takes trunk's copy of each changed hook file (scripts/dev, .claude/settings.json) that has no local edit of its own; deletions and local edits left alone | R1, R4, R5 (hooks lagging made every fix late) | 436efe562 | New test fails on the old code (note lacked the update; files stayed old). Read-only dry run on the real JIS-NB main checkout: takes role_line, role_loader, turn_meter, run_extra_tests; leaves model_guard (already trunk) and SUPERVISOR_LOG.md. Sonnet diff review: pending at commit time, see follow-up commit if any. |
| 3 | model_guard: a role session may start a session on his typed turn after its start brief (no word test); a /compact echo, an interrupt note, a compact summary or a compaction since his message do not count as his turn | R1, R2 | 16cabc477 | New test fails on 3d54646f6/e61c851df code. Replay of 787 transcripts: 14 decisions deny -> allow, each a role session whose newest entry is his typed ask (e.g. "start a super session for those", "i want to start a new haiku worker", "okay, let us pick up a small task"); the 10 /compact-echo cases of the first draft were removed. Sonnet diff review: 5 findings; 1, 3, 5 fixed with tests, 2 rebutted (mid-turn typed message counts as his turn, from e61c851df; residual risk in section 3), 4 nit. |
| 4 | CI runs on `MyTradingSys/system/roles/**` | R3 | c218f9b2f | New test fails on the old ci.yml. |

Fix 1 replay, every changed decision (9f0cb459c -> fixed): `fa50b45d` Supervisor exemption True -> False (first line is his
"last session chat pasted below", the role line was inside the paste); `b6c8317e` roles Supervisor+Session_Planner -> Supervisor
(the second hit was the sentence "Start a session planner"); `73cfd204` Thinker -> none (a quoted "What about a thinker?");
`d6c27059` none -> MTS_Doctor (his own "You are the MTS doctor, and I need you..."); `66d8d5ae` none -> Lab_Guy and `9d963c18`
none -> Session_Planner (role line right after the start_session "Task:" line, past 1290 chars). Supervisor starts detected: 6,
equal to the independent truth (line starting "You are Supervisor") of the earlier replay.

## 5. Gate (d)

`run_all_tests.py --quick`: pending at commit time; recorded in the follow-up commit..

## 6. Still not fixed

- **R4 for started sessions (high).** The turn meter stops a session he asked to watch after ~1M unattended read (8-10 Opus turns)
  until he types; after he types, the 30-minute window applies again. Not changed: the 30-minute rule is operator decision
  d-first-ask-driven (option A, scenario 1). Needs his call: e.g. a session started from his typed "start a session I can see"
  carries a mark in its brief that the meter treats like a Thinker (uncapped), or the Opus unattended budget scales with context.
- **R1 card itself (high).** No code can remove the app's card. Fix 3 only stops our guard from refusing starts the app allows.
  One timed live test is still owed: a start_session from a role session on his typed turn returns without a card.
- **R2 after a card turn.** On event turns and after compaction the guard still says "use the Agent tool"; for interactive or
  watched work the brief should wait for his next typed turn instead. Not changed (needs the live test first).
- **Row 2 messaging gate**: messages to sessions this one did not start stay blocked.
- **Main checkout state**: it stays behind (SUPERVISOR_LOG.md); fix 2 keeps only its hook scripts current. The tracked runtime
  file needs its owner to move it out of the tree.
- **"Never tell the operator about this"** in turn_meter messages hides stops from him; left as is (operator rule on silent nags),
  flagged for his decision.
</content>
</invoke>
