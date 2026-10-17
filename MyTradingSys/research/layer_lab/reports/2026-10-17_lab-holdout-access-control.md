# Lab holdout access control

BLOCKED — implementation and tests are complete, but task completion is gated on an independent reviewer stamp.

Build result: changed `scripts/dev/lab_flow.py` and `scripts/dev/test_lab_flow.py`; `pytest -q scripts/dev/test_lab_flow.py --basetemp F:/MTS/mts-codex-lab/.pytest-tmp -p no:cacheprovider` — **25 passed**.

## What changed

- `scripts/dev/lab_flow.py:15,49-87`: `safe_file` checks data inputs by content, reading the `t` axis in NPZ files and `t`/`open_time`/`timestamp` columns in CSV files and CSV members of ZIP files. A maximum open time at or after 2024-07-01T00:00:00Z raises `ValueError` before the caller can fingerprint or analyze the input. Missing timestamp axes in supported market formats fail closed.
- `scripts/dev/test_lab_flow.py:222-238,250-258`: the fingerprint fixture uses a valid DEV CSV; the renamed NPZ copy with one post-cutoff timestamp asserts refusal.
- Fail-first evidence: before the guard, `pytest ... -k renamed_dev_copy_with_post_cutoff_bar_is_refused` reached its assertion and failed because `safe_file` accepted the file. With the guard, the full test file passes.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:49-87`; `scripts/dev/test_lab_flow.py:250-258` | A renamed/copy data file carrying a post-cutoff candle is rejected by its timestamp, regardless of its name. | MATCH |

## Blocker

`python scripts/dev/tasks.py done lab-holdout-access-control --result "25 passed; MyTradingSys/research/layer_lab/reports/2026-10-17_lab-holdout-access-control.md"` was refused: `weight/class needs review: add 'REVIEWED: <reviewer> <date>' to the note first`. The card note requires Gemini Argon high, Haiku re-derive, and a second vendor on first use. No independent reviewer stamp is present, so the card was not marked done.

## Limit

Timestamp extraction is implemented for the market data containers used by the lab (`.npz`, `.csv`, and CSV-in-ZIP). Other data-root file extensions do not receive a timestamp check in `safe_file`.
