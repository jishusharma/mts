# PRE-REG: Malkan reverse divergence on the lower TF, fresh-data check (2026-10-31, frozen before any 2020-2021 bar is read)

Card `div-reverse-lower-tf-confirm-2020-2021`. Lead from `explore_div.py` (EXPLORATORY, DEV 2022-01..2024-06, about 66 cells looked at).
This run tests that one cell once, on data no part of this study has seen.

## Data
BTCUSDT 1m `F:/MTS/Dumps/backtest/raw_1m_2019/klines`, files 2020-01..2021-12 only (24 files). The run asserts no bar at or after
2022-01-01 is loaded. DEV, VALIDATION and HOLDOUT are not read.

## Trades (unchanged from explore_div.py / meta.py)
tf_break events from `study.events` (real levels), classes H / R / W1, direction d = side x SGN[cls], entry at the open of bar e+1,
exit at the close of bar e+4, cost 0.10 % round trip (`fees.BINANCE_TAKER` both legs), no slippage, no funding. Trades with e+MAXH past
the last bar are dropped (MAXH 24/24/12), as in explore_div.py.

## Rule (frozen)
Take a trade only when a Malkan reverse divergence WITH the trade on the next lower TF (15m->5m, 1h->15m, 4h->1h) is known in the
last 10 trade-TF bars before entry: PRD for a long (d = +1), NRD for a short (d = -1). Detector `rsi_divergence.py`, settings
`params/malkan_divergence_default.json` (SOURCED: reverse 5-14 bars, PRD RSI >= 60, NRD RSI <= 40). Event known at the close of its
stamp bar; window (entry - 10 bars, entry]. LOOK = 10 is OURS. Code: `explore_div.build` unchanged, flag = `at_lower_rsi_prd_with` OR
`at_lower_rsi_nrd_with`.

## Tests (m = 3: 15m, 1h, 4h; longs and shorts pooled)
- Statistic: mean net % per flagged trade. 95 % CI and one-sided p from a week-block bootstrap (1000 resamples, seed 1);
  p = share of resampled means <= 0. Holm over the three timeframes.
- PASS at a timeframe: mean net > 0, CI lower bound > 0, Holm p < 0.05.
- Card PASS: 1h or 4h passes. FAIL: no timeframe has mean net > 0. Otherwise INCONCLUSIVE.
- If a timeframe has fewer than 30 flagged trades it is INCONCLUSIVE (too few), not FAIL.

## Reported without a verdict
Flagged vs not-flagged difference, long and short separately, share of the best 5 % that carry the flag, each year (2020, 2021) separately.

## What follows
PASS: the rule becomes a candidate for the S3 funnel (VALIDATION read under its own pre-reg). FAIL or INCONCLUSIVE: the lead is
recorded as not confirmed; no re-tuning on 2020-2021.
