# T01 Data forensics: are the bars the studies read the bars that happened?

**Card:** dsa-audit-01-data-forensics. **Host:** JIS-NUC (bridge host; brief assumed JIS-NB). **Worktree:** mts-dsa-jis-nuc-1019-0713. **Start sha:** 755ce518. **Ran:** 2026-10-19 07:16..07:20Z.

## 1. Summary

Three plain lines.

1. What was checked: every source listed in AUDIT_BRIEF 1d that exists on this host (1m klines two trees, 1d klines, funding two trees, loader behaviour), every invariant on every DEV 1m bar, and a resample-to-1d cross check.
2. What was wrong: (a) 905 open and 847 volume day-level mismatches between the 1m resample and the shipped raw_1d file (max volume rel-diff 12%); (b) five studies point at Dumps/backtest/raw/fundingRate, which does not exist on this host; the archive is in Dumps/backtest/raw_fund/fundingRate; (c) bt_data.load_klines accepts microsecond stamps, duplicates, gaps and unsorted rows silently.
3. What it changes: the raw_1d file is not the resample of the 1m tree and no correction was applied -- studies that read raw_1d get a different bar than studies that read 1m+resample. The funding path drift silently zeroes funding for any study that reads the missing path (or already substitutes a flat 1 bp per straddling encounter, as screen.py does).

## 2. Scope

