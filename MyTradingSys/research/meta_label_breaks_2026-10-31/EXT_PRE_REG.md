# EXT_PRE_REG: meta-label 1h lead, fresh-data check (2026-11-01, frozen before any 2020-2021 outcome is scored)

Card `meta-label-1h-dev-ext-check`. Lead: the 1h best third in `RESULT.md` (DEV net +0.063 %, CI -0.048..+0.179, INCONCLUSIVE). This run
scores that one frozen model once on data it has not seen. VALIDATION and HOLDOUT are not read.

## Data
BTCUSDT 1m `F:/MTS/Dumps/backtest/raw_1m_2019/klines`, 24 monthly files 2020-01..2021-12 (header-less spot-format klines, 1,052,640 bars;
`confirm_div.load_fresh` asserts no bar outside 2020-01-01..2021-12-31). Fit set: the existing DEV table (`table.csv`, 2022-01..2024-06).

## Frozen (unchanged from PRE_REG.md; every value OURS unless marked)
- Events, 15 features F1-F15, trade side, entry open e+1, exit close e+4, label win = net > 0: `meta.py` as it stands. TF 1h only.
- Cost 2 x `fees.BINANCE_TAKER` = 0.10 % round trip (SOURCED fees.py); no slippage, no funding.
- Model: logistic, L2 1.0, features standardized with the FIT set's mean and sd, Newton fit, no tuning. Fit on ALL DEV 1h trades with
  no missing feature (the same dropna as the DEV run). Cut = 1/3 and 2/3 quantiles of the fit set's own scores. A test event is "top
  third" when its score >= the 2/3 cut.
- Ext events: recomputed with `meta.build` on the fresh bars, trades with a missing feature dropped (the daily SMA200 needs 200 days, so
  early 2020 trades drop out, as in DEV; stated, not a choice made after seeing outcomes). No refit on any 2020-2021 bar.

## Test (m = 1)
- Statistic: mean fee-net % per trade in the ext top third. 95 % CI = week-block bootstrap (1000 draws, seed 1).
- PASS: top-third net > 0 AND CI lower bound > 0 AND label-shuffle p <= 0.05. FAIL: top-third net <= 0 or CI upper bound < 0.
  Otherwise INCONCLUSIVE. Top third with < 100 trades = NOT ENOUGH DATA.
- Label shuffle: 200 permutations of the DEV outcome labels (features kept), refit, score ext, statistic = top-third net minus all-ext net;
  p = (1 + count(placebo >= real)) / 201.
- Reported without a verdict: n, gross, net per third (top, middle, bottom) and all, the 2020 and 2021 top-third nets separately.

## Power (count-only, `scripts/dev/prereg_gate.py`)
1108 ext 1h events before the SMA200 drop; assume top third ~260. DEV sd of net per trade 1.084 % (`output.md`, 1h sd_net). m = 1,
cost 0.10: MDE 0.188 + 0.10 = 0.288 < 0.30, gate exit 0 (PASS: may freeze). Units are % per trade, not R. The DEV lift was 0.096 %, below
the MDE, so a miss here is weak evidence either way; the verdict rule above does not change.
