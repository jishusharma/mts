# BLOCKED - Tom profile shape parity (2026-10-13, JIS-NUC)

## What was checked

- Read the authorized dev frames from `F:/MTS/data/tom_videos/frames/`: `n7ZSkjb7JXs_0314.jpg` (T1, 1280x720) and `k0zm5NYn0IQ_0280.jpg` (T2, 1280x720), using Pillow 12.3.0. No 2026-04-11-or-later frame or bar data was opened.
- Read `MyTradingSys/research/tom_transfer_2026-10-11/PROFILE_PARITY_T1.json` and `_T2.json`; computed levels are T1 VAL/POC/VAH 24280.70/24314.70/24333.40 and T2 25066.69/25078.14/25123.94.
- T2: axis ticks show 25070-25370; widest histogram row is approximately y=357-365 px, around price 25220. `f_drawn ~= (25220-25070)/(25370-25070) = 0.500`. Computed `f_computed ~= (25078.14-25066.69)/(25123.94-25066.69) = 0.200`. Difference ~=0.300; one drawn row is approximately 8/570 = 0.014 of visible height. T2 is MISMATCH. Pixel boxes and values are recorded in `PROFILE_PARITY.md:107-110`.
- T1: the relevant DAX chart is the lower-left panel (approx chart box x=18-535, y=360-695). Histogram rows are visible at its right edge, but axis endpoint labels are too small/obscured in this 1280x720 frame to read reliably. Visible range, row price, and `f_drawn` are NOT_IN_DATA. See `PROFILE_PARITY.md:107`.

## Findings

| Severity | Evidence | Finding | Disposition |
|---|---|---|---|
| HIGH | `F:/MTS/data/tom_videos/frames/n7ZSkjb7JXs_0314.jpg`; `PROFILE_PARITY.md:107`; `TOM_LAYER_V2_SPEC.md:341` | Axis endpoints cannot be read reliably at source resolution, so T1 `f_drawn` cannot be calculated. Both frames are required. | T1 = NOT_IN_DATA; overall PROFILE arm = NOT_IN_DATA. A higher-resolution T1 frame or readable axis evidence is required. |
| HIGH | `F:/MTS/data/tom_videos/frames/k0zm5NYn0IQ_0280.jpg`; `PROFILE_PARITY.md:108`; `PROFILE_PARITY_T2.json` | T2 drawn fraction ~=0.500 vs computed ~=0.200, a difference ~=0.300 versus row tolerance ~=0.014. | T2 = MISMATCH. |
| LOW | `MyTradingSys/tests/test_tom_profile_parity.py:19-27` | Requested synthetic parity and mismatch cases are implemented. | `python -m pytest MyTradingSys/tests/test_tom_profile_parity.py -q`: 4 passed; pytest emitted a cache-path warning (WinError 183). |

## Verdict

**BLOCKED** - T1 axis data is unreadable in the supplied frame, so the mandatory two-frame decision cannot be completed. Per the card's unreadable rule and `TOM_LAYER_V2_SPEC.md` section 12, **PROFILE arm on DAX = NOT_IN_DATA**. T2 alone is a mismatch and cannot turn the two-frame result into PASS. No offset fitting, outcome tuning, holdout data, BTC run, or live-tree work was done.

No follow-up card was created. The task card was not marked done because T1 evidence is missing.
