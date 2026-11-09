Verdict: T02=INCONCLUSIVE (7-star MTF long, n=7 DEV, net +1.06 R +- 1.01, screen not passed) T03=INCONCLUSIVE (5-star MTF long, n=8 DEV, net +0.07 R +- 0.51, screen not passed)

# eh-h2-malkan-star-grades: Malkan 5-star and 7-star MTF RSI long grades (BTC, ETH daily)

Plain words: the grades are rare. Over DEV (signals 2018-10-01..2024-06-30) the 7-star rule (T02) fired 8 times and the 5-star rule (T03) 9 times across BTC and ETH. That is far below the n >= 30 the DEV screen needs, so neither trial can be read as an edge or as a non-edge. The point estimates are positive for both (T02 +1.06 R, T03 +0.07 R), but the standard errors (1.01 and 0.51 R) are wider than the means. The 7-star result is driven by two large winners (2020-09-09 BTC +3.81 R, 2021-06-26 ETH +3.98 R). VALIDATION was not read, because the DEV screen was not passed (the rule requires that). Nothing is promoted. No testnet-forward card is filed. The honest next step is not a longer backtest on these rules: they cannot reach power on daily BTC and ETH from 2017 to 2024. The question stays open and is recorded as INCONCLUSIVE.

## Context
- Regime: research_kit-style weekly tag on DEV (BTC): bull 24 %, range 74 %, bear 0 %, n/a 2 % (see Regime mix).
- Phase: DEV pooled 2018-10..2024-06. Not split by cycle phase (that is eh-o2's question).
- Session: daily bars, UTC; no session filter.
- Entry: next daily open, taker, each symbol independently; one trade at a time per symbol.

Regime mix: 300 weeks: bull 72 (24%) | bear 0 (0%) | range 223 (74%) | n/a 5 (2%). Source: BTC weekly tags on DEV Mondays from 2018-10-01. The tag is the research_kit contract (ma_side + rsi_band, as-of the Monday open), computed by regime_pure in star_grades.py because research_kit.regime_tag returned None for every week in the first run (DECISION (OURS) below).

## Data
- BTCUSDT, ETHUSDT spot 1d klines, 2017-08-17 onward (fetch_binance_archive --spot-history). Cache F:/MTS/Dumps/backtest/eh-h2-spot (outside the repo).
- Perp fundingRate archive from 2019-09 (fetch --datasets fundingRate, 2019-09..2025-06; 4 monthly files returned 404 and count as zero funding). Cache F:/MTS/Dumps/backtest/eh-h2-fund.
- Funding before 2019-09 is 0 (spot-history trades). The DEV trades in 2020 onward carry funding; no 2018-2019 trade does (none fired in those years).
- Weekly and monthly bars resampled from closed daily bars in UTC, Monday weeks. A higher-TF bar counts only once its close time is at or before the daily signal bar's close (tested).
- RSI14 is rsi_core.py (Wilder; the only Wilder implementation in the repo).
- Splits: DEV = 2017-08-01..2024-06-30 (signals from 2018-10-01); VALIDATION 2024-07-01..2025-06-30 not read; HOLDOUT (2025-07-01+) never loaded. The loader refuses any bar at or after 2025-07-01 (test_split_refusal).

## Results (DEV, n, R net of fees and funding)

| Trial | candidates | trades | overlap skipped | invalid entry | censored at DEV end | n | hit (net > 0) | mean gross R | mean fee_r | mean funding_r | mean net R | SE (ISO week) | 95 % CI | MDE (80 %) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T02 7-star | 8 | 7 | 0 | 0 | 1 | 7 | 57 % | +1.134 | 0.025 | 0.051 | +1.058 | 1.012 | -0.93..+3.04 | 2.83 |
| T03 5-star | 9 | 8 | 1 | 0 | 0 | 8 | 38 % | +0.125 | 0.040 | 0.013 | +0.072 | 0.509 | -0.92..+1.07 | 1.42 |

Per-year DEV (net R mean, n):
- T02: 2020 n=1 +3.808; 2021 n=5 +0.627; 2022 n=1 +0.464. No trades in 2018-19, 2023 or 2024.
- T03: 2020 n=1 -1.027; 2021 n=5 -0.447; 2024 n=2 +1.921. No trades in 2018-19, 2022 or 2023.

Per symbol: T02 BTC 5 trades, ETH 2; T03 BTC 4, ETH 4.

Count pass (no returns): T02 and T03 candidates are all longs. Events per year on DEV: T02 about 1.2 per year, T03 about 1.4 per year across both symbols (7-8 trades over 5.75 years).

Exploratory only (no trial, no returns), PRD/NRD reverse divergence 5-50 bars, per year on DEV (repo reverse path, levels 60/40): BTC PRD 2.09/yr (12 events), BTC NRD 0.70/yr (4); ETH PRD 1.91/yr (11), ETH NRD 0.35/yr (2).

Every event (date = signal day, symbol, grade, net R) is in events.csv (15 rows). Gross R, fees and funding per event are in the run output (dev_run.txt, summary).

## Verdict logic
- T02: DEV screen not passed (n = 7 < 30; CI lower -0.93 < 0). Mean > 0, so the FAIL rule does not apply. INCONCLUSIVE.
- T03: DEV screen not passed (n = 8 < 30; CI lower -0.92). Mean > 0. INCONCLUSIVE.
- VALIDATION: not read for either trial (the screen was not passed). Holm m = 15 not applied.

## Sanity checks
- test_star_grades.py: 14 passed, 0 failed (hand-built bars for the target and stop-tie rules, the 40-bar time stop, divergence event and span-low stop, green rule, overlap skip, fee and funding arithmetic, cluster SE, split refusal for DEV and HOLDOUT, microsecond timestamp normalisation, no-lookahead on monthly and weekly bars).
- The test run before the code existed failed as expected; its last line: `ModuleNotFoundError: No module named 'star_grades'`.

## DECISION (OURS) list
1. Warm-up: signals counted from 2018-10-01 (14 months after the 2017-08 start for monthly RSI14). Brief gives DEV 2017-08..2024-06-30, not the repo splits.py window (DEV_START 2022-01-01); we follow the brief and do not edit splits.py.
2. Green bar (T03) = close > open AND close > prior close, from the brief. The 38..42 band is applied to the daily RSI14 at the signal bar (not a "low of the RSI" over several bars). Picked once, not tuned.
3. T02 stop = lowest low over the divergence span from swing A to the signal bar (inclusive). T03 stop = signal bar low.
4. Target fills: a stop-market gap fills at the open if the open is through the stop; a target limit fills at the open if the open is past the target. Entries at next open are taker (regime A).
5. Cost: regime A, 10 bps taker round trip plus 2 bps slippage = 12 bps round trip; fee_r = 12 bps / stop distance.
6. Funding: long pays positive funding, summed over calc times inside the hold, times entry price over the risk. Funding is zero before 2019-09 (no perp archive); 4 missing monthly funding files count as zero.
7. Overlap: a signal bar before the open trade's exit bar is skipped and counted; a signal on the exit bar is free (the trade closed at that bar's close).
8. Invalid entries (next open at or below the stop) are not trades and are counted (0 in DEV).
9. Censoring: a trade still open at the DEV end is dropped and counted (1 for T02). Nothing after 2024-06-30 is read for DEV.
10. SE: cluster-robust by ISO week of the signal day, sum of deviations per cluster over N.
11. MDE = 2.8 x SE (80 % power, one-sided, repo research_kit convention). CI = mean +- 1.96 SE.
12. Weekly regime: research_kit.regime_tag returned None for every week in the count run (its _last_closed path did not resolve with the inputs passed). Replaced by regime_pure with the same contract: ma_side (SMA14 on daily closes known at the Monday open) and rsi_band (weekly and monthly RSI14 known at the Monday open). Regime mix is from BTC only.
13. Holm for VALIDATION (not run): m = 15 applied as p x 15 (the smallest-p case). Not used here.
14. Not split by cycle phase; DEV pooled.

## Noticed
- Path slip: my first PRE_REG write landed in the planner checkout (mts-jis-nb-edge-hunt-plan-opus-1109b), an untracked folder with one file. I moved the file into the worktree and removed the stray folder there. Nothing else was touched in that checkout. Worth a look if the planner checkout is watched.
- sync.py printed "this tree is not yours (worker start)" on the first line, then the WORKTREE line; I worked only in the worktree.
- research_kit.regime_tag returns None on this data (see DECISION 12). That is a repo-side question, not fixed here (read-only rule).
- The brief's DEV start (2017-08) disagrees with splits.py (2022-01-01). Flagged in DECISION 1.
- Sample sizes: 7 and 8 trades over 5.75 years of daily BTC and ETH cannot test the claim. A pooled or intraday version would need a different trial; this wave does not re-cut trials.
