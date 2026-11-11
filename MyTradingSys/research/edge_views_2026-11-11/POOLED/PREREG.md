# POOLED pre-registration, 10 coins (written before anything was run). Card forced-selloff-long-pooled-10-coins-1111.
Both rules were frozen on BTC (FLOW/PREREG.md event (b) long side; TREND/PREREG.md rule 2). No parameter changes, no sweep, one run.

## Context
- Why: BTC alone gave validation n 17 (flow) and t 0.97 (trend); the pooled run asks if the same frozen rules hold on more coins.
- Market phase of the data (calendar, not a filter): 2022 bear, 2023 recovery, 2024 up-trend, 2025-26 mixed. No regime gate is used or added.
  RESULT.md reports the share of bull / bear / range weeks per period (rule for the label: BTC 13-week return above +15 % = bull,
  below -15 % = bear, else range).
- Parameter labels: every number below is SOURCED from the BTC PREREGs (which call them OURS for flow, SOURCED Turtle System 2 for 55/20). Nothing new.
- Prior looks at this idea: 7 forced-flow studies (descriptive, no fees) plus the BTC rows; this is look 8 as a fee-net rule. 100 studies exist in TESTED_MAP.md, so one pass is weak evidence; the bar is stricter than t 2.

Regime mix: pending, computed by pooled.py from BTC 13-week return and written into RESULT.md (calendar: 2022 bear, 2023 recovery, 2024 up, 2025-26 mixed).

## Data (public 1m candles on disk, DATA_MAP.md)
- BTC and ETH: F:/MTS/data/tom_raw/klines and klines_eth, 2022-01-01 to 2026-09 (daily and monthly files overlap; deduped by open_time).
- ADA, AVAX, BNB, DOGE, LINK, LTC, SOL, XRP: F:/MTS/data/tom_raw/klines_<sym>, 2022-01-01 to 2024-06-30.
- 1h and 4h bars built from 1m (UTC grid; open = first, high = max, low = min, close = last, volume = sum; empty bars dropped).
- Ten coins = BTC, ETH + the eight above. Perp candles (inferred), same family as the BTC studies. A coin starts trading when its file starts.

## Split (dates copied from the BTC studies, then limited to each coin's range)
- Rule A (FLOW): BTC study DEV end 2024-02-19 00:00 UTC, VALIDATION from 2024-03-20 00:00 UTC (30-day gap). Entries before 2024-02-19 = DEV; entries from 2024-03-20 = VALIDATION.
  Consequence stated now: the eight alts have only 2024-03-20..2024-06-30 in VALIDATION; BTC and ETH carry 2024-03..2026-09. Most VALIDATION days are BTC/ETH.
- Rule B (TREND): BTC study DEV = 4h bars up to 2023-07-05 16:00, VALIDATION from 2023-08-04 20:00 (180 4h bars gap). Each segment run on its own (own warm-up, open trade closed at segment end at last close), as trend.py.
  Alts: VALIDATION 2023-08-04..2024-06-30.

## Rule A. FLOW cascade (flow_test.py signals_cascade, long only)
- 1h bar i: close/open - 1 <= -3 % AND volume > 3 x the median volume of the previous 720 bars (bar i excluded; "trailing average" in the order = the median, as the code). Signal on the closed bar, LONG at the open of bar i+1, exit at the close of bar i+24 (H = 24 bars: entry bar plus 23).
- One position at a time per coin; signals while in a position are skipped. A trade needs 24 contiguous 1h bars after entry (skip otherwise, count reported).
- Net = close/open - 1 - FEE, with `from fees import BINANCE_TAKER` and `FEE = BINANCE_TAKER * 2` (10 bp round trip), price + fee only, no funding (not on disk for alts).
- Day clustering: the day = UTC date of the entry bar. Per-day observation = mean net of all coins that entered that day. Reported: per-event n/mean, per-day n/mean/t (t = mean/(sd/sqrt(n_days)) on per-day values), DEV and VALIDATION separately, plus per-coin rows (n, mean, t).
- Placebo: for each coin and period the same number of entry hours as the real events, drawn uniformly from the eligible hours of that period, long, 24 h hold, overlap ignored, 200 draws, seed 11; each draw is clustered by day exactly like the real data. Percentile = share of draws with a lower mean (per-day mean primary; per-event also shown).

## Rule B. TREND 4h Donchian 55/20 (trend.py donchian, copied unchanged)
- Long: close > highest high of previous 55 bars; short: close < lowest low of previous 55. Exit long: close < lowest low of previous 20; exit short: close > highest high of previous 20. Fill at next bar open. One position per coin. Fee as above.
- Reported per coin and pooled: ALL, long, short, for DEV and VALIDATION: n, win %, mean net per trade, t. Pooled t is computed on monthly pooled returns: each trade goes to the calendar month of its exit; the month value = mean net of trades exited that month (all coins); t = mean/(sd/sqrt(months)) over months with at least one trade. Pooled per-trade mean is shown next to it.
- Placebo (trend.py logic): same trade count per coin and row, same directions, holding times resampled from that coin's real trades, random entry inside the segment, 200 draws, seed 1; pooled draw = trade-count-weighted mean over coins. Percentile = share of draws below actual.
- Buy-and-hold per coin on the same segment (close-last / open-first). Strategy compounded return per coin (all trades chained) beside it. The long side is compared to buy-and-hold in words; the short side is reported separately.

## Pass bar (fixed now)
VALIDATION per-day t (rule A) / monthly-pooled t (rule B) >= 2.5 AND VALIDATION net mean > 0 AND real mean above the placebo 95th percentile (percentile >= 95).
Otherwise FAIL (a number misses the bar with n large enough: at least 30 per-day observations for A, 12 months with trades for B) or INCONCLUSIVE (n below that). DEV is reported, not part of the bar.
No edge claim, no forecast. FAIL is a result.

## Look-ahead
Signals use closed bars only (shift(1) windows, bar i signal, fill at i+1 open). lookahead_lint.py run before ship; flagged outcome / next-open lines appended to the allowlist.
