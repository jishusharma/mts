# Trend-line G3 marking pack (built 2026-10-17)

Status: READY TO MARK. 60 blind windows over 3 mark units (TL-1h, TL-4h, TL-1d; 20 each). Question per window: is there an obvious, legitimate trend line at the right edge? Definitions: `../../layer_rebuild_2026-10-15/READER_PROTOCOL.md` section 4 (read it first, OURS). Why this pack: `../CLAUDE_VERIFY.md` (G3 before any eye-read selector), contract P8 in `../TRENDLINE_CONTRACT.md`.
Data rule: DEV only, BTCUSDT 1m klines 2022-01-01..2024-06-30 aggregated to closed 1h/4h/1d. The loader refuses any later bar (test_loader_refuses_bar_at_or_after_2024_07_01). Exposure logged in `../../gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`.

## Files
| file | what | who may open |
|---|---|---|
| `WINDOWS.csv` | window id, row, timeframe, bars shown, right edge (UTC), seed | builders (it holds dates; the charts do not) |
| `MARKING_SHEET_reader1_operator.csv`, `MARKING_SHEET_reader2_claude.csv` | one row per window: obvious_line, side, anchor1_offset, anchor2_offset, touches_seen, note | each reader their own |
| `ANSWER_KEY_CLOSED/KEY.csv`, `SELECTION_RULES.md` | per-window selection record and dates; how windows were chosen. KEY sha256 `090d3d4f6ebf61567e46156d5f6a10187b34da45fd9bda1de246cbcbf1bbc37c` (recorded before any mark exists) | nobody until both sheets are committed |
| `g3_pack.py`, `render_png.ps1`, `test_g3_pack.py` | generator, chart geometry, GDI+ renderer, 9 tests | |
| charts (not in git) | `F:/MTS/data/g3_pack_trendlines_2026-10-17/charts/<window_id>.png`, rebuilt by `python g3_pack.py draw` | readers |

Window ids are `<unit>-NN` with a shuffled number. Nothing in an id, a chart or a sheet says how a window was selected, and every chart has the same panels (candles, volume) and the same text: no overlay, no date, no clock time. Selection is builder-only (closed key).

## How to mark
1. Open the PNG and fill your own sheet as protocol section 4 says. No notes about outcomes: you cannot see any.
2. Reader 1 = the operator (about 20 s a window, about 20 min for 60). Reader 2 = one Sonnet subagent given only the PNG paths, READER_PROTOCOL.md section 4 and section 3 step 1; never WINDOWS.csv, the key, the other sheet or a date. Prompt: "You are a blind chart reader. Read research/layer_rebuild_2026-10-15/READER_PROTOCOL.md section 4. For each PNG in <chart folder>, look at the chart only and fill one row of MARKING_SHEET_reader2_claude.csv (columns as in the sheet). Do not open any other file in the trendlines_2026-10-17 folder, any file with 'KEY' or 'WINDOWS' in its name, or reader 1's sheet. Do not infer dates or outcomes."
3. When both sheets are committed (`git cherry` empty), open the key and write `G3_REPORT.md`: per row and per half the YES rate per reader, Cohen kappa on obvious_line (undefined stays "undefined"), anchor agreement among joint YES, disagreeing windows. Kappa below 0.4: the "obvious line" selector is not reproducible; back to G2 before any G4 encode.

## Decisions (OURS, logged)
- 20 windows per unit (10 + 10), as the 2026-10-16 pack: 60 windows is a 20-minute task; the extension rule of the G3 brief applies if a unit has too few YES marks.
- Three units (1h, 4h, 1d) = contract F3 set; 1m excluded as in the contract. Bars shown: 240 / 180 / 180, linear % axis (the line is judged by eye on a linear chart; the detector's log family is a separate question).
- No detector line is ever drawn: a drawn candidate would anchor the readers. The detector appears only in the closed key's selection.
- Edges start at least 2 months after the first DEV bar (4 months for 1d) so the line history exists; windows are spaced 48 / 24 / 15 bars apart.
- PNGs drawn through Windows GDI+ (no Pillow/matplotlib), kept out of git; a phone marking page is a follow-up.

Reproduce: `python g3_pack.py counts | build | draw` (about 3 minutes each; build rewrites WINDOWS.csv, the sheets and the key; the key sha must stay unchanged once marking starts).
