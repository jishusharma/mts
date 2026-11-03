FOUND=0 DIFF=0 NOT_IN_DATA=13

# Blind read of Eagle C36 (1m WT turn + RSI confluence), card `gemini-blind-read-eagle-c36-wt-confluence-1103`

- Audited: row C36 in `MyTradingSys/research/eagle_eyes_picture_2026-10-28/BACKTEST_CANDIDATES.md:45`, lesson 12 in `MyTradingSys/system/EAGLE_EYES_BIBLE.md:160`, script `MyTradingSys/research/eagle_eyes_picture_2026-10-28/wt_turn_rsi_confluence_1m.py` (read only, byte-identical, `git diff` empty).
- Host: Lenovo laptop DESKTOP-F7IU69N (Gemini lane). `Test-Path F:/MTS/data/tom_raw/klines` = False (no F: drive); a recursive search of `C:\Users\e-ngineers` for `BTCUSDT-1m*` found nothing. The script reads only that path (`wt_turn_rsi_confluence_1m.py:19`), so it cannot run here. Per the card, every quoted number is `NOT_IN_DATA`. Nothing below is a reproduction (OURS).
- To close the gap: run the script on a host that has the klines (JIS-NB or JIS-NUC, `python wt_turn_rsi_confluence_1m.py`) and compare to the table.

## One row per number quoted in C36 (also quoted in lesson 12)

| # | Quoted number | Meaning in C36 | Script line that would print it | Result |
|---|---|---|---|---|
| 1 | n=13,466 | BULL all crosses | `rep('all crosses')` :99 | NOT_IN_DATA |
| 2 | 33.8 | bare cross, target first % | :99 | NOT_IN_DATA |
| 3 | 36.1 | bare cross, stop first % | :99 | NOT_IN_DATA |
| 4 | n=906 | BULL all three (ext+MA+div) | `rep('+ all three')` :105 | NOT_IN_DATA |
| 5 | 40.5 | all three, target first % | :105 | NOT_IN_DATA |
| 6 | 35.8 | all three, stop first % | :105 | NOT_IN_DATA |
| 7 | median +0.055 % | all three, r30 median | :105 | NOT_IN_DATA |
| 8 | n=1,131 | mirror (BEAR) all three | :105 (sd=-1) | NOT_IN_DATA |
| 9 | 37.4 | mirror target first % | :105 (sd=-1) | NOT_IN_DATA |
| 10 | 34.6 | mirror stop first % | :105 (sd=-1) | NOT_IN_DATA |
| 11 | n=69 | BULL none of the three | `rep('none of the three')` :106 | NOT_IN_DATA |
| 12 | 26 | none of three, target first % | :106 | NOT_IN_DATA |
| 13 | 46 | none of three, stop first % | :106 | NOT_IN_DATA |

## Checks that need no data (OURS, arithmetic and code read only)

- C36 and lesson 12 quote the same figures (no text drift between the two files).
- The window `2023-01-01..2025-06-30` (script :17, END exclusive 2025-07-01) is about 912 days. 13,466 / 912 = 14.8 crosses a day matches the lesson's "15 a day"; 906 / 912 = 0.99 matches "one a day".
- The script's rule matches the lesson text: WT cross out of the +-53 band (:74), RSI 5-bar extreme under 35 / over 65 (:76-77), RSI over its SMA14 within 3 bars (:78, range i..i+3), divergence 15 vs 15 bars (:79-81), outcome +-0.30 % within 60 bars (:49).
- Open point for the rerun: C36 does not say which side the "none of the three 26 / 46 (n=69)" row belongs to. The script prints BULL and BEAR blocks separately (:96-106), so the rerun must name the block for rows 11-13; rows 8-10 are the BEAR block.
