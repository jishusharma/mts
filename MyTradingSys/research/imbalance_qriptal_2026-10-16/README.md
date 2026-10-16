# Imbalance trading on Binance: what we tested before, which candles are "imbalances", and a fee-net test (2026-10-16)

Result: **NO EDGE.** A Qriptal-style imbalance fade (volume-anomaly candle with a small body at a new 20-bar low or high, faded with the stop at the candle's own extreme) loses money after fees on every Binance BTCUSDT perp timeframe from 30m to 1d, in both design (2022-01..2025-08) and check (2025-09..2026-06-25). It does not beat the same candle shape without the volume spike. One claim of his holds clearly: fading a high-volume LARGE-body candle loses heavily (gross -0.10 to -0.42 R per trade), so "big body = strength, do not fade it" is right. The holdout (2026-06-26..) was not read for outcomes.

## 1. What MTS did before (read from the repo, not re-derived)

| Work | What "imbalance" meant there | Result |
|---|---|---|
| P4 quarter-hour imbalance (2026-10-06/08, `research/P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md`) | taker-buy minus taker-sell volume of the first 1m bar of each quarter hour (Kim and Hansen paper) | NO REPLICATION |
| T093 turn-of-candle imbalance (2026-10-10, `research/T093_TOC_IMBALANCE_KLINES_2026-10-10.md`, `items/T093_*`) | same taker-delta proxy, held 4/8/12 h, 2022-2026, n about 166,000 | NO REPLICATION: gross +0.5 bp vs 10 bp fee, sign flips by year |
| `backtest/layers/run_t055_c3_imbalance.py` | same quarter-hour taker delta, momentum and contrarian | research only, never a layer |
| Order-book imbalance research (2026-10-10, `research/imbalance_2026-10-10/RESEARCH.md`) | depth OBI / OFI / VPIN | literature: real but seconds-scale and smaller than retail fees; no fee-net strategy found |
| B171 imbalance indicator end to end (`items/B171_*`, 2026-10-10) | "no sourced rule" | parked as NO-SOURCE, but its search only grepped Tom's 113 transcripts, not Qriptal's |
| Tom layer v2 family A "imbalance fade" (`tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md`) | auction-market imbalance (value area, single prints) | a different concept again; separate track |
| Fabio volume FVG (`backtest/layers/fabio/fabio_volume_fvg.py`) | lowest-volume price inside a leg's value area | separate track |
| Qriptal call ledger and scorecard (`research/qriptal_2026-10-10/`) | his posted calls | 70 statements, 2 fully priced, scored n = 0 (both in holdout) |

So the answer to "did we choose the right candles" for the earlier backtests is **no**: P4, T093 and C3 tested a taker-delta number on the first minute of a quarter hour. That is not the candle Qriptal (Habib) trades. Nobody had defined his candle until now.

## 2. What "imbalance" means: five constructs that share one word

| Construct | Definition | Data it needs | Where it is used |
|---|---|---|---|
| A. ICT fair value gap ("imbalance" in SMC) | 3-candle price gap: candle 1 high < candle 3 low | OHLC | ICT/SMC traders, most TradingView "imbalance" scripts |
| B. ICT volume imbalance | gap between two adjacent bodies, wicks overlap | OHLC | ICT |
| C. Footprint (diagonal) imbalance | ask volume at a price >= 3x bid volume at the price below (or the reverse) | trade-level aggTrades | order-flow traders (footprint) |
| D. Order-book imbalance | (bid depth - ask depth) / (bid + ask) | L2 book | HFT / market making |
| E. Taker-delta bar imbalance | (taker buy - taker sell) / volume of a bar | klines | P4, T093, C3 (our past tests) |
| **F. Qriptal volume-anomaly candle** | **a candle whose volume is anomalous for its timeframe on one exchange; a small body means the volume failed to move price** | **per-exchange OHLCV** | **Qriptal (Habib)** |

Construct F in his own words (verbatim, staged raw transcripts in `extracts/_staged_2026-09-27/raw/`):
- What it measures: "this is uh an indicator that measures volume" (`qriptal_ZPFK3ZsLwoo_raw.txt`, live stream, about lines 560-600).
- Small body = trapped traders: "volume anomalies but you have very small bodies. That means that volume came in but price ... failed to move" (same place).
- Large body = strength, not a fade: "this is not an imbalance to pay attent attention to for a short because it has a very large body".
- Per exchange: he checks Binance, Coinbase and Bybit separately ("on Binance, we do have two hourly imbalances"; `qriptal_AsAI5mglRSw_raw.txt`).
- Timeframes: 30m, 1h, 4h, 12h, daily; higher timeframes weigh more ("you need higher time frame imbalances", `qriptal_dYlk1gtY2Lk_raw.txt`).
- Levels: he uses the midpoint or the open of an imbalance candle as support/resistance, and calls unfilled ones "partially filled" magnets.
- Trade: "I look for a good resistance or support. I look for imbalances, and I look for a good reaction" (`qriptal_wveE-r1mzTc_raw.txt:108-120`); "my strategy requires a wick" (`qriptal_u0T-jOoesfc_raw.txt`).
- His indicator's formula, thresholds and his 86-setup record are not public. qriptal.com is a login app with no indicator text; his record (67.1% win rate, self-reported) stays unverified (see `qriptal_2026-10-10/SCORECARD.md`).

Outside sources (web search 2026-10-16) give no verified track record for any of A-F on crypto after fees. The closest published idea to F is Wyckoff/VSA "effort vs result" (high volume, narrow spread), described in VSA write-ups but never backtested with numbers there. Vendor FVG studies (A) give fill rates of about 50% and are not fee-net. B171's earlier X sweep found nothing fee-surviving for D. No other public trader was found who posts priced, timestamped Binance imbalance trades that could be scored.

## 3. Are our candles his candles? (the definition check)

1. **Candle construction is exact.** Our 1m-to-TF resample matches Binance's own 30m/1h/4h/12h/1d USD-M klines with 0 OHLC and 0 volume mismatches over 26,730 bars (2025-11..2026-09; `imb.py parity`). Any later difference is in the definition, not in the bars.
2. **Answer key.** `labels.json`: 22 candles Qriptal names with a timeframe and a spoken price (e.g. "a very important imbalance on Binance down at 65.4"; "12-hour imbalance ... the midpoint is at 63.9"), plus his statement that the late-June 2026 low had no daily/12h/4h imbalance on Binance. Every quote is checked verbatim with a file:line (`imb.py verify-labels`).
3. **Detector (OURS):** relative volume = volume / median volume of the prior 50 bars of the same TF, flagged at k = 1.5/2/2.5/3. Matching: a flagged candle of that TF, closed before the video, whose range holds the level (+-0.4%) or whose midpoint equals it (+-0.25%). Chance = the same hit if the window's flags were placed at random. Full table: `LABEL_CHECK.md`.

| | k = 1.5 | k = 2 | k = 3 |
|---|---|---|---|
| Binance perp: hits / chance (lift) | 17 / 14.5 (1.17) | 15 / 11.4 (1.32) | 12 / 8.0 (1.50, p = 0.003) |
| Binance spot: hits / chance (lift) | 18 / 13.4 (1.34) | 14 / 10.7 (1.31) | 11 / 6.3 (1.73, p = 0.001) |
| 30m-4h labels (10), perp, hits / chance | 10 / 9.5 | 10 / 9.1 | 10 / 7.5 |
| 12h-1d labels (12), perp, hits / chance | 7 / 5.0 | 5 / 2.3 | 2 / 0.5 |
| Late-June low: agrees there was no imbalance (3 TF) | 0-1 of 3 | 1 of 3 | 3 of 3 |

Reading:
- Relative volume picks his candles more often than chance, so "volume anomaly" is the right family. It does **not** reproduce his indicator. At any single k it misses part of the key (k = 3 misses most of his 12h/daily imbalances; k = 1.5 flags so much that chance explains most hits). His higher-timeframe imbalances are milder volume spikes than his intraday ones, or his baseline differs from a 50-bar median.
- The 30m-4h labels are weak evidence: so many intraday candles sit at a price that chance alone hits 75-95% of them.
- Spot and perp score about the same; the data cannot tell which Binance market he reads.
- The p-values treat labels as independent. They are not (L13/L14 and L16/L17 are the same statement on two TFs), so read them as rough.
- Limits: 22 labels from 19 videos, all 2026-04..09; 2 labels have no price match at all (L15, L19). The labels sit in the holdout window. Only candle shape and volume were read there, never a trade outcome.

So the honest answer to "how do we know the candles are right": the bars are exactly Binance's, the family (volume anomaly) is confirmed above chance, and the exact threshold is unknown. A rule that needs his exact candles needs his indicator, or more labelled candles (his Discord/Sunday streams).

## 4. Fee-net fade test (`imb.py backtest`, `BACKTEST.md` k = 2, `BACKTEST_k3.md` k = 3)

Spec, frozen before the run (all parameters OURS except the qualitative rule, which is his): Binance USD-M BTCUSDT 1m to 30m/1h/4h/12h/1d. Event classes: `imb_small` = relative volume >= k and body <= 30% of range; `imb_large` = relative volume >= k and body >= 70%; `normal_small` = relative volume < 1.2 and body <= 30% (control). Long at a new 20-bar low, short at a new 20-bar high. Entry at the next bar's open, stop at the candle's own low/high, target 1R or 2R, time exit after 24 bars. Stop first inside a shared minute. Taker 0.05% per side. Day-block bootstrap CI95. 30 cells per k (5 TF x 3 classes x 2 targets), k = 2 primary and k = 3 sensitivity: 60 cells declared. PASS = imb_small net CI95 low > 0 in design AND check, and above the control in both.

Net R per trade at 2R, k = 2 (design / check; n in brackets):

| TF | imb_small (his setup) | normal_small (control) | imb_large (the "strength" fade) |
|---|---|---|---|
| 30m | -0.29 (2011) / -0.44 (375) | -1.03 / -0.67 | -5.5 / -15.3 |
| 1h | -0.28 (1013) / -0.09 (219) | -0.08 / -0.24 | -5.9 / -11.1 |
| 4h | -0.07 (197) / -0.07 (51) | -0.19 / +0.19 | -1.19 / -18.2 |
| 12h | -0.18 (38) / -0.62 (7) | +0.29 / -0.04 | -0.36 / -0.33 |
| 1d | +0.22 (16) / none (0) | +0.10 / +0.22 | -0.45 / +0.37 (2) |

- Verdict: **NO EDGE** in all 10 TF x target cells at k = 2 and all 10 at k = 3.
- Gross before fees, imb_small is about zero (-0.10 to +0.14 R on 30m-4h). The fee is 0.09-0.38 R per trade on 30m-4h because the stop at the candle's own extreme is tight (median 44-144 bp).
- "Price comes back": price reaches the candle's other extreme before the stop in 61-72% of imb_small events on 30m-4h. The control shape scores the same or more, 62-76%, so the volume anomaly adds nothing to this.
- The large-body result is the clearest number here: fading a high-volume large-body candle loses 0.10-0.42 R gross (every TF except 1d check, n = 2). Use it as a veto, never as an entry.
- 12h/1d samples are small (7-38 trades); their CIs span zero widely.

## 5. What this means and what is next

1. The imbalance concept people actually trade (Qriptal's F) is a **context/location** tool in his own process: level + imbalance + reaction (wick), with HTF imbalances as bias. Tested alone as a mechanical fade on Binance it has no edge after fees. That matches all earlier imbalance tests (E, D).
2. Not tested here, and the only remaining honest routes:
   - his full three-part rule (pre-planned level + imbalance + wick reaction), which needs a level source; MTS levels exist (`lc-levels-hold`, pit-levels). Candidate: imbalance as a filter on an existing level layer, with fee-net DEV and a declared trial count. Task card `imb-filter-on-levels`.
     **Done 2026-10-16 (`filter/RESULT.md`, DEV 2022-04..2024-06, 5,976 first-touch fades of the 8 lc KEEP families, 28 declared cells): FAIL.** A closed small-body volume-anomaly candle at the level lifts fee-net R by +0.10 R (-0.366 vs -0.467 R per trade, Holm p 0.017, same sign in both halves, k = 3: +0.14 R) but the layer is -0.06 R gross and the fee is 0.35 R at the 0.40 % width, so the best cell is still -0.32 R. The large-body veto adds nothing on this layer (+0.009 R, t 0.27).
   - more labelled candles from his Discord / Sunday streams to pin his threshold (B162 D21 feed). Until then, a detector claiming to be "his" indicator is REJECT tier.
   - a footprint-imbalance (C) check needs aggTrades, which exist only for some periods (`F:/MTS/data/binance_raw/aggTrades`).
3. Layer status: no imbalance layer is promoted. `imb_large` (do not fade high-volume large-body candles) is offered as a veto candidate only, to be tested on an existing layer's trades, never as an entry.

## 6. Audit follow-up (2026-10-16, after the DSA audit brief, the lab audit and Q79)

- **Split exposure.** The main split (`dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md` section 1a): DEV before 2024-07-01, VALIDATION 2024-07-01..2025-06-30, HOLDOUT 2025-07-01..2026-09-30 (sealed, operator only). Section 4 used the Qriptal/Tom protocol instead. Its design window (2022-01..2025-08) crosses main VALIDATION and two months of main HOLDOUT, and its check window (2025-09..2026-06-25) lies inside main HOLDOUT. Fee-net returns for those windows are published in `BACKTEST.md` / `BACKTEST_k3.md`.
  - Logged in `EXPOSURE_LEDGER.csv`.
  - Registered as 20 FAIL rows in `research/VERDICTS.csv` (study_dir `imbalance_qriptal_2026-10-16`, split_read DEV+VALIDATION+HOLDOUT). `verdicts.py check` now blocks a re-run of the fade.
  - Consequence: no later imbalance-candle test may call 2024-07..2026-06-25 clean out-of-sample. A PRE_REG in this family must state this.
- **Trial count.** The filter study took Holm m = 16 before these 20 fade cells were registered. With them, m = 36. The H1 raw p of 0.0011 becomes about 0.040 at the first Holm step. The verdict does not change: FAIL rests on IMB net R > 0, which fails at -0.366 R.
- **imb_large net R is not meaningful.** The net values (-5 to -18 R) are driven by events whose next-bar open sits next to the stop after a large body; there is no minimum-risk floor, so the fee in R explodes. Gross R is bounded in [-1, R], so the gross claim (-0.10 to -0.42 R) stands. Read gross only for that class.
- **Q79 (touch-bar look-ahead in lc, fixed in `3b3ea9df`).**
  - The lc HOLD rates fell 15-25 points once the side came from the previous close (for example prior_day_high 62.1 to 37.6 %). All 8 KEEP families still beat their control.
  - The filter study already used the causal side and gave no touch-bar credit, so its numbers stand (46.2 % target, in line with the corrected HOLD rates).
  - The LC1 control itself is still under audit (AUDIT_BRIEF lead L8, card dsa-audit-05).
- **Lab audit `imb-filter-audit-1-map`** (Codex, `layer_lab/reports/2026-10-16_imb-filter-audit-1-map.md`):
  - C1 PASS: the headline -0.366 / -0.467 / +0.101 R recomputes exactly from the committed CSVs.
  - C2 and C3 BLOCKED as NOT_IN_DATA. The six scoped files have no loader manifest, previous close, touch OHLC or exit time.
  - The criteria were rewritten to accept a documented gap (`d52132b8`), and the card is ready again. Stage 2 (challenge) waits on it.
- **The suggested wide-stop retest is partly answered already.** The 4h fade cells here have median stops of 120-228 bp (near the 1.4 % fee-share target) and gross -0.08 to +0.02 R (n 248 at k = 2, 113 at k = 3; only the k = 3 check cell, n 22, is lower at -0.47 R). A wide stop alone does not create a gross edge.
  - The only positive signal in this family is the +0.10 R level-plus-imbalance lift, on a layer that is -0.06 R gross.
  - A new PRE_REG is worth writing only if a level layer first shows a gross edge at a 1.4 %+ width, DEV only, with m counted from VERDICTS.csv.

## Reproduce

```
python MyTradingSys/research/imbalance_qriptal_2026-10-16/test_imb.py
python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py verify-labels
python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py fetch
python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py parity
python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py label-check
python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py backtest --k 3.0   # then rename BACKTEST.md -> BACKTEST_k3.md
python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py backtest --k 2.0
```
Data: `F:/MTS/data/tom_raw/klines` (Binance USD-M BTCUSDT 1m, 2022-01..2026-09-26) and `F:/MTS/data/binance_tf` (Binance TF klines from data.binance.vision, spot and um, 2025-11..2026-09). Runtime about 20 s per backtest.
