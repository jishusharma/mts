# G3 marking pack, first batch (built 2026-10-16)

Status: READY TO MARK (blindness fixes audited, 213 charts rebuilt 2026-10-17 from the fixed g3_pack.py). 213 blind windows over 11 mark units (13 catalogue rows). Definitions: `../layer_rebuild_2026-10-15/READER_PROTOCOL.md` (read it first). Design: `../observer_2026-10-15/OBSERVER_REPORT.md` G3 brief (revised 2026-10-16).
Data rule: DEV only. Footprint rows (Tom/Fabio) read F:/MTS/data/orderflow_1m 2024-12-02..2025-03-31, which is the Tom footprint track's DEV per the task brief but lies inside the standard VALIDATION dates (2024-07-01..2025-06-30); the exposure is logged in `gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`. Daily/weekly rows read daily klines 2021-03-01..2024-06-30 (standard DEV). The loaders cannot open a later file or row (test_dev_fences_never_read_later_data).

## Files
| file | what | who may open |
|---|---|---|
| `WINDOWS.csv` | window id, row, timeframe, bars shown, right edge (UTC), seed | builders (it holds dates; the charts do not) |
| `MARKING_SHEET_reader1_operator.csv`, `MARKING_SHEET_reader2_claude.csv` | one row per window to fill: take_skip, side, trigger_bar_offset, concepts_seen, stop_pct, target_pct, note | each reader their own |
| `ANSWER_KEY_CLOSED/KEY.csv` | per-window selection record and tag, dates. sha256 `0bfdf336a9ced5674579e183aac0ea39c7ce069fb832de09e2fecc84b79402e6` (recorded before any mark exists) | nobody until both sheets are committed |
| `g3_pack.py`, `render_png.ps1`, `test_g3_pack.py` | generator, selection code, chart geometry, GDI+ renderer, 8 tests | |
| charts (not in git) | `F:/MTS/data/g3_pack_2026-10-16/charts/<window_id>.png`, rebuilt by `python g3_pack.py draw` | readers |

## Windows (seed 20261016, per row `<seed>-<code>`)
213 blind windows over 11 mark units (20 per unit; MAL-2/5 has 13). Window ids carry the row code and a shuffled number; nothing in an id, a chart or a sheet says how a window was selected. The selection method and its rules are builder-only and live in `ANSWER_KEY_CLOSED/SELECTION_RULES.md` (closed with the key; readers must not open it).

## How to mark
1. Open the PNG, fill the reader's own sheet: `take_skip` TAKE or SKIP (MAL-16/17: side SHORT / LONG / none); `side` LONG or SHORT; `trigger_bar_offset` 0 = last closed bar, up to 3 back; `concepts_seen` from the fixed list in the protocol section 3; `stop_pct`, `target_pct` as % from the last close. No notes about outcomes: you cannot see any.
2. Reader 1 = the operator (about 12 s a window, about 45 min for all 213). Suggested batches: A Krown + Malkan (KR-S1, KR-S8, MAL-2/5, MAL-16/17: 73 windows), B Tom (TOM-4, 6, 12, 15: 80), C Fabio (FAB-1, 4, 5: 60).
3. Reader 2 = a Sonnet subagent started per unit with only: the PNG paths of that unit, READER_PROTOCOL.md, and the row's catalogue text (SETUP_CATALOG.md / KROWN_SETUP_CATALOG.md / SETUP_SUMMARY.md, the row's own section). It must not be given WINDOWS.csv, the key, reader 1's sheet or any date. It writes reader 2's sheet.
   Reader 2 prompt (one subagent per unit, model Sonnet; fill the three placeholders): "You are a blind chart reader. Read research/layer_rebuild_2026-10-15/READER_PROTOCOL.md, then the catalogue section headed <ROW ID> (find it by heading in <catalogue file>). For each PNG <window_id>.png in <chart folder> whose id starts with <CODE>-, look at the chart only and decide TAKE or SKIP for that row as the protocol section 3 says. Write your answers into MARKING_SHEET_reader2_claude.csv (only the rows of your unit). Do not open any other file in the g3_marks folder, any file with 'KEY' or 'WINDOWS' in its name, or reader 1's sheet. Do not infer dates or outcomes."
4. When both sheets are committed (`git cherry` empty), open the key and write `G3_REPORT.md`: per row and per half the yes-rate per reader, Cohen kappa (undefined stays "undefined"), disagreeing windows. Kappa < 0.4: back to G2.

## Decisions (OURS, logged)
- 20 windows per row (10 + 10), not 30: 13 rows x 30 would be a 65-minute task before the first number; the extension rule in the G3 brief covers rows with too few positives.
- MAL-5 merged into MAL-2 (same event, order mechanic only); MAL-16 and MAL-17 share windows with a three-way mark (D3).
- MAL-2/5 shows 60 weekly bars (not 104): daily data on disk starts 2020-01, 104 weeks would push the first edge to 2022-01.
- PNGs are drawn through Windows GDI+ (no Pillow, no matplotlib on this machine) from pure-Python geometry; PNGs stay out of git.
- A phone marking page (Artifact with the db capability, as the 2026-10-15 brief proposed) is a follow-up; the CSV sheets and the PNG folder work today.

Reproduce: `python g3_pack.py counts | build | draw` (build rewrites WINDOWS.csv and the key; the key sha must stay unchanged once marking starts).
