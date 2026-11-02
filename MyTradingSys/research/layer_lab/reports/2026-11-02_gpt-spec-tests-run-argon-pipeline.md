# Spec tests for `run_argon_pipeline.py`

**8 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_run_argon_pipeline.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/run_argon_pipeline.py` lines 1-293. Audited pure evaluation helpers `flash_counts`, `trials_headline`, and `generate_report` without external CLI or model invocations.
- Branches covered:
  - `flash_counts`:
    - Safely skips items missing `flash_parsed` attribute or empty items without raising exceptions.
    - Accurately converts input items to pseudo-evaluations and scores matches, mismatches, and field mappings against truth values.
    - Correctly scores and classifies invented numbers (where truth is null but model returned a numeric value) and correct nulls.
  - `trials_headline`:
    - Assembles the standardized trial ledger headline incorporating 7-frame field totals, match/mismatch/null metrics, Flash comparison figures, and contested crop notes.
    - Dynamically reflects changes in count dictionary values.
  - `generate_report`:
    - Automatically creates missing parent directories for the output Markdown report path.
    - Formats all 6 report sections (`Headline Numbers and Verdict`, `What was Run`, `Comparison Table`, `Enlarged Crop Transcriptions`, `Findings & Defect Ledger`, `Follow-up Cards`).
    - Populates the comparison table rows with per-field scoring status and notes.
    - Integrates enlarged crop raw descriptive transcripts for contested target and stop regions.
- `python -m pytest scripts/dev/test_run_argon_pipeline.py -v`: **8 passed in 0.34s**.
- Scratch mutations on temporary copies:
  - M1: Broke `flash_counts` truth mapping (`"truth": {}`) (**2 failed, 6 passed**; caught by `test_flash_counts_scoring_accurately` and `test_flash_counts_invented_and_correct_null`).
  - M2: Omitted the Flash comparison string in `trials_headline` (**2 failed, 6 passed**; caught by `test_trials_headline_format` and `test_trials_headline_dynamic_counts`).
  - M3: Omitted crop descriptive response in `generate_report` (**1 failed, 7 passed**; caught by `test_generate_report_includes_crop_descriptions`).
- Audited source unchanged: SHA-256 of `scripts/dev/run_argon_pipeline.py` is `081928c7f760564710e903b8ce7b97275135423fef0411b898336fff6c61169d`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/run_argon_pipeline.py:130-255` | MATCH | Pure evaluation and report generation functions match docstring rules and reporting format. Source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:190` | MATCH | Registered `scripts/dev/test_run_argon_pipeline.py` into extra test runner. | None. |

## Follow-up cards

None.
