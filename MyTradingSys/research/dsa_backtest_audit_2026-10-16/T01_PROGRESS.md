# T01 progress (crash-safe)

worktree: C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629
host: JIS-NUC
card: dsa-audit-01-data-forensics
claim: dsa-audit-01-data-forensics
start_utc: 2026-10-16T06:29Z

## Steps
1. inventory      - DONE (result #29, #33, #35). data_inventory.csv written. Extra inventory also done.
2. bar invariants - DONE (result #37, #44). 1,313,280 DEV bars: 0 OHLC/taker/quote/size violations; 182 frozen; 3 close->open jumps >0.5%.
3. cross-source   - DONE (result #48). 912 DEV days with 1m coverage; OHLC exact; volume mismatch on 10 days, worst +13.6%.
4. loader torture - DONE (result #39, #41). Table built.
5. impact         - DONE (in report).
6. delta sign     - DONE (result #44). Consistent.

## Files written (scripts/T01/)
- inventory_klines.py, inventory_extra.py
- invariants_dev.py
- loader_torture.py, loader_torture_more.py
- cross_and_delta.py, resample_cross.py
- out/data_inventory.csv

## Report
- T01_data_forensics.md: being written next.

## Findings so far
- F1 10,080 duplicate 1m rows in tom_raw/klines (2025-09-01..07, out of DEV). S2.
- F2 bt_data.load_klines accepts microsecond-stamped row silently. S3.
- F3 bt_data.load_klines: keeps first duplicate, silently sorts unsorted input, no gap check. S3.
- F4 funding non-8h adjacent transitions: 4541 of 7394 pairs. SUSPECTED. S3.
- F5 1m->1d volume mismatch on 10 DEV days, worst +13.6% (2023-11-10). S2.
- F6 182 frozen bars (h==l, v==0) on DEV. S3.
- F7 3 close->open jumps >0.5% on DEV. S3.
- F8 funding tail stamp .002 ms (2026-09-30T16:00:00.002). S3.
- F9 tom_snapshots 57 files, last_ts 2025-12-07 (brief says 114 files). S3.
- F10 krown_daily missing on NUC. Lead L10 BLOCKED on this host.

## Next
- Write T01_data_forensics.md
- Card F1, F5 via tasks.py new
- Commit + mts-ship + release + tasks.py done

## Bridge log (results seen)
10,11,14,15,19,20,21,22,23,24,29,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48 = OK
12,13 = path error (Set-Location truncated by shell)
16,17,18 = not_run (over 6-block cap)
25,26,27,28 = not_run (over cap, sent 9 again)
30,31 = not_run (I sent while pending)
49 = refused (duplicate edit)
50 = OK (duplicate rerun)
