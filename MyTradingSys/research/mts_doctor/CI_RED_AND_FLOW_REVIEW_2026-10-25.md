# CI red handling and the operator flow: independent review (2026-10-25, Opus, login C)

Asked by the Lead/Doctor (gulf-otter) for the operator. Read-only review; every claim checked in the source this turn.
Dates are the file's last change on trunk.

## A. CI red: the six claims

**Main finding (claim 5): why the local ship passed what CI failed. Not CRLF.** `test_role_budget.py:28-32` (2026-10-23) counts
CRLF bytes the same on every OS (7686 > 7500 everywhere). The real cause is that `sync.py` has two meanings of "docs only":
- `sync.py:141` `needs_gate()` looks only at the file ending: `.md`/`.txt` are docs, so the 9 task-card `.json` files in 5f12bc06c
  made it "code" and the ship took the code path (`sync.py:774`, 2026-10-24).
- On that path `gate_select.py:52-57,226-230` (2026-10-24) calls `.json` under `MyTradingSys/system/` data, so the whole ship is
  "docs" and runs **zero** local steps (`DOC_STEPS = ()`, line 43).
- The quick docs checks that would have caught it (`preship.py` DOCS_SHIP_RULES: role budget, role loader, card lint) only run on the
  other branch (`sync.py:778-780`), which this ship never took.

Checked by running both functions on the commit's 15 files: `needs_gate = True`, every file `_is_doc = True`. So any mixed
docs + cards ship gets no local check at all. Fix: one line at `sync.py:774`, decide "docs" with gate_select's rule (as
`ci_applies()` at :557 already does), so mixed ships take the docs path and run the role/card checks (seconds, not a new gate).

