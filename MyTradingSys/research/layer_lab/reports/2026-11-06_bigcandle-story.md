# bigcandle_story study.py spec tests (2026-11-06)

Test: `MyTradingSys/research/bigcandle_story_2026-11-05/test_study_spec.py` (6 tests, written from the study.py docstring and PRE_REG.md; expected values computed independently, constants are OURS per PRE_REG).

- Trunk: `python -m pytest MyTradingSys/research/bigcandle_story_2026-11-05/test_study_spec.py -q` -> 6 passed.
- Mutation 1 (copy of study.py in a temp dir, source untouched): `tt_class` line 54 `abs(pos_rel) < TT_FLAT or abs(acc_rel) < TT_FLAT` -> `<=` (PRE_REG: "|change| < 0.2 % = FLAT"). Result: 1 failed (`test_tt_class_flat_band_is_strict_and_symmetric`), 5 passed.
- Mutation 2: `outcomes` line 253 undone `(cf - o_start) * sgn < 0` -> `> 0`. Result: 1 failed (`test_outcomes_continue_and_undone_by_direction`), 5 passed.
- Covered: constants, tt_class boundary, Wilson 95 % hand values (5/10 -> 0.2366..0.7634), trailing_z prior-bars-only and 80 % validity, outcomes continue/undone by direction and off-data None.
- Not covered: load/IO, walkthrough text, JS output.