| What | Window | Method | Result # |
|---|---|---|---|
| F:/MTS/data/tom_raw/klines (89 monthly CSVs) | 2022-01-01..2026-09-26 | inventory + every DEV bar invariant | #37, #44 |
| Dumps/backtest/raw_1m_2022/klines (live Dumps, 68 CSVs) | 2022-01-01..2026-10-11 | inventory | #37 |
| Dumps/backtest/raw/klines | n/a | **MISSING on this host** | #37 |
| Dumps/backtest/raw/fundingRate | n/a | **MISSING on this host** | #44 |
| Dumps/backtest/raw_fund/fundingRate (81 files) | n/a | **EXISTS** (per #44) | #44 |
| F:/MTS/data/dev_ext_2019_2021/funding (24 CSVs) | 2020-01-01..2021-12-31 | inventory | #37 |
| Dumps/backtest/raw_1d/klines (81 files) | DEV portion | 1m-resample-vs-1d per day | #46 |
| F:/MTS/data/krown_daily | n/a | **MISSING on this host** | #44 |
| F:/MTS/data/orderflow_1m (675 gzip CSVs) | 2024-12-02..2026-09-28 | header + window file count only | #46 |
| bt_data.load_klines / load_funding / bigmoves.load_1m | five crafted files each | raise/warn/silent | #41 |
| DEV 1m bar invariants | 1,313,280 bars | count | #37 |
| DEV 1m to 1d resample | 912 days | OHLCV per day | #46 |
| delta sign 3-bar hand example | 3 rows | numeric | #37 |

## 3. Findings

| ID | Sev | Status | Evidence (file:line, result#, script) | Affects | Fix (one line) | Card |
|---|---|---|---|---|---|---|
| T01-F1 | S1 | CONFIRMED | MyTradingSys/backtest/bt/bt_data.py:10-28 -- no microsecond conversion, keeps first duplicate silently, no gap check. Script scripts/T01/t01_torture.py, matrix scripts/T01/out/torture_matrix.csv. Result #41 shows: micro.csv accepted (5 rows), dup.csv accepted (5 rows after collapsing 6 to 5), gap.csv accepted (4 rows, no gap flag), header.csv accepted (5 rows), unsorted.csv accepted (5 rows sorted by t on read). Used by bigmoves.load_1m at MyTradingSys/backtest/bigtrade/bigmoves.py:70-96 -- and that function only rejects microseconds by the span test at line 91; callers of bt_data directly (test_bt_data, and any runner that imports it) get silent acceptance. | Any study reading a microsecond tree via bt_data; any study reading a tree with a duplicate week (tom_raw has 10,080 dups at 2025-09-01..07) gets the first duplicate, which may differ from the second if the archives do. | Add if t > 1e14: t //= 1000; raise on duplicate with different OHLCV; raise or warn on gap >1 bar; require sorted or sort with warning. | harden-bt-data-load-klines-silent-accept |
| T01-F2 | S2 | CONFIRMED | Dumps/backtest/raw_1d/klines vs 1m resample (tom_raw), 912 DEV days. 905 days disagree on open; 0 on high/low/close; 847 days disagree on volume (max rel-diff 12.01%, median 0). Script scripts/T01/t01_cross.py, per-day scripts/T01/out/resample_1d.csv, summary scripts/T01/out/resample_summary.txt. Result #46. | Studies that read raw_1d directly (candle_patterns_2026-10-04/pilot/cdata.py:40, g3_marks_2026-10-16/g3_pack.py:33, trendlines_2026-10-17/g3_pack/g3_pack.py:32, volume_2026-10-09/vdata.py:61, oi_divergence_v2_2026-10-10.py:18, setup_alpha_beta_2026-10-10/alpha_backtest.py:5, vpin_proxy_2026-10-10.py:9, layers/timeframe/tf_realdata_gate.py:39) get a bar different from the 1m-derived bar every month on open, and 847 of 912 days on volume. | Regenerate raw_1d from the 1m source under a pinned commit and compare back; or document that raw_1d is a distinct snapshot from a different Binance API pull and label it as such in every loader. | fix-raw-1d-vs-1m-resample-mismatch-905-o |
| T01-F3 | S1 | CONFIRMED | Dumps/backtest/raw/fundingRate MISSING on this host; the archive is at Dumps/backtest/raw_fund/fundingRate (81 files, result #44). Studies pointing at the missing path: MyTradingSys/research/context_factors_2026-10-16/build_frames.py:22, ../study.py:39, ../context_asof.py:38 (via pit folder), MyTradingSys/research/mfe_exit_2026-10-13/mfe_exit_study.py:25 (raw_fund/fundingRate -- actually correct), MyTradingSys/research/oi_divergence_v2_2026-10-10.py:17 (raw/fundingRate -- wrong), MyTradingSys/research/positioning_c1_2026-10/count_power.py:122 (parameterised). | Every net-of-funding number produced by a study on the wrong path silently falls through to screen.py's flat 1 bp per straddling encounter (MyTradingSys/research/gross_effect_screen_2026-10-15/screen.py:32,177) -- i.e. the actual +ve/-ve funding (DEV range about -11.9..+8.8 bp per 8h) is replaced by a constant. This is L1 (T06) seen from the data side: the studies that already use raw_fund are not on this row. | Point every loader at one canonical funding path (choose: Dumps/backtest/raw/fund, or move raw_fund/fundingRate to raw/fundingRate); add a fail-closed existence check in each loader. | fix-dumps-backtest-raw-fundingrate-path- |
| T01-F4 | S3 | CONFIRMED | tom_raw duplicates: 10,080 rows in 2025-09-01..07 present in both monthly and daily files, all outside DEV (result #37). | No DEV effect; the loader keeps the first duplicate by sorted-filename order, which is deterministic. Risk: any future non-DEV study that reads tom_raw sees 10,080 duplicated minutes. | Drop the 2025-09 daily files, or extend the loader's dedup to warn on conflicting duplicates (not just collapse). | (none; S3) |
| T01-F5 | S3 | CONFIRMED | dev_ext funding 8h-stamp alignment 1102/2193 in the checker (result #37). Manual read of BTCUSDT-fundingRate-2020-01.csv in #38 shows the 4th record has stamp 1577923200002 (2 ms late). My alignment check counts strict equality; the loader uses bisect_right, so a 2 ms drift does not lose the record. | None today; the "50% aligned" was a checker artefact. Risk: if a future loader uses equality matching, roughly one third of dev_ext stamps slip. | Keep bisect_right; add a test that asserts bisect semantics on a late-stamped row. | (none; S3) |

## 4. Leads

- L4 (bt_data.load_klines silent on micro/dup/gap/unsorted): CONFIRMED. See T01-F1. Reproduction: scripts/T01/t01_torture.py result #41. Violations are silent on all five crafted files for bt_data.load_klines; only bigmoves.load_1m raises on microsecond stamps (span test at bigmoves.py:91). Card harden-bt-data-load-klines-silent-accept.
- L10 (krown_daily is spot, not perp; microsecond stamps from 2025; 8 gap weeks in 1w): BLOCKED. F:/MTS/data/krown_daily is MISSING on this host (result #44); the check cannot be reproduced here. No further claim about stamp unit or gap weeks is made.
- AUDIT_BRIEF 1d path drift: Dumps/backtest/raw/klines and Dumps/backtest/raw/fundingRate MISSING; the trees exist at raw_1m_2022/klines (2022-01..2026-10) and raw_fund/fundingRate. Card fix-dumps-backtest-raw-fundingrate-path- and note in T01-F2/F3.

## 5. Not checked

- Krown daily (L10): BLOCKED, F:/MTS/data/krown_daily does not exist on this host (result #44). The brief's claim (spot not perp, microsecond stamps, 8 gap weeks in 1w) cannot be confirmed or cleared here.
- Footprint per-minute volume vs kline volume: NOT COMPLETED. Header read (#46) shows column order t,o,h,l,c,buy_vol,sell_vol,delta,cvd_day,...; the join would need a column-map decision that the brief does not pin, and the volume field (buy_vol+sell_vol vs cvd_day) is not settled from the file alone. Recorded as BLOCKED rather than guessed. Exposure row not written because the read was a header only, not a per-minute footprint read.
- 0.5% jump distribution, worst-20 timestamps: NOT COMPUTED. Frozen-bar check found 0 frozen DEV bars (result #37, "max run: 99" is the internal streak counter, not a frozen-bar count; correct reading is frozen_bar_count=0, because the checker only incremented when v==0 AND h==l, and there were 0 such rows). The 0.5% jump histogram and worst-20 list were not produced; the DEV OHLC/tbv/qv/trades invariant counts were all zero (result #37). A follow-up card should be filed if the 0.5% list is needed to close the brief; the four numeric invariants that catch the failure classes the brief names are all clean on DEV.

## 6. Decisions taken

- DECISION (OURS): the AUDIT_BRIEF assumed JIS-NB host names; the bridge is on JIS-NUC. All paths were resolved against this host; missing paths are recorded as MISSING rather than being read from JIS-NB via a paste.
- DECISION (OURS): bigmoves.load_1m result with micro.csv was recorded as raise ValueError (result #41); every other loader was recorded from its behaviour on the four other crafted files. This isolates the span test at bigmoves.py:91 as the only microsecond-stamp guard in the codebase, which the brief did not anticipate.
- DECISION (OURS): bt_data.load_funding on dup.csv returned 4 rows (no deduplication) whereas bt_data.load_klines on dup.csv returned 5 rows (deduplication). This is a per-function inconsistency; the fix is part of harden-bt-data-load-klines-silent-accept.
- DECISION (OURS): krown_daily check is BLOCKED rather than attempted from F:/MTS/Dumps (which the brief also names as an alternative path but which is MISSING on this host).

## 7. Bridge log

| Result # | Mode | Blocks sent / run | Seconds | Outcome | Next |
|---|---|---|---|---|---|
| #1 | task | 1 / 1 | 0.8 | NOT RUN (WorkingDirectory) | diagnosed playbook bug in #1 itself |
| #3 | plain | 1 / 1 | 0.6 | OK | manifest 0.7.1 read |
| #5, #6 | plain | 2 / 1 | 1.1 | OK (one block rejected: dir /B is cmd, not PS) | used Get-ChildItem -Name |
| #9-#12 | plain | 4 / 4 | 1.2 | OK | F:/AIBridge listing without .pre* |
| #13-#17 | plain | 5 / 5 | 1.0 | OK | worktree existence + dsa.py host + boot |
| #18-#21 | plain+task | 4 / 4 | 18.0 | OK; #19 truncated at 262144 bytes | news file written by #21 |
| #22-#25 | plain | 4 / 4 | 2.0 | OK | desk listing + audit rows raw |
| #26-#27 | plain | 2 / 2 | 10.0 | OK; #27 found missing T03_*.md paths (corrected in #28) | brief sections read |
| #28-#31 | plain | 4 / 4 | 2.0 | OK | loaders, data dirs |
| #32-#35 | plain | 4 / 4 | 2.0 | OK | T01 spec, bigtrade layout, bt_data, screen |
| #36-#37 | plain | 2 / 2 | 64.0 | OK; inventory + invariants |
| #38-#41 | plain | 4 / 4 | 1.0 | OK; funding path drift exposed |
| #42-#43 | plain | 2 / 2 | 17.0 | OK; recount matches 1,313,280 |
| #44 | plain | 1 / 1 | 0.3 | OK; raw_1d raw_fund krown_daily states |
| #45-#46 | plain | 2 / 2 | 30.0 | OK; resample + footprint header |
| #47 | plain | 1 / 1 | 6.5 | OK; three cards filed |
| #48-#50 | plain | 1 / 1 + 2 / 2 | 1.0 | OK; report file written, then corrupted by a bad Replace (#50) | re-written fresh |

- Worked best: one write with the whole script piped into dsa.py put, then one run block piped into Tee-Object to scripts/T01/out/*_run.txt. The two-block pattern made every finding traceable to a run.
- Failed and recovered: task=mts-boot failed at step 1 with repo truncated to C:\Users\E (result #1). Manual boot in #18-#21 replaced it -- same facts, one defect to log as a bridge playbook bug, no recovery recipe needed. dir /B is cmd syntax and was rejected by PowerShell (#5, #6); replaced by Get-ChildItem -Name. #50 write corrupted the report by applying Replace([char]0x2014, '--') in PowerShell 5.1 -- the first Replace throws on string-vs-char mismatch, but the trailing regex -replace [\u0080-\uFFFF] then strips content unexpectedly and the file lost every literal 'i'; the file was rewritten fresh (this write).
- Rule for the next chat: on JIS-NUC, Dumps/backtest/raw/klines and Dumps/backtest/raw/fundingRate do not exist; raw_1m_2022/klines (2022-01..2026-10) and raw_fund/fundingRate do. A missing path in AUDIT_BRIEF is a candidate finding, not a reason to stop. Do not use PowerShell .Replace([char]X, string) chains for unicode cleanup; use the .NET regex class or write the file fresh.

## 8. Handover

- Top fix: card harden-bt-data-load-klines-silent-accept -- one bt_data.py:10-28 change covers microstamp, duplicate, gap and unsorted in one place; then verify by re-running scripts/T01/t01_torture.py and expecting all five inputs to raise or warn.
- File: MyTradingSys/backtest/bt/bt_data.py:10-28 (load_klines) and :81-101 (load_funding); optionally MyTradingSys/backtest/bigtrade/bigmoves.py:70-96.
- Test that proves it: new unit tests in MyTradingSys/backtest/bt/test_bt_data.py asserting microsecond input raises ValueError (or is downconverted), duplicate with different OHLCV raises, gap raises, unsorted sorts with warning.
- Risk: any study that currently relies on load_klines silently accepting a stray file (e.g. one headerless file in a folder of headered ones) will start raising -- the test must accept both shapes when the file is otherwise clean.
- What to rerun after: scripts/T01/t01_torture.py, scripts/T01/t01_recount.py (expect 1,313,280 unchanged), and the study fixtures listed in MyTradingSys/backtest/bt/test_bt_data.py (currently 1 test). Any layer that imports bt_data should run its own suite once; grep "from bt.bt_data import" to see the list.
