# Live Aid idea-flag groups, full-history test (2026-11-13)

**VERDICT: 0 of 30 cells pass. No idea-flag group has an edge; none goes to a testnet-forward run.** Rule, data, split, fee, placebo and correction as frozen in PRE_REG.md (committed before any outcome). The Live Aid code ran unchanged (66,559 idea events on BTC 5m, 2019-01..2026-11; 66,554 scored, 5 skipped for a gap); no parameter was searched.

Regime mix: up 41.1 % / down 32.2 % / range 26.8 % (BTC, all days; rule in PRE_REG). VALIDATION = days from 2024-07-02 (last 30 %). Fee 4 bps round trip, 60-min time exit. PASS needs n >= 100, fee-net CI lower bound > 0, beats the same-day random placebo (* = beats its p95), and survival of Benjamini-Hochberg at 10 % over all 30 cells (bootstrap p, day blocks). Cells overlap (an event sits in idea, its state group and its fade group), so the 30 are not independent; BH stays valid under that positive dependence.

| group | side | VAL n | hit % | fee-net bps [95 % CI] | placebo p (* beats p95) | boot p, BH survive | verdict |
|---|---|---|---|---|---|---|---|
| idea | LONG | 10096 | 50.9 | -4.2 [-5.5, -2.8] | 0.77 | 1.000 n | FAIL |
| idea | SHORT | 10669 | 49.3 | -5.3 [-6.6, -4.0] | 1.00 | 1.000 n | FAIL |
| idea REJECTED | LONG | 3443 | 51.9 | -5.1 [-7.4, -2.9] | 0.57 | 1.000 n | FAIL |
| idea REJECTED | SHORT | 3726 | 51.3 | -5.5 [-7.6, -3.4] | 0.51 | 1.000 n | FAIL |
| idea ACCEPTED | LONG | 3297 | 49.2 | -3.6 [-5.7, -1.6] | 0.93 | 0.999 n | FAIL |
| idea ACCEPTED | SHORT | 3378 | 48.1 | -5.2 [-7.3, -3.2] | 1.00 | 1.000 n | FAIL |
| idea FAILED BREAK | LONG | 3356 | 51.6 | -3.7 [-5.7, -1.7] | 0.38 | 1.000 n | FAIL |
| idea FAILED BREAK | SHORT | 3565 | 48.4 | -5.1 [-6.8, -3.3] | 0.90 | 1.000 n | FAIL |
| idea fade @ Day open | LONG | 1877 | 50.6 | -6.1 [-8.4, -3.9] | 0.98 | 1.000 n | FAIL |
| idea fade @ Day open | SHORT | 1989 | 50.1 | -4.0 [-6.3, -1.7] | 0.69 | 1.000 n | FAIL |
| idea fade @ 2-day-ago low | LONG | 476 | 54.6 | -5.0 [-10.4, +0.4] | 0.25 | 0.967 n | FAIL |
| idea fade @ 2-day-ago low | SHORT | 448 | 49.1 | -6.2 [-12.7, +0.1] | 0.91 | 0.973 n | FAIL |
| idea fade @ 2-day-ago high | LONG | 399 | 50.9 | -1.3 [-7.9, +6.0] | 0.25 | 0.655 n | FAIL |
| idea fade @ 2-day-ago high | SHORT | 536 | 46.8 | -9.0 [-13.5, -4.5] | 0.84 | 1.000 n | FAIL |
| idea fade @ Asia low | LONG | 979 | 51.3 | -3.2 [-6.7, +0.3] | 0.00* | 0.964 n | FAIL |
| idea fade @ Asia low | SHORT | 503 | 50.1 | -2.1 [-7.5, +3.8] | 0.90 | 0.770 n | FAIL |
| idea fade @ Asia high | LONG | 456 | 49.8 | -4.5 [-10.4, +1.0] | 0.99 | 0.943 n | FAIL |
| idea fade @ Asia high | SHORT | 1124 | 51.2 | -5.3 [-8.8, -1.9] | 0.06 | 0.999 n | FAIL |
| idea fade @ Yesterday low | LONG | 643 | 51.8 | -7.8 [-13.4, -2.2] | 0.60 | 0.997 n | FAIL |
| idea fade @ Yesterday low | SHORT | 311 | 48.2 | -8.6 [-15.1, -2.3] | 1.00 | 0.996 n | FAIL |
| idea fade @ Yesterday high | LONG | 446 | 45.7 | -6.7 [-11.4, -1.9] | 1.00 | 0.997 n | FAIL |
| idea fade @ Yesterday high | SHORT | 814 | 53.7 | -3.9 [-7.6, -0.2] | 0.02* | 0.982 n | FAIL |
| idea fade @ Europe low | LONG | 833 | 56.8 | -1.4 [-6.1, +3.3] | 0.00* | 0.715 n | FAIL |
| idea fade @ Europe low | SHORT | 317 | 47.0 | -4.5 [-10.4, +1.4] | 0.97 | 0.932 n | FAIL |
| idea fade @ Europe high | LONG | 378 | 51.1 | +0.6 [-4.7, +6.1] | 0.21 | 0.415 n | FAIL |
| idea fade @ Europe high | SHORT | 949 | 47.7 | -7.6 [-11.9, -3.3] | 0.74 | 1.000 n | FAIL |
| idea fade @ Last week low | LONG | 135 | 53.3 | -8.1 [-21.1, +4.1] | 0.58 | 0.899 n | FAIL |
| idea fade @ Last week low | SHORT | 135 | 52.6 | -0.6 [-9.8, +8.4] | 0.28 | 0.561 n | FAIL |
| idea fade @ Last week high | LONG | 177 | 58.2 | -2.6 [-13.0, +8.0] | 0.51 | 0.673 n | FAIL |
| idea fade @ Last week high | SHORT | 165 | 49.7 | -8.9 [-16.5, -1.8] | 0.55 | 0.992 n | FAIL |

