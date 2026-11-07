MATCH: 46 | DIFF: 0 | NOT_IN_DATA: 1

# Independent Re-derivation of `michael_lines_2026-11/RESULT.md` Numbers (`gpt-rederive-michael-lines-1107`)

- **Card**: `gpt-rederive-michael-lines-1107`
- **Model / Lane Provenance**: Executed by `gemini-4-argon-low` worker on throwaway worktree branch `gemini-q/gpt-rederive-michael-lines-1107`.
- **Scope In Read**:
  - `MyTradingSys/research/michael_lines_2026-11/RESULT.md` (`:1-24`, SOURCED)
  - `MyTradingSys/research/michael_lines_2026-11/STATED_LINES.md` (`:1-19`, SOURCED)
  - `MyTradingSys/backtest/layers/FORMULAS.md` (`:492-515`, Section 19 Trend-line contract formulas, SOURCED/OURS)
  - `MyTradingSys/research/trendlines_2026-10-17/counts/CELLS.csv` (`:1-76`, cited as `"Source of counts"` in `RESULT.md:5`, SOURCED)
  - `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md` (`:18-86`, cited in `RESULT.md:22`, SOURCED/OURS)
- **Scope Out Respected**: No study script (`extract_stated_lines.py` or `count_only.py`) was executed or used to derive numbers; no source files edited; no live-tree, `.secrets`, or `.env` touched.

## Formula & Data Provenance Check (`FORMULAS.md` Section 19 & Raw Folder Data)

1. **Folder contents (`MyTradingSys/research/michael_lines_2026-11/`)**:
   - The study folder contains `RESULT.md`, `STATED_LINES.md`, `extract_stated_lines.py`, and `test_stated_lines.py` (no raw klines or `.csv` files reside inside `michael_lines_2026-11/`).
   - `STATED_LINES.md:7-17` holds the table of stated trend-line rows (with column `chart geometry = NOT_IN_DATA` on all rows because video chart frames are not in the repository, `STATED_LINES.md:3`).
   - `RESULT.md:5` explicitly identifies its count table input as the committed DEV run `MyTradingSys/research/trendlines_2026-10-17/counts/CELLS.csv` (`config=wick_log_age500`, `slope_tercile=ALL`).
2. **`FORMULAS.md` Section 19 (`:492-515`)**:
   - Defines pivot anchor window `k=3` strict inequality (`19.1`, OURS), log-price line interpolation `L(t) = exp(ln pa + (ln pb - ln pa)*(t-ia)/(ib-ia))` (`19.2`, OURS), plain-SMA `ATR(14)` fixed at `ib` (`19.3`, OURS), slope measures (`19.4`, OURS), contact/poke/close-break tolerances `0.25*ATR_b` and `0.10*ATR_b` (`19.5`, OURS), contact episode reset `1.0*ATR_b` for Arm A (`19.6`, OURS), volume anchor ratio `V >= 2*M` over 20 prior bars for Arm V (`19.7`, SOURCED `2x / 20 bars` in `TRENDLINE_CONTRACT.md:65`), and third pivot anchor within `0.25*ATR_b` for Arm B (`19.8`, OURS).
   - Because raw BTC 1m klines are not in the study folder (`RESULT.md:5`), each of the 36 detector event counts in `RESULT.md:11-16` was checked both directly against the `slope_tercile=ALL` row in `CELLS.csv` and by independently summing the disjoint slope-tercile strata (`T0 + T1 + T2 + T3`) in `CELLS.csv:2-15,62-76` (OURS arithmetic verification). All 36 cells reproduce identically (`MATCH`).

---

## Complete Number-by-Number Audit Table (`RESULT.md` vs `STATED_LINES.md`, `CELLS.csv`, and `FORMULAS.md`)

