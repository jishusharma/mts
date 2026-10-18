# G3 trend-line marking pack (built 2026-10-17, card trendline-g3-marks-pack)

Status: READY TO MARK, no mark exists. Marking is the operator's (reader 1) and a blind Sonnet subagent's (reader 2); this pack does not contain or fake any mark. 40 blind windows over 2 units (TL-4H, TL-1D, 20 each). Definitions: `../../layer_rebuild_2026-10-15/READER_PROTOCOL.md` section 4 (read it first). Question per window: is there an obvious legitimate trend line? Purpose: a reproducibility number (Cohen kappa between readers) for the "obvious line" concept that `../TRENDLINE_CONTRACT.md` P8 defers to this pack.
Data rule: DEV only. 4h bars are built from the 1m store `F:/MTS/data/tom_raw/klines` 2022-01-01..2024-06-30; 1d bars from daily klines 2020-01-01..2024-06-30 (first right edge 2021-03-01). The loaders cannot open a later file or bar (test_dev_fences_never_read_later_data). Exposure line: `EXPOSURE_LEDGER_LINE.csv` in this folder.

## Files
| file | what | who may open |
|---|---|---|
| `WINDOWS.csv` | window id, row, timeframe, bars shown, right edge (UTC), seed | builders only (it holds dates; the charts do not) |
| `MARKING_SHEET_reader1_operator.csv`, `MARKING_SHEET_reader2_claude.csv` | one blank row per window: obvious_line, side, anchor_offsets, note | each reader their own |
| `ANSWER_KEY_CLOSED/KEY.csv` | per-window selection record and dates. sha256 `26048af789efabb1082b419051dc64104dfdc8d7ed1d10be73ff8a647391bda9` (recorded before any mark exists) | nobody until both sheets are committed |
| `ANSWER_KEY_CLOSED/SELECTION_RULES.md` | how windows were chosen | closed with the key |
| `g3_pack.py`, `render_png.ps1`, `test_g3_pack.py` | generator, selection code, chart geometry, GDI+ renderer, 7 tests | |
| charts (not in git) | `F:/MTS/data/g3_trendline_pack_2026-10-17/charts/<window_id>.png`, rebuilt by `python g3_pack.py draw` | readers |

## Blindness (same fixes as g3_marks_2026-10-16, applied from the start)
Ids are `<unit>-NN` with a shuffled number; charts show offsets from the right edge, never a date or clock time; every chart has the same panels (candles, volume) and no overlay, so nothing drawn depends on how a window was chosen or on any bar after the right edge (tests: no_bar_after_the_decision_bar, chart_is_blind_and_independent). The selection rule is only in the closed key folder.

## How to mark
1. Open the PNG; fill your own sheet: `obvious_line` YES or NO; if YES `side` SUPPORT / RESISTANCE / BOTH and `anchor_offsets` (e.g. `-118;-64;-19`). No outcomes are visible and none may be guessed.
2. Reader 1 = the operator (about 10 s a window, about 7 min for 40).
3. Reader 2 = a Sonnet subagent given only: the PNG paths, READER_PROTOCOL.md section 4. It must not be given WINDOWS.csv, the key folder, reader 1's sheet or any date. It writes `MARKING_SHEET_reader2_claude.csv`.
4. When both sheets are committed (`git cherry` empty), open the key and write `G3_TRENDLINE_REPORT.md`: yes-rate per reader per unit and per half, Cohen kappa (undefined stays "undefined"), disagreeing windows. Kappa below 0.4 means "obvious" is not reproducible: the contract's obvious-swing step stays an eye-read and is not mechanised.

## Decisions (OURS, logged)
- 2 units, 20 windows each (10 + 10), not 30: 40 windows keep the operator's pass under 10 minutes; the extension rule of the G3 brief covers a low positive count.
- 4h (200 bars) and 1d (180 bars) only: the contract's 1h line TF is the least powered cell and a 1h chart of 200 bars hides the structure a reader judges.
- Charts carry no volume average, no indicator, no grid beyond % axis: the question is about price geometry.
- Seed 20261017, per unit `<seed>-<code>`; windows of a unit are at least 40 (4h) / 20 (1d) bars apart.

Reproduce: `python g3_pack.py counts | build | draw` (build rewrites WINDOWS.csv and the key; the key sha must stay unchanged once marking starts).
