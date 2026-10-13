# BLOCKED - Tom profile shape parity

## What was checked

- Read `MyTradingSys/backtest/tom_profile_parity.py` and its existing tests; added normalized shape helpers and a synthetic regression case.
- Read computed development profile JSON: T1 POC/VAL/VAH 24314.70/24280.70/24333.40; T2 25078.14/25066.69/25123.94.
- Inspected only approved frames `F:/MTS/data/tom_videos/frames/n7ZSkjb7JXs_0314.jpg` and `k0zm5NYn0IQ_0280.jpg` with Pillow 12.3.0 (1280x720). T2's axis and widest histogram row are readable; T1 is a multi-panel frame with compressed/obscured axis labels, so exact visible endpoints and a row-height normalized threshold cannot be established.
- Updated `MyTradingSys/research/tom_transfer_2026-10-11/PROFILE_PARITY.md`; it records T1 NOT_IN_DATA, T2 estimated shape fractions and the required overall verdict.

## Findings

| Severity | Evidence | Finding | Proposed resolution |
|---|---|---|---|
| HIGH | `PROFILE_PARITY.md` shape table; T1 frame axis endpoints unreadable | NOT_IN_DATA: required T1 visible range cannot be recovered at the precision needed for a one-row comparison. Thus both-frame PASS/FAIL cannot be decided. | Re-read T1 from a higher-resolution/source frame with legible axis labels. |
| MED | `PROFILE_PARITY.md` T2 row; estimated f_drawn ~0.500 vs f_computed ~0.200, row fraction ~0.014 | MISMATCH on T2 based on approximate pixel boxes; not sufficient to override the required two-frame verdict. | Confirm with source-resolution pixel bounds if T1 evidence becomes available. |
| LOW | `MyTradingSys/backtest/tom_profile_parity.py` new `profile_shape_fraction` and `profile_shape_matches`; `MyTradingSys/tests/test_tom_profile_parity.py` synthetic test | MATCH: 0.40 vs 0.40 within 0.033; MISMATCH: 0.40 vs 0.60. | None. |

## Verification

- Red first: `python -m pytest MyTradingSys/tests/test_tom_profile_parity.py -q` failed during collection because `profile_shape_fraction` did not exist.
- After implementation: `python -m pytest MyTradingSys/tests/test_tom_profile_parity.py -q` -> 4 passed (one pytest cache warning due to pre-existing cache path collision).

Task status: BLOCKED by missing readable T1 axis evidence. Per instruction, the task card is not marked done.
