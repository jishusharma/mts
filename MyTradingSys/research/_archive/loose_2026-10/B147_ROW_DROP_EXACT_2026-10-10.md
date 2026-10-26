# B147 - exact Tom backtest row drop, regenerated with HEAD Java (2026-10-10)

Closes the "needs regenerated snapshots" part of B147_ROW_DROP_ATTRIBUTION_2026-10-10.md. Desk task B147/B135, run on JIS-NB.

## What was run
- Trunk Java at origin/fast-track cceff62 (archive-mode HistoricalSource/ArchiveHistoricalSource/MarketDataSnapshot(Path) are committed now, no overlays), TomSnapshotGen + SnapAt from
  research/core_readiness_2026-09-27/harness/java, compiled with JDK 17 into a temp copy (never src/ or target/), 3 shards, below-normal priority, empty cwd.
- Klines F:\MTS\data	om_raw, 2022-01-20..2026-09-27, 15-min step -> F:\MTS\data	om_snapshots_head: 57 months, 164257 evaluated, 0 errors, **90295 kept**
  (old run 120892, 2026-10-06 rerun 90699: the 404 gap is HEAD changes between 10-06 and cceff62; not decomposed).
- TOM_SNAP_DIR=...tom_snapshots_head TOM_WORK_DIR=...tom_bt_head: `tom_bt_run.py rows` (24 s) then `tom_bt_diag.py`: 90295 cache rows, **0 rows with proof>=5**, 0 replay-vs-cache verdict mismatches.
- Tables below: `MyTradingSys/research/loose_code/b147_row_drop_exact.py <old_snap> <old_rows> <new_snap> <new_rows>` (old = F:\MTS\data	om_snapshots + tom_bt, new = *_head).
  Fallback stop = stop equals zone x 1.002 (short) / x 0.998 (long) within 0.011; this tolerance gives 79.3 % of old rows, the 80.7 % (and 287 of 320 proof>=5 rows) in the attribution note used a slightly looser match; the conclusion does not change.

## Result (answers the attribution note)
1. **Attribution confirmed.** Of 40401 snapshots that had a candidate in the old run and not now, **37798 (93.6 %)** had an old top candidate on the removed 0.2 % fallback stop.
   Fallback-stop rows: old 95842 of 120892 (79.3 %), new 4 of 90295 (coincidental equality). 9804 snapshots gained a candidate (net -30597).
2. **Old proof>=5 rows: 320 (105 long, 215 short). 280 used the fallback stop.** New run: 0. Of the 320, 168 snapshots still have a candidate, none at proof>=5; their new proof histogram (proof: count) is 0: 3, 1: 17, 2: 21, 3: 44, 4: 83.
3. **Old SETUP_FORMING: 19. 17 used the fallback stop; 8 of the 19 snapshots survive, at new proof 1 (x3) and 4 (x5), verdict no longer SETUP_FORMING.** New: 0.
4. New proof ceiling is 4 (379 rows). Long vs short at proof>=5 under sourced stops: **0 / 0**. SETUP_FORMING under sourced stops: 0. Tom live rule = **insufficient N (zero signals)**, not "no edge" and not an edge.
5. B135 (tom_bt_diag on regenerated rows): nothing to tabulate, all diag sections n=0. Base-rate table: proof 0: 16287, 1: 21051, 2: 38677, 3: 13901, 4: 379, 5-6: 0.
6. The old 19 signals and the old proof-5 rows must not be cited for the live rule. B147 part 4 (DSR/PBO) has no trials to deflate: skip until a rule produces N > 0.

Provenance: only existing sourced code ran; no parameter was selected or tuned.

## Kept snapshots per month (old vs HEAD Java)