| # | Claim | Verdict | Smallest right fix |
|---|---|---|---|
| 1 | ci_watch only prints, needs 2 red runs, 5 min cache, nothing wakes an idle session | RIGHT (`ci_watch.py:9-11,24-25`, 2026-10-23; hooks `.claude/settings.json:24,55`) | Nothing new. The gap: with MIN_STREAK=2 the author's OWN first red run is silent. The author waits for their own sha (Lead resume rule 9) inside the same ship shell, and one red on their own sha is enough. |
| 2 | "first to see it reverts in 10 min", nobody assigned; whole-commit revert of a batched commit? | RIGHT, and the docs disagree: CLAUDE.md step 2 says "first to see it", SUPER_SESSION.md D3 says "whoever wrote it", SUPERVISOR.md:13 says "start a ci-<sha> worker" | One wording in all three: the author reverts first (only they know they just shipped); anyone who sees red later does it if the author is idle. **Reverting only the failing file is a revert, not a forward-fix, when it puts back the exact last-green bytes and adds nothing new.** That is what d65c2b35f did: acceptable. Revert the whole commit when it touches code, or when unsure which file broke. Writing a new line to make the test pass is a forward-fix: not allowed. |
| 3 | red blocks code ships, docs ships pass: that is how red grows | INCOMPLETE (`sync.py:536-595`) | Letting docs ships through red is right (the revert and its note are docs). Red grows for two other reasons: claim 5 (docs/cards ships skip their own checks) and claim 4 (card pushes start no CI, so a bad card turns red on someone else's later push). Fix those two, keep this. |
| 4 | ci.yml skips md/json-only pushes, so their reverts get no CI run | INCOMPLETE, and wrong for this incident: `MyTradingSys/system/roles/**` IS in the filter (`ci.yml:18`, 2026-10-23), so 5f12bc06c and the revert both ran CI | Add one line `MyTradingSys/system/tasks/**` to the filter: CI runs the card lint, but card pushes never start a run, so a bad card is blamed on the next code sha. Other md stays skipped (correct). |
| 5 | local gate passed what CI failed: role files treated as docs? CRLF? | WRONG cause: not CRLF, see main finding | The `sync.py:774` one-liner above. |
| 6 | supervisor stops dispatch while red; ci_red_card files a ci-<sha> card | Half works. `supervisor.py:161-175` (2026-10-23) reads ci_watch on each wake, so "stop dispatch" works, but only when it wakes. `ci_red_card.py` (2026-10-17) needs `gh` (not on JIS-NUC or DESKTOP) and is run only by `auto_deploy.py` (a retired scheduled task); last card filed: ci-1687ee8 on 2026-10-22. Paper. | Remove, do not repair: SUPERVISOR.md:13 says "CI RED -> stop dispatch, revert" like SUPER_SESSION D6; drop the ci-<sha> worker and the card filing. |

**Missing, not named in the claims**
1. The commit check (`preship.py:9-11`) blocks the same failure only once per session, then lets the second try through. Whether it ran
   in the Lead's tree: NOT_IN_DATA (no hook log read).
2. Batching makes reverts costly: the 10-min gap between ships (`sync.py check_ship_gap`) pushes people to put 15 unrelated files in one
   commit, so a revert also undoes 8 cards. One topic per commit is the cheap cure; no new rule needed beyond the revert wording above.
3. No headroom: roles/supervisor.md was 7388 of 7500 bytes (98.5 %) before the edit. Trim the file, do not raise the budget.
4. Nobody owns trunk after a ship: the author goes idle and the coordinator only wakes on a message. Claim 1's fix (author waits for own sha) closes it.

## B. The operator flow

**Designed flow today (SUPER_SESSION.md 2026-10-24, it wins over the others)**
1. Operator types in the Win App: `You are Supervisor. Login <A|B|C>. <tasks>` (roles/supervisor.md, ROLES.md:17). That session IS the super session.
2. It boots: `get_usage`, `supervisor.py plan`, a Doctor Agent if the last report is over 12 h old, a Planner Agent if fewer than 6 ready cards.
3. It starts 2 workers (one card each; sessions on operator turns, Agents on event turns). Each worker ships once, reports, is archived.
4. Unattended: it wakes on worker reports and its own `supervisor.py wait` shell; its notes file lets it survive compaction.
5. It ends on STOP/HOLD, CI red, 5 h window over 80 %, no cards, or 24 h; hands over; the operator types the next start line.
Thinker stays a separate operator session. RUN_MODEL.md (2026-10-22, design) moves unattended work to the CLI loop `mts_run.py`.

**Contradictions**
- Length: SUPER_SESSION D1/D6 "one session, up to 24 h" vs RUN_MODEL.md section 1 "the supervisor is the script, not an LLM session" vs the 10-25 Lead resume ("fresh session so no session runs long") and Pilot 3 (supervisor 127k context for 2 small cards).
- Workers unattended: D3 step 4 "Agents on event turns", but Pilot 3 addendum (a) shows Agents cannot edit in their own worktree, and findings row 5 shows sessions cannot be started on event turns. So unattended spawning works in neither form today.
- Worker caps: SUPER_SESSION rule 2 "stop at 40 turns" vs WORKERS.md rule 5 (context caps, 2026-10-25) vs test_role_budget's retired words "<= 40 turns" / "tool-turn cap", which CLAUDE.md step 5 still uses.
- CI red owner: three answers (claim 2).
- "Lead": the session that actually steers the day has no row in ROLES.md or HOW_MTS_RUNS.md (NOT_IN_DATA).

**Recommended simple flow now**
1. **Plain session (default):** one task he types. Ends when it ships. Most work should be this.
2. **Super session (= Supervisor, one thing):** only when 4+ ready cards sit on different files and the 5 h window is under 60 %. He types the start line himself (so it can start sessions). One 5 h window, not 24 h; ends at 80 % or no cards.
3. **Lead:** one short session a day for his messages and steering; writes a LEAD_RESUME file and is replaced, never compacted. When to replace: NOT_IN_DATA; OURS: about 150k context or 10 of his turns.
4. **Thinker:** design questions with him, separate, as now.
5. **Overnight / unattended:** the `mts_run.py` CLI loop once the Lenovo steps 7-8 are done, not a super session (event turns cannot start sessions).
6. **Session got long:** tell it "write your resume file and ship"; open a fresh session with one line "read handover/<file>". Never send /compact as a message.

## Proposed cards (not created)
1. `ship-docs-checks-on-mixed-ships`: sync.py:774 uses gate_select's docs rule; test: a ship of a role .md plus a card .json runs the role budget check (fail-first). Sonnet, S, review Agent (gate file).
2. `ci-paths-task-cards`: add `MyTradingSys/system/tasks/**` to ci.yml paths. Haiku, XS.
3. `ci-red-one-wording`: same revert rule in CLAUDE.md step 2, SUPER_SESSION D3, SUPERVISOR.md:13 (author first; last-green bytes of the failing file, whole commit for code or when unsure); drop the ci-<sha> worker. Sonnet, S.
4. `ship-waits-own-ci`: the ship shell waits for its own sha's CI and prints red at once (folds Lead rule 9 into the ship; not a new process). Sonnet, S.
5. `supervisor-role-trim`: bring roles/supervisor.md under 90 % of its budget. Haiku, XS.
6. `one-coordinator-doc`: Supervisor and super session are one role; SUPERVISOR.md and SUPER_LOOP.md become pointers; fix the 40-turn wording. Sonnet, M (after the tooling freeze).
