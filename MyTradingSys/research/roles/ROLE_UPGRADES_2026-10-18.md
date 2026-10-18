# Role upgrades 2026-10-18: one tool per role (reviews by GPT-6 Astra and Gemini 3.8 Flash, merged by MTS_Doctor)

Context: every role now loads through `scripts/dev/role_loader.py` (hook, proof token, banner; trunk f1203643, 20 tests).
Two independent read-only reviews were asked the same questions (weak points, the biggest speed-up per role, merges, top 5).
"Both" = the two reviews proposed the same thing independently. Savings are GUESS until measured over one week.

| # | Card | Role | Extends | Both? | Effort | Verify |
|---|---|---|---|---|---|---|
| RU1 | `tasks.py dispatch --json`: one ranked snapshot of ready cards with holds, overlapping claims, dependencies, CI state and reviewer slot resolved | Session_Planner (and Pipeliner reads it) | scripts/dev/tasks.py | yes | M | fixtures: held, claimed and dependency-blocked cards are excluded; output equals a hand-ranked table |
| RU2 | `desk.py sweep --dry-run`: desk rows > 48 h, claims > 24 h, rows whose work is already on trunk (topic-word match, sha as proof), lane depths; proposed action per row, idempotent | Pipeliner | scripts/dev/desk.py | yes | M | fixtures: duplicate, stale and delivered rows each get the right proposal; second run proposes nothing new |
| RU3 | `shot.py bundle <set>`: classify, engine snapshot, previous read, open mismatches and mirror age in one packet; extract stub with MATCH/MISMATCH lines | Eagle_Eyes | scripts/dev/shot.py | yes | M | a stored multi-chart set yields one packet; stale mirror is flagged, not used |
| RU4 | `role_loader.py lint` (or mts_doctor roles section): policy contradictions across role files and ROLES.md, dead commands, missing files; mts_doctor guidance selector currently skips roles/*.md (mts_doctor.py:40) | MTS_Doctor | scripts/dev/mts_doctor.py, role_loader.py | GPT | S | fixture with the known contradiction (eagle_eyes.md:35 compaction vs ROLES.md:40 no compaction) is caught |
| RU5 | Lab pre-check: zero-token checks of lab_guy.md:25 (formula id exists in FORMULAS.md, holdout path, split dates) inside `tasks.py check` | Lab_Guy | scripts/dev/tasks.py | Gemini | S | a card naming a missing formula id fails check with exit 1 |
| RU6 | Content-bound review receipts: a review stamp records hashes of card, spec, data and code it reviewed; a later change voids it; producer cannot self-review | Lab_Guy | scripts/dev/tasks.py | GPT | M | change to an approved scope voids the stamp; unchanged keeps it |
| RU7 | `operator_questions.py pending`: typed questions without a recorded decision, ranked, pasted reports filtered | Q&A_Helper | scripts/dev/operator_questions.py | yes | S | fixture log with one answered and one open question lists only the open one |
| RU8 | `nowin.py` diagnostic log (opt-in): parent, child, creation flags, elapsed per spawn; `audit` lists spawns without CREATE_NO_WINDOW | Network_Admin_Guy | scripts/dev/nowin.py | yes | S | a spawn without the flag shows in audit |
| RU9 | `artifacts.py audit-links`: registry vs repo copy (newer?), every link opened, result table; removes the history-search boot step (ROLES.md Artifacts_Guy row) | Artifacts_Guy | scripts/dev/artifacts.py | yes | S | a page with a dead link and one with a newer repo copy both show |
| RU10 | Fix now-stale texts: eagle_eyes.md compaction lines (no compaction since 2026-10-18), lab_guy.md stamp-enforcement contradiction (lines 60 vs 82), pipeliner.md "first job" (drain already done in ebfffe68: later openings go straight to the sweep); then `role_loader.py retoken` | all | roles/*.md | GPT | S | `role_loader.py check` ok; no "compact" instruction left in roles/ |

## Decided, not built
- Pipeliner and Session_Planner stay separate (Gemini proposed a merge, GPT against): Planner is per super session and edits cards; Pipeliner is cross-machine and owns routing. They share RU1's snapshot.
- No CI_Fixer role (Gemini): MTS_Doctor's report gets a "CI red and owner" line instead (part of RU4).
- The banner is a receipt, not enforcement (both reviews). Enforcement of a role's required outputs is a later step after RU1-RU4.

Reviews (not committed, scratch): GPT-6 Astra medium, Gemini 3.8 Flash medium, both read-only on a detached trunk worktree at 61a5d705.
