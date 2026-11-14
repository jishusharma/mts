**Verdict: FAIL, no NK rule tested so far has an edge. 0 of 9 edge8 cells and 0 of 6 new NK studies (about 100 rows) pass the gates on VALIDATION (2024+), fee-net at 12 bp. Gross R is about zero, and the fee eats it.**

Regime mix (VAL, new studies): UP 25% / DOWN 35% / RANGE 40%. DEV: UP 32% / DOWN 32% / RANGE 36%. Edge8 (BTC weekly): bull 56% / bear 31% / range 13%.

## All NK rules tested to date

Best matched row per rule, 12 bp taker unless noted. Mean net R is after fees. "Phase" is the trend phase the rule trades with (long in UP or RANGE, short in DOWN or RANGE).

| Rule | Video | Trade type | Phase | n VAL | Mean net R | Verdict | Reviewer flag |
|---|---|---|---|---|---|---|---|
| NK1 first-hour low break + VWAP (best: S_NY, session-end exit, 6bp maker) | NK extract (see PRE_REG) | Intraday short/long on opening-range break | Phase-matched | 9560 | -0.029 (12bp best: -0.136) | FAIL, 0/12 rows | Study.py stop line differs from PRE_REG (not disclosed); maker placebo not like-for-like; controls include a positive row (+0.058) the worker did not read; code first committed with the result |
| NK2 pivot S/R reclaim (best: 1h SHORT-P) | NK extract | Reclaim of daily pivot P/S1/R1 | Phase-matched | 6102 | -0.009 (6bp maker +0.046) | FAIL, 0/8 | Regime label is 1h bars not coin-days; gap-through targets fill at level (optimistic); code first committed with result; look-ahead test covers levels only |
| NK3 breakout / fakeout / retest (best: 1h B X1, no filter) | NK extract | A = retest of true breakout, B = fakeout fade | Phase-matched | 2448 | -0.034 (6bp maker +0.030, no CI) | FAIL, 0/16 | DEV/VAL split by entry bar not signal bar; fee charged on entry notional only; placebo p near 0 means "beats random", not "profitable" |
| NK4 Hilega Milega recon (best: 15m confirmed) | NK extract | HM state flip, 15m RSI 30/70 confirm | Phase-matched | 12897 | -0.192 | FAIL, 0/12 | HM formula is OURS (unverified vs his chart); headline should be confirmed rows only; BTC-today block is a day stale; RSI confirm path untested |
| NK5 session open 15/10/5 (best: NY-asia hold to 08:00 UTC) | NK extract | Session-open signal, 15m RSI + 10m/5m HM | Phase-matched | 1663 | +0.074 | FAIL: day CI low -0.151, ex-best-5 -0.108, BH q 1.00 | HM is OURS; RESULT says RSI 30/70 SOURCED but code uses 35/65 (OURS); study not re-run after final commit |
| NK6 confluence combos (best: L2&L3&L5) | NK extract | Layer-agreement combos, 33 combos | Phase-matched | 1996 | -0.112 (gross +0.084) | FAIL, 0/33 | 11-14 phase and pivots use a partial 11-13 day; dead `phase_next_day` field; close-based stop not tested |
| NK-R04 (15m RSI 30/70, NK window) | edge8 extract | Overnight-gap transplant, 15m | none | 951 | -3.685 R (tiny stop, cost about 0.8 R) | FAIL | Partial test: 2 of 3 conditions NOT_STATED; crypto has no NSE gap; stop is very tight |
| NK-R04 ALL hours | edge8 extract | same | none | 25177 | -2.043 R | FAIL | same |
| NK-R05 (NK window) | edge8 extract | same family | none | 1043 | -2.247 R | FAIL | same |
| NK-R05 ALL hours | edge8 extract | same | none | 23430 | -3.181 R | FAIL | same |
| NK-R11 Bollinger breakout long | edge8 extract | 15m BB breakout | none | 49922 | -0.236 R | FAIL, placebo p 1.00 | Band width, arming window and 15m are OURS; coarser timeframe not tested |
| MAL-R05 (not NK, same batch) | edge8 extract | Weekly divergence + third daily candle | none | 9 short / 7 long | +0.394 short / -0.602 long | UNDERPOWERED | CI spans zero widely |
| CBP-R05 (not NK) | edge8 extract | One dated BTC episode | n/a | 0 | n/a | NOT_TESTABLE | N = 1 |

Pattern across all studies: matched-direction rows are no better than mismatched-direction controls, and several rows beat random entries only because random entries lose about -0.18 to -0.20 R after fees. "Beats placebo" is not "profitable".

Reviewer notes that apply to all six new studies: code (study.py, run.py, tests) was first committed with the result, not with PRE_REG, so "code frozen before results" cannot be shown from git. Several RESULT.md files have the path typo `data_cacheinance`. The shared cache `F:\MTS\data_cache\binance` / `binance_spot` was written by sibling workers with the same filenames and mixed keys (`t` vs `ts`), with no provenance check. None of this changes any FAIL.

## NK concepts still untested

| Concept | Why untested |
|---|---|
| Options-only H23 and butterfly | Need option chain data; none in the pipeline |
| 55 NK videos, uncaptioned | Gemini caption fetchers locked. Desktop (JIS-NB) until 2026-11-16T03:02Z; NUC (JIS-NUC) until 2026-11-16T14:21Z (level 3 of 3). No quotes can be verified before then |
| NK-R04/R05 other two conditions, 10m/5m confirmation | NOT_STATED in the extract |
| RSI<30 filter, CPR, S2/S3/R2/R3 triggers (NK calls S3/R3 strong) | Not in the NK2 pre-registration; open follow-up |
| Tighter opening range ("break within first 10 minutes") | Separate pre-registration; NK1 trigger fires on almost every day |
| Maker-entry variant of 1h fakeout fade (NK3) | Needs its own pre-registered CI and placebo, with a fill model |
| Close-based stop (NK "stop on closing basis") | Never tested; NK6 and edge8 used intraday stops |
| NK-R11 on a coarser timeframe | Would be a new pre-registration |
| MAL-R05 | Too rare on 20 coins; needs longer or wider history |
| Hilega Milega exact formula | NK never gave it; ours is RSI9 with EMA3 vs WMA21 |

## Most promising row

**NK5 NY-asia (session open, phase-matched, hold to 08:00 UTC), 12 bp: mean net R +0.074, n VAL 1663, win 30.7%, placebo p 0.000.** It is the only row in all studies with a positive fee-net mean at 12 bp and it beats random same-phase entries. It still fails: per-trade CI low -0.036, day-cluster CI low -0.151, ex-best-5 -0.108, BH q 1.00. It is a long-tail result (30.7% win) carried by a few days. It was also one of three exits tried, so it is selected, and the Hilega Milega inputs are OURS.

Runners-up with positive gross but negative net: NK2 1h SHORT-P (gross +0.101, net -0.009, 6bp +0.046) and NK3 1h B X1 (net -0.034, 6bp +0.030, beats random).

**Test that decides it:** pre-register NY-asia alone (one exit, hold to 08:00 UTC, no other exits, no new parameters), and run it on data it has not seen. Use 10 or more new coins outside the current 20, plus the days since 2026-11-13 forward. Pass only if the day-cluster CI low is above 0, ex-best-5 is above 0 and the result holds at 12 bp. Commit the code with PRE_REG this time. If it fails on fresh coins, stop pursuing NK session-open rules.
