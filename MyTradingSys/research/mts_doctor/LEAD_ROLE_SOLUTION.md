# Lead role merge: the solution (Thinker session, Opus, 2026-10-25, origin/fast-track @ 4375d08a8)
Inputs: LEAD_ROLE_IMPACT_MAP.md, CONTEXT_FILES_DESIGN.md s10/10f/10g/C1-C7, handover/LEAD.md, roles/*, role_loader.py, lease.py, sync.py, mts_run.py, tasks.py, tests.
Every line ref below was re-read this session. Baseline: the 6 role/doc test files = 99 tests, 15.4 s (pytest, JIS-NB, this session).

## 1. Target design
**Roster 10 -> 7**: `Lead` (operator), `Eagle_Eyes` (operator, interactive screenshots), `1985Artifacts_Guy` (operator, login-bound), `Supervisor`
(wave worker; `You are Supervisor.` stays, test_super_session_doc.py:44 asserts it), `Lab_Guy` (until C7 renames it `Checker`), `Session_Planner`, `Builder` (embedded).
Thinker, Admin_Guy, Pipeliner, MTS_Doctor stop being roles: their files are deleted, their names become Lead aliases.

**`roles/lead.md` core** (always injected by the hook; budget 4000 B CRLF vs 21.5 KB for the 4 files today: thinker 7109, pipeliner 7812, admin 5044, doctor 1589):
1. Header `<!-- role: Lead | version: v1 | token: PENDING | triggers: lead, the lead -->`, line 2 `# Lead: the one session the operator talks to ...`, `Read first:` + `Model` in the first 8 lines (lint, test_role_budget.py:52-58).
2. Talk: design with the operator; every discussion closes per s10b (decision record, raw cards + `fill --note "OPERATOR QUOTE"`, Session_Planner Agent refine, wave = a Supervisor worker session, one line in LEAD.md Discussions).
3. Mode table, one line each; the Lead loads ONE mode when the talk needs it:
   | mode | when | file |
   |---|---|---|
   | think | design, options, cost/ROI, "should we", scans | `roles/lead/think.md` (Thinker body minus Pin, THINKER BLOCK, OPEN_<topic> note) |
   | admin | a question to answer, a decision to record verbatim, a backlog idea, one machine's fault (triage -> card) | `roles/lead/admin.md` |
   | pipeline | desk queue, idle logins/lanes, cards -> refine -> wave | `roles/lead/pipeline.md` (step 1 `lease.py acquire Pipeliner`) |
   | doctor | health, cost, "did the fix really go live" | `roles/lead/doctor.md` = the brief for a one-use Sonnet read Agent (`mts_doctor.py`, REPORT_<date>.md, one card per defect) |
4. Loading: `python scripts/dev/role_loader.py mode <name>` prints the trunk copy and `MODE LOADED: <name> · token x-y · @sha8` (the reply quotes it).
   A role line with an old name (`You are Thinker.`, `Start the Pipeliner.`, ...) or a fallback reason naming its keywords = load that mode first.
   A loaded mode cannot be unloaded: a 3rd mode in one session = rotate (s10g trigger 3), after finishing the open discussion.
5. Rotation (s10c): context >= 150K, 3 discussions closed, or 3 modes loaded -> rewrite LEAD.md, docs ship, `clear_session`; refused -> print `You are Lead.` and stop.
6. Worker use: a brief from another session naming an old role (`You are MTS_Doctor.` from tasks.py audit cards) = run that mode as a worker on the card: no operator talk, no rotation, ship once.

**Doctor rule, reworded for the Lead** (replaces mts_doctor.md:20 "Never build code or tools, edit others' cards, route work, touch a machine"):
"The Lead never builds code, never touches a machine or the live tree, never deploys: code goes to a Builder card, machine work to a desk row or
worker session on that host. Routing is its pipeline job. What doctor mode measured is fixed by someone else (a card), never in the same
discussion, except the Doctor's own guidance-text findings (DEAD-REF, DUPLICATE, MEMORY)." Diagnose-vs-treat stays; "route work" is dropped.

**Stays outside the Lead**: Supervisor (the wave; the Lead never wakes on worker events, s10d.1), Builder, Session_Planner, Eagle_Eyes,
1985Artifacts_Guy, and the Checker (C7: Lab_Guy stamp duties + the diff-only review Agent of SUPER_SESSION Rule 3; never the producer).

**DECISION (OURS): mode files, not `.claude/skills/`.** Evidence: (a) desktop worktree sessions take `.claude/` config from the MAIN checkout,
274 commits behind today (SessionStart notice); a stale main dropped role_loader before (memory hooks-come-from-main-checkout, 2026-10-20);
(b) the one staged skill, `scripts/dev/skill_src/mts-session-handoff`, was never installed: it is absent from this session's skill list, and writes under
`.claude/` were blocked (archive/system_2026-10-15/cli_tasks/2026-10-09_install_handoff_skill.md:3); (c) skills auto-load on description match,
which breaks "one mode at a time"; (d) role_loader serves trunk, so a mode is never older than origin/fast-track. Same lazy cost as skills: only the table is in context.
Mode files live in the subfolder `roles/lead/`, so `glob("*.md")` (role_loader.py:555-557, test_role_roster.py:39, test_role_budget.py:37) never sees them as roles.

## 2. Migration: 3 commits now + 2 existing cards
**K1 `role-loader-mode-command`** (no behaviour change; ships first so K2 can depend on it)
- `role_loader.py`: `mode <name>` subcommand: `git_show` of `roles/lead/<name>.md`, token from `compute_token`, banner line; missing file = `MODE NOT LOADED: <why>`, exit 1 (fail closed).
  For `pipeline`: `mark_injected(sid, "Pipeliner", explicit=False)` with sid = `CLAUDE_CODE_SESSION_ID`. Then `lease.current_role` (lease.py:157-169) returns Pipeliner, so
  `sync.py` lease_guard (sync.py:1336-1350) and desk.py:462 guard ship/claim/desk exactly as for today's Pipeliner; `explicit=False` keeps
  `explicit_injected` = [Lead], so compaction re-injects lead.md, not a missing pipeliner.md (role_loader.py:336-341, 499-505).
- `lint` (role_loader.py:799-929) also scans `roles/lead/*.md` for dead commands and missing files (no header check).
- Tests (same commit, test_role_loader.py): `test_mode_prints_trunk_file_and_banner` (fixture mode file via patched `git_show`), `test_mode_missing_fails_closed`.
**K2 `lead-role-core-and-modes`** (one atomic commit: the roster, headers, KNOWN_ROLES and budget tests bind these files together)
- Add `roles/lead.md` (core above) and `roles/lead/{think,admin,pipeline,doctor}.md` (bodies moved from the 4 files, Boot steps kept, Pin/THINKER BLOCK/
  OPEN-note/Admin "go to Thinker" lines dropped); `role_loader.py retoken lead.md`. Delete `thinker.md`, `admin_guy.md`, `pipeliner.md`, `mts_doctor.md`.
- `ROSTER.json`: one `Lead` entry (start operator, `You are Lead.`, model "Sonnet (Opus when named)", lane SONNET, limit "one at a time; a second reads LEAD.md");
  aliases = every old name and trigger: thinker, thinker_guy, thinker guy, think_guy, think guy, admin_guy, admin guy, q&a_helper, q&a helper, qa helper,
  q and a helper, network_admin_guy, network admin guy, pipeliner, traffic_controller, traffic controller, traffic cop, mts_doctor, mts doctor, doctor;
  keywords/weak_keywords = the union of the 4 old lists (so the best-guess fallback behaves as today, only the name changes).
- `role_loader.py:57-58` NO_ROSTER_NAMES = the 7 names; `SINGLETON_ROLES` stays ("Pipeliner",) = `lease.SINGLETONS` (the lease name, not a roster name).
  Then `role_loader.py render` (ROLES.md, START_HERE.txt tables) and `check`/`lint` exit 0.
- `role_hook_launcher.py:26-27` KNOWN: append `Lead`, keep every old name (old checkouts still trigger the trunk loader).
- `mts_run.py:44` ROLE_FILES: `"Lead": "lead.md", "MTS_Doctor": "lead/doctor.md", "Pipeliner": "lead/pipeline.md"` (today a missing name falls back to builder.md silently, :88).
- `eagle_eyes.md:45` and its Think-mode section: `roles/thinker.md` -> `roles/lead/think.md`, "needs Opus Thinker" -> "needs Opus Lead"; bump to v5 + retoken.
- Tests in the same commit: `test_role_budget.py` BUDGET: drop the 4, add `lead.md: 4000`; new `MODE_BUDGET` for `roles/lead/*.md` (think 7500, pipeline 8000, admin 5200,
  doctor 1800, OURS = today's size + ~5%) checked in the existing fits-test loop; eagle think-mode needles -> `roles/lead/think.md`, `needs Opus Lead`, `| version: v5 |`.
  `test_role_roster.py:63-65` ALIASES asserts -> `rl.ALIASES["Lead"]`; `test_role_loader.py:313` merged-roles test -> `test_old_role_lines_open_lead`;
  delete `test_thinker_role_registered...` (:355), `test_admin_guy_file_carries...` (:339), `test_admin_guy_runs_on_sonnet_everywhere` (:344),
  `AskedWorkRunsNow.test_thinker_no_go_ahead_request` (test_role_roster.py:208-211); add `test_lead_core_and_modes`, `test_pipeline_mode_marks_pipeliner_for_lease`.
  `test_tie_asks_once` ("chart screenshot design options": Eagle_Eyes vs Lead) keeps passing unchanged.
- Left as is on purpose (aliases absorb them, each is test-locked): `tasks.py:1384-1390` (CODEX->Lab_Guy, audit->MTS_Doctor), `supervisor.py:784,866,880,1086`,
  `traffic.py:519,564,638` + `test_traffic.py` "You are Pipeliner", `lease.py`, `system/leases/pipeliner.json`, `traffic_inventory.json:27`, `.claude/settings.json`.
**K3 `lead-docs-and-pages`** (docs + one test; old prompts already work after K2, so this can lag)
- `make_home.py:220-255` recipes -> `You are Lead.` (+ "say think / pipeline / doctor / a decision"); regenerate `system/artifacts/mts_home.html`;
  `test_artifacts.py:181-182` start lines -> the 4 remaining operator starts + Lead.
- `SUPER_SESSION.md` D2: "Thinker stays a separate session" -> "the Lead is the separate session with the operator; it starts this session as its wave
  worker"; D4 unchanged (Session_Planner Agent). test_super_session_doc.py asserts no role name in D2/D4 (verified), so no test change.
- `ROLES.md` "Who does what" line, `TRAFFIC_CONTROLLER.md`, `WORKERS.md:32` (its Thinker exemption names `turn_meter`, which is no longer in scripts/dev: drop the sentence), `ARCHITECTURE.md:82`.
- Republish mts_home via `artifacts.py publish-record` is a 1985Artifacts_Guy desk row, not part of the commit.
**Then (existing cards)**: C7 `checker-role` (Lab_Guy -> `checker.md`, alias Lab_Guy; `supervisor.py:784,866` + `test_supervisor.py:431,537-539`; `tasks.py:1036,1369,1389`
no_stamp text) and C6 `lead-role-and-handover` shrinks to `supervisor.py handover --kind lead` + `--verify` (the role half is K1+K2; depends C4, C2).

**Open decisions answered**
- DECISION (OURS) best-guess fallback (role_loader.py:254-293): KEEP it, with Lead keywords = the union of the 4 merged roles. Zero code, today's behaviour exactly,
  ties inside the merged group vanish. 10f's removal waits for data: delete it (and test_role_roster.py:181-202, test_role_loader.py:182-212, ~9 tests) when
  `context_gap.py measure` (C1) shows 14 days with no fallback banner on an operator session. Removing it now would change what the operator sees.
- DECISION (OURS) aliases: Thinker, Admin_Guy, Pipeliner, MTS_Doctor (and their old aliases) all load Lead; no pointer files (they would fail
  test_role_roster.py:37-45, every roles/*.md must be a roster role). The Pipeliner lease keeps its name and is taken by pipeline mode (K1).

## 3. Do not break (pilot-proven, REPORT_pilots_2026-10-25.md rows 1-8, PILOT1B_NOTES.md) and its one test
| Function | Test (file) | Asserts | Time | Change |
|---|---|---|---|---|
| Worker brief `You are Builder.` behind the app wrapper loads its role | `BootStepTests.test_real_wrapped_briefs_with_text_after_the_name_load` (test_role_loader.py:449) | wrapped brief -> one role | <0.1 s | keep |
| Cross-session briefs get no fallback role (pilot 2026-10-22) | `test_supervisor_brief_gets_no_fallback_role` (test_role_roster.py:193) | Background brief -> "" | <0.1 s | keep |
| Old start lines keep working | `test_old_role_lines_open_lead` (test_role_loader.py, replaces :313) | 13 old prompts -> ["Lead"], `You are Supervisor.` -> Supervisor | <0.1 s | replace |
| Pipeliner singleton lease guards ship/claim/desk | `test_pipeline_mode_marks_pipeliner_for_lease` (test_role_loader.py) | after `mode pipeline`: current_role == Pipeliner, explicit_injected == [Lead] | <0.2 s | new |
| Lead core small, modes load on demand | `test_lead_core_and_modes` (test_role_loader.py) | lead.md <= 4000 B; its mode table names exactly the 4 files in roles/lead/; "ASKED WORK RUNS NOW" in core | <0.1 s | new (absorbs 4 deleted) |
| Mode load fails closed | `test_mode_missing_fails_closed` (K1) | exit 1 + `MODE NOT LOADED` | <0.1 s | new |
| One ship at a time / 2 gate slots (row 2) | existing GATE_SLOTS tests in `scripts/dev/test_sync.py` | unchanged area | - | keep, not touched |
| Lab_Guy stamp before dispatch (no_stamp) | existing `test_tasks.py` needs_review tests | unchanged until C7 | - | keep |
| Session_Planner refine at < 6 ready (D4) + notes file (D5) | `test_super_session_doc.py` (74 lines) | D1-D6 rows, D5 names SUPERVISOR_<L>.md | <0.1 s | keep (verified: no role names asserted) |
| Banner parse / roster render / lint | `test_check_and_lint_exit_zero`, `test_docs_..._render_is_current` (test_role_roster.py) | exit 0, render current | ~2 s | keep |
Net: -5 tests (thinker_registered, admin_guy_file, admin_guy_sonnet, thinker_no_go_ahead, merged_roles) +5 (old_role_lines, pipeline_lease, lead_core_and_modes,
mode_prints, mode_missing) = flat at 99; all new ones in-process (no subprocess), so runtime stays ~15 s. No new file in run_extra_tests.py (it forces the full gate, PILOT1B_NOTES.md:56).
**UNVERIFIED items, now verified**: (1) `tests/docs/test_integrity.py:13-18` SIZE_CAPS = CLAUDE.md, SURFACE_POLICY.md, OPERATOR_INBOX.md, RELAY.md only:
no role file, ROLES.md or START_HERE.txt; no cap change needed. (2) `tests/docs/test_super_session_doc.py` names no role except the `You are Supervisor.`
start block (:44); D2/D4 text can change freely.

## 4. Cards for the Session_Planner (not filed; all live_path false)
| id | title | lane | est_turns | depends_on |
|---|---|---|---|---|
| K1 | role_loader `mode <name>`: print roles/lead/<name>.md from trunk + MODE LOADED banner; pipeline marks Pipeliner (soft) for the lease; lint scans roles/lead/ | SONNET | 12 | - |
| K2 | Lead role: roles/lead.md core + 4 mode files; roster 10->7 with old names as Lead aliases; render; budgets; launcher KNOWN; mts_run ROLE_FILES; eagle_eyes think pointer; tests per LEAD_ROLE_SOLUTION s2 | SONNET | 20 | K1 |
| K3 | Lead docs and pages: make_home recipes + mts_home.html, test_artifacts starts, SUPER_SESSION D2, ROLES.md who-does-what, WORKERS.md:32, TRAFFIC_CONTROLLER.md | SONNET | 8 | K2 |
| C7 | checker-role (existing card; add supervisor.py:880 Pipeliner spawn line -> "Lead: pipeline mode") | SONNET | 10 | K2 |
| C6 | lead-role-and-handover, reduced to `supervisor.py handover --kind lead` + `--verify` (role part done by K1+K2) | SONNET | 12 | C4, C2, K2 |
One editor per file: K1 and K2 both touch role_loader.py and test_role_loader.py, so they run in order, never in parallel.

## 5. Risks not closed
1. Skills-vs-files: not tested whether a worktree session reads `.claude/skills/` from the worktree or the main checkout; files avoid the question, not answer it.
2. A Lead started by "Start the Pipeliner." in a second session gets the lease only at `mode pipeline`; until then two Leads can both talk desk (the lease still blocks the second's ship/claim).
3. Audit cards brief workers as `You are MTS_Doctor.` -> Lead core + doctor mode in a worker; the core's worker rule (s1 item 6) is prose, no test enforces it.
4. The fallback now injects 4 KB Lead core where it injected Thinker/Admin/Pipeliner/Doctor; whether the mode hint from the fallback reason is followed is NOT_IN_DATA until C1 measures modes per session.
5. Mode budgets are OURS (today's size + 5%); moving bodies without trimming keeps one think+pipeline session at ~19 KB, so the rotation trigger (3 modes) is the only cap.
