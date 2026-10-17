# G3 blindness audit rerun ? 2026-10-17

## Verdict: FIX-FIRST

The current builder removes direct time labels and selection-conditioned overlays, and the README no longer publishes enrichment rules. Rebuild the existing charts before any of the 213 marks because the previous draw predates these fixes. `Draw rebuild: YES`.

## What was checked

- Blindness subsection (b) only of `2026-10-16_gpt-g3-pack-audit.md:37-46`; its HIGH concern was last-bar/prefilter-tag inference, and MED concerns were IDs/titles and intraday edge time.
- Current code and surfaces: `g3_pack.py:38-50,448-468,616-722,778-798`; `test_g3_pack.py:203-233`; `README.md:3,9-16`; all 213 rows of `WINDOWS.csv`; `render_png.ps1:1-31`; `READER_PROTOCOL.md:7-45`.
- No `git` command was run, per the task boundary. Therefore no `git show 198c1aed` comparison is claimed; findings reflect the current workspace contents only.
- Key material, marking sheets, market inputs, and rendered PNGs were not opened. No pack build or draw was run. Evidence is aggregate; no window id is paired with a half or tag.

## Blindness surfaces

| Surface | Result | Aggregate evidence |
|---|---|---|
| IDs, filenames, titles | FIXED for half/tag; MED residual for row identity | IDs and PNG basenames use `<unit>-NN`; the unit repeats as chart title and `WINDOWS.csv` has only `window_id,row,timeframe,bars_shown,right_edge_utc,seed,data` (`g3_pack.py:467-468,622,699,749-750,792-796`; `WINDOWS.csv:1`, 213 rows). No literal half/tag is emitted in these fields. Titles identify the setup family (`g3_pack.py:622,699`), which reveals the row under review but not the selection half. |
| Bar count and spacing | FIXED / MATCH | One shared bar count and minimum spacing per unit: 15m/5m units show 288 bars, 30m units 240, daily units 180, weekly 60; spacing is respectively configured as 48, 72, 24, 10, and 4 bars (`g3_pack.py:38-50`). `WINDOWS.csv` has 213 records: ten units have 20 records each; weekly MAL-2/5 has 13. No half-specific count/spacing is published. |
| Right-edge time and UTC day line | FIXED for clock labels; MED residual inference | Intraday labels are relative offsets only, no clock text (`g3_pack.py:627-633`; test `test_g3_pack.py:220-228`). UTC-midnight vertical lines remain (`g3_pack.py:632-633`), so an informed reader may estimate edge time-of-day from line position relative to the right edge and known bar spacing. Daily/weekly axes also use relative offsets (`g3_pack.py:701-702`). Exact edge times are in builder-only `WINDOWS.csv`, whose role is described in `README.md:9`; they were not surfaced here. |
| Last-bar pattern and pre-filter tag | RESIDUAL (MED inference; no direct tag cue found) | No half/tag text is emitted in chart titles or primitives (`g3_pack.py:616-686,689-722`); selection metadata remains in internal records/key output (`g3_pack.py:448-468,751-754`). Clock labels are removed, and TOM-15 balance edges are now always drawn, removing the conditional overlay (`g3_pack.py:656-659`; regression `test_g3_pack.py:208-218`). Charts still show final candles and row-specific price/volume/VA/delta/RSI/BBWP features, which a reader can compare with the catalogue/protocol (`g3_pack.py:621-684,700-719`; `READER_PROTOCOL.md:27-45`). Direct disclosure is fixed, but an informed reader may infer a trigger from the evidence intended for marking; no key-based half/tag association was tested. |
| README text | FIXED for published selection rule; operational rebuild instruction remains | README says the 213 windows are blind and IDs/charts/sheets omit selection labels; selection rules are builder-only (`README.md:15-16`). It explicitly says marking is not ready until fixes are audited and charts rebuilt (`README.md:3`). It documents the chart folder and draw command (`README.md:13,32`), not enrichment rules. |

## Tests

Requested command using pytest's default temp directory: `python -m pytest MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py -q` hit two tmp-path setup errors because Windows denied scanning the default temp root; result **12 passed, 0 failed, 2 setup errors, 0 skipped**. Retried in the writable lab: `python -m pytest MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py -q -p no:cacheprovider --basetemp=MyTradingSys/research/layer_lab/reports/pytest_g3_blindness_1017_tmp` ? **14 passed, 0 failed, 0 skipped**.

## Findings

| Severity | File:line | Result / evidence | Required action |
|---|---|---|---|
| HIGH (operational) | `README.md:3,13`; `g3_pack.py:778-798` | Existing chart artifacts predate the current builder fixes; README explicitly gates marking on chart rebuild. This rerun did not inspect or modify chart artifacts. | Rebuild all 213 charts from the current builder, then mark. |
| MED (residual inference) | `g3_pack.py:622,630-633,656-659,699-702`; `READER_PROTOCOL.md:27-45` | Row is named, exact clock labels are absent, and the balance overlay is unconditional, but day-line geometry and visible setup evidence leave inference possible. No individual half/tag attribution is made. | No additional direct source-level disclosure cue was established in this scoped rerun; rebuild remains required for the fixes already made. |

No probe was needed or saved. No follow-up cards were created.

Draw rebuild: YES ? the pre-fix chart artifacts must be regenerated from the current builder before the 213 marks because `README.md:3` explicitly gates marking on the rebuild.
