# RV05 H2 position-line adjudication

## Read protocol and outcome

`RV05_H2_READS.csv` was created before opening `FABIO_TRADE_LEDGER.csv` or the RV05 ledger table. It contains all 10 required row-field readings, with `NULL` for every value because no target frame could be decoded. Requested video times were F8 1325s, F12 3100s, F12-m2 3150s, F13 3375s, F13-m1 3400s. OpenCV reported 1280x720, 25 fps, 212,493 indexed frames, but sequential `VideoCapture.read()` stopped at frame 11,243 (449.72s) with AV1 `Corrupt frame detected / Failed to decode tile data`. The targets are beyond that point. Random seeking also failed (read returned false; position reported frame 146). No full-resolution visual claims are made.

## Field status table

Frame times are the requested chart/video times. Since each blind reading is NULL, all ten adjudications are `NOT_IN_DATA` for this pass. The known prior disagreements below remain unresolved; they do not become settled by the failed read.

| Row | Field | frame_t (s) | blind read | Status |
|---|---|---:|---|---|
| F8 | entry | 1325 | NULL | NOT_IN_DATA |
| F8 | stop | 1325 | NULL | NOT_IN_DATA |
| F12 | entry | 3100 | NULL | NOT_IN_DATA |
| F12 | stop | 3100 | NULL | NOT_IN_DATA |
| F12-m2 | entry | 3150 | NULL | NOT_IN_DATA |
| F12-m2 | stop | 3150 | NULL | NOT_IN_DATA |
| F13 | entry | 3375 | NULL | NOT_IN_DATA |
| F13 | stop | 3375 | NULL | NOT_IN_DATA |
| F13-m1 | entry | 3400 | NULL | NOT_IN_DATA |
| F13-m1 | stop | 3400 | NULL | NOT_IN_DATA |

No CSV cell is changed by this audit; CHANGED count from this adjudication is 0. A `git diff`/HEAD comparison was not run because the task instruction prohibits git. `F:/MTS/data/fabio_videos/DyS79Eb92Ug.f398.mp4` remains the source required by the card; no alternate video or low-resolution sheet was substituted.

## Independent arithmetic cross-checks

The entry reconstruction is `stop + |STP dollars| / (contracts x $20 per point)`. These are independently recomputed from the visible-label quantities and the declared NQ multiplier; they are not asserted as position-line reads. The layer `FORMULAS.md` does not define this ledger's NQ label arithmetic (it covers indicator, crypto layer, metrics and execution rounding formulas), so it supplies no alternate expected frame prices here.

| Row | Inputs | Recomputed label-derived entry | Comparison / issue already recorded in ledger |
|---|---|---:|---|
| F8 | 25021.75 + 2040/(8x20) | 25034.50 | displayed average recorded 25034.53; difference 0.03 pt |
| F12-m2 | 25098.25 + 2050/(10x20) | 25108.50 | row stop 25098.75 implies 1950 dollars at 10x20; 100 dollar gap |
| F13 | 25097 + 1520/(8x20) | 25106.50 | recorded position-line average 25108.90 differs by 2.40 pt; at 8x20 that average implies 1904 dollars, 384 above label |
| F13-m1 | 25097 + 1760/(8x20) | 25108.00 | label covers 8 while 10 are open; using 10 would give 25105.80, a 2.20 pt denominator effect |

F13 partial coverage is 8 covered versus 10 open; its daily P/L change is 20,668 - 17,758 = 2,910 dollars, 1,150 more than the -1,760 stop label. These arithmetic checks do not identify the execution cause. The default that a displayed position-line average outranks a label-derived value is OURS, per the card; it cannot be applied as a new cell value without the required readable evidence.

## Findings

1. **HIGH ? `MyTradingSys/research/lab_guy/specs/rv05-h2-position-line-evidence.md:7` and `F:/MTS/data/fabio_videos/DyS79Eb92Ug.f398.mp4:frame 11,243`.** The required full-resolution source is undecodable past 449.72s, before every requested time (1,325?3,400s), so no blind position-line or stop reading can be made. Reproduce with `python MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/extract_frames.py`; OpenCV stops at frame 11,243 with AV1 corrupt tile data.
2. **HIGH ? `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md:110-114, 181-192`.** The already-published evidence has unresolved competing entry/stop interpretations: F12-m2 label-derived stop 25098.25 vs row stop 25098.75; F13 derived entry 25106.50 vs recorded displayed average 25108.90; F13-m1 label quantity 8 vs open quantity 10. The computations above reproduce the mismatches. These rows cannot be fully adjudicated with this source failure; no CSV value was changed.
3. **MED ? task brief step 2 / desk handoff requirement (`python scripts/dev/tasks.py brief rv05-h2-position-line-evidence`).** The three named contested cases require one non-Claude blind DSA-NUC read and a desk row id. A desk row was not posted because it would write outside the only permitted output directory. No desk row id can truthfully be reported.

## Verification

- `python -m pytest MyTradingSys/research/fabio_transfer/test_ledger_audit.py -q -p no:cacheprovider`: 18 passed.
- Required `check_rv05_h2.py` is not present in the permitted output directory, and creating it under `research/fabio_transfer/` would violate the write boundary.
- The required status table, ledger edits, CONTESTED desk row ids, and CSV updates cannot be completed from NULL reads. No `tasks.py done`, git, sync, push, cherry, or ls-tree commands were run.
