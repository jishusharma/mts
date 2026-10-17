# PRE-REGISTRATION: WaveTrend (LazyBear) behaviour atlas, BTCUSDT perp, DEV (frozen 2026-10-17)

Card `wavetrend-prereg-counts`. Status: EXPLORATORY BEHAVIOUR TABLE, not a strategy test. Nothing here adopts a rule.
Precedes: `wavetrend-observation-module` (fixture-tested module) and `wavetrend-dev-atlas` (the one DEV run). The commit that adds this file precedes any commit that adds an outcome.
Spec: `ATLAS_STUDY_SPEC.md`; oscillator pin: `PARITY_CONTRACT.md`; verification fixes: `CLAUDE_VERIFY.md` s D.
Labels: SOURCED = quoted from a saved source with file:line; OURS = judgement or tuned on DEV counts (allowed; checked once on VALIDATION later, HOLDOUT sealed, variants in the trial ledger).

## 0. What was read to produce this file
- Read: Binance USDT-M BTCUSDT 1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01.csv .. -2024-06.csv` (30 files, DEV, 912 days, zero missing 1m bars; the loader refuses any bar >= 2024-07-01). Fields used: open, high, low, close, volume.
- Computed: WT (reference implementation `wt_parity_ref.py`, conventions of PARITY_CONTRACT s3), event timestamps, context bins, and COUNTS (events, distinct event-days, side split, bars per matching stratum).
- NOT computed anywhere (script `count_events.py`, `select_cells.py`, `counts/*.csv` have no such column): any return, MFE/MAE, hit rate, response time, fee, or any bar after an event. VALIDATION and HOLDOUT: zero reads. Counts are logged in `gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`.
- Reproduce: `python count_events.py --out counts --R 3 --c 5 --k 2 --G 20` then `python select_cells.py counts/counts_R3_c5_k2_G20.csv`. Tests: `test_count_events.py`.

## 1. Frozen numbers
| Item | Value | Label |
|---|---|---|
| WT parameters, source | hlc3, EMA 10, EMA 21, SMA 4, 0.015, bands +/-53, +/-60, centre 0 | SOURCED `source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:9-23` (PARITY_CONTRACT s2) |
| Warm-up, cross convention, gaps, closed bars | PARITY_CONTRACT s3 | OURS (as contracted) |
| Timeframes counted | 5m, 15m, 1h, 4h, 1d | spec s1 |
| Power floor FLOOR | **153 distinct UTC event-days** per cell: Holm over 12 cells (alpha 0.05/12 two-sided, z=2.87), power 80 % (z=0.84), MDE (z+z)/sqrt(n) <= 0.30 SD of the outcome | OURS; a day is the independence unit (spec s5) |
| R_out (A1: bars outside the zone before an arrival counts) | **3** | OURS from counts: smallest of {1,3,6,12} that marks >= 5 % of band entries as flicker on both 15m (8 %) and 1h (6 %); A1 days at 1h: 410 (R=1), 404 (R=3), 373 (R=6), 335 (R=12) |
| c (B2 centre-test half-width, WT points) | **5** | OURS from counts: smallest of {3,5,10} whose B2 reaches FLOOR on 1h (c=3: 128 days, c=5: 196, c=10: 279) |
| k (right-hand pivot bars) and G (max bars between pivots) | **k=2, G=20** | OURS from counts: largest k, then smallest G, in {2,3,5} x {20,40,60}, such that C1 reaches FLOOR on 1h (331 days) and C2 reaches 2 x FLOOR on 15m (307 days; k=3: 297, k=5: 247 fail). A small k means pivots are short-lived; this is disclosed, the neighbours k=3/5 are NOT run (no variant shopping) |
| L for cells | 53; L=60 is the "extreme" control family (counts below) | OURS |
| Vol bin | std of 100 trailing close-to-close log returns, terciles of DEV (edges below) | OURS |
| Trend bin | with / mixed / against the event side: with = close > EMA(200) and EMA(200)[t] > EMA(200)[t-10] for a long-side event (mirror for a short-side event) | OURS |
| HTF bin | zone of the next-higher TF WT at its last closed bar: with the event side (wt1 x side >= 53) / mid / against (<= -53). 5m->15m, 15m->1h, 1h->4h, 4h->1d | OURS; spec s3 |
| Participation bin | bar volume / mean volume of the same UTC slot over the previous 20 days, DEV terciles | OURS |
| Hour bin | UTC close hour thirds 00-08, 08-16, 16-24 | OURS |

Frozen bin edges (DEV terciles, from `counts/quality.txt`; vol edge = std of 100 log returns, participation edge = ratio):
| TF | vol t1 | vol t2 | part t1 | part t2 |
|---|---|---|---|---|
| 5m | 0.000982 | 0.001575 | 0.4478 | 0.9394 |
| 15m | 0.001841 | 0.002743 | 0.4941 | 0.9657 |
| 1h | 0.004031 | 0.005564 | 0.5585 | 1.0115 |
| 4h | 0.008555 | 0.011455 | 0.6399 | 1.0680 |
| 1d | 0.025124 | 0.030767 | 0.7610 | 1.1153 |

## 2. Event counts (DEV, all sides, no context; events / distinct event-days)
| Event | 5m | 15m | 1h | 4h | 1d |
|---|---|---|---|---|---|
| A1 arrival L53 | 5114 / 912 | 1633 / 839 | 436 / 404 | 102 / 102 | 12 / 12 |
| A2 turn-in-zone L53 | 4229 / 908 | 1370 / 788 | 351 / 328 | 85 / 85 | 10 / 10 |
| A3 zone cross L53 (CONTROL) | 6374 / 911 | 2034 / 829 | 533 / 412 | 126 / 124 | 15 / 15 |
| A4 re-entry L53 | 5546 / 911 | 1778 / 844 | 471 / 395 | 116 / 115 | 11 / 11 |
| A1 arrival L60 (extreme control) | 3353 / 899 | 1123 / 705 | 292 / 262 | 68 / 68 | 8 / 8 |
| A3 zone cross L60 (CONTROL) | 3855 / 899 | 1269 / 686 | 340 / 269 | 78 / 77 | 10 / 10 |
| B1 centre cross | 14124 / 912 | 4889 / 907 | 1116 / 659 | 245 / 205 | 25 / 25 |
| B2 centre test (c=5) | 2597 / 856 | 873 / 556 | 221 / 196 | 56 / 56 | 6 / 6 |
| C1 regular divergence (k=2, G=20) | 3840 / 907 | 1288 / 694 | 392 / 331 | 104 / 102 | 15 / 15 |
| C2 lower second peak in band (k=2, G=20) | 1207 / 646 | 403 / 307 | 123 / 110 | 22 / 21 | 2 / 2 |
Full table with every context bin: `counts/counts_R3_c5_k2_G20.csv`. Data-quality: wt1 == wt2 exact tie bars = 0 on every TF; NaN bars = 0; valid wt1 bars 262,456 / 87,352 / 21,688 / 5,272 / 712.
Independence note: 5m and 15m event-days saturate near 912 because many events share a day; the unit of inference is the day (cluster), so 5m cells have a small MDE but each day-mean rests on a handful of correlated bars. The atlas reports events per day beside every cell.

## 3. TFs and events dropped (spec s1: "drops any TF whose independent episodes cannot reach its MDE")
- 1d: no event reaches FLOOR (max 25 days). Dropped.
- 4h: every A, B2 and C2 count is below FLOOR (A1 102, A2 85, B2 56, C2 21; C1 102, B1 205 but a context bin <= 3 splits B1 below FLOOR). Dropped from cells; 4h counts remain as descriptive controls only if the atlas runs them unconditioned, flagged "underpowered", never in Holm.
- C2 (structure): reaches FLOOR unconditioned only on 5m and 15m, and its eligible bins (5m trend-with 611 days, 15m trend-with 287) are excluded by the section 4 rule (events are ranked before C2 take the 3-cells-per-TF slots on 5m and 15m). **No C2 cell**; C2 is listed "underpowered, not tuned".

## 4. Selection rule (written before `select_cells.py` was run)
Eligible row: context bin (not ALL), event in {A1_L53, A2_L53, B2, C1, C2, B1}, bin event-days >= FLOOR, and the TF's unconditioned event-days >= FLOOR. In that event order: take the top 2 rows by event-days with distinct (TF, context variable); at most 3 cells per TF; at most 12 cells in total. Ties break on TF order then variable name. Effect: the largest eligible bins win, which are usually the broadest ("with trend", "mid" HTF); this is a power-first choice, disclosed, and means vol / participation / hour contexts are not in the 9 cells (they stay as stratifiers of the random-clock arm).

## 5. Frozen cells (9, <= 12)
Side handling: a cell pools both sides in the IMPLIED direction (OURS, so a short from the upper zone and a long from the lower zone are one sample); side counts are reported. Implied direction: A1, A2, C1 = reversal toward the centre (short from the upper zone); B1 = direction of the cross; B2 = continuation of the side the oscillator came from. The implied direction is a measurement convention for the atlas, not a trading rule.
| Cell | TF | Event | Context bin | Events | Event-days | Up / lower side | MDE (SD units, Holm 12, 80 %) | Hit-rate MDE at p=0.5 (pp) |
|---|---|---|---|---|---|---|---|---|
| W01 | 5m | A1 L53 arrival | trend: with | 3893 | 910 | 1969 / 1924 | 0.123 | 6.1 |
| W02 | 5m | A1 L53 arrival | HTF(15m): mid | 4196 | 908 | 2096 / 2100 | 0.123 | 6.1 |
| W03 | 5m | A2 L53 turn | trend: with | 3509 | 904 | 1800 / 1709 | 0.123 | 6.2 |
| W04 | 15m | A2 L53 turn | trend: with | 1155 | 716 | 598 / 557 | 0.139 | 6.9 |
| W05 | 15m | B2 centre test | HTF(1h): mid | 788 | 511 | 408 / 380 | 0.164 | 8.2 |
| W06 | 15m | B2 centre test | trend: with | 538 | 390 | 274 / 264 | 0.188 | 9.4 |
| W07 | 1h | C1 regular divergence | trend: with | 298 | 251 | 159 / 139 | 0.234 | 11.7 |
| W08 | 1h | C1 regular divergence | HTF(4h): mid | 271 | 239 | 134 / 137 | 0.240 | 12.0 |
| W09 | 1h | B1 centre cross | HTF(4h): mid | 947 | 562 | 475 / 472 | 0.156 | 7.8 |
(`counts/CELLS.csv` is the machine form.) MDE is in SD units because no outcome was read; the atlas converts it to bps with the realised SD of the random-clock arm. The MDE assumes the conjunction arm is compared with a large control; the conjunction-vs-WT-alone contrast, whose WT-alone arm is bigger but comparable, is at most sqrt(2) larger: still < 0.35 SD for every cell. **Hit-rate MDE is for the 50 % reference only.**

## 6. Outcomes, arms, tests (for `wavetrend-dev-atlas`; spec s4-s5 as written, with these frozen choices)
- Horizons H = {4, 12, 48} bars of the cell's TF (OURS). **Primary outcome: signed gross return open(t+1) -> close(t+12) in the implied direction.** H=4 and H=48, MFE/MAE (bar extremes, upper bounds), response time, excursion depth, hit rate with Wilson CI: descriptive, outside Holm.
- Arms per cell: (1) WT event alone (the unconditioned event at that TF), (2) context alone (same bin, no WT event, hour-of-day matched), (3) conjunction (the cell), (4) random clock: 200 draws matched on TF, UTC hour slot and vol tercile (draw from bars with valid features; eligible pool per stratum: min/median bars 5m 160/304, 15m 280/305, 1h 290/303; 5m strata below 200 are drawn with replacement across days and flagged).
- CONTROLS reported beside each A cell: A3 zone cross (L53) and the L60 extreme variants at the same TF. They are never cells.
- Primary test: conjunction mean primary outcome minus random-clock mean, day-clustered; **Holm over the 9 primary tests (m = 9)**. A cell passes the incremental-information screen only if the conjunction beats its WT-alone arm, its context-alone arm and the random clock; otherwise "no incremental information". Cells below FLOOR on the realised data: "underpowered", not tuned.
- Output is gross (no fees, no funding) and descriptive. Any strategy needs its own PRE_REG with Binance-venue costs, VALIDATION once and HOLDOUT sealed; no net edge is claimed or implied.

## 7. Trial ids (each variant is one ledger row; `verdicts.py` aliases {WT, wave_trend, wavetrend, LazyBear, cipher})
`verdicts.py check` for WaveTrend, wave_trend, LazyBear, cipher on 2026-10-17: no prior row matches. Registered trials (count-only, no outcome): WT-T01 R_out grid {1,3,6,12}; WT-T02 c grid {3,5,10}; WT-T03 (k,G) grid 3x3; WT-T04 L in {53,60}. Atlas trials: WT-A01..WT-A09 = cells W01..W09 (one primary test each).

## 8. Known weaknesses (read before trusting any later number)
1. Bin edges and the k, c, R_out, G choices were made on DEV counts: a mild selection on the same period the atlas will read (spec s3); VALIDATION is the check.
2. k=2 pivots are short-lived; the neighbours were not run.
3. The largest-bin rule favours broad contexts; a regime effect hidden in a small bin cannot be seen at this power.
4. 5m events within a day are strongly autocorrelated; the day cluster is the unit, and effective n is smaller than "events".
5. Hidden divergence, volume/VWMA and the BTC-author stop/target variant are out of scope (spec s7).
6. `wt_parity_ref.py` is the WT source here and is not a golden source (PARITY_CONTRACT s3); a spreadsheet golden fixture is the module card's job, and event counts here will be re-derived from the module once it exists (any change in a count above its rounding is a finding to report, not to tune around).