| month | evaluated | kept old | kept new | lost | gained |
|---|---|---|---|---|---|
| 2022-01 | 1152 | 703 | 492 | 288 | 77 |
| 2022-02 | 2688 | 1856 | 1254 | 798 | 196 |
| 2022-03 | 2976 | 2154 | 1466 | 838 | 150 |
| 2022-04 | 2880 | 2054 | 1593 | 688 | 227 |
| 2022-05 | 2976 | 1946 | 1460 | 721 | 235 |
| 2022-06 | 2880 | 1714 | 1244 | 693 | 223 |
| 2022-07 | 2976 | 1979 | 1429 | 767 | 217 |
| 2022-08 | 2976 | 2191 | 1503 | 843 | 155 |
| 2022-09 | 2880 | 2060 | 1572 | 684 | 196 |
| 2022-10 | 2976 | 2356 | 1803 | 708 | 155 |
| 2022-11 | 2880 | 2106 | 1538 | 716 | 148 |
| 2022-12 | 2976 | 2419 | 1914 | 630 | 125 |
| 2023-01 | 2976 | 2302 | 1689 | 785 | 172 |
| 2023-02 | 2688 | 2029 | 1540 | 649 | 160 |
| 2023-03 | 2976 | 2108 | 1586 | 735 | 213 |
| 2023-04 | 2880 | 2327 | 1632 | 802 | 107 |
| 2023-05 | 2976 | 2376 | 1684 | 808 | 116 |
| 2023-06 | 2880 | 2233 | 1646 | 739 | 152 |
| 2023-07 | 2976 | 2446 | 1909 | 661 | 124 |
| 2023-08 | 2976 | 2340 | 1843 | 638 | 141 |
| 2023-09 | 2880 | 2385 | 1770 | 710 | 95 |
| 2023-10 | 2976 | 2310 | 1649 | 803 | 142 |
| 2023-11 | 2880 | 2159 | 1664 | 659 | 164 |
| 2023-12 | 2976 | 2213 | 1597 | 810 | 194 |
| 2024-01 | 2976 | 2228 | 1602 | 779 | 153 |
| 2024-02 | 2784 | 2085 | 1550 | 677 | 142 |
| 2024-03 | 2976 | 2058 | 1510 | 754 | 206 |
| 2024-04 | 2880 | 2014 | 1477 | 728 | 191 |
| 2024-05 | 2976 | 2214 | 1665 | 724 | 175 |
| 2024-06 | 2880 | 2126 | 1682 | 665 | 221 |
| 2024-07 | 2976 | 2188 | 1503 | 867 | 182 |
| 2024-08 | 2976 | 1947 | 1487 | 690 | 230 |
| 2024-09 | 2880 | 2138 | 1541 | 744 | 147 |
| 2024-10 | 2976 | 2219 | 1738 | 665 | 184 |
| 2024-11 | 2880 | 1991 | 1505 | 680 | 194 |
| 2024-12 | 2976 | 2130 | 1585 | 709 | 164 |
| 2025-01 | 2976 | 2084 | 1624 | 705 | 245 |
| 2025-02 | 2688 | 1877 | 1530 | 541 | 194 |
| 2025-03 | 2976 | 1970 | 1531 | 655 | 216 |
| 2025-04 | 2880 | 2088 | 1529 | 697 | 138 |
| 2025-05 | 2976 | 2243 | 1750 | 666 | 173 |
| 2025-06 | 2880 | 2194 | 1630 | 704 | 140 |
| 2025-07 | 2976 | 2275 | 1722 | 693 | 140 |
| 2025-08 | 2976 | 2223 | 1715 | 681 | 173 |
| 2025-09 | 2880 | 2223 | 1692 | 663 | 132 |
| 2025-10 | 2976 | 2206 | 1634 | 756 | 184 |
| 2025-11 | 2880 | 2036 | 1503 | 697 | 164 |
| 2025-12 | 2976 | 2233 | 1732 | 729 | 228 |
| 2026-01 | 2976 | 2189 | 1778 | 638 | 227 |
| 2026-02 | 2688 | 1732 | 1332 | 612 | 212 |
| 2026-03 | 2976 | 2169 | 1587 | 763 | 181 |
| 2026-04 | 2880 | 2219 | 1645 | 740 | 166 |
| 2026-05 | 2976 | 2302 | 1752 | 747 | 197 |
| 2026-06 | 2880 | 2111 | 1482 | 780 | 151 |
| 2026-07 | 2976 | 2221 | 1602 | 803 | 184 |
| 2026-08 | 2976 | 2211 | 1710 | 679 | 178 |
| 2026-09 | 2497 | 1982 | 1493 | 597 | 108 |
| **total** | | **120892** | **90295** | **40401** | **9804** |

Lost snapshots whose OLD top candidate used the 0.2 % fallback stop: 37798 of 40401 (93.6 %).

Rows with the fallback stop: old 95842 of 120892 (79.3 %), new 4 of 90295 (0.0 %).

## Proof histogram (top candidate per kept snapshot)

| proof | old | new |
|---|---|---|
| 0 | 10831 | 16287 |
| 1 | 20373 | 21051 |
| 2 | 39105 | 38677 |
| 3 | 39496 | 13901 |
| 4 | 10767 | 379 |
| 5 | 320 | 0 |

## Long vs short at proof>=5

| run | long | short | SETUP_FORMING |
|---|---|---|---|
| old | 105 | 215 | 19 |
| new | 0 | 0 | 0 |

## Verdict counts

| verdict | old | new |
|---|---|---|
| SETUP_FORMING | 19 | 0 |
| WAIT_PROOF | 17810 | 35858 |
| WAIT_RR | 80847 | 26932 |
| WAIT_TRIGGER | 16232 | 24287 |
| WATCH | 5984 | 3218 |
