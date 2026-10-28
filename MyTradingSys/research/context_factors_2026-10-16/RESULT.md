INCONCLUSIVE

# RESULT: operator context composite C vs context-matched controls, BTCUSDT 1h decisions, daily-candle stop-ladder trade, DEV only, one run

Verdict above is per PRE_REG.md s.4, applied verbatim. Run 2026-10-16T05:11Z. PRE_REG.md sha256 `bd56a752d327a5cd6d2074d2f8e7364e0a015041f012532d9a381ae8ee9f1c34` (frozen at commit 3e961c2f, unchanged); context_asof.py sha256 `efa3513f738337ebd48d09806b936fdef186092c14bb5b18c4df1c4415e49401` (same commit). Trade: entry at the open of the 1m bar opening at T + 60 s, ladder stop (prior D / 12h / 8h extreme), 2 R target, 24 h time stop, 7 bp per side, realised funding. net_R in R.

## READ cell: C pooled (long + short; the short trade's P&L is already sign-flipped in net_R)

| item | value |
|---|---|
| C events (counted, PRE_REG s.2) | 1010 events / 456 days (long 554/254, short 456/202): MATCH |
| executed C trades | 1010 |
| matched C events (>= 10 controls) | 241 on 164 UTC days (need >= 387) |
| trigger effect E (mean of event net_R minus mean of its controls' net_R) | -0.0233 R |
| day-clustered SE of E | 0.0739 R |
| t = E / SE | -0.32 |
| two-sided p / Holm-adjusted p (m = 37) | 0.7525 / 1 |
| MDE of this cell (2.8 x SE) | 0.2070 R |
| mean net_R of C, all executed trades (SE day-clustered) | -0.1367 (0.0426) over 1010 |
| mean net_R of C, matched events only | -0.1392 (0.0738) over 241 |
| E by year (matched events): 2022 Apr-Dec / 2023 / 2024H1 | -0.0585 (n 86) / -0.1269 (n 78) / +0.1209 (n 77) |
| max drawdown of cumulative net_R: C matched / C all executed / controls' mean path (matched) | 39.45 R / 142.24 R / 27.96 R |

Gate by gate:

- NO : matched days >= 387
- NO : E > 0
- NO : |t| >= 3.205 (Holm m=37, p <= 0.05)
- NO : mean net_R of C > 0 (all executed C trades AND matched C trades)
- NO : E > 0 in 2022, 2023 and 2024H1
- NO : MDD(C) <= MDD(matched controls' mean path) (matched events AND all executed C trades)

Week-clustered SE of E 0.0671 R, t_week -0.35 (day-clustered t -0.32). 

## Report-only rows (printed beside the READ cell, no verdict, never a gate)

| row | n matched events | days | E (R) | SE | t |
|---|---|---|---|---|---|
| E, long only | 103 | 77 | -0.0485 | 0.1063 | -0.46 |
| E, short only | 138 | 87 | -0.0045 | 0.1020 | -0.04 |

- Maker-in readout (0.09 % round trip: 2 bp on entry instead of 7 bp): mean net_R of C (all executed) -0.1078 R; E -0.0326 R (SE 0.0738). Never rescues a FAIL.
- Context-only line (matched controls' mean net_R minus the mean net_R of the whole tradeable ledger, both sides, 5598 trades): -0.0408 R (SE 0.0220).
- Controls: 3065 draws, each distinct control used 2.5x on average (heavy reuse understates the SE when above 5).
- Skipped / flagged: entry_beyond_stop 0, no_entry_bar 0, no_context 0, too_few_controls (< 10) 769, cut_at_split_end 0 (24 h window runs past 2024-06-30 23:59; exit at the last DEV 1m close), short window not at split end (data gap) 0.
- Exit mix, C executed trades: stop 348, target 114, time 548. Controls (all draws): stop 1181, target 513, time 1371.
- Matching diagnostics (counts only, independent of any outcome): long: C events with a defined key 554, with >= 10 pool candidates in their key cell (before spacing) 103, median candidates 6, key cells with a C event 179; short: C events with a defined key 456, with >= 10 pool candidates in their key cell (before spacing) 138, median candidates 7, key cells with a C event 186.
- Pools: long: ledger 2817, C 554, excluded within 24 h of C 816, pool 1447; short: ledger 2781, C 456, excluded within 24 h of C 621, pool 1704.

## Cells not read (PRE_REG s.4): REFUSED_POWER, no number computed or looked at

| cell | days available | verdict |
|---|---|---|
| C long only | 254 | REFUSED_POWER |
| C short only | 202 | REFUSED_POWER |
| every single factor value, each side (F1-F7, 24 factors, 86 values) | largest bucket 768 | REFUSED_POWER |
| candle confidence (O2) as a condition | not in C | REFUSED_POWER |

The two per-side E lines above are the s.4 'E per side' print-beside rows of the READ cell; they carry no verdict.

## DECISION (OURS) lines (details PRE_REG s.0-8 left open; each is the conservative or the literal reading)

- Funding data: `F:/MTS/data/candle_close_dev_2022_2024` does not exist on this machine (JIS-NB). The same Binance monthly fundingRate series (identical columns) is read from `F:/MTS/Dumps/backtest/raw/fundingRate/*.csv`, months 2022-01..2024-06, settlements before 2024-07-01. Funding is not part of C; it enters only net_R (and the unused `f7_funding` frame column, built by `build_frames.py` with that loader).
- Frames were built by the frozen `run_dev.py vec` through `build_frames.py` (a wrapper that only swaps the funding loader; no frozen file was edited, context_asof.py sha unchanged).
- Stop price = close x (1 -+ f3_stop_pct/100) of the T row, rounded to the archive's 0.01 grid (off-grid error < 1e-6 asserted).
- Entry beyond the stop = entry at or past the stop (R <= 0 on the wrong side); skipped.
- Funding: a settlement counts when entry-bar open <= settlement time < end of the exit bar; funding term = sign x sum of rates x entry.
- Controls pool = tradeable-ledger events (valid ladder stop, entry bar present, entry not beyond stop, context key defined) of the same side, not in C, not within 24 h (inclusive) of any C event of that side. One `default_rng(0)` per side, C events in time order, candidates shuffled, K = 20 without replacement, spacing > 4 h, kmin = 10.
- Mean net_R of C > 0 is required both over all executed C trades and over the matched events; the MDD gate is required both on the matched events and on all executed C trades against the controls' mean path (cumulative sum in time order). Where the text allows two readings the stricter one gates.
- Holm: m = 37, p two-sided from the normal approximation; the |t| >= 3.205 rule gates.

## Provenance

- Counts: `python study.py counts` printed C long 554/254, short 456/202, pooled 1010/456 before any outcome: MATCH PRE_REG s.2.
- DEV data: 1m archive F:/MTS/data/tom_raw/klines; 1313280 bars with open < 2024-07-01; missing 1h grid hours filled: 0.
- Files: ledger_C.csv (every C event, executed or skipped), controls.csv (every control draw), EXPOSURE_LEDGER.csv, VERDICTS.csv row (kill scope PRE_REG s.5).

## Why INCONCLUSIVE: the matched-days gate failed on counts alone

- The verdict is set by the first line of the s.4 rule: matched days 164 < 387. The matching depends only on the context keys and on pool membership, never on an outcome: a plumbing run with RANDOM P&L (`python study.py smoke`, run before this one) printed the same 241 matched events / 164 days before any real outcome was computed.
- Cause: the PRE_REG pool is the same-side ledger events outside C and more than 24 h from any C event: 1,447 long and 1,704 short events spread over 216 key cells (24 hours x 3 vol terciles x 3 trend tags). The median C event has 6 (long) or 7 (short) candidates in its key cell, and kmin is 10, so 769 of the 1,010 C events found fewer than 10 controls and are dropped (counted above as too_few_controls). The s.4 power row used the 456 unmatched C days; matching attrition was not counted before the freeze.
- Per the rule this is INCONCLUSIVE, never FAIL, and it kills nothing (kill scope: none). VERDICTS.csv carries it as one_run = yes, so this PRE_REG is not re-run; a successor must say why it is a different design (a pool large enough for kmin, for example all same-side decision hours with the same key as `context_null.run` draws them, instead of ledger events only; power recomputed on matched days). DEV outcomes of C are now read, so a powered successor needs a fresh read (VALIDATION, by a separate card after a PASS, as s.6 says).
- What the numbers do say, descriptively and without a verdict: E = -0.023 R with SE 0.074 R (MDE 0.207 R) on 241 matched events cannot separate a 0.375 R effect from zero or from a small negative one; and the whole composite, all 1,010 executed trades, averages -0.137 R per trade all-taker (SE 0.043; -0.108 R maker-in), 114 targets / 348 stops / 548 time exits.

## Test record (test_study.py, CI-safe, no market data)

- 22 tests: 14 hand-fixture checks (target, stop first when a bar holds both, long and short, gap through the stop fills at the open, target gap fills at the target, entry bar can stop, 24 h time stop at the close of the 1440th bar with the next bar ignored, stop on the last window bar, cut window, entry beyond stop skipped, cost 7 bp per side in R, funding sign), the entry-bar index (T + 60 s, never the bar at T), the funding window, and 4 planted-bug cases. Expected values are hand-computed from PRE_REG s.1-2, not from the code.
- Fails on old code: before `entry_index` existed in study.py the file ran 1 failed / 21 passed (AttributeError). Planted bug: a copy of study.py with the stop-first test changed to target-first, run through `STUDY_UNDER_TEST=<copy> pytest test_study.py -k test_real_simulator`, gave 2 failed (chk_stop_first_long, chk_stop_first_short) / 12 passed. In-file, `test_planted_bug_is_caught` checks that target-first, no-gap-fill, 1441-bar window and an unflipped short funding sign each fail at least one fixture check.
- Honest order note: a first draft of the simulator existed in study.py before test_study.py was written (counts check came first, as the card orders); the fixture numbers were then computed by hand from the PRE_REG, and the planted-bug runs are the evidence the fixture can fail.

## Files added by this session

study.py, test_study.py (registered in scripts/dev/run_extra_tests.py), build_frames.py (funding-loader wrapper around `run_dev.py vec`), ledger_C.csv, controls.csv, EXPOSURE_LEDGER.csv, RESULT.md, one VERDICTS.csv row. Nothing frozen was edited (PRE_REG.md, context_asof.py, counts.py, run_dev.py, context_null.py unchanged). No VALIDATION or HOLDOUT bar was read (1m bars end 2024-06-30 23:59; settlements before 2024-07-01).
