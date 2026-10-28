# MTS-2026-10-04-0538Z-CLI-BLD-b072-b073-math-object
surface: CLI
host: DESKTOP-F7IU69N
account: none
model: claude-sonnet-5-5
role: BLD
branch: fast-track
branch_alias: none
predecessor: none
lanes: none
started: 2026-10-04 05:38Z
ended: 2026-10-04 06:10Z
status: closed
commits: B072+B073 (grep the commit subjects)
handoff: none
## Notes
- B072: build_math_object raises ValueError unless current_price is a finite number > 0 (bool rejected); build_mo_cli.py turns it into exit 1.
- B073: gross_rr and net_rr rounded to 4 dp first, rr_sanity computed on the rounded gross_rr.
- Backup runtime/math_object_builder.py.pre_b072_b073 (gitignored). Fail-first run on a scratch copy of the tree with the pre file: 11 fail (10 B072 cases + 1 B073), new file 49 pass.
- Gate: run_all_tests --quick fails only step 4 test_2_no_forbidden_refs (B091 docs and an earlier session record contain a forbidden git phrase); not touched here. Build-Check STATUS FAIL from B102 and B103 (no items file, not in INDEX), not these items.
- Deviations: Build-Check run twice (second run to read the failure lines); item doc cites no row set, so the 72-row 2 dp check was not reproducible; Java 2 dp rounding residual.
