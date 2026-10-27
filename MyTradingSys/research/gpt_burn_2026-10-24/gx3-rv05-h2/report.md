# GPT audit: rv05-h2-position-line-evidence

## Outcome

I ran `python scripts/dev/tasks.py brief rv05-h2-position-line-evidence` and followed the blind-read order. `RV05_H2_READS.csv` was written first, with 10 row-field entries and `NULL` for every value. Only after that did I read the existing CSV and ledger table.

The required 1280x720 video could not be decoded to any target. OpenCV `VideoCapture` reports 25 fps / 212,493 frames, but sequential decoding stops at frame 11,243 (449.72s) with an AV1 corrupt tile error. Targets are at 1,325, 3,100, 3,150, 3,375 and 3,400 seconds. Seek attempts also fail. So all ten field statuses in `ledger_adjudication.md` are `NOT_IN_DATA`, not guessed readings.

Independent arithmetic checks in `ledger_adjudication.md` recompute the stop-label-derived entries using `stop + |STP dollars| / (contracts x $20/point)`. The NQ multiplier and prior label examples are documented in the Fabio ledger; the layer `FORMULAS.md` does not define these NQ futures labels. Results: F8 25034.50; F12-m2 25108.50; F13 25106.50; F13-m1 25108.00 when denominator is the 8 lots covered by its stop label. The audit does not promote these derived numbers to position-line readings. F13 remains 8 covered versus 10 open; 20,668 - 17,758 = 2,910 dollars, or 1,150 above the -1,760 label.

## Findings

- **HIGH ? `MyTradingSys/research/lab_guy/specs/rv05-h2-position-line-evidence.md:7`; `F:/MTS/data/fabio_videos/DyS79Eb92Ug.f398.mp4:frame 11,243`.** The required source fails before all requested times. Reproduce with `python MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/extract_frames.py`; it stops at frame 11,243 with `Corrupt frame detected / Failed to decode tile data`.
- **HIGH ? `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md:110-114,181-192`.** Existing readings and label-derived values conflict: F12-m2's 25098.25 label tie versus 25098.75 row stop; F13's 25106.50 recomputation versus 25108.90 displayed average; F13-m1 uses an 8-lot label while 10 lots are open. Independent computations above reproduce these gaps. No cell was changed.
- **MED ? task brief step 2, returned by `python scripts/dev/tasks.py brief rv05-h2-position-line-evidence`.** It requires a non-Claude blind DSA-NUC read and a desk row id for contested cases. Posting that row would write outside the user-authorized directory, so it was not posted; no id is claimed.

## Verification and scope

- `python -m pytest MyTradingSys/research/fabio_transfer/test_ledger_audit.py -q -p no:cacheprovider`: **18 passed**.
- The required `fabio_transfer/check_rv05_h2.py`, ledger edits, CSV changes and DSA desk handoff were not made because user instructions restrict all writes to this report directory. A git HEAD comparison, task completion, git, sync, push, cherry or ls-tree command was not run.
- Files created here: `RV05_H2_READS.csv`, `extract_frames.py`, and `ledger_adjudication.md`. No frame crops were successfully produced.

Result: BLOCKED - unreadable source prevents blind adjudication; 10 NULL reads recorded and existing ledger tests pass (18/18).
