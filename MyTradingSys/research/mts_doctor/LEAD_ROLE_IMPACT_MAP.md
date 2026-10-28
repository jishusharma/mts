# Lead role: impact map (read-only Agent, 2026-10-25, for the Opus solution session)
Question: fold Thinker, Admin_Guy, Pipeliner, MTS_Doctor, Lab_Guy duties into one Lead (core + skills, CONTEXT_FILES_DESIGN.md s10, s10g, cards C6, C7) without breaking what works. Line numbers were read once by the Agent; re-verify before editing.

## Riskiest (a coordinated edit is needed)
1. Roster = role headers = KNOWN_ROLES = no-roster fallback = generated tables: `MyTradingSys/tests/test_role_roster.py:35-45,69`; `scripts/dev/role_loader.py:57-59`. Edit `roles/ROSTER.json`, `NO_ROSTER_NAMES`, run `role_loader.py render`, one commit.
2. Byte budget for every `roles/*.md`, file-name set checked for equality: `MyTradingSys/tests/test_role_budget.py:13-16,37-38`. New `lead.md` fails until BUDGET has it.
3. Eagle_Eyes think-mode test asserts text `roles/thinker.md` and "PENDING OPERATOR: needs Opus Thinker": `test_role_budget.py:62-71`. Keep `thinker.md` as a pointer, or change test + `eagle_eyes.md` together.
4. `lease.py:47` Pipeliner is the only singleton (desk, `sync.py ship`, `sync.py claim`); 46 test hits: `role_loader.py:62`, `test_role_loader.py:334`, `test_lease.py`, `test_runner_lease_env.py:14-40`, `system/leases/pipeliner.json:12`, `system/traffic_inventory.json:27`. Keep the name Pipeliner for the lease; the pipeline skill takes it.
5. Role linter (header, "Read first:" in first 8 lines, dead commands, missing files): `role_loader.py:799-929`, `preship.py:42,79-82`, `test_preship.py:156-173`, `test_role_lint.py`. `lead.md` needs the full header; run `role_loader.py retoken lead.md` and `lint`.

## Others
- Hooks `.claude/settings.json:34,60` name only `role_loader.py hook`; `test_hook_settings.py:41` (must stay synchronous). No change.
- Old-checkout launcher `scripts/dev/role_hook_launcher.py:26-27` has its own KNOWN list; `test_role_hook_launcher.py:15-60`, `test_role_loader.py:372`. Append `Lead`, keep old names (else "ROLE NOT LOADED").
- CI `.github/workflows/ci.yml:18` already covers `roles/**`.
- Best-guess role fallback: `role_loader.py:254-293`; tests `test_role_roster.py:181-202`, `test_role_loader.py:182-212`. Design 10f removes it; remove with tests in one commit, or give Lead keywords.
- ~31 assertions name roles: `test_role_loader.py:316-334,339-352,355-372,443-454` (Thinker triggers `thinker_guy`/`think_guy`, `ROLES.md` row, "You are Thinker." in `START_HERE.txt`, Admin_Guy file content/Sonnet model).
- Card->role: `scripts/dev/tasks.py:1369,1384-1390` (CODEX->Lab_Guy, audit->MTS_Doctor), `test_builder_role.py:61-80`, `test_tasks.py:987-995`; C7 must update `tasks.py:1036` and `roles/lab_guy.md`.
- Worker role files: `scripts/dev/mts_run.py:44` ROLE_FILES (missing name falls back to builder.md silently). Add Lead, Checker.
- Supervisor: `supervisor.py:567,784,866,880,1086`; `test_supervisor.py:431,537-539` (asserts "Pipeliner"/"Lab_Guy" not in action text; Lab_Guy NUC-only rule). C7 edits `:784`,`:866` + test together.
- Traffic: `traffic.py:329,519,541,564,638`, `test_traffic.py:93-142` assert "You are Pipeliner". Keep text.
- Operator pages: `make_home.py:220-251`, `test_artifacts.py:181-182` (ten "You are X." lines), `system/artifacts/mts_home.html:118`. Regenerate with make_home.py.
- UNVERIFIED: which files are in `MyTradingSys/tests/docs/test_integrity.py` SIZE_CAPS (13-19,175-184; ROLES.md, START_HERE.txt hold generated tables); `SUPER_SESSION.md:12-14` D2/D4 and `tests/docs/test_super_session_doc.py`.

## Doctor rule and report
"Build code or tools, edit others' cards, route work, touch a machine" = `roles/mts_doctor.md:20` (machine work routed to Admin_Guy at `:7`). Prose only, no test enforces it; `lead.md` must reword it. Report path `research/mts_doctor/REPORT_<date>.md` written by `scripts/dev/mts_doctor.py:7,19,159,190`, named in `system/MTS_DOCTOR.md:8`, `roles/mts_doctor.md:15`, `ANNOUNCEMENTS.md:68`; keep it. `test_mts_doctor.py` imports `mts_doctor` (assertions not read).

## Pilots
Context-files pilots read git cherry, `get_usage`, `handover/SUPERVISOR_C.md`, transcripts; no role files/roster/role_loader. See `PILOT_super_session_2026-10-24.md`, `PILOT1_CARDS.md`, `PILOT1B_NOTES.md`, `REPORT_pilots_2026-10-25.md` (Pilot 3 preconditions at :34). NOT_FOUND on trunk: `context_gap.py` (C1), `supervisor.py handover --kind lead/--verify` (C6), `roles/lead.md`, `.claude/skills/` (only `scripts/dev/skill_src/mts-session-handoff` exists).
