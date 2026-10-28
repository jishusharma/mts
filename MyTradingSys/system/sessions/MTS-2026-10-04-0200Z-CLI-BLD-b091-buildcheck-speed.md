# MTS-2026-10-04-0200Z-CLI-BLD-b091-buildcheck-speed
surface: CLI
host: DESKTOP-F7IU69N
account: none
model: claude-sonnet-5-5
role: BLD
branch: fast-track
branch_alias: none
predecessor: none
lanes: none
started: 2026-10-04 02:00Z
ended: 2026-10-04 02:40Z
status: closed
commits: the one tagged B091
handoff: none
## Notes
- Chosen fix: (A) -Quick and (B) -ReadOnly, plus (D) cicd_run.py build-check step passes both (stage 2.3 already runs math tests itself).
- Build-Check never wrote session_log.json; only BUILD_REPORT.md. -ReadOnly removes that write.
- Build-Check now exits 1 on STATUS FAIL (was always 0).
- Backup scripts/Build-Check.ps1.pre_b091 (gitignored, not committed).
- Gate: run_all_tests.py --quick PASS; Build-Check -ReadOnly full tier: compile/math 240/240/docs PASS, STATUS FAIL from another session's B102 (no items file), not B091.
- Deviation: first test draft recursed (Build-Check full runs the suite that calls Build-Check); killed only the _bc_/test_b091 processes, added B091_NESTED guard.
