# Manifest-freeze fix: independent completion verification

**DONE / MATCH.** The implementation already shipped in `f068fd95ff5e`; the task remained open. This session verified the current code and acceptance suite and closed the stale card. No product code or frozen research artifact was changed.

- `screen.py:274-286`: manifest creation returns without overwriting an existing baseline.
- `screen.py:289-318`: check_manifest compares the exact filename set and SHA256 per file, raises SystemExit naming the difference, and returns rows only after matching. Missing baseline is created once.
- `screen.py:403`: main calls check_manifest before loading/analysing the input bars.
- `test_screen.py:149-215`: matching hashes, changed content, extra/missing files and frozen-manifest byte preservation are covered using temporary files. The original delivery report `2026-10-18_gross-screen-refuse-a-changed-data-manif.md` records the pre-change red run of the three manifest tests; this session added no tests requiring a new implementation red run.

Validation:

```
python -m pytest MyTradingSys/research/gross_effect_screen_2026-10-15/test_screen.py -q
```

**13 passed in 2.70 s.** SHA256 snapshots before/after prove all four protected files (`DATA_MANIFEST.csv`, `ledger.csv`, `RESULT.md`, `PRE_REG.md`) byte-identical. The frozen manifest has 31 lines, SHA256 `39795d9f9c4ac550e4144e09027ccb453ec46bcd108202182052aa05cca4b099`. Only its bytes/count were inspected; no archived outcome values were read.

No `--full` study rerun or raw-market-data read was performed. The test suite's planted/flat fixtures are synthetic. The later upstream implementation has one more test than the older 12-test delivery report; current verification uses the actual 13-test result.