| # | `RESULT.md` Line & Verbatim Quote (`SOURCED`) | Metric / Number | Reported Value | Recomputed Value & Formula / Source (`file:line`) | Verdict |
|---:|---|---|---|---|---|
| 1 | `RESULT.md:3` `"detector events exist at all 5 kinds on 4h/1d"` | Count of detector event kinds (`5`) | `5` (OURS schema count) | `5` event columns in `RESULT.md:9` and `CELLS.csv:1` (`first_touch`, `all_touches`, `break`, `retested`, `reclaimed`); all 5 have non-zero counts on `1d` (`CELLS.csv:5,10`) and `4h` (`CELLS.csv:66,71,76`) | `MATCH` |
| 2 | `RESULT.md:5` `"config wick_log_age500, tercile ALL"` | Maximum line age cap (`500` bars) | `500` (OURS cap, `RESULT.md:22`) | `500` in `CELLS.csv:2-16,62-77` (`config=wick_log_age500`) and `TRENDLINE_CONTRACT.md:44` (`L5`: `t - ib > 500 bars`, OURS use of SOURCED `ideal_periods=500`) | `MATCH` |
| 3 | `RESULT.md:7` `"Stated lines: 11 statements in 8 of 10 videos (STATED_LINES.md)."` | Total stated-line rows (`11`) | `11` (OURS count of SOURCED quotes) | `11` markdown table rows in `STATED_LINES.md:7-17` (and `STATED_LINES.md:19`: `"11 statements"`) | `MATCH` |
| 4 | `RESULT.md:7` `"Stated lines: 11 statements in 8 of 10 videos (STATED_LINES.md)."` | Distinct videos with statements (`8`) | `8` (OURS count) | `8` unique video IDs across `STATED_LINES.md:7-17`: `7wl0C1lVfRE` (1), `_LDxOX42NS8` (2), `avnJKLxX4FY` (1), `E_AP5kudK5Y` (1), `F0HeO0os0GM` (1), `IjC2eoUzA6M` (3), `KKnktsvQMyo` (1), `NWwIbm6j6wg` (1) | `MATCH` |
| 5 | `RESULT.md:7` `"Stated lines: 11 statements in 8 of 10 videos (STATED_LINES.md)."` | Total videos in feed (`10`) | `10` (OURS feed size) | Stated only as prose in `STATED_LINES.md:1,19` (`"10 transcripts"` / `"of 10 videos"`), cannot be recomputed from the 8 video IDs present in `STATED_LINES.md:7-17` (the 2 zero-hit transcript files live in `MyTradingSys/research/yt_feed_2026-10-31/transcripts_michael-pizzino-new10/`, outside `michael_lines_2026-11/`) | `NOT_IN_DATA` |
| 6 | `RESULT.md:7` `"9 of 11 reference oil/gold/Nasdaq (5 oil, 3 gold, 1 nasdaq; 2 asset NOT_IN_DATA; OURS keyword guess)"` | Named non-BTC asset rows (`9` of `11`) | `9` (OURS keyword guess) | `5 + 3 + 1 = 9` rows in `STATED_LINES.md:7-17` have `asset (OURS)` in `{oil, gold, nasdaq}` out of `11` total rows | `MATCH` |
| 7 | `RESULT.md:7` `"(5 oil, 3 gold, 1 nasdaq; 2 asset NOT_IN_DATA; OURS keyword guess)"` | `oil` asset rows (`5`) | `5` (OURS keyword guess) | `5` rows in `STATED_LINES.md:8,11,12,13,17` (`_LDxOX42NS8` `00:07:22`, `E_AP5kudK5Y` `00:07:49`, `F0HeO0os0GM` `00:06:57`, `IjC2eoUzA6M` `00:08:12`, `NWwIbm6j6wg` `00:08:40`) | `MATCH` |
| 8 | `RESULT.md:7` `"(5 oil, 3 gold, 1 nasdaq; 2 asset NOT_IN_DATA; OURS keyword guess)"` | `gold` asset rows (`3`) | `3` (OURS keyword guess) | `3` rows in `STATED_LINES.md:14,15,16` (`IjC2eoUzA6M` `00:09:18`, `IjC2eoUzA6M` `00:11:33`, `KKnktsvQMyo` `00:08:52`) | `MATCH` |
| 9 | `RESULT.md:7` `"(5 oil, 3 gold, 1 nasdaq; 2 asset NOT_IN_DATA; OURS keyword guess)"` | `nasdaq` asset rows (`1`) | `1` (OURS keyword guess) | `1` row in `STATED_LINES.md:7` (`7wl0C1lVfRE` `00:03:51`) | `MATCH` |
| 10 | `RESULT.md:7` `"(5 oil, 3 gold, 1 nasdaq; 2 asset NOT_IN_DATA; OURS keyword guess), none BTC"` | `NOT_IN_DATA` asset rows (`2`) | `2` (OURS keyword guess) | `2` rows in `STATED_LINES.md:9,10` (`_LDxOX42NS8` `00:07:29`, `avnJKLxX4FY` `00:02:19`; `11 - 9 = 2`) | `MATCH` |
| 11 | `RESULT.md:7` `"(5 oil, 3 gold, 1 nasdaq; 2 asset NOT_IN_DATA; OURS keyword guess), none BTC"` | `BTC` asset rows (`0` / `"none"`) | `0` (OURS keyword guess) | `0` rows in `STATED_LINES.md:7-17` have `asset (OURS)` equal to `btc` or `bitcoin` | `MATCH` |
| 12 | `RESULT.md:11` `"\| 1d \| A \| 17 \| 6 \| 8 \| 14 \| 10 \| 2 \|"` | `1d \| A` `eligible lines n` | `17` (OURS detector count) | `17` (`CELLS.csv:5`; tercile sum `T1(10)+T2(5)+T3(2) = 17` from `CELLS.csv:2-4`) | `MATCH` |
| 13 | `RESULT.md:11` `"\| 1d \| A \| 17 \| 6 \| 8 \| 14 \| 10 \| 2 \|"` | `1d \| A` `first_touch n` | `6` (OURS detector count) | `6` (`CELLS.csv:5`; tercile sum `4+1+1 = 6` from `CELLS.csv:2-4`) | `MATCH` |
| 14 | `RESULT.md:11` `"\| 1d \| A \| 17 \| 6 \| 8 \| 14 \| 10 \| 2 \|"` | `1d \| A` `all_touches n` | `8` (OURS detector count) | `8` (`CELLS.csv:5`; tercile sum `6+1+1 = 8` from `CELLS.csv:2-4`) | `MATCH` |
| 15 | `RESULT.md:11` `"\| 1d \| A \| 17 \| 6 \| 8 \| 14 \| 10 \| 2 \|"` | `1d \| A` `break n` | `14` (OURS detector count) | `14` (`CELLS.csv:5`; tercile sum `8+4+2 = 14` from `CELLS.csv:2-4`) | `MATCH` |
| 16 | `RESULT.md:11` `"\| 1d \| A \| 17 \| 6 \| 8 \| 14 \| 10 \| 2 \|"` | `1d \| A` `retested n` | `10` (OURS detector count) | `10` (`CELLS.csv:5`; tercile sum `7+2+1 = 10` from `CELLS.csv:2-4`) | `MATCH` |
| 17 | `RESULT.md:11` `"\| 1d \| A \| 17 \| 6 \| 8 \| 14 \| 10 \| 2 \|"` | `1d \| A` `reclaimed n` | `2` (OURS detector count) | `2` (`CELLS.csv:5`; tercile sum `1+0+1 = 2` from `CELLS.csv:2-4`) | `MATCH` |
| 18 | `RESULT.md:12` `"\| 1d \| B \| 19 \| 3 \| 5 \| 17 \| 15 \| 8 \|"` | `1d \| B` `eligible lines n` | `19` (OURS detector count) | `19` (`CELLS.csv:10`; tercile sum `T0(3)+T1(9)+T2(6)+T3(1) = 19` from `CELLS.csv:6-9`) | `MATCH` |
| 19 | `RESULT.md:12` `"\| 1d \| B \| 19 \| 3 \| 5 \| 17 \| 15 \| 8 \|"` | `1d \| B` `first_touch n` | `3` (OURS detector count) | `3` (`CELLS.csv:10`; tercile sum `0+3+0+0 = 3` from `CELLS.csv:6-9`) | `MATCH` |
| 20 | `RESULT.md:12` `"\| 1d \| B \| 19 \| 3 \| 5 \| 17 \| 15 \| 8 \|"` | `1d \| B` `all_touches n` | `5` (OURS detector count) | `5` (`CELLS.csv:10`; tercile sum `0+5+0+0 = 5` from `CELLS.csv:6-9`) | `MATCH` |
| 21 | `RESULT.md:12` `"\| 1d \| B \| 19 \| 3 \| 5 \| 17 \| 15 \| 8 \|"` | `1d \| B` `break n` | `17` (OURS detector count) | `17` (`CELLS.csv:10`; tercile sum `3+7+6+1 = 17` from `CELLS.csv:6-9`) | `MATCH` |
| 22 | `RESULT.md:12` `"\| 1d \| B \| 19 \| 3 \| 5 \| 17 \| 15 \| 8 \|"` | `1d \| B` `retested n` | `15` (OURS detector count) | `15` (`CELLS.csv:10`; tercile sum `2+6+6+1 = 15` from `CELLS.csv:6-9`) | `MATCH` |
| 23 | `RESULT.md:12` `"\| 1d \| B \| 19 \| 3 \| 5 \| 17 \| 15 \| 8 \|"` | `1d \| B` `reclaimed n` | `8` (OURS detector count) | `8` (`CELLS.csv:10`; tercile sum `2+1+4+1 = 8` from `CELLS.csv:6-9`) | `MATCH` |
| 24 | `RESULT.md:13` `"\| 1d \| V \| 1 \| 1 \| 1 \| 1 \| 0 \| 0 \|"` | `1d \| V` `eligible lines n` | `1` (OURS detector count) | `1` (`CELLS.csv:15`; tercile sum `T0(1)+T1(0)+T2(0)+T3(0) = 1` from `CELLS.csv:11-14`) | `MATCH` |
| 25 | `RESULT.md:13` `"\| 1d \| V \| 1 \| 1 \| 1 \| 1 \| 0 \| 0 \|"` | `1d \| V` `first_touch n` | `1` (OURS detector count) | `1` (`CELLS.csv:15`; tercile sum `1+0+0+0 = 1` from `CELLS.csv:11-14`) | `MATCH` |
| 26 | `RESULT.md:13` `"\| 1d \| V \| 1 \| 1 \| 1 \| 1 \| 0 \| 0 \|"` | `1d \| V` `all_touches n` | `1` (OURS detector count) | `1` (`CELLS.csv:15`; tercile sum `1+0+0+0 = 1` from `CELLS.csv:11-14`) | `MATCH` |
| 27 | `RESULT.md:13` `"\| 1d \| V \| 1 \| 1 \| 1 \| 1 \| 0 \| 0 \|"` | `1d \| V` `break n` | `1` (OURS detector count) | `1` (`CELLS.csv:15`; tercile sum `1+0+0+0 = 1` from `CELLS.csv:11-14`) | `MATCH` |
| 28 | `RESULT.md:13` `"\| 1d \| V \| 1 \| 1 \| 1 \| 1 \| 0 \| 0 \|"` | `1d \| V` `retested n` | `0` (OURS detector count) | `0` (`CELLS.csv:15`; tercile sum `0+0+0+0 = 0` from `CELLS.csv:11-14`) | `MATCH` |
| 29 | `RESULT.md:13` `"\| 1d \| V \| 1 \| 1 \| 1 \| 1 \| 0 \| 0 \|"` | `1d \| V` `reclaimed n` | `0` (OURS detector count) | `0` (`CELLS.csv:15`; tercile sum `0+0+0+0 = 0` from `CELLS.csv:11-14`) | `MATCH` |
| 30 | `RESULT.md:14` `"\| 4h \| A \| 177 \| 105 \| 133 \| 166 \| 140 \| 98 \|"` | `4h \| A` `eligible lines n` | `177` (OURS detector count) | `177` (`CELLS.csv:66`; tercile sum `T0(3)+T1(66)+T2(58)+T3(50) = 177` from `CELLS.csv:62-65`) | `MATCH` |
| 31 | `RESULT.md:14` `"\| 4h \| A \| 177 \| 105 \| 133 \| 166 \| 140 \| 98 \|"` | `4h \| A` `first_touch n` | `105` (OURS detector count) | `105` (`CELLS.csv:66`; tercile sum `2+41+30+32 = 105` from `CELLS.csv:62-65`) | `MATCH` |
| 32 | `RESULT.md:14` `"\| 4h \| A \| 177 \| 105 \| 133 \| 166 \| 140 \| 98 \|"` | `4h \| A` `all_touches n` | `133` (OURS detector count) | `133` (`CELLS.csv:66`; tercile sum `2+55+41+35 = 133` from `CELLS.csv:62-65`) | `MATCH` |
| 33 | `RESULT.md:14` `"\| 4h \| A \| 177 \| 105 \| 133 \| 166 \| 140 \| 98 \|"` | `4h \| A` `break n` | `166` (OURS detector count) | `166` (`CELLS.csv:66`; tercile sum `3+58+56+49 = 166` from `CELLS.csv:62-65`) | `MATCH` |
| 34 | `RESULT.md:14` `"\| 4h \| A \| 177 \| 105 \| 133 \| 166 \| 140 \| 98 \|"` | `4h \| A` `retested n` | `140` (OURS detector count) | `140` (`CELLS.csv:66`; tercile sum `2+47+48+43 = 140` from `CELLS.csv:62-65`) | `MATCH` |
| 35 | `RESULT.md:14` `"\| 4h \| A \| 177 \| 105 \| 133 \| 166 \| 140 \| 98 \|"` | `4h \| A` `reclaimed n` | `98` (OURS detector count) | `98` (`CELLS.csv:66`; tercile sum `2+36+34+26 = 98` from `CELLS.csv:62-65`) | `MATCH` |
| 36 | `RESULT.md:15` `"\| 4h \| B \| 208 \| 66 \| 78 \| 199 \| 167 \| 109 \|"` | `4h \| B` `eligible lines n` | `208` (OURS detector count) | `208` (`CELLS.csv:71`; tercile sum `T0(5)+T1(92)+T2(70)+T3(41) = 208` from `CELLS.csv:67-70`) | `MATCH` |
| 37 | `RESULT.md:15` `"\| 4h \| B \| 208 \| 66 \| 78 \| 199 \| 167 \| 109 \|"` | `4h \| B` `first_touch n` | `66` (OURS detector count) | `66` (`CELLS.csv:71`; tercile sum `0+34+18+14 = 66` from `CELLS.csv:67-70`) | `MATCH` |
| 38 | `RESULT.md:15` `"\| 4h \| B \| 208 \| 66 \| 78 \| 199 \| 167 \| 109 \|"` | `4h \| B` `all_touches n` | `78` (OURS detector count) | `78` (`CELLS.csv:71`; tercile sum `0+41+23+14 = 78` from `CELLS.csv:67-70`) | `MATCH` |
| 39 | `RESULT.md:15` `"\| 4h \| B \| 208 \| 66 \| 78 \| 199 \| 167 \| 109 \|"` | `4h \| B` `break n` | `199` (OURS detector count) | `199` (`CELLS.csv:71`; tercile sum `5+85+68+41 = 199` from `CELLS.csv:67-70`) | `MATCH` |
| 40 | `RESULT.md:15` `"\| 4h \| B \| 208 \| 66 \| 78 \| 199 \| 167 \| 109 \|"` | `4h \| B` `retested n` | `167` (OURS detector count) | `167` (`CELLS.csv:71`; tercile sum `4+70+63+30 = 167` from `CELLS.csv:67-70`) | `MATCH` |
| 41 | `RESULT.md:15` `"\| 4h \| B \| 208 \| 66 \| 78 \| 199 \| 167 \| 109 \|"` | `4h \| B` `reclaimed n` | `109` (OURS detector count) | `109` (`CELLS.csv:71`; tercile sum `2+50+42+15 = 109` from `CELLS.csv:67-70`) | `MATCH` |
| 42 | `RESULT.md:16` `"\| 4h \| V \| 114 \| 84 \| 96 \| 110 \| 90 \| 58 \|"` | `4h \| V` `eligible lines n` | `114` (OURS detector count) | `114` (`CELLS.csv:76`; tercile sum `T0(1)+T1(33)+T2(37)+T3(43) = 114` from `CELLS.csv:72-75`) | `MATCH` |
| 43 | `RESULT.md:16` `"\| 4h \| V \| 114 \| 84 \| 96 \| 110 \| 90 \| 58 \|"` | `4h \| V` `first_touch n` | `84` (OURS detector count) | `84` (`CELLS.csv:76`; tercile sum `0+24+33+27 = 84` from `CELLS.csv:72-75`) | `MATCH` |
| 44 | `RESULT.md:16` `"\| 4h \| V \| 114 \| 84 \| 96 \| 110 \| 90 \| 58 \|"` | `4h \| V` `all_touches n` | `96` (OURS detector count) | `96` (`CELLS.csv:76`; tercile sum `0+28+37+31 = 96` from `CELLS.csv:72-75`) | `MATCH` |
| 45 | `RESULT.md:16` `"\| 4h \| V \| 114 \| 84 \| 96 \| 110 \| 90 \| 58 \|"` | `4h \| V` `break n` | `110` (OURS detector count) | `110` (`CELLS.csv:76`; tercile sum `1+32+34+43 = 110` from `CELLS.csv:72-75`) | `MATCH` |
| 46 | `RESULT.md:16` `"\| 4h \| V \| 114 \| 84 \| 96 \| 110 \| 90 \| 58 \|"` | `4h \| V` `retested n` | `90` (OURS detector count) | `90` (`CELLS.csv:76`; tercile sum `1+25+26+38 = 90` from `CELLS.csv:72-75`) | `MATCH` |
| 47 | `RESULT.md:16` `"\| 4h \| V \| 114 \| 84 \| 96 \| 110 \| 90 \| 58 \|"` | `4h \| V` `reclaimed n` | `58` (OURS detector count) | `58` (`CELLS.csv:76`; tercile sum `1+16+17+24 = 58` from `CELLS.csv:72-75`) | `MATCH` |

---

## Summary of Counts

- **MATCH**: `46` (36 table cells across `1d` and `4h` arms `A`, `B`, `V` verified directly and via tercile-sum identity in `CELLS.csv:2-15,62-76`, plus 10 prose numbers in `RESULT.md:3,5,7,22` verified against `STATED_LINES.md:7-19` and `CELLS.csv:1`)
- **DIFF**: `0` (the earlier `8 of 11` prose error flagged in `2026-11-02_gemini-blind-read-michael-lines-1102.md:17` was already corrected to `9 of 11` in commit `c124d6df1`)
- **NOT_IN_DATA**: `1` (the total feed size `"of 10 videos"` in `RESULT.md:7` is stated in `STATED_LINES.md:1,19` header/footer prose, whereas only the 8 video IDs with matches appear in `STATED_LINES.md:7-17`)
