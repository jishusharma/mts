# Gross-effect screen: refuse changed data manifest (audit fix)

Resolution for GPT audit finding MED (`MyTradingSys/research/layer_lab/reports/2026-10-15_gross-screen-gpt-audit.md:32`).

## Findings & Changes

1. **check_manifest implementation** ([`screen.py`](file:///F:/MTS/gq/gross-screen-refuse-a-changed-data-manif/MyTradingSys/research/gross_effect_screen_2026-10-15/screen.py#L270-L305)):
   - SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-15_gross-screen-gpt-audit.md:32`
   > "manifest(files) calculates the current hashes and overwrites DATA_MANIFEST.csv before load_dev runs. It never compares the inputs with the already-frozen manifest."
   - Implemented `check_manifest(files, path=None)`: validates the exact set of file names and per-file SHA256 hashes against stored rows in `DATA_MANIFEST.csv`. If any mismatch or extra/missing file is found, it raises `SystemExit` naming the file.
   - Preserves frozen manifest on refusal or mismatch.
   - `manifest(files, path=None)` only writes the manifest file if it does not already exist.

2. **Wiring in main()** ([`screen.py`](file:///F:/MTS/gq/gross-screen-refuse-a-changed-data-manif/MyTradingSys/research/gross_effect_screen_2026-10-15/screen.py#L385-L390)):
   - Replaced `rows = manifest(files)` with `rows = check_manifest(files)`.

3. **Tests added in test_screen.py** ([`test_screen.py`](file:///F:/MTS/gq/gross-screen-refuse-a-changed-data-manif/MyTradingSys/research/gross_effect_screen_2026-10-15/test_screen.py#L134-L203)):
   - Tested using tempfile dirs only (never modifying the frozen baseline manifest).
   - `test_manifest_matches_pass`: checks that matching file names and sha256 hashes pass and leave manifest intact.
   - `test_manifest_refuses_changed_input`: checks that 1 changed byte in a file raises `SystemExit` naming the file and leaves manifest bytes untouched.
   - `test_manifest_refuses_file_set_change`: checks that extra or missing files raise `SystemExit` and leave manifest bytes untouched.
   - Verified fail-on-old-code requirement: all 3 tests failed on the unmodified `screen.py` with `AttributeError` (OURS: command `python -m pytest MyTradingSys/research/gross_effect_screen_2026-10-15/test_screen.py -k "test_manifest"` exited code 1 with 3 failed).

4. **Verification & Done When**:
   - `python -m pytest MyTradingSys/research/gross_effect_screen_2026-10-15/test_screen.py -q`: 12 passed (9 existing + 3 new tests pass) (OURS: command output `12 passed in 91.78s`).
   - `git diff MyTradingSys/research/gross_effect_screen_2026-10-15/DATA_MANIFEST.csv`: empty diff (OURS: 31 data rows + 1 header row = 32 lines / 31 data lines unchanged).
