# Promised fixes audit, 2026-10-22

Base: origin/fast-track @ 59d64023f (2026-10-21), plus the NEXT_SESSION.md fix in this branch.
Status: DONE = shown on trunk now by file or test. NOT DONE = absent or failing. PARTIAL = some shown, rest unverified.

## Summary
- DONE: 2 (S2 start rule, O1 silent turn notices)
- PARTIAL: 2 (C1 CI red, S2b transcript count)
- NOT DONE: 1 (R1 role fallback)
- Not audited in full: X1 (fast-track fix commits, only listed by title)

## CI state
- Newest run on 59d64023 (run 39663504601, 2026-10-21 19:39Z): FAILED on both Offline gate jobs, Step 4d.
- Cause: `test_integrity.py::test_7b_nothing_else_depends_on_the_claude_md_cap_number`: "CLAUDE.md cap number quoted outside SIZE_CAPS: ['MyTradingSys/system/NEXT_SESSION.md']".
- Fix in this branch: NEXT_SESSION.md line 19 no longer quotes the cap number. `pytest MyTradingSys/tests/docs/test_integrity.py`: 12 passed.
- Not yet shipped: CI on this fix is unknown until it runs on trunk.

## Rows

| ID | Promise (quote + source) | On trunk now (file:line, commit date) | Status | Owner area |
|---|---|---|---|---|
| C1 | "CLAUDE.md under its size cap (CI red)" (59d64023f, 2026-10-21). Run 43e7370e failed on the CLAUDE.md size cap (7241 B > 7168 B). | CLAUDE.md 7163 B (`git cat-file -s`); cap at `MyTradingSys/tests/docs/test_integrity.py:14`. The size test passes. But 59d64023f then failed test_7b (NEXT_SESSION.md quoted the cap number, run 39663504601). Fixed in this branch, not on trunk yet. | PARTIAL: size fix verified; the next red cause is fixed here, not shipped. | CI / docs gate |
| S2 | "started sessions use user_asked, never cards" (8fd2c71ac, 2026-10-21 22:18 IST). Rule text: `roles/supervisor.md:34-35`, `SUPERVISOR.md:52`, `SUPER_SESSION.md:10-12` and the start-rule bullet near line 70. | `scripts/dev/model_guard.py:308-315` (`card_reason`) denies `start_session` unless initiation is `user_asked` or a proposal_id is given. Wired as PreToolUse in `.claude/settings.json:104`. Commit ca962f99a (2026-10-18). `test_model_guard.py`: 16 passed. | DONE (mechanical hook, test-backed). The prompt rule is in 3 files. | Supervisor / model_guard |
| S2b | "offer/own_initiative starts still in transcripts after 8fd2c71ac" (brief). | Earlier grep hits after the commit were the app's own prompt and tool-description text, not start calls. The one real `own_initiative` call found is 2026-10-14, before the guard. A full count of real `start_session` tool_use inputs did not complete (earlier scan blocked by the turn-budget hook). | PARTIAL: claim not supported by what was read; the count is open. | Supervisor |
| R1 | "best-role fallback" (0c6700cd2, 2026-10-21): no role line -> best fit (`scripts/dev/role_loader.py:219+`). | `ROSTER.json:9` Admin_Guy `weak_keywords` include `"?"`, `"what"`, `"why"`, `"how"`, `"where"`, `"when"`. `python scripts/dev/role_loader.py pick --text "why are super sessions still asking me to click a card? what is going on?"` returns `Admin_Guy: task text says what is, ?, what, why` (run this session). | NOT DONE. Card needed. | Role loader / ROSTER |
| O1 | CLAUDE.md 5b: "Never tell the operator about turn caps, turn counts, context size or compaction" (2026-10-21). | `scripts/dev/turn_meter.py:295` ("Silent: do not mention the compaction"); test `MyTradingSys/tests/test_turn_meter.py:153` `test_notices_tell_the_model_to_stay_silent_to_the_operator`. Commit 742fd744b (2026-10-21). | DONE for the notice text (test-backed). It relies on the model obeying the notice, not a block. | Turn meter |
| X1 | Fast-track fix commits, 3 days: turn_meter 390f02e60, 2ead83703, 742fd744b, b200b4d85, 8557ad144, ba7c049b2; mts_signal 39c858c5c, a82ac0212; supervisor/roles 67fb3ce5e, 02e00c4e2, 64f366f2c. | Commit titles listed (`git log origin/fast-track --since='3 days ago'`). Behaviour tests for each were not run. | NOT AUDITED in full. | Turn meter, usage bounds, mts_signal |

## Cards to create (lane SONNET, prio 2)
1. `Role fallback: "what", "why", "when", "how", "where", "?" must not pick Admin_Guy` (R1). Edit `ROSTER.json` weak_keywords or the scoring in `role_loader.py`. Test: the sentence above picks no role; a real backlog sentence still picks Admin_Guy.
2. `CI: 59d64023 red on test_7b; ship NEXT_SESSION cap-number fix and confirm green` (C1). Evidence: run 39663504601, `test_integrity.py:171`.
3. `Audit: count real start_session initiation values after 8fd2c71ac` (S2b). Parse assistant tool_use blocks only, not text matches.
4. `Audit: behaviour tests for X1 fast-track fix commits` (X1).

## Pending operator
- None decided here. Whether an unclear role should ask or fall back is a judgement call for the operator.

Shipped on: pending (see the ship step's result).
