# Krown recall check: rules fixed before the run (PRE_REG_KROWN item 3)

Data: Binance spot BTCUSDT 1d and 1w_from_1d, Coinbase BTC-USD 1d (weekly built Monday-start, full weeks), all from
`F:/MTS/data/krown_daily` (DATA_MANIFEST.csv: every zip matched its published checksum). Only bars with open time before
2024-07-01 UTC are loaded (DEV); VALIDATION and HOLDOUT are not read. Detector parameters stay at v0.

**Pass bars (OURS, from PRE_REG_KROWN item 3, restated):**
1. RECALL: detector fires within 2 bars (either side) of the example's target bar for at least 6 examples that verify against klines.
   Strict count = every verified example, an example with no v0 detector counts as a miss. A covered count (verified
   AND a v0 detector is mapped) is shown next to it, never instead of it.
2. FIRE RATE: per setup S1..S9 pooled on Binance 1d DEV, at most 1.0 event per 10 daily bars. Weekly rates are shown for information.
3. Chance baseline per row: share of all bars of that series that have a matching event within 2 bars (so a hit is read against it).

**Verification rule per example** (a caption is not evidence; the klines are). Tolerances are OURS and fixed here:
- R01 VOL-13 weekly low March 2020: target = lowest-low week among weeks opening 2020-02-17..2020-04-13 (Binance 1w); verified if that week's volume >= 2.5x the mean of the prior 20 weeks (he says 3 to 3.5x). Detector: any long event S1-S8, 1w.
- R03 TRL-20 Dec 2018 anchor respected Mar 2020: verified if the Mar 2020 weekly low is above the Dec 2018 weekly low and the Dec 2018 low week volume >= 2x the prior 20 weeks (Binance 1w). A trend line has no price in the caption: only these two facts are checked. Detector: none in v0 (no trend-line detector).
- R04 RNG-05 2018 range, about February to November: span 2018-02-15..2018-11-13 (Binance 1d); verified if max close / min close <= 2.0. Detector: `range_state` non-empty on >= 50% of the span's days (S3 and S4 counts shown).
- R06a-d MAV-16 weekly 200 SMA lows 2015, 2018, 2020, 2022 (Coinbase 1w, the only series long enough): verified if the cycle-low week's low is within +-15% of the weekly SMA200 (a 200-week average needs 200 weeks: 2015 and 2018 lows come before the first Coinbase week that has one = NOT_IN_DATA). Cycle-low weeks: 2020 = lowest low weeks opening 2020-02-17..2020-04-13; 2022 = lowest low among weeks opening 2022-05-01..2022-12-31. Detector: none in v0 (S5 uses the 200 SMA of its own timeframe, not a weekly touch).
- R07 MAV-21 death cross January 2022 (Binance 1d): verified if the SMA50 crosses below the SMA200 on a day in 2021-12-15..2022-02-15 and the SMA200 is lower than 30 days earlier. Detector: S5 short within 2 daily bars of the cross (S5 is the only cross setup; its 21/55 cross is a different pair from his 50/200).
- R09 TOP-12 Bitcoin 2017 weekly top (Coinbase 1w; Binance weekly has only about 17 weeks before December, too few for BBWP): target = highest-high week among weeks opening 2017-09-01..2018-03-31; verified if (a) it opens in December 2017, (b) BBWP (v0 params) >= 85 on at least 8 weeks opening 2017-05-01..target, (c) the target week volume >= 2x the prior 30 weeks, (d) weekly RSI14 (own Wilder) at the target < its maximum over the prior 12 weeks while the target high exceeds all 12 prior highs, (e) own MACD(12,26,9) crosses down within 8 weeks after the target. Detector: S9 short, 1w, Coinbase.
- R10 TOP-32 Bitcoin 2021 weekly top (Binance 1w): target = highest-high week among weeks opening 2021-10-01..2021-12-31; verified if (a) RSI14 at the target < RSI14 at the highest-high week opening 2021-03-01..2021-05-31 while the target high is higher, (b) the target week or the week before is a shooting star on raw bars (upper wick >= 2x body, body in the lower third of the range), (c) own MACD crosses down within 8 weeks after the target. Detector: S9 short, 1w.
- R12 VJZ-50 coming off the 2018 lows, 55 EMA reclaim then break, about 4,000 to 14,000 (Binance 1w, inferred weekly): target = first weekly close above the weekly EMA55 after the lowest-low week opening 2018-11-01..2019-01-31; verified if that close is within 3,000..5,000 and the highest high in the next 26 weeks is within 12,600..15,400. Detector: S2 or S5 long, 1w.
- R13 VJZ-49 about 40,000 to 52,000 (Binance 1d, timeframe inferred daily): low bar = lowest low among days 2024-01-01..2024-02-10; verified if that low is within 38,000..42,000 and the highest high in the next 30 days is within 50,500..53,500. Detector: S2, S5 or S8 long on any day from the low bar to the first day with high >= 50,500 (generous window: the caption names no signal bar).

**Dropped without a read (listed in RECALL.md):** VOL-08 (February 2026 low: HOLDOUT, sealed), SNR-17 (the 100,000 test reached
about 108,000: after 2024-07, sealed), MAV-11/MAV-15 (no date, price or extract cite in the pre-reg row), VJZ-13 (weekly 55 EMA
reclaim given up in two closes: no date or price in the caption), KCM-15 (two BBWP-high dumps: no date or price).
