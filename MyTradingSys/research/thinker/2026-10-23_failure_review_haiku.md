# Root-cause review: operator asks, 2026-10-21 to 2026-10-23

Read-only review. Input table: `MyTradingSys/research/thinker/2026-10-23_operator_asks_48h.md`. Nothing committed, no file edited except this report. Probes were read-only: one `model_guard.py hook` run with a synthetic start_session, `role_loader.py pick`, `gh run list`, `git log/show/status`, transcript reads.

## Method and limits

- Each FAILED, OPEN, UNVERIFIED row, and the HELD rows I think are mislabelled, were traced to code (file:line), a commit on origin/fast-track, and a transcript line.
- Transcripts read: `1451cd3a-...jsonl` (silly-joliot worktree, Supervisor C), `cc7463df-...jsonl` (eloquent-lederberg, Q&A helper), `528eee96-...jsonl` (ecstatic-roentgen, Krown/Codex/Gemini), `21a18436-...jsonl` (supervisor-dsa-nb-handover, routine check), `c26d4e18-...jsonl` (backup), `c6fb0840-...jsonl` (mts-doctor-role, ship timeouts).
- Main checkout checked: branch fast-track at `e3ac66a23`, 15 commits behind origin/fast-track `2eba558b3`, 54 dirty tracked/untracked entries.
- Not verified: see the last section.

## Ranked root causes

Rows are counted once per cause they primarily explain. "Touched" adds rows where the cause contributed.

