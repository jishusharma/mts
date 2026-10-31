# PRE_REG: meta-label and early-exit test on the tf_break events (card meta-label-break-events-layer-features)

Operator 2026-10-31: "can we identify other layer confluence to separate the failed cases ... and check for confluence from other layers
for winning trades"; and "when it wins and when it loses - can we identify early and decide if to be in the trade". Frozen before any
outcome of this test is read. Amendments of `research/meta_label_roadmap_2026-10-31/ROADMAP.md` 2.1 are applied (items 1-8, mapped
below). Every parameter is OURS unless marked SOURCED. Nothing here is a result.

Known before writing (already published, not new reads): the base per-class means in `research/tf_break_event_study_2026-10-30/RESULT.md`
(15m FAIL, 1h/4h INCONCLUSIVE near zero).

## 1. Trades (the primary setup being labelled)
| item | value | label |
|---|---|---|
| Events | real-level events of `tf_break_event_study_2026-10-30/study.py` (same code, recomputed), TF 15m, 1h, 4h; classes H, R, W1; 1D and W excluded (n < 100) | OURS |
| Trade side | H: follow the break. R: fade the break, i.e. trade back inside the level = follow the reclaim. W1: fade the pierce | OURS (tf_break) |
| Entry / exit | open of bar e+1 (e = break bar + N for H/R, the break bar for W1); exit at the close of bar e+4 | OURS (tf_break) |
| Cost | round trip 2 x `fees.BINANCE_TAKER` = 0.10 %; no slippage (stated limit) | SOURCED fees.py |
| Label | win = net > 0 | OURS |
| Sets | DEV 2022-01-01..2024-06-30 (halves 2022 and 2023-01..2024-06); VAL 2024-07-01..2025-06-30; HOLDOUT 2025-07+ never opened (`study.load` stops at 2025-06) | OURS |

## 2. Features (frozen; all known at the open of bar e+1; amendment 1)
Bars of the trade TF up to and including bar e (closed). Higher-timeframe values use the last bar with open + tf <= entry time.

| id | feature | definition | label |
|---|---|---|---|
| F1 | bbwp | BBWP basis 7, lookback 100 of trade-TF closes at bar e (`krown_core.bbwp`, FORMULAS 21.5) | basis/lookback SOURCED KR-Q01 |
| F2 | bbwp_4h | same on 4h closes, last closed 4h bar; not used at TF 4h (equal to F1) | OURS |
| F3 | trend_d | d x (daily close / SMA200 of daily closes - 1), last closed daily bar; d = +1 long, -1 short | OURS |
| F4 | rsi_e | RSI14 of the trade TF at bar e, mirrored to the trade side (100 - RSI for shorts) | OURS |
| F5 | flow_e | d x mean taker-flow ratio (2 x taker buy - volume) / volume over bars e-4..e | OURS |
| F6 | relvol_e | volume of bar e / median volume of the same hour-of-week bar over the previous 8 weeks (amendment 1.1) | OURS |
| F7 | dist_atr | break depth, from study.py | OURS |
| F8 | move_e | d x (close[e] / close[break bar] - 1) / (ATR14 / close at the break bar); 0 for W1 | OURS |
| F9 | rv | ATR14 / close at bar e, % | OURS |
| F10-12 | session | entry hour UTC: EU 8-12, US 13-20, late 21-23 (Asia 0-7 is the base) | OURS |
| F13-15 | setup | class R, class W1 (H base); high-side break | OURS |

Funding: NOT RUN (not on disk for DEV; amendment 6). Open interest: not used (no DEV coverage).

## 3. Meta-label model and verdict (amendments 2-5, 8)
- Model: logistic, L2 penalty 1.0 on features standardized with the training fold's mean and sd, Newton fit; no tuning.
- Verdict-bearing CV: 6 contiguous time blocks over DEV by entry time; training events within 7 days of a test block edge are purged.
- Score cut: the top third = test events whose score >= the 2/3 quantile of the training fold's own scores (amendment 3).
- Measures per TF: n, gross, fee, net mean % for the top, middle and bottom thirds and for all trades; week-block bootstrap 95 % CI
  (1000 draws) of the top-third net; a bucket under 30 trades = too few.
- Placebo: 200 shuffles of the outcome vector across the TF's DEV events (features kept), same CV; statistic = top-third net minus all-trade
  net; p = (1 + count(placebo >= real)) / 201.
- Family: m = 3 (one specification x 3 TFs). Holm on the placebo p; BH-FDR reported beside.
- Same sign: out-of-fold top-third net > 0 in 2022 and in 2023-01..2024-06.
- DEV verdict per TF: NOT ENOUGH DATA if the top third has < 100 trades; PASS if top-third CI lower bound > 0 AND Holm p <= 0.05 AND same
  sign in both halves; FAIL if raw placebo p > 0.05 or the top-third CI upper bound < 0; else INCONCLUSIVE.
- Power line: from the DEV all-trade sd, the lift detectable per third at 80 % power, n = 7.849 x (sd / delta)^2 (SETUP_REVIEW.md:240).
- VAL: read once, only for a TF that PASSES DEV: refit on all DEV, cut = 2/3 quantile of DEV scores; VAL PASS = top-third net > 0 with CI
  lower bound > 0. No TF passes DEV -> VAL is not read for this arm.
- Descriptive, no verdict: per feature, net mean of DEV trades in that feature's DEV thirds, and the winners' vs losers' median.

## 4. Early-exit arm (the second question)
- Variant k in {1, 2}: at the close of bar e+k, if the trade is not in profit (d x (close[e+k] / entry - 1) <= 0), exit at that close;
  otherwise hold to the close of bar e+4. One round trip either way (same fee).
- Measure per TF and k: mean net % early-exit vs hold, the paired difference (early - hold) with week-block 95 % CI, DEV.
- Family m = 6 (3 TFs x 2 k). Verdict "early exit beats holding" per cell: paired-difference CI lower bound > 0 and same sign in both DEV
  halves; it is a profitable rule only if its own net CI lower bound is also > 0. VAL read only for a cell that passes on DEV.
- Descriptive: share of hold-winners that were not in profit at bar k (how many winners look like losers early).

## 5. Checks before the read
- The recomputed events reproduce `events.csv` counts and cont4 for real levels (study code unchanged).
- Look-ahead forcing test: changing every bar after bar e leaves F1-F15 unchanged.
- Hand-number tests for the purged blocks, the training-fold cut and the early-exit P&L.