## Reading the table
- Fee-net mean is negative in 29 of 30 cells; the only positive one is Europe high LONG (+0.6 bps, CI [-4.7, +6.1], p 0.415), nowhere near significant. The corrected survivors are zero, and the smallest bootstrap p over all cells is 0.415, so the correction was not even the binding gate: no cell has a fee-net CI above 0.
- Three cells beat the same-day placebo (Asia low LONG, Yesterday high SHORT, Europe low LONG; Asia high SHORT misses at p 0.06). The placebo is a same-day random entry that pays the same 4 bps, so it sits near -4 bps; beating it while still losing money is not an edge.
- Hit rates of 54-58 % (2-day-ago low LONG, Last week high LONG, Europe low LONG) carry n 135-833 and fee-net bps of -1.4 to -5.0: the gross move is smaller than the fee. At 4 bps round trip a 1h time exit needs about +4 bps gross just to break even.
- Europe high rows reproduce the earlier study exactly (LONG n 378, SHORT n 949); the learner's 60 % was chance.

## What Live Aid should do
- Stop showing as signals (BTC-measured, all FAIL): idea (all), idea REJECTED / ACCEPTED / FAILED BREAK, and every `idea fade @` group (Day open, 2-day-ago low/high, Asia low/high, Yesterday low/high, Europe low/high, Last week low/high), both sides. Keep them as drawn levels and context only.
- Retire the 28-day keep/drop table as a decision source: `live_aid_learn.py` verdicts (n >= 30, 10 points from 50 %) are not evidence of fee-net edge.
- Testnet-forward run: none from this set. ETH and SOL replication was not run because nothing passed on BTC.

## Not covered
- `setup` and `timing` groups (2 of the learner's 17): their code needs 1m/2m/3m lanes, 1h/4h RSI votes and VWAP, and the full-history data on disk is 5m; they stay "28-day descriptive only" until a 1m BTC history is loaded.
- Only the 60-min time exit, no stop or target, entry at the next 5m open; other horizons, stops or context filters (analyst levels, MA levels, which the page merges but the replay cannot) were not tried and would be new trials.
- Cells with n < 100 would be UNDERPOWERED (none occurred; smallest n is 135). Funding and slippage excluded (4 bps is the optimistic bound; 10 bps is worse for every cell).
- Spot 2019 and perp 2020+ are pooled (src switch not split here; in the Europe-high study both sources were negative).
- Files: `cells_BTC.json` (all numbers incl. DEV mean, 10 bp mean, placebo p95), `REPORT_RAW_BTC.md` (run output), `run.py`, `replay_events.js`, `test_run.py`.