| Rank | Root cause | Rows explained | Evidence | Smallest fix | Test |
|---|---|---|---|---|---|
| 1 | **RC-A. Starting a session has three gates, and only one is ours.** (a) `model_guard` denies role-session starts (`nested_reason`, model_guard.py:403-416). (b) On event turns it denies even `user_asked` (`card_reason`/`event_turn`, :319-353). (c) The app shows its own approval card for session starts; no hook controls that. The Eagle_Eyes fix (3edcc612d) was committed at 14:05Z, after the 13:29, 13:34 and 13:35 attempts, and nothing retried afterwards. | 1, 3, 4, 5, 38 (session half), 46. Touched: 1, 3, 4, 5, 46. | Transcript 1451cd3a: 13:29:46 "a start_session from a role session waits for an operator approval"; 13:34:30 event-turn deny; 13:35:57 nested deny. No start_session call after 13:35. My probe: `model_guard.py hook` on an Eagle_Eyes `user_asked` start from this transcript returns allow now. supervisor.md:39 says "even user_asked showed the operator an approval card (NUC, 2026-10-22)". Five tool results in 2026-10-21 17:04: "you can start a session only on a message typed in the desktop app". | (1) Run one live probe: typed-turn role session calls start_session `user_asked` with "You are Eagle_Eyes." on line 1, record whether a card appears. (2) If the card stays, test a `permissions.allow` entry for `mcp__ccd_session__start_session` in the local settings (not in trunk settings.json) on one machine. Only (2) can remove the card. | Hook: parametrised cases in MyTradingSys/tests/test_model_guard.py (typed role-session Eagle_Eyes allow; same on event turn deny; Builder via start_session deny). Each must fail on `3edcc612d^`. Live: the probe result is the only real test of the card. |
| 2 | **RC-B. Trunk fixes never reach the main checkout, which the hooks and scripts run from.** `trunk_lag.py fast_forward` skips a checkout with any tracked change (trunk_lag.py:84-85, `git status --porcelain --untracked-files=no`). Main checkout has tracked edits to runtime CSVs and SUPERVISOR_LOG, so the fast-forward never runs. Which checkout the hooks load from in worktree sessions is not verified. | 18, 26 (primary). Touched: 1, 3, 5, 25 (fixed by hand). | Main checkout `e3ac66a23`, 15 behind `2eba558b3`; `git status` shows `D MyTradingSys/runtime/orderflow_live/*.csv`, `M .../SUPERVISOR_LOG.md`. Reflog: last ff by hand at 20:01 IST. 26 was "HELD" in the table but has recurred. | Refuse the fast-forward only when a dirty path is in `git diff --name-only HEAD origin/fast-track` (git's own ff check already refuses overlaps). Ignore runtime and live-state paths. | scripts/dev/test_trunk_lag.py: temp repo, clean commits behind, a dirty runtime file not in the diff. Must move HEAD. Current code returns 0, so it fails on current code. |
| 3 | **RC-K. Plans and cards shipped as "done" with no owner for the build step or the data.** Designs, plans and a Workflow were shipped; the thing that records results, logs tokens, or builds the feature had no card with an owner. The Workflow ran at 12:52Z with no recording step. | 11, 13, 20. Touched: 12, 31. | Usage pilot: "The token columns stay empty until a usage-logging script exists" (transcript 1451cd3a 12:04). CBP run results: "I haven't recorded these results" (row 11). 19:27 prompt-hook: research only (row 20). E2E_PROOF.md never written (row 31). | Tasks lint: a card whose "done" needs a file or column that a named card will produce must depend on that card (tasks.py). A plan is not "done" until its result file exists on trunk. | MyTradingSys/tests/test_tasks.py: a fixture card with an unbuilt data source fails lint. Fails on current code. |
| 4 | **RC-F. Ship and CI claims are made before the gate finishes.** A foreground `sync.py ship` takes longer than the 600 s Bash timeout, so it is moved to background and the builder retries. The 10-minute same-tree ship gap (sync.py:41, :514) then refuses retries. Separately, the Supervisor said "CI green" on the push, not on the run. Its 3edcc612d change grew supervisor.md to 7626 bytes and failed the role budget in CI (e3ac66a23 trimmed it). Which gate the ship ran is not verified. | 16, 30, 31. | Transcript c6fb0840 12:11:38: "Command did not complete within its 600s timeout and was moved to the background". gh: 3edcc612d CI failure 14:12Z; e23afbd43 failure 15:03Z in the offline gate shards; 71682e1ea success 14:08Z. | Builders run `sync.py ship` with `run_in_background`, then poll the run. Sessions say "CI green" only from `gh run list` for the pushed sha. | A fixture where ship is slower than the timeout must not report success before the gate returns. Role-budget edits must run test_role_budget before ship (preship.py:82 already lists it). |
| 5 | **RC-G. A launch reports "started" when the process spawns, not when the job runs.** Gemini: `agy.exe` missing; `Start-Process` returned "started" and the reply said "Gemini is started". Codex: a foreground tick took the lab lock and reported IDLE for up to 3 h (codex_run.py:48). Backup: a fire-and-forget loop kept going past robocopy exit 16 and did not resume when the NUC came back. | 32, 33, 43. | Transcript 528eee96 05:40:57 `ls ... agy.exe: No such file`; 05:41:11 "started"; 05:34:55 "IDLE a lab run holds the lock". Backup c26d4e18 09:05:47 "exit 9 ... exit 16 ... exit 16"; 09:09 NUC back, copy not restarted. | Each launcher checks its binary exists and waits for the first heartbeat (log file or pid) before saying "running". Backup loop stops on exit >= 8 and retries after a reachability check. Codex tick releases its own lock in a finally. | Launcher with a missing binary must exit non-zero with a message (fails now). Backup fixture with an unreachable destination must not report success. Lock test: kill the holder, next tick runs. |
| 6 | **RC-C. Multi-part asks and compaction drop asks.** A two-clause message gets an answer to the first clause. A compaction summary drops open work. | 12, 15, 21. | 528eee96 05:40:31: two asks ("Use it as per remaining usage" and "Where are we with simulators?"). Only the Gemini part was answered; the ROADMAP.md was read at 05:40:49 but no answer text was written. Compaction at 12:36Z: the Krown pilot was lost ("Sorry, that was my mistake"). | A stop check that lists each `?` and imperative in the last operator message and fails if the final reply does not address each. Weak, because matching is by hand. | Fixture transcript with a two-clause ask: the stop check must block on the missing clause. Fails now (no check exists). |
| 7 | **RC-I. A rule written as prose in a role file with no hook behind it.** "Never say go" is in thinker.md:35 (a8d4fb2de). Nothing checks the final text. The Supervisor's "interactive roles start as sessions" rule is in supervisor.md:38, with the code 3edcc612d. | 4, 19, 18 (question instead of action). | Row 19: "Send any message from the desktop app and I'll start it then" (03:40Z 10-23) after the rule was on trunk. Row 18: "Should I create the three fix cards?" | A Stop-hook regex on the last reply for "say go", "send any message", and "should I" when the work was ordered. Block once, as stop_guard does. | stop_guard fixture: a final text containing "say go" is blocked once; a normal reply passes. Fails now. |
| 8 | **RC-D. Role fallback ignores aliases; path matching was the bug.** `pick_role` reads keywords only (role_loader.py ~233-250); aliases like "q&a helper" are used only for an explicit `You are <Role>` line. The 21:31Z banner "ROLE LOADED: Thinker (fallback: task text says idea)" came from "IdeaProjects" in the path, fixed by 8b4ea32a2 on 10-22. | 21 (primary). 2 (session identity). | `role_loader.py pick --text "Q&A helper"` returns "NONE: no role keywords in the text" today. Transcript cc7463df 21:31:24 shows the Thinker fallback. | Let `pick_role` accept an alias phrase as a full-word match. | Test: `pick("Q&A helper")` == Admin_Guy. Fails now. |
| 9 | **RC-E. Messaging is gated to sessions this session started.** `message_reason` denies a SendMessage to any session not in this session's start_session results (model_guard.py:171-186). So a session cannot wake or message an operator-started session. Whether the app wakes an idle session at all is not verified. | 2, 22 (caveat). | Transcript cc7463df 20:10Z: "The hook blocks me from messaging sessions I didn't start." 66f635cee says "wakes reachable sessions" but delivery stays pull-only (row 22). | Allow SendMessage to sessions on this host that the operator started (or whose transcript shows a typed turn). | test_model_guard: an operator-started target is allowed; an unknown target is still denied. Fails now. |
| 10 | **RC-J. No single source for which login or machine a chat runs on.** The Supervisor guessed login from a machine name. | 34, 35. | 34: "The Lenovo session (login C)". 11:47 op: "you are reading stale information". Lenovo is login A. | ba8b2e077 (roll call) is on trunk; keep. | Its test; cross-host use still unverified. |
| 11 | **RC-M. Destroying unshipped work needs an explicit operator decision the operator never gave.** tidy and wt_maint keep trees with unshipped commits (correct). Claude asked in-session and removed only the safe subset. | 39. | 1451cd3a 05:42: "Discard the 7 worktrees kept for 7 days? That permanently loses their uncommitted changes". Operator asked 3x. | A dry-run list the operator approves once, then `--discard-unshipped <list>`. | wt_maint dry-run output test: unshipped trees are listed, none removed without the flag. |
| 12 | **RC-H. The scheduler check looked at one surface.** `list_scheduled_tasks` returned "No scheduled tasks found" (21a18436 05:43:28). Cloud routines were not checked. | 9. | Routine named "cbp-daily-workflow" in the operator's own prompts. Claude concluded it "isn't registered with the scheduler". | Check cloud routines too before saying "not found". | Not testable in-repo; a checklist line in the Supervisor brief. |

Also on the list, with one row each and no shared cause: rows 6 (CBP gates: CI billing, scheduler task, scorecard), 8 (video HTTP 429 with no backoff), 24 and 37 (no evidence), 41 (fresh session stopped; likely TOOL_CAP=40 at turn_meter.py:32 or the unattended read budget, not checked), 44 (note: the "Local note only" answer came back in a question card).

## Adversarial notes: fixes that cannot solve their symptom

- **8fd2c71ac (`user_asked` allowed) cannot remove the approval card.** The hook only decides whether the session may try. The card is the app's own permission prompt. The only lever is the permissions allow list, which trunk settings.json does not carry (`.claude/settings.json` has `env` and `hooks` only). The Supervisor's own 15:16 message says the same.
- **3edcc612d (interactive-role exemption) fixed the hook, not the symptom, and was not retried.** On my probe the hook allows Eagle_Eyes now. The row is OPEN because the one attempt that could tell (a live typed-turn start after 14:05Z) never happened.
- **f9dca7304 (session-start fast-forward, 10-22 23:13 IST) cannot hold on a main checkout that the live system dirties.** Its clean check is over-broad (RC-B).
- **Cards (b5d04c050, 96784f370, c2e76d8df) do not fix behaviour.** Each card is a record; the fix is the hook or the check. Rows 17, 19 and 30 each shipped a card and kept the failure.
- **a8d4fb2de ("never say go") cannot work as prose.** It is the same rule that was already in the prompt for row 19 (RC-I).
- **Row 25's fix (f3ac1d6c0 SubagentStart role injection) is real.** My reading of the probe result is that it holds; keep HELD.

## One line per row

Label, then cause code. "Mislabel" means I would change the table label.

1. FAILED, RC-A (+RC-B: guard 3edcc612d not on the main checkout). Fix 8fd2c71ac did not stop the card; nothing retried after 14:05Z.
2. FAILED, RC-E. The hook blocks messaging sessions not started by this session; delivery to idle sessions is not verified.
3. FAILED, RC-A (+RC-B). 13:29 and 13:35 denied as role-session nested starts (13:35 was before 3edcc612d reached trunk). No retry after the fix.
4. OPEN, RC-A. Rule held (hook probe allows); no start attempt after 14:05Z.
5. FAILED, RC-A (+ hand-written brief with three errors). Admitted at 15:12.
6. OPEN, one-off gates (CI billing, scheduler, scorecard). Not systemic.
7. HELD. Consumer row and profile on trunk; the seventh quote issue is row 8.
8. OPEN, external: video 429 with no retry/backoff. Six of seven held (ec54395ba).
9. OPEN, RC-H. "No scheduled tasks found" was the only check.
10. HELD. Design on trunk; the run it designed then ran (row 11).
11. OPEN, RC-K. Run finished 15:03Z; results not recorded; no recording card.
12. OPEN, RC-C + RC-K. Krown pilot lost at the 12:36Z compaction; S2-S6 never launched.
13. OPEN, RC-K. Cards on trunk; token column empty until a logger card exists.
14. HELD. Answer only, as asked.
15. UNVERIFIED, confirmed no answer. RC-C: the roadmap question was not answered in the transcript.
16. FAILED, RC-F. "CI green" claimed on push; 3edcc612d red at 14:12Z (role budget), e23afbd43 red at 15:03Z (offline gate shards).
17. HELD. Report on trunk (b5d04c050); the first run was blocked by the turn budget.
18. FAILED, RC-B (+RC-I). Recurrence: the main checkout is 15 behind again (`e3ac66a23` vs `2eba558b3`). Same failures on 10-23.
19. FAILED, RC-I. Rule in thinker.md:35 only; the reply still ends with "Send any message ... and I'll start it then".
20. UNVERIFIED, RC-K. Research only; no builder card for the prompt hook found.
21. OPEN, RC-D + RC-C. Misrouted to Thinker at 21:31Z (fixed by 8b4ea32a2); the 82.5k ask got no reply. Q&A helper still not routed by fallback.
22. HELD (caveat). Broadcast fix on trunk (66f635cee); delivery stays pull-only (RC-E).
23. HELD. Audit file on trunk.
24. UNVERIFIED. Answer only, no proof run; not re-run here.
25. HELD. f3ac1d6c0 + 92b1ee625; SubagentStart injection works. Main checkout fast-forwarded by hand (later lagged again, RC-B).
26. Mislabel: should be OPEN. RC-B; main checkout 15 behind now.
27. HELD, but value questioned. 367f68b59 on trunk; d6dfe85ea tuned to 0 pairs; the check may not be worth keeping.
28. HELD. 1f1233020 on trunk; role tests pass.
29. HELD. Design only, nothing built (as the row says).
30. OPEN, RC-F. Ship timed out (600 s Bash limit) and 10-minute ship gap; A1/A2 never reached trunk.
31. OPEN, RC-F + RC-K. E2E_PROOF.md not on trunk; the 10th ship failed at 13:39.
32. OPEN, RC-G. Codex IDLE on a lock held by its own foreground tick; 3 h stale window (codex_run.py:48).
33. FAILED, RC-G. `agy.exe` missing on JIS-NB; launcher printed "started" with no check.
34. FAILED, RC-J. Premise wrong (login guessed from machine name). Real fix ba8b2e077.
35. HELD. ba8b2e077, 0acafd134, 8c00b0277 on trunk; cross-host use unverified.
36. HELD. d985ef3be; tail open (rename NB .mts_live, mirror brief).
37. UNVERIFIED. No git or sidebar check made here.
38. HELD (session half failed, RC-A). Coin box on trunk (8fd2c71ac); session start fix did not hold on the operator's side.
39. OPEN, RC-M. 38 removed; 34 kept because they hold unshipped work. Operator asked 3x; decision never recorded.
40. HELD. Operator paste shows "0 exclusion(s) missing".
41. OPEN, not checked. Likely TOOL_CAP (turn_meter.py:32) or unattended read budget; no transcript check made.
42. HELD. Paused as asked.
43. FAILED, RC-G. Loop continued after exit 16; no resume after the NUC came back at 09:09.
44. HELD (question to check). "Local note only" came back as an answer to a question card; confirm the operator chose it.
45. HELD. Memory file habib-not-qriptal.md; no repo sha.
46. Mislabel: should be FAILED. Operator asked for a separate session; blanket "workers are background Agents" rule (supervisor.md:39, nested_reason) gave a background worker. RC-A.

## Not verified

- Whether a typed-turn `start_session user_asked` still shows an approval card today. No post-14:05Z attempt exists. Needs one live probe.
- Which checkout the hook scripts load from for worktree sessions (settings.json is tracked in both; a memory note says main). This decides how much RC-B matters per session.
- Whether the ship that landed 3edcc612d ran the role-budget gate (preship.py:82).
- Whether a cloud routine "cbp-daily-workflow" exists (only the local scheduled-task list was checked).
- Rows 24, 37, 20 and 41: no evidence was re-run.
- NUC state after 09:09 (row 43) and Gemini state on the NUC (row 33) were not checked; the 08:23 claim is taken from the table.
- The ranking is by rows explained, judged from one or two transcripts per root cause. RC-K and RC-C rest on the thinnest evidence.
